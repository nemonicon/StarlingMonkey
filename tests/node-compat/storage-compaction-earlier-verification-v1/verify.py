"""Independent read-only post-compression verification of exactly 92 files.

No compactor import, compression, reversal copy, deletion, build or guest call.
Writes only new verification receipts beside this source.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SUMMARY = Path('/tmp/starling-node-compat/storage-compaction-earlier-v1/20261103T174608Z-033ee1db.summary.json')
AUDIT = REPO / 'tests/node-compat/storage-candidate-audit-earlier-v1/results.json'
PACKET = REPO / 'tests/node-compat/storage-compaction-earlier-v1'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def json_read(path):
    return json.loads(Path(path).read_bytes())


assert sha(AUDIT) == '6a3664ff4ebe283910672090ed4481123ab3d634146781ff7a9321a1302378a8'
assert sha(PACKET / 'index.json') == '8f16992e5cf12d900042398b145a641fa574e7d571fd07a5805ed30b130f524d'
for row in json_read(PACKET / 'index.json')['files']:
    assert sha(PACKET / row['path']) == row['sha256']
audit = json_read(AUDIT)
summary = json_read(SUMMARY)
assert summary['apply'] is True and summary['completed'] is True
assert summary['compressedFiles'] == summary['eligibleFiles'] == 92
assert not summary['failures'] and summary['skippedEntries'] == 0
assert summary['physicalBytesRecovered'] == 810020864
journal = Path(summary['journal'])
assert sha(journal) == summary['journalSha256']
assert sha(summary['frozenInputs']) == summary['frozenInputsSha256'] == summary['expectedInventorySha256']
assert summary['frozenInputsSha256'] == '3ef59f2f8f38903e138054d2b758bfd2e35ecca21279fa557997bdafd2737efa'
records = [json.loads(line) for line in journal.read_text().splitlines()]
prepared = [row for row in records if row['event'] == 'prepared']
after = {row['path']: row for row in records if row['event'] == 'after'}
released = [row for row in records if row['event'] == 'rollback-link-released']
assert len(prepared) == len(after) == len(released) == 92
assert not any(row['event'] in ['failure', 'rolled-back'] for row in records)
assert set(after) == {row['path'] for row in audit['files']}
for row in prepared:
    for key in ['rollbackPath', 'temporaryPath']:
        path = Path(row[key])
        assert not path.exists() and not path.is_symlink(), path
proofs = {}
verified = []
for old in audit['files']:
    path = Path(old['path'])
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not path.is_symlink()
    assert value.st_flags == 32 and value.st_nlink == 1
    observed = {'logicalBytes': value.st_size, 'mode': stat.S_IMODE(value.st_mode),
                'uid': value.st_uid, 'gid': value.st_gid, 'mtimeNs': value.st_mtime_ns}
    for key, result in observed.items():
        assert result == old[key], (path, key)
    attrs = {}
    for name in subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines():
        if name == 'com.apple.decmpfs':
            continue
        raw = subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(path)], text=True)
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    assert attrs == old['xattrDigests']
    assert subprocess.check_output(['/bin/ls', '-led', str(path)], text=True).splitlines()[1:] == old['acl']
    assert sha(path) == old['sha256'], path
    allocated = value.st_blocks * 512
    assert allocated == after[str(path)]['after']['allocatedBytes'] < old['allocatedBytes']
    assert value.st_ino == after[str(path)]['after']['inode']
    proof = old['completionProof']
    for key, digest in [('milestoneSummary', 'milestoneSummarySha256'),
                        ('archivedReport', 'reportSha256'), ('currentOriginalReport', 'reportSha256')]:
        witness = Path(proof[key])
        if not witness.is_absolute():
            witness = REPO / witness
        assert sha(witness) == proof[digest]
        proofs[str(witness)] = proof[digest]
    for witness in old.get('generatedJsReferences', []):
        assert sha(witness['path']) == witness['sha256']
        proofs[witness['path']] = witness['sha256']
    verified.append({'path': str(path), 'sha256': old['sha256'], 'logicalBytes': value.st_size,
                     'oldAllocatedBytes': old['allocatedBytes'], 'newAllocatedBytes': allocated,
                     'flags': value.st_flags, 'nlink': value.st_nlink})
assert len(verified) == 92 and len(proofs) == 71
assert sum(row['oldAllocatedBytes'] for row in verified) == summary['oldAllocatedBytes']
assert sum(row['newAllocatedBytes'] for row in verified) == summary['newAllocatedBytes']
assert sum(row['oldAllocatedBytes'] - row['newAllocatedBytes'] for row in verified) == summary['physicalBytesRecovered']
free = os.statvfs(HERE).f_bavail * os.statvfs(HERE).f_frsize
result = {'state': 'INDEPENDENT_READ_ONLY_POST_COMPRESSION_VERIFICATION_PASSED',
          'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'summary': {'path': str(SUMMARY), 'sha256': sha(SUMMARY)},
          'journal': {'path': str(journal), 'sha256': sha(journal)},
          'auditSha256': sha(AUDIT), 'sourceAndDryRunPacketIndexSha256': sha(PACKET / 'index.json'),
          'filesRehashed': 92, 'requiredMetadataUnchanged': True,
          'allUfCompressedRegularSingleLink': True, 'allFilesHaveSmallerAllocation': True,
          'allKnown92RollbackAndTemporaryPathsAbsent': True, 'rollbackReleaseRecords': 92,
          'acceptedReportAndGeneratedJsWitnessesRehashed': 71,
          'sourceAndDryRunPacketUnchanged': True,
          'logicalBytesVerified': summary['logicalBytes'], 'oldAllocatedBytes': summary['oldAllocatedBytes'],
          'newAllocatedBytes': summary['newAllocatedBytes'], 'measuredPhysicalAllocationReductionBytes': summary['physicalBytesRecovered'],
          'currentFreeBytesNonreserved': free, 'twoGiBLaunchGateMetAtObservation': free >= 2 * 1024**3,
          'files': verified, 'compressionDeletionBuildGuestOrReversalCopyExecutedByVerifier': False,
          'limitations': ['Allocation reduction is summed per-file st_blocks, not exclusive whole-filesystem free-space causality.',
                          'No rollback failure branch or reversal-copy test executed; prior accepted bytes and runtime claims unchanged.']}
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
index = {'state': 'INDEPENDENT_READ_ONLY_STORAGE_VERIFICATION_FROZEN',
         'files': [{'path': name, 'sha256': sha(HERE / name), 'bytes': (HERE / name).stat().st_size}
                   for name in ['verify.py', 'results.json']],
         'compressionDeletionBuildOrGuestExecuted': False}
with (HERE / 'index.json').open('x') as stream:
    json.dump(index, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': result['state'], 'files': 92, 'physicalBytesRecovered': summary['physicalBytesRecovered'],
                  'reportSha256': sha(HERE / 'results.json'), 'indexSha256': sha(HERE / 'index.json'),
                  'currentFreeBytesNonreserved': free}))
