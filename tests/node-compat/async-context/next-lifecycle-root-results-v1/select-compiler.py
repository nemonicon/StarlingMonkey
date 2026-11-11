"""Select the newly rebuilt package; never pretend it is the deleted old package."""
import hashlib
import json
from pathlib import Path
import os
import sys

REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
PACKAGE = WORK / 'package'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    materialization = json.loads((WORK / 'source-materialization.json').read_bytes())
    for member in materialization['sourceMembers']:
        actual = row(WORK / 'source' / member['path'])
        if (actual['sha256'], actual['bytes']) != (member['sha256'], member['bytes']):
            raise RuntimeError('Compiler source changed: ' + member['path'])
    old = json.loads((REPO / 'tests/node-compat/foundation-scheduler/clock-io-pruning-candidate-v1/tool-cut-references.json').read_bytes())['jsToolchain']
    same, metadata = [], []
    for record in old['files']:
        name = record['relativePath']
        if name in ('package.json', 'package-lock.json', 'node_modules/.package-lock.json'):
            metadata.append(name)
            continue
        actual = row(WORK / 'toolchain' / name)
        expected = record['descriptor']
        if (actual['sha256'], actual['bytes']) != (expected['sha256'], expected['bytes']):
            raise RuntimeError('Dependency payload differs from original tool cut: ' + name)
        if name.startswith('node_modules/'):
            copied = row(PACKAGE / name)
            if (copied['sha256'], copied['bytes']) != (actual['sha256'], actual['bytes']):
                raise RuntimeError('Private dependency copy differs: ' + name)
        same.append(name)
    files, links = [], []
    for path in sorted(PACKAGE.rglob('*')):
        name = path.relative_to(PACKAGE).as_posix()
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(PACKAGE):
                raise RuntimeError('Package symlink escapes: ' + name)
            links.append(dict(path=name, target=os.readlink(path), resolvedPath=str(resolved)))
        elif path.is_file():
            files.append(dict(row(path), relativePath=name, mode=path.stat().st_mode & 0o777))
        elif not path.is_dir():
            raise RuntimeError('Unexpected package member: ' + name)
    if [(r['path'], r['target']) for r in links] != [(r['path'], r['target']) for r in old['symlinks']]:
        raise RuntimeError('Package link inventory changed')
    commands = {}
    for name in ('npm-ci', 'materialize-source', 'build-splicer', 'wrap-splicer', 'transpile-splicer'):
        terminal_path = WORK / 'commands' / name / 'terminal.json'
        terminal = json.loads(terminal_path.read_bytes())
        if not (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and
                not terminal['remainingObservedPids'] and not terminal['timeout'] and
                not terminal['forcedCleanup'] and not terminal['signals'] and
                not terminal['interruptedSignals'] and not terminal['errors']):
            raise RuntimeError('Unclean build command: ' + name)
        commands[name] = row(terminal_path)
    result = dict(schemaVersion=1, state='FRESH_COMPILER_PACKAGE_SELECTED_V1',
                  package=dict(root=str(PACKAGE), files=files, links=links),
                  sourceMaterialization=row(WORK / 'source-materialization.json'),
                  originalDependencyPayloadsMatched=len(same), relocatedMetadata=metadata,
                  optionalPayloadRestoration=row(HERE / 'optional-restoration.json'),
                  compilerCore=row(PACKAGE / 'lib/spidermonkey-embedding-splicer.core.wasm'),
                  commands=commands, originalPackageRestored=False,
                  freshCompilerBinaryRequiresComponentValidation=True,
                  componentConstructed=False, guestExecuted=False)
    with (HERE / 'compiler-selection.json').open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(dict(selection=row(HERE / 'compiler-selection.json'), files=len(files), links=len(links),
                         originalDependencyPayloadsMatched=len(same), compilerCore=result['compilerCore'])))


if __name__ == '__main__':
    main()
