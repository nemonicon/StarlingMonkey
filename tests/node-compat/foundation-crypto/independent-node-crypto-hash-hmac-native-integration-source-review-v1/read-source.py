"""Independent Source/data reader; imports only inert pure command models.

No native helper, producer, stage, compiler, engine or crypto workload is run.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import shlex

OWN = Path(__file__).resolve().parent
SOURCE = OWN.parent / 'node-crypto-hash-hmac-native-integration-candidate-v1'
EXPECTED = '7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
captured = {}
families = {}


def descriptor(path):
    path = Path(path)
    a = path.lstat()
    assert path.is_file() and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4194304), b''):
            h.update(block)
    z = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink,
                          s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    assert identity(a) == identity(z)
    row = dict(path=str(path), sha256=h.hexdigest(), bytes=z.st_size)
    if str(path) in captured:
        assert captured[str(path)] == (row, identity(z))
    captured[str(path)] = (row, identity(z))
    return row


def checked(row):
    assert {k: descriptor(row['path'])[k] for k in ['path', 'sha256', 'bytes']} == row
    return Path(row['path'])


def read(path):
    return json.loads(Path(path).read_bytes())


def family(index):
    checked(index)
    base = Path(index['path']).parent
    value = read(index['path'])
    names = {'index.json'}
    for row in value['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute()
        assert '\\' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        checked(dict(path=str(base / name), sha256=row['sha256'], bytes=row['bytes']))
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == names
    families[str(base)] = names


own = descriptor(SOURCE / 'index.json')
assert own['sha256'] == EXPECTED
family(own)
refs = read(SOURCE / 'references.json')
inputs = read(SOURCE / 'input-hashes.json')
assert len(inputs['files']) == 2622
for row in inputs['files']:
    checked(row)
assert len(refs['familyIndices']) == 7
for index in refs['familyIndices']:
    family(index)

policy = read(SOURCE / 'policy.json')
origins = read(SOURCE / 'native-origins.json')
before_meta = read(refs['nativeParentMetadata']['path'])
before = {r['path']: r['sha256'] for r in before_meta['sourceManifest']}
after = {r['path']: r['sha256'] for r in policy['expectedNativeSourceManifest']}
assert len(before) == 355 and len(after) == 357 and before.keys() <= after.keys()
assert sum(before[p] == after[p] for p in before) == 353
assert sum(before[p] != after[p] for p in before) == 2
assert len(after.keys() - before.keys()) == 2
assert len(origins['files']) == 357
assert {r['path']: r['sha256'] for r in origins['files']} == after
for row in origins['files']:
    checked(dict(path=row['original'], sha256=row['sha256'], bytes=row['bytes']))
assert len(read(SOURCE / 'embedding-origins.json')['files']) == 3
assert len([p for p in after if p.endswith('.cpp') and p.startswith(('builtins/', 'runtime/'))]) == 63
assert len(policy['privateTargetCpp']) == 7
assert set(policy['expectedRawMetadataKeys']) == set(before_meta) | {
    'nodeCryptoHashHmacEnabled', 'nodeCryptoAuditedBorrowEnabled', 'nodeCryptoHashHmacPolicy'}
assert len(before_meta) == 80 and policy['expectedRawMetadataFields'] == 83
assert len(policy['selectedModuleManifests']) == len(policy['selectedManifestValues']) == 12
assert policy['hashHmacSourcePolicy']['packagingManifestInput']['path'] not in after

derivations = read(SOURCE / 'tooling-derivations.json')
assert len(derivations['edits']) == 54
names = {'helper': 'layer-policy.py', 'recipe': 'build-engine.sh',
         'metadata-model': 'native-admission-model.py'}
for role, name in names.items():
    text = (SOURCE / name).read_text()
    for edit in reversed([e for e in derivations['edits'] if e['role'] == role]):
        assert len(edit['afterPositions']) == edit['count']
        for position in reversed(edit['afterPositions']):
            assert text[position:position + len(edit['after'])] == edit['after']
            text = text[:position] + edit['before'] + text[position + len(edit['after']):]
    donor = next(r for r in derivations['donors'] if Path(r['path']).name == name)
    assert text.encode() == checked(donor).read_bytes()

for path in SOURCE.glob('*.py'):
    ast.parse(path.read_bytes(), filename=str(path))

# This original module contains definitions only. It does not import the native
# helper, generate metadata, compile anything or invoke OpenSSL.
path = SOURCE / 'hash-hmac-model.py'
spec = importlib.util.spec_from_file_location('original_hash_hmac_pure_command_model', path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
repo = Path(policy['contexts']['configuredSourceRoot'])
include = '/prospective/guest-openssl/include'
entries = []
for name in sorted(policy['privateTargetCpp']) + ['runtime/event_loop.cpp']:
    words = ['/prospective/clang++', '--target=wasm32-wasi', '-O3', '-DNDEBUG']
    if name in policy['privateTargetCpp']:
        words += ['-DNODE_COMPAT_CRYPTO_HASH_HMAC=1', '-isystem', include]
    file = str(repo / name)
    words += ['-o', '/prospective/output.o', '-c', file]
    entries.append(dict(file=file, command=shlex.join(words)))
metadata = dict(nodeCryptoHashHmacEnabled=True, nodeCryptoAuditedBorrowEnabled=False,
                entropyPolicy='off', gcStress=False, oomTesting=False,
                openssl=dict(installDir='/prospective/guest-openssl'),
                requestedCMakeOptions={'NODE_COMPAT_CRYPTO_HASH_HMAC': 'ON',
                                       'NODE_CRYPTO_AUDITED_BORROW': 'OFF',
                                       'ENABLE_BUILTIN_WEB_CRYPTO': 'ON'})
metadata['observedCMakeOptions'] = copy.deepcopy(metadata['requestedCMakeOptions'])
tests = []
result = model.validate_hash_hmac_commands(entries, [], repo, metadata, policy)
assert result['defaultCopyOnly'] is True
tests.append('private command primitive accepts synthetic seven plus one rows; not a complete DB claim')


def rejects(label, change):
    rows = copy.deepcopy(entries)
    change(rows)
    try:
        model.validate_hash_hmac_commands(rows, [], repo, metadata, policy)
    except (AssertionError, KeyError, ValueError):
        tests.append(label)
        return
    raise AssertionError('Independent negative accepted: ' + label)


kernel = next(i for i, r in enumerate(entries) if r['file'].endswith('/hash-hmac-kernel.cpp'))
rejects('missing kernel', lambda rows: rows.pop(kernel))
rejects('duplicate kernel', lambda rows: rows.append(copy.deepcopy(rows[kernel])))
rejects('borrowed input macro', lambda rows: rows[kernel].update(
    command=rows[kernel]['command'] + ' -DNODE_CRYPTO_AUDITED_BORROW=1'))
rejects('host OpenSSL include', lambda rows: rows[kernel].update(
    command=rows[kernel]['command'].replace(include, '/usr/local/include/openssl')))
rejects('syntax cannot substitute for compilation', lambda rows: rows[kernel].update(
    command=rows[kernel]['command'] + ' -fsyntax-only'))

for path, (row, _) in list(captured.items()):
    checked(row)
for base, names in families.items():
    assert {p.relative_to(base).as_posix() for p in Path(base).rglob('*') if p.is_file()} == names
summary = dict(schemaVersion=1, sourceIndex=own, checks='all assertions passed',
               currentHashedFiles=len(captured), indexedFamilies=len(families),
               declaredInputRows=2622, nativeSourceFiles=357, retained=353, changed=2,
               added=2, metadataFields=83, selectedManifests=12,
               exactToolingReversals=54, independentPureCommandChecks=tests,
               originalPureModelImported=True, nativeHelperImported=False,
               stageBuildCompilerEngineOrCryptoInvoked=False,
               scope='Exact declared Source boundary, not recursive historical BUILD ledgers')
(OWN / 'reader-results.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
