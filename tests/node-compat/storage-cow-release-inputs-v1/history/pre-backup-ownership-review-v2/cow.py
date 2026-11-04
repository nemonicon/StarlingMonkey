#!/usr/bin/env python3
"""Exact two-pair macOS clonefile preparation; default is READ-ONLY dry run.

Only --apply can call clonefile or create an owned temporary/rollback link.
No ordinary data-copy fallback, source writes, compiler, SDK input or guest execution.
"""
import argparse
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

BASE = Path('/tmp/starling-node-compat')
REPO = Path(__file__).resolve().parents[3]
RECEIPTS = BASE/'storage-cow-release-inputs-v1'
HEADER = Path('/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk/usr/include/sys/clonefile.h')
CLONE_NOFOLLOW = 1
RESERVE_BYTES = 64*1024*1024
PAIRS = [
    {'name':'release-library',
     'source':BASE/'native-build/spidermonkey-dist-release/libspidermonkey.a',
     'target':BASE/'improved-build/spidermonkey-dist-release/libspidermonkey.a',
     'sha256':'298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc',
     'bytes':538170426},
    {'name':'release-archive',
     'source':BASE/'native-build/spidermonkey-release.tar.gz',
     'target':BASE/'improved-build/spidermonkey-release.tar.gz',
     'sha256':'c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b',
     'bytes':184568633},
]
PROOFS = [
    ('tests/node-compat/storage-candidate-audit-sdk-release-v1/results.json',
     '96c952bc3f58353cae079286512f39da402f74411cd1b0670025424b6dc77ff3'),
    ('tests/node-compat/storage-candidate-audit-release-sdk-v1/results.json',
     'e8cdad568c0faa3f83150181699269c6950d1862ddf40009876417cf18146d85'),
]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path):
    value = os.lstat(path)
    return {'device':value.st_dev,'inode':value.st_ino,'logicalBytes':value.st_size,
            'blocks':value.st_blocks,'allocatedBytes':value.st_blocks*512,
            'mode':stat.S_IMODE(value.st_mode),'uid':value.st_uid,'gid':value.st_gid,
            'mtimeNs':value.st_mtime_ns,'atimeNs':value.st_atime_ns,
            'ctimeNs':value.st_ctime_ns,'birthtimeSeconds':value.st_birthtime,
            'flags':value.st_flags,'nlink':value.st_nlink,
            'regular':stat.S_ISREG(value.st_mode),'symlink':stat.S_ISLNK(value.st_mode)}


def metadata(path):
    value = file_stat(path)
    attrs = {}
    # No compression exception: ALL application/filesystem xattrs must match.
    for name in subprocess.check_output(['/usr/bin/xattr',str(path)],text=True).splitlines():
        raw = subprocess.check_output(['/usr/bin/xattr','-p','-x',name,str(path)],text=True)
        attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    return {key:value[key] for key in ['logicalBytes','mode','uid','gid','mtimeNs']} | {
        'xattrDigests':attrs,
        'acl':subprocess.check_output(['/bin/ls','-led',str(path)],text=True).splitlines()[1:]}


def identity(value):
    return {key:value[key] for key in ['device','inode','logicalBytes','allocatedBytes',
            'mode','uid','gid','mtimeNs','flags','nlink','regular','symlink']}


def require_regular(path):
    assert path.is_absolute() and path.is_relative_to(BASE)
    cursor = path.parent
    while cursor != BASE:
        assert cursor.is_dir() and not cursor.is_symlink(),cursor
        cursor = cursor.parent
    value = file_stat(path)
    assert value['regular'] and not value['symlink'] and value['nlink'] == 1 and value['flags'] == 0,path


def capture(path,digest,size):
    require_regular(path)
    before = file_stat(path)
    value = {'path':str(path),'before':before,'metadata':metadata(path),'sha256':sha(path)}
    assert value['sha256'] == digest and before['logicalBytes'] == size,path
    assert identity(file_stat(path)) == identity(before),path
    return value


def check_preimage(value):
    path = Path(value['path'])
    require_regular(path)
    assert identity(file_stat(path)) == identity(value['before']),path
    assert metadata(path) == value['metadata'] and sha(path) == value['sha256'],path
    assert identity(file_stat(path)) == identity(value['before']),path


def freeze():
    proofs = []
    for name,digest in PROOFS:
        path = REPO/name
        assert path.is_file() and not path.is_symlink() and sha(path) == digest
        proofs.append({'path':str(path),'sha256':digest})
    # Installed header supplies the actual ctypes ABI, not the manpage's int wording.
    text = HEADER.read_text()
    assert 'int clonefile(const char *, const char *, uint32_t)' in text
    assert '#define CLONE_NOFOLLOW        0x0001' in text
    rows = []
    for pair in PAIRS:
        source = capture(pair['source'],pair['sha256'],pair['bytes'])
        target = capture(pair['target'],pair['sha256'],pair['bytes'])
        assert source['before']['device'] == target['before']['device']
        assert source['before']['inode'] != target['before']['inode']
        # Only timestamps may differ between the source attributes and required target.
        assert {k:v for k,v in source['metadata'].items() if k != 'mtimeNs'} == {k:v for k,v in target['metadata'].items() if k != 'mtimeNs'}
        rows.append({'name':pair['name'],'source':source,'target':target})
    return {'schemaVersion':1,'helperSha256':sha(__file__),'pairs':rows,'proofs':proofs,
            'header':{'path':str(HEADER),'sha256':sha(HEADER)},
            'cloneContract':{'function':'clonefile','argtypes':['c_char_p','c_char_p','c_uint32'],
                             'restype':'c_int','flags':CLONE_NOFOLLOW,'fallback':None}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--expected-inventory',type=Path)
    parser.add_argument('--root-build-quiescent',action='store_true')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        raise SystemExit('macOS-only exact-file storage helper')
    if args.apply and (not args.expected_inventory or not args.root_build_quiescent):
        raise SystemExit('Apply requires frozen --expected-inventory and explicit --root-build-quiescent acknowledgement')
    frozen = freeze()  # Read-only: no temporary path or clonefile binding/call.
    if args.apply:
        expected = json.loads(args.expected_inventory.read_text())
        assert expected['helperSha256'] == frozen['helperSha256']
        assert expected['proofs'] == frozen['proofs'] and expected['header'] == frozen['header']
        assert expected['cloneContract'] == frozen['cloneContract']
        assert len(expected['pairs']) == len(frozen['pairs']) == 2
        for old,new in zip(expected['pairs'],frozen['pairs']):
            assert old['name'] == new['name']
            for key in ['source','target']:
                assert old[key]['path'] == new[key]['path'] and old[key]['sha256'] == new[key]['sha256']
                assert old[key]['metadata'] == new[key]['metadata']
                assert identity(old[key]['before']) == identity(new[key]['before'])
    RECEIPTS.mkdir(exist_ok=True)
    run = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    snapshot = RECEIPTS/(run+'.frozen-inputs.json')
    with snapshot.open('x') as stream:
        json.dump(frozen,stream,indent=2,sort_keys=True)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())
    journal_path = RECEIPTS/(run+'.journal.jsonl')
    journal = journal_path.open('x')

    def record(value):
        try:
            journal.write(json.dumps({'timestampUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**value},sort_keys=True)+'\n')
            journal.flush();os.fsync(journal.fileno())
            return True
        except OSError as error:
            # Preserve in-memory status even if later failure logging also fails.
            summary['evidenceErrors'].append({'stage':'journal-write','event':value.get('event'),'error':str(error)})
            return False

    def require_record(value):
        if not record(value):
            raise RuntimeError('Required journal write failed; stop before further adoption')

    summary = {'schemaVersion':1,'state':'DRY_RUN_NO_CLONEFILE_CALL' if not args.apply else 'APPLY_IN_PROGRESS',
               'apply':args.apply,'run':run,'helperSha256':sha(__file__),
               'frozenInputs':str(snapshot),'frozenInputsSha256':sha(snapshot),
               'expectedInventory':str(args.expected_inventory) if args.apply else None,
               'rootBuildQuiescenceAcknowledged':args.root_build_quiescent,
               'journal':str(journal_path),'clonefileCalls':0,'successfulClonefileCalls':0,
               'adoptedTargets':0,'pairs':[],'failures':[],'evidenceErrors':[],
               'freeBytesBeforeNonreserved':shutil.disk_usage(BASE).free,
               'uniqueExtentRecoveryProved':False,'exclusivePhysicalBytesRecovered':None,
               'compilerGuestOrSdkInputExecution':False}
    if not record({'event':'start',**summary}):
        summary['failures'].append({'stage':'start-journal','error':'Cannot authenticate a mutation run'})
    if not args.apply:
        for pair in frozen['pairs']:
            record({'event':'inventory','name':pair['name'],'source':pair['source'],'target':pair['target']})
    else:
        selected = [str(Path(row[key]['path'])) for row in frozen['pairs'] for key in ['source','target']]
        lsof = subprocess.run(['/usr/sbin/lsof','-nP','--',*selected],capture_output=True,text=True)
        if not record({'event':'lsof-preapply','returncode':lsof.returncode,'stdout':lsof.stdout,'stderr':lsof.stderr}):
            summary['failures'].append({'stage':'preapply-journal','error':'Cannot record quiescence'})
        if not (lsof.returncode == 1 and not lsof.stdout and not lsof.stderr):
            summary['failures'].append({'stage':'preapply-quiescence','error':'Selected inputs open or lsof failed'})
        for pair in frozen['pairs']:
            if summary['failures']:
                break
            source,target = Path(pair['source']['path']),Path(pair['target']['path'])
            temporary = backup = None
            temporary_owned = replaced = restored = False
            try:
                check_preimage(pair['source']);check_preimage(pair['target'])
                free = shutil.disk_usage(BASE).free
                require_record({'event':'headroom','name':pair['name'],'freeBytes':free,'requiredBytes':RESERVE_BYTES})
                if free < RESERVE_BYTES:
                    raise RuntimeError('Less than64MiB operational metadata headroom; no clone attempted')
                # Prepare symbol/ABI only in the explicit apply branch.
                system = ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
                clonefile = system.clonefile
                clonefile.argtypes = [ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32]
                clonefile.restype = ctypes.c_int
                fd,name = tempfile.mkstemp(prefix='.storage-cow-',suffix='.tmp',dir=target.parent)
                os.close(fd);os.unlink(name)  # Only our newly created empty reservation.
                temporary = Path(name)
                assert not os.path.lexists(temporary)
                require_record({'event':'clone-prepared','name':pair['name'],'source':str(source),'target':str(target),'temporary':str(temporary)})
                ctypes.set_errno(0)
                summary['clonefileCalls'] += 1
                result = clonefile(os.fsencode(source),os.fsencode(temporary),ctypes.c_uint32(CLONE_NOFOLLOW))
                error_number = ctypes.get_errno()
                if result == 0:
                    # Ownership/accounting must precede fallible journal I/O.
                    temporary_owned = True
                    summary['successfulClonefileCalls'] += 1
                require_record({'event':'clonefile-result','name':pair['name'],'returncode':result,'errno':error_number,'flags':CLONE_NOFOLLOW})
                if result != 0:
                    raise OSError(error_number,os.strerror(error_number))
                clone = file_stat(temporary)
                assert clone['regular'] and not clone['symlink'] and clone['nlink'] == 1 and clone['flags'] == 0
                assert clone['device'] == pair['source']['before']['device']
                assert clone['inode'] not in [pair['source']['before']['inode'],pair['target']['before']['inode']]
                # Metadata changes ONLY on our owned temporary. Source files are never written.
                os.utime(temporary,ns=(pair['target']['before']['atimeNs'],pair['target']['before']['mtimeNs']))
                assert metadata(temporary) == pair['target']['metadata'] and sha(temporary) == pair['target']['sha256']
                os.utime(temporary,ns=(pair['target']['before']['atimeNs'],pair['target']['before']['mtimeNs']))
                with temporary.open('rb') as stream:
                    os.fsync(stream.fileno())
                check_preimage(pair['source']);check_preimage(pair['target'])
                backup = target.parent/('.storage-cow-original-'+uuid.uuid4().hex+'.rollback')
                os.link(target,backup,follow_symlinks=False)
                assert file_stat(backup)['inode'] == pair['target']['before']['inode']
                assert file_stat(target)['nlink'] == 2
                require_record({'event':'prepared','name':pair['name'],'source':str(source),'target':str(target),
                        'temporary':str(temporary),'rollback':str(backup),'clone':file_stat(temporary),
                        'targetBefore':pair['target']['before'],'sha256':pair['target']['sha256']})
                os.replace(temporary,target)
                replaced = True;temporary = None;temporary_owned = False
                after = file_stat(target)
                assert after['regular'] and not after['symlink'] and after['nlink'] == 1 and after['flags'] == 0
                assert after['inode'] == clone['inode'] and after['inode'] != pair['source']['before']['inode']
                assert metadata(target) == pair['target']['metadata'] and sha(target) == pair['target']['sha256']
                check_preimage(pair['source'])
                require_record({'event':'after','name':pair['name'],'target':str(target),'after':file_stat(target),
                        'sha256':pair['target']['sha256'],'requiredMetadataVerified':True,'sourcePreimageUnchanged':True})
                adoption = {'name':pair['name'],'target':str(target),'sha256':pair['target']['sha256'],
                            'before':pair['target']['before'],'after':file_stat(target),'directClonefileReturn':0}
                backup.unlink();backup = None  # Only our old-target rollback link, after verified adoption.
                # This target is now irreversibly adopted: count it before logging.
                summary['adoptedTargets'] += 1
                summary['pairs'].append(adoption)
                require_record({'event':'rollback-link-released','name':pair['name'],'target':str(target)})
            except Exception as error:
                failure = {'name':pair['name'],'error':str(error),'replaced':replaced,'originalRestored':False}
                if replaced and backup is not None:
                    try:
                        os.replace(backup,target);backup = None
                        assert file_stat(target)['inode'] == pair['target']['before']['inode']
                        assert metadata(target) == pair['target']['metadata'] and sha(target) == pair['target']['sha256']
                        restored = True;failure['originalRestored'] = True
                        record({'event':'rolled-back','name':pair['name'],'target':str(target)})
                    except Exception as restore_error:
                        failure['restorationError'] = str(restore_error)
                        failure['retainedRollback'] = str(backup) if backup is not None else None
                summary['failures'].append(failure)
                record({'event':'failure',**failure})
            finally:
                if backup is not None and not replaced:
                    # Failed before adoption: remove only our extra link if the old target still owns that inode.
                    if file_stat(target)['inode'] == pair['target']['before']['inode']:
                        backup.unlink();backup = None
                if temporary_owned and temporary is not None and os.path.lexists(temporary):
                    temporary.unlink()  # Only a clone known to have been created successfully by this call.
                # On a failed syscall, never unlink an unexpected destination: ownership is unproved.
    source_checks = []
    for pair in frozen['pairs']:
        try:
            check_preimage(pair['source'])
            source_checks.append({'name':pair['name'],'unchanged':True})
        except Exception as error:
            source_checks.append({'name':pair['name'],'unchanged':False,'error':str(error)})
            summary['failures'].append({'stage':'source-postcheck','name':pair['name'],'error':str(error)})
    summary['sourcePostchecks'] = source_checks
    summary['freeBytesAfterNonreserved'] = shutil.disk_usage(BASE).free
    summary['nonexclusiveFreeDeltaBytes'] = summary['freeBytesAfterNonreserved']-summary['freeBytesBeforeNonreserved']

    def update_status():
        summary['completed'] = not summary['failures'] and not summary['evidenceErrors']
        summary['state'] = ('APPLY_VERIFIED' if summary['completed'] else 'APPLY_FAILED_STOPPED') if args.apply else ('DRY_RUN_NO_CLONEFILE_CALL' if summary['completed'] else 'DRY_RUN_FAILED_NO_CLONEFILE_CALL')

    update_status()
    record({'event':'finish',**summary})
    try:
        journal.close()
    except OSError as error:
        summary['evidenceErrors'].append({'stage':'journal-close','error':str(error)})
    try:
        summary['journalSha256'] = sha(journal_path)
    except OSError as error:
        summary['evidenceErrors'].append({'stage':'journal-hash','error':str(error)})
    update_status()
    summary_path = RECEIPTS/(run+'.summary.json')
    try:
        with summary_path.open('x') as stream:
            json.dump(summary,stream,indent=2,sort_keys=True);stream.write('\n')
            stream.flush();os.fsync(stream.fileno())
    except OSError as error:
        summary['evidenceErrors'].append({'stage':'summary-write','error':str(error)})
        update_status()
    # Like the reviewed native launcher: final storage failure keeps full status
    # on stdout, including verified adoptions. No crash/ENOSPC guarantee follows.
    print(json.dumps({'summary':str(summary_path),**summary},indent=2),flush=True)
    if not summary['completed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
