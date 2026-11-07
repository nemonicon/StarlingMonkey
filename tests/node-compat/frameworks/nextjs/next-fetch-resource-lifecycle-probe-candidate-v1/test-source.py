"""Python-only Source/retained-DATA tests; never parse/execute JavaScript or fetch."""
from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def main():
    checks = 0
    def need(value, message):
        nonlocal checks
        if value is not True: raise AssertionError(message)
        checks += 1
    builder = load('source_only_lifecycle_assembly', HERE / 'build-entry.py')
    validator = load('retained_lifecycle_json_only', HERE / 'verify-data.py')
    plan = json.loads((HERE / 'plan.json').read_text())
    protocol = json.loads((HERE / 'runtime-protocol.json').read_text())
    refs = json.loads((HERE / 'source-references.json').read_text())
    cases = (HERE / 'cases.mjs').read_text(); tail = (HERE / 'guest-tail.mjs.in').read_text()
    reference = (HERE / 'node-reference.mjs').read_text()
    rendered = builder.render()['lifecycle']
    need((HERE / 'guest-lifecycle.mjs').read_text() == rendered, 'actual authenticated text assembly')
    need(builder.descriptor(HERE / 'guest-lifecycle.mjs') == plan['entry'], 'selected raw guest entry')
    for key, name in [('guestCollector', 'cases.mjs'), ('independentNodeReference', 'node-reference.mjs'), ('dataValidator', 'verify-data.py')]:
        need(plan[key] == builder.descriptor(HERE / name), 'selected finite Source role ' + key)
    need(plan['actionsAllowed'] is False and protocol['actionsAllowed'] is False, 'unissued Source')
    need(all(value is False for value in protocol['permissions'].values()), 'no actor permission')
    for key in ['actualNativeBuild', 'actualEngine', 'actualNativeMetadata', 'actualConstructor', 'actualComponent',
                'actualComponentAudit', 'actualNodeReference', 'actualControlOwner', 'actualGuestProbe', 'rootAuthority']:
        need(plan[key] is None, 'future role remains null: ' + key)
    need(all(value is None for value in protocol['lateBindings'].values()), 'no invented future bindings')
    need(plan['entryMode'] == 'lifecycle' and plan['cases'] == validator.CASE_IDS, 'new literal public profile')
    need(len(plan['groups']) == 5 and sum(len(group) for group in plan['groups'].values()) == 8,
         'five public groups/eight cases')
    need(plan['bounds']['exactFetches'] == 11 and plan['bounds']['sequentialHealthRepeats'] == 4, 'finite fetch denominator')
    need(plan['worldSourceIndex'] == refs['families']['standardWorld'] and
         len(set(plan['selectedInterfaces'])) == 13 and all(name.endswith('@0.2.10') for name in plan['selectedInterfaces']), 'same complete std13 world')
    need(plan['cleanupSourceIndex'] == refs['families']['cleanup'] and
         refs['families']['cleanup']['sha256'].startswith('f52274f3'), 'genuine held cleanup ancestry')
    need(plan['cleanupCorrectionSourceIndex'] == refs['families']['cleanupNodiscardCorrection'] ==
         protocol['admission']['cleanupCorrectionSourceIndex'] and
         plan['cleanupCorrectionSourceIndex']['sha256'].startswith('445e118e'), 'explicit held nodiscard correction')
    need(plan['requiredSelectedRequestResponseAfterimage'] == refs['direct']['requiredSelectedRequestResponseAfterimage'] ==
         protocol['admission']['requiredSelectedRequestResponseAfterimage'] and
         plan['requiredSelectedRequestResponseAfterimage']['sha256'].startswith('1fe296b8'), 'future selected exact corrected CPP, no old frontend projection')
    need(plan['futureConstructor']['newSelectorRequired'] is True and
         plan['futureRuntime']['newThinReviewedControllerRequired'] is True and
         plan['futureRuntime']['oldInteropModeMustNotBeRetargeted'] is True, 'honest missing actor/selector seam')
    need('globalThis.fetch(origin + path' in cases and "redirect: 'error'" in cases, 'guest installed global fetch')
    need(cases.index('export async function collectFetchLifecycle') < cases.index('globalThis.fetch('), 'fetch only inside deployed collector')
    need(tail.index('async function prepareFetchLifecycleProbe') < tail.index('bootstrap();') < tail.index('process.env.STARLING_FETCH_CONTROL_ORIGIN'), 'runtime-only bootstrap/environment')
    need("if (globalThis.process !== process)" in tail and "if (++calls !== 1)" in tail,
         'real process and one collection')
    need("url.pathname !== '/fetch-lifecycle'" in tail and "url.search !== ''" in tail, 'exact incoming request')
    need("url.hostname !== '127.0.0.1'" in cases and "url.origin !== value" in cases, 'literal canonical loopback target')
    for forbidden in ['setTimeout(', 'setInterval(', 'Math.random(', 'crypto.', 'Date.', 'AbortController(', 'eval(', 'new Function(']:
        need(forbidden not in cases + tail, 'no timer/entropy/fault/private setup: ' + forbidden)
    need(cases.index('await lifecycleDrain(clone') < cases.index('o.cancel = await canceled; o.canceledClosed'), 'drain survivor before awaiting tee cancel')
    need('const pending = afterRead ? null : reader.read().then(' in cases and
         'const canceled = lifecycleOutcome(() => reader.cancel(' in cases, 'immediate handlers for both direct promises')
    need("console.log('NEXT_FETCH_LIFECYCLE_CASE_V1 '" in cases and
         cases.index('output.records.push(record)') < cases.index("console.log('NEXT_FETCH"), 'raw per-case stdout before semantics')
    need('captureLogError = lifecycleError(error)' in cases and 'record.error = lifecycleError(error)' in cases, 'error capture never success filtering')
    need('import ' not in cases and "from './cases.mjs'" not in reference and
         'globalThis.fetch' not in reference, 'Node independently implemented; guest no host helper import')
    need('const request = path => fetch(origin + path' in reference and
         'process.version !== \'v22.14.0\'' in reference and 'process.execArgv.length !== 0' in reference, 'Node genuine public fetch/pin policy')
    need("await write('observations.json', capture)" in reference and 'verify-data.py' not in reference,
         'all Node raw before separate DATA semantics')
    need('await saveRecord(row);' in reference and "'wx', 0o600" in reference, 'exclusive per-case publication')
    need(protocol['control']['completedStockServerAssumedLive'] is False and
         protocol['control']['newServerCode'] is False and protocol['control']['actualOrigin'] is None,
         'no imaginary live control or new server')
    need(protocol['admission']['oldReturnedFunctionCountMustNotBeProjected'] is True and
         protocol['admission']['minimumFreeBytesBeforeAnyIssueOrOutput'] == 1073741824, 'fresh imports and original runtime floor')
    need(all(plan[key] is False for key in ['nativeResourcesProved', 'allHttpCleanupProved', 'currentPostAbortCauseProved', 'fullNextAccepted', 'adoption']), 'bounded nonclaims')
    for path in HERE.glob('*.py'):
        tree = ast.parse(path.read_text())
        need(not any(isinstance(node, (ast.Import, ast.ImportFrom)) and
                     any(item.name in ['subprocess', 'socket', 'urllib'] for item in node.names) for node in ast.walk(tree)), 'no actor imports ' + path.name)

    # Synthetic JSON only. No fetch/stream/native/C++ implementation is modeled or executed.
    def meta(target, used): return dict(status=200, url=target, contentType='application/json; charset=utf-8', bodyUsed=used)
    def drain(target, payload):
        return dict(before=meta(target, False), after=meta(target, True), hex=payload.hex(),
                    receivedBytes=len(payload), parts=[len(payload)], eof=copy.deepcopy(validator.EOF),
                    closed=dict(fulfilled=True, valueUndefined=True), complete=True)
    base = 'http://127.0.0.1:34567'; target = base + '/api/json?q=lifecycle-v1'
    rows = []
    for case in validator.CASE_IDS:
        o = dict(before=meta(target, False), after=meta(target, True))
        if case == 'read-eof-metadata': o = drain(target, validator.JSON_BYTES)
        elif case.startswith('bodyall-'):
            o['secondRead'] = dict(fulfilled=False, error=dict(isTypeError=True))
            if case.endswith('-text'): o['value'] = validator.JSON_BYTES.decode()
            elif case.endswith('-json'): o['value'] = copy.deepcopy(validator.JSON_VALUE)
            else: o['hex'] = validator.JSON_BYTES.hex()
        elif case == 'repeat-read-eof':
            o = dict(responses=[dict(drain(base + '/api/health', validator.HEALTH_BYTES), ordinal=n) for n in [1, 2, 3, 4]])
        elif case == 'clone-one-cancel-other-drain':
            o = drain(target, validator.JSON_BYTES)
            o.update(cloneBefore=meta(target, False), cloneAfter=meta(target, True),
                     cancel=dict(fulfilled=True, valueUndefined=True), canceledClosed=dict(fulfilled=True, valueUndefined=True))
        else:
            o.update(cancel=dict(fulfilled=True, valueUndefined=True), closed=dict(fulfilled=True, valueUndefined=True),
                     readAfterCancel=copy.deepcopy(validator.EOF))
            chunk = dict(done=False, valueUndefined=False, hex=validator.JSON_BYTES.hex())
            if case.endswith('-pending'): o['pendingRead'] = dict(fulfilled=True, part=chunk)
            else: o['firstRead'] = chunk
        rows.append(dict(id=case, observations=o, error=None, cleanupErrors=[], captureLogError=None))
    guest = dict(schemaVersion=1, executor='guest-global-fetch', origin=base, caseIds=validator.CASE_IDS.copy(),
                 records=rows, allCasesAttempted=True, expectedJsonUrl=target, call=1)
    reference_data = copy.deepcopy(guest); reference_data['executor'] = 'node22-global-fetch'; del reference_data['call']
    need(validator.compare(guest, reference_data)['passed'] is True, 'complete synthetic DATA positive')
    partition = copy.deepcopy(guest); partition['records'][0]['observations']['parts'] = [1, len(validator.JSON_BYTES)-1]
    partition['records'][6]['observations']['pendingRead']['part'] = copy.deepcopy(validator.EOF)
    need(validator.compare(partition, reference_data)['passed'] is True, 'chunk partition/pending read timing not equated')
    mutations = [
        ('failedcase', lambda x: x['records'][0].update(error=False)),
        ('truthyint', lambda x: x['records'][0]['observations']['after'].update(bodyUsed=1)),
        ('statusbool', lambda x: x['records'][0]['observations']['before'].update(status=True)),
        ('missingcase', lambda x: x['records'].pop()),
        ('caseorder', lambda x: x['records'].reverse()),
        ('incomplete', lambda x: x.update(allCasesAttempted=False)),
        ('call', lambda x: x.update(call=2)),
        ('wrongbytes', lambda x: x['records'][0]['observations'].update(hex='00')),
        ('nonsurvivingclone', lambda x: x['records'][5]['observations'].update(complete=False)),
        ('badclonecancel', lambda x: x['records'][5]['observations'].update(cancel={'fulfilled':False})),
        ('secondreadsuccess', lambda x: x['records'][1]['observations'].update(secondRead={'fulfilled':True})),
        ('JSONboolint', lambda x: x['records'][2]['observations']['value'].update(query=True)),
        ('repeatcount', lambda x: x['records'][4]['observations']['responses'].pop()),
        ('healthwrongvalue', lambda x: x['records'][4]['observations']['responses'][0].update(hex='00')),
        ('cancelbadpending', lambda x: x['records'][6]['observations']['pendingRead'].update(fulfilled=False)),
        ('cancelwrongprefix', lambda x: x['records'][6]['observations']['pendingRead']['part'].update(hex='00')),
        ('afterreadEOF', lambda x: x['records'][7]['observations'].update(firstRead=copy.deepcopy(validator.EOF))),
        ('cancelnotEOF', lambda x: x['records'][7]['observations'].update(readAfterCancel={'done':False})),
        ('cleanupfailure', lambda x: x['records'][0].update(cleanupErrors=[{'operation':'releaseLock'}])),
        ('logfailure', lambda x: x['records'][0].update(captureLogError={})),
        ('redirected', lambda x: x['records'][0]['observations']['after'].update(url=base+'/api/health')),
        ('notJSON', lambda x: x['records'][0]['observations']['after'].update(contentType='text/html')),
        ('badchunkaccounting', lambda x: x['records'][0]['observations'].update(parts=[1])),
        ('missingmetadata', lambda x: x['records'][0]['observations'].pop('after')),
    ]
    for name, mutate in mutations:
        bad = copy.deepcopy(guest); mutate(bad)
        try: validator.compare(bad, reference_data)
        except (ValueError, TypeError, KeyError): need(True, 'DATA refusal: ' + name)
        else: need(False, 'accepted invalid DATA: ' + name)
    other_origin = copy.deepcopy(reference_data); other_origin['origin'] = 'http://127.0.0.1:34568'
    try: validator.compare(guest, other_origin)
    except ValueError: need(True, 'different reference origin refused')
    else: need(False, 'accepted retargeted reference')
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks, syntheticDataRefusals=len(mutations)+1,
                         syntheticDataPositives=2, javascriptParsedOrExecuted=False, nodeReferenceExecuted=False,
                         guestFetchOrConstructorOrCompilerOrServerExecuted=False)))

if __name__ == '__main__': main()
