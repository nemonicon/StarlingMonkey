#!/usr/bin/env python3
"""Lossless, journalled macOS filesystem compression of 72 exact accepted public ordinary Release embedding engine outputs.

This changes filesystem representation only. It never edits WebAssembly bytes.
Run without --apply to inventory the deliberately narrow allowlist.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid


BASE = Path('/tmp/starling-node-compat')
REPO = Path(__file__).resolve().parents[3]
AUDIT_PATH = REPO / 'tests/node-compat/storage-candidate-audit-public-engines-v1/results.json'
AUDIT_SHA256 = '1dc393a9ba5658f37b69857b6d324251129e2e871f9172856e501c2578d76206'
AUDIT_INDEX_PATH = AUDIT_PATH.with_name('index.json')
AUDIT_INDEX_SHA256 = 'b6bee8327b7ef6428cf9fe324d5267bd94bbbafae42ea64795242407e77b1d6d'
assert hashlib.sha256(AUDIT_PATH.read_bytes()).hexdigest() == AUDIT_SHA256
assert hashlib.sha256(AUDIT_INDEX_PATH.read_bytes()).hexdigest() == AUDIT_INDEX_SHA256
AUDIT = json.loads(AUDIT_PATH.read_text())
assert AUDIT['eligiblePaths'] == AUDIT['uniqueInodes'] == 72
assert len(AUDIT['rows']) == len({row['path'] for row in AUDIT['rows']}) == 72
ROOTS = {'parent-' + str(i): Path(name) for i,name in enumerate(sorted({str(Path(row['path']).parent) for row in AUDIT['rows']}))}
AUDITED = {row['path']:row for row in AUDIT['rows']}
RECEIPTS = BASE / 'storage-compaction-public-engines-v1'
EXPECTED_ELIGIBLE_COUNT = 72
HEADROOM_RESERVE = 64 * 1024 * 1024
COMPRESSED = 32  # UF_COMPRESSED on this macOS host.


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path):
    value = os.lstat(path)
    return {
        'device': value.st_dev, 'inode': value.st_ino,
        'logicalBytes': value.st_size, 'blocks': value.st_blocks,
        'allocatedBytes': value.st_blocks * 512,
        'mode': stat.S_IMODE(value.st_mode), 'uid': value.st_uid, 'gid': value.st_gid,
        'mtimeNs': value.st_mtime_ns, 'atimeNs': value.st_atime_ns,
        'ctimeNs': value.st_ctime_ns, 'birthtimeSeconds': value.st_birthtime,
        'flags': value.st_flags, 'nlink': value.st_nlink,
        'regular': stat.S_ISREG(value.st_mode), 'symlink': stat.S_ISLNK(value.st_mode),
    }


def xattrs(path):
    names = subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines()
    result = {}
    for name in sorted(names):
        # ditto's compression implementation may store this filesystem metadata.
        if name == 'com.apple.decmpfs':
            continue
        value = subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(path)])
        result[name] = hashlib.sha256(bytes.fromhex(value.decode())).hexdigest()
    return result


def acl(path):
    listing = subprocess.check_output(['/bin/ls', '-led', str(path)], text=True)
    # First line includes the path/inode metadata. Remaining lines describe ACLs.
    return listing.splitlines()[1:]


def preserved_metadata(path):
    value = file_stat(path)
    return {key: value[key] for key in ('logicalBytes', 'mode', 'uid', 'gid', 'mtimeNs')} | {
        'xattrDigests': xattrs(path), 'acl': acl(path),
    }


def stable_identity(value):
    return {key: value[key] for key in (
        'device', 'inode', 'logicalBytes', 'mode', 'uid', 'gid', 'mtimeNs',
        'flags', 'nlink', 'regular', 'symlink',
    )}


def verify_report_closure():
    # Terminal accepted public ordinary Release only; no engine execution.
    checked = set()
    def pinned(path,digest):
        path = Path(path)
        assert path.is_file() and not path.is_symlink()
        assert sha256(path) == digest, path
        checked.add((str(path),digest))
    for row in json.loads(AUDIT_INDEX_PATH.read_text())['files']:
        pinned(AUDIT_PATH.parent / row['path'],row['sha256'])
    milestones = {}
    for row in AUDIT['acceptedMilestoneWitnesses']:
        pinned(row['path'],row['sha256'])
        milestones[row['path']] = json.loads(Path(row['path']).read_text())
    sidecars = {}
    for row in AUDIT['terminalSidecars']:
        pinned(row['path'],row['sha256'])
        metadata = json.loads(Path(row['path']).read_text())
        assert metadata['engineSha256'] == row['engineSha256']
        assert metadata['gcStress'] is False and metadata['oomTesting'] is False
        assert metadata.get('diagnosticOnly',False) is False
        assert 'internalTickDiagnosticPolicy' not in metadata
        options = metadata.get('observedCMakeOptions',metadata.get('requestedCMakeOptions',{}))
        assert options['CMAKE_BUILD_TYPE'] == 'Release'
        assert metadata.get('debuggerEnabled',False) is False
        for ref in row['milestoneReferences']:
            value = milestones[ref['path']]
            for part in ref['key'].split('.'):
                value = value[part]
            assert value == row['engineSha256']
        sidecars[row['path']] = metadata
    assert len(sidecars) == 22
    for row in AUDIT['rows']:
        assert any(d['expectedSha256'] == row['sha256'] for d in row['derivations'])
        for derivation in row['derivations']:
            assert sidecars[derivation['sidecar']]['engineSha256'] == derivation['expectedSha256']
    return len(checked)


def candidates(roots):
    # Exact audit whitelist; never walk, glob or rediscover build outputs.
    assert set(roots) == set(ROOTS.values())
    for row in sorted(AUDIT['rows'],key=lambda row:row['path']):
        path = Path(row['path'])
        assert path.is_absolute() and path.is_relative_to(BASE) and path.parent in roots
        value = file_stat(path)
        reason = None
        if not path.name.endswith('.wasm'):
            reason = 'not-an-explicit-engine-wasm-file'
        elif any(token in str(path).lower() for token in ('debug','oom','private','candidate','probe')):
            reason = 'excluded-debug-oom-private-candidate-or-probe-path'
        elif value['symlink'] or not value['regular']:
            reason = 'not-a-regular-nonsymlink-file'
        elif value['nlink'] != 1:
            reason = 'multiple-hardlinks'
        elif value['flags'] & COMPRESSED:
            reason = 'already-compressed'
        elif value['flags'] != 0:
            reason = 'other-file-flags-not-modified'
        yield path,reason


def match_audited_preimage(path,value):
    prior = AUDITED[str(path)]
    for key in ['device','inode','logicalBytes','allocatedBytes','mode','uid','gid','mtimeNs','flags','nlink']:
        assert value['before'][key] == prior[key],(str(path),key)
    assert value['sha256'] == prior['sha256'],path
    expected = {key:prior[key] for key in ['logicalBytes','mode','uid','gid','mtimeNs']}
    expected.update(xattrDigests=prior['xattrs'],acl=prior['aclLines'])
    assert value['metadata'] == expected,path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--root', choices=tuple(ROOTS), action='append')
    parser.add_argument('--expected-inventory', type=Path, help='Required frozen dry-run preimage when applying')
    args = parser.parse_args()
    if args.apply and (args.root or not args.expected_inventory):
        raise SystemExit('Apply requires all exact roots and --expected-inventory from the frozen dry run.')
    if sys.platform != 'darwin':
        raise SystemExit('This helper requires macOS transparent HFS/APFS compression.')
    if args.root:
        raise SystemExit('This finite whitelist has no subset mode.')
    roots = list(ROOTS.values())
    closure_count = verify_report_closure()
    RECEIPTS.mkdir(exist_ok=True)
    run = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    journal_path = RECEIPTS / f'{run}.journal.jsonl'
    summary_path = RECEIPTS / f'{run}.summary.json'
    journal = open(journal_path, 'x')

    def record(value):
        value = {'timestampUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **value}
        journal.write(json.dumps(value, sort_keys=True) + '\n')
        journal.flush()
        os.fsync(journal.fileno())

    summary = {
        'run': run, 'apply': args.apply, 'roots': [str(path) for path in roots],
        'script': str(Path(__file__).resolve()), 'scriptSha256': sha256(__file__),
        'ditto': '/usr/bin/ditto', 'dittoSha256': sha256('/usr/bin/ditto'),
        'command': ['/usr/bin/ditto', '--hfsCompression', '--noclone', 'SOURCE', 'FRESH_SAME_DIRECTORY_TEMP'],
        'platform': platform.platform(), 'python': sys.version,
        'journal': str(journal_path), 'diskFreeBeforeBytes': shutil.disk_usage(BASE).free,
        'acceptedPublicEngineAudit':str(AUDIT_PATH), 'acceptedPublicEngineAuditSha256':AUDIT_SHA256,
        'acceptedPublicEngineAuditIndexSha256':AUDIT_INDEX_SHA256, 'reportClosureWitnessesVerified':closure_count,
        'dataClass':'exact accepted public ordinary Release engine outputs; no binary execution or compatibility promotion',
        'headroomPolicy':'Before each copy: free >= 2*logicalBytes + 64MiB; not a hidden-allocation guarantee',
        'compressedFiles': 0, 'eligibleFiles': 0, 'skippedEntries': 0,
        'logicalBytes': 0, 'oldAllocatedBytes': 0, 'newAllocatedBytes': 0,
        'physicalBytesRecovered': 0, 'failures': [],
    }
    record({'event': 'start', **summary})
    # Freeze the complete path/preimage inventory before any replacement. Files
    # appearing later are never assumed complete and cannot enter this pass.
    assert all(root.is_dir() and not root.is_symlink() for root in roots)
    frozen_entries = list(candidates(roots))
    frozen = {}
    for path, reason in frozen_entries:
        if reason is None:
            value = {'path': str(path), 'before': file_stat(path),
                     'metadata': preserved_metadata(path), 'sha256': sha256(path)}
            assert stable_identity(file_stat(path)) == stable_identity(value['before'])
            match_audited_preimage(path,value)
            frozen[str(path)] = value
    assert len(frozen) == EXPECTED_ELIGIBLE_COUNT, len(frozen)
    if args.apply:
        expected = json.loads(args.expected_inventory.read_text())
        assert expected['roots'] == [str(root) for root in roots]
        expected_files = {item['path']: item for item in expected['files']}
        assert set(expected_files) == set(frozen)
        for path, value in frozen.items():
            prior = expected_files[path]
            assert value['sha256'] == prior['sha256']
            assert value['metadata'] == prior['metadata']
            assert stable_identity(value['before']) == stable_identity(prior['before'])
        summary['expectedInventory'] = str(args.expected_inventory.resolve())
        summary['expectedInventorySha256'] = sha256(args.expected_inventory)
    snapshot = RECEIPTS / f'{run}.frozen-inputs.json'
    with open(snapshot, 'x') as stream:
        json.dump({'roots': [str(root) for root in roots], 'files': list(frozen.values()),
                   'excludedEntries': [{'path': str(path), 'reason': reason}
                                       for path, reason in frozen_entries if reason]},
                  stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    summary['frozenInputs'] = str(snapshot)
    summary['frozenInputsSha256'] = sha256(snapshot)
    record({'event': 'frozen-inventory', 'path': str(snapshot),
            'sha256': summary['frozenInputsSha256'], 'files': len(frozen)})
    for path, reason in frozen_entries:
        if reason:
            summary['skippedEntries'] += 1
            record({'event': 'skip', 'path': str(path), 'reason': reason})
            continue
        summary['eligibleFiles'] += 1
        before = frozen[str(path)]['before']
        if not args.apply:
            record({'event': 'inventory', 'path': str(path), 'before': before})
            continue
        temporary = None
        backup = None
        backup_owned = False
        replaced = False
        restored = False
        try:
            original_metadata = frozen[str(path)]['metadata']
            digest = frozen[str(path)]['sha256']
            if preserved_metadata(path) != original_metadata or sha256(path) != digest:
                raise RuntimeError('source no longer matches its frozen completed preimage')
            if stable_identity(file_stat(path)) != stable_identity(before):
                raise RuntimeError('source changed while preparing its digest')
            record({'event': 'before', 'path': str(path), 'sha256': digest,
                    'before': before, 'preservedMetadata': original_metadata})
            free_bytes = shutil.disk_usage(BASE).free
            required_bytes = 2 * before['logicalBytes'] + HEADROOM_RESERVE
            record({'event':'headroom-check','path':str(path),'freeBytes':free_bytes,'requiredBytes':required_bytes})
            if free_bytes < required_bytes:
                raise RuntimeError('insufficient per-file headroom before creating a temporary copy')
            fd, temporary_name = tempfile.mkstemp(prefix='.storage-compression-', suffix='.wasm', dir=path.parent)
            os.close(fd)
            os.unlink(temporary_name)  # Only this newly created empty reservation.
            temporary = Path(temporary_name)
            command = ['/usr/bin/ditto', '--hfsCompression', '--noclone', str(path), str(temporary)]
            copy_result = subprocess.run(command, capture_output=True)
            record({'event': 'ditto-copy-result', 'path': str(path),
                    'returncode': copy_result.returncode,
                    'stdout': copy_result.stdout.decode('utf-8', errors='replace'),
                    'stderr': copy_result.stderr.decode('utf-8', errors='replace'),
                    'stdoutHex': copy_result.stdout.hex(), 'stderrHex': copy_result.stderr.hex()})
            if copy_result.returncode:
                raise subprocess.CalledProcessError(copy_result.returncode, command,
                                                    output=copy_result.stdout, stderr=copy_result.stderr)
            copied = file_stat(temporary)
            if not copied['regular'] or copied['symlink'] or copied['nlink'] != 1:
                raise RuntimeError('temporary output is not an independent regular file')
            if preserved_metadata(temporary) != original_metadata:
                raise RuntimeError('temporary output did not preserve required metadata')
            if copied['flags'] != (before['flags'] | COMPRESSED):
                raise RuntimeError('unexpected compression/file flags')
            if sha256(temporary) != digest:
                raise RuntimeError('temporary output logical bytes do not match')
            if copied['allocatedBytes'] >= before['allocatedBytes']:
                summary['skippedEntries'] += 1
                record({'event': 'skip', 'path': str(path), 'reason': 'no-physical-space-saving',
                        'sha256': digest, 'before': before, 'temporary': copied})
                continue
            # Hashing affects access times. Restore the original observed value.
            os.utime(temporary, ns=(before['atimeNs'], before['mtimeNs']))
            with open(temporary, 'rb') as stream:
                os.fsync(stream.fileno())
            if (stable_identity(file_stat(path)) != stable_identity(before) or
                    preserved_metadata(path) != original_metadata or sha256(path) != digest):
                raise RuntimeError('source changed before atomic replacement')
            # Retain the original inode under an owned temporary hardlink until
            # post-replacement verification. This adds no second data allocation.
            # Only sources initially having nlink==1 were admitted.
            backup = path.parent / ('.storage-original-' + uuid.uuid4().hex + '.rollback')
            os.link(path, backup, follow_symlinks=False)
            backup_owned = True
            assert file_stat(backup)['inode'] == before['inode']
            assert file_stat(path)['nlink'] == 2
            record({'event': 'prepared', 'path': str(path), 'temporaryPath': str(temporary),
                    'rollbackPath': str(backup), 'sha256': digest, 'before': before,
                    'temporary': file_stat(temporary)})
            os.replace(temporary, path)
            replaced = True
            temporary = None
            after = file_stat(path)
            if (sha256(path) != digest or preserved_metadata(path) != original_metadata or
                    not after['regular'] or after['symlink'] or after['nlink'] != 1 or
                    after['flags'] != (before['flags'] | COMPRESSED)):
                raise RuntimeError('post-replacement logical bytes or metadata mismatch: STOP')
            os.utime(path, ns=(before['atimeNs'], before['mtimeNs']))
            after = file_stat(path)
            recovered = before['allocatedBytes'] - after['allocatedBytes']
            if recovered <= 0:
                raise RuntimeError('post-replacement file allocation did not shrink: STOP')
            record({'event': 'after', 'path': str(path), 'sha256': digest,
                    'before': before, 'after': after, 'preservedMetadata': original_metadata,
                    'physicalBytesRecovered': recovered, 'logicalBytesVerified': True,
                    'requiredMetadataVerified': True})
            backup.unlink()  # Only our extra original-inode link after success.
            backup = None
            record({'event': 'rollback-link-released', 'path': str(path), 'sha256': digest})
            summary['compressedFiles'] += 1
            summary['logicalBytes'] += before['logicalBytes']
            summary['oldAllocatedBytes'] += before['allocatedBytes']
            summary['newAllocatedBytes'] += after['allocatedBytes']
            summary['physicalBytesRecovered'] += recovered
            print(json.dumps({'path': str(path), 'recoveredBytes': recovered,
                              'totalRecoveredBytes': summary['physicalBytesRecovered']}), flush=True)
        except Exception as error:
            if replaced and backup_owned and backup is not None:
                os.replace(backup, path)  # Restore the verified original inode.
                backup = None
                assert sha256(path) == digest
                assert preserved_metadata(path) == original_metadata
                assert file_stat(path)['flags'] == before['flags']
                restored = True
                record({'event': 'rolled-back', 'path': str(path), 'sha256': digest})
            failure = {'path': str(path), 'error': str(error), 'replaced': replaced,
                       'originalRestored': restored}
            summary['failures'].append(failure)
            record({'event': 'failure', **failure})
            if replaced:
                raise
            # Stop after the first unadopted failure; retain the journal and
            # publish a failed summary instead of repeating copy attempts.
            break
        finally:
            if backup_owned and backup is not None and backup.exists():
                # Unadopted case: the accepted source still owns this inode.
                assert not replaced
                backup.unlink()
            if temporary is not None and temporary.exists():
                temporary.unlink()  # Only an unadopted fresh copy, never an accepted artifact.
    summary['diskFreeAfterBytes'] = shutil.disk_usage(BASE).free
    summary['journalSha256BeforeSummary'] = sha256(journal_path)
    summary['completed'] = not summary['failures']
    summary['finishedUtc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record({'event': 'finish', **summary})
    journal.close()
    summary['journalSha256'] = sha256(journal_path)
    with open(summary_path, 'x') as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'summary': str(summary_path), **summary}, indent=2))


if __name__ == '__main__':
    main()
