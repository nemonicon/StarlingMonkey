"""Independently read and hash an existing storage result; never rerun helpers."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import stat
import subprocess

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SUMMARY = Path('/tmp/starling-node-compat/storage-compaction-public-engines-v1/20261103T195936Z-9628b894.summary.json')
SUMMARY_SHA = '342c53de51e89ba3f1aff5a62fe30f074f9dd756cffa5755d6efe6899c37dc11'
JOURNAL_SHA = '95130b80a43d7aaa537a0b1c66090521cd42543753207244704a213bf5614322'
AUDIT = REPO / 'tests/node-compat/storage-candidate-audit-public-engines-v1'
COMPACTOR = REPO / 'tests/node-compat/storage-compaction-public-engines-v1'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def pinned(path, expected):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    assert digest(path) == expected, str(path)
    return path


def current(path):
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode) and not path.is_symlink()
    return dict(device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                logicalBytes=s.st_size, allocatedBytes=s.st_blocks * 512,
                mode=stat.S_IMODE(s.st_mode), uid=s.st_uid, gid=s.st_gid,
                mtimeNs=s.st_mtime_ns, flags=s.st_flags)


def preserved(path):
    value = current(path)
    names = subprocess.run(['/usr/bin/xattr', str(path)], check=True, capture_output=True, text=True).stdout.splitlines()
    attrs = {}
    for name in names:
        if name == 'com.apple.decmpfs':
            continue  # Filesystem compression metadata, deliberately introduced.
        raw = subprocess.run(['/usr/bin/xattr', '-px', name, str(path)], check=True, capture_output=True, text=True).stdout
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    acl = subprocess.run(['/bin/ls', '-lde', str(path)], check=True, capture_output=True, text=True).stdout.splitlines()[1:]
    return {key: value[key] for key in ['logicalBytes', 'mode', 'uid', 'gid', 'mtimeNs']} | dict(xattrDigests=attrs, acl=acl)


summary = json.loads(pinned(SUMMARY, SUMMARY_SHA).read_bytes())
assert summary['apply'] is True and summary['completed'] is True
assert summary['compressedFiles'] == summary['eligibleFiles'] == 72 and summary['failures'] == []
assert summary['skippedEntries'] == 0
assert summary['scriptSha256'] == '3b86a1b74ad12bd25abf496cd3162d5528d821aa3d6181276b444a2b592c95c5'
pinned(summary['script'], summary['scriptSha256'])
journal = pinned(summary['journal'], JOURNAL_SHA)
raw_lines = journal.read_bytes().splitlines(keepends=True)
events = [json.loads(line) for line in raw_lines]
assert events[-1]['event'] == 'finish' and events[-1]['completed'] is True
assert hashlib.sha256(b''.join(raw_lines[:-1])).hexdigest() == summary['journalSha256BeforeSummary']
assert summary['journalSha256'] == JOURNAL_SHA
expected = pinned(summary['expectedInventory'], summary['expectedInventorySha256'])
executed = pinned(summary['frozenInputs'], summary['frozenInputsSha256'])
assert expected.read_bytes() == executed.read_bytes()
preimage = json.loads(executed.read_bytes())
assert preimage['roots'] == summary['roots'] and preimage['excludedEntries'] == []
before = {row['path']: row for row in preimage['files']}
assert len(before) == 72

audit = json.loads(pinned(AUDIT / 'results.json', summary['acceptedPublicEngineAuditSha256']).read_bytes())
audit_index = json.loads(pinned(AUDIT / 'index.json', summary['acceptedPublicEngineAuditIndexSha256']).read_bytes())
witnesses = {}
for row in audit_index['files']:
    path = pinned(AUDIT / row['path'], row['sha256'])
    assert path.stat().st_size == row['bytes']
    witnesses[str(path)] = row['sha256']
for row in audit['acceptedMilestoneWitnesses'] + audit['terminalSidecars']:
    path = pinned(row['path'], row['sha256'])
    witnesses[str(path)] = row['sha256']
assert len(witnesses) == summary['reportClosureWitnessesVerified'] == 38
compactor_index = pinned(COMPACTOR / 'index.json', '235e95672dba11b8a07b7b067ec451c5dc0b88bc32bf9cb09ba74b0b1a0fa4ec')
for row in json.loads(compactor_index.read_bytes())['files']:
    path = pinned(COMPACTOR / row['path'], row['sha256'])
    assert path.stat().st_size == row['bytes']
pinned(REPO / 'tests/node-compat/storage-compaction-current-release-corpus-v1/compact.py',
       'ee01bd140bda86474603f372a26f9258bd5a1cd675025abf78374464921b0241')

event_sets = {}
for name in ['before', 'headroom-check', 'ditto-copy-result', 'prepared', 'after', 'rollback-link-released']:
    selected = [event for event in events if event['event'] == name]
    assert len(selected) == 72 and {row['path'] for row in selected} == set(before)
    assert len({row['path'] for row in selected}) == 72
    event_sets[name] = {row['path']: row for row in selected}
assert not any(event['event'] in ['failure', 'rolled-back', 'skip'] for event in events)

cleanup, files = [], []
for path_string, original in before.items():
    path = Path(path_string)
    assert event_sets['before'][path_string]['before'] == original['before']
    assert event_sets['before'][path_string]['sha256'] == original['sha256']
    copied = event_sets['ditto-copy-result'][path_string]
    assert copied['returncode'] == 0
    assert copied['stdoutHex'] == copied['stderrHex'] == ''
    headroom = event_sets['headroom-check'][path_string]
    assert headroom['freeBytes'] >= headroom['requiredBytes'] == 2 * original['before']['logicalBytes'] + 64 * 1024 * 1024
    prepared, after = event_sets['prepared'][path_string], event_sets['after'][path_string]
    assert prepared['before'] == original['before'] and prepared['sha256'] == original['sha256']
    indices = [next(i for i,event in enumerate(events) if event['event']==name and event.get('path')==path_string)
               for name in ['before','headroom-check','ditto-copy-result','prepared','after','rollback-link-released']]
    assert indices == sorted(indices)
    for key, prefix, suffix in [('temporaryPath','.storage-compression-','.wasm'),('rollbackPath','.storage-original-','.rollback')]:
        other = Path(prepared[key])
        assert other.parent == path.parent and other.name.startswith(prefix) and other.name.endswith(suffix)
        try:
            other.lstat()
        except FileNotFoundError:
            pass
        else:
            raise AssertionError('Recorded temporary/rollback path remains: ' + str(other))
        cleanup.append(str(other))
    value = current(path)
    assert value['flags'] == stat.UF_COMPRESSED == 32 and value['nlink'] == 1
    assert value['device'] == original['before']['device'] and value['inode'] != original['before']['inode']
    assert all(value[key] == after['after'][key] for key in value)
    assert digest(path) == original['sha256'] == after['sha256']
    assert preserved(path) == original['metadata'] == after['preservedMetadata']
    assert current(path) == value
    assert after['physicalBytesRecovered'] == original['before']['allocatedBytes'] - value['allocatedBytes'] > 0
    files.append(dict(path=path_string, sha256=original['sha256'], before=original['before'], after=value,
                      logicalBytesVerified=True, requiredMetadataVerified=True))
assert len(cleanup) == len(set(cleanup)) == 144
assert sum(row['after']['logicalBytes'] for row in files) == summary['logicalBytes'] == 698052574
assert sum(row['before']['allocatedBytes'] for row in files) == summary['oldAllocatedBytes'] == 698212352
assert sum(row['after']['allocatedBytes'] for row in files) == summary['newAllocatedBytes'] == 275595264
assert summary['physicalBytesRecovered'] == 422617088
policy_path = REPO / 'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json'
policy = json.loads(pinned(policy_path, '98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0').read_bytes())
for row in policy['expectedNativeSourceManifest']:
    pinned(REPO / row['path'], row['sha256'])
assert len(policy['expectedNativeSourceManifest']) == 306
pinned(SUMMARY, SUMMARY_SHA)
pinned(journal, JOURNAL_SHA)
result = dict(schemaVersion=1, state='INDEPENDENT_PUBLIC_ENGINE_COMPRESSION_POSTVERIFICATION_PASSED',
              verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              summaryPath=str(SUMMARY), summarySha256=SUMMARY_SHA, journalSha256=JOURNAL_SHA,
              executedPreimageSha256=summary['frozenInputsSha256'], executedPreimageMatchesDryRunBytes=True,
              filesVerified=72, files=files, unchangedWitnesses=[dict(path=k,sha256=v) for k,v in witnesses.items()],
              unchangedWitnessCount=38, compactorIndexSha256=digest(compactor_index),
              currentNativeSourceInputsUnchanged=306, recordedCleanupPathsAbsent=cleanup,
              orderedRollbackLinkReleaseEvents=72, logicalBytes=698052574,
              summedAllocatedBytesBefore=698212352, summedAllocatedBytesAfter=275595264,
              summedFileAllocationReductionBytes=422617088,
              recordedGlobalFreeBeforeBytes=summary['diskFreeBeforeBytes'], recordedGlobalFreeAfterBytes=summary['diskFreeAfterBytes'],
              recordedGlobalFreeDeltaBytes=summary['diskFreeAfterBytes']-summary['diskFreeBeforeBytes'],
              independentCurrentFreeBytes=shutil.disk_usage('/tmp/starling-node-compat').free,
              globalFreeDeltaIsNonexclusive=True, uniqueExtentsMeasured=False,
              requiredMetadataExcludes=['read-atime','ctime','birthtime','new filesystem com.apple.decmpfs compression metadata'],
              compactorRerun=False, compressionOrMutationExecutedByVerifier=False,
              compilerBuildLinkBinaryOrGuestExecuted=False,
              compatibilityOrRuntimePerformanceResult=False)
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key:result[key] for key in ['state','filesVerified','unchangedWitnessCount','summedFileAllocationReductionBytes','independentCurrentFreeBytes']}))
