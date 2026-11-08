"""Build the filesystem-backed callback-generation fixture using the original four monitored phases."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
SOURCE_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-app-build-v1/index.json', 'sha256': 'd7f154cf5aba3d941fc369b00538f4f5cd4be5986453e31436b91e2544041d40', 'bytes': 7189}
BUILDER = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-app-build-v1/build.py', 'sha256': 'c660d7c7e9677c37b33159e4f5fb148c5b08ae5428b26e3cc25c568a42382efe', 'bytes': 16702}
INTEROP = dict(path=str(BASE / 'next-module-fileurl-interop-probe-root-results-v1/actual-runtime-review.json'),
    sha256='030fad8bec22f753d0436d0089d47d38014bae73cfdee911bd5d9baf4da3a226', bytes=7649)
NODE = dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
    sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', bytes=108619024)
NPM = dict(path='/private/tmp/starling-node-compat/next-app-tools-bootstrap-v1/lib/node_modules/npm/bin/npm-cli.js',
    sha256='8e5f6f3429f8cdbe693cdc29904e9d5a7b127a494bd15c804bd54c7403bfcbe7', bytes=54)
OUTPUT = Path('/private/tmp/starling-node-compat/next-fs-callback-app-build-v1-first')


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    assert type(SOURCE_INDEX) is dict and type(BUILDER) is dict, 'FS callback builder Source pins pending before reads/imports/outputs'
    assert SOURCE_INDEX['path'] == str(BASE / 'next-fs-callback-app-build-v1/index.json')
    assert BUILDER['path'] == str(BASE / 'next-fs-callback-app-build-v1/build.py')
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_fs_callback_build_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    self_ref = prep.row(Path(__file__).resolve())
    refs = [PREPARER, INNER_AUTHORITY, SOURCE_INDEX, BUILDER, INTEROP, NODE, NPM, self_ref]

    def protect():
        prep.family(SOURCE_INDEX)
        for ref in refs:
            prep.checked(ref)

    protect()
    prerequisite = prep.document(INTEROP)
    assert prerequisite['verifiedPassed'] is True and prerequisite['all16Passed'] is True
    assert prerequisite['state'] == 'COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1'
    authority = prep.document(INNER_AUTHORITY)
    before = prep.admit(authority)
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    assert not OUTPUT.exists() and not OUTPUT.is_symlink() and OUTPUT.resolve() == OUTPUT
    admission = HERE / 'build-admission.json'
    receipt = HERE / 'build-owner-result.json'
    assert not admission.exists() and not admission.is_symlink() and not receipt.exists() and not receipt.is_symlink()
    ar = prep.save(admission, dict(schemaVersion=1, state='ROOT_FS_CALLBACK_HOST_BUILD_ADMITTED_V1',
        sourceIndex=SOURCE_INDEX, builder=BUILDER, controller=self_ref, node=NODE, npmCli=NPM,
        interopPrerequisite=INTEROP, originalInnerAuthority=INNER_AUTHORITY,
        outputRoot=str(OUTPUT), constructorGuardBefore=before, perPhaseSeconds=[120, 120, 600, 900],
        hostBuildOnly=True, guestOrBrowserOrNativeBuildAllowed=False, actorInvoked=False))
    result, primary, after, protected = None, None, None, False
    try:
        protect()
        builder = prep.original(BUILDER, 'genuine_fs_callback_app_builder')
        result = builder.run(OUTPUT, Path(NODE['path']), Path(NPM['path']))
    except BaseException as error:
        primary = error
    finally:
        secondary = []
        try:
            after = prep.admit(authority)
            protect()
            prep.checked(ar)
            protected = True
        except BaseException as error:
            if primary is None:
                primary = error
            else:
                secondary.append(dict(name=type(error).__name__, message=str(error)[:2048]))
        try:
            data = dict(schemaVersion=1, state='ROOT_FS_CALLBACK_HOST_BUILD_COMPLETED_UNREVIEWED_V1',
                admission=ar, controller=self_ref, sourceIndex=SOURCE_INDEX,
                result=prep.row(OUTPUT / 'result.json') if (OUTPUT / 'result.json').is_file() else None,
                invocationAttempted=True, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, constructorGuardBefore=before, constructorGuardAfter=after,
                finalInputsPreserved=protected, buildPassed=result is not None and result.get('passed') is True,
                engineOrComponentRebuilt=False, runtimeExecuted=False, fullNextAccepted=False)
            record = prep.save(receipt, data)
            print(json.dumps(dict(receipt=record, buildPassed=data['buildPassed'], runtimeExecuted=False)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0 if data['buildPassed'] and protected else 1


if __name__ == '__main__':
    raise SystemExit(main())
