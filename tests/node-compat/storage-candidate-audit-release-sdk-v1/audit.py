"""Read-only provenance/metadata/headroom audit of one Release guest SDK member."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import stat
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat/improved-build')
LIBRARY = BASE / 'spidermonkey-dist-release/libspidermonkey.a'
ARCHIVE = BASE / 'spidermonkey-release.tar.gz'
ARCHIVE_SHA = 'c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'
LIBRARY_SHA = '298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'
MEMBER = 'spidermonkey-dist-release/libspidermonkey.a'


def hash_stream(stream):
    value = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        value.update(chunk)
    return value.hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return hash_stream(stream)


assert LIBRARY.is_file() and not LIBRARY.is_symlink()
assert ARCHIVE.is_file() and not ARCHIVE.is_symlink()
before = LIBRARY.lstat()
archive_before = ARCHIVE.lstat()
assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_flags == 0
assert before.st_size == 538170426 and before.st_blocks * 512 == 538173440
assert sha(ARCHIVE) == ARCHIVE_SHA
assert sha(LIBRARY) == LIBRARY_SHA
members = []
with tarfile.open(ARCHIVE, mode='r|gz') as archive:
    for member in archive:
        if member.name != MEMBER:
            continue
        assert member.isreg() and member.size == before.st_size
        with archive.extractfile(member) as stream:
            assert hash_stream(stream) == LIBRARY_SHA
        members.append({'name': member.name, 'bytes': member.size, 'sha256': LIBRARY_SHA,
                        'type': 'regular tar member', 'archiveMode': member.mode})
assert len(members) == 1
attrs = {}
for name in subprocess.check_output(['/usr/bin/xattr', str(LIBRARY)], text=True).splitlines():
    raw = subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(LIBRARY)], text=True)
    attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
assert 'com.apple.decmpfs' not in attrs
acl = subprocess.check_output(['/bin/ls', '-led', str(LIBRARY)], text=True).splitlines()[1:]
after = LIBRARY.lstat()
archive_after = ARCHIVE.lstat()
for initial, current in [(before, after), (archive_before, archive_after)]:
    assert (initial.st_dev, initial.st_ino, initial.st_size, initial.st_mtime_ns,
            initial.st_flags, initial.st_nlink) == (
                current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns,
                current.st_flags, current.st_nlink)
lsof = subprocess.run(['/usr/sbin/lsof', '-nP', '--', str(LIBRARY), str(ARCHIVE)], capture_output=True, text=True)
assert lsof.returncode in [0, 1]
free = os.statvfs(BASE).f_bavail * os.statvfs(BASE).f_frsize
required = 2 * before.st_size + 64 * 1024**2
report = {'state': 'READ_ONLY_SINGLE_RELEASE_GUEST_SDK_MEMBER_AUDIT',
          'atUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'dataClass': 'current pinned Release SpiderMonkey guest SDK static library; not component output, engine or host runtime executable',
          'candidate': {'path': str(LIBRARY), 'sha256': LIBRARY_SHA,
                        'logicalBytes': before.st_size, 'allocatedBytes': before.st_blocks * 512,
                        'device': before.st_dev, 'inode': before.st_ino, 'mode': stat.S_IMODE(before.st_mode),
                        'uid': before.st_uid, 'gid': before.st_gid, 'mtimeNs': before.st_mtime_ns,
                        'flags': before.st_flags, 'nlink': before.st_nlink, 'xattrDigests': attrs, 'acl': acl},
          'archive': {'path': str(ARCHIVE), 'sha256': ARCHIVE_SHA, 'bytes': archive_before.st_size,
                      'member': members[0], 'streamedOnlyNoExtractionCopy': True,
                      'archiveBytesAndStableMetadataUnchanged': True},
          'candidateBytesEqualExactlyOnePinnedArchiveMember': True,
          'lsof': {'argv': ['/usr/sbin/lsof', '-nP', '--', str(LIBRARY), str(ARCHIVE)],
                   'status': lsof.returncode, 'stdout': lsof.stdout, 'stderr': lsof.stderr,
                   'noOpensObserved': lsof.returncode == 1 and not lsof.stdout and not lsof.stderr},
          'headroom': {'policy': 'free >= 2*logicalBytes + 64MiB before any separately authorized one-file copy',
                       'requiredBytes': required, 'freeBytesNonreservedAtObservation': free,
                       'metAtObservation': free >= required, 'largestOneFileTemporaryLogicalBytes': before.st_size,
                       'capacityReservationOrCompressionRecoveryClaim': False},
          'separateFromAdditional67AndEarlierComponentWhitelists': True,
          'metadataPreservationFeasibility': 'Regular flags0/nlink1 file with captured required metadata; a separate exact-one-file helper and dry run must preserve it and the original verified rollback inode.',
          'compressedSizeOrRecoveryMeasured': False,
          'compatibilityOrFutureLinkExecutionClaim': False,
          'compressionDeletionBuildGuestOrLibraryExecution': False,
          'nextGate': 'Separately reviewed SDK data-class helper and dry-run preimage; repeat lsof/headroom immediately before any authorized mutation. Archive must remain untouched.'}
with (HERE / 'results.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
with (HERE / 'index.json').open('x') as stream:
    json.dump({'state': 'READ_ONLY_RELEASE_GUEST_SDK_AUDIT_FROZEN',
               'files': [{'path': name, 'sha256': sha(HERE / name), 'bytes': (HERE / name).stat().st_size}
                         for name in ['audit.py', 'results.json']],
               'compressionDeletionBuildOrGuestExecuted': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'resultSha256': sha(HERE / 'results.json'), 'indexSha256': sha(HERE / 'index.json'),
                  'noOpensObserved': report['lsof']['noOpensObserved'], 'metadata': report['candidate'],
                  'headroom': report['headroom']}))
