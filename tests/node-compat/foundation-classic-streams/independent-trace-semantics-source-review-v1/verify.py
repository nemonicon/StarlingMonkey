"""Read-only source/data reconstruction. No Node, generator, build or guest run."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import posixpath
import re

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OWNER = BASE / 'trace-semantics-candidate-v1'
REPO = BASE.parents[2]
CANONICAL = REPO / 'builtins/node-compat/classic-streams'
INDEX = '59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631'
verified = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, digest=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert digest is None or sha(data) == digest, path
    assert size is None or len(data) == size, path
    verified[str(path)] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    return data


def document(path, digest=None):
    return json.loads(read(path, digest))


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def main():
    index = document(OWNER / 'index.json', INDEX)
    assert len(index['files']) == 65
    for row in index['files']:
        read(OWNER / row['path'], row['sha256'], row['bytes'])
    source = document(OWNER / 'input-freeze.json', '0492bd99bffd97ad8ab9c7a0269e13d7235916466058a1cfc74b7f2b3e3582ef')
    assert len(source['inputs']) == 488
    for row in source['inputs']:
        read(row['path'], row['sha256'], row['bytes'])
    for row in document(OWNER / 'primary-source-pins.json')['sources']:
        assert row['url'].startswith('https://raw.githubusercontent.com/nodejs/node/v22.14.0/lib/internal/streams/')
        read(OWNER / row['path'], row['sha256'], row['bytes'])
    assert document(OWNER / 'primary-source-pins.json')['release'] == 'v22.14.0'
    for name in ['LICENSE.node', 'LICENSE.readable-stream']:
        assert read(OWNER / name) == read(CANONICAL / name)
    node_writable = read(OWNER / 'node-v22.14.0/writable.js').decode()
    for text in ["if ((state[kState] & kObjectMode) === 0)", "encoding = null;", "const ret = state.length < state.highWaterMark || state.length === 0;", "return ret && (state[kState] & (kDestroyed | kErrored)) === 0;"]:
        assert text in node_writable
    assert node_writable.index('stream._write(chunk, encoding, state.onwrite);', node_writable.index('function writeOrBuffer')) < node_writable.index('const ret = state.length < state.highWaterMark', node_writable.index('function writeOrBuffer'))
    assert 'Permission is hereby granted' in node_writable and 'Permission is hereby granted' in read(OWNER / 'LICENSE.node').decode()
    proof = document(OWNER / 'transformation-proof.json')
    assert len(proof['edits']) == 5
    before = read(OWNER / 'before/writable.transformed.js', proof['writableBeforeSha256']).decode()
    after = before
    for edit in proof['edits']:
        assert after.count(edit['old']) == edit['count'] == 1
        assert after.index(edit['old']) == edit['offset']
        after = after.replace(edit['old'], edit['new'])
    assert after.encode() == read(OWNER / 'proposed/writable.transformed.js', proof['writableAfterSha256'])
    reverse = after
    for edit in reversed(proof['edits']):
        offset = edit['offset']
        assert reverse[offset:offset+len(edit['new'])] == edit['new']
        reverse = reverse[:offset] + edit['old'] + reverse[offset+len(edit['new']):]
    assert reverse == before
    old_receipt = document(CANONICAL / 'transformation-receipt.json')
    receipt = document(OWNER / 'proposed/transformation-receipt.json')
    assert old_receipt['rawSources'] == receipt['rawSources'] and len(receipt['rawSources']) == 24
    writable_id = 'readable-stream/lib/internal/streams/writable.js'
    for old, new in zip(old_receipt['transformations'], receipt['transformations']):
        if old['path'] == writable_id:
            assert new['edits'][:-5] == old['edits']
            assert new['edits'][-5:] == [{key: edit[key] for key in ['old', 'new', 'count']} for edit in proof['edits']]
            assert new['afterSha256'] == proof['writableAfterSha256']
        else:
            assert old == new
    modules = []
    ids = {row['path'].replace('readable-stream/', '', 1) for row in receipt['rawSources']}
    for row in receipt['rawSources']:
        body = read(CANONICAL / 'vendor' / row['path'], row['sha256']).decode()
        record = next(record for record in receipt['transformations'] if record['path'] == row['path'])
        assert record['beforeSha256'] == row['sha256']
        for edit in record['edits']:
            if 'old' in edit:
                assert body.count(edit['old']) == edit['count']
                body = body.replace(edit['old'], edit['new'])
            elif 'replacement' in edit:
                assert edit['replacement'] in ['captured-primordials.cjs', 'private-util.cjs']
                body = read(CANONICAL / edit['replacement']).decode()
            elif 'append' in edit:
                body += '\n'+edit['append']+'\n'
            else:
                raise AssertionError('Unknown transformation')
        module_id = row['path'].replace('readable-stream/', '', 1)
        def require(match):
            target = match.group(2)
            if target.startswith('.'):
                target = posixpath.normpath(posixpath.join(posixpath.dirname(module_id), target))
                if not target.endswith('.js'):
                    target += '.js'
                assert target in ids
            else:
                assert target in ['buffer', 'events', 'string_decoder/', 'abort-controller']
            return 'require('+compact(target)+')'
        body = re.sub(r'\brequire\(([\'"])([^\'"]+)\1\)', require, body)
        assert sha(body.encode()) == record['afterSha256']
        modules.append(compact(module_id)+': function(module, exports, require) {\n'+body+'\n}')
    core = read(CANONICAL / 'core-prefix.mjs').decode()+'\nconst modules = {\n'+',\n'.join(modules)+'\n};\n'+read(CANONICAL / 'core-suffix.mjs').decode()
    assert core.encode() == read(OWNER / 'proposed/classic-core.generated.mjs', proof['candidateCoreSha256'])
    old_core = read(CANONICAL / 'classic-core.generated.mjs', proof['canonicalCoreBeforeSha256']).decode()
    assert old_core.count(before) == 1 and old_core.replace(before, after) == core
    assert read(OWNER / 'proposed/classic-streams.mjs') == read(CANONICAL / 'classic-streams.mjs')
    facade = read(CANONICAL / 'classic-streams.mjs').decode().replace("import {createClassicCore} from './classic-core.generated.mjs';\n", '')
    facade = re.sub(r'^export function ', 'function ', facade, flags=re.M)
    manifest = document(CANONICAL / 'export-manifest.classic-streams.node-v22.14.0.json')
    factory = "(function(dependencies){\n'use strict';\n"+re.sub(r'^export function ', 'function ', core, flags=re.M)+'\n'+facade+'\nreturn createClassicStreams(dependencies);\n})'
    header = '// Generated source-only classic candidate; do not edit.\n// Canonical-source SHA-256: '+sha((core+'\0'+facade+'\0'+compact(manifest)).encode())+'\nstatic constexpr const char kClassicStreamsFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\n'
    assert header.encode() == read(OWNER / 'proposed/factories.generated.h')
    patch = ''
    changes = document(OWNER / 'source-receipt.json')['intendedNativeSourceChanges']
    assert len(changes) == 3
    for row in changes:
        old = read(REPO / row['path'], row['beforeSha256'], row['beforeBytes'])
        new = read(OWNER / 'proposed' / Path(row['path']).name, row['afterSha256'], row['afterBytes'])
        patch += ''.join(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True), fromfile='a/'+row['path'], tofile='b/'+row['path']))
    assert patch.encode() == read(OWNER / 'canonical-3file.UNAPPLIED.patch')
    for file in ['workload/workload.mjs', 'workload/node-provider.mjs']:
        assert read(OWNER / file) == read(BASE / 'measurement-workload-candidate-v1' / Path(file).name)
    summary = document(OWNER / 'host-comparison-summary.json')
    full = document(summary['fullReportReference']['path'], summary['fullReportReference']['sha256'])
    assert len(full['workloadCases']) == len(full['workloadObserved']) == 20
    original = document(full['originalWorkloadCounterexamplesPreserved']['path'], full['originalWorkloadCounterexamplesPreserved']['sha256'])
    assert len(original['canonicalHostCounterexamples']) == 14
    for expected, observed in zip(original['expected'], full['workloadObserved']):
        assert observed == expected['oracle']
    assert full['minimalNode'] == full['minimalCandidate'] and len(full['minimalNode']) == 8
    assert sum(row['originalMatches'] is False for row in full['minimalCases']) == 4
    assert full['legacyCases'] == 19 and full['legacyExactMatches'] and full['legacyFirstDifference'] is None
    assert full['sameRealNodeDependencies'] and full['sameRealProcessNextTick'] and not full['schedulerPatched'] and not full['traceNormalized']
    for name, digest in full['sourceHashes'].items():
        read(OWNER / name, digest)
    encoding = document(OWNER / 'encoding-results.json')
    assert len(encoding['expected']) == 14 and encoding['after'] == encoding['expected']
    assert sum(row['originalMatches'] is False for row in encoding['cases']) == 11
    ablation = document(OWNER / 'ablation-summary.json')
    ablation_raw = document(ablation['reference']['path'], ablation['reference']['sha256'])
    returns = next(row for row in ablation_raw['results'] if row['group'] == 'returns')
    assert [row['observed'] for row in returns['minimal']] == ablation_raw['expectedRepro']
    for group in ['encoding', 'returns']:
        text = before
        indices = [0, 1, 2] if group == 'encoding' else [3, 4]
        for i in indices:
            text = text.replace(proof['edits'][i]['old'], proof['edits'][i]['new'])
        assert read(OWNER / 'ablations' / group / 'classic-core.generated.mjs').decode() == old_core.replace(before, text)
    assert read(OWNER / 'ablations/returns-encoding/classic-core.generated.mjs').decode() == core
    # The retained afterWrite experiment is not silently included in final5.
    start, end = before.index('function afterWrite('), before.index('function errorBuffer(', before.index('function afterWrite('))
    assert before[start:end] in after and before[start:end] in core
    assert document(OWNER / 'source-receipt.json')['liveSource342Changed'] is False
    for path in OWNER.rglob('*.py'):
        ast.parse(path.read_text())
    for path, row in list(verified.items()):
        read(path, row['sha256'], row['bytes'])
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_UNAPPLIED_WRITABLE_SEMANTICS_SOURCE_REVIEW_PASSED',
        'sourceIndexSha256': INDEX, 'indexedFiles': 65, 'sealedInputFiles': 488, 'rawVendorModules': 24,
        'exactWritableEdits': 5, 'productionAfterimages': 3, 'rawGraphAndAllOtherModuleTransformsUnchanged': True,
        'coreAndHeaderIndependentlyReconstructed': True, 'threeFilePatchExact': True,
        'recordedFullWorkloadDataExact': 20, 'recordedMinimalPublicDataExact': 8, 'recordedEncodingBoundaryDataExact': 14,
        'legacy19': 'Reported equality/source assertion independently inspected; full observed legacy array was not retained for independent data-only equality.',
        'returnOnlyAblationMatchesMinimal8': True, 'unnecessaryAfterWriteExperimentExcluded': True,
        'schedulerOrWorkloadOrOracleOrSurfaceChanged': False,
        'scope': 'Source and existing raw-data review only. No owner helper, generator, Node workload, guest, native build, packaging, host or timing rerun.',
        'adoptionRequirements': ['New explicit policy/recipe/source hashes and fresh native/component gates are required.',
            'Retain primary-source-pin/MIT provenance in the future artifact tooling closure; the receipt annotation path is proposal-relative, not a deployed runtime lookup.',
            'Host Node nextTick equality does not prove the private guest queue or all topologies. Existing342/native pins remain old semantics.',
            'Stock Jco is unchanged and its separate counterexamples remain. No performance or complete Node streams claim.'],
        'verifiedFiles': sorted(verified.values(), key=lambda row: row['path'])}
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ['state', 'indexedFiles', 'sealedInputFiles', 'recordedFullWorkloadDataExact']}))


if __name__ == '__main__':
    main()
