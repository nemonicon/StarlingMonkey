"""Independent read-only verification: exact67 public outputs, no compactor import.

No compression, reversal, deletion, compiler, componentization or guest call.
Only new verification receipts are written, with exclusive creation.
"""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import os
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SUMMARY = Path('/tmp/starling-node-compat/storage-compaction-additional-public-v1/20261103T181027Z-fea6a995.summary.json')
AUDIT = REPO/'tests/node-compat/storage-candidate-audit-additional-public-v1/inventory.json'
PACKET = REPO/'tests/node-compat/storage-compaction-additional-public-v1'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


assert sha(AUDIT) == 'dc9e37e95736b9ccd8a630513d02c8ad35e2be24d72b2f3f4743c3393e993e96'
assert sha(AUDIT.with_name('index.json')) == '4fe5ad4a02f75c5a2380d3d6be8d0145a19255ac13baf987be4dbf73f7153cbc'
assert sha(PACKET/'index.json') == '7550d3e995e1f3f3fd06e34a9b3486545296fe29b544e9813304b3e128880fdd'
for directory in [AUDIT.parent, PACKET]:
    for row in read(directory/'index.json')['files']:
        assert sha(directory/row['path']) == row['sha256'], row['path']
assert sha(SUMMARY) == '73940fc75bf0d4fdb816c5b2a859f4a230fd19d0eb4fe26113741f572e4a7983'
audit, summary = read(AUDIT), read(SUMMARY)
assert audit['eligibleCount'] == len(audit['files']) == 67
assert summary['apply'] is True and summary['completed'] is True
assert summary['compressedFiles'] == summary['eligibleFiles'] == 67
assert not summary['failures'] and summary['skippedEntries'] == 0
assert summary['physicalBytesRecovered'] == 542859264
assert summary['releaseAcceptanceOrCompatibilityClaim'] is False
assert summary['terminalProofKindCounts'] == dict(collections.Counter(row['terminalProof']['kind'] for row in audit['files']))
journal = Path(summary['journal'])
assert sha(journal) == summary['journalSha256']
assert sha(summary['frozenInputs']) == summary['frozenInputsSha256'] == summary['expectedInventorySha256'] == 'cf2a41438715c8ca9f027c8b435117c5681b1dc09f2515e3f0ddb28bc98aa22d'
frozen = {row['path']: row for row in read(summary['frozenInputs'])['files']}
expected_paths = {row['path'] for row in audit['files']}
assert set(frozen) == expected_paths
records = [json.loads(line) for line in journal.read_text().splitlines()]
events = {}
for event in ['prepared','after','rollback-link-released','headroom-check','ditto-copy-result']:
    selected = [row for row in records if row['event'] == event]
    assert len(selected) == len({row['path'] for row in selected}) == 67
    assert {row['path'] for row in selected} == expected_paths
    events[event] = {row['path']: row for row in selected}
assert not any(row['event'] in ['failure','rolled-back'] for row in records)
for row in events['headroom-check'].values():
    assert row['freeBytes'] >= row['requiredBytes']
    assert row['requiredBytes'] == 2*frozen[row['path']]['before']['logicalBytes'] + 64*1024*1024
assert all(row['returncode'] == 0 for row in events['ditto-copy-result'].values())
for row in events['prepared'].values():
    for key in ['rollbackPath','temporaryPath']:
        path = Path(row[key])
        assert not path.exists() and not path.is_symlink(), path
witnesses = set()
verified = []
for old in audit['files']:
    path = Path(old['path'])
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not path.is_symlink()
    assert value.st_flags == 32 and value.st_nlink == 1
    observed = {'logicalBytes':value.st_size, 'mode':stat.S_IMODE(value.st_mode),
                'uid':value.st_uid, 'gid':value.st_gid, 'mtimeNs':value.st_mtime_ns}
    for key,result in observed.items():
        assert result == old[key], (path,key)
    attrs = {}
    for name in subprocess.check_output(['/usr/bin/xattr',str(path)],text=True).splitlines():
        if name == 'com.apple.decmpfs':
            continue
        raw = subprocess.check_output(['/usr/bin/xattr','-p','-x',name,str(path)],text=True)
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    assert attrs == old['xattrDigests'], path
    assert subprocess.check_output(['/bin/ls','-led',str(path)],text=True).splitlines()[1:] == old['acl']
    assert sha(path) == old['sha256'], path
    after = events['after'][str(path)]['after']
    allocated = value.st_blocks*512
    assert allocated == after['allocatedBytes'] < old['allocatedBytes']
    assert value.st_ino == after['inode']
    assert value.st_dev == after['device']
    assert frozen[str(path)]['terminalProof'] == old['terminalProof']
    proof = old['terminalProof']
    assert proof['releaseAcceptanceClaimed'] is False
    pairs = [(Path(proof['path']),proof['sha256'])]
    for name in ['hostReport','finalReport']:
        if name in proof:
            pairs.append((Path(proof[name]['path']),proof[name]['sha256']))
    if 'laterAcceptedReport' in proof:
        pairs.append((Path(proof['laterAcceptedReport']),proof['laterAcceptedReportSha256']))
    pairs += [(Path(row['path']),row['sha256']) for row in old.get('generatedJsReferences',[])]
    if 'componentPath' in old:
        pairs.append((Path(old['componentPath']),old['componentSha256']))
    for witness,digest in pairs:
        assert witness.is_file() and not witness.is_symlink()
        assert sha(witness) == digest, witness
        witnesses.add((str(witness),digest))
    verified.append({'path':str(path),'sha256':old['sha256'],'logicalBytes':value.st_size,
                     'oldAllocatedBytes':old['allocatedBytes'],'newAllocatedBytes':allocated,
                     'flags':value.st_flags,'nlink':value.st_nlink,'terminalProofKind':proof['kind']})
assert len(verified) == 67 and len(witnesses) == summary['reportClosureWitnessesVerified'] == 63
assert sum(row['oldAllocatedBytes'] for row in verified) == summary['oldAllocatedBytes']
assert sum(row['newAllocatedBytes'] for row in verified) == summary['newAllocatedBytes']
assert sum(row['logicalBytes'] for row in verified) == summary['logicalBytes']
assert sum(row['oldAllocatedBytes']-row['newAllocatedBytes'] for row in verified) == summary['physicalBytesRecovered']
# Reauthenticate original source/dry-run artifacts after all public file reads.
for row in read(PACKET/'index.json')['files']:
    assert sha(PACKET/row['path']) == row['sha256']
free = os.statvfs(HERE).f_bavail*os.statvfs(HERE).f_frsize
result = {'state':'INDEPENDENT_READ_ONLY_POST_COMPRESSION_VERIFICATION_PASSED',
          'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'summary':{'path':str(SUMMARY),'sha256':sha(SUMMARY)},
          'journal':{'path':str(journal),'sha256':sha(journal)},
          'auditSha256':sha(AUDIT),'sourceAndDryRunPacketIndexSha256':sha(PACKET/'index.json'),
          'filesRehashed':67,'requiredMetadataUnchanged':True,
          'allUfCompressedRegularSingleLink':True,'allFilesHaveSmallerAllocation':True,
          'allKnown67RollbackAndTemporaryPathsAbsent':True,'rollbackReleaseRecords':67,
          'successfulDittoCopyRecords':67,'headroomRecordsVerified':67,
          'terminalReportJsAndPairedComponentWitnessesRehashed':63,
          'sourceAndDryRunPacketUnchanged':True,'releaseAcceptanceOrCompatibilityClaim':False,
          'terminalProofKindCounts':summary['terminalProofKindCounts'],
          'logicalBytesVerified':summary['logicalBytes'],'oldAllocatedBytes':summary['oldAllocatedBytes'],
          'newAllocatedBytes':summary['newAllocatedBytes'],
          'measuredPhysicalAllocationReductionBytes':summary['physicalBytesRecovered'],
          'currentFreeBytesNonreserved':free,'twoGiBLaunchGateMetAtObservation':free>=2*1024**3,
          'files':verified,'compressionDeletionBuildGuestOrReversalCopyExecutedByVerifier':False,
          'limitations':['Summed file-block reduction is not exclusive volume-space causality.',
                        'No induced rollback/reversal/fault proof; failed-original, build-only and benchmark labels remain unchanged.']}
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
index = {'state':'INDEPENDENT_READ_ONLY_STORAGE_VERIFICATION_FROZEN',
         'files':[{'path':name,'sha256':sha(HERE/name),'bytes':(HERE/name).stat().st_size} for name in ['verify.py','results.json']],
         'compressionDeletionBuildOrGuestExecuted':False}
with (HERE/'index.json').open('x') as stream:
    json.dump(index,stream,indent=2)
    stream.write('\n')
print(json.dumps({'state':result['state'],'files':67,'physicalBytesRecovered':summary['physicalBytesRecovered'],
                  'reportSha256':sha(HERE/'results.json'),'indexSha256':sha(HERE/'index.json'),'currentFreeBytesNonreserved':free}))
