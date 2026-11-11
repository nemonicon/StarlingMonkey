"""Relocate the retained npm lock without changing any dependency resolution."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / 'tests/node-compat/milestones/foundations-v12/docs/node-compat/component-tests/toolchain/package-lock.json'
SOURCE_SHA = 'bd852f41ddaa956d9135640690dffb4b05c47c326210ccd277cd632449aca952'
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
HERE = Path(__file__).resolve().parent


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    original = SOURCE.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA:
        raise RuntimeError('Retained lock changed')
    lock = json.loads(original)
    prefix = '../../../private/tmp/starling-node-compat/toolchain/'
    packages = {}
    for name, value in lock['packages'].items():
        if name and not name.startswith(prefix + 'node_modules/'):
            raise ValueError('Unexpected package location: ' + name)
        relocated = name.removeprefix(prefix)
        if relocated in packages or 'link' in value:
            raise ValueError('Alias or collision in lock')
        packages[relocated] = value
    if len(packages) != 181:
        raise ValueError('Original package inventory changed')
    lock.update(name='starling-lifecycle-toolchain', version='1.0.0', packages=packages)
    package = dict(name=lock['name'], version=lock['version'], private=True, **packages[''])
    if shutil.disk_usage(WORK.parent).free < 3 * 1024**3:
        raise RuntimeError('Need at least 3 GiB free')
    WORK.mkdir(mode=0o700)
    toolchain = WORK / 'toolchain'
    toolchain.mkdir(mode=0o700)
    (WORK / 'commands').mkdir(mode=0o700)
    (WORK / 'npm-cache').mkdir(mode=0o700)
    for name, value in [('package-lock.json', lock), ('package.json', package)]:
        with (toolchain / name).open('x') as handle:
            json.dump(value, handle, indent=2)
            handle.write('\n')
    normalized = json.loads((toolchain / 'package-lock.json').read_bytes())
    if {('' if k == '' else prefix + k): v for k, v in normalized['packages'].items()} != json.loads(original)['packages']:
        raise RuntimeError('Dependency records changed')
    result = dict(schemaVersion=1, state='RETAINED_NPM_LOCK_RELOCATED_NOT_INSTALLED_V1',
                  original=dict(path=str(SOURCE), sha256=SOURCE_SHA, bytes=len(original)),
                  packageCount=len(packages), dependencyRecordsUnchanged=True,
                  changes=['strip original toolchain prefix from nonempty package keys', 'root name/version metadata'],
                  workRoot=str(WORK), installed=False)
    with (HERE / 'npm-lock-relocation.json').open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
