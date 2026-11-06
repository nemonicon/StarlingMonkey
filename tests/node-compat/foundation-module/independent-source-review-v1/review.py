"""Root's read-only source checks. No builder, compiler, guest or app execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'node-module-candidate-v1'


def descriptor(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def read(name):
    return json.loads((SOURCE / name).read_text())


index = read('index.json')
assert descriptor(SOURCE / 'index.json')['sha256'] == '29f603f7652acabef8adfa12217c70cec177d8aaf07f177f0d09031f2a99009e'
members = set()
for item in index['files']:
    path = SOURCE / item['path']
    assert not path.is_symlink() and item['path'] not in members
    members.add(item['path'])
    row = descriptor(path)
    assert all(row[key] == item[key] for key in ('sha256', 'bytes'))
assert members == {str(path.relative_to(SOURCE)) for path in SOURCE.rglob('*') if path.is_file() and path != SOURCE / 'index.json'}
derivations = read('derivations.json')['files']
for item in derivations:
    before, after = Path(item['before']['path']), Path(item['after']['path'])
    for path, record in ((before, item['before']), (after, item['after'])):
        assert all(descriptor(path)[key] == record[key] for key in ('sha256', 'bytes'))
    text = before.read_text()
    for edit in item['edits']:
        assert text.count(edit['before']) == edit['count']
        text = text.replace(edit['before'], edit['after'])
    assert text == after.read_text()
    for edit in reversed(item['edits']):
        assert text.count(edit['after']) == edit['count']
        text = text.replace(edit['after'], edit['before'])
    assert text == before.read_text()
manifest = read('prospective-source-manifest.json')
assert len(manifest['files']) == manifest['nativeSourceFiles'] == 363
assert len({row['path'] for row in manifest['files']}) == 363
assert (manifest['retainedNativeFiles'], manifest['changedNativeFiles'], manifest['newNativeFiles']) == (351, 6, 6)
assert len(manifest['externalEmbeddingSources']) == 3 and manifest['externalEmbeddingChanges'] == 0
parent_source = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze/source')
for item in manifest['files']:
    choices = [SOURCE / 'after' / item['path'], parent_source / item['path'], SOURCE / Path(item['path']).name]
    path = next(path for path in choices if path.is_file())
    assert descriptor(path)['sha256'] == item['sha256'], item['path']
host = json.loads((SOURCE / 'final-host-tests.stdout.log').read_text())
factory = json.loads((SOURCE / 'final-factory-tests.stdout.log').read_text())
assert host['checks'] == len(host['cases']) == 42 and all(row['passed'] for row in host['cases'])
assert factory['checks'] == 8 and factory['manifestSchemaPassed'] and not factory['nativeProviderCalled']
assert not host['nativeGuestProviderExecuted'] and not host['compilerOrComponentOrGuestExecuted']
kernel = (SOURCE / 'module-kernel.cpp').read_text()
for name, operation in (('kind', 'module.stat'), ('read_text', 'module.readText'), ('real_path', 'module.realpath'), ('cwd', 'module.cwd')):
    start = kernel.index('static bool ' + name + '(')
    end = kernel.find('\nstatic bool ', start + 1)
    part = kernel[start:end if end != -1 else len(kernel)]
    assert 'require_io(cx,"' + operation + '")' in part
    if name != 'cwd':
        assert part.index('require_io(') < part.index('path_arg(')
assert 'engine->state()==api::EngineState::Initialized&&entropy::deployed_execution_started()' in kernel
assert 'JS::RootedFunction fn(cx,JS::CompileFunction(' in kernel
assert 'JS::SourceOwnership::Borrowed' in kernel and 'std::unique_ptr<FILE,CloseFile>' in kernel
assert 'JS::MapGet(cx, builtinModules, key, result)' in (SOURCE / 'after/runtime/script_loader.cpp').read_text()
generator = (SOURCE / 'generate-module-factory.mjs').read_text()
assert "new URL('./node-inventory.json',import.meta.url)" in generator
assert 'builtins/node-compat/node-inventory.json' not in {row['path'] for row in manifest['files']}
result = {'schemaVersion': 1, 'state': 'NODE_MODULE_SOURCE_REVIEW_NEEDS_INVENTORY_INTEGRATION_V1',
          'sourceOnly': True, 'sourceReviewPassed': False, 'hostDifferentialChecksPassed': True,
          'nativeSourceFiles': 363, 'retainedNativeFiles': 351, 'changedNativeFiles': 6, 'newNativeFiles': 6,
          'externalEmbeddingSources': 3, 'ownerNativeActionsInvoked': False,
          'compilerActionsInvoked': False, 'guestActionsInvoked': False, 'nextServerExecuted': False,
          'sourceIndex': descriptor(SOURCE / 'index.json'), 'payloadsChecked': len(members),
          'sourceIndexSha256': descriptor(SOURCE / 'index.json')['sha256'],
          'prospectiveNativePayloadsChecked': 363,
          'derivationsCheckedForwardAndInverse': len(derivations),
          'authorHostChecks': 42, 'authorGeneratedFactoryChecks': 8,
          'manualReview': ['Real Module objects/cache before eval; exact thrown values evict failed entries.',
                           'Mutable resolver/prototype require support genuine Next interposition.',
                           'Private lookup uses the existing rooted native builtin map and actual default binding.',
                           'Owned source/filename bytes survive CompileFunction; FILE RAII and explicit close.',
                           'All IO uses initialized+deployed state before path encoding/libc; no host addon or custom interface.'],
          'blockingFinding': 'Installed generator reads node-inventory.json, but the proposed native Source cut does not install that required file. Package a versioned inventory and include it in the generator canonical digest in a successor.',
          'outstanding': ['SDK syntax, native linking and guest filesystem behavior are untested.',
                          'Join libc cwd/preopens and errors with the new direct-P2 filesystem provider.',
                          'Not full npm ESM/conditional-exports/Node errno compatibility; not a security boundary.',
                          'No deployed re-snapshot/reuse or emitted-import acceptance is inferred.'],
          'actualNativeBuild': None, 'actualGuestProof': None, 'grantsActionAuthority': False}
print(json.dumps(result, indent=2))
