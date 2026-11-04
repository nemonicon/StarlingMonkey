"""Own HTTP source/reverse/path checks; no main, bundler or preflight."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('pure_trace_http_source_functions', HERE / 'activate-http-source.py')
model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
checks = []


def sha(data): return hashlib.sha256(data).hexdigest()


def check(name, value=True): assert value, name; checks.append(name)


def main():
    assert len(sys.argv) == 2
    output = Path(sys.argv[1]).absolute()
    assert str(output).startswith('/tmp/starling-node-compat/') and not output.exists()
    output.mkdir(parents=True, exist_ok=False)
    proof = json.loads((HERE / 'http-transformations.json').read_bytes())
    check('twenty-one finite HTTP source copies', len(proof['files']) == 21)
    for row in proof['files']:
        before = Path(row['origin']).read_text(); text = before
        check('old HTTP source ' + row['path'], sha(before.encode()) == row['beforeSha256'])
        for edit in row['edits']:
            assert text.count(edit['old']) == edit['count']; text = text.replace(edit['old'], edit['new'])
        check('forward HTTP source ' + row['path'], text == (HERE / 'http-payload' / row['path']).read_text() and sha(text.encode()) == row['afterSha256'])
        for edit in reversed(row['edits']):
            assert text.count(edit['new']) == edit['count']; text = text.replace(edit['new'], edit['old'])
        check('reverse HTTP source ' + row['path'], text == before)
    payload = model.source_payload()
    old, mapped, mappings = model.inherited_http_inputs(payload)
    check('full original7518 HTTP rows interpreted as source only', len(old['inputs']) == 7518)
    for name in json.loads((model.BASE / 'input-freeze.json').read_bytes())['liveComputedInputs']:
        check('canonical actual LIVE input ' + name, str(model.CANONICAL_SOURCE_ROOT / name) in mapped)
    check('phase pin null and sealed in future source', json.loads(payload['capability/component-pins.json'])['component'] is None)
    check('whole-entry bundle check available unexecuted', 'test-bundle.mjs' in payload and 'production-trace-runtime-activated-v1/harness/checks.mjs' in payload['test-bundle.mjs'].decode())
    contract = payload['capability/http-contract.mjs'].decode()
    check('old external HTTP phase state cannot authorize corrected source', "'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1'" in contract and "'ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1'" not in contract)
    check('original build source entry check retained', 'pin.sourceEntryPath,join(here,' in contract)
    check('same-byte source audit/bundle/input/native checks retained', 'pin.sourceInputSha256' in contract and 'combined.composerSha256,hash(COMPOSER_SOURCE)' in contract)
    check('optional intrinsics1 rejected before host readiness', payload['capability/run-http-wasmtime.mjs'].decode().index('HTTP_REQUIRE_INTRINSICS') < payload['capability/run-http-wasmtime.mjs'].decode().index('await verifyHTTPReady()'))
    check('baseline/protected/classic host validators exact', payload['capability/validate-combined.mjs'] == (model.PARENT / 'capability/validate-combined.mjs').read_bytes() and payload['capability/validate-hosts.mjs'] == (model.PARENT / 'capability/validate-hosts.mjs').read_bytes())
    check('both transport wrappers exact', all(payload['capability/hosts/' + name] == (model.PARENT / 'capability/hosts' / name).read_bytes() for name in ('run-host.mjs', 'test-wasmtime-http.mjs')))
    check('six-interface validator exact', payload['capability/capabilities.mjs'] == (model.PARENT / 'capability/capabilities.mjs').read_bytes())
    check('no future HTTP activation output', not model.OUTPUT.exists() and not model.OUTPUT.with_name(model.OUTPUT.name + '.staging').exists())
    for name in ('activate-http-source.py', 'prepare-http-source.py', 'test-http-source.py'):
        ast.parse((HERE / name).read_text(), filename=name); check('Python AST ' + name)
    (output / 'mapped-inputs.json').write_text(json.dumps({'inputs': list(mapped.values()), 'mappings': mappings}, indent=2) + '\n')
    result = {'schemaVersion': 1, 'state': 'CORRECTED_HTTP_SOURCE_REVERSE_AND_PATH_CHECKS_PASSED_NOT_BUNDLE_PROOF',
        'passed': len(checks), 'checks': checks, 'output': str(output), 'parentInputs': 7518, 'mappedExistingSourceRows': len(mapped),
        'futureReplayIndexStillRequired': True, 'hostBundleOrNativePreflightOrActivationExecuted': False,
        'componentizerGuestHostNativeOrTimingExecuted': False, 'sourceOrOldReportsModified': False}
    (output / 'results.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))


if __name__ == '__main__': main()
