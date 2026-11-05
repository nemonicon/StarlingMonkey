"""Finite DATA/source models. Never imports or executes a candidate/owner module."""
import ast
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
checks = 0
models = []


def check(value, label):
    global checks
    checks += 1
    if not value:
        raise AssertionError(label)


def load(path):
    return json.loads(Path(path).read_text())


freeze = load(HERE / 'input-freeze.json')
for r in freeze['files']:
    p = Path(r['path'])
    data = p.read_bytes()
    check(p.is_absolute(), 'explicit original absolute descriptor')
    check(len(data) == r['bytes'] and hashlib.sha256(data).hexdigest() == r['sha256'], 'actual source/data bytes')
derivations = load(HERE / 'derivations.json')
check(derivations['nativeSourceCount'] == 350 and derivations['unchangedSourceCount'] == 347, 'genuine350 inventory')
for record in derivations['records']:
    before = Path(record['before']['path']).read_bytes()
    after = Path(record['after']['path']).read_bytes()
    check(hashlib.sha256(after).hexdigest() == record['after']['sha256'], 'afterimage digest')
    check(len(after) == record['after']['bytes'], 'afterimage size')
    if record['edits']:
        reversed_source = after.decode()
        for edit in reversed(record['edits']):
            count = edit.get('occurrences', 1)
            check(reversed_source.count(edit['after']) == count, 'unique exact reverse ' + edit['label'])
            reversed_source = reversed_source.replace(edit['after'], edit['before'])
        check(reversed_source.encode() == before, 'complete kernel reversal')
    elif record['path'].endswith('factories.generated.h'):
        check(before.splitlines()[2:] == after.splitlines()[2:], 'generated factory executable bytes unchanged')
        check(before.splitlines()[0] == after.splitlines()[0], 'factory format unchanged')
    else:
        old, new = json.loads(before), json.loads(after)
        x = copy.deepcopy(new)
        x['status'] = old['status']
        x['modules']['node:zlib']['deviations'] = old['modules']['node:zlib']['deviations']
        check(x == old, 'only manifest status and deviation text changed')

kernel = (HERE / 'after/builtins/node-compat/zlib/kernel.cpp').read_text()
before_kernel = Path(derivations['records'][0]['before']['path']).read_text()
check('#include <optional>' in kernel, 'explicit standard optional dependency')
check('std::optional<int> codec_errno = std::nullopt' in kernel, 'absent errno default')
check('JS::Int32Value(*codec_errno)' in kernel and kernel.count('if (codec_errno) {') == 1, 'engaged optional property guard')
check('JS::Int32Value(status)' not in kernel and 'result.zlib_status' not in kernel, 'no private last-status leak')
check('Missing dictionary' in kernel, 'Node primary-source dictionary message')
check('ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED' not in kernel, 'dictionary-required old code removed')
check(kernel.count('JS_ReportOutOfMemory(cx)') == before_kernel.count('JS_ReportOutOfMemory(cx)'), 'OOM cleanup path unchanged')
check(kernel[kernel.index('// Private factory contract only:'):] ==
      before_kernel[before_kernel.index('// Private factory contract only:'):], 'whole run/ownership/output/factory unchanged')
check(kernel[kernel.index('static bool backend_info'):kernel.index('static bool codec_failure')] ==
      before_kernel[before_kernel.index('static bool backend_info'):before_kernel.index('static bool codec_failure')],
      'private backend API and actual version checks not replaced')

# Extract the actual proposed C++ switch return arguments as DATA. This is not
# C++ evaluation; the independent model below covers only this finite switch.
switch = kernel[kernel.index('static bool codec_failure'):kernel.index('// Private factory contract only:')]
pattern = re.compile(r'return fail\(cx, (\w+), "([A-Z0-9_]+)"(?:, (\w+))?\);')
returns = pattern.findall(switch)
check(len(returns) == 8, 'all finite fail returns including final fallback')
number = {'Z_DATA_ERROR': -3, 'Z_BUF_ERROR': -5, 'Z_NEED_DICT': 2, '': None}
policies = {kind: {'code': code, 'errno': number[errno]} for kind, code, errno in returns}
check(set(policies) == {'InputLimit', 'OutputLimit', 'InvalidData', 'IncompleteData', 'NeedsDictionary', 'TrailingData', 'InternalFailure'}, 'finite error map')
contract = load(HERE / 'error-contract.proposal.json')
for r in contract['codecErrors'] + contract['profileErrors']:
    kind = {'DictionaryRequired': 'NeedsDictionary', 'InternalError': 'InternalFailure', 'Ok': 'InternalFailure'}.get(r['status'], r['status'])
    check(policies[kind] == {'code': r['code'], 'errno': r['ownErrno']}, 'contract matches actual switch ' + kind)
check('case codec::Status::OutOfMemory:\n    JS_ReportOutOfMemory(cx);\n    return false;' in switch, 'OOM remains direct native failure')

sentinels = [-6, -5, -4, -3, -2, -1, 0, 1, 2]
for kind, policy in policies.items():
    for last_status in sentinels:
        # policy no longer depends on the retained result.zlib_status. This
        # tests semantic independence, not a real codec/error allocation.
        modeled = {'name': 'RangeError' if kind in ('InputLimit', 'OutputLimit') else 'Error', 'code': policy['code']}
        if policy['errno'] is not None:
            modeled['errno'] = policy['errno']
        check(('errno' in modeled) == (kind in ('InvalidData', 'IncompleteData', 'NeedsDictionary')), 'selective own errno')
        check(modeled.get('errno') not in (0, 1), 'never surface codec success/status errno')
        models.append({'kind': kind, 'lastDiagnosticStatus': last_status, 'modeledError': modeled,
                       'realCodecOrCppExecuted': False})

refs = load(HERE / 'references.json')['roles']
ledger = load(refs['historicalDifferenceLedger']['path'])
oracle = load(refs['nodeOracle']['path'])
remediation = load(HERE / 'difference-remediation.json')
inventory = load(HERE / 'complete-case-inventory.json')
check(len(inventory['cases']) == 61, 'full61 inventory')
check([r['index'] for r in inventory['cases']] == list(range(61)), 'no dropped or duplicated cases')
check(len(remediation['rows']) == 22, 'all22 differences')
check(sum(r['sourceDeviationValuePreserved'] is None for r in remediation['rows']) == 11, 'all11 null labels')
check(sum(r['observationCount'] for r in remediation['rows']) == 100, 'all100 differing observations retained')
check(sum(r['observationCount'] for r in ledger['allErrorComparisons']) == 145, 'all145 retained compared errors')
prediction = []
targeted, remaining = [], []
for original, proposal in zip(ledger['rows'], remediation['rows']):
    x = copy.deepcopy(proposal)
    del x['remediation']
    check(x == original, 'historical full row/citations untouched')
for original in ledger['allErrorComparisons']:
    profile = copy.deepcopy(original['profileErrorAsObserved'])
    fields = profile['fields']
    code = fields['code']['value']
    # Only native-generated errors have absent own operation. Facade errors
    # are unchanged. Same mapping is extracted from the proposed C++ switch.
    if not fields['operation']['own']:
        kind = {'ERR_BUFFER_TOO_LARGE': 'OutputLimit', 'ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED': 'TrailingData',
                'ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED': 'NeedsDictionary', 'Z_DATA_ERROR': 'InvalidData',
                'Z_BUF_ERROR': 'IncompleteData'}[code]
        policy = policies[kind]
        fields['code']['value'] = policy['code']
        fields['errno'] = {'own': policy['errno'] is not None,
                           'type': 'number' if policy['errno'] is not None else 'undefined', 'value': policy['errno']}
    n = original['nodeOutcomeAndErrorAsRecorded']
    differences = []
    if n['kind'] != 'error':
        differences.append('outcome')
    else:
        if n['name'] != profile['name']:
            differences.append('error.name')
        for field in ('code', 'errno'):
            # Node own-property flags were NOT captured. Compare typed value
            # only; never turn undefined into a Node-own-absence assertion.
            if n[field] != {k: fields[field][k] for k in ('type', 'value')}:
                differences.append('error.' + field)
    if original['comparisonDifferences'] and not differences:
        targeted.append(original['index'])
    if differences:
        remaining.append(original['index'])
    prediction.append({'index': original['index'], 'id': original['id'], 'modeledProfileError': profile,
                       'predictedComparedDifferences': differences, 'runtimeVerified': False})
check(targeted == [7, 10, 24, 27, 41, 44, 51], 'exact7 targeted rows')
check(remaining == [12, 15, 16, 29, 32, 33, 46, 49, 50, 52, 53, 56, 58, 59, 60], 'all15 remaining differences')
check(sum(not r['comparisonDifferences'] for r in ledger['allErrorComparisons']) == 9, 'all9 matching error rows preserved')
for item, r in zip(inventory['cases'], oracle['cases']):
    check(item['node'] == r['node'] and item['id'] == r['id'], 'complete Node outcome retained')
check(Counter(r['remediation']['classification'] for r in remediation['rows']) ==
      Counter({'FIXABLE_ERROR_FORM': 6, 'OUTPUT_CAP': 3, 'STRICT_MEMBER_OR_TRAILING': 6,
               'FIXABLE_CODEC_ERROR_CODE': 1, 'INPUT_CAP': 2, 'FRACTIONAL_OPTION': 1,
               'OPTION_ABOVE_PROFILE_CAP': 1, 'UNSUPPORTED_LEVEL_OPTION': 1, 'BYTE_ONLY_INPUT': 1}), 'full category accounting')

manifest = load(HERE / 'after/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json')
schema_path = Path(freeze['contexts']['configuredSource']) / 'builtins/node-compat/manifest.schema.json'
schema = load(schema_path)
check(set(manifest) == set(schema['required']), 'exact manifest top keys')
module = manifest['modules']['node:zlib']
check(set(module) <= set(schema['$defs']['module']['properties']), 'no unsupported manifest fields')
check(len(module['exports']) == len(set(module['exports'])) == 40, 'finite40 exports')
check(len(module['supportedStatic']) == 6 and len(module['importOnlyExports']) == 31, 'six plus31 callable policies')
check(module['limits'] == {'inputBytes': 1048576, 'outputBytes': 16777216}, 'caps unchanged')
check(manifest['requiredHostInterfaces'] == [] and module['aliases'] == ['zlib'], 'no new capabilities or aliases')
check('also freezes codes' in module['deviations'][4], 'corrected bounded descriptor/mutability claim')
version = load(HERE / 'backend-evidence-protocol.json')
check(version['historicalRuntimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}, 'old backend proof untouched')
check(version['evidenceEntryImplemented'] is False and version['actualRawRecord'] is None, 'actual backend evidence remains open')
for name in ('error-contract.proposal.json', 'differential-validation-plan.json'):
    obj = load(HERE / name)
    check(obj['sourcePeer'] is None and obj['rootAuthority'] is None, 'future authority null')
    check(obj.get('adoption', False) is False and obj.get('runtimeAcceptance', False) is False, 'no adoption or runtime grant')

node_js = (HERE.parent / 'source-freeze/node/lib/zlib.js').read_text()
node_cpp = (HERE.parent / 'source-freeze/node/src/node_zlib.cc').read_text()
check('genericNodeError(message, { errno, code })' in node_js, 'Node codec error errno source')
check('throw new ERR_BUFFER_TOO_LARGE(self._maxOutputLength)' in node_js, 'Node separate output cap error source')
check('case Z_NEED_DICT:' in node_cpp and 'return ErrorForMessage("Missing dictionary")' in node_cpp, 'Node dictionary source')
check('value: ObjectFreeze(codes)' in node_js, 'Node codes frozen baseline')
for row in load(HERE / 'source-evidence.json')['citations']:
    check(Path(row['path']).read_text().splitlines()[row['line'] - 1] == row['sourceLine'], 'actual exact source citation')
    check(row['needle'] in row['sourceLine'], 'citation marker')
future = load(HERE / 'future-source-peer-contract.json')
check(future['sourceIndexSha256'] is None and future['independentReview'] is None, 'no invented source peer')
for name in ('prepare.py', 'check-source.py', 'run-source-checks.py', 'seal-source.py'):
    if (HERE / name).exists():
        ast.parse((HERE / name).read_text(), filename=name)
        check(True, 'Python grammar only ' + name)
result = {'schemaVersion': 1, 'state': 'SOURCE_DATA_AND_EXTRACTED_MODELS_PASSED_V1', 'checks': checks,
          'inputFilesRehashed': len(freeze['files']), 'statusModelCases': len(models),
          'sourceManifestRows': 350, 'unmodifiedSourceRows': 347, 'completeCases': 61,
          'historicalErrorComparisons': 31, 'historicalDifferentCases': 22,
          'targetedRowsPredictedOnly': targeted, 'remainingRowsPredictedOnly': remaining,
          'matchingErrorRowsPredictedUnchanged': 9, 'rawErrorRecordsAuthenticated': 145,
          'factoryTransformReproducedByPythonBeforeDerivation': True,
          'pythonGrammarOnly': True, 'jsOrCppParsedOrCompiled': False,
          'nodeHelpersCodecGuestNativeOrRuntimeActionsInvoked': False,
          'realFaultOrOomExecuted': False, 'runtimeVerifiedSuccessor': False}
(HERE / 'source-results.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'model-evidence.json').write_text(json.dumps({'schemaVersion': 1, 'statusCases': models,
    'predictedErrorComparisons': prediction, 'cppAndCodecNotExecuted': True}, indent=2) + '\n')
print(json.dumps(result))
