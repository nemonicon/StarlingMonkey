"""Distinct future normal-only export/bootstrap guard; no action at import."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys

def descriptor(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'}
 assert type(row['path'])is str and row['path'].startswith('/')and not row['path'].startswith('//')and str(Path(row['path']))==row['path']and '\\'not in row['path']and '\0'not in row['path']and '..'not in row['path'].split('/')
 assert type(row['bytes'])is int and row['bytes']>=0 and type(row['sha256'])is str and len(row['sha256'])==64 and all(c in'0123456789abcdef'for c in row['sha256'])
 return dict(row)

def checked(row):
 row=descriptor(row);p=Path(row['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 for q in(physical,*physical.parents):assert not q.is_symlink()
 a=physical.stat();assert stat.S_ISREG(a.st_mode);d=hashlib.sha256()
 with physical.open('rb')as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):d.update(chunk)
 b=physical.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert a.st_size==row['bytes']and d.hexdigest()==row['sha256'];return p

def read(row):
 assert row['bytes']<=32*1024*1024;raw=checked(row).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)

def family(row):
 x=read(row);base=Path(row['path']).parent;rows=[row];names=set()
 assert x['schemaVersion']==1 and 0<len(x['files'])<=2048
 for r in x['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n);d=dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
 assert not any(p.is_symlink()for p in base.rglob('*'))
 assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'};return rows

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/resource-pin-tooling-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
FROZEN=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze')
EXPORT_ROOT=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-pin-tooling')
EXPORT_FILE=EXPORT_ROOT/'export-normal-off-UNREVIEWED.json'
RESOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
FREEZER_SHA='f88db73e4541e72bf37fa1c2a684257a737fde1dc685a34f00335ebc0705b072'
def root_model(root,config,phase):
 assert phase in('export','bootstrap')and root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1'and root['phase']==phase
 assert root['toolingIndex']==config['toolingIndex']and root['resourceSourceIndexSha256']==RESOURCE_SHA and root['freezerSourceIndexSha256']==FREEZER_SHA
 assert root['variant']=='normal-off'and root['nativeSourceFiles']==342 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==9
 assert root['configuredSourceRoot']==str(SOURCE)and root['frozenSourceRoot']==str(FROZEN/'source')and root['freezeRoot']==str(FROZEN)
 assert root['exportAllowed']is(phase=='export')and root['bootstrapAllowed']is(phase=='bootstrap')
 for key in('buildAllowed','freezeAllowed','gcReconfigureAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):assert root[key]is False
 if phase=='export':
  assert root['candidateOutput']==str(EXPORT_FILE)
  for key in('actualExportCandidate','independentExportReview','reviewedPins','rootPinReview'):assert root[key]is None
 else:
  assert root['candidateOutput']is None
  descriptor(root['actualExportCandidate']);descriptor(root['reviewedPins']);descriptor(root['rootPinReview']);assert root['independentExportReview']['index']and root['independentExportReview']['result']
def source_peer_model(value,config):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_PIN_TOOLING_SOURCE_REVIEW_PASSED_V1'
 assert value['toolingSourceIndexSha256']==config['toolingIndex']['sha256']and value['resourceSourceIndexSha256']==RESOURCE_SHA and value['freezerSourceIndexSha256']==FREEZER_SHA
 assert value['sourceOnly']is True and value['sourceReviewPassed']is True
 for key in('ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked'):assert value[key]is False
def artifact_model(value,refs):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_PASSED_V1'and value['verifiedPassed']is True
 assert value['resourceSourceIndexSha256']==RESOURCE_SHA and value['freezerSourceIndexSha256']==FREEZER_SHA and value['variant']=='normal-off'
 assert value['nativeSourceFiles']==342 and value['externalEmbeddingSources']==3 and value['selectedManifestCount']==9
 for key in('engine','metadata','freezeReceipt'):assert value[key]==refs[key]
 assert value['engineSha256']==refs['engine']['sha256']and value['metadataSha256']==refs['metadata']['sha256']
 assert value['configuredSourceRoot']==str(SOURCE)and value['freezeRoot']==str(FROZEN)and value['frozenSourceRoot']==str(FROZEN/'source')and value['sourceRoot']==str(FROZEN/'source')
 for key in('engineExecuted','bootstrapExecuted','gcReconfigureAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeAdoption'):assert value[key]is False
def recheck(frame):
 for row in frame['captured']:checked(row)
 for index in frame['families']:family(index)
def load_exact(row,name):
 checked(row);spec=importlib.util.spec_from_file_location(name,row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def authorize(config_row,phase):
 assert __debug__ and sys.dont_write_bytecode and Path(__file__).resolve().parent==OWN
 assert not any(os.environ.get(k)for k in('PYTHONOPTIMIZE','PYTHONHOME','PYTHONPATH','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'))
 config=read(config_row);assert config['schemaVersion']==1;root=read(config['rootAuthority']);root_model(root,config,phase)
 own_index=config['toolingIndex'];assert own_index['path']==str(OWN/'index.json')
 own=family(own_index);refs=read(next(r for r in own if r['path']==str(OWN/'references.json')))
 assert config['resourceSourceIndex']==refs['resourceSourceIndex']and config['freezerIndex']==refs['freezerIndex']
 resource=family(config['resourceSourceIndex']);freezer=family(config['freezerIndex']);captured=[config_row,config['rootAuthority'],*own,*resource,*freezer];families=[own_index,config['resourceSourceIndex'],config['freezerIndex']]
 for pair in(root['sourceIndependentReview'],refs['freezerSourceReview'],refs['actualArtifactReview']):
  rows=family(pair['index']);assert pair['result']in rows;captured+=rows;families.append(pair['index'])
 source_peer_model(read(root['sourceIndependentReview']['result']),config)
 fp=read(refs['freezerSourceReview']['result']);assert fp['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'and fp['freezerSourceIndexSha256']==FREEZER_SHA and fp['sourceOnly']is True and fp['sourceReviewPassed']is True and fp['ownerActionsInvoked']is False
 assert root['actualArtifactReview']==refs['actualArtifactReview']and root['actualArtifactContract']==refs['actualArtifactContract']
 artifact_model(read(refs['actualArtifactReview']['result']),refs);contract_rows=family(refs['actualArtifactReview']['index']);assert refs['actualArtifactContract']in contract_rows
 for row in(refs['actualArtifactContract'],refs['actualFreezeRootObservation'],refs['freezeReceipt'],refs['metadata'],refs['actualStageResult'],refs['node'],refs['python']):checked(row);captured.append(row)
 assert refs['frozenVerifier']in freezer and refs['metadataModel']in resource and refs['resourcePolicy']in resource
 # Explicit configured context is checked directly; no original/copy helper projection.
 stage=read(refs['actualStageResult']);assert stage['sourceIndex']==config['resourceSourceIndex']and stage['destination']==str(SOURCE)and len(stage['copies'])==501
 for item in stage['copies']:
  row=dict(item['original'],path=item['path']);checked(row);captured.append(row)
 metadata=read(refs['metadata']);policy=read(refs['resourcePolicy'])
 frame=dict(config=config,root=root,ownRows=own,refs=refs,captured=captured,families=families,metadata=metadata,phase=phase)
 try:
  recheck(frame)
  if phase=='bootstrap':
   # All review/pin gates precede genuine verifier/helper actions or engine reads.
   pin_model=load_exact(next(r for r in own if r['path']==str(OWN/'pin_model.py')),'resource342_prehelper_pin_model')
   expected=pin_model.candidate(read(refs['freezeReceipt']),metadata,refs,config['toolingIndex'])
   pair=root['independentExportReview'];rows=family(pair['index']);assert pair['result']in rows;captured+=rows;families.append(pair['index']);proof=read(pair['result'])
   assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True
   assert proof['toolingSourceIndexSha256']==config['toolingIndex']['sha256']and proof['resourceSourceIndexSha256']==RESOURCE_SHA and proof['freezerSourceIndexSha256']==FREEZER_SHA
   assert proof['candidate']==root['actualExportCandidate']and proof['actualArtifactReview']==refs['actualArtifactReview']and proof['freezeReceipt']==refs['freezeReceipt']
   assert proof['variant']=='normal-off'and proof['rawExporterExitCode']==0
   assert proof['engineExecuted']is False and proof['bootstrapExecuted']is False and proof['operationalAdmission']is False and proof['runtimeAcceptanceClaim']is False
   assert read(root['actualExportCandidate'])==pin_model.unreviewed_document(expected)
   frame['reviewedPin']=pin_model.select_reviewed(read(root['reviewedPins']),read(root['rootPinReview']),expected,root['reviewedPins']['sha256'],root['actualExportCandidate'],pair)
   captured += [root['actualExportCandidate'],root['reviewedPins'],root['rootPinReview']];recheck(frame)
  model=load_exact(refs['metadataModel'],'genuine_resource342_pin_raw_model')
  model.validate_metadata(metadata,policy,refs['policySha256'],refs['helperSha256'],refs['recipeSha256'],refs['externalSourceManifest'],'normal-off')
  verifier=load_exact(refs['frozenVerifier'],'genuine_resource342_frozen_verifier')
  assert Path(verifier.__file__).resolve()==Path(refs['frozenVerifier']['path'])and verifier.FREEZE==FROZEN
  verified=verifier.verify_frozen(refs['freezeReceipt']);receipt=read(refs['freezeReceipt'])
  assert verified['engine']==refs['engine']and verified['metadata']==refs['metadata']and verified['copies']==refs['actualCopiedRows']==666
  assert receipt['configuredSourceRoot']==str(SOURCE)and receipt['sourceRoot']==str(FROZEN/'source')and receipt['componentizeSourceRoot']==refs['componentizeSourceRoot']
  for row in receipt['copies']:
   d={k:row[k]for k in('path','sha256','bytes')};checked(d);captured.append(d)
  manifests=[]
  assert metadata['selectedModuleManifests']==refs['selectedManifestRecords']and len(metadata['selectedModuleManifests'])==9
  for row in metadata['selectedModuleManifests']:
   relative=row['path'];assert relative in{r['path']for r in metadata['sourceManifest']}
   path=FROZEN/'source'/relative;d=dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size);manifests.append(read(d));captured.append(d)
  frame.update(receipt=receipt,selectedManifests=manifests,verifier=verifier)
  return frame
 finally:recheck(frame)
