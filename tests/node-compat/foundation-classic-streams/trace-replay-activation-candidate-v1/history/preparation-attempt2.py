"""Derive only owned source payloads. Does not create the future replay family."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'production-regression-activated-v3'
RUNTIME = HERE.parent / 'production-trace-runtime-activated-v1'
proofs = []


def sha(data): return hashlib.sha256(data).hexdigest()


def put(name, data):
    path = HERE / name; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == data, str(path)
    else:
        with path.open('xb') as out: out.write(data)


def derive(name, origin, edits):
    before = origin.read_text(); text = before; applied = []
    for old, new in edits:
        count = text.count(old); assert count > 0, (name, old)
        text = text.replace(old, new); applied.append({'old': old, 'new': new, 'count': count})
    reversed_text = text
    for edit in reversed(applied):
        assert reversed_text.count(edit['new']) == edit['count']
        reversed_text = reversed_text.replace(edit['new'], edit['old'])
    assert reversed_text == before
    put(name, text.encode())
    proofs.append({'origin': str(origin), 'path': name, 'beforeSha256': sha(before.encode()),
        'afterSha256': sha(text.encode()), 'edits': applied, 'reverseExact': True})


def main():
    assert sha((BASE / 'index.json').read_bytes()) == '577dbad5759ef06f075763c2a793ae278fddc15df8f4f61edc9a7d2de51ecb51'
    exclude = {'README.md', 'source-receipt.json', 'input-freeze.json', 'capability/input-freeze.json',
        'native-preflight.mjs', 'native-preflight.template.mjs', 'runtime-pins.json', 'root-review-receipt.json',
        'activation-reference.json', 'runtime-contract.mjs'}
    for row in json.loads((BASE / 'index.json').read_bytes())['files']:
        name = row['path']
        if name in exclude: continue
        data = (BASE / name).read_bytes(); assert sha(data) == row['sha256']
        if name == 'release/helpers/native-scalar-harness.mjs':
            derive('payload/' + name, BASE / name, [
                ('137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f', '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'),
                ('71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7', '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'),
                ('tests/node-compat/foundation-classic-streams/integration-candidate-v1/policy.json', 'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/policy.json'),
                ('  assert.equal(metadata.sourceManifest.length,342);', "  assert.equal(classic.classicTraceSourcePolicy.version,'sm-classic-trace-source-v1');\n  assert.deepEqual(metadata.classicTraceSourcePolicy,classic.classicTraceSourcePolicy);\n  assert.equal(metadata.sourceManifest.length,342);")])
        elif name == 'common/runners/allocator-gc.mjs':
            derive('payload/' + name, BASE / name, [("pins.state,'reviewed-real-classic-production-freeze'", "pins.state,'reviewed-real-classic-trace-production-freeze'")])
        else: put('payload/' + name, data)
    put('payload/runtime-contract.mjs', (RUNTIME / 'runtime-contract.mjs').read_bytes())
    derive('native-preflight.template.mjs', BASE / 'native-preflight.template.mjs', [
        ("RUNTIME=resolve(HERE,'../@RUNTIME_FAMILY@')", "RUNTIME='@RUNTIME_ROOT@'"),
        ('c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e', '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'),
        ('1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56', 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'),
        ('ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED', 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'),
        ('ROOT_REVIEWED_CLASSIC342_REPLAY_AUTHORITY_BOUND_NOT_EXECUTED', 'ROOT_REVIEWED_CLASSIC_TRACE342_REPLAY_AUTHORITY_BOUND_NOT_EXECUTED'),
        ('ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1', 'ROOT_REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'),
        ('REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1', 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'),
        ('ACTUAL_REVIEWED_CLASSIC_RUNTIME_FAMILY_CREATED_NOT_EXECUTED', 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_FAMILY_CREATED_NOT_EXECUTED'),
        (".replaceAll('@'+'RUNTIME_FAMILY'+'@',RUNTIME.split('/').at(-1))", ".replaceAll('@'+'RUNTIME_ROOT'+'@',RUNTIME)")])
    put('body-transformations.json', (json.dumps({'schemaVersion': 1, 'state': 'SOURCE_ONLY_TRACE_REPLAY_SUCCESSOR_WIRING',
        'parentIndexSha256': sha((BASE / 'index.json').read_bytes()), 'files': proofs, 'inheritedBodies': 64,
        'currentV3BodiesByteIdentical': 62, 'newChangedHostBodies': 2, 'guestOrOracleBodiesChanged': False,
        'fullStrictAndProtectedTagsChanged': False}, indent=2) + '\n').encode())
    put('authority.py', (HERE.parent / 'trace-runtime-activation-candidate-v1/authority.py').read_bytes())
    print(json.dumps({'state': 'SOURCE_PAYLOADS_DERIVED_NO_ACTIVATION', 'reversibleFiles': len(proofs)}))


if __name__ == '__main__': main()
