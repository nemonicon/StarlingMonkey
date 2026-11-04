"""Read-only verification of the exact20 newly compressed Release corpus files.

No compactor import, filesystem mutation of inputs, compiler or guest execution.
Only new verification receipts are written, exclusively, below HERE.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKET = REPO/'tests/node-compat/storage-compaction-current-release-corpus-v1'
AUDIT = REPO/'tests/node-compat/storage-candidate-audit-current-release-corpus-v1/results.json'
SUMMARY = Path('/tmp/starling-node-compat/storage-compaction-current-release-corpus-v1/20261103T190127Z-c009d6ce.summary.json')
CORPUS = Path('/tmp/starling-node-compat/foundation-scheduler-v4/ordinary-release-components-v1')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


assert sha(PACKET/'index.json') == 'd785bc81c979208131ac912370be32c388407a7ec7347b953558bbdde5f6ad61'
assert sha(AUDIT) == '6845fa7e5d16888c9d5c02182736490e107c7cbc753c9ea16217447463f1b271'
assert sha(AUDIT.with_name('index.json')) == '02f6f560f9121ed93335ee9d72cacb3c84f81cbe490f9239332f12ca3ecf5007'
for directory in [PACKET,AUDIT.parent]:
    for row in read(directory/'index.json')['files']:
        assert sha(directory/row['path']) == row['sha256'],row['path']
assert sha(SUMMARY) == '8502cb57cc9465aed6907a4e6f26ebe0838071a7a91ecf04f12abf843fc62fd0'
audit,summary = read(AUDIT),read(SUMMARY)
assert audit['artifactCount'] == audit['coreDependencyCount'] == 10 and len(audit['files']) == 20
assert summary['apply'] is True and summary['completed'] is True
assert summary['compressedFiles'] == summary['eligibleFiles'] == 20 and summary['skippedEntries'] == 0
assert not summary['failures'] and summary['physicalBytesRecovered'] == 149131264
assert summary['scriptSha256'] == sha(PACKET/'compact.py') == 'ee01bd140bda86474603f372a26f9258bd5a1cd675025abf78374464921b0241'
journal = Path(summary['journal'])
assert sha(journal) == summary['journalSha256']
assert sha(summary['frozenInputs']) == summary['frozenInputsSha256'] == summary['expectedInventorySha256'] == 'b7913a989850361497aa050f6beaa30d4835c3e2aa312f14850cb9848e4da7c7'
frozen = {row['path']:row for row in read(summary['frozenInputs'])['files']}
paths = {row['path'] for row in audit['files']}
assert len(paths) == len(frozen) == 20 and paths == set(frozen)
events = {}
records = [json.loads(line) for line in journal.read_text().splitlines()]
for event in ['prepared','after','rollback-link-released','headroom-check','ditto-copy-result']:
    selected = [row for row in records if row['event'] == event]
    assert len(selected) == len({row['path'] for row in selected}) == 20
    assert {row['path'] for row in selected} == paths
    events[event] = {row['path']:row for row in selected}
assert not any(row['event'] in ['failure','rolled-back'] for row in records)
for row in events['prepared'].values():
    for key in ['rollbackPath','temporaryPath']:
        path = Path(row[key])
        assert not path.exists() and not path.is_symlink(),path
for path,row in events['headroom-check'].items():
    assert row['requiredBytes'] == 2*frozen[path]['before']['logicalBytes']+64*1024*1024
    assert row['freeBytes'] >= row['requiredBytes']
assert all(row['returncode'] == 0 for row in events['ditto-copy-result'].values())
source = audit['sourceReport']
independent = audit['independentVerification']
assert source['path'] == str(CORPUS/'results.json')
assert source['sha256'] == 'c865931b5e5573f036d9386517d8b3720224ab80baf27b521cda87860e056161'
assert sha(source['path']) == source['sha256'] and sha(independent['path']) == independent['sha256']
report,prior = read(source['path']),read(independent['path'])
assert report['state'] == 'private-diagnostic-ordinary-components-passed'
assert prior['state'] == 'INDEPENDENT_READ_ONLY_ORDINARY_RELEASE_DIAGNOSTIC_VERIFICATION_PASSED'
assert prior['sourceReportSha256'] == source['sha256'] and prior['gcStress'] is False and prior['oomTesting'] is False
artifacts = {row['name']:row for row in report['artifacts']}
prior_artifacts = {row['name']:row for row in prior['artifacts']}
assert len(artifacts) == len(prior_artifacts) == 10
witnesses = set()


def witness(path,digest):
    path = Path(path)
    assert path.is_file() and not path.is_symlink() and sha(path) == digest,path
    witnesses.add((str(path),digest))


witness(source['path'],source['sha256'])
witness(independent['path'],independent['sha256'])
verified = []
for old in audit['files']:
    path = Path(old['path'])
    assert path.parent == CORPUS and not path.is_symlink()
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and value.st_flags == 32 and value.st_nlink == 1
    current = {'logicalBytes':value.st_size,'mode':stat.S_IMODE(value.st_mode),'uid':value.st_uid,'gid':value.st_gid,'mtimeNs':value.st_mtime_ns}
    assert all(current[key] == old[key] for key in current),path
    attrs = {}
    for name in subprocess.check_output(['/usr/bin/xattr',str(path)],text=True).splitlines():
        if name == 'com.apple.decmpfs':
            continue  # Compression representation is intentionally different.
        raw = subprocess.check_output(['/usr/bin/xattr','-p','-x',name,str(path)],text=True)
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    assert attrs == old['xattrDigests']
    assert subprocess.check_output(['/bin/ls','-led',str(path)],text=True).splitlines()[1:] == old['acl']
    assert sha(path) == old['sha256']
    after = events['after'][str(path)]['after']
    allocated = value.st_blocks*512
    assert allocated == after['allocatedBytes'] < old['allocatedBytes']
    assert (value.st_dev,value.st_ino) == (after['device'],after['inode'])
    assert frozen[str(path)]['sha256'] == old['sha256']
    assert frozen[str(path)]['metadata'] == {key:old[key] for key in ['logicalBytes','mode','uid','gid','mtimeNs','xattrDigests','acl']}
    binding = old['binding']
    artifact = artifacts[binding['artifactName']]
    assert artifact['interfaceAudit']['emittedImports'] == []
    assert artifact['componentSha256'] == prior_artifacts[binding['artifactName']]['componentSha256']
    assert hashlib.sha256(artifact['emittedWit'].encode()).hexdigest() == prior_artifacts[binding['artifactName']]['recordedWitSha256']
    witness(artifact['componentPath'],artifact['componentSha256'])
    witness(artifact['sourcePath'],artifact['sourceSha256'])
    if binding['kind'] == 'passed reported component':
        assert str(path) == artifact['componentPath'] and old['sha256'] == artifact['componentSha256']
    else:
        assert binding['kind'] == 'transpiled core directly referenced by reported Jco module'
        assert binding['componentPath'] == artifact['componentPath'] and binding['componentSha256'] == artifact['componentSha256']
        assert binding['modulePath'] == artifact['modulePath']
        witness(binding['modulePath'],binding['moduleSha256'])
        text = Path(binding['modulePath']).read_text()
        refs = re.findall(r"new URL\(['\"](\./[^'\"]+\.core\d*\.wasm)['\"],\s*import\.meta\.url\)",text)
        assert len(refs) == 1 and str(path) == str(CORPUS/refs[0][2:])
    verified.append({'path':str(path),'sha256':old['sha256'],'logicalBytes':value.st_size,
                     'oldAllocatedBytes':old['allocatedBytes'],'newAllocatedBytes':allocated,
                     'flags':value.st_flags,'nlink':value.st_nlink,'bindingKind':binding['kind']})
assert len(verified) == 20 and len(witnesses) == summary['reportClosureWitnessesVerified'] == 32
assert sum(row['logicalBytes'] for row in verified) == summary['logicalBytes'] == 242867185
assert sum(row['oldAllocatedBytes'] for row in verified) == summary['oldAllocatedBytes'] == 242909184
assert sum(row['newAllocatedBytes'] for row in verified) == summary['newAllocatedBytes'] == 93777920
assert sum(row['oldAllocatedBytes']-row['newAllocatedBytes'] for row in verified) == summary['physicalBytesRecovered']
assert sha(source['path']) == source['sha256']
for row in read(PACKET/'index.json')['files']:
    assert sha(PACKET/row['path']) == row['sha256']
free = os.statvfs(HERE).f_bavail*os.statvfs(HERE).f_frsize
result = {'schemaVersion':1,'state':'INDEPENDENT_READ_ONLY_EXACT20_POST_COMPRESSION_VERIFICATION_PASSED',
          'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'summary':{'path':str(SUMMARY),'sha256':sha(SUMMARY)},
          'journal':{'path':str(journal),'sha256':sha(journal)},
          'sourcePacketIndexSha256':sha(PACKET/'index.json'),'auditSha256':sha(AUDIT),
          'filesRehashed':20,'componentFiles':10,'directJcoCoreFiles':10,
          'requiredMetadataUnchanged':True,'allRegularUfCompressed32SingleLink':True,
          'allAllocationsSmallerAndMatchJournal':True,'all40KnownTemporaryAndRollbackPathsAbsent':True,
          'rollbackReleaseRecords':20,'successfulDittoRecords':20,'headroomRecordsVerified':20,
          'reportSourceAndBindingWitnessesRehashed':32,'sourcePacketUnchanged':True,
          'ordinaryReleaseReport':source,'ordinaryReleaseReportByteIdentical':True,
          'priorIndependentVerification':independent,'priorIndependentVerificationByteIdentical':True,
          'logicalBytes':summary['logicalBytes'],'oldAllocatedBytes':summary['oldAllocatedBytes'],
          'newAllocatedBytes':summary['newAllocatedBytes'],'summedFileAllocationReductionBytes':summary['physicalBytesRecovered'],
          'currentFreeBytesNonreserved':free,'twoGiBLaunchGateMetAtObservation':free>=2*1024**3,
          'files':verified,'witnesses':[{'path':path,'sha256':digest} for path,digest in sorted(witnesses)],
          'compressionDeletionBuildGuestOrCorpusRerunExecutedByVerifier':False,
          'limitations':['Summed st_blocks reduction is not exclusive whole-volume free-space attribution.',
                        'No rerun, new compatibility promotion, GC-stress, rollback/reversal/fault or publication-failure test.']}
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
index = {'state':'FROZEN_INDEPENDENT_READ_ONLY_EXACT20_POSTVERIFICATION',
         'files':[{'path':name,'sha256':sha(HERE/name),'bytes':(HERE/name).stat().st_size} for name in ['verify.py','results.json','README.md']]}
with (HERE/'index.json').open('x') as stream:
    json.dump(index,stream,indent=2);stream.write('\n')
print(json.dumps({'state':result['state'],'files':20,'resultSha256':sha(HERE/'results.json'),'indexSha256':sha(HERE/'index.json'),'summedFileAllocationReductionBytes':summary['physicalBytesRecovered'],'currentFreeBytesNonreserved':free}))
