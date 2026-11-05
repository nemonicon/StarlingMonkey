"""Normal-only resource342 freeze admission. Standard-library source checks first."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/resource-freezer-candidate-v1'
PROPOSAL=REPO/'tests/node-compat/foundation-scheduler/resource-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze')
EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze-external-root')
SOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
ENGINE_SHA='fec7a900f0c04815e3609d2f9a5ed94056d854bd1a8f241bf74cb5f3f475a704'
META_SHA='51fbc0a06ed2e06c24e6d1fd3190873a5a3190657cfe2d74bf44ff4128b0e80e'

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
def recheck(frame):
 for r in frame['captured']:checked(r)
 for ix in frame['families']:family(ix)
 for r in frame['refs']['sdkAliases']:
  p=Path(r['path']);assert p.is_symlink()and str(p.readlink())==r['link']and str(p.resolve(strict=True))==r['resolvedTarget']
def root_model(root,own):
 assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZE_V1'
 assert root['phase']=='freeze'and root['variant']=='normal-off'and root['resourceSourceIndexSha256']==SOURCE_SHA
 assert root['freezerIndex']==own and root['freezerEntry']['path']==str(OWN/'freeze.py')
 assert root['configuredSourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['freezeRoot']==str(FREEZE)and root['externalOutputRoot']==str(EXTERNAL)
 assert root['nativeSourceFiles']==342 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==9
 assert root['freezeAllowed']is True and root['postBuildNinjaCommandsAllowed']is True and root['externalParentDeadlineSeconds']==2400
 assert root['requiredStartFreeBytes']==2147483648 and root['gcStress']is False and root['entropyMode']=='OFF'
 for k in('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):assert root[k]is False
 for k in('actualFreezeResult','independentFreezeReview','reviewedEnginePins','runtimeAuthority'):assert root[k]is None
def peer_model(value,own):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'
 assert value['freezerSourceIndexSha256']==own['sha256']and value['resourceSourceIndexSha256']==SOURCE_SHA
 assert value['sourceOnly']is True and value['sourceReviewPassed']is True
 for k in('ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked'):assert value[k]is False
def authorize(config_row):
 assert __debug__ and sys.dont_write_bytecode
 assert not any(os.environ.get(k)for k in('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'))
 config=read(config_row);root=read(config['rootAuthority']);own=config['freezerIndex'];root_model(root,own)
 assert own['path']==str(OWN/'index.json')and config['resourceSourceIndex']==dict(path=str(PROPOSAL/'index.json'),sha256=SOURCE_SHA,bytes=5390)
 own_rows=family(own);assert root['freezerEntry']in own_rows;source_rows=family(config['resourceSourceIndex'])
 refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')));captured=[config_row,config['rootAuthority'],*own_rows,*source_rows];families=[own,config['resourceSourceIndex']]
 for item in refs['families']:captured+=family(item['index']);families.append(item['index'])
 for r in refs['files']:checked(r);captured.append(r)
 pair=root['sourceIndependentReview'];peers=family(pair['index']);assert pair['result']in peers;peer_model(read(pair['result']),own);captured+=peers;families.append(pair['index'])
 assert root['actualBuildReview']==refs['actualBuildReview']and root['actualBuildContract']==refs['actualBuildContract']
 build=read(root['actualBuildReview']['result']);contract=read(root['actualBuildContract']);assert contract['reviewResult']==root['actualBuildReview']['result']
 for key,value in contract['requiredFixedValues'].items():assert build[key]==value,key
 assert build['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1'and build['verifiedPassed']is True
 assert build['engineSha256']==ENGINE_SHA and build['metadataSha256']==META_SHA and build['configuredSourceRoot']==str(SOURCE)and build['variant']=='normal-off'
 assert root['actualBuildResult']==build['actualBuildResult']and root['actualBuildRootObservation']==build['rootObservation']and root['engine']==refs['engine']and root['metadata']==refs['metadata']
 # Every configured source/tool/proof stage copy is authenticated before helpers.
 stage=read(refs['actualStageResult']);assert stage['destination']==str(SOURCE)and stage['sourceIndex']['sha256']==SOURCE_SHA and len(stage['copies'])==501
 for item in stage['copies']:
  original=descriptor(item['original']);current=dict(original,path=item['path']);a=checked(original).stat();b=checked(current).stat();assert stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino);captured.extend([original,current])
 metadata=read(refs['metadata']);policy=read(next(r for r in source_rows if r['path']==str(PROPOSAL/'policy.json')))
 frame=dict(config=config,root=root,captured=captured,families=families,ownRows=own_rows,sourceRows=source_rows,refs=refs,metadata=metadata,policy=policy)
 try:
  # Genuine pure metadata function, not old trace/355 selector or transformed metadata.
  model_row=next(r for r in source_rows if r['path']==str(PROPOSAL/'native-admission-model.py'));checked(model_row)
  spec=importlib.util.spec_from_file_location('genuine_resource342_raw_metadata_model',model_row['path']);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
  model.validate_metadata(metadata,policy,refs['policySha256'],refs['helperSha256'],refs['recipeSha256'],refs['externalSourceManifest'],'normal-off')
  assert len(metadata['selectedModuleManifests'])==9 and metadata['selectedModuleManifests']==refs['selectedManifests']
  for r in metadata['selectedModuleManifests']:
   d=next(x for x in metadata['sourceManifest']if x['path']==r['path']);assert d['sha256']==r['sha256'];path=SOURCE/r['path'];checked(dict(path=str(path),sha256=r['sha256'],bytes=path.stat().st_size))
  layer_row=dict(path=str(SOURCE/'tests/node-compat/foundation-scheduler/resource-integration-candidate-v1/layer-policy.py'),sha256=refs['helperSha256'],bytes=refs['helperBytes']);checked(layer_row)
  spec=importlib.util.spec_from_file_location('genuine_configured_resource342_layer',layer_row['path']);layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
  assert layer.HERE==SOURCE/'tests/node-compat/foundation-scheduler/resource-integration-candidate-v1';layer.validate_sources(SOURCE,metadata['sourceManifest'])
  cache={}
  for line in checked(refs['cmakeCache']).read_text().splitlines():
   key,colon,tail=line.partition(':')
   if colon and '='in tail:cache[key]=tail.partition('=')[2]
  database=read(refs['compileCommands']);assert len(database)==67
  policy_cpp={str(SOURCE/r['path'])for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};assert len(policy_cpp)==61
  other={str(SOURCE/p)for p in('host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/host_call.cpp','host-apis/wasi-0.2.3/sockets.cpp','host-apis/wasi-0.2.10/bindings/bindings.c','crates/rust-hooks/src/wrappers.cpp')}
  assert len({r['file']for r in database})==67 and {r['file']for r in database}==policy_cpp|other|{str(Path(metadata['cmakeCachePath']).parent/'starling-raw.wasm/null.cpp')}
  assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions']and all(cache.get(k)==v for k,v in metadata['observedCMakeOptions'].items())
  assert cache['CMAKE_HOME_DIRECTORY']==refs['externalSourceRoot']and cache['ENABLE_BUILTIN_WEB_TIMERS']=='ON'
  layer.validate_classic_compilation(database,metadata['actualEmbeddingCompileCommands'],SOURCE,metadata)
  assert len(metadata['actualEmbeddingCompileCommands'])==1 and not any(r['file'].endswith('/embedding/embedding.cpp')for r in database)
  # Full original build inputs are verified only after the raw metadata/source gate.
  ledger=read(refs['buildInputLedger']);engine_path=refs['engine']['path']
  for item in ledger['files']:
   d={k:item[k]for k in('path','sha256','bytes')}
   if d['path']!=engine_path:checked(d);captured.append(d)
  frame.update(layer=layer,database=database);return frame
 finally:recheck(frame)
