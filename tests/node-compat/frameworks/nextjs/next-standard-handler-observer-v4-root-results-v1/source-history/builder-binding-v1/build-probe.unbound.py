"""Build and validate the V4 observer with the unchanged diagnostic probe inner only. No runtime or Next composition."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-standard-handler-observer-build-v4-first')
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-probe-root-results-v1/prepare-construction.py'),
    sha256='62142edc1a76bd7c47bc482737c16faa2364cde898ffb790aebf8a8ebf0859ef', bytes=17890)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-probe-root-results-v1/actual-construction-review.json'),
    sha256='163eb782152b11c62be41165a5ea6a2130a70795b6d7490b477b0004b4646bca', bytes=21317)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-probe-root-results-v1/diagnostic-probe-construction-authority.json'),
    sha256='4548cc3f0627fc338986119ac223b81c43468e097ecf9eba64dff8d5fd2a586d', bytes=5596754)
OBSERVER_INDEX = None
OBSERVER_SOURCE = None
OBSERVER_MANIFEST = None
OBSERVER_PROTOCOL = None
WAC = dict(path='/private/tmp/starling-node-compat/next-standard-handler-wac-build-v1-first/target/debug/wac',
    sha256='6577e5eedeb0644025a8454c3d600ecad14a3788432c48e8d40b7ba56d271f5f', bytes=30168152)
WASM_TOOLS = dict(path='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasm-tools/1448/wasm-tools',
    sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d', bytes=17556208)


def main():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1 and
            all(type(ref) is dict for ref in (OBSERVER_INDEX, OBSERVER_SOURCE, OBSERVER_MANIFEST, OBSERVER_PROTOCOL))):
        raise RuntimeError('Use non-optimized Python -I -B with four genuine bound observer Source roles; no helper/IO/action')
    source = Path(PREPARER['path'])
    raw = source.read_bytes()
    assert source.resolve() == source and not source.is_symlink() and source.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_v4_probe_observer_build_admission', source)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    review = prep.document(INNER_REVIEW)
    assert review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is True and review['rootAuthority'] == INNER_AUTHORITY
    observer_root = BASE / 'next-standard-handler-return-observer-v4'
    index = prep.family(OBSERVER_INDEX)
    prep.require(OBSERVER_INDEX['path'] == str(observer_root / 'index.json'), 'Genuine V4 Source family')
    for ref, name in ((OBSERVER_SOURCE, 'observer.wat'), (OBSERVER_MANIFEST, 'manifest.json'), (OBSERVER_PROTOCOL, 'protocol.json')):
        prep.require(ref['path'] == str(observer_root / name) and any(dict(member, path=str(observer_root / member['path'])) == ref for member in index['files']), 'Exact indexed V4 Source member: ' + name)
    protocol = prep.document(OBSERVER_PROTOCOL)
    prep.require(protocol['version'] == 4 and protocol['marker'] == 'NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4' and protocol['headerName'] == 'x-next-public-request-correlation', 'Exact selected V4 protocol')
    inner = review['component']
    prep.require(inner == dict(path='/private/tmp/starling-node-compat/next-native-export-diagnostic-probe-component-v2-real-next-diagnostic-probe-native-export-first/api-return/returned-component.wasm', sha256='d04c4289dfdc4d5c2a2679d4cc0245d12c5a1ed332247a7574ef287042de46a3', bytes=37156919), 'Unchanged reviewed d04 probe inner; no Next inner in this phase')
    refs = [PREPARER, INNER_REVIEW, INNER_AUTHORITY, OBSERVER_INDEX, OBSERVER_SOURCE, OBSERVER_MANIFEST, OBSERVER_PROTOCOL, WAC, WASM_TOOLS, inner]
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        prep.family(OBSERVER_INDEX)
        for ref in refs + [self_ref]:
            prep.checked(ref)

    protect()
    authority = prep.document(INNER_AUTHORITY)
    before = prep.admit(authority)
    assert not WORK.exists() and not WORK.is_symlink() and WORK.resolve() == WORK
    output = HERE / 'observer-v4-build-result.json'
    assert not output.exists() and not output.is_symlink()
    WORK.mkdir(mode=0o700)
    binary = WORK / 'observer.wasm'
    envelope = WORK / 'probe-with-observer.wasm'
    skeleton = WORK / 'envelope.skeleton.wat'
    steps = [
        ('parse', [WASM_TOOLS['path'], 'parse', OBSERVER_SOURCE['path'], '-o', str(binary)]),
        ('observer-validate', [WASM_TOOLS['path'], 'validate', str(binary)]),
        ('observer-wit', [WASM_TOOLS['path'], 'component', 'wit', str(binary)]),
        ('compose', [WAC['path'], 'plug', '--plug', inner['path'], str(binary), '-o', str(envelope)]),
        ('envelope-validate', [WASM_TOOLS['path'], 'validate', str(envelope)]),
        ('envelope-wit', [WASM_TOOLS['path'], 'component', 'wit', str(envelope)]),
        ('skeleton', [WASM_TOOLS['path'], 'print', '--skeleton', '--print-offsets', str(envelope), '-o', str(skeleton)]),
    ]
    result = dict(schemaVersion=1, state='ROOT_STANDARD_HANDLER_OBSERVER_V4_PROBE_BUILD_COLLECTING_V1',
        controller=self_ref, innerComponent=inner, innerConstructionReview=INNER_REVIEW,
        innerConstructionAuthority=INNER_AUTHORITY, observerSourceIndex=OBSERVER_INDEX,
        observerSource=OBSERVER_SOURCE, observerManifest=OBSERVER_MANIFEST, observerProtocol=OBSERVER_PROTOCOL, commands=[], error=None, finalizationErrors=[],
        constructorGuardBefore=before, constructorGuardAfter=None, finalInputsPreserved=False,
        runtimeInvoked=False, fullNextAccepted=False)
    primary = None
    try:
        for label, argv in steps:
            protect()
            out, err = WORK / (label + '.stdout.log'), WORK / (label + '.stderr.log')
            attempt = dict(label=label, argv=argv, rawExitCode=None, timeout=False, error=None, stdout=None, stderr=None)
            result['commands'].append(attempt)
            try:
                with out.open('xb') as stdout, err.open('xb') as stderr:
                    completed = subprocess.run(argv, cwd=WORK, env=dict(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C'),
                        stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=120, check=False)
                attempt['rawExitCode'] = completed.returncode
            except BaseException as error:
                attempt['timeout'] = isinstance(error, subprocess.TimeoutExpired)
                attempt['error'] = dict(name=type(error).__name__, message=str(error)[:2048])
                raise
            finally:
                for key, path in [('stdout', out), ('stderr', err)]:
                    if path.exists():
                        try:
                            attempt[key] = prep.row(path)
                        except BaseException as error:
                            if attempt['error'] is None:
                                raise
                            result['finalizationErrors'].append(dict(stage=label + '-' + key, name=type(error).__name__, message=str(error)[:2048]))
            assert completed.returncode == 0, 'Composition tool failed: ' + label
        result.update(observerBinary=prep.row(binary), envelope=prep.row(envelope), actualSkeleton=prep.row(skeleton),
            observerWit=prep.row(WORK / 'observer-wit.stdout.log'), externalWit=prep.row(WORK / 'envelope-wit.stdout.log'), allRequestedToolStepsPassed=True)
    except BaseException as error:
        primary = error
        result['error'] = dict(name=type(error).__name__, message=str(error)[:2048])
    finally:
        try:
            result['constructorGuardAfter'] = prep.admit(authority)
            protect()
            result['finalInputsPreserved'] = True
        except BaseException as error:
            if primary is None:
                primary = error
            result['finalizationErrors'].append(dict(stage='final-admission', name=type(error).__name__, message=str(error)[:2048]))
        result['state'] = ('ROOT_STANDARD_HANDLER_OBSERVER_V4_PROBE_BUILD_COMPLETED_UNREVIEWED_V1'
            if primary is None else 'ROOT_STANDARD_HANDLER_OBSERVER_V4_PROBE_BUILD_FAILED_PRESERVED_V1')
        try:
            receipt = prep.save(output, result)
            print(json.dumps(dict(result=receipt, state=result['state'], runtimeInvoked=False)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
