"""Review the thin inventory-packaging correction. No operational action."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'node-module-candidate-v1'
SOURCE = HERE.parent / 'node-module-candidate-v2'


def descriptor(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def read(path):
    return json.loads(path.read_text())


assert descriptor(SOURCE / 'index.json')['sha256'] == 'c69350e3ed12574b2a21b0a5c224d9e16c70c5ec725c3da3b14c1ad860812687'
assert descriptor(PARENT / 'index.json')['sha256'] == '29f603f7652acabef8adfa12217c70cec177d8aaf07f177f0d09031f2a99009e'
for directory in (SOURCE, PARENT):
    index = read(directory / 'index.json')
    for item in index['files']:
        assert all(descriptor(directory / item['path'])[key] == item[key] for key in ('sha256', 'bytes'))
manifest = read(SOURCE / 'prospective-source-manifest.json')
old = read(PARENT / 'prospective-source-manifest.json')
mapping = read(SOURCE / 'native-mappings.json')
assert len(manifest['files']) == manifest['nativeSourceFiles'] == 364
assert len(manifest['externalEmbeddingSources']) == 3 and manifest['externalEmbeddingSources'] == old['externalEmbeddingSources']
expected = {item['path']: item['sha256'] for item in old['files']}
for item in mapping['overrides']:
    origin = item['origin']
    assert descriptor(Path(origin['path'])) == origin
    expected[item['path']] = origin['sha256']
assert expected == {item['path']: item['sha256'] for item in manifest['files']}
assert set(expected) - {item['path'] for item in old['files']} == {'builtins/node-compat/module-builtin-inventory.node-v22.14.0.json'}
source = (PARENT / 'module-core.mjs').read_text()
inventory = (SOURCE / 'module-builtin-inventory.node-v22.14.0.json').read_text()
data, old_data = json.loads(inventory), read(PARENT / 'node-inventory.json')
for key, value in old_data.items():
    assert data[key] == value
generator = (SOURCE / 'generate-module-factory.mjs').read_text()
assert "new URL('./module-builtin-inventory.node-v22.14.0.json',import.meta.url)" in generator
assert "inventoryVersion!=='node-module-builtin-exports-v22.14.0-v1'" in generator
digest = hashlib.sha256(('module-core.mjs\0' + source + '\0module-builtin-inventory.node-v22.14.0.json\0' + inventory + '\0').encode()).hexdigest()
header = (SOURCE / 'module-factory.generated.h').read_text()
assert '// Canonical Source SHA256: ' + digest in header
assert re.sub(r'// Canonical Source SHA256: [0-9a-f]{64}', '', header) == re.sub(r'// Canonical Source SHA256: [0-9a-f]{64}', '', (PARENT / 'module-factory.generated.h').read_text())
commands = read(SOURCE / 'checks.json')['commands']
assert len(commands) == 10
for item in commands:
    assert item['rawExitCode'] == item['expectedRawExitCode']
    for key in ('stdout', 'stderr'):
        assert descriptor(Path(item[key]['path'])) == item[key]
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_NODE_MODULE_COMMONJS_SOURCE_REVIEW_PASSED_V2',
          'sourceIndex': descriptor(SOURCE / 'index.json'), 'sourceIndexSha256': descriptor(SOURCE / 'index.json')['sha256'],
          'sourceOnly': True, 'sourceReviewPassed': True, 'nativeSourceFiles': 364,
          'retainedNativeFiles': 351, 'changedNativeFiles': 6, 'newNativeFiles': 7,
          'externalEmbeddingSources': 3, 'actualInstalledGeneratorLayoutPassed': True,
          'wholeInventoryAndCoreDigestCovered': True, 'guestCodeFunctionBodyUnchanged': True,
          'compilerActionsInvoked': False, 'guestActionsInvoked': False, 'nextServerExecuted': False,
          'blockingV1FindingResolvedInSuccessor': True, 'originalV1HoldUnchanged': True,
          'packagingCommandsChecked': len(commands), 'actualNativeBuild': None, 'actualGuestProof': None,
          'grantsActionAuthority': False,
          'limitations': ['No native frontend/link/guest action by this reviewer.',
                          'V1 core/native source review qualifications still apply.',
                          'Host full-Next control uses test-only Node capabilities; no Wasm acceptance.']}
print(json.dumps(result, indent=2))
