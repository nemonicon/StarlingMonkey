"""One V3 owned native build; default checks inputs without launching tools."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).absolute().parent
DRAFT = HERE / 'authority.unissued.json'
DRAFT_SHA = '2c135131c3bd2d1401b6694fd3505fa6f9ca441dd88eff6194c1af43d31daedf'
CALLER_SHA = 'a803c451b1c63f978cfe7b77be8acdeeefda2bafc3b57cccda917b8293ca8bcc'
ENTRY_SHA = 'd4e6a2aab5ef3aab17792446e1b73a6c61fd6ab053efc618a1e8842c591d8a01'
PLAN_SHA = 'f7ab6e269d8f5bd7c7021c38ff97522c7b1b6e48bdd32908b47e05f1fa5c2f73'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
WRAPPER_PYTHON_SHA = 'b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758'
BUILD_TOOL_PYTHON_SHA = '4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8'


def require(value, message):
    if not value:
        raise ValueError(message)


def row(path):
    p = Path(path)
    require(p.is_absolute() and '..' not in p.parts, 'Absolute canonical input required')
    for q in (p, *p.parents):
        require(not q.is_symlink(), 'Input alias refused')
    require(p.is_file() and p.stat().st_nlink == 1, 'Unique regular input required')
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def fresh(path):
    p = Path(path)
    require(p.is_absolute() and '..' not in p.parts and not p.exists() and not p.is_symlink(), 'Fresh path required')
    for q in p.parents:
        require(not q.is_symlink(), 'Output ancestor alias refused')
    require(p.parent.is_dir() and p.resolve() == p, 'Canonical existing output parent required')


def free_bytes(path):
    s = os.statvfs(path)
    return s.f_bavail * s.f_frsize


def capacity(free, required):
    require(type(free) is int and free >= required, 'Capacity held: requires at least 3 GiB before issuing or creating output')


def issued_copy(draft):
    require(draft['state'] == 'UNISSUED_ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'
            and draft['configureAllowed'] is draft['buildAllowed'] is None, 'Unissued draft required')
    issued = copy.deepcopy(draft)
    issued.update(state='ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1', configureAllowed=True, buildAllowed=True)
    require({k for k in issued if issued[k] != draft[k]} == {'state', 'configureAllowed', 'buildAllowed'}, 'Unexpected authority change')
    return issued


def terminal_clean(t):
    return (type(t['rawExitCode']) is int and t['rawExitCode'] == 0
            and t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
            and t['timeout'] is t['forcedCleanup'] is False
            and all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
            and all(g['alive'] is False for g in t['finalGroups']))


def outer_environment(base):
    env = {k: base[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME', 'PATH', 'LANG', 'LC_ALL'] if k in base}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def prepare():
    draft_ref = row(DRAFT)
    require(draft_ref['sha256'] == DRAFT_SHA, 'Draft changed; review before repinning')
    a = json.loads(DRAFT.read_bytes())
    for key, expected in [('callerIndex', CALLER_SHA), ('entry', ENTRY_SHA), ('plan', PLAN_SHA)]:
        require(row(a[key]['path']) == a[key] and a[key]['sha256'] == expected, 'Held caller/plan changed')
    root = Path(a['callerIndex']['path']).parent
    require(a['entry']['path'] == str(root / 'run.py') and a['plan']['path'] == str(root / 'plan.json'), 'Caller role mismatch')
    index = json.loads(Path(a['callerIndex']['path']).read_bytes())
    require({str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == {'index.json', *[r['path'] for r in index['files']]}, 'Caller membership changed')
    for r in index['files']:
        require('..' not in Path(r['path']).parts and not Path(r['path']).is_absolute(), 'Unsafe caller member')
        require(row(root / r['path']) == dict(path=str(root / r['path']), sha256=r['sha256'], bytes=r['bytes']), 'Caller member changed')
    spec = importlib.util.spec_from_file_location('pinned_portable_native_build', a['entry']['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = module.read(a['plan'])
    require(plan['disk'] == dict(startBytes=3 * 1024**3, stopBytes=1024**3), 'Build disk policy changed')
    require(plan['timeouts']['build'] == 7200, 'Outer timeout policy changed')
    require(plan['wrapperPython']['sha256'] == WRAPPER_PYTHON_SHA
            and row(plan['wrapperPython']['path']) == plan['wrapperPython'], 'Pinned wrapper Python changed')
    require(row(Path(sys.executable).resolve()) == plan['wrapperPython'], 'Use the pinned Python 3.11 wrapper')
    module.cargo_admission(a, plan)
    fresh(a['workRoot'])
    output = Path(a['workRoot'] + '-root-monitor')
    fresh(output)
    return a, draft_ref, module, plan, output


def run(a, draft_ref, module, plan, output):
    # This action gate precedes native/tool input reads, issuance, mkdir and copy.
    capacity(free_bytes(Path(a['workRoot']).parent), plan['disk']['startBytes'])
    effective = module.effective_plan(a)
    composition, source, embedding, support, trees, openssl, protected = module.inputs(a, plan, effective)
    module.selected_manifests(a, source)
    build_python = next(t['executable'] for t in effective['hostTools'] if t['name'] == 'python3')
    require(build_python['sha256'] == BUILD_TOOL_PYTHON_SHA and row(build_python['path']) == build_python,
            'Pinned native build-tool Python changed')
    python = plan['wrapperPython']
    require(python['sha256'] == WRAPPER_PYTHON_SHA and row(python['path']) == python, 'Pinned wrapper Python changed')
    cargo_before = module.recheck_cargo(a, plan)
    require(effective['monitor']['sha256'] == MONITOR_SHA and row(effective['monitor']['path']) == effective['monitor'], 'Original monitor changed')
    issued = issued_copy(a)
    module.validate_authority(issued)  # Pure validation; never calls the runner.
    launcher = row(Path(__file__).absolute())
    protected += [draft_ref, launcher]
    fresh(a['workRoot'])
    fresh(output)
    capacity(free_bytes(output.parent), plan['disk']['startBytes'])
    output.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='PORTABLE_NATIVE_BUILD_ROOT_FAILED_UNREVIEWED_V3',
                  draft=draft_ref, launcher=launcher, workRoot=a['workRoot'], rootOutput=str(output),
                  portableCargoSelection=a['portableCargoSelection'], wrapperPython=python,
                  nativeBuildToolPython=build_python,
                  monitorInvoked=False, issuedAuthority=None, terminal=None, workerResult=None,
                  errors=[], rawFiles={}, originalInputProtection=None, automaticRetry=False, engineOrGuestExecuted=False)
    try:
        authority = output / 'authority.issued.json'
        module.save(authority, issued)
        result['issuedAuthority'] = module.descriptor(authority)
        module.save(output / 'launch-scope.json', dict(
            scope='One fresh full native configure/build, unchanged offline/jobs1/3GiB-start/1GiB-floor policy; no engine/guest/freeze/network/rustup/retry.',
            inheritedPreparationOnlyTextIsDraftProvenance=True,
            authorityChangedKeys=['state', 'configureAllowed', 'buildAllowed'],
            timeoutSeconds=7200, cleanup='Original0af bounded cleanup additional',
            inheritedSystemEnvironmentNames=list(outer_environment(os.environ)),
            continuousOuterDiskGuardClaimed=False, independentBuildDataReviewRequired=True))
        monitor = module.load_utility(effective['monitor'], 'original_portable_build_root_monitor')
        argv = [python['path'], '-B', '-I', a['entry']['path'], '--authority', str(authority)]
        result['monitorInvoked'] = True
        monitor.monitor(argv, str(HERE.parents[4]), outer_environment(os.environ), output,
                        plan['timeouts']['build'], result['issuedAuthority'])
    except BaseException as error:
        result['errors'].append(dict(stage='owned-build-or-collector', type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
    finally:
        # Each collector is independent so none can skip final source protection.
        for name in ['started.json', 'stdout.log', 'stderr.log', 'terminal.json']:
            try:
                if (output / name).exists():
                    result['rawFiles'][name] = module.descriptor(output / name)
            except BaseException as error:
                result['errors'].append(dict(stage='raw-file-collection', path=name, type=type(error).__name__, message=str(error)))
        try:
            if (output / 'terminal.json').exists():
                result['terminal'] = module.descriptor(output / 'terminal.json')
                terminal = module.read(result['terminal'])
                started = module.read(module.descriptor(output / 'started.json'))
                require(started['argv'] == argv and started['timeoutSeconds'] == plan['timeouts']['build']
                        and started['pid'] == terminal['pid']
                        and started['authority'] == terminal['authority'] == result['issuedAuthority'],
                        'Original outer started/terminal roles differ')
                result['rawExitCode'] = terminal['rawExitCode']
                result['ownedCleanRawZero'] = terminal_clean(terminal)
        except BaseException as error:
            result['errors'].append(dict(stage='terminal-collection', type=type(error).__name__, message=str(error)))
        try:
            path = Path(a['workRoot']) / 'result.json'
            if path.exists():
                result['workerResult'] = module.descriptor(path)
                worker = module.read(result['workerResult'])
                result['workerInputProtection'] = worker['inputProtection']
                result['workerReportedPassed'] = (worker['passed'] is True and worker['inputProtection']['unchanged'] is True
                    and worker['inputProtection']['wholeTrees'] == len(trees) and worker['inputProtection']['errors'] == [])
        except BaseException as error:
            result['errors'].append(dict(stage='worker-result-collection', type=type(error).__name__, message=str(error)))
        protection_errors = []
        try:
            for r in protected:
                module.checked(r)
            module.check_family(a['callerIndex'])
            module.portable_admission(a, plan)
            module.recheck_cargo(a, plan, cargo_before)
            if result['issuedAuthority']:
                require(module.read(result['issuedAuthority']) == issued, 'Issued authority changed')
        except BaseException as error:
            protection_errors.append(dict(type=type(error).__name__, message=str(error)))
        result['originalInputProtection'] = dict(unchanged=not protection_errors, errors=protection_errors,
                                                liveToolTreeScope='Worker responsibility; no independent outer tree result inferred')
        passed = (result.get('ownedCleanRawZero') is True and result.get('workerReportedPassed') is True
                  and not result['errors'] and not protection_errors)
        result['completedUnreviewed'] = passed
        result['independentBuildDataReviewRequired'] = True
        result['state'] = 'PORTABLE_NATIVE_BUILD_ROOT_COMPLETED_UNREVIEWED_V3' if passed else result['state']
        module.save(output / 'observation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if result['completedUnreviewed'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare-only', action='store_true')
    mode.add_argument('--check-capacity', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    require(__debug__ and sys.flags.isolated and sys.dont_write_bytecode, 'Run Python with -B -I without -O')
    a, draft_ref, module, plan, output = prepare()
    free = free_bytes(Path(a['workRoot']).parent)
    if not args.run:
        summary = dict(state='PORTABLE_NATIVE_BUILD_ROOT_PREPARE_ONLY_V3', draft=draft_ref,
                       workRoot=a['workRoot'], rootOutput=str(output), freeBytes=free,
                       requiredStartBytes=plan['disk']['startBytes'], phaseFloorBytes=plan['disk']['stopBytes'],
                       rootAuthorityIssued=False, outputCreated=False, actualCommandInvoked=False)
        print(json.dumps(summary))
        if args.check_capacity:
            capacity(free, plan['disk']['startBytes'])
        return 0
    return run(a, draft_ref, module, plan, output)


if __name__ == '__main__':
    raise SystemExit(main())
