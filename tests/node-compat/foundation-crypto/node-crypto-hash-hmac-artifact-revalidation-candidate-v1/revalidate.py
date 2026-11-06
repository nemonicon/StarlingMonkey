"""New read-only P3 API argument context; never an original bootstrap record.
Stdlib authentication precedes every custom import. No child process is started.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-candidate-v1')
def checked(r):
 assert type(r)is dict and set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0
 p=Path(r['path']);assert p.is_absolute()and str(p)==r['path']and not r['path'].startswith('//')and '..'not in p.parts and '\\'not in r['path']and '\0'not in r['path']
 for q in(p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert stat.S_ISREG(a.st_mode)and a.st_size==r['bytes'];h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and h.hexdigest()==r['sha256'];return p
def read(r):assert r['bytes']<=32*1024*1024;return json.loads(checked(r).read_bytes())
def family(r):
 p=checked(r);v=json.loads(p.read_bytes());rows=[r];names={'index.json'}
 for x in v['files']:
  n=x['path'];assert n not in names and n and not n.startswith('/')and '\\'not in n and all(t not in('','.','..')for t in n.split('/'));names.add(n);item=dict(x,path=str(p.parent/n));checked(item);rows.append(item)
 assert not any(q.is_symlink()for q in p.parent.rglob('*'))and names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()};return rows
def load(row,name):
 spec=importlib.util.spec_from_file_location(name,checked(row));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def trees(values):
 for tree in values:
  base=Path(tree['root']);assert not base.is_symlink();actual=[]
  for parent,dirs,files in os.walk(base,followlinks=False):
   for n in dirs+files:
    p=Path(parent)/n;kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file';actual.append(dict(path=p.relative_to(base).as_posix(),kind=kind,mode=stat.S_IMODE(p.lstat().st_mode)))
  assert sorted(actual,key=lambda x:x['path'])==tree['entries']
def recheck(frame):
 frame['capture'].recheck();trees(frame['artifactTrees']);
 for alias in frame['aliases']['symlinks']:
  p=Path(alias['path']);assert p.is_symlink()and os.readlink(p)==alias['linkText']and str(p.resolve(strict=True))==alias['resolved']
 x=frame['refs']['indexException'];assert stat.S_IMODE(checked(x['currentActual']).stat().st_mode)==0o600
 for p in [frame['refs']['freezeRoot']]:assert not Path(p).exists()and not Path(p).is_symlink()
 frame['indexModel'].decode(checked(x['currentActual']).read_bytes(),checked(frame['refs']['baselineTreeTransport']).read_bytes())
def bootstrap(configRow):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
 cfg=read(configRow);assert cfg['schemaVersion']==1 and cfg['state']=='HASH_HMAC357_READ_ONLY_REVALIDATION_CONFIG_V1';root=read(cfg['rootAuthority']);own=cfg['adapterIndex'];ownrows=family(own)
 assert own['path']==str(OWN/'index.json')and root['adapterIndex']==own
 byname={Path(r['path']).relative_to(OWN).as_posix():r for r in ownrows[1:]};refs=read(byname['references.json']);assert root['entry']==refs['entry']and refs['entry']==byname['revalidate.py']
 captured={};families={}
 def add(r):checked(r);assert r['path']not in captured or captured[r['path']]==r;captured[r['path']]=r
 def indexed(r):
  rows=family(r)
  for x in rows:add(x)
  families[r['path']]=r;return rows
 for r in [configRow,cfg['rootAuthority'],*ownrows]:add(r)
 inputs=read(byname['source-inputs.json'])
 for r in inputs['files']:add(r)
 for r in inputs['families']:indexed(r)
 peerrows=indexed(root['sourceReview']['index']);assert peerrows.count(root['sourceReview']['result'])==1;peer=read(root['sourceReview']['result'])
 assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_ARTIFACT_REVALIDATION_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True
 for key in ['ownerActionsInvoked','hostActionsInvoked','admissionOrHelperActionsInvoked','engineExecuted','cryptoOperationsInvoked']:assert peer[key]is False
 assert root['state']=='ROOT_REVIEWED_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATION_V1'and root['readOnlySourceAdmissionAllowed']is root['ownedEvidencePublicationAllowed']is True
 for key in ['nativeBuildAllowed','recipeAllowed','compilerAllowed','ninjaAllowed','gitAllowed','engineExecutionAllowed','guestAllowed','cryptoAllowed','componentAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','gcAllowed','oomAllowed','debugAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']:assert root[key]is False
 assert root['actualRevalidationResult']is root['actualIndependentArtifactReview']is root['futureFreezeAuthority']is None
 assert root['indexException']==refs['indexException']and root['expectedEngine']==refs['engine']and root['expectedMetadata']==refs['metadata']
 for key in ['producerControllerIndex','originalFailureReview','originalFailureContract','configuredSourceRoot','workRoot','freezeRoot','outputRoot','externalOutputRoot','monitorEntry','monitorIndex']:assert root[key]==refs[key]
 assert root['schemaVersion']==1 and root['deadlineSeconds']==600 and root['nativeSourceFiles']==357 and root['externalEmbeddingSources']==3 and root['selectedWholeManifests']==12 and root['rawMetadataFields']==83
 assert peer['producerControllerSourceIndexSha256']==refs['producerControllerIndex']['sha256']and peer['integrationSourceIndexSha256']==refs['integrationSourceIndex']['sha256']and peer['originalFailureReviewIndexSha256']==refs['originalFailureReview']['index']['sha256']and peer['actualRevalidationProof']is None
 oldrows=indexed(refs['originalFailureReview']['index']);assert oldrows.count(refs['originalFailureReview']['result'])==oldrows.count(refs['originalFailureContract'])==1
 failure=read(refs['originalFailureReview']['result']);contract=read(refs['originalFailureContract']);assert failure['state']==contract['requiredReviewState']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_BUILD_V4_WRAPPER_FAILURE_REVIEW_PASSED_V1'and failure['verifiedPassed']is True
 for group in ['requiredFixedValues','requiredExactDescriptors']:
  for key,value in contract[group].items():assert failure[key]==value
 assert failure['coverage']==contract['requiredCoverage']and failure['phaseSucceeded']is failure['buildAcceptanceClaim']is failure['originalSourcePreservationPassed']is False
 for key in ['engine','metadata','actualBuildResult']:assert failure[key]==refs['originalBuildResult'if key=='actualBuildResult'else key]
 # Full current fixed artifact payload protection, including distributions,
 # occurs BEFORE the first own or original P3 custom module import.
 ledger=read(byname['artifact-inputs.json']);assert len(ledger['files'])==len({r['path']for r in ledger['files']})
 for r in ledger['files']:add(r)
 artifactTrees=read(byname['artifact-trees.json'])['trees'];trees(artifactTrees)
 aliases=read(byname['reference-aliases.json'])
 for r in aliases['symlinks']:
  p=Path(r['path']);assert p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve(strict=True))==r['resolved']
 assert stat.S_IMODE(checked(refs['indexException']['currentActual']).stat().st_mode)==0o600
 for r in captured.values():checked(r)
 io=load(refs['producerIo'],'genuine_original_P3_io_read_only');cap=io.Capture()
 for r in captured.values():cap.add(r)
 for r in families.values():cap.family(r)
 indexModel=load(byname['index_data.py'],'new_read_only_index_data');models=load(byname['models.py'],'new_read_only_revalidation_models');models.root(root,own,refs);models.peer(peer,own,refs)
 frame=dict(config=cfg,configRow=configRow,root=root,adapterIndex=own,refs=refs,ownRows=byname,io=io,capture=cap,artifactTrees=artifactTrees,aliases=aliases,indexModel=indexModel,models=models)
 recheck(frame);return frame
def run(frame):
 refs=frame['refs'];io=frame['io'];out=Path(refs['outputRoot']);assert not out.exists()and not out.is_symlink()
 for p in(out,*out.parents):assert not p.is_symlink()
 os.umask(0o077);out.mkdir(mode=0o700);result=None;received=False;primary=None
 try:
  raw=checked(refs['metadata']).read_bytes();fd=os.open(out/'raw-metadata.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb')as f:assert f.write(raw)==len(raw);f.flush();os.fsync(f.fileno())
  metadata=json.loads(raw);recheck(frame)
  # A NEW argument context, not a transported/bootstrap-authenticated old frame.
  # P3 module/refs/ownIndex keep their actual original source-owner identity.
  producerRefs=read(refs['producerReferences']);argument=dict(io=io,refs=producerRefs,ownIndex=refs['producerControllerIndex'])
  admission=load(refs['producerAdmission'],'genuine_original_P3_admission')
  wholeReturn=admission.admit(argument,lambda unused:recheck(frame))
  received=True
  io.write(out/'producer-admission-return.json',wholeReturn) # whole genuine DATA before caller checks
  distributions=load(frame['ownRows']['archive_data.py'],'new_read_only_archive_data').verify(metadata,refs,io);io.write(out/'distribution-data.json',distributions)
  semantics=frame['indexModel'].decode(checked(refs['indexException']['currentActual']).read_bytes(),checked(refs['baselineTreeTransport']).read_bytes())
  recheck(frame)
  inputrow=io.write(out/'current-input-hashes.json',dict(schemaVersion=1,files=sorted(frame['capture'].files.values(),key=lambda r:r['path'])))
  aliasrow=io.write(out/'reference-aliases.json',dict(schemaVersion=1,symlinks=frame['aliases']['symlinks'],archiveHardlinks=distributions['archiveHardlinks']))
  result=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATED_UNREVIEWED_V1',adapterSourceIndex=frame['adapterIndex'],rootAuthority=frame['config']['rootAuthority'],producerControllerIndex=refs['producerControllerIndex'],argumentContextKind='NEW_READ_ONLY_ARGUMENT_CONTEXT_ORIGINAL_P3_OWNER_V1',originalBootstrapFrameClaimed=False,originalFailureReview=refs['originalFailureReview'],originalBuildResult=refs['originalBuildResult'],originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,originalResultRewritten=False,engine=refs['engine'],metadata=refs['metadata'],rawMetadataFields=83,nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=12,producerAdmission=wholeReturn,currentIndexSemantics=semantics,indexException=refs['indexException'],distributionAudit=distributions,inputHashes=inputrow,referenceAliases=aliasrow,currentInputBookendsPassed=True,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,freezeInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsAnyActionAuthority=False)
  frame['models'].result(result,refs);io.write(out/'result.json',result);recheck(frame);print(json.dumps(result),flush=True);return result
 except BaseException as error:
  primary=error
  try:io.write(out/'failure.json',dict(schemaVersion=1,state='READ_ONLY_REVALIDATION_FAILED_UNACCEPTED',errorType=type(error).__name__,errorMessage=str(error),producerReturnReceived=received,originalBuildResult=refs['originalBuildResult'],engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False))
  except BaseException:pass
  raise
 finally:
  try:recheck(frame)
  except BaseException as finalError:
   if primary is None:raise
   try:io.write(out/'secondary-protection-failure.json',dict(errorType=type(finalError).__name__,errorMessage=str(finalError),originalErrorRethrown=True))
   except BaseException:pass
def main():
 assert len(sys.argv)==2;return run(bootstrap(json.loads(sys.argv[1])))
if __name__=='__main__':main()
