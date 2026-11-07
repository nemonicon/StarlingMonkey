"""Check ten installed generators only; default is a read-only Source plan."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
COMMANDS = [
    ['generate-factories.mjs', '--crypto-random'], ['generate-fs-factory.mjs'],
    ['generate-startup-factory.mjs'], ['generate-module-factory.mjs'],
    ['generate-async-hooks-factory.mjs'], ['generate-vm-data-factory.mjs'],
    ['zlib/generate-factory.mjs', '--repository', '{sourceRoot}'],
    ['zlib/generate-stream-factory.mjs'], ['next-http/generate-http-factory.mjs'],
    ['next-imports/generate-imports-factory.mjs'],
]


def canonical(value):
    p = Path(value)
    assert p.is_absolute() and '..' not in p.parts and p.resolve() == p
    assert not any(q.is_symlink() for q in (p, *p.parents))
    return p


def row(value):
    p = canonical(value)
    before = p.stat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    data = p.read_bytes()
    after = p.stat()
    assert (before.st_dev, before.st_ino, before.st_mode, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == \
           (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(p), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def verify(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and type(ref['bytes']) is int
    assert re.fullmatch('[0-9a-f]{64}', ref['sha256']) and row(ref['path']) == ref


def read(ref):
    verify(ref)
    assert ref['bytes'] <= 32 * 1024 * 1024
    return json.loads(Path(ref['path']).read_bytes())


def family(ref):
    index = read(ref)
    root = Path(ref['path']).parent
    assert Path(ref['path']).name == 'index.json'
    names = [r['path'] for r in index['files']]
    assert len(names) == len(set(names))
    nodes = list(root.rglob('*'))
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(names) | {'index.json'}
    dirs = set()
    for r in index['files']:
        rel = Path(r['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        dirs.update(p.as_posix() for p in rel.parents if p != Path('.'))
        verify(dict(r, path=str(root / rel)))
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_dir()} == dirs


def load(ref, name):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def durable(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as handle:
        handle.write(data)
        handle.flush()
        os.fchmod(handle.fileno(), 0o600)
        os.fsync(handle.fileno())


def diagnostic(error):
    return dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc())


def command_argv(plan, source):
    return [[plan['node']['path'], str(Path(source) / 'builtins/node-compat' / args[0]),
             *[source if x == '{sourceRoot}' else x for x in args[1:]], '--check'] for args in COMMANDS]


def clean(terminal):
    return bool(terminal and terminal['parentOwnedGroupGone'] is True and
        terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is False and
        terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in
        ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def layout(a, plan):
    assert type(a['schemaVersion']) is int and a['schemaVersion'] == 1
    assert a['state'] == 'ROOT_PORTABLE_NEXT_GENERATORS_AUTHORIZED_V1' and a['unissued'] is False
    assert a['generatorChecksAllowed'] is a['nodeHostSourceOnly'] is True
    for key in ['nativeBuildAllowed', 'compilerAllowed', 'cmakeAllowed', 'cargoAllowed',
                'engineAllowed', 'guestAllowed', 'networkAllowed', 'copySourceAllowed']:
        assert a[key] is False
    assert isinstance(a['runId'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', a['runId'])
    assert not any(k in a for k in ['argv', 'environment', 'outputRoot', 'monitorOutputRoot'])
    assert plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-native-portable-generators'
    assert plan['perCommandSeconds'] == 30 and plan['outerSeconds'] == 900
    assert plan['minimumFreeBytes'] == 67108864
    assert plan['maxAcceptedRawStreamBytes'] == 1048576 and plan['maxAcceptedOutputBytes'] == 8388608
    output = canonical(plan['outputPrefix'] + '-' + a['runId'])
    outer = canonical(str(output) + '-external-root')
    materialized = canonical(plan['materializationRoot'])
    assert output.parent == outer.parent == materialized.parent
    assert output != materialized and outer != materialized
    return output, outer


def bootstrap(authority_path):
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without -O')
    authority_ref = row(canonical(authority_path))
    a = read(authority_ref)
    assert a['sourceIndex'] == row(HERE / 'index.json') and a['plan'] == row(HERE / 'plan.json')
    plan = read(a['plan'])
    output, outer = layout(a, plan)
    family(a['sourceIndex'])
    family(plan['materializerIndex'])
    admission = plan['portableAdmission']
    family(admission['sourceIndex'])
    verify(admission['module'])
    assert Path(admission['module']['path']).parent == Path(admission['sourceIndex']['path']).parent
    assert Path(admission['module']['path']).name == 'portable.py'
    policy_plan = read(admission['plan'])
    assert Path(admission['plan']['path']).parent == Path(admission['sourceIndex']['path']).parent
    for ref in [plan[k] for k in ['node', 'monitor', 'python', 'commandDonor', 'composition', 'materializationSummary']]:
        verify(ref)
    module = load(admission['module'], 'held_portable_generator_admission')
    selected = module.admit(a['portableSelection'], policy_plan['portableSourcePolicy'], REPO)
    assert selected['composition'] == plan['composition'] and selected['sourceMaterialization'] == plan['materializationSummary']
    assert selected['sourceRoot'] == plan['sourceRoot'] and selected['roleContentSha256'] == plan['roleContentSha256']
    assert selected['roleCounts'] == plan['expectedRoleCounts'] and len(selected['files']) == 825
    assert len(selected['physicalRecords']) == 825 and isinstance(selected['directoryRecords'], list)
    assert command_argv(plan, selected['sourceRoot']) == module.generator_argv(policy_plan['portableSourcePolicy'], selected['sourceRoot'], plan['node'])
    assert native_descriptors(selected) == [r['source'] for r in module.role_copies(selected, 'native-policy-source')]
    return a, plan, authority_ref, output, outer, selected


def native_descriptors(selected):
    rows = sorted((r for r in selected['files'] if r['role'] == 'native-policy-source'), key=lambda r: r['path'])
    assert len(rows) == 435
    return [dict(path=str(Path(selected['sourceRoot']) / r['path']), sha256=r['sha256'], bytes=r['bytes']) for r in rows]


def tool_snapshot(plan):
    refs = [plan[k] for k in ['node', 'monitor', 'python']]
    refs += [plan['portableAdmission'][k] for k in ['sourceIndex', 'module', 'plan']]
    result = []
    for ref in refs:
        verify(ref)
        s = Path(ref['path']).stat()
        result.append(dict(path=ref['path'], sha256=ref['sha256'], bytes=ref['bytes'], mode=stat.S_IMODE(s.st_mode),
            dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns))
    return result


def environment(plan):
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH=str(Path(plan['node']['path']).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C')
    return env


def total_bytes(output):
    nodes = list(output.rglob('*'))
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes)
    return sum(p.stat().st_size for p in nodes if p.is_file())


def collect(authority_path):
    a, plan, authority_ref, output, outer, before = bootstrap(authority_path)
    assert not output.exists() and not output.is_symlink()
    assert shutil.disk_usage(output.parent).free >= plan['minimumFreeBytes']
    tools_before = tool_snapshot(plan)
    os.umask(0o077)
    output.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1',
        passed=False, sourceRoot=before['sourceRoot'], composition=before['composition'],
        materializationSummary=before['sourceMaterialization'], roleContentSha256=before['roleContentSha256'],
        node=plan['node'], sourceFiles=435, sourceBefore=native_descriptors(before), sourceAfter=None,
        wholePortableBefore=before['physicalRecords'], wholePortableAfter=None,
        portableDirectoriesBefore=before['directoryRecords'], portableDirectoriesAfter=None,
        commands=[], sourceBeforeAfterUnchanged=False, portableInputsPreserved=False,
        nativeOrGuestExecuted=False, rootAuthority=authority_ref, sourceIndex=a['sourceIndex'], plan=a['plan'],
        primaryError=None, finalProtectionError=None, toolProtectionError=None,
        toolInputsBefore=tools_before, toolInputsAfter=None, toolInputsPreserved=False,
        byteCapsArePostCaptureAdmissionNotContinuousLimits=True)
    try:
        monitor = load(plan['monitor'], 'genuine_portable_generator_command_monitor')
        for i, argv in enumerate(command_argv(plan, before['sourceRoot'])):
            assert bootstrap(authority_path)[5] == before
            folder = output / ('command-' + str(i).zfill(2))
            folder.mkdir(mode=0o700)
            terminal, monitor_error = None, None
            try:
                terminal = monitor.monitor(argv, before['sourceRoot'], environment(plan), folder,
                                           plan['perCommandSeconds'], authority_ref)
            except BaseException as error:
                monitor_error = error
            observed = {name: row(folder / name) if (folder / name).exists() else None
                        for name in ['stdout.log', 'stderr.log', 'started.json', 'terminal.json']}
            record = dict(argv=argv, cwd=before['sourceRoot'], rawExitCode=terminal['rawExitCode'] if terminal else None,
                stdout=observed['stdout.log'], stderr=observed['stderr.log'],
                stdoutSha256=observed['stdout.log']['sha256'] if observed['stdout.log'] else None,
                stderrSha256=observed['stderr.log']['sha256'] if observed['stderr.log'] else None,
                started=observed['started.json'], terminal=observed['terminal.json'], ownedGroupsClean=clean(terminal),
                monitorError=diagnostic(monitor_error) if monitor_error is not None else None)
            result['commands'].append(record)
            durable(folder / 'record.json', record)  # Capture full failure DATA before assertions.
            if monitor_error is not None:
                raise monitor_error
            assert all(record[k] is not None for k in ['stdout', 'stderr', 'started', 'terminal'])
            assert all(record[k] == terminal[k] for k in ['stdout', 'stderr'])
            assert clean(terminal) and type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
            assert terminal['stderr']['sha256'] == hashlib.sha256(b'').hexdigest()
            assert all(terminal[k]['bytes'] <= plan['maxAcceptedRawStreamBytes'] for k in ['stdout', 'stderr'])
            assert total_bytes(output) <= plan['maxAcceptedOutputBytes']
    except BaseException as error:
        result['primaryError'] = diagnostic(error)
    finally:
        try:
            after = bootstrap(authority_path)[5]
            result['sourceAfter'] = native_descriptors(after)
            result['wholePortableAfter'] = after['physicalRecords']
            result['portableDirectoriesAfter'] = after['directoryRecords']
            assert after == before
            result['sourceBeforeAfterUnchanged'] = result['sourceBefore'] == result['sourceAfter']
            result['portableInputsPreserved'] = True
        except BaseException as error:
            result['finalProtectionError'] = diagnostic(error)
        try:
            result['toolInputsAfter'] = tool_snapshot(plan)
            assert result['toolInputsAfter'] == tools_before
            result['toolInputsPreserved'] = True
        except BaseException as error:
            result['toolProtectionError'] = diagnostic(error)
        result['passed'] = bool(len(result['commands']) == 10 and result['primaryError'] is None and
            result['finalProtectionError'] is None and result['toolProtectionError'] is None and
            result['toolInputsPreserved'] and result['sourceBeforeAfterUnchanged'] and result['portableInputsPreserved'])
        if not result['passed']:
            result['state'] = 'PORTABLE_NEXT_INSTALLED_GENERATORS_FAILED_UNACCEPTED_V1'
        durable(output / 'body-result.json', result)
    print(json.dumps(dict(bodyResult=row(output / 'body-result.json'), passed=result['passed'])), flush=True)
    return 0 if result['passed'] else 1


def own(authority_path):
    a, plan, authority_ref, output, outer, before = bootstrap(authority_path)
    tools_before = tool_snapshot(plan)
    assert not output.exists() and not output.is_symlink() and not outer.exists() and not outer.is_symlink()
    free = shutil.disk_usage(output.parent).free
    assert free >= plan['minimumFreeBytes'], 'Generator-only 64 MiB admission, not a continuous floor'
    os.umask(0o077)
    outer.mkdir(mode=0o700)
    monitor = load(plan['monitor'], 'genuine_portable_generator_outer_monitor')
    argv = [plan['python']['path'], '-I', '-B', str(HERE / 'run.py'), '--worker-authority', authority_ref['path']]
    terminal, owner_error, after, tools_after = None, None, None, None
    try:
        terminal = monitor.monitor(argv, str(REPO), environment(plan), outer, plan['outerSeconds'], authority_ref)
    except BaseException as error:
        owner_error = diagnostic(error)
    finally:
        try:
            after = bootstrap(authority_path)[5]
            assert after == before
        except BaseException as error:
            owner_error = dict(primary=owner_error, finalProtection=diagnostic(error))
        try:
            tools_after = tool_snapshot(plan)
            assert tools_after == tools_before
        except BaseException as error:
            owner_error = dict(primary=owner_error, toolProtection=diagnostic(error))
    body_path = output / 'body-result.json'
    body = read(row(body_path)) if body_path.exists() else None
    if not output.exists():
        output.mkdir(mode=0o700)  # Genuine failure receipt even if worker failed before output creation.
    result = dict(body or {})
    result.update(schemaVersion=1, state='ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1',
        bodyResult=row(body_path) if body_path.exists() else None, rootAuthority=authority_ref,
        sourceIndex=a['sourceIndex'], plan=a['plan'], outerOwnerError=owner_error,
        outerOwnedGroupsClean=clean(terminal), outerInputsPreserved=after == before,
        outerToolInputsBefore=tools_before, outerToolInputsAfter=tools_after,
        outerStarted=row(outer / 'started.json') if (outer / 'started.json').exists() else None,
        outerTerminal=row(outer / 'terminal.json') if terminal else None,
        outerStdout=terminal['stdout'] if terminal else None, outerStderr=terminal['stderr'] if terminal else None,
        freeBytesAtAdmission=free, minimumFreeBytes=plan['minimumFreeBytes'], continuousFreeFloorClaimed=False,
        maxAcceptedOutputBytes=plan['maxAcceptedOutputBytes'], capturedNamespaces=[str(output), str(outer)],
        outputBytesBeforeFinalReceipt=total_bytes(output) + total_bytes(outer))
    result['passed'] = bool(body and body['passed'] is True and terminal and type(terminal['rawExitCode']) is int and
        terminal['rawExitCode'] == 0 and clean(terminal) and owner_error is None and after == before)
    result['outputCapSatisfied'] = result['outputBytesBeforeFinalReceipt'] + len((json.dumps(result, indent=2) + '\n').encode()) + 128 <= plan['maxAcceptedOutputBytes']
    result['passed'] = result['passed'] and result['outputCapSatisfied']
    if not result['passed']:
        result['state'] = 'PORTABLE_NEXT_INSTALLED_GENERATORS_FAILED_UNACCEPTED_V1'
    durable(output / 'result.json', result)
    print(json.dumps(dict(result=row(output / 'result.json'), passed=result['passed'])), flush=True)
    return 0 if result['passed'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--authority')
    group.add_argument('--worker-authority')
    args = parser.parse_args()
    if not args.authority and not args.worker_authority:
        plan = json.loads((HERE / 'plan.json').read_text())
        print(json.dumps(dict(sourceOnly=True, commands=command_argv(plan, plan['sourceRoot']), actorInvoked=False), indent=2))
        return 0
    return collect(args.worker_authority) if args.worker_authority else own(args.authority)


if __name__ == '__main__':
    raise SystemExit(main())
