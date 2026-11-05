"""Dormant secret355 export/bootstrap CLI; standard-only authentication before custom imports."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,stat,sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v2'
VERIFIER=REPO/'tests/node-compat/foundation-crypto/ownership-secret-pin-tooling-candidate-v1'
BASE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v2')
TIMEOUT=600
SOURCE_PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V2'

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


def outputs(phase):
    assert phase in ('export','bootstrap')
    out=Path(str(BASE)+'-'+phase+'-normal-off');return out,Path(str(out)+'-external-root')


def validate_root(root,index,refs,phase):
    assert root['schemaVersion']==2 and root['state']=='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V2'
    assert root['phase']==phase and root['variant']=='normal-off' and root['toolingIndex']==index
    assert root['nativeSourceIndex']==refs['nativeSourceIndex'] and root['verifierSourceIndex']==refs['verifierSourceIndex']
    assert root['actualVerifierReview']==refs['actualVerifierReview'] and root['actualArtifactReview']==refs['actualArtifactReview']
    assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==11
    for key in ['engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','frozenRoot']:assert root[key]==refs[key]
    assert root['exportAllowed']is (phase=='export') and root['bootstrapAllowed']is (phase=='bootstrap')
    out,external=outputs(phase)
    assert root['outputRoot']==str(out) and root['externalOutputRoot']==str(external) and root['externalParentDeadlineSeconds']==TIMEOUT
    assert root['expectedCompleteVerifierCalls']==1 and root['jsOutputRoot']==(str(BASE)+'-bootstrap-js-normal-off' if phase=='bootstrap' else None)
    for key in ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:assert root[key]is False
    for key in ['runtimeAuthority','actualBootstrap']:assert root[key]is None
    if phase=='export':
        for key in ['actualExportCandidate','independentExportReview','reviewedPins','rootPinReview']:assert root[key]is None
    else:
        for key in ['actualExportCandidate','reviewedPins','rootPinReview']:descriptor(root[key])
        assert set(root['independentExportReview'])=={'index','result'}


def validate_source_peer(value,index,refs):
    assert value['schemaVersion']==1 and value['state']==SOURCE_PEER_STATE
    assert value['toolingSourceIndexSha256']==index['sha256'] and value['verifierSourceIndexSha256']==refs['verifierSourceIndex']['sha256']
    assert value['nativeSourceIndexSha256']==refs['nativeSourceIndex']['sha256'] and value['sourceOnly']is True and value['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked']:assert value[key]is False


def authenticate_actual_review(capture,refs):
    value,rows=capture.proof(refs['actualVerifierReview']);assert refs['actualVerifierContract']in rows
    contract=capture.read(refs['actualVerifierContract'])
    assert contract['requiredReviewState']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_RESULTS_REVIEW_PASSED_V1'
    assert value['schemaVersion']==1 and value['state']==contract['requiredReviewState']
    for key,expected in contract['requiredFixedValues'].items():assert value[key]==expected
    for key,expected in contract['requiredExactDescriptors'].items():assert value[key]==expected
    assert value['coverage']==contract['requiredCoverage']
    assert value['actualWholeFrame']==refs['actualVerifierWholeFrame'] and value['inputClosure']==refs['protectedInputLedger']
    assert value['actualFrozenArtifactReview']==refs['actualArtifactReview'] and value['verifierSourceIndex']==refs['verifierSourceIndex']
    assert value['nativeSourceIndex']==refs['nativeSourceIndex'] and value['freezerSourceIndex']==refs['freezerSourceIndex']
    assert value['engine']==refs['engine'] and value['metadata']==refs['metadata'] and value['freezeReceipt']==refs['freezeReceipt']
    return value


def authorize(config_row,phase):
    """All custom code is loaded only after complete fixed protection is captured."""
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert Path(__file__).resolve().parent==OWN
    assert not any(os.environ.get(k) for k in ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])
    capture=Capture();config_row=descriptor(config_row);config=capture.read(config_row)
    assert config['schemaVersion']==2 and config['state']=='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V2' and config['phase']==phase
    index=descriptor(config['toolingIndex']);assert index['path']==str(OWN/'index.json')
    own=capture.family(index);refs=capture.read(next(r for r in own if r['path']==str(OWN/'references.json')))
    assert refs['schemaVersion']==2 and refs['originalToolingRoot']==str(OWN)
    root_row=descriptor(config['rootAuthority']);root=capture.read(root_row);validate_root(root,index,refs,phase)
    for item in refs['families']:capture.family(item)
    source_peer,_=capture.proof(root['sourceIndependentReview']);validate_source_peer(source_peer,index,refs)
    actual=authenticate_actual_review(capture,refs)
    ledger=capture.read(refs['protectedInputLedger']);assert len(ledger['files'])==refs['protectedInputRows']==27729
    for item in ledger['files']:capture.file({k:item[k] for k in ['path','sha256','bytes']})
    # Reopen exact original/configured/build inputs for preservation, separate
    # from the original verifier's FROZEN-only payload read scope.
    normal=capture.read(refs['normalProtection']);assert normal['originalReferenceEntries']==1387
    capture.file(normal['freezeReceipt'])
    for item in normal['frozenCopyEntries']:capture.file({k:item[k] for k in ['path','sha256','bytes']})
    for item in normal['originals']:capture.file(item['original']);capture.file(item['frozen'])
    assert len(normal['requiredNormalFreezeMembership'])==1391
    capture.families.append((Path(normal['freezeReceipt']['path']).parent,set(normal['requiredNormalFreezeMembership']),False))
    c=capture.read(refs['verifierContract']);receipt=capture.read(refs['freezeReceipt']);historical=capture.read(refs['actualVerifierWholeFrame'])
    assert c['originalToolingRoot']==str(VERIFIER) and c['engine']==refs['engine'] and c['metadata']==refs['metadata']
    names={'normal-off-freeze-receipt.json'}
    assert len(receipt['copies'])==1902 and sum(r['original']is not None for r in receipt['copies'])==1899
    for item in receipt['copies']:
        p=Path(item['path']);assert p.is_relative_to(Path(refs['frozenRoot']));names.add(local(str(p.relative_to(refs['frozenRoot']))))
        capture.file({k:item[k] for k in ['path','sha256','bytes']})
        assert p.stat().st_nlink==1
        if item['original']is not None:
            capture.file(dict(path=item['original'],sha256=item['sha256'],bytes=item['bytes']))
            original=Path(item['original']).stat();frozen=p.stat();assert (original.st_dev,original.st_ino)!=(frozen.st_dev,frozen.st_ino)
    capture.families.append((Path(refs['frozenRoot']),names,True));assert len(names)==1903
    for key in ['verifierEntry','monitorEntry','node','python']:capture.file(refs[key])
    assert refs['verifierEntry']in capture.family(refs['verifierSourceIndex']) and refs['monitorEntry']in capture.family(refs['monitorIndex'])
    assert refs['python']['path']==str(Path(sys.executable).resolve())
    frame=dict(config=config,configRow=config_row,index=index,own=own,root=root,rootRow=root_row,refs=refs,capture=capture,contract=c,receipt=receipt,historical=historical,phase=phase)
    # Bootstrap review and pin gates also precede ANY custom module import.
    if phase=='bootstrap':
        proof,_=capture.proof(root['independentExportReview'])
        assert proof['schemaVersion']==2 and proof['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V2' and proof['verifiedPassed']is True
        assert proof['toolingSourceIndexSha256']==index['sha256'] and proof['candidate']==root['actualExportCandidate']
        assert proof['actualVerifierReview']==refs['actualVerifierReview'] and proof['freezeReceipt']==refs['freezeReceipt']
        assert proof['variant']=='normal-off' and type(proof['rawExporterExitCode'])is int and proof['rawExporterExitCode']==0
        assert proof['nativeSourceFiles']==355 and proof['externalEmbeddingSources']==3 and proof['selectedManifestCount']==11
        for key in ['engine','metadata','nativeSourceIndex','freezerSourceIndex','verifierSourceIndex']:assert proof[key]==refs[key]
        assert proof['allObservedOwnedGroupsGone']is True and proof['wholeCandidateAndRawJSONEqual']is True and proof['otherVariantsNull']is True
        for key in ['rootAuthority','config','controllerObservation','externalTerminal','wholeVerifierFrame']:capture.file(proof[key])
        for key in ['engineExecuted','bootstrapExecuted','operationalAdmission','runtimeAcceptanceClaim']:assert proof[key]is False
        for key in ['actualExportCandidate','reviewedPins','rootPinReview']:capture.read(root[key])
    capture.recheck()
    try:
        model=load_actual(next(r for r in own if r['path']==str(OWN/'pin_model.py')),'secret355_artifact_pin_data_v2')
        frame['model']=model;frame['expected']=model.candidate(historical,receipt,refs,index)
        if phase=='bootstrap':
            assert capture.read(root['actualExportCandidate'])==model.unreviewed_document(frame['expected'])
            frame['reviewedPin']=model.select_reviewed(capture.read(root['reviewedPins']),capture.read(root['rootPinReview']),frame['expected'],root['reviewedPins'],root['actualExportCandidate'],root['independentExportReview'],refs)
        return frame
    finally:capture.recheck()


def write(path,value):
    path=Path(path);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return fingerprint(path)[0]


def worker(frame):
    phase=frame['phase'];out,_=outputs(phase);assert out.is_dir()and not out.is_symlink()and stat.S_IMODE(out.stat().st_mode)==0o700
    helper=load_actual(frame['refs']['verifierEntry'],'genuine_original_secret355_artifact_verifier_v2')
    assert helper.HERE==VERIFIER and str(helper.FROZEN)==frame['refs']['frozenRoot']
    frame['capture'].recheck()
    verified=helper.verify_frozen(frame['contract'])
    # Full actual helper return is durable BEFORE equality/model checks.
    write(out/'whole-verifier-frame.json',verified)
    assert verified==frame['historical'],'Whole unchanged metadata/manifests/contexts must agree with actual reviewed verifier DATA'
    model=frame['model'];pin=model.candidate(verified,frame['receipt'],frame['refs'],frame['index'])
    assert pin==frame['expected']
    if phase=='export':value=model.unreviewed_document(pin);name='candidate-UNREVIEWED.json'
    else:
        root=frame['root'];value=model.bootstrap_frame(frame['reviewedPin'],verified,frame['refs'],frame['index'],frame['rootRow'],frame['configRow'],root['reviewedPins'],root['rootPinReview'],root['actualExportCandidate'],root['independentExportReview']);name='bootstrap-frame.json'
    write(out/name,value)
    print(json.dumps(value,allow_nan=False),flush=True)


def parent(frame):
    out,external=outputs(frame['phase'])
    assert not out.exists()and not out.is_symlink()and not external.exists()and not external.is_symlink()
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_original_secret355_artifact_owned_monitor_v2')
    frame['capture'].recheck();os.umask(0o077);out.mkdir(mode=0o700);external.mkdir(mode=0o700);identity=(out.stat().st_dev,out.stat().st_ino)
    argv=[frame['refs']['python']['path'],'-B','-I',str(OWN/'artifact_tooling.py'),'worker',frame['phase'],'--config-descriptor',json.dumps(frame['configRow'],separators=(',',':'))]
    terminal=None;value=None;errors=[];protected=False;row=None
    try:
        terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},external,TIMEOUT,frame['rootRow'])
        terminal_row=fingerprint(external/'terminal.json')[0]
        assert frame['capture'].read(terminal_row)==terminal
        for key in ['stdout','stderr']:assert fingerprint(terminal[key]['path'])[0]==terminal[key]
        write(out/'raw-terminal-observed.json',dict(schemaVersion=2,terminal=terminal_row,stdout=terminal['stdout'],stderr=terminal['stderr'],interpretationPending=True))
        clean_terminal(terminal,frame['rootRow']);assert terminal['stdout']['bytes']<=16*1024*1024
        value=json.loads(Path(terminal['stdout']['path']).read_bytes());name='candidate-UNREVIEWED.json' if frame['phase']=='export' else 'bootstrap-frame.json'
        row=fingerprint(out/name)[0];retained=frame['capture'].read(row);assert value==retained
        whole=frame['capture'].read(fingerprint(out/'whole-verifier-frame.json')[0]);assert whole==frame['historical']
        if frame['phase']=='export':assert value==frame['model'].unreviewed_document(frame['expected'])
        else:
            r=frame['root'];assert value==frame['model'].bootstrap_frame(frame['reviewedPin'],whole,frame['refs'],frame['index'],frame['rootRow'],frame['configRow'],r['reviewedPins'],r['rootPinReview'],r['actualExportCandidate'],r['independentExportReview'])
    except BaseException as error:errors.append(dict(stage='owned-phase-or-whole-return',type=type(error).__name__,rawFilesPreserved=True,completeEvidenceRequiresFileReview=True))
    finally:
        try:frame['capture'].recheck();protected=True
        except BaseException as error:errors.append(dict(stage='final-or-failure-protection',type=type(error).__name__))
    assert out.is_dir()and not out.is_symlink()and (out.stat().st_dev,out.stat().st_ino)==identity
    success=value is not None and protected and errors==[]
    result=dict(schemaVersion=2,state='SECRET_OWNER355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V2' if success else 'SECRET_OWNER355_ARTIFACT_PHASE_FAILED_UNACCEPTED_V2',
        phase=frame['phase'],toolingIndex=frame['index'],rootAuthority=frame['rootRow'],config=frame['configRow'],actualVerifierReview=frame['refs']['actualVerifierReview'],
        rawTerminal=None if terminal is None else fingerprint(external/'terminal.json')[0],rawExitCode=None if terminal is None else terminal['rawExitCode'],
        completePhaseReturn=row,wholeVerifierFrame=None if not(out/'whole-verifier-frame.json').exists()else fingerprint(out/'whole-verifier-frame.json')[0],
        sourceAndOriginalProtectionRechecked=protected,errors=errors,requiresIndependentActualReview=True,engineExecuted=False,guestExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False)
    observation=write(out/'controller-observation.json',result);print(json.dumps(dict(observation=observation,completeUnreviewed=success)),flush=True)
    return 0 if success else 1


def main():
    assert Path(__file__).resolve().parent==OWN and len(sys.argv)==5 and sys.argv[1]in ['parent','worker'] and sys.argv[2]in ['export','bootstrap'] and sys.argv[3]=='--config-descriptor'
    frame=authorize(json.loads(sys.argv[4]),sys.argv[2])
    try:
        if sys.argv[1]=='parent':return parent(frame)
        worker(frame);return 0
    finally:frame['capture'].recheck()


if __name__=='__main__':sys.exit(main())

