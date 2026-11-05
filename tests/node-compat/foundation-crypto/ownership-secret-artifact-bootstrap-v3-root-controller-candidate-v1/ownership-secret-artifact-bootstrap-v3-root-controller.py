"""Dormant Root-gated pin DATA derivation and one-shot JS bootstrap observer.

No original tooling context is rebound; original d62 API owns its Python call.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,stat,sys
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-artifact-bootstrap-v3-root-controller-candidate-v1')
REPO=Path('/Users/dan/dev/StarlingMonkey')
TOOLING=REPO/'tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v3'
SOURCE_PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_SECRET_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
FORBIDDEN=['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed','moduleAdmissionAllowed']

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
    with os.fdopen(fd,'w')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return fingerprint(path)[0]

def four_pin_edits(before,after):
    paths=[]
    def walk(a,b,path):
        if type(a)is dict and type(b)is dict:
            assert set(a)==set(b)
            for k in a:walk(a[k],b[k],path+(k,))
        elif type(a)is list and type(b)is list:
            assert len(a)==len(b)
            for i in range(len(a)):walk(a[i],b[i],path+(i,))
        elif type(a)is not type(b)or a!=b:paths.append((path,a,b))
    walk(before,after,())
    expected={('state',):('UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3','ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3'),('reviewRequired',):(True,False),('variants','normal-off','state'):('unreviewed-secret-owner355-normal-off-pin-v3','reviewed-secret-owner355-normal-off-pin-v3'),('variants','normal-off','reviewRequired'):(True,False)}
    assert len(paths)==4 and {p:(a,b)for p,a,b in paths}==expected
    assert set(after['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}
    assert all(after['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off'])
    return [list(p)for p,a,b in paths]


def export_gate(c,refs):
    proof,rows=c.proof(refs['exportReview']);assert refs['exportContract']in rows
    contract=c.read(refs['exportContract'])
    assert contract['schemaVersion']==contract['requiredResultSchemaVersion']==3
    assert contract['requiredReviewState']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V3'
    assert proof['schemaVersion']==3 and proof['state']==contract['requiredReviewState']
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
        for key,value in contract[group].items():assert proof[key]==value
    assert proof['coverage']==contract['requiredCoverage']
    assert proof['candidate']==refs['exportCandidate']and proof['rootObservation']==refs['exportRootObservation']and proof['inputClosure']==refs['exportInputLedger']
    assert proof['toolingSourceIndex']==refs['toolingIndex']and proof['toolingSourceReview']==refs['toolingSourceReview']
    c.file(refs['exportRootObservation']);candidate=c.read(refs['exportCandidate'])
    assert candidate['schemaVersion']==3 and candidate['state']=='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3'and candidate['reviewRequired']is True
    assert candidate['toolingIndex']==refs['toolingIndex']and candidate['validationBootstrapOnly']is True
    assert candidate['operationalAdmission']is candidate['runtimeAcceptanceClaim']is False
    assert set(candidate['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}
    assert all(candidate['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off'])
    return proof,candidate


def validate_tooling_bootstrap(c,root,refs,tr):
    cfg=c.read(root['toolingBootstrapConfig']);authority=c.read(root['toolingBootstrapAuthority'])
    assert cfg==dict(schemaVersion=3,state='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3',phase='bootstrap',toolingIndex=refs['toolingIndex'],rootAuthority=root['toolingBootstrapAuthority'])
    assert authority['schemaVersion']==3 and authority['state']=='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3'and authority['phase']=='bootstrap'and authority['variant']=='normal-off'
    assert authority['toolingIndex']==refs['toolingIndex']and authority['sourceIndependentReview']==refs['toolingSourceReview']
    assert authority['exportAllowed']is False and authority['bootstrapAllowed']is True
    for key in ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:assert authority[key]is False
    for key in ['nativeSourceIndex','verifierSourceIndex','actualVerifierReview','actualArtifactReview','engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','frozenRoot']:assert authority[key]==tr[key]
    for key,value in dict(nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,outputRoot=refs['bootstrapOutputRoot'],externalOutputRoot=refs['bootstrapExternalRoot'],jsOutputRoot=refs['bootstrapJsRoot'],externalParentDeadlineSeconds=600,expectedCompleteVerifierCalls=1,actualExportCandidate=refs['exportCandidate'],independentExportReview=refs['exportReview'],reviewedPins=root['reviewedPins'],rootPinReview=root['rootPinReview']).items():assert authority[key]==value
    assert authority['runtimeAuthority']is authority['actualBootstrap']is None
    document=c.read(root['reviewedPins']);review=c.read(root['rootPinReview']);candidate=c.read(refs['exportCandidate']);four_pin_edits(candidate,document)
    expected=c.read(refs['pinReviewTemplate'])
    expected.update(state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex=refs['toolingIndex'],reviewedPins=root['reviewedPins'],actualExportCandidate=refs['exportCandidate'],independentExportReview=refs['exportReview'])
    assert review==expected,'Exact genuine schema3 Root pin-review fields; no projected metadata'


def authorize(config_row,phase):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and HERE==ORIGINAL
    assert phase in ['derive-pins','bootstrap-js']
    assert not any(os.environ.get(k)for k in ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])
    c=Capture();config_row=descriptor(config_row);cfg=c.read(config_row)
    assert cfg['schemaVersion']==1 and cfg['state']=='SECRET355_BOOTSTRAP_ROOT_CONTROLLER_CONFIG_V1'and cfg['phase']==phase
    own=descriptor(cfg['controllerIndex']);assert own['path']==str(HERE/'index.json');c.family(own)
    refs=c.read(fingerprint(HERE/'references.json')[0]);manifest=c.read(fingerprint(HERE/'source-inputs.json')[0])
    assert refs['originalControllerRoot']==str(HERE)and refs['schemaVersion']==1
    assert manifest['schemaVersion']==1 and type(manifest['files'])is list and 27800<=len(manifest['files'])<=40000
    assert len({r['path']for r in manifest['files']})==len(manifest['files'])
    for r in manifest['files']:c.file(r)
    for index in manifest['families']:c.family(index)
    root_row=descriptor(cfg['rootAuthority']);root=c.read(root_row)
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SECRET355_BOOTSTRAP_CONTROLLER_PHASE_V1'and root['phase']==phase
    assert root['controllerIndex']==own and root['controllerEntry']==fingerprint(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.py')[0]
    assert root['runnerEntry']==fingerprint(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.mjs')[0]
    assert root['toolingIndex']==refs['toolingIndex']and root['independentExportReview']==refs['exportReview']and root['actualExportCandidate']==refs['exportCandidate']
    assert root['pinDerivationAllowed']is(phase=='derive-pins')and root['bootstrapJsAllowed']is(phase=='bootstrap-js')
    for k in FORBIDDEN:assert root[k]is False
    for key in ['actualBootstrap','runtimeAuthority']:assert root[key]is None
    for key in ['pinOutputRoot','observerOutputRoot','observerExternalRoot','outerDeadlineSeconds']:assert root[key]==refs[key]
    peer,_=c.proof(root['sourceIndependentReview']);assert peer['schemaVersion']==1 and peer['state']==SOURCE_PEER_STATE
    assert peer['controllerSourceIndexSha256']==own['sha256']and peer['toolingSourceIndexSha256']==refs['toolingIndex']['sha256']
    assert peer['sourceOnly']is peer['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','bootstrapActionsInvoked']:assert peer[key]is False
    c.family(refs['toolingIndex']);sp,_=c.proof(refs['toolingSourceReview'])
    assert sp['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'and sp['toolingSourceIndexSha256']==refs['toolingIndex']['sha256']and sp['sourceOnly']is sp['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked']:assert sp[key]is False
    proof,candidate=export_gate(c,refs);tr=c.read(refs['toolingReferences'])
    assert str(Path(sys.executable).resolve())==refs['python']['path']
    assert len(c.read(refs['toolingInputs'])['files'])==241
    for source in [refs['toolingInputs'],tr['protectedInputLedger'],refs['exportInputLedger']]:
        data=c.read(source)
        for r in data['files']:c.file({k:r[k]for k in ['path','sha256','bytes']})
    receipt=c.read(tr['freezeReceipt']);assert len(receipt['copies'])==1902
    names={'normal-off-freeze-receipt.json'}|{local(str(Path(r['path']).relative_to(tr['frozenRoot'])))for r in receipt['copies']};assert len(names)==1903
    for r in receipt['copies']:
        frozen=Path(r['path']).stat();assert frozen.st_nlink==1
        if r['original']is not None:
            original=Path(r['original']).stat();assert(frozen.st_dev,frozen.st_ino)!=(original.st_dev,original.st_ino)
    exact_tree(Path(tr['frozenRoot']),names,True);c.families.append((Path(tr['frozenRoot']),names,True))
    normal=c.read(tr['normalProtection']);assert normal['originalReferenceEntries']==1387 and len(normal['requiredNormalFreezeMembership'])==1391
    c.families.append((Path(normal['freezeReceipt']['path']).parent,set(normal['requiredNormalFreezeMembership']),False))
    if phase=='derive-pins':
        for key in ['toolingBootstrapConfig','toolingBootstrapAuthority','reviewedPins','rootPinReview']:assert root[key]is None
    else:validate_tooling_bootstrap(c,root,refs,tr)
    c.recheck()
    return dict(capture=c,config=cfg,configRow=config_row,index=own,refs=refs,toolingRefs=tr,root=root,rootRow=root_row,candidate=candidate,proof=proof)


def fresh(paths):
    for p in paths:assert not Path(p).exists()and not Path(p).is_symlink()


def derive_pins(frame):
    refs=frame['refs'];c=frame['capture'];out=Path(refs['pinOutputRoot']);fresh([out]);c.recheck()
    # Root's NEW explicit derive-pins authority gates this pure original model.
    model=load_actual(refs['pinModelEntry'],'genuine_original_secret355_v3_pin_model_for_root_derivation')
    try:
        candidate=frame['candidate'];reviewed=model.reviewed_document(candidate);paths=four_pin_edits(candidate,reviewed)
        os.umask(0o077);out.mkdir(mode=0o700)
        pins=write(out/'reviewed-validation-pins.json',reviewed);assert c.read(pins)==reviewed
        review=c.read(refs['pinReviewTemplate']);review.update(state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex=refs['toolingIndex'],reviewedPins=pins,actualExportCandidate=refs['exportCandidate'],independentExportReview=refs['exportReview'])
        model.select_reviewed(reviewed,review,candidate['variants']['normal-off'],pins,refs['exportCandidate'],refs['exportReview'],frame['toolingRefs'])
        pin_review=write(out/'root-pin-review.json',review);assert c.read(pin_review)==review
        c.recheck()
        result=dict(schemaVersion=1,state='ROOT_DERIVED_SECRET355_VALIDATION_PIN_DATA_UNREVIEWED_V1',controllerIndex=frame['index'],rootAuthority=frame['rootRow'],config=frame['configRow'],reviewedPins=pins,rootPinReview=pin_review,changedPinPaths=paths,otherVariantsNull=True,validationBootstrapOnly=True,bootstrapExecuted=False,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
        print(json.dumps(write(out/'derivation-observation.json',result)),flush=True)
        return 0
    finally:c.recheck()


def bootstrap_js(frame):
    refs=frame['refs'];c=frame['capture'];out=Path(refs['observerOutputRoot']);external=Path(refs['observerExternalRoot'])
    fresh([out,external,refs['bootstrapOutputRoot'],refs['bootstrapExternalRoot'],refs['bootstrapJsRoot']]);c.recheck()
    monitor=load_actual(refs['monitorEntry'],'genuine_original_secret355_v3_js_outer_monitor')
    c.recheck();os.umask(0o077);out.mkdir(mode=0o700);external.mkdir(mode=0o700)
    identity=(out.stat().st_dev,out.stat().st_ino)
    owner=write(out/'owner.json',dict(schemaVersion=1,controllerIndex=frame['index'],rootAuthority=frame['rootRow'],config=frame['configRow'],outputRoot=str(out),outputIdentity=list(identity)))
    argv=[refs['node']['path'],str(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.mjs'),json.dumps(frame['configRow'],separators=(',',':')),json.dumps(owner,separators=(',',':'))]
    terminal=None;error=None;protection_error=None;protected=False;observer=None;raw_availability=None
    try:
        terminal=monitor.monitor(argv,str(REPO),dict(os.environ),external,1800,frame['rootRow'])
        raw=fingerprint(external/'terminal.json')[0];assert c.read(raw)==terminal
        for key in ['stdout','stderr']:c.file(terminal[key])
        write(out/'raw-terminal-observed.json',dict(schemaVersion=1,terminal=raw,stdout=terminal['stdout'],stderr=terminal['stderr'],interpretationPending=True))
        clean_terminal(terminal,frame['rootRow'])
        value=c.read(terminal['stdout']);observer=c.read(value['observation']);assert observer['state']=='SECRET355_JS_BOOTSTRAP_OBSERVED_UNREVIEWED_V1'
        assert observer['apiCalls']==observer['returnedRecheckCalls']==1 and observer['wholeDataEqualsPythonFrame']is True
        assert observer['engineExecuted']is observer['operationalAdmission']is observer['runtimeAcceptanceClaim']is False
    except BaseException as e:error=dict(type=type(e).__name__,scope='Actual streams/status retained; no accepted bootstrap on error')
    finally:
        try:c.recheck();protected=True
        except BaseException as e:protection_error=dict(type=type(e).__name__,scope='final or failure input protection')
    # A monitor/collector exception does not erase raw files it already wrote.
    # Record only actual available rows, with explicit missing names. Collection
    # or writer failure still propagates as failure; no blanket retention claim.
    if error is not None or protection_error is not None:
        available=[];missing=[]
        for name in ['stdout.log','stderr.log','terminal.json']:
            path=external/name
            if path.is_file()and not path.is_symlink():available.append(fingerprint(path)[0])
            else:missing.append(name)
        raw_availability=write(out/'raw-failure-availability.json',dict(schemaVersion=1,availableFiles=available,missingNames=missing,allExpectedRawFilesAvailable=not missing,semanticSuccess=False))
    assert out.is_dir()and not out.is_symlink()and(out.stat().st_dev,out.stat().st_ino)==identity
    passed=error is None and protection_error is None and protected and observer is not None
    result=dict(schemaVersion=1,state='ROOT_OBSERVED_SECRET355_JS_BOOTSTRAP_ZERO_UNREVIEWED_V1'if passed else'ROOT_OBSERVED_SECRET355_JS_BOOTSTRAP_FAILED_UNACCEPTED_V1',controllerIndex=frame['index'],rootAuthority=frame['rootRow'],config=frame['configRow'],rawTerminal=None if terminal is None else fingerprint(external/'terminal.json')[0],rawExitCode=None if terminal is None else terminal['rawExitCode'],observer=observer,error=error,protectionError=protection_error,rawFailureAvailability=raw_availability,sourceAndOriginalProtectionRechecked=protected,requiresIndependentActualReview=True,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    print(json.dumps(write(out/'root-observation.json',result)),flush=True)
    return 0 if passed else 1


def main():
    assert len(sys.argv)==3 and sys.argv[1]in ['derive-pins','bootstrap-js']
    frame=authorize(json.loads(sys.argv[2]),sys.argv[1])
    try:return derive_pins(frame)if sys.argv[1]=='derive-pins'else bootstrap_js(frame)
    finally:frame['capture'].recheck()

if __name__=='__main__':sys.exit(main())
