"""Independent read-only verification of Root's exact two-pair CoW operation.

No import of cow.py, clone/compression call, library execution or asset write.
Only this new verification directory receives output.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess


REPO = Path(__file__).resolve().parents[3]
BASE = Path('/tmp/starling-node-compat/storage-cow-release-inputs-v1')
RUN = '20261103T185556Z-6973297f'
HELPER_SHA = '0885aa9fa8aff6dde7d685757dad54d9d7a889a309b9dddd7bf862db8f2a1bcc'
SNAPSHOT_SHA = '6d152e16f849fcf97495aef5118fc3a0c593188399cb20f34d7fb4fcb51af11f'
JOURNAL_SHA = 'a0a446fa76d46076ebe770338e5007347cb463f1a284b5664f49af17942f1c5f'
PACKET_SHA = '47e9c89ad3bc8c1daa1641fc90fa857a6ec00eba8b0217c882554ca90be12049'
EXPECTED = {
    'release-library': ('libspidermonkey.a', 538170426,
                        '298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'),
    'release-archive': ('spidermonkey-release.tar.gz', 184568633,
                        'c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'),
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def attributes(path):
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not path.is_symlink()
    return {'device': value.st_dev, 'inode': value.st_ino,
            'logicalBytes': value.st_size, 'allocatedBytes': value.st_blocks * 512,
            'mode': stat.S_IMODE(value.st_mode), 'uid': value.st_uid, 'gid': value.st_gid,
            'mtimeNs': value.st_mtime_ns, 'flags': value.st_flags, 'nlink': value.st_nlink,
            'regular': True, 'symlink': False}


def required_metadata(path):
    value = attributes(path)
    attrs = {}
    for name in subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines():
        raw = subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(path)], text=True)
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    acl = subprocess.check_output(['/bin/ls', '-led', str(path)], text=True).splitlines()[1:]
    return {key: value[key] for key in ('logicalBytes', 'mode', 'uid', 'gid', 'mtimeNs')} | {
        'xattrDigests': attrs, 'acl': acl}


def identity(value):
    return {key: value[key] for key in ('device', 'inode', 'logicalBytes', 'allocatedBytes',
            'mode', 'uid', 'gid', 'mtimeNs', 'flags', 'nlink', 'regular', 'symlink')}


summary_path = BASE / (RUN + '.summary.json')
summary_sha = sha(summary_path)
assert summary_sha.startswith('34653680') and summary_sha.endswith('8685f9c')
summary = json.loads(summary_path.read_bytes())
assert summary['completed'] is True and summary['state'] == 'APPLY_VERIFIED'
assert summary['apply'] is True and summary['rootBuildQuiescenceAcknowledged'] is True
assert summary['clonefileCalls'] == summary['successfulClonefileCalls'] == summary['adoptedTargets'] == 2
assert not summary['failures'] and not summary['evidenceErrors']
assert summary['helperSha256'] == HELPER_SHA and summary['frozenInputsSha256'] == SNAPSHOT_SHA
assert summary['journalSha256'] == JOURNAL_SHA
assert summary['nonexclusiveFreeDeltaBytes'] == 3612672
assert summary['uniqueExtentRecoveryProved'] is False
assert summary['exclusivePhysicalBytesRecovered'] is None
assert all(row['unchanged'] for row in summary['sourcePostchecks'])

snapshot_path = Path(summary['frozenInputs'])
assert sha(snapshot_path) == SNAPSHOT_SHA
snapshot = json.loads(snapshot_path.read_bytes())
assert snapshot['helperSha256'] == HELPER_SHA
assert {row['name'] for row in snapshot['pairs']} == set(EXPECTED)
journal_path = Path(summary['journal'])
assert sha(journal_path) == JOURNAL_SHA
records = [json.loads(line) for line in journal_path.read_text().splitlines()]
assert not any(row['event'] in ('failure', 'cleanup-failure', 'rolled-back') for row in records)
pre_lsof = [row for row in records if row['event'] == 'lsof-preapply']
assert len(pre_lsof) == 1 and pre_lsof[0]['returncode'] == 1
assert not pre_lsof[0]['stdout'] and not pre_lsof[0]['stderr']

verified = []
for pair in snapshot['pairs']:
    name = pair['name']
    basename, size, digest = EXPECTED[name]
    source, target = Path(pair['source']['path']), Path(pair['target']['path'])
    assert source.name == target.name == basename
    expected_parent = 'spidermonkey-dist-release/' if name == 'release-library' else ''
    assert str(source) == '/tmp/starling-node-compat/native-build/' + expected_parent + basename
    assert str(target) == '/tmp/starling-node-compat/improved-build/' + expected_parent + basename
    assert pair['source']['sha256'] == pair['target']['sha256'] == digest
    before_source = attributes(source)
    before_target = attributes(target)
    assert sha(source) == sha(target) == digest  # Four complete file hashes, no execution.
    assert source.stat().st_size == target.stat().st_size == size
    assert attributes(source) == before_source and attributes(target) == before_target
    assert identity(before_source) == identity(pair['source']['before'])
    assert required_metadata(source) == pair['source']['metadata']
    assert required_metadata(target) == pair['target']['metadata']
    assert before_target['flags'] == 0 and before_target['nlink'] == 1
    assert before_target['inode'] != before_source['inode']
    assert before_target['inode'] != pair['target']['before']['inode']
    adopted = [row for row in summary['pairs'] if row['name'] == name]
    assert len(adopted) == 1 and adopted[0]['directClonefileReturn'] == 0
    assert identity(before_target) == identity(adopted[0]['after'])
    events = [(index, row) for index, row in enumerate(records) if row.get('name') == name]
    calls = [(index, row) for index, row in events if row['event'] == 'clonefile-result']
    prepared = [(index, row) for index, row in events if row['event'] == 'prepared']
    after = [(index, row) for index, row in events if row['event'] == 'after']
    released = [(index, row) for index, row in events if row['event'] == 'rollback-link-released']
    assert len(calls) == len(prepared) == len(after) == len(released) == 1
    assert calls[0][1]['returncode'] == calls[0][1]['errno'] == 0
    assert calls[0][1]['flags'] == 1
    assert calls[0][0] < prepared[0][0] < after[0][0] < released[0][0]
    assert prepared[0][1]['clone']['inode'] == before_target['inode']
    assert after[0][1]['sourcePreimageUnchanged'] and after[0][1]['requiredMetadataVerified']
    verified.append({'name': name, 'source': str(source), 'target': str(target),
                     'sha256': digest, 'logicalBytesEach': size,
                     'sourceIdentityUnchanged': True, 'sourceRequiredMetadataUnchanged': True,
                     'targetRequiredMetadataUnchanged': True, 'sourceIdentity': before_source,
                     'targetIdentity': before_target, 'targetNewDistinctInode': True,
                     'cloneReturn0AndOrderedReleaseJournalVerified': True})

# Include every known temp/rollback path in this operation namespace's journals,
# including earlier dry runs (which should contain no mutation events).
known = set()
all_journals = []
for path in sorted(BASE.glob('*.journal.jsonl')):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        for key in ('temporary', 'rollback'):
            if row.get(key):
                known.add(row[key])
    all_journals.append({'path': str(path), 'sha256': sha(path)})
assert len(known) == 4
assert all(not os.path.lexists(path) for path in known)

packet = REPO / 'tests/node-compat/storage-cow-release-inputs-v1'
assert sha(packet / 'index.json') == PACKET_SHA
index = json.loads((packet / 'index.json').read_bytes())
assert len(index['files']) == 12
for row in index['files']:
    path = Path(row['path'])
    if not path.is_absolute():
        path = packet / path
    assert path.is_file() and sha(path) == row['sha256']
    if 'bytes' in row:
        assert path.stat().st_size == row['bytes']

report = {'schemaVersion': 1, 'state': 'INDEPENDENT_READ_ONLY_COW_POSTVERIFICATION_PASS',
          'timestampUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceSummary': str(summary_path), 'sourceSummarySha256': summary_sha,
          'sourceJournal': str(journal_path), 'sourceJournalSha256': JOURNAL_SHA,
          'snapshotPath': str(snapshot_path), 'snapshotSha256': SNAPSHOT_SHA,
          'helperSha256': HELPER_SHA, 'verifierSha256': sha(Path(__file__)),
          'fourFullFileHashesVerified': True, 'pairs': verified,
          'sourceDryrunPacketIndexSha256': PACKET_SHA, 'sourceDryrunFilesRehashed': 12,
          'allKnownTemporaryAndRollbackPathsAbsent': sorted(known), 'journalNamespaceRehashed': all_journals,
          'reportedClonefileReturn0': 2, 'reportedAdoptions': 2,
          'operationNonexclusiveFreeDeltaBytes': 3612672,
          'uniqueExtentRecoveryProved': False, 'exclusivePhysicalBytesRecovered': None,
          'diskFreeAtIndependentObservationBytes': shutil.disk_usage(BASE).free,
          'requiredMetadata': ['logical size', 'mode', 'uid', 'gid', 'mtime_ns', 'all xattr digests', 'ACL'],
          'excludedFromProtectedIdentity': ['read atime', 'ctime', 'creation time'],
          'assetsModifiedByVerifier': False, 'helperOrClonefileRerun': False,
          'compilerGuestLibraryExecution': False, 'noCompressionRetry': True,
          'limits': ['Clonefile returns are authenticated operation records, not repeated syscalls.',
                     'No unique/shared physical extent inspection or 722MB recovery claim.',
                     'Global free-space delta is nonexclusive and not runtime performance.',
                     'Rollback/restoration failure branches were not induced.']}
output = Path(__file__).with_name('results.json')
with output.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'results': str(output), 'resultsSha256': sha(output),
                  'fourHashes': True, 'unchangedSourceDryrunFiles': 12,
                  'absentKnownPaths': len(known), 'nonexclusiveFreeDeltaBytes': 3612672}))
