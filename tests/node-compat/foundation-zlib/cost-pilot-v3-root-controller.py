"""Root calibration-only phase; existing reviewed runner and owned monitor."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
Z = REPO / 'tests/node-compat/foundation-zlib'
SOURCE = Z / 'cost-pilot-timing-candidate-v3'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
GLOBAL_BUDGET_MS = 5400000


def row(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(value):
    index = read(value)
    root = Path(value['path']).parent
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(member, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}


def write(name, value):
    path = Z / name
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
    return row(path)


def utc(value):
    return value.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def main():
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    source = row(SOURCE / 'index.json')
    assert source['sha256'] == 'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9'
    family(source)
    peer_dir = Z / 'independent-cost-pilot-timing-v3-source-review-v1'
    peer_index = row(peer_dir / 'index.json')
    assert peer_index['sha256'] == '501022404e9bc4f86e1e675fe23f795c72d60d3b5bf96ec476c8ed2b4adb5bc8'
    family(peer_index)
    peer = dict(index=peer_index, result=row(peer_dir / 'results.json'))
    assert read(peer['result'])['sourceIndexSha256'] == source['sha256']
    plan = row(Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v3/prepared-plan.json'))
    assert plan['sha256'] == 'c914e3a02928ae23d579b66bc2910476c2585854500bd0ef4760f8115145383b'
    plan_review_dir = Z / 'independent-cost-measurement-plan-v3-results-review-v1'
    plan_review_index = row(plan_review_dir / 'index.json')
    assert plan_review_index['sha256'] == '5e81da01611fa0d8b6081d495487d13e37c8351b75a70384d9905d956e12b73c'
    family(plan_review_index)
    plan_review = dict(index=plan_review_index, result=row(plan_review_dir / 'results.json'))
    assert read(plan_review['result'])['verifiedPassed'] is True
    output = Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v3')
    external = Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v3-external-root')
    assert not output.exists() and not external.exists()
    now = datetime.datetime.now(datetime.timezone.utc)
    run_id = 'zlib_pilot_v3_20261105_01'
    quiet = dict(schemaVersion=1, state='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1',
                 runId=run_id, sourceIndexSha256=source['sha256'], phase='pilot-candidate',
                 startsAtUtc=utc(now), expiresAtUtc=utc(now + datetime.timedelta(hours=2)),
                 exclusiveMeasurementApproved=True, selectedGlobalBudgetMs=GLOBAL_BUDGET_MS,
                 competingAgentWorkStopped=True,
                 confirmedIdleAgents=['/root/buffer_templates', '/root/cost_component_results_review', '/root/runtime_gc_component_review'],
                 rootOtherBuildRuntimeOrHashAuditsStopped=True, backgroundDesktopAndSystemActivityControlled=False,
                 scope='Coordinated task workloads only; unrelated workstation/system activity remains a measurement limitation')
    quiet_row = write('cost-pilot-v3-quiet-window.json', quiet)
    phase = dict(schemaVersion=1, state='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1',
                 runId=run_id, phase='pilot-candidate', sourceIndexSha256=source['sha256'],
                 actionAllowed=True, globalBudgetMs=GLOBAL_BUDGET_MS, preparedPlan=plan,
                 quietWindowAuthority=quiet_row, warmNPlan=None, warmNMatchedPlan=None,
                 operationalAdmission=False, runtimeAcceptanceClaim=False, timingAcceptanceClaim=False,
                 scope='Unchanged paired geometric calibration: all60 comparisons/cases, both arms at50ms within original caps; no case omission or control subtraction')
    phase_row = write('cost-pilot-v3-phase-authority.json', phase)
    root = read(row(SOURCE / 'future-authority.template.json'))
    root.update(sourceIndexSha256=source['sha256'], sourceIndependentReview=peer, phase='pilot-candidate',
                runId=run_id, actionAllowed=True, outputRoot=str(output), globalBudgetMs=GLOBAL_BUDGET_MS,
                preparedPlan=plan, phaseAuthority=phase_row, quietWindowAuthority=quiet_row,
                independentPreparedPlanReview=plan_review, externalController=row(Path(__file__).resolve()),
                externalParentDeadlineSeconds=7200, externalOutputRoot=str(external))
    root_row = write('cost-pilot-v3-root-authority.json', root)
    config = dict(sourceIndex=source, rootAction=root_row)
    config_row = write('cost-pilot-v3-root-config.json', config)
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
    family(monitor_index)
    refs = read(row(SOURCE / 'references.json'))
    node = refs['node']
    assert row(node['path']) == node
    environment = {k: v for k, v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_')) and k not in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH')}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1',
                       NODE_COMPAT_TOOLCHAIN='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain',
                       NODE_COMPAT_COMPONENTIZE_MODULE='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js')
    spec = importlib.util.spec_from_file_location('genuine_reviewed_codec_pilot_owned_monitor', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    external.mkdir(mode=0o700)
    argv = [node['path'], str(SOURCE / 'run.mjs'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, external, 7200, root_row)
    assert read(root_row) == root and read(config_row) == config
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == terminal['errors'] == terminal['interruptedSignals'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    print(json.dumps(dict(rawExitCode=terminal['rawExitCode'], terminal=row(external / 'terminal.json'),
                          allObservedOwnedGroupsGone=terminal['allObservedOwnedGroupsGone'], operationalElapsedSeconds=terminal['operationalElapsedSeconds'])), flush=True)


if __name__ == '__main__':
    main()
