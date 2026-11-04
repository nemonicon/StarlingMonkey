"""Own read/data/AST checks only. Never import activation, preflight or drivers."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.dont_write_bytecode = True
checks = []


def hash(data): return hashlib.sha256(data).hexdigest()


def check(name, value=True):
    assert value, name
    checks.append(name)


def main():
    assert len(sys.argv) == 2, 'Explicit fresh /tmp/starling-node-compat/... output directory required'
    output = Path(sys.argv[1]).absolute()
    assert str(output).startswith('/tmp/starling-node-compat/') and not output.exists()
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('trace_activation_pure_authority', HERE / 'authority.py')
    authority = importlib.util.module_from_spec(spec); spec.loader.exec_module(authority)
    missing_review = output / 'never-read-review.json'
    def reject(name, value):
        raw = (json.dumps(value) + '\n').encode(); path = output / ('case-' + str(len(checks)) + '.json')
        path.write_bytes(raw)
        try: authority.load_authority(path, hash(raw), missing_review, hash(b'not-read'))
        except (AssertionError, KeyError, TypeError): check(name)
        else: raise AssertionError('Unexpected future authority acceptance: ' + name)
    reject('null authority refuses before review/artifact/output access', None)
    reject('unconfigured trace pins refuse', json.loads((HERE / 'runtime-pins.json').read_bytes()))
    reject('unreviewed trace exporter refuses', {'schemaVersion': 1, 'state': 'UNREVIEWED_CLASSIC_TRACE_PRODUCTION_PIN_CANDIDATES_V1', 'variants': {label: None for label in authority.LABELS}})
    reject('reviewed outer state does not admit null rows', {'schemaVersion': 1, 'state': 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1', 'variants': {label: None for label in authority.LABELS}})
    reject('missing variant refuses', {'schemaVersion': 1, 'state': 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1', 'variants': {}})
    old = json.loads((HERE.parent / 'production-runtime-activated-v3/runtime-pins.json').read_bytes())
    reject('original actual342 Root-reviewed document refuses', old)
    changed = json.loads(json.dumps(old)); changed['state'] = 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
    reject('outer relabelling does not admit old342 tuples', changed)
    changed['diagnosticOnly'] = True
    reject('diagnostic authority refuses before artifact use', changed)
    del changed['diagnosticOnly']
    policy = json.loads((HERE.parent / 'trace-integration-candidate-v1/policy.json').read_bytes())
    for label, pin in changed['variants'].items():
        pin.update(state='reviewed-real-classic-trace-production-freeze', recipeSha256=authority.RECIPE,
                   sourceContractVersion=authority.CONTRACT, classicTraceSourcePolicy=policy['classicTraceSourcePolicy'])
    reject('old actual tuple still refuses after attempted source-label projection', changed)
    invalid = output / 'invalid-json.json'; invalid.write_bytes(b'{broken')
    try: authority.read_document(invalid, hash(b'different-beforeimage'))
    except AssertionError: check('authority hash precedes JSON parse')
    else: raise AssertionError('Changed authority was parsed')
    proof = json.loads((HERE / 'derivations.json').read_bytes())
    for row in proof['files']:
        before = (REPO / row['origin']).read_text(); text = before
        check('exact original ' + row['path'], hash(before.encode()) == row['beforeSha256'])
        for edit in row['edits']:
            assert text.count(edit['before']) == edit['count']; text = text.replace(edit['before'], edit['after'])
        check('exact forward ' + row['path'], text == (HERE / row['path']).read_text() and hash(text.encode()) == row['afterSha256'])
        for edit in reversed(row['edits']):
            assert text.count(edit['after']) == edit['count']; text = text.replace(edit['after'], edit['before'])
        check('exact reverse ' + row['path'], text == before)
    for path in (HERE / 'payload/harness').iterdir():
        if path.name != 'component-driver.mjs':
            check('unchanged semantic/CJS/completion file ' + path.name, path.read_bytes() == (HERE.parent / 'production-runtime-activated-v3/harness' / path.name).read_bytes())
    for name in ('cases.mjs', 'guest.mjs', 'node-results.json'):
        check('exact eleven-case parent ' + name, (HERE / 'payload/trace' / name).read_bytes() == (HERE.parent / 'stream-trace-regression-candidate-v2' / name).read_bytes())
    activation = (HERE / 'activate.py').read_text()
    check('authority before exporter/native verifier import', activation.index('load_authority(pin_path') < activation.index('importlib.util.spec_from_file_location'))
    check('expected own index primitive required', 'expectedOwnIndexSHA' in activation and 'verified_index(HERE, own_sha)' in activation)
    check('actual corrected342/tool92 required', "len(source_expected) == 342" in activation and "len(tool_document['toolDependencies']) == 92" in activation)
    check('old preparation1175 not followed from copy', "verified_index(SOURCE_ROOT / relative_integration, INTEGRATION_SHA)" in activation and "json.loads(regular(INTEGRATION / 'input-freeze.json'" not in activation)
    check('all four genuine successor candidates compared', "row = exporter.candidate(label)" in activation and "assert pin[key] == value" in activation)
    check('tool bytes and membership retained', "add(path, row['sha256'])" in activation and "tool_trees == old_seal['toolTrees']" in activation and "tool_links == old_seal['toolLinks']" in activation)
    check('post-stage authority/source recheck', activation.rfind('load_authority(pin_path') > activation.index('stage.mkdir(exist_ok=False)') and 'stage.rename(OUTPUT)' in activation)
    template = (HERE / 'runtime-preflight.template.mjs').read_text()
    check('corrected staged admission and selector before dynamic import', "join(SOURCE_ROOT,'tests/node-compat/classic-streams-admission.mjs')" in template and 'await regular(liveSelector,SELECTOR_SHA);await regular(liveAdmission,ADMISSION_SHA);' in template)
    check('no original repository selector import', "await import('../../module-selection.mjs')" not in template)
    check('six substitutions reconstructed', 'ROOT_REVIEW_SHA' in template and '{PINS_SHA,INPUTS_SHA,RECIPE_SHA,SELECTOR_SHA,ADMISSION_SHA,ROOT_REVIEW_SHA}' in template)
    check('recheck uses private snapshots', 'privateRoot=pin.freezeRoot' in template and 'const checks=pin.frozenFiles.map(row=>({...row}))' in template)
    check('new future freeze state', "freeze.state,'immutable-trace-release-engine-frozen'" in template)
    trace = (HERE / 'payload/trace/component-driver.mjs').read_text()
    check('eleven-case exact Node parity added after retained/fresh comparisons', 'trace-counterexamples.json' in trace and "assert.deepEqual(retained[0].observed,oracle.nodeObserved" in trace)
    check('eleven-case historical model still reported', 'hostModelEqualsActualGuest' in trace)
    gates = json.loads((HERE / 'fresh-gates.json').read_bytes())
    check('fresh stages explicit, old pass reuse forbidden', len(gates['gates']) == 8 and gates['oldPassReuseAllowed'] is False)
    for name in ('activate.py', 'authority.py', 'test-source.py'):
        ast.parse((HERE / name).read_text(), filename=name); check('Python AST ' + name)
    check('activation output remains absent', not (HERE.parent / 'production-trace-runtime-activated-v1').exists())
    check('staging output remains absent', not (HERE.parent / 'production-trace-runtime-activated-v1.staging').exists())
    result = {'schemaVersion': 1, 'state': 'TRACE_RUNTIME_ACTIVATION_SOURCE_AND_NEGATIVE_AUTHORITY_CHECKS_PASSED',
        'passed': len(checks), 'checks': checks, 'output': str(output), 'actualOrSyntheticNewEnginePinsCreated': False,
        'ownerActionMainsImportedOrExecuted': False, 'actualNativePreflightExecuted': False,
        'componentizerGuestNativeHostOrTimingExecuted': False, 'activationOutputCreated': False}
    (output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
