"""Derive combined HTTP source only; no bundler, preflight or activation."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'classic-http-candidate-v1'
RUNTIME = HERE.parent / 'production-trace-runtime-activated-v1'
proofs = []


def sha(data): return hashlib.sha256(data).hexdigest()


def put(name, data):
    path = HERE / name; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == data
    else:
        with path.open('xb') as out: out.write(data)


def main():
    assert sha((PARENT / 'index.json').read_bytes()) == 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982'
    for row in json.loads((PARENT / 'index.json').read_bytes())['files']:
        name = row['path']
        if not name.startswith('capability/') or name == 'capability/preflight.mjs': continue
        before = (PARENT / name).read_text(); assert sha(before.encode()) == row['sha256']
        edits = []
        if name in ('capability/composer-plugin.mjs', 'capability/http-component.mjs'):
            edits.append(('../../production-regression-candidate-v1/', '../../production-trace-regression-activated-v1/'))
        if name == 'capability/composer-plugin.mjs':
            edits.append(("'../../production-runtime-activated-v2/harness/checks.mjs'", repr(str(RUNTIME / 'harness/checks.mjs'))))
        if name == 'capability/ordinary.mjs':
            edits.append(("'../../production-runtime-activated-v2/harness/checks.mjs'", repr((RUNTIME / 'harness/checks.mjs').as_uri())))
        if name == 'capability/preflight.template.mjs':
            edits += [
                ('8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a', 'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'),
                ("resolve(here,'../../production-runtime-activated-v2')", repr(str(RUNTIME))),
                ('ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED', 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED')]
        if name == 'capability/http-contract.mjs':
            edits += [('ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1', 'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1'),
                      ('reviewed-classic-combined-http-component', 'reviewed-classic-trace-combined-http-component')]
        if name == 'capability/run-http-wasmtime.mjs':
            edits.append(("const ready=await verifyHTTPReady(),{pin}=ready;", "assert.notEqual(process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1','This fixed combined fixture has no optional native.intrinsics field');\nconst ready=await verifyHTTPReady(),{pin}=ready;"))
        text = before; applied = []
        for old, new in edits:
            count = text.count(old); assert count == 1, (name, old, count)
            text = text.replace(old, new); applied.append({'old': old, 'new': new, 'count': count})
        reversed_text = text
        for edit in reversed(applied):
            assert reversed_text.count(edit['new']) == edit['count']
            reversed_text = reversed_text.replace(edit['new'], edit['old'])
        assert reversed_text == before
        put('http-payload/' + name, text.encode())
        proofs.append({'path': name, 'origin': str(PARENT / name), 'beforeSha256': sha(before.encode()),
            'afterSha256': sha(text.encode()), 'edits': applied, 'reverseExact': True})
    before = (PARENT / 'test-bundle.mjs').read_text(); text = before
    edits = [('/production-runtime-activated-v2/harness/checks.mjs', '/production-trace-runtime-activated-v1/harness/checks.mjs'),
             ('/tmp/starling-node-compat/classic-http-bundle-v1-', '/tmp/starling-node-compat/classic-trace-http-bundle-v1-')]
    applied = []
    for old, new in edits:
        assert text.count(old) == 1; text = text.replace(old, new); applied.append({'old': old, 'new': new, 'count': 1})
    reverse = text
    for edit in reversed(applied): assert reverse.count(edit['new']) == 1; reverse = reverse.replace(edit['new'], edit['old'])
    assert reverse == before
    put('http-payload/test-bundle.mjs', text.encode())
    proofs.append({'path': 'test-bundle.mjs', 'origin': str(PARENT / 'test-bundle.mjs'), 'beforeSha256': sha(before.encode()),
        'afterSha256': sha(text.encode()), 'edits': applied, 'reverseExact': True})
    put('http-transformations.json', (json.dumps({'schemaVersion': 1, 'state': 'CORRECTED_COMBINED_HTTP_SOURCE_SUCCESSOR_NO_BUNDLE_OR_RUNTIME',
        'parentIndexSha256': 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982',
        'files': proofs, 'baselineBodyModified': False, 'ordinary19OrNodeOracleModified': False,
        'hostAssertionsOrTransportModified': False, 'futureComponentPhaseNull': True}, indent=2) + '\n').encode())
    print(json.dumps({'state': 'COMBINED_HTTP_SOURCE_PAYLOAD_DERIVED_NOT_ACTIVATED', 'files': len(proofs)}))


if __name__ == '__main__': main()
