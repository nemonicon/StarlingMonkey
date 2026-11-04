"""Finish independent DATA-only result checks and seal this review's text files."""
import codecs
import hashlib
import json
import os
import stat
from pathlib import Path

HERE = Path(__file__).parent
CLASSIC = HERE.parent
ADOPTION = CLASSIC / 'production-adoption-v1'
ROOT = Path('/tmp/starling-node-compat/classic-artifact-preservation-pending-v1').resolve(strict=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def write(name, value):
    with (HERE / name).open('x') as target:
        json.dump(value, target, indent=2); target.write('\n')


index_raw = (ROOT / 'index.json').read_bytes()
assert sha(index_raw) == '1934c03e75e23a24e35e944502692a7cde774e5f49a132a63c1686cc5d7babde'
index = json.loads(index_raw)
completion_raw = (ROOT / 'completion.json').read_bytes()
assert sha(completion_raw) == '0177ec7f2c9daf2f2376af997dd7a798ebe7e96e8068ee3c68fc005a773b1b1b'
completion = json.loads(completion_raw)
root_stat = ROOT.lstat()
assert stat.S_ISDIR(root_stat.st_mode) and stat.S_IMODE(root_stat.st_mode) == 0o700
assert completion['rootIdentity'] == {'device': root_stat.st_dev, 'inode': root_stat.st_ino}
report = load(HERE / 'results.json')
assert report['verifiedPassed'] is True and report['checkCount'] == 8
actual = load(ROOT / 'results.json')
stdout = load('/tmp/starling-node-compat/classic-artifact-preservation-copy-v1.stdout.log')
assert stdout['state'] == 'PENDING_INDEPENDENT_REVIEW' and stdout['accepted'] is False
assert stdout['privateRoot'] == '/tmp/starling-node-compat/classic-artifact-preservation-pending-v1'
assert stdout['completion'] == {'path': 'completion.json', 'sha256': sha(completion_raw), 'bytes': 704}

source_result = load(ROOT / 'evidence/publisher-source-review/results.json')
required = {'schemaVersion': 1, 'state': 'INDEPENDENT_CLASSIC_PRESERVATION_PUBLISHER_SOURCE_REVIEW_PASSED',
            'publisherSourceIndexSha256': 'fb9baef5e9886c17a4d335738497adeac96e2a003ced4f14dcd35b99a2456b73',
            'sourceOnly': True, 'sourceReviewPassed': True, 'ownerActionsInvoked': False,
            'archiveCopyExecuted': False, 'sourcePromotionIssued': False, 'runtimeAcceptanceClaim': False}
for key, value in required.items():
    assert type(source_result[key]) is type(value) and source_result[key] == value
source_index = load(ROOT / 'evidence/publisher-source-review/index.json')
assert len([r for r in source_index['files'] if r['path'] == 'results.json' and
            r['sha256'] == '1435c36fd9f8e8873192bd00079caa14945ffd6d648794e28cd6192e3b4c4fa0']) == 1
memory_index = load(ROOT / 'evidence/late-memory-proof/index.json')
assert len(memory_index['files']) == 16
assert len([r for r in memory_index['files'] if r['path'] == 'results.json' and
            r['sha256'] == '7c47de9da9a24da84731dbd97478ddd5567dcaece77a723acf6409aa30726e1d']) == 1

# Confirm actual storage classes. Text is checked incrementally, never formatted
# into an assertion or retained in a giant per-byte array. Binary bytes are data.
counts = {'text': 0, 'centralSourceBinary': 0, 'externalWasm': 0}
for row in actual['copiedObjects']:
    name = row['destination']
    if name.startswith('evidence/text/objects/'):
        path = ROOT / name
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        decoder = codecs.getincrementaldecoder('utf-8')('strict')
        try:
            before = os.fstat(fd)
            while True:
                block = os.read(fd, 1024 * 1024)
                if not block:
                    break
                assert b'\0' not in block
                decoder.decode(block, final=False)
            decoder.decode(b'', final=True)
            after = os.fstat(fd)
            assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == \
                   (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        finally:
            os.close(fd)
        counts['text'] += 1
    elif name.startswith('external-wasm/objects/'):
        with (ROOT / name).open('rb') as source:
            assert source.read(4) == b'\0asm'
        counts['externalWasm'] += 1
    elif name.startswith('evidence/source/'):
        counts['centralSourceBinary'] += 1
assert counts == {'text': 10516, 'centralSourceBinary': 5, 'externalWasm': 260}
assert sha((ROOT / 'index.json').read_bytes()) == sha(index_raw)
assert sha((ROOT / 'completion.json').read_bytes()) == sha(completion_raw)
assert (ROOT.lstat().st_dev, ROOT.lstat().st_ino) == (root_stat.st_dev, root_stat.st_ino)
write('additional-checks.json', {
    'schemaVersion': 1,
    'state': 'ACTUAL_PRESERVATION_CAPSULE_AND_STORAGE_CLASS_CHECKS_PASSED',
    'actualRawStdoutAndCompletionTupleMatch': True,
    'sourceReviewExactContractIndexedOnce': True,
    'actualMemorySixteenMembersAndResultIndexedOnce': True,
    'incrementallyVerifiedNulFreeUtf8TextObjects': counts['text'],
    'verifiedExternalWasmMagicAsData': counts['externalWasm'],
    'exactCentralBinarySourceObjectCount': counts['centralSourceBinary'],
    'archiveRootIndexCompletionUnchanged': True,
    'runtimeToolsOrOwnerActionsInvoked': False,
})
write('review-receipt.json', {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_ACTUAL_PRIVATE_PRESERVATION_REVIEW_COMPLETE_PENDING_ROOT_DECISION',
    'resultsSha256': sha((HERE / 'results.json').read_bytes()),
    'archiveIndexSha256': sha(index_raw),
    'archiveCompletionSha256': sha(completion_raw),
    'archiveResultSha256': '306ae3e4516f13870f821d3ceb33cf2ee8206528abaa0abc7d7c8af2a4cbf86f',
    'rootCopyResultSha256': '14451a5496c2384ffb2fab0e5ae2da0f141cbbbf9aef536cab5b79d03a1dfd73',
    'regularFilesIndependentlyVerified': 21682,
    'copiedObjectsIndependentlyVerified': 10835,
    'selectedTuplesIndependentlyVerified': 50894,
    'allPlannedOriginalPhysicalInputHashesRechecked': 18751,
    'newRuntimeExecutionOrAcceptanceClaim': False,
    'reviewerInvokedPublisherOrOwnerActions': False,
    'sourcePromotionIssued': False,
    'archiveAcceptanceIssued': False,
    'pendingArchiveModified': False,
    'originalPathsRedirected': False,
    'readerCorrectionHistoryPreserved': True,
})
rows = []
for path in sorted(HERE.rglob('*')):
    if path.is_dir():
        continue
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink()
    if path.name == 'index.json':
        continue
    raw = path.read_bytes()
    assert b'\0' not in raw
    raw.decode('utf-8', 'strict')
    rows.append({'path': str(path.relative_to(HERE)), 'sha256': sha(raw), 'bytes': len(raw)})
assert len([r for r in rows if r['path'] == 'results.json']) == 1
write('index.json', {'schemaVersion': 1,
                     'state': 'SEALED_INDEPENDENT_ACTUAL_PRIVATE_PRESERVATION_RESULTS_REVIEW',
                     'files': rows, 'fileCount': len(rows), 'bytes': sum(r['bytes'] for r in rows),
                     'archiveAcceptanceIssued': False, 'sourcePromotionIssued': False,
                     'runtimeAcceptanceClaim': False})
for row in rows:
    raw = (HERE / row['path']).read_bytes()
    assert sha(raw) == row['sha256'] and len(raw) == row['bytes']
print(json.dumps({'indexSha256': sha((HERE / 'index.json').read_bytes()),
                  'indexedFiles': len(rows), 'indexedBytes': sum(r['bytes'] for r in rows),
                  'resultsSha256': sha((HERE / 'results.json').read_bytes()),
                  'receiptSha256': sha((HERE / 'review-receipt.json').read_bytes()),
                  'archiveAcceptanceIssued': False, 'sourcePromotionIssued': False}))
