"""Dormant combined355 full80 export/bootstrap. Stdlib guard before imports."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-artifact-tooling-candidate-v1'
BASE=Path('/private/tmp/starling-node-compat/combined-native355-artifact-tooling-v1')
TIMEOUT=600
SOURCE_PEER_STATE='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1'
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
    def __init__(self):self.rows={};self.families=[];self.checks=[]
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
        for check in self.checks:check()

def clean_terminal(t,authority):
    assert type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and t['timeout']is False and t['forcedCleanup']is False
    for k in['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['finalGroups']and all(r['alive']is False for r in t['finalGroups'])and t['stderr']['bytes']==0

def load_actual(row,name):
    actual,_,_=fingerprint(row['path']);assert actual==row
    spec=importlib.util.spec_from_file_location(name,row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def outputs(phase):
 assert phase in ('export','bootstrap');root=Path(str(BASE)+'-'+phase+'-normal-off');return root,Path(str(root)+'-external-root')

def frozen_proof(c,refs):
 proof,rows=c.proof(refs['actualFrozenReview']);assert refs['actualFrozenContract'] in rows
 contract=c.read(refs['actualFrozenContract']);assert contract['requiredReviewState']=='INDEPENDENT_COMBINED355_NATIVE_FREEZE_V2_RESULTS_REVIEW_PASSED_V1'
 for key,value in contract['requiredFixedValues'].items():assert proof[key]==value,key
 for key,value in contract['requiredExactDescriptors'].items():assert proof[key]==value,key
 assert proof['coverage']==contract['requiredCoverage']
 for key in ('engine','metadata','freezeReceipt','nativeSourceIndex','freezerSourceIndex','retryBuildControllerIndex'):assert proof[key]==refs[key]
 assert proof['inputHashes']==refs['compactInputBoundary'] and proof['frozenCopyInventory']==refs['frozenCopyInventory']
 return proof

def protected_tree(row):
 root=Path(row['root']);assert root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==row['mode']
 files=set();links={}
 for path in root.rglob('*'):
  name=path.relative_to(root).as_posix()
  if path.is_symlink():links[name]=os.readlink(path)
  elif path.is_file():files.add(name)
 assert files==set(row['files']) and links==row['links']

def protect(c,refs):
 compact=c.read(refs['compactInputBoundary']);assert compact['schemaVersion']==1 and len(compact['files'])==2618 and compact['historicalTreesRecopied'] is False
 assert compact['reviewedBuildInputLedger']==refs['reviewedBuildInputLedger'] and compact['reviewedBuildReferencesRehashed']==20816
 for row in compact['files']:c.file(row)
 ledger=c.read(refs['reviewedBuildInputLedger']);assert len(ledger['files'])==20816
 for row in ledger['files']:c.file(row)
 assert compact['reviewedInheritedFamilies']==refs['inheritedFamilies']
 for ix in refs['inheritedFamilies']:c.family(ix)
 # Frozen ownership and exact original-copy references are current scoped DATA,
 # not a recursive walk through arbitrary historical descriptor dictionaries.
 inv=c.read(refs['frozenCopyInventory']);assert len(inv['files'])==2596 and inv['wholeMembershipFiles']==2597
 names={Path(refs['freezeReceipt']['path']).name}
 for row in inv['files']:
  name=local(str(Path(row['copy']['path']).relative_to(refs['frozenRoot'])));assert name not in names;names.add(name)
  c.file(row['copy']);s=Path(row['copy']['path']).stat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  if row['original'] is not None:
   c.file(row['original']);a=Path(row['original']['path']).stat();assert (s.st_dev,s.st_ino)!=(a.st_dev,a.st_ino)
 assert len(names)==2597;c.families.append((Path(refs['frozenRoot']),names,True))
 protection=c.read(refs['freezerProtection'])
 for row in protection['files']:
  c.file(row['descriptor']);s=Path(row['descriptor']['path']).stat();assert stat.S_IMODE(s.st_mode)==row['mode'] and s.st_nlink==row['nlink']
 for row in protection['modePairs']:
  c.file(row['copy']);c.file(row['original']);a,b=Path(row['copy']['path']).stat(),Path(row['original']['path']).stat();assert stat.S_IMODE(a.st_mode)==row['copyMode'] and stat.S_IMODE(b.st_mode)==row['originalMode'] and (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 for row in protection['trees']:
  protected_tree(row);c.checks.append(lambda row=row:protected_tree(row))
 aliases=c.read(refs['referenceAliasWitness'])
 def reference_checks():
  for row in aliases['symlinks']:
   p=Path(row['path']);assert p.is_symlink() and os.readlink(p)==row['linkText'] and str(p.resolve(strict=True))==row['resolved']
  for row in aliases['archiveHardlinks']:
   a,b=Path(row['path']).stat(),Path(row['target']).stat();assert (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino) and row['sameInode'] is True
  for row in protection['trees']:assert stat.S_IMODE(Path(row['root']).stat().st_mode)==row['mode']
 reference_checks();c.checks.append(reference_checks)


def validate_root(root,index,refs,phase):
 assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_ARTIFACT_PHASE_V1' and root['phase']==phase and root['toolingIndex']==index and root['variant']=='normal-off'
 assert root['actualFrozenReview']==refs['actualFrozenReview'] and root['nativeSourceIndex']==refs['nativeSourceIndex'] and root['freezerSourceIndex']==refs['freezerSourceIndex']
 for key in ('engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','workRoot'):assert root[key]==refs[key]
 assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==11 and root['fullMetadataFields']==80
 assert root['exportAllowed'] is (phase=='export') and root['bootstrapAllowed'] is (phase=='bootstrap') and root['frozenReadOnlyVerifierAllowed'] is True
 out,external=outputs(phase);assert root['outputRoot']==str(out) and root['externalOutputRoot']==str(external) and root['externalParentDeadlineSeconds']==TIMEOUT and root['expectedFrozenVerifierCalls']==1
 for key in ('nativeBuildAllowed','nativeFreezeAllowed','ninjaAllowed','gcReconfigureAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','sourcePromotionAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'):assert root[key] is False
 assert root['actualBootstrapReview'] is root['runtimeAuthority'] is None
 if phase=='export':
  for key in ('actualExportCandidate','independentExportReview','reviewedPins','rootPinReview'):assert root[key] is None
 else:
  for key in ('actualExportCandidate','reviewedPins','rootPinReview'):descriptor(root[key])
  assert set(root['independentExportReview'])=={'index','result'}


def authorize(config_row,phase):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and Path(__file__).resolve().parent==OWN
 for key in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'):assert not os.environ.get(key)
 c=Capture();config_row=descriptor(config_row);cfg=c.read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='COMBINED355_NATIVE_ARTIFACT_CONFIG_V1' and cfg['phase']==phase
 index=descriptor(cfg['toolingIndex']);assert index['path']==str(OWN/'index.json');own=c.family(index);refs=c.read(next(r for r in own if r['path']==str(OWN/'references.json')))
 root_row=descriptor(cfg['rootAuthority']);root=c.read(root_row);validate_root(root,index,refs,phase)
 for r in c.read(next(r for r in own if r['path']==str(OWN/'source-inputs.json')))['files']:c.file(r)
 peer,_=c.proof(root['sourceIndependentReview']);assert peer['schemaVersion']==1 and peer['state']==SOURCE_PEER_STATE and peer['toolingSourceIndexSha256']==index['sha256']
 assert peer['nativeSourceIndexSha256']==refs['nativeSourceIndex']['sha256'] and peer['freezerSourceIndexSha256']==refs['freezerSourceIndex']['sha256'] and peer['sourceOnly'] is peer['sourceReviewPassed'] is True
 for key in ('ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked'):assert peer[key] is False
 frozen_proof(c,refs);protect(c,refs)
 # The active executing verifier Source is authenticated separately from its
 # frozen payload. Its own __file__ self-auth path is genuine, never rebound.
 assert refs['activeVerifier'] in c.family(refs['freezerSourceIndex'])
 assert refs['monitorEntry'] in c.family(refs['monitorIndex'])
 for key in ('activeVerifier','monitorEntry','python'):c.file(refs[key])
 assert refs['python']['path']==str(Path(sys.executable).resolve())
 receipt=c.read(refs['freezeReceipt']);metadata=c.read(refs['metadata']);capsule=c.read(refs['historicalVerifierCapsule'])
 manifests=[]
 for row in metadata['selectedModuleManifests']:
  path=Path(refs['frozenSourceRoot'])/row['path'];manifests.append(c.read(dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size)))
 if phase=='bootstrap':
  exported,_=c.proof(root['independentExportReview']);assert exported['schemaVersion']==1 and exported['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V1' and exported['verifiedPassed'] is True
  assert exported['toolingSourceIndexSha256']==index['sha256'] and exported['candidate']==root['actualExportCandidate'] and exported['actualFrozenReview']==refs['actualFrozenReview']
  assert exported['rawExporterExitCode']==0 and exported['allObservedOwnedGroupsGone'] is True and exported['wholeCandidateAndRawJsonEqual'] is True and exported['otherVariantsNull'] is True
  for key in ('engineExecuted','bootstrapExecuted','operationalAdmission','runtimeAcceptanceClaim'):assert exported[key] is False
  for key in ('actualExportCandidate','reviewedPins','rootPinReview'):c.read(root[key])
 c.recheck()
 try:
  model=load_actual(next(r for r in own if r['path']==str(OWN/'pin_model.py')),'combined355_full80_pin_data_model')
  native=model.native_frame(capsule,receipt,metadata,manifests,refs,index);expected=model.candidate(native,receipt,refs,index)
  pin=None
  if phase=='bootstrap':
   assert c.read(root['actualExportCandidate'])==model.unreviewed_document(expected)
   pin=model.select_reviewed(c.read(root['reviewedPins']),c.read(root['rootPinReview']),expected,root,refs,index)
  return dict(capture=c,configRow=config_row,config=cfg,index=index,own=own,refs=refs,root=root,rootRow=root_row,phase=phase,receipt=receipt,metadata=metadata,manifests=manifests,capsule=capsule,model=model,native=native,expected=expected,pin=pin)
 finally:c.recheck()


def write(path,value):
 path=Path(path);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(parent)
 finally:os.close(parent)
 return fingerprint(path)[0]


def worker(f):
 out,_=outputs(f['phase']);assert out.is_dir() and not out.is_symlink() and stat.S_IMODE(out.stat().st_mode)==0o700
 helper=load_actual(f['refs']['activeVerifier'],'genuine_original_combined355_frozen_verifier')
 assert Path(helper.__file__).resolve()==Path(f['refs']['activeVerifier']['path']) and helper.FREEZE==Path(f['refs']['frozenRoot'])
 f['capture'].recheck();verified=helper.verify_frozen(f['refs']['freezeReceipt'],f['refs']['freezerSourceIndex']['sha256'])
 write(out/'whole-verifier-capsule.json',verified);assert verified==f['capsule']
 native=f['model'].native_frame(verified,f['receipt'],f['metadata'],f['manifests'],f['refs'],f['index']);write(out/'native-frame.json',native);assert native==f['native']
 pin=f['model'].candidate(native,f['receipt'],f['refs'],f['index']);assert pin==f['expected']
 if f['phase']=='export':value=f['model'].unreviewed_document(pin);name='candidate-UNREVIEWED.json'
 else:value=f['model'].bootstrap_frame(f['pin'],native,f['refs'],f['index'],f['rootRow'],f['configRow'],f['root']);name='bootstrap-frame.json'
 write(out/name,value);print(json.dumps(value,allow_nan=False),flush=True)


def parent(f):
 out,external=outputs(f['phase']);assert not out.exists() and not out.is_symlink() and not external.exists() and not external.is_symlink()
 for q in (out,external,*out.parents,*external.parents):assert not q.is_symlink()
 monitor=load_actual(f['refs']['monitorEntry'],'genuine0af_combined355_artifact_monitor');f['capture'].recheck();os.umask(0o077);out.mkdir(mode=0o700);external.mkdir(mode=0o700)
 fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
 def same_root():
  s=out.lstat();held=os.fstat(fd);assert stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode)==0o700 and (s.st_dev,s.st_ino)==identity==(held.st_dev,held.st_ino)
 terminal=None;value=None;errors=[];protected=False;row=None
 try:
  try:
   argv=[f['refs']['python']['path'],'-B','-I',str(OWN/'artifact_tooling.py'),'worker',f['phase'],'--config-descriptor',json.dumps(f['configRow'],separators=(',',':'))]
   terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},external,TIMEOUT,f['rootRow'])
   terminal_row=fingerprint(external/'terminal.json')[0];assert f['capture'].read(terminal_row)==terminal
   for key in ('stdout','stderr'):assert fingerprint(terminal[key]['path'])[0]==terminal[key]
   write(out/'raw-terminal-observed.json',dict(schemaVersion=1,terminal=terminal_row,stdout=terminal['stdout'],stderr=terminal['stderr'],interpretationPending=True))
   clean_terminal(terminal,f['rootRow']);assert terminal['stdout']['bytes']<=16*1024*1024
   value=json.loads(Path(terminal['stdout']['path']).read_bytes());name='candidate-UNREVIEWED.json' if f['phase']=='export' else 'bootstrap-frame.json';row=fingerprint(out/name)[0];assert f['capture'].read(row)==value
   assert f['capture'].read(fingerprint(out/'whole-verifier-capsule.json')[0])==f['capsule'] and f['capture'].read(fingerprint(out/'native-frame.json')[0])==f['native']
   expected=f['model'].unreviewed_document(f['expected']) if f['phase']=='export' else f['model'].bootstrap_frame(f['pin'],f['native'],f['refs'],f['index'],f['rootRow'],f['configRow'],f['root'])
   assert value==expected
  except BaseException as error:errors.append(dict(stage='owned-phase-or-whole-return',type=type(error).__name__,rawFilesPreserved=True))
  finally:
   try:f['capture'].recheck();protected=True
   except BaseException as error:errors.append(dict(stage='final-or-failure-protection',type=type(error).__name__))
  same_root();success=value is not None and protected and errors==[]
  result=dict(schemaVersion=1,state='COMBINED355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V1' if success else 'COMBINED355_ARTIFACT_PHASE_FAILED_UNACCEPTED_V1',phase=f['phase'],toolingIndex=f['index'],rootAuthority=f['rootRow'],config=f['configRow'],actualFrozenReview=f['refs']['actualFrozenReview'],rawTerminal=None if terminal is None else fingerprint(external/'terminal.json')[0],rawExitCode=None if terminal is None else terminal['rawExitCode'],completePhaseReturn=row,nativeFrame=None if not (out/'native-frame.json').exists() else fingerprint(out/'native-frame.json')[0],verifierCapsule=None if not (out/'whole-verifier-capsule.json').exists() else fingerprint(out/'whole-verifier-capsule.json')[0],sourceAndOriginalProtectionRechecked=protected,errors=errors,requiresIndependentActualReview=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  observation=write(out/'controller-observation.json',result);same_root();print(json.dumps(dict(observation=observation,completeUnreviewed=success)),flush=True);return 0 if success else 1
 finally:os.close(fd)


def main():
 assert len(sys.argv)==5 and sys.argv[1] in ('parent','worker') and sys.argv[2] in ('export','bootstrap') and sys.argv[3]=='--config-descriptor'
 f=authorize(json.loads(sys.argv[4]),sys.argv[2])
 try:
  if sys.argv[1]=='parent':return parent(f)
  worker(f);return 0
 finally:f['capture'].recheck()
if __name__=='__main__':sys.exit(main())
