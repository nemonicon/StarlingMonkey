"""Read DATA and create unapplied afterimages. No owner module is imported."""
import copy
import difflib
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
Z = HERE.parent
SOURCE = Path('/private/tmp/starling-node-compat/zlib-source-v4')
FROZEN = Path('/private/tmp/starling-node-compat/production-zlib-v4/native-freeze')
REVIEW = Z / 'independent-normal-codec-validation-v2-results-review-v1'
GUEST = Z / 'component-validation-activated-v8'
inputs = {}


def read(path, expected=None):
    path = Path(path).absolute()
    data = path.read_bytes()
    row = {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    if expected:
        assert row['sha256'] == expected['sha256'], path
        if 'bytes' in expected:
            assert row['bytes'] == expected['bytes'], path
    assert inputs.get(str(path), row) == row
    inputs[str(path)] = row
    return data


def load(path):
    return json.loads(read(path))


def write(name, value):
    target = HERE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2) + '\n')


ledger = load(REVIEW / 'node-profile-difference-ledger.json')
constant_ledger = load(REVIEW / 'constant-difference-ledger.json')
oracle = load(GUEST / 'node-results.json')
corpus = read(GUEST / 'corpus.mjs').decode()
assert oracle['node'] == 'v22.14.0' and len(oracle['cases']) == 61
assert len(ledger['rows']) == 22 and len(ledger['allErrorComparisons']) == 31
assert sum(r['observationCount'] for r in ledger['rows']) == 100
assert [r['index'] for r in oracle['cases']] == list(range(61))
assert 'MAX_INPUT=1048576,MAX_OUTPUT=16777216' in corpus
for row in oracle['dataFiles']:
    read(row['path'], row)  # Binary fixture DATA, not decoded or executed.

policy = load(Z / 'native-integration-candidate-v4/policy.json')
read(Z / 'native-integration-candidate-v4/index.json')
assert len(policy['expectedNativeSourceManifest']) == 350
for row in policy['expectedNativeSourceManifest']:
    read(SOURCE / row['path'], row)
    read(FROZEN / 'source' / row['path'], row)
receipt = load(FROZEN / 'normal-off-freeze-receipt.json')
assert receipt['engineSha256'] == 'fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'
read(receipt['engine'], {'sha256': receipt['engineSha256'], 'bytes': receipt['engineBytes']})
metadata = load(FROZEN / 'normal-off.engine.wasm.build.json')
assert receipt['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}

corrected_domain = load(Z / 'node-deviation-contract-mutability-amendment-v1/proposed/contract.proposal.json')
read(Z / 'node-deviation-contract-mutability-amendment-v1/index.json')
for row in corrected_domain['nodePrimarySources']:
    read(row['path'], row)
read(GUEST / 'component.mjs')
read(GUEST / 'activation.json')
for name in ('index.json', 'results.json'):
    read(REVIEW / name)
decision = load(Z / 'cost-timing-v5-root-decision.json')
assert decision['operationalAdmission'] is False and decision['sourcePromotionAllowed'] is False
for row in decision['independentReview'].values():
    read(row['path'], row)

# Verify every retained compared error observation without running its producer.
for record in ledger['allErrorComparisons']:
    assert oracle['cases'][record['index']]['node'] == record['nodeOutcomeAndErrorAsRecorded']
    for citation in record['citations']['guestRawObservations']:
        observation = json.loads(read(citation['path']))
        assert observation['index'] == record['index'] and observation['id'] == record['id']
        assert observation['error'] == record['profileErrorAsObserved']
        assert observation['outcome'] == 'error' and observation['partialOutputPublished'] is False

kernel_path = 'builtins/node-compat/zlib/kernel.cpp'
manifest_path = 'builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'
factory_path = 'builtins/node-compat/zlib/factories.generated.h'
kernel = read(SOURCE / kernel_path).decode()
edits = []


def replace_once(label, before, after):
    global kernel
    assert kernel.count(before) == 1, label
    kernel = kernel.replace(before, after)
    edits.append({'label': label, 'before': before, 'after': after})


replace_once('explicit optional codec errno', '#include <cstring>\n', '#include <cstring>\n#include <optional>\n')
replace_once('dictionary is codec need, not added dictionary support',
             'DEF_ERR(NeedsDictionary, JSEXN_ERR, "Zlib dictionaries are not supported by this profile", 0)',
             'DEF_ERR(NeedsDictionary, JSEXN_ERR, "Missing dictionary", 0)')
replace_once('errno is absent unless explicitly supplied',
             'const char *code, int status = Z_OK) {',
             'const char *code, std::optional<int> codec_errno = std::nullopt) {')
replace_once('attach only a selected codec errno',
             '    JS::RootedValue number(cx, JS::Int32Value(status));\n    if (!JS_DefineProperty(cx, error, "errno", number, JSPROP_ENUMERATE)) return false;',
             '    // A profile refusal is not a zlib errno, even when the last codec\n'
             '    // status was Z_OK or Z_STREAM_END. Never expose that diagnostic\n'
             '    // as a Node-style errno. Only actual codec errors opt in.\n'
             '    if (codec_errno) {\n'
             '      JS::RootedValue number(cx, JS::Int32Value(*codec_errno));\n'
             '      if (!JS_DefineProperty(cx, error, "errno", number, JSPROP_ENUMERATE)) return false;\n'
             '    }')
replace_once('backend mismatch remains profile error',
             'return fail(cx, BackendMismatch, "ERR_SM_ZLIB_BACKEND_MISMATCH", Z_VERSION_ERROR);',
             'return fail(cx, BackendMismatch, "ERR_SM_ZLIB_BACKEND_MISMATCH");')
for label, before, after in [
    ('input cap has no codec errno', 'InputLimit, "ERR_OUT_OF_RANGE", result.zlib_status', 'InputLimit, "ERR_OUT_OF_RANGE"'),
    ('output cap has no codec errno', 'OutputLimit, "ERR_BUFFER_TOO_LARGE", result.zlib_status', 'OutputLimit, "ERR_BUFFER_TOO_LARGE"'),
    ('invalid data uses its actual codec error class', 'InvalidData, "Z_DATA_ERROR", result.zlib_status', 'InvalidData, "Z_DATA_ERROR", Z_DATA_ERROR'),
    ('incomplete data uses Node codec error class', 'IncompleteData, "Z_BUF_ERROR", result.zlib_status', 'IncompleteData, "Z_BUF_ERROR", Z_BUF_ERROR'),
    ('dictionary-required code and errno', 'NeedsDictionary, "ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED", result.zlib_status', 'NeedsDictionary, "Z_NEED_DICT", Z_NEED_DICT'),
    ('trailing policy has no codec errno', 'TrailingData, "ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED", result.zlib_status', 'TrailingData, "ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED"'),
]:
    replace_once(label, '    return fail(cx, ' + before + ');',
                 '    return fail(cx, ' + after + ');')
before = 'InternalFailure, "ERR_SM_ZLIB_INTERNAL", result.zlib_status'
assert kernel.count(before) == 2
kernel = kernel.replace(before, 'InternalFailure, "ERR_SM_ZLIB_INTERNAL"')
edits.append({'label': 'both internal fallback returns omit diagnostic errno', 'before': before,
              'after': 'InternalFailure, "ERR_SM_ZLIB_INTERNAL"', 'occurrences': 2})
target = HERE / 'after' / kernel_path
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(kernel)

old_manifest = read(SOURCE / manifest_path)
manifest = json.loads(old_manifest)
manifest['status'] = 'UNAPPLIED error-semantics successor; no new build, runtime result, backend-version proof or installed support.'
deviations = manifest['modules']['node:zlib']['deviations']
assert deviations[4] == 'Frozen null-prototype constants/codes and frozen default differ from Node mutability; Z_MAX_CHUNK remains numeric Infinity.'
deviations[4] = ('The profile freezes its default/constants/codes and uses null-prototype constants/codes. '
                 'Pinned Node22 also freezes codes; that alone is not a deviation. Other Node descriptor/prototype/mutability '
                 'comparisons require separate evidence. Z_MAX_CHUNK remains numeric Infinity.')
deviations.append('Error-semantics proposal: only Z_DATA_ERROR, Z_BUF_ERROR and Z_NEED_DICT carry numeric codec errno; '
                  'profile limits/refusals/backend/internal errors omit errno. Dictionary-required input throws Z_NEED_DICT '
                  'without enabling dictionaries. Six errno-only and one dictionary-code ledger differences are targeted; '
                  '15 other recorded differences remain explicit and unapproved. Error messages/descriptors are not claimed fully Node-identical.')
new_manifest = (json.dumps(manifest, indent=2) + '\n').encode()
(HERE / 'after' / manifest_path).write_bytes(new_manifest)


def factory(manifest_bytes):
    # Transcription of the pinned generator's DATA transform, never importing it.
    c = read(SOURCE / 'builtins/node-compat/zlib/constant-data.generated.mjs').decode()
    f = read(SOURCE / 'builtins/node-compat/zlib/facade.mjs').decode()
    digest = hashlib.sha256()
    for name, source in [('constant-data.generated.mjs', c), ('facade.mjs', f),
                         ('export-manifest.zlib.node-v22.14.0.json', manifest_bytes.decode())]:
        digest.update((name + '\0' + source + '\0').encode())
    dependency = "import {createZlibData} from './constant-data.generated.mjs';"
    assert f.count(dependency) == 1
    f = f.replace(dependency, '')
    c = re.sub(r'^export function ', 'function ', c, flags=re.M)
    f = re.sub(r'^export function ', 'function ', f, flags=re.M)
    body = "(function(argument){\n'use strict';\n" + c + '\n' + f + '\nreturn createZlibModule(argument.kernel, argument.Buffer);\n})'
    return ('// Generated unapplied bounded zlib proposal; do not edit.\n'
            '// Canonical-source SHA-256: ' + digest.hexdigest() + '\n'
            'static constexpr const char kZlibFactorySource[] = R"SM_NODE_PROFILE(' + body + ')SM_NODE_PROFILE";\n').encode()


assert factory(old_manifest) == read(SOURCE / factory_path)
(HERE / 'after' / factory_path).write_bytes(factory(new_manifest))
read(SOURCE / 'builtins/node-compat/manifest.schema.json')
read(SOURCE / 'builtins/node-compat/register.cpp')
read(SOURCE / 'builtins/node-compat/zlib/generate-factory.mjs')
read(Path('/private/tmp/starling-node-compat/zlib-v4-build/spidermonkey-dist-release/include/zlib.h'))

errno_indices = {7, 10, 24, 27, 41, 44}
categories = {12: 'OUTPUT_CAP', 29: 'OUTPUT_CAP', 46: 'OUTPUT_CAP',
              15: 'STRICT_MEMBER_OR_TRAILING', 16: 'STRICT_MEMBER_OR_TRAILING',
              32: 'STRICT_MEMBER_OR_TRAILING', 33: 'STRICT_MEMBER_OR_TRAILING',
              49: 'STRICT_MEMBER_OR_TRAILING', 50: 'STRICT_MEMBER_OR_TRAILING',
              52: 'INPUT_CAP', 53: 'INPUT_CAP', 56: 'FRACTIONAL_OPTION',
              58: 'OPTION_ABOVE_PROFILE_CAP', 59: 'UNSUPPORTED_LEVEL_OPTION', 60: 'BYTE_ONLY_INPUT'}
routes = {
    'OUTPUT_CAP': ('Kept finite16MiB output bound; not globally unavoidable Node behavior.',
                   'A separately reviewed larger or streaming profile, allocation policy and fresh correctness/cost evidence are required to remove the cap deviation.'),
    'STRICT_MEMBER_OR_TRAILING': ('Kept strict single-member/no-trailing policy; not a codec limitation proven unavoidable.',
                   'Separate per-format design must distinguish concatenated gzip decoding from zlib/raw trailing handling, consume exact byte windows, preserve output budget across members, then compare full bytes with Node.'),
    'INPUT_CAP': ('Kept1MiB admission before codec, including the resulting error precedence.',
                   'Changing the cap/precedence requires a separately reviewed input/allocator policy and fresh correctness/cost evidence; do not codec-probe rejected input to imitate a Node error.'),
    'FRACTIONAL_OPTION': ('Current integer-only contract remains a deliberate unapproved option deviation.',
                   'A future fractional compatibility change can use floor(value) as an integer byte bound after real Node range-validation source is pinned, while preserving Number type/NaN/infinity and precedence behavior; no such change is implemented here.'),
    'OPTION_ABOVE_PROFILE_CAP': ('Current option range is1..16MiB even when actual output would be small.',
                   'Separate decision: accept a Node-valid larger requested maximum but enforce a distinct internal16MiB budget. Pin Node kMaxLength/range semantics and keep profile-budget failures explicit; do not silently clamp or expand resources.'),
    'UNSUPPORTED_LEVEL_OPTION': ('Only maxOutputLength is admitted; level1 is refused.',
                   'Adding level requires genuine native option propagation, range tests and fresh codec/cost validation. Never ignore a recognized option or substitute a provider.'),
    'BYTE_ONLY_INPUT': ('No string encoding is admitted.',
                   'A future explicit string/encoding conversion layer must define UTF8/encoding errors, length accounting and bounded staging; separate source/native/correctness/cost validation required.'),
}
rows = []
for r in ledger['rows']:
    x = copy.deepcopy(r)
    if r['index'] in errno_indices:
        x['remediation'] = {'classification': 'FIXABLE_ERROR_FORM', 'implementedInUnappliedAfterimage': True,
                            'change': 'Omit errno on profile OutputLimit error; preserve RangeError/code and all historical observations.',
                            'predictedComparedDifferencesAfterNewBuild': [], 'runtimeVerified': False}
    elif r['index'] == 51:
        x['remediation'] = {'classification': 'FIXABLE_CODEC_ERROR_CODE', 'implementedInUnappliedAfterimage': True,
                            'change': 'Use actual codec Z_NEED_DICT code/errno2 and Missing dictionary message; no dictionary support added.',
                            'predictedComparedDifferencesAfterNewBuild': [], 'runtimeVerified': False}
    else:
        category = categories[r['index']]
        x['remediation'] = {'classification': category, 'implementedInUnappliedAfterimage': False,
                            'boundedContract': routes[category][0], 'nodeGoalFollowOn': routes[category][1],
                            'predictedComparedDifferencesAfterNewBuild': r['comparisonDifferences'], 'runtimeVerified': False}
    rows.append(x)
write('difference-remediation.json', {'schemaVersion': 1, 'state': 'UNAPPROVED_SOURCE_ONLY_22_ROW_REMEDIATION',
      'historicalRowsPreserved': True, 'originalNullDeviationLabelsPreserved': 11,
      'observedDifferentCases': 22, 'observedDifferentRawErrorRecords': 100,
      'afterimageTargetedCases': 7, 'afterimageTargetedObservedRecords': 35,
      'remainingDifferentCasesPredictedNotExecuted': 15, 'remainingDecisionsApproved': False,
      'sourceCoupledVernumSeparate': True, 'rows': rows})

comparisons = {r['index']: r for r in ledger['allErrorComparisons']}
diffs = {r['index']: r for r in rows}
inventory = []
for r in oracle['cases']:
    inventory.append({'index': r['index'], 'id': r['id'], 'node': r['node'],
                      'historicalProfileExpectedKind': r['profileExpectedKind'],
                      'historicalProfileExpectedCode': r['profileExpectedCode'], 'historicalDeviation': r['deviation'],
                      'historicalErrorComparison': comparisons.get(r['index']),
                      'remediation': diffs[r['index']]['remediation'] if r['index'] in diffs else
                      {'classification': 'NO_RECORDED_ERROR_DIFFERENCE', 'runtimeVerifiedSuccessor': False},
                      'citations': {'nodeOracle': str(GUEST / 'node-results.json'), 'jsonPointer': '/cases/' + str(r['index']),
                                    'corpus': str(GUEST / 'corpus.mjs')}})
write('complete-case-inventory.json', {'schemaVersion': 1, 'cases': inventory, 'caseCount': 61,
      'profileErrorComparisonCount': 31, 'historicalDifferentCaseCount': 22, 'noNewRuntimeClaim': True})

changed = [kernel_path, manifest_path, factory_path]
records = []
patch = ''
for relative in changed:
    before = read(SOURCE / relative)
    after = (HERE / 'after' / relative).read_bytes()
    records.append({'path': relative, 'before': inputs[str(SOURCE / relative)],
                    'after': {'path': str(HERE / 'after' / relative), 'sha256': hashlib.sha256(after).hexdigest(), 'bytes': len(after)},
                    'kind': 'EXACT_REVERSIBLE_EDITS' if relative == kernel_path else
                            'MANIFEST_JSON_DERIVATION' if relative == manifest_path else 'PINNED_FACTORY_DATA_TRANSFORM',
                    'edits': edits if relative == kernel_path else []})
    patch += ''.join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True),
                                        fromfile='a/' + relative, tofile='b/' + relative))
(HERE / 'node-error-semantics.UNAPPLIED.patch').write_text(patch)
write('derivations.json', {'schemaVersion': 1, 'nativeSourceCount': 350, 'changedSourceCount': 3,
      'unchangedSourceCount': 347, 'cppBehaviorChanges': 1,
      'factoryRuntimeCodeUnchanged': True, 'facadeBoundedCodecConstantsAndRegistrationsUnchanged': True,
      'records': records})
write('references.json', {'schemaVersion': 1, 'roles': {
      'historicalNormalResultIndex': inputs[str(REVIEW / 'index.json')],
      'historicalDifferenceLedger': inputs[str(REVIEW / 'node-profile-difference-ledger.json')],
      'historicalConstantLedger': inputs[str(REVIEW / 'constant-difference-ledger.json')],
      'nodeOracle': inputs[str(GUEST / 'node-results.json')], 'corpus': inputs[str(GUEST / 'corpus.mjs')],
      'source350Policy': inputs[str(Z / 'native-integration-candidate-v4/policy.json')],
      'actualNormalFreezeReceipt': inputs[str(FROZEN / 'normal-off-freeze-receipt.json')],
      'actualNormalMetadata': inputs[str(FROZEN / 'normal-off.engine.wasm.build.json')],
      'costDecision': inputs[str(Z / 'cost-timing-v5-root-decision.json')],
      'correctedDeviationProposal': inputs[str(Z / 'node-deviation-contract-mutability-amendment-v1/proposed/contract.proposal.json')]}})
write('input-freeze.json', {'schemaVersion': 1, 'state': 'FINITE_SOURCE_AND_HISTORICAL_DATA_ONLY',
      'files': sorted(inputs.values(), key=lambda r: r['path']),
      'contexts': {'configuredSource': str(SOURCE), 'frozenSource': str(FROZEN / 'source'),
                   'originalProposal': str(HERE), 'historicalPreparationContextsExecuted': False}})
print(json.dumps({'state': 'SOURCE_AFTERIMAGES_PREPARED_NOT_EXECUTED', 'inputRows': len(inputs),
                  'cases': 61, 'differences': 22, 'targeted': 7, 'remainingPredicted': 15,
                  'changedSourceFiles': 3, 'nodeCodecCompilerHelpersOrGuestsExecuted': False}))
