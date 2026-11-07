"""One owned compiler frontend check; preserve failed WORK, tools and new Source."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'syntax-inputs.json'
INPUTS_SHA = 'eb5c75119bf2e169431805e43a40d12c71d3cd63ed10bd5387d2dadd3209ab5c'


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and not path.is_symlink()
    h, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(data)
            size += len(data)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=size)


def verify(ref):
    assert row(ref['path']) == ref


def family(ref):
    verify(ref)
    root = Path(ref['path']).parent
    index = json.loads(Path(ref['path']).read_text())
    names = {v['path'] for v in index['files']}
    assert len(names) == len(index['files'])
    nodes = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in nodes)
    assert all(p.is_file() or p.is_dir() for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == names | {'index.json'}
    for value in index['files']:
        assert not Path(value['path']).is_absolute() and '..' not in Path(value['path']).parts
        path = root / value['path']
        assert path.stat().st_nlink == 1
        verify(dict(value, path=str(path)))


def load(name, ref):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    input_ref = row(INPUTS)
    assert input_ref['sha256'] == INPUTS_SHA
    selected = json.loads(INPUTS.read_text())
    self_ref = row(Path(__file__).resolve())
    family(selected['candidateSourceIndex'])
    family(selected['builderSourceIndex'])
    prepare = load('genuine_v6_preparer_for_syntax_admission', selected['builderPreparationEntry'])
    plan, portable, cargo, run, own_refs = prepare.load()
    assert run.descriptor(run.__file__) == selected['genuineTreeUtility']['source']
    deriver = load('genuine_sealed_single_tu_argv_deriver', selected['syntaxDeriver'])
    verify(selected['syntaxPlan'])
    syntax_plan = json.loads(Path(selected['syntaxPlan']['path']).read_text())
    derived = deriver.derive(syntax_plan)
    assert derived['argv'] == selected['argv'] and derived['removedOutputArguments'] == selected['removedOutputArguments']
    assert derived['cwd'] == selected['cwd'] and derived['TMPDIR'] == selected['TMPDIR']
    assert selected['perCommandSeconds'] == 180 and '-fsyntax-only' in derived['argv']
    assert not any(arg == '-o' or arg.startswith('-M') for arg in derived['argv'])
    output = Path(selected['proposedFreshOutputRoot'])
    assert output.is_absolute() and output.resolve() == output and not output.exists() and not output.is_symlink()
    assert Path(selected['cwd']).parent == Path(selected['TMPDIR']).parent == output
    free = shutil.disk_usage(output.parent).free
    assert free >= 1073741824

    def protect():
        assert row(INPUTS) == input_ref and row(Path(__file__).resolve()) == self_ref
        family(selected['candidateSourceIndex'])
        family(selected['builderSourceIndex'])
        for ref in own_refs + [selected['portableSelection'], selected['syntaxPlan'], selected['syntaxDeriver'],
                              selected['failureEvidence'], selected['originalWrapper'], selected['actualSdkCompiler'],
                              selected['originalMonitor'], *selected['selectedSdkApiHeaders']]:
            verify(ref)
        for link in selected['compilerSymlinkChain']:
            path = Path(link['path'])
            assert path.is_symlink() and os.readlink(path) == link['target']
            assert path.resolve() == Path(selected['actualSdkCompiler']['path'])
        source = portable.admit(selected['portableSelection'], plan['portableSourcePolicy'], prepare.REPO)
        assert len(source['files']) == 825 and len(source['physicalRecords']) == 825
        assert source['roleContentSha256'] == '89331d9264f7807ed5241d109531e1131d4e79ce588596e1d9e30a1a706bbc27'
        return source

    source_before = protect()
    tree_specs = selected['completeToolTreeSpecifications']
    tools_before = {role: run.authenticate_tree(spec) for role, spec in tree_specs.items()}
    failed_before = run.tree_snapshot(selected['failedWorkGuard']['root'])
    for key in ['originalResult', 'originalFailedMetadata']:
        verify(selected['failedWorkGuard'][key])
    os.umask(0o077)
    output.mkdir(mode=0o700)
    for name in ['cwd', 'tmp', 'owned-monitor']:
        (output / name).mkdir(mode=0o700)
    authority = dict(state='ROOT_SINGLE_TU_FRONTEND_COMPILER_AUTHORIZED_V1', inputs=input_ref,
        controller=self_ref, argv=derived['argv'], cwd=selected['cwd'], TMPDIR=selected['TMPDIR'],
        originalMonitor=selected['originalMonitor'], capSeconds=180, freeBytes=free, minimumFreeBytes=1073741824,
        compilerFrontendOnly=True, originalWorkWritesAllowed=False, linkAllowed=False, guestAllowed=False,
        fullNativeBuildAccepted=False, sourceInput=selected['portableSelection'])
    authority_path = output / 'authority.json'
    save(authority_path, authority)
    save(output / 'source-before.json', source_before)
    save(output / 'tools-before.json', tools_before)
    save(output / 'failed-work-before.json', failed_before)
    monitor = load('genuine_original_single_tu_owned_monitor', selected['originalMonitor'])
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/opt/homebrew/Cellar/bash/5.2.37/bin:/usr/bin:/bin', LANG='C', LC_ALL='C', TMPDIR=selected['TMPDIR'])
    terminal = None
    primary_error = None
    guards = {}
    try:
        terminal = monitor.monitor(derived['argv'], selected['cwd'], env, output / 'owned-monitor', 180, row(authority_path))
    except BaseException as error:
        primary_error = dict(type=type(error).__name__, message=str(error))
    finally:
        try:
            source_after = protect()
            tools_after = {role: run.tree_snapshot(spec['root']) for role, spec in tree_specs.items()}
            failed_after = run.tree_snapshot(selected['failedWorkGuard']['root'])
            save(output / 'source-after.json', source_after)
            save(output / 'tools-after.json', tools_after)
            save(output / 'failed-work-after.json', failed_after)
            guards = dict(sourceUnchanged=source_after == source_before, toolsUnchanged=tools_after == tools_before,
                          failedWorkUnchanged=failed_after == failed_before,
                          treeSnapshotRecordsCtime=False, continuousWriteAttestationClaimed=False)
        except BaseException as error:
            guards = dict(error=dict(type=type(error).__name__, message=str(error)))
    clean = bool(terminal and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        and terminal['timeout'] is terminal['forcedCleanup'] is False
        and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        and all(group['alive'] is False for group in terminal['finalGroups']))
    passed = bool(terminal and type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0 and clean
        and primary_error is None and all(guards.get(k) is True for k in ['sourceUnchanged', 'toolsUnchanged', 'failedWorkUnchanged']))
    result = dict(state='SINGLE_TU_FRONTEND_CHECK_COMPLETED_DATA_PENDING_V1', authority=row(authority_path),
        terminal=row(output / 'owned-monitor/terminal.json') if terminal else None,
        rawExitCode=terminal['rawExitCode'] if terminal else None, ownedClean=clean, primaryError=primary_error,
        guards=guards, passed=passed, objectOrLinkProduced=False, engineOrGuestExecuted=False,
        fullNativeBuildOrInteropAccepted=False)
    save(output / 'result.json', result)
    print(json.dumps(result))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
