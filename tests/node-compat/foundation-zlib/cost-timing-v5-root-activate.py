"""Issue separate Root timing files only after reviewed source and explicit idle DATA."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

Z = Path(__file__).resolve().parent
SOURCE = Z / 'cost-timing-v5-root-controller-candidate-v1'
SOURCE_SHA = 'ae8e1f2398fa524bd8058540521da4ee827eb2bf06117281c6be4108aecb9efb'
IDLE = Z / 'cost-timing-v5-idle-coordination.json'
RUN_ID = 'codec-cost-timing-v5'


def row(path):
    path = Path(path); a = path.stat(); h = hashlib.sha256()
    assert path.is_absolute() and path.is_file() and not any(p.is_symlink() for p in [path, *path.parents])
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    b = path.stat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=b.st_size)


def family(descriptor):
    assert row(descriptor['path']) == descriptor
    root = Path(descriptor['path']).parent; index = json.loads(Path(descriptor['path']).read_bytes()); names = {'index.json'}
    for value in index['files']:
        name = value['path']; assert name and name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name); assert row(root / name) == dict(value, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names
    return index


def write(name, value):
    path = Z / ('cost-timing-v5-' + name + '.json')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n'); stream.flush()
        import os
        os.fsync(stream.fileno())
    return row(path)


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv) == 2
    own = row(SOURCE / 'index.json'); assert own['sha256'] == SOURCE_SHA and own['bytes'] == 4973
    family(own)
    peer = json.loads(sys.argv[1]); peer_index = family(peer['index'])
    assert row(peer['result']['path']) == peer['result']
    member = dict(peer['result'], path=Path(peer['result']['path']).relative_to(Path(peer['index']['path']).parent).as_posix())
    assert peer_index['files'].count(member) == 1
    verdict = json.loads(Path(peer['result']['path']).read_bytes())
    assert verdict['schemaVersion'] == 1 and verdict['state'] == 'INDEPENDENT_ZLIB_COST_TIMING_V5_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert verdict['controllerSourceIndexSha256'] == SOURCE_SHA and verdict['sourceOnly'] is verdict['sourceReviewPassed'] is True and verdict['ownerActionsInvoked'] is False
    idle_row = row(IDLE); idle = json.loads(IDLE.read_bytes())
    assert idle['schemaVersion'] == 1 and idle['state'] == 'ROOT_OBSERVED_THREE_AGENT_IDLE_FOR_CODEC_TIMING_V5_V1'
    assert idle['rootOtherBuildRuntimeOrHashAuditsStopped'] is True and idle['allRootExternalJobsTerminal'] is True
    assert {v['agent'] for v in idle['agents']} == {'/root/buffer_templates', '/root/cost_component_results_review', '/root/runtime_gc_component_review'}
    assert len(idle['agents']) == 3 and all(v['allToolsTerminal'] is v['writesHashesTestsStopped'] is v['resumeRequiresRootRelease'] is True for v in idle['agents'])
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    for key in ['sourceIndex', 'sourcePeer', 'planReview', 'pilotReview']:
        value = refs[key]
        family(value if key == 'sourceIndex' else value['index'])
    for key in ['preparedPlan', 'matchedPlan']:
        assert row(refs[key]['path']) == refs[key]
    assert not Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5').exists()
    assert not Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5-external-root').exists()
    now = datetime.datetime.now(datetime.timezone.utc)
    instant = lambda value: value.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    quiet = json.loads((SOURCE / 'future-quiet-window.template.json').read_bytes())
    quiet.update(sourceIndexSha256=refs['sourceIndex']['sha256'], phase='timing', runId=RUN_ID, exclusiveMeasurementApproved=True, startsAtUtc=instant(now), expiresAtUtc=instant(now + datetime.timedelta(hours=2)), competingAgentWorkStopped=True, rootOtherBuildRuntimeOrHashAuditsStopped=True, backgroundDesktopAndSystemActivityControlled=False, idleCoordination=idle_row, controllerSourceIndex=own, controllerIndependentReview=peer, rootActivationIssuer=row(Path(__file__).resolve()), observationPolicy='Only lightweight owned-handle/status observation and progress records; no other agent builds, reads/hash audits or source work during this window. Unrelated desktop/system activity remains uncontrolled.')
    quiet_row = write('quiet-window', quiet)
    phase = json.loads((SOURCE / 'future-phase-authority.template.json').read_bytes())
    phase.update(sourceIndexSha256=refs['sourceIndex']['sha256'], sourceIndependentReview=refs['sourcePeer'], phase='timing', runId=RUN_ID, actionAllowed=True, globalBudgetMs=5400000, preparedPlan=refs['preparedPlan'], quietWindowAuthority=quiet_row, warmNPlan=refs['pilotReview'], warmNMatchedPlan=refs['matchedPlan'], calibrationSourceIndex=refs['originalCalibrationSource'])
    phase_row = write('phase-authority', phase)
    root = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    root.update(sourceIndexSha256=refs['sourceIndex']['sha256'], sourceIndependentReview=refs['sourcePeer'], phase='timing', runId=RUN_ID, actionAllowed=True, outputRoot='/private/tmp/starling-node-compat/zlib-cost-timing-v5', globalBudgetMs=5400000, preparedPlan=refs['preparedPlan'], phaseAuthority=phase_row, quietWindowAuthority=quiet_row, warmNPlan=refs['pilotReview'], warmNMatchedPlan=refs['matchedPlan'], calibrationSourceIndex=refs['originalCalibrationSource'], externalController=row(SOURCE / 'controller.py'), controllerSourceIndex=own, controllerIndependentReview=peer, independentPreparedPlanReview=refs['planReview'], externalParentDeadlineSeconds=7200, externalOutputRoot='/private/tmp/starling-node-compat/zlib-cost-timing-v5-external-root', rootActivationIssuer=row(Path(__file__).resolve()))
    root_row = write('root-authority', root)
    run = json.loads((SOURCE / 'future-run-config.template.json').read_bytes()); run.update(sourceIndex=refs['sourceIndex'], rootAction=root_row)
    run_row = write('run-config', run)
    config = json.loads((SOURCE / 'future-controller-config.template.json').read_bytes()); config.update(controllerSourceIndex=own, controllerIndependentReview=peer, runConfig=run_row)
    config_row = write('controller-config', config)
    for value in [idle_row, quiet_row, phase_row, root_row, run_row, config_row]:
        assert row(value['path']) == value
    receipt = write('root-activation-receipt', dict(schemaVersion=1, state='ROOT_ISSUED_TIMING_V5_PHASE_FILES_NOT_EXECUTION_OR_ACCEPTANCE_V1', controllerSourceIndex=own, controllerIndependentReview=peer, idleCoordination=idle_row, quietWindow=quiet_row, phaseAuthority=phase_row, rootAuthority=root_row, runConfig=run_row, controllerConfig=config_row, globalBudgetMs=5400000, outerDeadlineSeconds=7200, sourceIndex=refs['sourceIndex'], originalCalibrationSource=refs['originalCalibrationSource'], metadataProjection=False, controlsSubtracted=False, timingAcceptanceClaim=False, operationalAdmission=False, runtimeAcceptanceClaim=False))
    print(json.dumps(dict(receipt=receipt, controllerConfig=config_row)), flush=True)


if __name__ == '__main__':
    main()
