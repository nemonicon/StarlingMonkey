"""Dormant exact-normalize + one-shot valid native CLI phase. Root grants required."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-io-valid-adapter-candidate-v1')
REPO=Path('/Users/dan/dev/StarlingMonkey')
FORBIDDEN=['adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']
def descriptor(value):
    assert type(value)is dict and set(value)=={'path','sha256','bytes'}
    assert type(value['path'])is str and Path(value['path']).is_absolute()and str(Path(value['path']))==value['path']and '..'not in Path(value['path']).parts and '\\'not in value['path']and '\0'not in value['path']
    assert type(value['bytes'])is int and 0<=value['bytes']<=2**40
    assert type(value['sha256'])is str and len(value['sha256'])==64 and all(x in'0123456789abcdef'for x in value['sha256'])
    return dict(value)

def fingerprint(path):
    p=Path(path);assert p.is_file()and not p.is_symlink()
    a=p.stat();real=str(p.resolve());h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(a)==identity(z)and real==str(p.resolve())
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z),real

def local(name):
    assert type(name)is str and name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(x not in('','.','..')for x in name.split('/'))
    return name

def exact_tree(root,names,private=False):
    assert root.is_dir()and not root.is_symlink()
    if private:assert stat.S_IMODE(root.stat().st_mode)==0o700
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            actual.add(str(p.relative_to(root)))
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o600
        else:
            assert p.is_dir()
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o700
    assert actual==set(names)

class Capture:
    def __init__(self):self.rows={};self.families=[]
    def file(self,value):
        row=descriptor(value);actual,identity,real=fingerprint(row['path']);assert actual==row
        if row['path']in self.rows:assert self.rows[row['path']]==(row,identity,real)
        self.rows[row['path']]=(row,identity,real);return row
    def read(self,value):
        row=self.file(value);assert row['bytes']<=32*1024*1024
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)
    def family(self,index):
        value=self.read(index);root=Path(index['path']).parent;names=set();rows=[index]
        assert value['schemaVersion']==1 and type(value['files'])is list and 0<len(value['files'])<=2048
        for r in value['files']:
            name=local(r['path']);assert name not in names;names.add(name);row=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);self.file(row);rows.append(row)
        exact_tree(root,names|{'index.json'});self.families.append((root,names|{'index.json'},False));return rows
    def proof(self,pair):
        rows=self.family(pair['index']);assert pair['result']in rows;return self.read(pair['result']),rows
    def recheck(self):
        for row,identity,real in list(self.rows.values()):assert fingerprint(row['path'])==(row,identity,real)
        for root,names,private in self.families:exact_tree(root,names,private)

def clean_terminal(t,authority):
    assert type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and t['timeout']is False and t['forcedCleanup']is False
    for k in['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['finalGroups']and all(r['alive']is False for r in t['finalGroups'])and t['stderr']['bytes']==0

def load_actual(row,name):
    actual,_,_=fingerprint(row['path']);assert actual==row
    spec=importlib.util.spec_from_file_location(name,row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def write(path,value):
    path=Path(path);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'w',closefd=False)as stream:
            json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    finally:os.close(fd)
    return fingerprint(path)[0]


def authenticate(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and HERE==ORIGINAL
    assert not any(os.environ.get(k)for k in ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])
    c=Capture();config_row=descriptor(config_row);cfg=c.read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='CLOCK_IO_VALID_ADAPTER_CONFIG_V1'
    own=descriptor(cfg['sourceIndex']);assert own['path']==str(HERE/'index.json');c.family(own)
    refs=c.read(fingerprint(HERE/'references.json')[0]);inputs=c.read(fingerprint(HERE/'source-inputs.json')[0])
    assert refs['originalRoot']==str(HERE)and inputs['schemaVersion']==1 and 24332<=len(inputs['files'])<=40000
    assert len({r['path']for r in inputs['files']})==len(inputs['files'])
    for r in inputs['files']:c.file(r)
    for index in inputs['families']:c.family(index)
    root_row=descriptor(cfg['rootAuthority']);root=c.read(root_row)
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CLOCK_IO_VALID_ADAPTER_PHASE_V1'and root['sourceIndex']==own
    assert root['entry']==fingerprint(HERE/'controller.py')[0]and root['phase']=='normalize-and-prune-once'
    for k in ['normalizationAllowed','singlePrunerCallAllowed','coreValidationAllowed','metadataWitDecodeAllowed']:assert root[k]is True
    for k in FORBIDDEN:assert root[k]is False
    for k in ['outputRoot','externalRoot','prunerDeadlineSeconds','nodeValidationDeadlineSeconds','phaseDeadlineSeconds']:assert root[k]==refs[k]
    assert root['metadataDeadlineSeconds']==60 and root['actualAdapterReview']is None
    peer,_=c.proof(root['sourceIndependentReview']);assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False
    proof,_=c.proof(refs['buildReview']);contract=c.read(refs['buildContract']);assert proof['state']==contract['requiredReviewState']=='INDEPENDENT_CLOCK_IO_TOOLS_BUILD_RESULTS_REVIEW_PASSED_V2'
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
        for key,value in contract[group].items():assert proof[key]==value
    assert proof['coverage']==contract['requiredCoverage']and proof['artifacts']==contract['artifacts']and proof['artifacts'][0]==refs['hostPruner']
    assert proof['actualRootObservation']==refs['actualRootObservation']and proof['actualWorkerResult']==refs['actualWorkerResult']
    requirements=c.read(refs['followonRequirements']);assert requirements['actualHostPruner']==refs['hostPruner']and requirements['originalAdapter']==refs['originalAdapter']and requirements['rootAuthority']is None
    assert str(Path(sys.executable).resolve())==refs['python']['path'];c.file(refs['python']);c.file(refs['node']);c.file(refs['originalAdapter']);c.file(refs['normalizer']);c.file(refs['hostPruner']);c.file(refs['monitor'])
    c.recheck();return dict(c=c,config=cfg,configRow=config_row,own=own,refs=refs,root=root,rootRow=root_row)


def available(out):
    rows=[]
    for n in ['normalized-adapter.wasm','pruned-adapter.wasm','core-validation.json','structural-audit.json','embedded-wit-component.wasm']:
        p=out/n
        if p.is_file()and not p.is_symlink():rows.append(fingerprint(p)[0])
    return rows


def owned(frame,name,argv,deadline):
    folder=Path(frame['refs']['externalRoot'])/name;folder.mkdir(mode=0o700)
    t=frame['monitor'].monitor(argv,str(REPO),dict(os.environ),folder,deadline,frame['rootRow'])
    row=fingerprint(folder/'terminal.json')[0];assert frame['c'].read(row)==t
    for key in ['stdout','stderr']:frame['c'].file(t[key])
    write(Path(frame['refs']['outputRoot'])/(name+'-raw-observed.json'),dict(terminal=row,stdout=t['stdout'],stderr=t['stderr'],interpretationPending=True))
    clean_terminal(t,frame['rootRow']);return row,t


def worker(frame):
    refs=frame['refs'];out=Path(refs['outputRoot']);assert out.is_dir()and not out.is_symlink()and stat.S_IMODE(out.stat().st_mode)==0o700
    normal=out/'normalized-adapter.wasm';pruned=out/'pruned-adapter.wasm';error=None;protection_error=None;normalized=None;pruned_row=None;terminals=[];audit=None
    try:
        frame['c'].recheck()
        normalizer=load_actual(refs['normalizer'],'genuine_original_clock_normalizer_55338')
        frame['monitor']=load_actual(refs['monitor'],'genuine_original_clock_valid_monitor_0af')
        auditor=load_actual(frame['c'].rows[str(HERE/'core_audit.py')][0],'new_clock_core_data_auditor')
        frame['c'].recheck()
        assert not normal.exists()and not normal.is_symlink()and not pruned.exists()and not pruned.is_symlink()
        # Genuine original API owns O_EXCL0600 + fd wrapping/flush/fsync/final close.
        normalized=normalizer.write_normalized(refs['originalAdapter']['path'],str(normal))
        assert frame['c'].file(normalized)==dict(path=str(normal),sha256=refs['normalizedSha256'],bytes=53512)
        write(out/'normalized-observation.json',dict(actual=normalized,source=refs['originalAdapter'],genuineNormalizer=refs['normalizer'],interpretationPending=True))
        frame['c'].recheck()
        # Exactly one actual native pruner invocation, no help/version/retry.
        assert not pruned.exists()and not pruned.is_symlink()
        row,t=owned(frame,'pruner',[refs['hostPruner']['path'],'prune-clock-adapter-io','--input',str(normal),'--output',str(pruned)],300);terminals.append(row)
        pruned_row=fingerprint(pruned)[0];write(out/'pruned-raw-descriptor.json',pruned_row)
        s=pruned.stat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 8<=pruned_row['bytes']<=1024*1024
        frame['c'].file(pruned_row);frame['c'].recheck()
        row,t=owned(frame,'core-validate',[refs['node']['path'],str(HERE/'validate-core.mjs'),str(normal),str(pruned),str(out/'core-validation.json')],60);terminals.append(row)
        validation=frame['c'].read(fingerprint(out/'core-validation.json')[0]);assert validation['normalizedValid']is validation['prunedValid']is True and validation['instantiated']is False and validation['normalized']==normalized and validation['pruned']==pruned_row
        audit=auditor.audit_pair(normal.read_bytes(),pruned.read_bytes());write(out/'structural-audit.json',audit)
        # Metadata aliases are independently decoded as tooling DATA, not app Wasm.
        payload=auditor.component_type_payload(pruned.read_bytes())
        assert payload==auditor.component_type_payload(normal.read_bytes())
        component_meta=out/'embedded-wit-component.wasm';fd=os.open(component_meta,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'wb',closefd=False)as f:assert f.write(payload)==len(payload);f.flush();os.fsync(f.fileno())
        finally:os.close(fd)
        row,t=owned(frame,'metadata-wit',[refs['node']['path'],refs['jcoEntry']['path'],'wit',str(component_meta)],60);terminals.append(row)
        assert t['stdout']['bytes']>0;wit=Path(t['stdout']['path']).read_text();assert 'world 'in wit
        result=dict(schemaVersion=1,state='CLOCK_IO_VALID_ADAPTER_COMPLETE_UNREVIEWED_V1',sourceIndex=frame['own'],rootAuthority=frame['rootRow'],config=frame['configRow'],originalAdapter=refs['originalAdapter'],normalizer=refs['normalizer'],hostPruner=refs['hostPruner'],normalized=normalized,pruned=pruned_row,coreValidation=fingerprint(out/'core-validation.json')[0],structuralAudit=fingerprint(out/'structural-audit.json')[0],metadataComponent=fingerprint(component_meta)[0],metadataWit=t['stdout'],commandTerminals=terminals,prunerCalls=1,metadataAliasesDecodedFromIdenticalPayload=True,applicationEngineOrGuestExecuted=False,toolingMetadataParserWasmMayExecute=True,adapterPromoted=False,defaultPackagerReplaced=False,requiresIndependentActualReview=True,operationalAdmission=False,runtimeAcceptanceClaim=False)
    except BaseException as e:
        error=dict(type=type(e).__name__,message=str(e));result=dict(schemaVersion=1,state='CLOCK_IO_VALID_ADAPTER_FAILED_UNACCEPTED_V1',sourceIndex=frame['own'],rootAuthority=frame['rootRow'],error=error,availableActualFiles=available(out),completeOutputClaim=False,prunerCallCountSourceBoundedAtMostOne=True,operationalAdmission=False,runtimeAcceptanceClaim=False)
    finally:
        try:frame['c'].recheck()
        except BaseException as e:protection_error=dict(type=type(e).__name__,message=str(e))
    result['finalProtectionError']=protection_error
    if protection_error is not None:result['state']='CLOCK_IO_VALID_ADAPTER_FAILED_UNACCEPTED_V1'
    row=write(out/'result.json',result);print(json.dumps(row),flush=True);return 0 if error is protection_error is None else 1


def parent(frame):
    refs=frame['refs'];out=Path(refs['outputRoot']);external=Path(refs['externalRoot'])
    for p in [out,external]:assert not p.exists()and not p.is_symlink()
    frame['c'].recheck();monitor=load_actual(refs['monitor'],'genuine_original_clock_valid_outer_monitor');frame['c'].recheck();os.umask(0o077);out.mkdir(mode=0o700);external.mkdir(mode=0o700)
    root_identity=(out.stat().st_dev,out.stat().st_ino);folder=external/'worker';folder.mkdir(mode=0o700);terminal=None;error=None
    try:
        argv=[refs['python']['path'],'-B','-I',str(HERE/'controller.py'),'worker',json.dumps(frame['configRow'],separators=(',',':'))]
        terminal=monitor.monitor(argv,str(REPO),dict(os.environ),folder,600,frame['rootRow']);row=fingerprint(folder/'terminal.json')[0];assert frame['c'].read(row)==terminal
        write(out/'worker-raw-observed.json',dict(terminal=row,stdout=terminal['stdout'],stderr=terminal['stderr'],interpretationPending=True));clean_terminal(terminal,frame['rootRow'])
        lines=[json.loads(x)for x in Path(terminal['stdout']['path']).read_text().splitlines()if x];assert len(lines)==4 and [x['timeoutSeconds']for x in lines[:3]]==[300,60,60]
        result=frame['c'].read(lines[-1]);assert result['state']=='CLOCK_IO_VALID_ADAPTER_COMPLETE_UNREVIEWED_V1'and result['prunerCalls']==1 and result['finalProtectionError']is None
    except BaseException as e:error=dict(type=type(e).__name__,message=str(e));result=None
    finally:frame['c'].recheck()
    assert(out.stat().st_dev,out.stat().st_ino)==root_identity
    observation=dict(schemaVersion=1,state='CLOCK_IO_VALID_ADAPTER_PARENT_COMPLETE_UNREVIEWED_V1'if error is None else'CLOCK_IO_VALID_ADAPTER_PARENT_FAILED_UNACCEPTED_V1',sourceIndex=frame['own'],rootAuthority=frame['rootRow'],config=frame['configRow'],rawTerminal=None if terminal is None else fingerprint(folder/'terminal.json')[0],workerResult=None if result is None else fingerprint(out/'result.json')[0],error=error,availableActualFiles=available(out),operationalAdmission=False,runtimeAcceptanceClaim=False,requiresIndependentActualReview=True)
    print(json.dumps(dict(observation=write(out/'parent-observation.json',observation),completeUnreviewed=error is None)),flush=True);return 0 if error is None else 1


def main():
    assert len(sys.argv)==3 and sys.argv[1]in ['parent','worker'];frame=authenticate(json.loads(sys.argv[2]))
    try:return parent(frame)if sys.argv[1]=='parent'else worker(frame)
    finally:frame['c'].recheck()
if __name__=='__main__':sys.exit(main())
