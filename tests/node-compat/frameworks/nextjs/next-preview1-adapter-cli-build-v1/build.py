"""Delegated Root native-CLI-only build. No adapter/engine/guest invocation."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,shutil,signal,stat,sys,threading,time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
OLD_SOURCE=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source')
OLD_BUILD=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build')
SOURCE=Path('/private/tmp/starling-node-compat/next-preview1-adapter-v1-tools-source')
WORK=Path('/private/tmp/starling-node-compat/next-preview1-adapter-v1-tools-build')
OUTER=Path(str(WORK)+'-root-monitor')
RUST=Path('/Users/dan/.rustup/toolchains/1.96.1-aarch64-apple-darwin')
CANDIDATE=HERE.parent/'next-preview1-adapter-candidate-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
PYTHON=Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
START_FREE=2*1024**3
STOP_FREE=800*1024**2

def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024**2),b''):h.update(block)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)

def identity(path):
    s=Path(path).lstat()
    return dict(mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,
                bytes=s.st_size,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)

def checked(row):
    p=Path(row['path']);assert p.is_absolute() and '..' not in p.parts
    assert all(not q.is_symlink() for q in (p,*p.parents)),p
    before=identity(p);assert stat.S_ISREG(p.lstat().st_mode)
    assert descriptor(p)=={k:row[k]for k in ('path','sha256','bytes')},p
    assert identity(p)==before,p
    return p

def write(path,value):
    raw=(json.dumps(value,indent=2)+'\n').encode() if not isinstance(value,bytes) else value
    path=Path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:
        os.fchmod(stream.fileno(),0o600);stream.write(raw);stream.flush();os.fsync(stream.fileno())

def tree(root):
    root=Path(root);assert root.is_dir() and not root.is_symlink()
    files=[];dirs=[]
    for base,names,leaves in os.walk(root,followlinks=False):
        for n in sorted(names):
            p=Path(base)/n;assert p.is_dir() and not p.is_symlink();dirs.append(str(p.relative_to(root)))
        for n in sorted(leaves):
            p=Path(base)/n;assert p.is_file() and not p.is_symlink();files.append(str(p.relative_to(root)))
    return dict(root=str(root),files=sorted(files),directories=sorted(dirs))

def capture(row,rows):
    p=checked(row);key=str(p)
    rows[key]=dict(descriptor={k:row[k]for k in ('path','sha256','bytes')},identity=identity(p))

def capture_tree(root,rows,trees):
    snapshot=tree(root);trees.append(snapshot)
    for name in snapshot['files']:capture(descriptor(Path(root)/name),rows)
    return snapshot

def recheck(rows,trees):
    for snapshot in trees:assert tree(snapshot['root'])==snapshot,snapshot['root']
    for path,row in rows.items():checked(row['descriptor']);assert identity(path)==row['identity'],path
    return dict(files=len(rows),trees=len(trees),unchanged=True)

def authenticate():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    a=json.loads((HERE/'authority.json').read_text())
    assert a['nativeCliBuildAllowed'] is True and all(a[k] is False for k in ('adapterInvocationAllowed','engineActionsAllowed','guestActionsAllowed','networkAllowed'))
    for row in a['pinned'].values():checked(row)
    assert descriptor(CANDIDATE/'index.json')['sha256']=='c6d7e097508dbef6cbdb2be2822eb81059714d5a1677f14c891520fd5d452311'
    index=json.loads((CANDIDATE/'index.json').read_text())
    assert {r['path']for r in index['files']}=={str(p.relative_to(CANDIDATE))for p in CANDIDATE.rglob('*')if p.is_file() and p!=CANDIDATE/'index.json'}
    for r in index['files']:checked(dict(r,path=str(CANDIDATE/r['path'])))
    assert a['outerDeadlineSeconds']==2400 and a['compilerDeadlineSeconds']==2200
    return a

def monitor_module():
    spec=importlib.util.spec_from_file_location('original_owned_monitor',MONITOR)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def clean(t):
    return t['timeout'] is False and t['forcedCleanup'] is False and t['allObservedOwnedGroupsGone'] is True and t['parentOwnedGroupGone'] is True and all(t[k]==[] for k in ('signals','interruptedSignals','errors','remainingObservedPids'))

def worker(a):
    assert not SOURCE.exists() and not WORK.exists()
    assert shutil.disk_usage(WORK.parent).free>=START_FREE
    rows={};trees=[];terminal=None;error=None;final_error=None;artifact=None
    WORK.mkdir(mode=0o700);(WORK/'tmp').mkdir(mode=0o700)
    # Pinned baseline records bind current copies/vendor, not an inferred cache.
    stage=json.loads(checked(a['pinned']['oldStageReceipt']).read_text())
    source_before=capture_tree(OLD_SOURCE,rows,trees)
    assert len(source_before['files'])==271
    copies=[r for r in stage['copies']if r['destination']['path'].startswith(str(OLD_SOURCE)+'/')]
    assert len(copies)==271 and {str(Path(r['destination']['path']).relative_to(OLD_SOURCE))for r in copies}==set(source_before['files'])
    for r in copies:capture(r['destination'],rows)
    vendor=stage['stageInventory']['vendor'];assert vendor['root']==str(OLD_BUILD/'vendor') and vendor['links']==[]
    vendor_before=tree(vendor['root']);assert set(vendor_before['files'])=={r['relativePath']for r in vendor['files']}
    trees.append(vendor_before)
    for r in vendor['files']:capture(r,rows)
    assert len(vendor['files'])==7264
    rust_before=capture_tree(RUST,rows,trees);assert len(rust_before['files'])==338
    for row in a['pinned'].values():capture(row,rows)
    for r in json.loads((CANDIDATE/'index.json').read_text())['files']:capture(dict(r,path=str(CANDIDATE/r['path'])),rows)
    # Cargo must see no ancestor config outside the new private CARGO_HOME.
    for q in (SOURCE,*SOURCE.parents):
        for name in ('config','config.toml'):assert not (q/'.cargo'/name).exists() and not (q/'.cargo'/name).is_symlink()
    write(WORK/'input-before.json',dict(files=rows,trees=trees))
    SOURCE.mkdir(mode=0o700)
    for name in source_before['directories']:(SOURCE/name).mkdir(mode=0o700,parents=True,exist_ok=True)
    target_vendor=WORK/'vendor';target_vendor.mkdir(mode=0o700)
    for name in vendor_before['directories']:(target_vendor/name).mkdir(mode=0o700,parents=True,exist_ok=True)
    plan=json.loads((CANDIDATE/'adapter-plan.json').read_text());changes={r['path']:r['source']for r in plan['afterimages']}
    journal=[]
    for original,target_root,snapshot in [(OLD_SOURCE,SOURCE,source_before),(OLD_BUILD/'vendor',target_vendor,vendor_before)]:
        for name in snapshot['files']:
            src=original/name;selection=changes.get(name)if original==OLD_SOURCE else None
            selected=checked(selection) if selection else src
            target=target_root/name;write(target,selected.read_bytes());os.chmod(target,stat.S_IMODE(src.stat().st_mode))
            assert (target.stat().st_dev,target.stat().st_ino)!=(src.stat().st_dev,src.stat().st_ino)
            journal.append(dict(relativePath=name,role='source'if original==OLD_SOURCE else'vendor',original=descriptor(src),selected=descriptor(selected),destination=descriptor(target),identity=identity(target)))
    assert tree(SOURCE)['files']==source_before['files'] and tree(target_vendor)['files']==vendor_before['files']
    assert sum(r['role']=='source'and r['original']['sha256']!=r['destination']['sha256']for r in journal)==2
    # Whole new vendor checksum membership is checked, not merely Cargo's cache
    # hit behavior. All distribution paths remain below their private crate.
    for crate in target_vendor.iterdir():
        checksum=json.loads((crate/'.cargo-checksum.json').read_text());assert len(checksum['package'])==64
        actual={str(p.relative_to(crate))for p in crate.rglob('*')if p.is_file()and p.name!='.cargo-checksum.json'}
        assert actual==set(checksum['files'])
        for name,digest in checksum['files'].items():assert descriptor(crate/name)['sha256']==digest
    (WORK/'cargo-home').mkdir(mode=0o700)
    config='[source.crates-io]\nreplace-with = "private-vendor"\n[source.private-vendor]\ndirectory = '+json.dumps(str(target_vendor))+'\n[net]\noffline = true\n'
    write(WORK/'cargo-home/config.toml',config.encode())
    write(WORK/'copy-journal.json',dict(sourceFiles=271,changedSourceFiles=2,vendorFiles=7264,crates=121,copies=journal))
    capture_tree(SOURCE,rows,trees);capture_tree(target_vendor,rows,trees)
    capture(descriptor(WORK/'cargo-home/config.toml'),rows)
    write(WORK/'complete-input-before.json',dict(files=rows,trees=trees))
    before=recheck(rows,trees);assert shutil.disk_usage(WORK).free>=START_FREE
    ctx=json.loads(checked(a['pinned']['hostContext']).read_text())
    env={k:os.environ[k]for k in ('HOME','USER','LOGNAME','CODEX_HOME')if k in os.environ}
    env.update(PATH=str(RUST/'bin')+':'+str(Path(ctx['hostLinkerDriver']['path']).parent)+':/usr/bin:/bin:/usr/sbin:/sbin',
      RUSTC=str(RUST/'bin/rustc'),RUSTDOC=str(RUST/'bin/rustdoc'),RUSTUP_TOOLCHAIN='1.96.1-aarch64-apple-darwin',
      CARGO_HOME=str(WORK/'cargo-home'),CARGO_NET_OFFLINE='true',CARGO_INCREMENTAL='0',CARGO_BUILD_JOBS='1',
      CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER=ctx['hostLinkerDriver']['path'],SDKROOT=ctx['sdkRoot'],TMPDIR=str(WORK/'tmp'),LC_ALL='C',LANG='C')
    argv=[str(RUST/'bin/cargo'),'build','--locked','--offline','--release','-p','spidermonkey-embedding-splicer','--bin','splicer','--target','aarch64-apple-darwin','--jobs','1','--target-dir',str(WORK/'target')]
    command=WORK/'command';command.mkdir(mode=0o700)
    write(WORK/'requested-command.json',dict(argv=argv,cwd=str(SOURCE),environment=env,timeoutSeconds=2200))
    disk=dict(startFreeBytes=shutil.disk_usage(WORK).free,minimumObservedFreeBytes=shutil.disk_usage(WORK).free,stopFreeBytes=STOP_FREE,stopRequested=False,samples=0,errors=[])
    stop=threading.Event();signals=[]
    for number in (signal.SIGTERM,signal.SIGINT):signal.signal(number,lambda number,_frame:signals.append(number))
    def watch():
        while not stop.wait(0.5):
            try:
                free=shutil.disk_usage(WORK).free;disk['samples']+=1;disk['minimumObservedFreeBytes']=min(disk['minimumObservedFreeBytes'],free)
                if free<STOP_FREE:disk['stopRequested']=True;os.kill(os.getpid(),signal.SIGTERM);return
            except Exception as e:disk['errors'].append(repr(e));os.kill(os.getpid(),signal.SIGTERM);return
    watcher=threading.Thread(target=watch,daemon=True);watcher.start()
    try:
        terminal=monitor_module().monitor(argv,str(SOURCE),env,command,2200,descriptor(HERE/'authority.json'))
    except Exception as e:error=repr(e)
    finally:
        stop.set();watcher.join(timeout=5)
        disk['finalFreeBytes']=shutil.disk_usage(WORK).free
        try:after=recheck(rows,trees)
        except Exception as e:final_error=repr(e);after=dict(unchanged=False,error=final_error)
        binary=WORK/'target/aarch64-apple-darwin/release/splicer'
        if binary.is_file():artifact=descriptor(binary)
        passed=terminal is not None and terminal['rawExitCode']==0 and clean(terminal)and error is None and final_error is None and not disk['stopRequested']and not disk['errors']and not signals
        result=dict(schemaVersion=1,state='NEXT_SELECTIVE_ADAPTER_NATIVE_CLI_BUILD_PASSED_UNREVIEWED_V1'if passed else'NEXT_SELECTIVE_ADAPTER_NATIVE_CLI_BUILD_FAILURE_PRESERVED_V1',passed=passed,
          sourceIndex=descriptor(CANDIDATE/'index.json'),authority=descriptor(HERE/'authority.json'),commandTerminal=descriptor(command/'terminal.json')if(command/'terminal.json').exists()else None,
          artifact=artifact,compilerError=error,finalProtectionError=final_error,inputBefore=before,inputAfter=after,disk=disk,rootSignals=signals,
          copyJournal=descriptor(WORK/'copy-journal.json'),completeInputBefore=descriptor(WORK/'complete-input-before.json'),
          sourceFiles=271,sourceChanges=2,vendorFiles=7264,vendorCrates=121,rustDistributionFiles=338,
          nativeCliInvoked=False,adapterInvoked=False,wasmSplicerRebuilt=False,jsPackageRebuilt=False,engineOrGuestExecuted=False,
          hostSdkScope='Selected clang/ld/SDKSettings pinned; not blanket OS/header/library attestation')
        write(WORK/'result.json',result);print(json.dumps(dict(result=descriptor(WORK/'result.json'),passed=passed)),flush=True)
    return 0 if passed else 1

if __name__=='__main__':
    authority=authenticate()
    if sys.argv[1:]==['--worker']:raise SystemExit(worker(authority))
    assert sys.argv[1:]==[] and not OUTER.exists() and not SOURCE.exists() and not WORK.exists()
    OUTER.mkdir(mode=0o700)
    terminal=monitor_module().monitor([str(PYTHON),'-B','-I',str(Path(__file__).resolve()),'--worker'],str(HERE),
        {k:os.environ[k]for k in ('HOME','USER','LOGNAME','CODEX_HOME','PATH')if k in os.environ},OUTER,2400,descriptor(HERE/'authority.json'))
    result=dict(schemaVersion=1,rawExitCode=terminal['rawExitCode'],cleanOwnedGroups=clean(terminal),outerTerminal=descriptor(OUTER/'terminal.json'),
                actualWorkerResult=descriptor(WORK/'result.json')if(WORK/'result.json').exists()else None,adapterOrGuestExecuted=False)
    write(HERE/'root-result.json',result);print(json.dumps(result),flush=True)
    raise SystemExit(0 if clean(terminal) and terminal['rawExitCode']==0 else 1)
