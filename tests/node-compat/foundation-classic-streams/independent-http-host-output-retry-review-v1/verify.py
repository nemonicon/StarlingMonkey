"""Independent data/source review only; never imports a JS host or preflight."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OWNER = BASE / 'http-host-output-retry-candidate-v1'
INDEX_SHA = '89b133b5d78ae35a1c60f82d2d9d2c37fb44f7da88312efdc806f210dde5554d'
INPUT_SHA = '879d8c24241380fe8391e66056579f941cc3bb587f130c296b83d8c4f7062158'
PHASE_SHA = 'eb1caa1168f57f135c1b38c924ef1ce99305aa34688419edd5847e242a5f9c29'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, digest=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert digest is None or sha(data) == digest, path
    assert size is None or len(data) == size, path
    return data


def main():
    index_bytes = read(OWNER / 'index.json', INDEX_SHA)
    index = json.loads(index_bytes)
    assert len(index['files']) == 15
    checked = {}
    for row in index['files']:
        path = OWNER / row['path']
        assert path not in checked
        data = read(path, row['sha256'], row['bytes'])
        checked[path] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    input_bytes = read(OWNER / 'input-freeze.json', INPUT_SHA)
    rows = json.loads(input_bytes)['inputs']
    assert len(rows) == 83
    input_paths = set()
    for row in rows:
        path = (OWNER / row['path']).resolve()
        assert path not in input_paths
        input_paths.add(path)
        data = read(path, row['sha256'], row['bytes'])
        checked[path] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    template = read(OWNER / 'verify-retry.template.mjs').decode()
    assert template.count('@INPUTS_SHA@') == 1
    assert template.replace('@INPUTS_SHA@', INPUT_SHA).encode() == read(OWNER / 'verify-retry.mjs')
    proof = json.loads(read(OWNER / 'transformation-proof.json'))
    assert len(proof['records']) == 2
    for record in proof['records']:
        original = read(BASE / 'classic-http-candidate-v1' / record['original'], record['beforeSha256'])
        after = read(OWNER / record['target'], record['afterSha256']).decode()
        for edit in reversed(record['edits']):
            assert after.count(edit['new']) == edit['occurrences']
            after = after.replace(edit['new'], edit['old'])
        assert after.encode() == original
    phase_path = BASE / 'production-adoption-v1/http-component-phase-root-review-v1.json'
    alternate_path = Path('/tmp/starling-node-compat/classic-http-root-reviewed-phase-v1.json')
    phase_bytes = read(phase_path, PHASE_SHA)
    assert phase_bytes == read(alternate_path, PHASE_SHA)
    phase = json.loads(phase_bytes)
    assert phase['state'] == 'ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1'
    assert phase['component']['componentSha256'] == '25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d'
    assert phase['component']['componentBytes'] == 64057853
    assert phase['component']['sourceInputSha256'] == '511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b'
    assert phase['component']['sourceEntryPath'] == str(BASE / 'classic-http-candidate-v1/capability/http-component.mjs')
    assert phase['component']['root'] == '/tmp/starling-node-compat/production-classic-http-v1/http'
    entry = read(OWNER / 'run-http-wasmtime.mjs').decode()
    body_import = "await import('./run-http-wasmtime-body.mjs')"
    assert entry.index('requireSupportedFixtureOptions(process.env);') < entry.index(body_import)
    assert entry.index('await verifyRetrySource();') < entry.index(body_import)
    assert entry.index(body_import) < entry.index('await source.recheck();')
    assert 'NODE_COMPAT_HTTP_REQUIRE_INTRINSICS=' not in entry
    pure_path = Path('/tmp/starling-node-compat/independent-http-host-output-retry-review-v1/source-test-results.json')
    pure_bytes = read(pure_path)
    pure = json.loads(pure_bytes)
    assert pure['checks'] == pure['passed'] == 13
    assert pure['state'] == 'HTTP_FRESH_OUTPUT_RETRY_SOURCE_CHECKS_PASSED'
    assert pure['bodyOrPreflightImported'] is False and pure['componentOrGuestOrHostExecuted'] is False
    assert pure['reviewedPhaseSha256'] == PHASE_SHA and pure['ownManifestSha256'] == INPUT_SHA
    evidence = HERE / 'evidence/source-test-results.json'
    evidence.parent.mkdir(exist_ok=True)
    with evidence.open('xb') as stream:
        stream.write(pure_bytes)
    for path, record in checked.items():
        read(path, record['sha256'], record['bytes'])
    read(OWNER / 'index.json', INDEX_SHA)
    report = {
        'schemaVersion': 1,
        'state': 'INDEPENDENT_HTTP_FRESH_OUTPUT_RETRY_SOURCE_REVIEW_PASSED',
        'sourceIndexSha256': INDEX_SHA,
        'sourceManifestSha256': INPUT_SHA,
        'indexedFilesVerified': 15, 'sealedInputsVerified': 83,
        'reverseProofsVerified': 2, 'renderedTemplateExact': True,
        'freshPureChecks': 13, 'freshPureCommandExitCodeObserved': 0,
        'pureCommand': ['/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node', str(OWNER / 'test-source.mjs')],
        'pureOutputPath': str(pure_path), 'pureOutputSha256': sha(pure_bytes),
        'authorityDocument': {'requiredPath': str(phase_path), 'originalCopyPath': str(alternate_path), 'sha256': PHASE_SHA, 'byteEqual': True},
        'sourceReview': [
            'Approved entry rejects optional intrinsics=1 before host-body import; it never clears the option.',
            'Host body changes only imports and fixed fresh Wasmtime-v2 output; original host implementation is unchanged.',
            'Audit changes only imports and two Wasmtime-v2 report/completion references; validators and artifact/config checks are unchanged.',
            'Original phase data, component/build/source Entry paths, component hash and six-standard-interface policy remain unchanged.',
            'Original preflight still delegates real342/native/tool and 7518-source admission; this review did not invoke that preflight.',
            'Response validation and SIGINT/SIGKILL finally cleanup are retained by exact source ancestry.'
        ],
        'componentOrGuestOrHostOrPreflightOrPackagerOrNativeBuildExecuted': False,
        'runtimeAcceptanceClaim': False,
        'limitations': [
            'Future retry still needs independent raw terminal0, completed actual reports and same-byte both-host audit.',
            'This review rehashed the outer83-input seal; the unchanged nested7518 closure is delegated, not freshly executed here.',
            'Prior failed Wasmtime-v1 output is historical and not reused.',
            'Getter, Symbol, GC-coowner, ALS/reset and request-reuse limitations are unchanged.'
        ],
        'verifiedSourceFiles': sorted(checked.values(), key=lambda row: row['path'])
    }
    with (HERE / 'results.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: report[key] for key in ['state', 'indexedFilesVerified', 'sealedInputsVerified', 'freshPureChecks']}))


if __name__ == '__main__':
    main()
