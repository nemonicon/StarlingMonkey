"""Compose a new experimental native Source generation. No compiler/engine runs.

Old engine metadata is input ancestry only. This writes a new source ledger,
never an adapted old build receipt. Refuse ambiguous merges; retain every edit.
"""
import difflib
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TESTS = REPO / 'tests/node-compat'
FROZEN = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
inputs, edits, files, origins = {}, [], {}, {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    row = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    if str(path) in inputs:
        assert inputs[str(path)] == row, ('changed input', path)
    inputs[str(path)] = row
    return data


def load(path):
    return json.loads(read(path))


def put(path, data, origin):
    assert not Path(path).is_absolute() and '..' not in Path(path).parts
    before = files.get(path)
    files[path] = data
    origins[path] = origin
    edits.append({'path': path, 'beforeSha256': None if before is None else sha(before),
                  'afterSha256': sha(data), 'origin': origin})


def replace(path, before, after, source):
    text = files[path].decode()
    if before == after:
        return
    assert before and text.count(before) == 1, ('localized edit not unique', path, source, before[:150])
    put(path, text.replace(before, after, 1).encode(), source)


def merge_afterimage(path, before_data, after_data, source):
    """Apply distinct line edits, preserving other already-composed changes."""
    if files[path] == before_data:
        put(path, after_data, source)
        return
    if files[path] == after_data:
        edits.append({'path': path, 'alreadySatisfied': True, 'origin': source})
        return
    old, new = before_data.decode().splitlines(True), after_data.decode().splitlines(True)
    for tag, i, j, k, n in reversed(difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes()):
        if tag == 'equal':
            continue
        before, after = ''.join(old[i:j]), ''.join(new[k:n])
        current = files[path].decode()
        if before:
            if current.count(before) == 1:
                replace(path, before, after, source)
            elif after and current.count(after) == 1:
                edits.append({'path': path, 'alreadySatisfied': True, 'origin': source,
                              'replacementSha256': sha(after.encode())})
            else:
                raise AssertionError(('merge needs explicit resolution', path, source, before[:180]))
        else:
            # Anchor insertion to a unique suffix of its actual baseline.
            # A different layer may have inserted immediately after this anchor.
            if after and current.count(after) == 1:
                edits.append({'path': path, 'alreadySatisfied': True, 'origin': source})
                continue
            found = False
            for context in range(2, 13):
                anchor = ''.join(old[max(0, i-context):i])
                if anchor and current.count(anchor) == 1:
                    replace(path, anchor, anchor + after, source)
                    found = True
                    break
            assert found, ('ambiguous insertion', path, source, after[:100])


def overlay_directory(directory, label, selected=None):
    for p in sorted(directory.rglob('*')):
        if p.is_file():
            name = p.relative_to(directory).as_posix()
            if selected is None or name in selected:
                put(name, read(p), label + ':' + str(p))


assert sys.dont_write_bytecode and sys.flags.isolated == 1 and __debug__
assert len(sys.argv) == 2
output = Path(sys.argv[1])
assert str(output).startswith('/private/tmp/starling-node-compat/next-native-profile-')
assert not output.exists(), 'Fresh source output required'
metadata = load(FROZEN / 'normal-off.engine.wasm.build.json')
assert inputs[str(FROZEN / 'normal-off.engine.wasm.build.json')]['sha256'] == '2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
assert len(metadata['sourceManifest']) == 357
for row in metadata['sourceManifest']:
    data = read(FROZEN / 'source' / row['path'])
    assert sha(data) == row['sha256']
    files[row['path']] = data
    origins[row['path']] = 'frozen9aec357'

families = [
    'foundation-module/node-module-candidate-v1',
    'foundation-module/node-module-candidate-v2',
    'foundation-fs/next-fs-candidate-v2',
    'foundation-fs/next-fs-candidate-v3',
    'foundation-startup/next-startup-candidate-v1',
    'foundation-startup/next-startup-candidate-v2',
    'async-context/native-als-candidate-v2',
    'async-context/native-als-candidate-v3',
    'async-context/native-als-candidate-v4',
    'async-context/native-als-candidate-v5',
    'foundation-timers/node-timers-candidate-v1',
    'buffer-next-candidate-v1',
    'node-crypto-rng-candidate-v1',
    'foundation-zlib/next-streaming-candidate-v1',
    'foundation-classic-streams/readable-toweb-candidate-v1',
    'foundation-util/format-primitive-candidate-v1',
    'foundation-crypto/node-builtin-namespace-identity-candidate-v1',
    'foundation-crypto/node-crypto-hash-hmac-init-barrier-candidate-v1',
    'foundation-vm/node-vm-candidate-v1',
]
available = {}
for family in families:
    root = TESTS / family
    index = load(root / 'index.json')
    for row in index['files']:
        data = read(root / row['path'])
        assert sha(data) == row['sha256'] and len(data) == row['bytes'], (family, row['path'])
        available.setdefault(row['sha256'], (root / row['path'], data))

# This cumulative Source union was derived on the actual frozen357 lineage.
# Its old raw83 references remain ancestry; no old build shape is projected.
timer = load(TESTS / 'foundation-timers/node-timers-candidate-v1/prospective-source-manifest.json')
assert len(timer['files']) == 397
for row in timer['files']:
    if row['path'] in files and sha(files[row['path']]) == row['sha256']:
        continue
    if 'afterimage' in row:
        donor = Path(row['afterimage']['path']); data = read(donor)
    else:
        donor, data = available[row['sha256']]
    assert sha(data) == row['sha256']
    put(row['path'], data, 'Timer397 cumulative Source:' + str(donor))
assert len(files) == 397

rng = TESTS / 'node-crypto-rng-candidate-v1'
integration = load(rng / 'integration.json')
for row in integration['overlays']:
    path = row if isinstance(row, str) else row['installedPath']
    donor = TESTS / 'buffer-next-candidate-v1/native' / path if isinstance(row, str) else rng / 'after' / path
    put(path, read(donor), 'RNG/Buffer Next Source:' + str(donor))
assert len(files) == 402

# FS v3 changes constant inspection semantics, not the native provider.
overlay_directory(TESTS / 'foundation-fs/next-fs-candidate-v3/after', 'FS3')
# Keep Timer's new virtual interest/Immediate methods while fixing the actual
# SDK-invalid ALSV2 default. Never install an older whole extension-api.h.
replace('include/extension-api.h', 'JS::HandleObject resource = JS::NullHandleObject',
        'JS::HandleObject resource = nullptr', 'ALSV3 actual SDK correction on Timer header')
put('runtime/async_context_queue.cpp',
    read(TESTS / 'async-context/native-als-candidate-v3/after/runtime/async_context_queue.cpp'), 'ALSV3 corrected queue')
overlay_directory(TESTS / 'async-context/native-als-candidate-v4/after', 'ALSV4 installed inventory/generator')

namespace = load(TESTS / 'foundation-crypto/node-builtin-namespace-identity-candidate-v1/derivation.json')
for edit in namespace['edits']:
    replace('runtime/script_loader.cpp', edit['before'], edit['after'], 'registered namespace identity')
barrier = load(TESTS / 'foundation-crypto/node-crypto-hash-hmac-init-barrier-candidate-v1/derivations.json')
for row in barrier['files']:
    if row['path'] == 'builtins/node-compat/hash-hmac-kernel.cpp':
        assert sha(files[row['path']]) == row['before']['sha256']
        put(row['path'], read(row['after']['path']), 'real INIT barrier; shared unconditional deployed accessor retained')
util = load(TESTS / 'foundation-util/format-primitive-candidate-v1/derivations.json')
for row in util['files']:
    assert sha(files[row['path']]) == row['before']['sha256']
    put(row['path'], read(row['after']['path']), 'bounded primitive util.format')

streaming = load(TESTS / 'foundation-zlib/next-streaming-candidate-v1/integration-edits.json')
for row in streaming['existingChanges']:
    merge_afterimage(row['path'], read(row['before']['path']), read(row['after']['path']), 'streaming zlib localized join')
for row in streaming['newPaths']:
    path = Path(row['path']); relative = path.relative_to(TESTS / 'foundation-zlib/next-streaming-candidate-v1/after').as_posix()
    put(relative, read(path), 'new native streaming zlib Source')

# Sources below must be sealed before a build. The composer is allowed to
# prepare an unsealed integration checkout for direct inspection only.
vm = TESTS / 'foundation-vm/node-vm-candidate-v1'
vm_delta = load(vm / 'localized-edits.json')
for row in vm_delta['files']:
    merge_afterimage(row['path'], read(row['before']['path']), read(row['after']['path']),
                     'finite-data native VM localized join')
for p in sorted((vm / 'after/builtins/node-compat').iterdir()):
    if p.name != 'register.cpp':
        put('builtins/node-compat/' + p.name, read(p), 'native VM new payload')

# Integration bindings themselves are supplied by the independently authored
# exact registrar/CMake delta, and remain a required input before execution.
join = HERE / 'root-module-integration.json'
root_integration = load(join)
for row in root_integration['nativeMappings']:
    data = read(row['source']['path'])
    assert sha(data) == row['source']['sha256'] and len(data) == row['source']['bytes']
    put(row['path'], data, 'Root Next guest bindings; actual registrar/CMake mapping')
for row in root_integration['files']:
    for edit in row['edits']:
        replace(row['path'], edit['before'], edit['after'], 'Root HTTP/imports registration')

performance = TESTS / 'foundation-startup/next-startup-candidate-v2'
for row in load(performance / 'localized-edits.json')['files']:
    merge_afterimage(row['path'], read(row['before']['path']), read(row['after']['path']),
                     'deployed Unix performance clock join')
for name in ['generate-startup-factory.mjs', 'next-startup-factory.generated.h',
             'export-manifest.process.node-v22.14.0.json', 'export-manifest.os.node-v22.14.0.json',
             'export-manifest.url.node-v22.14.0.json', 'private-startup-export-manifest.v1.json']:
    put('builtins/node-compat/' + name, read(performance / name), 'startup v2 canonical generation/manifest')

toweb = TESTS / 'foundation-classic-streams/readable-toweb-candidate-v1'
toweb_delta = load(toweb / 'integration-edits.json')
for r in toweb_delta['files']:
    for edit in r['edits']:
        replace(r['path'], edit['before'], edit['after'], 'bounded Readable.toWeb optional integration')
for r in toweb_delta['nativeFiles']:
    put(r['path'], read(r['source']), 'ToWeb compiled factory; canonical generation inputs authenticated in held packet')
put('builtins/node-compat/classic-streams/export-manifest.classic-toweb.node-v22.14.0.json',
    read(toweb / 'export-manifest.classic-toweb.node-v22.14.0.json'), 'alternative selected classic m0.23 manifest; old m0.12 retained')

als5 = load(TESTS / 'async-context/native-als-candidate-v5/results.json')
assert sha(files['cmake/builtins.cmake']) == als5['baseComposedCMake']['sha256']
edit = als5['localizedEdit']
replace(edit['path'], edit['before'], edit['after'], 'ALSV5 check real strict compile definition, not an unset CMake variable')
assert sha(files['cmake/builtins.cmake']) == als5['afterimage']['sha256']

# Guard actual native install: all demanded spellings and feature code must be
# present once; a new build will record actual compile options and dependencies.
registration = files['builtins/node-compat/register.cpp'].decode()
for marker in ['install_next_http(engine)', 'install_next_imports(engine)', 'install_vm_data(engine)',
               'install_async_local_storage(engine)', 'install_next_startup(engine,buffer_constructor)']:
    assert registration.count(marker) == 1, marker
assert 'JS::NullHandleObject' not in files['include/extension-api.h'].decode()
assert registration.count('installed_module.set(root);') == 1
assert 'NODE_COMPAT_ZLIB_STREAMING' in registration
assert 'deployed_execution_started' in files['builtins/node-compat/hash-hmac-kernel.cpp'].decode()

# All inputs are checked again before publishing this new Source directory.
for path, descriptor in list(inputs.items()):
    assert sha(Path(path).read_bytes()) == descriptor['sha256'], ('input changed', path)
output.mkdir(mode=0o700, parents=True)
native = output / 'source'; native.mkdir(mode=0o700)
for path, data in sorted(files.items()):
    target = native / path; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data); target.chmod(0o600)
embedding = output / 'componentize-source'
for relative in ['CMakeLists.txt', 'embedding/embedding.cpp', 'embedding/embedding.h']:
    donor = FROZEN / 'componentize-source' / relative
    target = embedding / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(read(donor))
for path, descriptor in list(inputs.items()):
    assert sha(Path(path).read_bytes()) == descriptor['sha256'], ('input changed while publishing', path)
manifest = [{'path': path, 'sha256': sha(data), 'bytes': len(data), 'origin': origins[path]} for path, data in sorted(files.items())]
result = {'schemaVersion': 1, 'state': 'NEXT_COMBINED_SOURCE_ONLY_NOT_BUILD_METADATA',
          'sourceRoot': str(native), 'nativeSourceFiles': len(files),
          'parentFrozenEngine': '9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e',
          'parentMetadata': inputs[str(FROZEN / 'normal-off.engine.wasm.build.json')],
          'files': manifest, 'inputs': list(inputs.values()), 'edits': edits,
          'engineBuilt': False, 'guestExecuted': False,
          'selectedManifestsMustBeDerivedFresh': True, 'legacyMetadataProjected': False}
(output / 'composition.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'state': result['state'], 'files': len(files), 'inputs': len(inputs), 'source': str(native)}))
