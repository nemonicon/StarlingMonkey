"""Dormant original-context read-only verifier parent/worker; stdlib bootstrap."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-verifier-controller-candidate-v1'
VERIFIER=REPO/'tests/node-compat/foundation-crypto/ownership-secret-pin-tooling-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1')
EXTERNAL=Path(str(OUT)+'-external-root')
TIMEOUT=600
VERIFIER_SHA='e8726a1c416afc48303faa1fd25dabed6a71872d6a65ae5ac438e2685aceb7ad'


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


def validate_root(root,index,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SECRET_OWNER355_FROZEN_VERIFIER_READ_ONLY_V1'
    assert root['phase']=='verify-frozen-read-only'and root['variant']=='normal-off'and root['verifierReadOnlyAllowed']is True
    assert root['controllerIndex']==index and index['path']==str(OWN/'index.json')and root['controllerEntry']['path']==str(OWN/'controller.py')
    for key in['verifierSourceIndex','verifierSourceReview','verifierContract','verifierEntry','actualArtifactReview','actualArtifactContract','nativeSourceIndex','freezerSourceIndex','engine','metadata','freezeReceipt','frozenRoot']:assert root[key]==refs[key]
    assert root['verifierSourceIndex']['sha256']==VERIFIER_SHA and root['verifierEntry']['path']==str(VERIFIER/'verifier.py')and root['verifierContract']['path']==str(VERIFIER/'source-contract.json')
    assert root['outputRoot']==str(OUT)and root['externalOutputRoot']==str(EXTERNAL)and root['externalParentDeadlineSeconds']==TIMEOUT and root['expectedVerifierCalls']==1
    for k in['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','ownerHelperAllowed','nodeAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','exportAllowed','bootstrapAllowed','componentAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed','sourcePromotionAllowed','timingAllowed']:assert root[k]is False
    for k in['actualVerifierResult','independentActualVerifierReview','actualExport','reviewedPins','actualBootstrap','runtimeAuthority']:assert root[k]is None


def validate_peer(value,index):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==index['sha256']and value['verifierSourceIndexSha256']==VERIFIER_SHA and value['sourceOnly']is True and value['sourceReviewPassed']is True
    for k in['ownerActionsInvoked','hostActionsInvoked','verifierActionsInvoked']:assert value[k]is False


def expected_frame(c,metadata,manifests):
    """Pure whole-value model. Never alter metadata or original context fields."""
    assert len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==len(manifests)==11
    return dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_BYTES_AND_METADATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',nativeSourceIndex=c['nativeSourceIndex'],freezerSourceIndex=c['freezerSourceIndex'],engine=c['engine'],metadataDescriptor=c['metadata'],freezeReceipt=c['freezeReceipt'],metadata=metadata,selectedManifests=manifests,selectedManifestPaths=[r['path']for r in metadata['selectedModuleManifests']],configuredSourceRoot=c['configuredSourceRoot'],sourceRoot=c['frozenSourceRoot'],componentizeSourceRoot=c['componentizeSourceRoot'],workRoot=c['workRoot'],freezerOriginalToolingRoot=c['freezerOriginalToolingRoot'],verifierOriginalToolingRoot=c['originalToolingRoot'],frozenFilesVerified=1902,frozenMembership=1903,originalReferenceCountAsData=1899,originalReferencesReopened=False,commands=dict(databaseRows=68,policyCpp=62,otherConfigured=5,generatedNull=1,strictCpp=4,privateCpp=6,embeddingSeparate=1,secretCpp=2),registryModuleExecuted=False,allOriginalSdkOrArchivesCopied=False,buildSemanticProvenance=c['actualBuildReview'],actualFrozenArtifactReview=c['actualArtifactReview'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)


def clean_terminal(t,authority):
    assert type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and t['timeout']is False and t['forcedCleanup']is False
    for k in['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['finalGroups']and all(r['alive']is False for r in t['finalGroups'])and t['stderr']['bytes']==0


def validate_retained_frame(value,retained,c,metadata,manifests):
    assert type(value)is dict and value==retained,'Whole stdout JSON must equal the complete saved return'
    assert value==expected_frame(c,metadata,manifests),'Whole returned frame must match genuine unchanged metadata/manifests/context roles'


def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert not any(os.environ.get(k)for k in['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])
    capture=Capture();config=capture.read(config_row);assert config['schemaVersion']==1 and config['state']=='SECRET_OWNER355_VERIFIER_CONTROLLER_CONFIG_V1'
    index=config['controllerIndex'];assert index['path']==str(OWN/'index.json');own=capture.family(index)
    refs=capture.read(next(r for r in own if r['path']==str(OWN/'references.json')));root=capture.read(config['rootAuthority']);validate_root(root,index,refs);assert root['controllerEntry']in own
    for f in refs['families']:capture.family(f['index'])
    source_peer,_=capture.proof(refs['verifierSourceReview'])
    assert source_peer['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_PASSED_V1'and source_peer['verifierSourceIndexSha256']==VERIFIER_SHA and source_peer['sourceOnly']is source_peer['sourceReviewPassed']is True
    for k in['ownerActionsInvoked','verifierHelpersInvoked','exportOrBootstrapInvoked']:assert source_peer[k]is False
    own_peer,_=capture.proof(root['controllerIndependentReview']);validate_peer(own_peer,index)
    c=capture.read(refs['verifierContract']);assert c['nativeSourceIndex']==refs['nativeSourceIndex']and c['freezerSourceIndex']==refs['freezerSourceIndex']and c['actualArtifactReview']==refs['actualArtifactReview']
    assert c['originalToolingRoot']==str(VERIFIER)and c['frozenRoot']==refs['frozenRoot']and c['engine']==refs['engine']and c['metadata']==refs['metadata']and c['freezeReceipt']==refs['freezeReceipt']
    artifact,rows=capture.proof(refs['actualArtifactReview']);assert refs['actualArtifactContract']in rows
    contract=capture.read(refs['actualArtifactContract']);assert artifact['state']==contract['requiredReviewState']and artifact['verifiedPassed']is True
    for k,v in contract['requiredFixedValues'].items():assert artifact[k]==v
    for k,v in contract['requiredExactDescriptors'].items():assert artifact['artifacts'][k]==v
    assert artifact['artifacts']==contract['artifacts']and artifact['coverage']==contract['requiredCoverage']
    source_inputs=capture.read(refs['verifierSourceInputs'])
    for r in source_inputs['files']:capture.file(r)
    assert source_inputs['artifactProofLedger']==refs['artifactInputLedger']
    ledger=capture.read(refs['artifactInputLedger'])
    for r in ledger['files']:capture.file(r)
    # Preservation is a separate caller responsibility; it opens original DATA.
    # The complete helper's own payload reads remain FROZEN-only by source flow.
    normal=capture.read(refs['normalProtection']);assert normal['originalReferenceEntries']==1387 and len(normal['requiredNormalFreezeMembership'])==1391
    capture.file(normal['freezeReceipt'])
    for r in normal['frozenCopyEntries']:capture.file({k:r[k]for k in['path','sha256','bytes']})
    for r in normal['originals']:capture.file(r['original']);capture.file(r['frozen'])
    capture.families.append((Path(normal['freezeReceipt']['path']).parent,set(normal['requiredNormalFreezeMembership']),False))
    receipt=capture.read(refs['freezeReceipt']);assert len(receipt['copies'])==1902 and sum(r['original']is not None for r in receipt['copies'])==1899
    frozen_names={'normal-off-freeze-receipt.json'}
    for r in receipt['copies']:
        path=Path(r['path']);assert path.is_relative_to(Path(c['frozenRoot']));frozen_names.add(local(str(path.relative_to(c['frozenRoot']))));capture.file({k:r[k]for k in['path','sha256','bytes']})
        if r['original']is not None:capture.file(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    capture.families.append((Path(c['frozenRoot']),frozen_names,True))
    for key in['verifierEntry','monitorEntry']:capture.file(refs[key])
    assert refs['verifierEntry']in capture.family(refs['verifierSourceIndex'])and refs['monitorEntry']in capture.family(refs['monitorIndex'])
    capture.recheck()
    return dict(config=config,configRow=config_row,root=root,rootRow=config['rootAuthority'],refs=refs,contract=c,capture=capture,receipt=receipt)


def load_actual(row,name):
    actual,_,_=fingerprint(row['path']);assert actual==row
    spec=importlib.util.spec_from_file_location(name,row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def write(path,value):
    with Path(path).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return fingerprint(path)[0]


def worker(frame):
    assert OUT.is_dir()and not OUT.is_symlink()and stat.S_IMODE(OUT.stat().st_mode)==0o700
    assert not(OUT/'whole-frame.json').exists()
    helper=load_actual(frame['refs']['verifierEntry'],'actual_original_secret355_frozen_verifier')
    assert helper.HERE==VERIFIER and str(helper.FROZEN)==frame['contract']['frozenRoot']
    frame['capture'].recheck()
    # Exactly one real verifier call, only in a separately authorized worker.
    value=helper.verify_frozen(frame['contract'])
    # Retain the complete return before any success/model assertion.
    write(OUT/'whole-frame.json',value)
    print(json.dumps(value),flush=True)


def parent(frame):
    assert not OUT.exists()and not OUT.is_symlink()and not EXTERNAL.exists()and not EXTERNAL.is_symlink()
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_original_secret355_verifier_owned_monitor');frame['capture'].recheck()
    os.umask(0o077)  # Only this fresh caller and its child; no user/global path change.
    OUT.mkdir(mode=0o700);EXTERNAL.mkdir(mode=0o700);identity=(OUT.stat().st_dev,OUT.stat().st_ino)
    argv=[sys.executable,'-B','-I',str(OWN/'controller.py'),'worker',json.dumps(frame['configRow'],separators=(',',':'))]
    terminal=None;observed=None;errors=[];protected=False
    try:
        terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},EXTERNAL,TIMEOUT,frame['rootRow'])
        terminal_row=fingerprint(EXTERNAL/'terminal.json')[0]
        assert frame['capture'].read(terminal_row)==terminal,'Durable raw terminal must equal the genuine monitor return'
        for key in['stdout','stderr']:assert fingerprint(terminal[key]['path'])[0]==terminal[key]
        write(OUT/'raw-terminal-observed.json',dict(schemaVersion=1,terminal=terminal_row,stdout=terminal['stdout'],stderr=terminal['stderr'],interpretationPending=True))
        clean_terminal(terminal,frame['rootRow'])
        assert terminal['stdout']['bytes']<=16*1024*1024
        raw=Path(terminal['stdout']['path']).read_bytes();value=json.loads(raw)
        retained=frame['capture'].read(fingerprint(OUT/'whole-frame.json')[0])
        c=frame['contract'];metadata=frame['capture'].read(c['metadata']);copies={r['path']:r for r in frame['receipt']['copies']};manifests=[]
        for r in metadata['selectedModuleManifests']:
            target=str(Path(c['frozenSourceRoot'])/local(r['path']));copy=copies[target];assert copy['sha256']==r['sha256']
            manifests.append(frame['capture'].read({k:copy[k]for k in['path','sha256','bytes']}))
        validate_retained_frame(value,retained,c,metadata,manifests)
        observed=dict(fullReturnedFrame=fingerprint(OUT/'whole-frame.json')[0],rawStdout=terminal['stdout'],wholeStdoutAndSavedFrameJsonEqual=True,wholeFrameModelPassed=True,helperCalls=1,helperPayloadReadScope='FROZEN only by reviewed e872 source flow',helperOriginalReferencesReopened=False,callerSourceAndOriginalPreservationReadsSeparate=True,syscallIsolationObserved=False,engineExecuted=False)
    except BaseException as error:errors.append(dict(stage='monitor-or-full-frame-collection',type=type(error).__name__,rawEvidenceLocationsUnchanged=True,completeEvidenceRequiresFileReview=True))
    finally:
        try:frame['capture'].recheck();protected=True
        except BaseException as error:errors.append(dict(stage='final-or-failure-protection',type=type(error).__name__))
    assert OUT.is_dir()and not OUT.is_symlink()and(OUT.stat().st_dev,OUT.stat().st_ino)==identity
    success=observed is not None and protected and errors==[]
    result=dict(schemaVersion=1,state='ROOT_OBSERVED_SECRET_OWNER355_FROZEN_VERIFIER_RAW_ZERO_UNREVIEWED_V1'if success else'ROOT_OBSERVED_SECRET_OWNER355_FROZEN_VERIFIER_FAILED_UNACCEPTED_V1',controllerIndex=frame['config']['controllerIndex'],rootAuthority=frame['rootRow'],config=frame['configRow'],verifierSourceIndex=frame['refs']['verifierSourceIndex'],verifierSourceReview=frame['refs']['verifierSourceReview'],actualArtifactReview=frame['refs']['actualArtifactReview'],rawTerminal=None if terminal is None else fingerprint(EXTERNAL/'terminal.json')[0],rawExitCode=None if terminal is None else terminal['rawExitCode'],observation=observed,errors=errors,sourceAndOriginalProtectionRechecked=protected,independentActualVerifierReview=None,actualExport=None,reviewedPins=None,actualBootstrap=None,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsAnyActionAuthority=False)
    row=write(OUT/'controller-observation.json',result);print(json.dumps(dict(observation=row,completeUnreviewed=success)),flush=True)
    return 0 if success else 1


def main():
    assert Path(__file__).resolve().parent==OWN and len(sys.argv)==3 and sys.argv[1]in('parent','worker')
    frame=authorize(json.loads(sys.argv[2]))
    try:
        if sys.argv[1]=='parent':return parent(frame)
        worker(frame);return 0
    finally:frame['capture'].recheck()


if __name__=='__main__':sys.exit(main())
