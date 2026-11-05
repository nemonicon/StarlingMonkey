"""Dormant Root-only V2 clock-tool issuer and owned outer observer.

Derived from the preserved unissued V1 wrapper (de2c4e54, 8144 bytes).
Only explicit issue(peer) / run(configDescriptor) calls perform actions.
Source preparation does not call either API. No valid adapter pruning, engine,
application component, guest, runtime or admission authority is issued here.
"""
from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, os, re, shutil, stat, sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ORIGINAL = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-io-tools-build-v2-root-controller.py')
SOURCE = HERE/'clock-io-pruning-candidate-v1'
CONTROLLER = HERE/'clock-io-build-controller-candidate-v2'
SOURCE_PEER = HERE/'independent-clock-io-pruning-source-review-v1'
CONTROLLER_PEER = HERE/'independent-clock-io-build-controller-v2-source-review-v1'
MONITOR = REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
SRC = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source')
WORK = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build')
PACKAGE = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package')
EXTERNAL = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-v2-external-root')
OBSERVER = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-v2-root-observer')
AUTHORITY = HERE/'clock-io-tools-build-v2-root-authority.json'
CONFIG = HERE/'clock-io-tools-build-v2-root-config.json'
ALLOWED = {'stageAllowed','privateVendorAllowed','downloadThreeLockedArchivesAllowed',
           'rustBuildAndUnitTestsAllowed','jcoToolPackagingAllowed','prunerRefusalUnitTestAllowed'}
DENIED = {'adapterPublicationAllowed','adapterPruningAllowed','validAdapterPruningAllowed',
          'nativeEngineBuildAllowed','applicationComponentAllowed','applicationGuestAllowed',
          'keyOrCryptoAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim'}

def descriptor(value):
    assert type(value)is dict and set(value)=={'path','sha256','bytes'}
    assert type(value['path'])is str and Path(value['path']).is_absolute() and '..'not in Path(value['path']).parts and '\\'not in value['path'] and '\0'not in value['path']
    assert type(value['bytes'])is int and 0<=value['bytes']<=2**40
    assert type(value['sha256'])is str and re.fullmatch('[a-f0-9]{64}',value['sha256'])
    return dict(value)

def fingerprint(path):
    p=Path(path);assert p.is_absolute() and p.is_file() and not p.is_symlink()
    before=p.stat();real=str(p.resolve());h=hashlib.sha256()
    with p.open('rb')as stream:
        for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    after=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(before)==identity(after) and real==str(p.resolve())
    return dict(path=str(p),sha256=h.hexdigest(),bytes=after.st_size),identity(after),real

def row(path):return fingerprint(path)[0]

class Capture:
    def __init__(self):self.files={};self.families=[];self.modes=[];self.links=[];self.sdk=None
    def file(self,value):
        d=descriptor(value);actual,identity,real=fingerprint(d['path']);assert actual==d
        if d['path']in self.files:assert self.files[d['path']]==(d,identity,real)
        self.files[d['path']]=(d,identity,real);return d
    def read(self,value):
        d=self.file(value);assert d['bytes']<=32*1024*1024
        b=Path(d['path']).read_bytes();assert len(b)==d['bytes']and hashlib.sha256(b).hexdigest()==d['sha256']
        return json.loads(b)
    def family(self,index,sha=None):
        if sha is not None:assert index['sha256']==sha
        v=self.read(index);assert v['schemaVersion']==1 and type(v['files'])is list and 0<len(v['files'])<=4096
        base=Path(index['path']).parent;names={'index.json'};members=[index]
        for m in v['files']:
            n=m['path'];assert type(n)is str and n and not n.startswith('/') and '\\'not in n and '\0'not in n and all(x not in ['','.','..']for x in n.split('/')) and n not in names
            names.add(n);members.append(self.file(dict(m,path=str(base/n))))
        self.membership(base,names);self.families.append((base,names));return members
    @staticmethod
    def membership(base,names):
        assert base.is_dir()and not base.is_symlink()and not any(p.is_symlink()for p in base.rglob('*'))
        assert {p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
    def recheck(self):
        for d,identity,real in self.files.values():assert fingerprint(d['path'])==(d,identity,real)
        for base,names in self.families:self.membership(base,names)
        for p,mode in self.modes:assert stat.S_IMODE(p.stat().st_mode)==mode
        for p,target,resolved in self.links:assert p.is_symlink()and os.readlink(p)==target and str(p.resolve())==resolved
        if self.sdk is not None:
            p,real,target=self.sdk;assert str(p.resolve())==real and (os.readlink(p)if p.is_symlink()else None)==target

def save(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w')as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return row(path)

def peer_pair():
    return dict(index=dict(path=str(CONTROLLER_PEER/'index.json'),sha256='9027e0d4a45729d444fc29cd42b1bc0e18af3825f72c9e82a2d4ed01de174092',bytes=2067),
                result=dict(path=str(CONTROLLER_PEER/'results.json'),sha256='4bcf4a625713efef9103f5754fa5d2df90c6cfb2e540deb48c1b0ca2e1200c8b',bytes=6970))

def authenticate(peer):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert Path(__file__).resolve()==ORIGINAL and REPO==Path('/Users/dan/dev/StarlingMonkey')
    assert not any(os.environ.get(n)for n in ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])
    peer=copy.deepcopy(peer);assert peer==peer_pair()
    cap=Capture();cap.file(row(ORIGINAL))
    cap.file(dict(path=str(HERE/'clock-io-tools-build-v1-root-controller.py'),sha256='de2c4e54f8a0f1cab805ccfa4f4dbebbaea577a54e105b91d9966e451eb12b42',bytes=8144))
    source=row(SOURCE/'index.json');controller=row(CONTROLLER/'index.json')
    cap.family(controller,'41b22225b82628e901a8350f33d3150846e3e0e777aa23e561239e0985a50be9')
    fixed=cap.read(row(CONTROLLER/'references.json'))
    declared=cap.read(row(CONTROLLER/'source-inputs.json'))
    assert declared['schemaVersion']==1 and len(declared['files'])==len({r['path']for r in declared['files']})==5667
    for r in declared['files']:cap.file(r)
    for item in declared['families']:
        cap.family(item['index'])
        assert set(item['memberNames'])=={'index.json'}|{m['path']for m in cap.read(item['index'])['files']}
    cap.family(source,'55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f')
    source_peer=copy.deepcopy(fixed['sourceReviewData'])
    members=cap.family(source_peer['index'],'c9fa3ef3d25804b04c44747a45dbb547d4c6df39391e826e57a053474c735805')
    assert source_peer['result']in members
    proof=cap.read(source_peer['result'])
    assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1'
    assert proof['sourceIndexSha256']==source['sha256'] and proof['sourceOnly']is proof['sourceReviewPassed']is True and proof['ownerActionsInvoked']is False
    members=cap.family(peer['index']);assert peer['result']in members
    proof=cap.read(peer['result'])
    assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2'
    assert proof['controllerSourceIndexSha256']==controller['sha256']and proof['sourceIndexSha256']==source['sha256']
    assert proof['sourceOnly']is proof['sourceReviewPassed']is True
    for n in ['ownerActionsInvoked','hostActionsInvoked','buildActionsInvoked']:assert proof[n]is False
    reviewed_command_plan=cap.read(proof['independentModelResults'])['commandPlan']
    assert len(reviewed_command_plan)==8 and sum(c['timeoutSeconds']for c in reviewed_command_plan)==7200
    cap.family(fixed['monitorIndex'],'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    monitor_entry=cap.file(fixed['monitorEntry']);assert monitor_entry['path']==str(MONITOR/'monitor.py')
    context=cap.read(row(CONTROLLER/'host-context.json'))
    for n in ['sdkSettings','hostLinkerDriver','appleLinker','wasmLinker','xcodeVersionPlist','python']:cap.file(context[n])
    assert str(Path(sys.executable).resolve())==context['python']['path']
    settings=cap.read(context['sdkSettings']);assert settings['Version']==context['sdkVersion']=='27.0'and settings['CanonicalName']==context['sdkCanonicalName']
    cap.sdk=(Path(context['sdkRoot']),context['sdkRootResolution'],context['sdkRootLinkText'])
    cut=cap.read(fixed['sourceCut']);tools=cap.read(fixed['toolReferences'])
    for r in cut['baseline']['files']:cap.modes.append((Path(r['descriptor']['path']),r['mode']))
    for r in tools['jsToolchain']['files']:cap.modes.append((Path(r['descriptor']['path']),r['mode']))
    for r in declared['links']:cap.links.append((Path(r['path']),r['target'],r['resolved']['path']))
    for p in (SRC,*SRC.parents):
        for n in ['config','config.toml']:
            cfg=p/'.cargo'/n;assert not cfg.exists()and not cfg.is_symlink()
    cap.recheck()
    return dict(capture=cap,source=source,controller=controller,sourcePeer=source_peer,controllerPeer=peer,context=context,monitorEntry=monitor_entry,commandPlan=reviewed_command_plan)

def validate_authority(root,frame):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2'and root['phase']=='build-clock-io-tools'
    assert root['controllerIndex']==frame['controller']and root['controllerEntry']==row(CONTROLLER/'controller.py')
    assert root['sourceIndex']==frame['source']and root['sourceReview']==frame['sourcePeer']and root['controllerReview']==frame['controllerPeer']
    assert root['rootOuterController']==row(ORIGINAL)and root['rootOuterDeadlineSeconds']==root['deadlineSeconds']==7200
    assert root['sourceRoot']==str(SRC)and root['workRoot']==str(WORK)and root['packageRoot']==str(PACKAGE)
    assert root['externalRoot']==str(EXTERNAL)and root['rootObserverOutput']==str(OBSERVER)
    assert root['cargoJobs']==1 and root['expectedCommandCount']==8
    assert root['requiredStartFreeBytes']==2*1024**3 and root['minimumBoundaryFreeBytes']==800*1024**2
    assert root['diskFloorPolicy']=='BEFORE_AFTER_COMMANDS_AND_STAGE_BOUNDARIES_ONLY'and root['diskFloorMonitoredDuringCommand']is False
    assert root['declaredToolRootMetadataDestination']=='.toolchain-metadata'
    assert {k for k in root if k.endswith('Allowed')}=={k for k in ALLOWED|DENIED if k.endswith('Allowed')}
    for k in ALLOWED:assert root[k]is True
    for k in DENIED:assert root[k]is False

def fresh_roots():
    for p in [SRC,WORK,PACKAGE,EXTERNAL,OBSERVER]:assert not p.exists()and not p.is_symlink()

def issue(peer):
    frame=authenticate(peer);cap=frame['capture'];fresh_roots()
    assert not AUTHORITY.exists()and not AUTHORITY.is_symlink()and not CONFIG.exists()and not CONFIG.is_symlink()
    root=cap.read(row(CONTROLLER/'future-root-authority.template.json'))
    assert root['state']is root['phase']is root['controllerIndex']is None
    root.update(state='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2',phase='build-clock-io-tools',sourceIndex=frame['source'],controllerIndex=frame['controller'],
        controllerEntry=row(CONTROLLER/'controller.py'),sourceReview=frame['sourcePeer'],controllerReview=frame['controllerPeer'],
        rootOuterController=row(ORIGINAL),rootOuterDeadlineSeconds=7200,rootObserverOutput=str(OBSERVER),
        issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    for k in ALLOWED|DENIED:assert root[k]is None;root[k]=k in ALLOWED
    validate_authority(root,frame);cap.recheck()
    authority=save(AUTHORITY,root)
    config=cap.read(row(CONTROLLER/'future-config.template.json'))
    assert config==dict(schemaVersion=1,state=None,controllerIndex=None,rootAuthority=None)
    config.update(state='CLOCK_IO_BUILD_CONTROLLER_CONFIG_V2',controllerIndex=frame['controller'],rootAuthority=authority)
    config_row=save(CONFIG,config);cap.recheck();print(json.dumps(config_row));return config_row

def clean_terminal(t,authority):
    assert type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority
    assert t['allObservedOwnedGroupsGone']is t['parentOwnedGroupGone']is True and t['timeout']is t['forcedCleanup']is False
    for k in ['signals','errors','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['finalGroups']and all(g['alive']is False for g in t['finalGroups'])

def run(config_descriptor):
    config_descriptor=descriptor(config_descriptor);assert config_descriptor['path']==str(CONFIG)
    # Read only standard DATA to discover the fixed peer, then authenticate all
    # code/protection before importing the genuine original monitor.
    initial=Capture();config=initial.read(config_descriptor)
    assert config['schemaVersion']==1 and config['state']=='CLOCK_IO_BUILD_CONTROLLER_CONFIG_V2'
    authority_row=descriptor(config['rootAuthority']);assert authority_row['path']==str(AUTHORITY)
    authority=initial.read(authority_row);frame=authenticate(authority['controllerReview']);cap=frame['capture']
    cap.file(config_descriptor);cap.file(authority_row);assert cap.read(config_descriptor)==config and cap.read(authority_row)==authority
    validate_authority(authority,frame);assert config['controllerIndex']==frame['controller'];fresh_roots();cap.recheck()
    os.umask(0o077);OBSERVER.mkdir(mode=0o700);identity=(OBSERVER.stat().st_dev,OBSERVER.stat().st_ino)
    terminal=None;terminal_row=None;streams={};errors=[];raw_capture_errors=[];observation=None;protected=False
    before=None;after=None;pre_error=None;post_error=None
    argv=[frame['context']['python']['path'],'-B','-I',str(CONTROLLER/'controller.py'),'parent',json.dumps(config_descriptor,separators=(',',':'))]
    try:
        before=shutil.disk_usage(WORK.parent).free
        assert before>=authority['requiredStartFreeBytes']
        cap.recheck()
        spec=importlib.util.spec_from_file_location('genuine_original_clock_tools_v2_root_monitor',frame['monitorEntry']['path'])
        monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor);cap.recheck()
        terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OBSERVER,7200,authority_row)
        terminal_row=row(OBSERVER/'terminal.json');assert cap.read(terminal_row)==terminal
        for k in ['stdout','stderr']:streams[k]=cap.file(terminal[k])
        clean_terminal(terminal,authority_row)
        assert terminal['stdout']['bytes']<=16*1024*1024
        parent_lines=[json.loads(b)for b in Path(terminal['stdout']['path']).read_bytes().splitlines()if b]
        assert len(parent_lines)==2 and set(parent_lines[0])=={'pid','timeoutSeconds'}and parent_lines[0]['timeoutSeconds']==7200
        parent_row=cap.file(row(EXTERNAL/'parent-observation.json'));parent=cap.read(parent_row)
        assert parent_lines[1]==dict(observation=parent_row,completeUnreviewed=True)
        assert parent['state']=='CLOCK_IO_BUILD_CONTROLLER_COMPLETE_UNREVIEWED_V2'and parent['controllerIndex']==frame['controller']and parent['sourceIndex']==frame['source']and parent['rootAuthority']==authority_row
        assert parent['errors']==[]and parent['protectedInputsRechecked']is True
        inner=cap.read(parent['rawTerminal']);clean_terminal(inner,authority_row)
        assert parent_lines[0]['pid']==inner['pid']
        for k in ['stdout','stderr']:cap.file(inner[k])
        worker_row=parent['workerObservation']['workerResult'];worker=cap.read(worker_row)
        assert parent['workerObservation']['rawWorkerStdout']==inner['stdout']and parent['workerObservation']['rawWorkerStderr']==inner['stderr']
        assert inner['stdout']['bytes']<=16*1024*1024
        worker_lines=[json.loads(b)for b in Path(inner['stdout']['path']).read_bytes().splitlines()if b]
        assert len(worker_lines)==9 and all(set(v)=={'pid','timeoutSeconds'}for v in worker_lines[:-1])and worker_lines[-1]==worker_row
        assert worker['state']=='CLOCK_IO_TOOLS_BUILD_COMPLETE_UNREVIEWED_V2'and worker['rootAuthority']==authority_row and worker['sourceIndex']==frame['source']
        assert worker['error']is worker['finalProtectionError']is None and worker['protectedInputsRechecked']is worker['privatePackageMembershipVerified']is True
        assert len(worker['commandTerminals'])==8
        for i,summary_row in enumerate(worker['commandTerminals']):
            summary=cap.read(summary_row);command=cap.read(summary['monitorTerminal']);clean_terminal(command,authority_row)
            expected=frame['commandPlan'][i]
            assert summary['argv']==expected['argv']and summary['cwd']==str(SRC)and summary['timeoutSeconds']==expected['timeoutSeconds']
            assert worker_lines[i]==dict(pid=command['pid'],timeoutSeconds=expected['timeoutSeconds'])
            for k in ['stdout','stderr']:cap.file(command[k])
            assert summary['beforeFloorPassed']is summary['afterFloorPassed']is summary['diskFloorCheckedBeforeAndAfter']is True and summary['diskFloorMonitoredDuringCommand']is False
        assert worker['prunerFunctionInvokedByRefusalUnitTest']is True
        for k in ['validAdapterPruningRun','adapterCliPruneCommandInvoked','adapterArtifactPublished','nativeEngineBuiltOrExecuted','applicationComponentConstructed','applicationGuestExecuted','operationalAdmission','runtimeAcceptanceClaim']:assert worker[k]is False
        for artifact in worker['artifacts']:cap.file(artifact)
        observation=dict(parentObservation=parent_row,workerResult=worker_row,innerTerminal=parent['rawTerminal'],rawParentJsonlRecords=2,
            rawWorkerJsonlLines=parent['workerObservation']['rawWorkerJsonlLines'],prunerFunctionInvokedByRefusalUnitTest=True)
    except BaseException as error:
        errors.append(dict(stage='owned-outer-build-or-whole-result',type=type(error).__name__,availablePartialFilesMayExist=True,fullPartialEvidenceClaim=False))
        if before is None:pre_error=dict(type=type(error).__name__)
    finally:
        # Actual post-space DATA precedes acceptance even on thrown monitor or
        # result checks. There is no continuous disk observation claim.
        try:after=shutil.disk_usage(WORK.parent).free
        except BaseException as error:post_error=dict(type=type(error).__name__)
        for k in ['stdout','stderr']:
            p=OBSERVER/(k+'.log')
            try:
                if p.is_file()and not p.is_symlink():streams[k]=row(p)
            except BaseException as error:raw_capture_errors.append(dict(stage='available-'+k+'-capture',type=type(error).__name__))
        p=OBSERVER/'terminal.json'
        try:
            if p.is_file()and not p.is_symlink():terminal_row=row(p)
        except BaseException as error:raw_capture_errors.append(dict(stage='available-terminal-capture',type=type(error).__name__))
        errors.extend(raw_capture_errors)
        try:cap.recheck();protected=True
        except BaseException as error:errors.append(dict(stage='final-input-protection',type=type(error).__name__))
    assert OBSERVER.is_dir()and not OBSERVER.is_symlink()and (OBSERVER.stat().st_dev,OBSERVER.stat().st_ino)==identity
    if after is None or after<authority['minimumBoundaryFreeBytes']:errors.append(dict(stage='actual-final-space-floor',type='UnavailableOrBelowFloor'))
    success=observation is not None and protected and not errors
    result=dict(schemaVersion=1,state='ROOT_OBSERVED_CLOCK_IO_TOOL_BUILD_PARENT_ZERO_UNREVIEWED_V2'if success else'ROOT_OBSERVED_CLOCK_IO_TOOL_BUILD_FAILED_UNACCEPTED_V2',
        sourceIndex=frame['source'],controllerIndex=frame['controller'],sourceReview=frame['sourcePeer'],controllerReview=frame['controllerPeer'],
        rootAuthority=authority_row,config=config_descriptor,rootOuterController=row(ORIGINAL),terminal=terminal_row,streams=streams,
        rawParentExitCode=None if terminal is None else terminal['rawExitCode'],rawMonitorCallReturned=terminal is not None,
        allObservedOwnedGroupsGone=False if terminal is None else terminal['allObservedOwnedGroupsGone'],cleanOwnedCleanup=success,
        buildObservation=observation,protectedInputsRechecked=protected,errors=errors,
        beforeFreeBytes=before,afterFreeBytes=after,preSpaceObservationError=pre_error,postSpaceObservationError=post_error,
        diskFloorMonitoredDuringCommand=False,diskFloorCheckedBeforeAndAfter=before is not None and after is not None,
        beforeFloorPassed=before is not None and before>=authority['requiredStartFreeBytes'],afterFloorPassed=after is not None and after>=authority['minimumBoundaryFreeBytes'],
        availableRawCaptureErrors=raw_capture_errors,allAvailableRawCaptureComplete=not raw_capture_errors,
        prunerFunctionInvokedByRefusalUnitTest=True if observation is not None else None,
        validAdapterPruningRun=False,adapterCliPruneCommandInvoked=False,adapterPublished=False,
        applicationEngineOrGuestExecuted=False,independentArtifactReview=None,operationalAdmission=False,runtimeAcceptanceClaim=False)
    result_row=save(OBSERVER/'root-observation.json',result);print(json.dumps(result_row));return 0 if success else 1

if __name__=='__main__':
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert len(sys.argv)==3 and sys.argv[1]in ['issue','run']
    if sys.argv[1]=='issue':issue(json.loads(sys.argv[2]))
    else:raise SystemExit(run(json.loads(sys.argv[2])))
