"""Dormant one-command encoded-WIT-package metadata continuation. Root gates required."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,stat,sys
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-io-metadata-package-decoder-candidate-v1')
REPO=Path('/Users/dan/dev/StarlingMonkey')
FORBIDDEN=['normalizationAllowed','pruningAllowed','nodeValidationAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']
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

def native_argv(refs):
    # Native1.235 default WIT output prints the main plus EVERY nested package.
    # No --importize/merge/no-docs/world selection or output truncation option.
    return [refs['wasmTools']['path'],'component','wit',refs['metadataPayload']['path']]


def tokens(raw):
    assert type(raw)is bytes and 0<len(raw)<=4*1024*1024
    text=raw.decode('utf-8','strict');assert '\x1b'not in text and '\0'not in text
    result=[];i=0
    while i<len(text):
        if text[i].isspace():i+=1;continue
        if text.startswith('//',i):
            end=text.find('\n',i);i=len(text)if end<0 else end+1;continue
        if text.startswith('/*',i):
            depth=1;i+=2
            while depth:
                assert i<len(text),'Unclosed comment'
                if text.startswith('/*',i):depth+=1;i+=2
                elif text.startswith('*/',i):depth-=1;i+=2
                else:i+=1
            continue
        if text[i]=='"':
            start=i;i+=1
            while i<len(text)and text[i]!='"':
                if text[i]=='\\':i+=1
                i+=1
            assert i<len(text);i+=1;result.append(text[start:i]);continue
        m=re.match(r'%?[A-Za-z_][A-Za-z0-9_-]*|[0-9]+(?:\.[0-9]+)*',text[i:])
        if m:result.append(m.group());i+=len(m.group())
        else:result.append(text[i]);i+=1
    return result


def full_wit_observations(raw,expected):
    """Finite output observations only. Native decode validates actual WIT types.

    This deliberately is NOT a replacement WIT parser. Preserve all raw bytes;
    observe package/interface/world declarations and specific resource aliases.
    """
    ts=tokens(raw);packages=[];decls={};bodies={}
    def end_block(i,end):
        assert ts[i]=='{';depth=1;j=i+1
        while j<end and depth:
            if ts[j]=='{':depth+=1
            elif ts[j]=='}':depth-=1
            j+=1
        assert depth==0,'Unclosed declaration block';return j
    def scope(start,end,package=None):
        i=start
        while i<end:
            kind=ts[i]
            if kind=='package':
                j=i+1
                while j<end and ts[j]not in [';','{']:j+=1
                assert j<end;name=''.join(ts[i+1:j]);assert re.fullmatch(r'wasi:[a-z-]+@0\.2\.0',name)
                assert name not in packages;packages.append(name)
                if ts[j]==';':assert package is None;package=name;i=j+1
                else:
                    z=end_block(j,end);scope(j+1,z-1,name);i=z
            elif kind in ['interface','world']:
                assert package is not None and i+2<end and ts[i+2]=='{'
                name=ts[i+1];assert re.fullmatch(r'[a-z][a-z0-9-]*',name)
                namespace,version=package.split('@');key=namespace+'/'+name+'@'+version
                assert key not in decls;decls[key]=kind
                z=end_block(i+2,end);bodies[key]=ts[i+3:z-1];i=z
            elif kind in ['{','}']:
                raise AssertionError('Unexpected declaration scope')
            else:i+=1
    scope(0,len(ts))
    assert sorted(packages)==expected['packages'] and sorted(decls)==expected['declarations']
    assert [k for k,v in decls.items()if v=='world']==['wasi:cli/imports@0.2.0']
    def has(key,fragment):
        body=bodies[key];needle=tokens(fragment.encode());assert any(body[i:i+len(needle)]==needle for i in range(len(body)-len(needle)+1)),(key,fragment)
    required=[
        ('wasi:io/error@0.2.0','resource error'),
        ('wasi:io/poll@0.2.0','resource pollable'),
        ('wasi:io/streams@0.2.0','resource input-stream'),
        ('wasi:io/streams@0.2.0','resource output-stream'),
        ('wasi:io/streams@0.2.0','use error.{error}'),
        ('wasi:io/streams@0.2.0','use poll.{pollable}'),
        ('wasi:cli/stdin@0.2.0','use wasi:io/streams@0.2.0.{input-stream}'),
        ('wasi:cli/stdout@0.2.0','use wasi:io/streams@0.2.0.{output-stream}'),
        ('wasi:cli/stderr@0.2.0','use wasi:io/streams@0.2.0.{output-stream}'),
        ('wasi:clocks/monotonic-clock@0.2.0','use wasi:io/poll@0.2.0.{pollable}'),
    ]
    for key,fragment in required:has(key,fragment)
    return dict(schemaVersion=1,fullRawBytes=len(raw),packages=sorted(packages),declarations=decls,
        observedResourceAliasClauses=[dict(declaration=k,clause=v)for k,v in required],
        completeGraphPrintedByPinnedNativeDecoder=True,finiteTextObservationsOnly=True,
        standaloneTextParserExecuted=False,applicationInstantiationPerformed=False)


def check_failed_phase(c,refs):
    failure,_=c.proof(refs['failedPhaseReview']);contract=c.read(refs['failedPhaseContract'])
    assert failure['schemaVersion']==contract['schemaVersion']==1
    assert failure['state']==contract['requiredFixedValues']['state']=='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_METADATA_FAILURE_REVIEW_PASSED_V1'
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
        for k,v in contract.get(group,{}).items():assert failure[k]==v
    if 'requiredCoverage'in contract:assert failure['coverage']==contract['requiredCoverage']
    assert failure['verifiedPassed']is True and failure['phasePassed']is failure['adapterAccepted']is failure['metadataDecoded']is False
    assert failure['rootObservation']==refs['failedRootObservation']
    for key in ['normalizedAdapter','prunedAdapter','metadataPayload','coreValidation','structuralAudit']:assert failure[key]==refs[key]
    assert failure['coreDataAuditPassed']is True and failure['actualWorkerExitCode']==1 and failure['prunerExitCode']==failure['nodeCoreValidationExitCode']==0 and failure['metadataExitCode']==1
    original=c.read(refs['failedRootObservation'])
    assert original['state']=='ROOT_OBSERVED_CLOCK_IO_VALID_ADAPTER_FAILED_AT_METADATA_V1'and original['finalProtectionError']is None
    assert original['applicationEngineOrGuestExecuted']is original['adapterPromoted']is original['operationalAdmission']is original['runtimeAcceptanceClaim']is False
    validation=c.read(refs['coreValidation']);assert validation['normalizedValid']is validation['prunedValid']is True and validation['instantiated']is False
    audit=c.read(refs['structuralAudit']);assert audit['convertedTargetImports']==14 and audit['clocksPreserved']==6 and audit['pollImportsPreserved']==2 and audit['encodedWitComponentSha256']==refs['metadataPayload']['sha256']
    for t in refs['oldTrees']:
        exact_tree(Path(t['root']),t['names']);c.families.append((Path(t['root']),set(t['names']),False))


def authenticate(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and HERE==ORIGINAL
    assert not any(os.environ.get(k)for k in ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])
    c=Capture();config_row=descriptor(config_row);cfg=c.read(config_row)
    assert cfg['schemaVersion']==1 and cfg['state']=='CLOCK_IO_METADATA_PACKAGE_CONFIG_V1'
    own=descriptor(cfg['sourceIndex']);assert own['path']==str(HERE/'index.json');c.family(own)
    refs=c.read(fingerprint(HERE/'references.json')[0]);inputs=c.read(fingerprint(HERE/'source-inputs.json')[0])
    assert refs['originalRoot']==str(HERE)and inputs['schemaVersion']==1 and 24359<=len(inputs['files'])<=40000
    assert len({r['path']for r in inputs['files']})==len(inputs['files'])
    for r in inputs['files']:c.file(r)
    for ix in inputs['families']:c.family(ix)
    root_row=descriptor(cfg['rootAuthority']);root=c.read(root_row)
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CLOCK_IO_METADATA_PACKAGE_PHASE_V1'
    assert root['sourceIndex']==own and root['entry']==fingerprint(HERE/'controller.py')[0]and root['phase']=='decode-retained-wit-package-once'
    assert root['metadataPackageDecodeAllowed']is True and root['failedPhaseReview']==refs['failedPhaseReview']
    for k in FORBIDDEN:assert root[k]is False
    for k in ['outputRoot','externalRoot','metadataDeadlineSeconds']:assert root[k]==refs[k]
    assert root['phaseDeadlineSeconds']==300 and root['actualMetadataReview']is None
    peer,_=c.proof(root['sourceIndependentReview'])
    assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_CLOCK_IO_METADATA_PACKAGE_DECODER_SOURCE_REVIEW_PASSED_V1'
    assert peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False
    check_failed_phase(c,refs)
    assert str(Path(sys.executable).resolve())==refs['python']['path'];c.file(refs['python']);c.file(refs['monitor']);c.file(refs['wasmTools'])
    assert refs['wasmTools']['sha256']=='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
    assert refs['metadataPayload']['sha256']=='7485a77ee78375ef134c4cebca67142ded37cd68891130b0213986a27f84c072'and refs['metadataPayload']['bytes']==10730
    c.recheck();return dict(c=c,config=cfg,configRow=config_row,own=own,refs=refs,root=root,rootRow=root_row)


def collect_terminal(c,row,terminal):
    # Preserve whole returned primitive frame and streams before clean assertions.
    assert c.read(row)==terminal
    for key in ['stdout','stderr']:c.file(terminal[key])
    return dict(terminal=row,stdout=terminal['stdout'],stderr=terminal['stderr'],rawExitCode=terminal['rawExitCode'])


def run(frame):
    refs=frame['refs'];c=frame['c'];out=Path(refs['outputRoot']);external=Path(refs['externalRoot'])
    for p in [out,external]:assert not p.exists()and not p.is_symlink()
    c.recheck();monitor=load_actual(refs['monitor'],'genuine_original_clock_metadata_monitor_0af');c.recheck()
    os.umask(0o077);out.mkdir(mode=0o700);external.mkdir(mode=0o700);command=external/'metadata-wit';command.mkdir(mode=0o700)
    roots={str(p):(p.stat().st_dev,p.stat().st_ino)for p in [out,external]};observed=None;error=None;protection_error=None;observations=None;attempted=False
    try:
        c.recheck();attempted=True
        terminal=monitor.monitor(native_argv(refs),str(REPO),dict(os.environ),command,60,frame['rootRow'])
        observed=collect_terminal(c,fingerprint(command/'terminal.json')[0],terminal)
        write(out/'metadata-raw-observed.json',observed)
        clean_terminal(terminal,frame['rootRow'])
        stdout=terminal['stdout'];assert 0<stdout['bytes']<=4*1024*1024
        raw=Path(stdout['path']).read_bytes();assert len(raw)==stdout['bytes']and hashlib.sha256(raw).hexdigest()==stdout['sha256']
        observations=full_wit_observations(raw,refs['expectedWitDeclarations']);write(out/'wit-observations.json',observations)
    except BaseException as e:
        error=dict(type=type(e).__name__,message=str(e))
        p=command/'terminal.json'
        if observed is None and p.is_file()and not p.is_symlink():
            terminal=c.read(fingerprint(p)[0]);observed=collect_terminal(c,fingerprint(p)[0],terminal)
            write(out/'metadata-raw-observed.json',observed)
    finally:
        try:
            c.recheck()
            for path,identity in roots.items():
                p=Path(path);assert not p.is_symlink()and(p.stat().st_dev,p.stat().st_ino)==identity and stat.S_IMODE(p.stat().st_mode)==0o700
        except BaseException as e:protection_error=dict(type=type(e).__name__,message=str(e))
    complete=error is protection_error is None
    result=dict(schemaVersion=1,state='CLOCK_IO_METADATA_PACKAGE_COMPLETE_UNREVIEWED_V1'if complete else'CLOCK_IO_METADATA_PACKAGE_FAILED_UNACCEPTED_V1',
        sourceIndex=frame['own'],rootAuthority=frame['rootRow'],config=frame['configRow'],failedRootObservation=refs['failedRootObservation'],failedPhaseReview=refs['failedPhaseReview'],
        normalizedAdapter=refs['normalizedAdapter'],prunedAdapter=refs['prunedAdapter'],metadataPayload=refs['metadataPayload'],wasmTools=refs['wasmTools'],
        command=observed,fullWit=None if not complete else observed['stdout'],witObservations=None if observations is None else fingerprint(out/'wit-observations.json')[0],
        nativeMetadataDecoderAttempted=attempted,sourceBoundedMaximumDecoderCalls=1,metadataDecoded=complete,wholeGraphRenderRequired=True,
        previousPhaseRemainsFailed=True,previousPhasePassed=False,normalizerOrPrunerRerun=False,nodeValidationRerun=False,
        applicationEngineOrGuestExecuted=False,adapterPromoted=False,defaultPackagerReplaced=False,requiresIndependentActualReview=True,
        operationalAdmission=False,runtimeAcceptanceClaim=False,error=error,finalProtectionError=protection_error)
    result_row=write(out/'result.json',result)
    rows=[]
    for p in sorted(external.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():rows.append(fingerprint(p)[0])
    write(out/'external-inventory.json',dict(schemaVersion=1,files=rows))
    members=[]
    for p in sorted(out.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():members.append(dict(fingerprint(p)[0],path=str(p.relative_to(out))))
    ix=write(out/'index.json',dict(schemaVersion=1,files=members))
    write(out/'completion.json',dict(schemaVersion=1,state='COMPLETE_UNREVIEWED'if complete else'FAILED_UNACCEPTED',index=ix,result=result_row,metadataDecoded=complete,operationalAdmission=False))
    c.recheck();print(json.dumps(result_row),flush=True);return 0 if complete else 1


def main():
    assert len(sys.argv)==2;frame=authenticate(json.loads(sys.argv[1]))
    try:return run(frame)
    finally:frame['c'].recheck()
if __name__=='__main__':sys.exit(main())
