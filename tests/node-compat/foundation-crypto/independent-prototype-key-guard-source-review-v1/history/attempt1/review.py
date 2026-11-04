"""Root read/hash/control-flow review. No owner import, SDK or key operation."""
from pathlib import Path
import hashlib, json, stat

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'prototype-key-guard-candidate-v1'
EXPECTED = '73fbf4f24e013bfe6f7f87830c95b8690ef1700683d9b9620b09ce839d9da831'
observed, cache = {}, {}
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def check(path, expected, size=None):
    p = Path(path)
    assert p.is_absolute() and not p.is_symlink()
    s = p.stat()
    assert stat.S_ISREG(s.st_mode)
    key = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if key not in cache:
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for raw in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(raw)
        after = p.stat()
        assert key == (after.st_dev, after.st_ino, after.st_size,
                       after.st_mtime_ns, after.st_ctime_ns)
        cache[key] = h.hexdigest()
    assert cache[key] == expected, p
    assert size is None or s.st_size == size, p
    observed[str(p)] = {'path': str(p), 'sha256': expected, 'bytes': s.st_size}

def indexed(root, digest):
    check(root / 'index.json', digest)
    index = json.loads((root / 'index.json').read_bytes())
    for row in index['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        check(root / row['path'], row['sha256'], row['bytes'])
    return index

index = indexed(OWNER, EXPECTED)
refs = json.loads((OWNER / 'source-inputs.json').read_bytes())['files']
for row in refs:
    check(row['path'], row['sha256'], row['bytes'])
composition = json.loads((OWNER / 'composition.json').read_bytes())
donor = HERE.parent / 'key-owner-candidate-v1'
indexed(donor, composition['ownerSourceIndexSha256'])
indexed(HERE.parent / 'independent-key-owner-source-review-v1',
        composition['ownerIndependentSourceReviewIndexSha256'])
for row in composition['afterimages']:
    if row['role'] == 'BYTE_EXACT_PARENT_OWNER_AFTERIMAGE':
        assert (OWNER / row['afterimage']).read_bytes() == (donor / row['afterimage']).read_bytes()

delta = json.loads((OWNER / 'source-derivations.json').read_bytes())
before = (OWNER / delta['preimage']).read_text()
after = (OWNER / delta['afterimage']).read_text()
current = before
for row in delta['edits']:
    assert current.count(row['old']) == 1
    current = current.replace(row['old'], row['new'], 1)
assert current == after and len(delta['edits']) == 2
for row in reversed(delta['edits']):
    assert current.count(row['new']) == 1
    current = current.replace(row['new'], row['old'], 1)
assert current == before
for operation in ['sign', 'verify']:
    body = after.split('bool SubtleCrypto::' + operation + '(', 1)[1]
    guard = body.index('&key_arg.toObject() == CryptoKey::proto_obj.get()')
    assert body.index('!CryptoKey::is_instance(key_arg) ||') < guard
    assert guard < body.index('JS::RootedObject key') < body.index('validate_crypto_buffer_source')
    assert guard < body.index('CryptoAlgorithmSignVerify::normalize') < body.index('CryptoKey::is_algorithm')
    assert 'return ReturnPromiseRejectedWithPendingError(cx, args);' in body[guard:body.index('JS::RootedObject key')]
for row in list(observed.values()):
    check(row['path'], row['sha256'], row['bytes'])
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_GUARD_SOURCE_DATA_CHECKS_PASSED',
          'sourceIndexSha256': EXPECTED, 'indexedFiles': len(index['files']),
          'preparationReferences': len(refs), 'observedPaths': len(observed),
          'uniquePhysicalHashReads': len(cache), 'exactReversibleGuardEdits': 2,
          'donorFourAfterimagesAndReviewAuthenticated': True,
          'sdkCompilerOwnerHelperKeyCryptoGcGuestOrRuntimeInvoked': False}
with (HERE / 'data-results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
with (HERE / 'rehashed-files.json').open('x') as stream:
    json.dump({'schemaVersion': 1, 'files': list(observed.values())}, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
