"""Run three owned frontend checks using exact existing Ninja/compiler roles.

No object/link/engine/guest execution. The explicit --run action requires a
fresh pinned input map and preserves every original stream and failed result.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import sys

HERE = Path(__file__).resolve().parent
INPUTS_SHA = '8b00ee2b16c9804817c280d8e33719155c4ecd2c6a6bdb8e7625303431ac1453'


def need(value, label):
    if value is not True:
        raise ValueError(label)


def row(path):
    path = Path(path)
    need(path.is_absolute() and path.resolve() == path and not path.is_symlink()
         and path.is_file() and path.stat().st_nlink == 1, 'canonical regular input')
    before = path.stat()
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for body in iter(lambda: stream.read(4 * 1024**2), b''):
            digest.update(body); size += len(body)
    after = path.stat()
    need(all(getattr(before, k) == getattr(after, k) for k in
             ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns']),
         'input read bookend')
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=size)


def verify(ref):
    need(row(ref['path']) == ref, 'exact input descriptor')


def load(name, ref):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def family(ref):
    verify(ref)
    root = Path(ref['path']).parent
    index = json.loads(Path(ref['path']).read_text())
    files, directories = {'index.json'}, set()
    for member in index['files']:
        relative = Path(member['path'])
        need(not relative.is_absolute() and '..' not in relative.parts and
             relative.as_posix() == member['path'] and member['path'] not in files,
             'safe unique family member')
        files.add(member['path'])
        directories.update(p.as_posix() for p in relative.parents if p != Path('.'))
        verify(dict(path=str(root / relative), sha256=member['sha256'], bytes=member['bytes']))
    nodes = list(root.rglob('*'))
    need(not any(p.is_symlink() for p in nodes)
         and all(p.is_file() or p.is_dir() for p in nodes), 'family aliases or specials')
    need({p.relative_to(root).as_posix() for p in nodes if p.is_file()} == files
         and {p.relative_to(root).as_posix() for p in nodes if p.is_dir()} == directories,
         'closed family files and directories')


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())


def clean(terminal):
    return bool(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        and terminal['timeout'] is terminal['forcedCleanup'] is False
        and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        and all(group['alive'] is False for group in terminal['finalGroups']))


def derive(selected):
    """Admit only the recorded three ordinary TU commands and exact output flags."""
    need(selected['translationUnits'] == [
         'host-apis/wasi-0.2.0/host_api.cpp',
         'builtins/web/fetch/fetch-api.cpp',
         'builtins/web/fetch/request-response.cpp'], 'exact three distinct changed TUs')
    verify(selected['compileDatabase']); verify(selected['wholeNinjaCommands'])
    database = json.loads(Path(selected['compileDatabase']['path']).read_text())
    lines = Path(selected['wholeNinjaCommands']['path']).read_text().splitlines()
    old, new = selected['originalSourceRoot'], selected['newSourceRoot']
    results = []
    for name in selected['translationUnits']:
        file = old + '/' + name
        matching = [item for item in database if item['file'] == file]
        need(len(matching) == 1, 'one original compile row')
        matching_lines = [line for line in lines if shlex.split(line)[-2:] == ['-c', file]]
        need(len(matching_lines) == 1, 'one actual Ninja TU line')
        original = shlex.split(matching_lines[0]); stripped, removed = [], []
        i = 0
        while i < len(original):
            token = original[i]
            if token in ['-o', '-MT', '-MF']:
                need(i + 1 < len(original), 'output operand')
                removed.append(original[i:i + 2]); i += 2; continue
            if token == '-MD':
                removed.append([token]); i += 1; continue
            need(not token.startswith('-M') and not token.startswith('-o'), 'known output flags only')
            stripped.append(token); i += 1
        output = matching[0]['output'].split('/build/', 1)[1]
        need(removed == [['-MD'], ['-MT', output], ['-MF', output + '.d'], ['-o', output]],
             'exact original Ninja output arguments')
        db = shlex.split(matching[0]['command'])
        db_output = db.index('-o')
        need(db[db_output:db_output+2] == ['-o', output], 'compile database output')
        need(db[:db_output] + db[db_output+2:] == stripped, 'compile database and Ninja agree')
        argv = []
        for token in stripped:
            if old in token:
                need(token == file or token.startswith('-I' + old + '/'), 'known source-root operand')
                token = token.replace(old, new, 1)
            argv.append(token)
        need(argv[0] == selected['originalWrapper']['path'], 'original compiler wrapper')
        argv.insert(-2, '-fsyntax-only')
        results.append(dict(relativePath=name, originalCompileRow=matching[0],
                            originalCompilerLine=matching_lines[0], removedOutputArguments=removed,
                            argv=argv))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    need(__debug__ and sys.flags.isolated > 0 and sys.dont_write_bytecode, 'isolated pinned Python')
    need(type(INPUTS_SHA) is str, 'concrete inputs not prepared')
    input_ref = row(HERE / 'frontend-inputs-v3.json')
    need(input_ref['sha256'] == INPUTS_SHA, 'pinned input map')
    selected = json.loads(Path(input_ref['path']).read_text())
    self_ref = row(Path(__file__).resolve())
    # Authenticate closed candidate and builder families before importing the preparer.
    for ref in [selected['candidateSourceIndex'], selected['builderSourceIndex']]:
        family(ref)
    prepare = load('genuine_cleanup_v7_preparer', selected['builderPreparationEntry'])
    plan, portable, cargo, run, own_refs = prepare.load()
    need(row(run.__file__) == selected['treeUtility'], 'genuine unchanged build utilities')
    commands = derive(selected)
    need(commands == selected['commands'], 'concrete derived frontend argv')

    def protect():
        need(row(Path(__file__).resolve()) == self_ref and row(HERE / 'frontend-inputs-v3.json') == input_ref,
             'controller/input map unchanged')
        for ref in own_refs + selected['protectedReferences']:
            verify(ref)
        family(selected['candidateSourceIndex']); family(selected['builderSourceIndex'])
        for link in selected['compilerSymlinkChain']:
            path = Path(link['path'])
            need(path.is_symlink() and os.readlink(path) == link['target'] and
                 path.resolve() == Path(selected['actualSdkCompiler']['path']), 'SDK driver chain')
        source = portable.admit(selected['portableSelection'], plan['portableSourcePolicy'], prepare.REPO)
        need(source['sourceRoot'] == selected['newSourceRoot'] and len(source['files']) == 825,
             'fresh selected source')
        need(source['roleContentSha256'] == selected['roleContentSha256'], 'source fingerprint')
        return source

    source_before = protect()
    output = Path(selected['freshOutputRoot'])
    need(output.is_absolute() and output.resolve() == output and not output.exists()
         and not output.is_symlink() and output.parent.is_dir(), 'fresh output')
    need(selected['perCommandSeconds'] == 180 and shutil.disk_usage(output.parent).free >= 1024**3,
         'original frontend cap and storage')
    if not args.run:
        print(json.dumps(dict(state='ROOT_THREE_FRONTEND_INPUTS_CHECKED_NO_COMPILER',
                              commands=commands, engineOrCompilerOrGuestInvoked=False)))
        return 0
    failed_before = run.tree_snapshot(selected['failedAttemptGuard']['root'])
    tools_before = {name: run.authenticate_tree(spec)
                    for name, spec in selected['toolTrees'].items()}
    monitor = load('genuine_original_cleanup_frontend_monitor', selected['originalMonitor'])
    os.umask(0o077); output.mkdir(mode=0o700)
    (output / 'cwd').mkdir(mode=0o700); (output / 'tmp').mkdir(mode=0o700)
    authority = dict(state='ROOT_THREE_FRONTEND_CHECKS_AUTHORIZED_V1', controller=self_ref,
                     inputs=input_ref, commands=commands, perCommandSeconds=180,
                     compilerFrontendOnly=True, objectOrLinkOrEngineOrGuestAllowed=False,
                     existingWorkWritesAllowed=False, sourceSelection=selected['portableSelection'])
    save(output / 'authority.json', authority)
    save(output / 'source-before.json', source_before); save(output / 'tools-before.json', tools_before)
    save(output / 'failed-attempt-before.json', failed_before)
    environment = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    environment.update(PATH='/opt/homebrew/Cellar/bash/5.2.37/bin:/usr/bin:/bin',
                       LANG='C', LC_ALL='C', TMPDIR=str(output / 'tmp'))
    terminals, primary_error, guards = [], None, {}
    try:
        for i, command in enumerate(commands):
            monitor_output = output / ('owned-%d' % i)
            monitor_output.mkdir(mode=0o700)
            terminal = monitor.monitor(command['argv'], str(output / 'cwd'), environment,
                monitor_output, 180, row(output / 'authority.json'))
            terminals.append(terminal)
            if not clean(terminal) or type(terminal['rawExitCode']) is not int or terminal['rawExitCode'] != 0:
                break
    except BaseException as error:
        primary_error = dict(type=type(error).__name__, message=str(error))
    finally:
        try:
            source_after = protect()
            tools_after = {name: run.tree_snapshot(spec['root'])
                           for name, spec in selected['toolTrees'].items()}
            failed_after = run.tree_snapshot(selected['failedAttemptGuard']['root'])
            save(output / 'failed-attempt-after.json', failed_after)
            save(output / 'source-after.json', source_after); save(output / 'tools-after.json', tools_after)
            guards = dict(sourceUnchanged=source_before == source_after, toolsUnchanged=tools_before == tools_after,
                          failedAttemptUnchanged=failed_before == failed_after,
                          toolSnapshotsRecordCtime=False, continuousWriteAttestationClaimed=False)
        except BaseException as error:
            guards = dict(error=dict(type=type(error).__name__, message=str(error)))
    passed = (len(terminals) == 3 and all(clean(t) and type(t['rawExitCode']) is int
              and t['rawExitCode'] == 0 for t in terminals) and primary_error is None
              and guards.get('sourceUnchanged') is True and guards.get('toolsUnchanged') is True
              and guards.get('failedAttemptUnchanged') is True)
    result = dict(state='ROOT_THREE_FRONTEND_CHECKS_COMPLETED_DATA_PENDING_V1',
                  authority=row(output / 'authority.json'), rawExitCodes=[t['rawExitCode'] for t in terminals],
                  collectedTerminalsOwnedClean=all(clean(t) for t in terminals) if terminals else None,
                  ownedClean=(all(clean(t) for t in terminals)
                              if terminals and primary_error is None else None),
                  primaryError=primary_error, guards=guards,
                  completedCommands=len(terminals), passed=passed, fullBuildOrGuestAccepted=False)
    save(output / 'result.json', result); print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
