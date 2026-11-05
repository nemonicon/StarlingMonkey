"""Selector342 normal-OFF freezer authority and explicit phase entry. Dormant."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/task-selection-freezer-candidate-v1'
PROPOSAL=REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze-external-root')
SOURCE_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
ENGINE_SHA='f6a775f019ca48bb6b9a46a88364aa51a2691101a9e79325848afb5504c3034f'
META_SHA='8219b7aaea6f5a311ccd9e2d038edcd213663078f9ff18917c155dfeb51dde4f'
_TOKEN=object()
class Frame(dict):pass

def descriptor(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'}
 assert type(row['path'])is str and row['path'].startswith('/')and not row['path'].startswith('//')and str(Path(row['path']))==row['path']and '\\'not in row['path']and '\0'not in row['path']and '..'not in row['path'].split('/')
 assert type(row['bytes'])is int and row['bytes']>=0 and type(row['sha256'])is str and len(row['sha256'])==64 and all(c in'0123456789abcdef'for c in row['sha256'])
 return dict(row)
def checked(row):
 row=descriptor(row);p=Path(row['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 for q in(physical,*physical.parents):assert not q.is_symlink()
 a=physical.stat();assert stat.S_ISREG(a.st_mode);h=hashlib.sha256()
 with physical.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=physical.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert a.st_size==row['bytes']and h.hexdigest()==row['sha256'];return physical
def unique(pairs):
 d={}
 for k,v in pairs:assert k not in d;d[k]=v
 return d
def read(row):
 assert row['bytes']<=32*1024*1024
 raw=checked(row).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 return json.loads(raw.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in()).throw(ValueError('finite JSON')))
def family(row):
 d=read(row);base=Path(row['path']).parent;rows=[row];names=set()
 assert d['schemaVersion']==1 and 0<len(d['files'])<=2048
 for r in d['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n)
  q=dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']);checked(q);rows.append(q)
 assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'}
 return rows
def add(frame,row):
 checked(row);key=row['path']
 if key in frame['captured']:assert frame['captured'][key]==row
 else:frame['captured'][key]=row
def require_frame(frame):assert type(frame)is Frame and frame.get('_token')is _TOKEN
def recheck(frame):
 require_frame(frame)
 for row in frame['captured'].values():checked(row)
 for ix in frame['families']:family(ix)
 for row in frame['refs']['sdkAliases']:
  p=Path(row['path']);assert p.is_symlink()and os.readlink(p)==row['linkText']and str(p.resolve(strict=True))==row['resolvedPath']
 for row in frame['modePairs']:
  a,b=Path(row['path']).stat(),checked(row['original']).stat()
  assert stat.S_IMODE(a.st_mode)==row['mode']==stat.S_IMODE(b.st_mode)and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 for root,names in frame['protectedTrees']:assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(names)and not any(p.is_symlink()for p in root.rglob('*'))
def root_model(root,own):
 assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZE_V1'
 assert root['phase']=='freeze'and root['variant']=='normal-off'and root['taskSelectionSourceIndexSha256']==SOURCE_SHA
 assert root['freezerIndex']==own and root['entry']['path']==str(OWN/'entry.py')
 assert root['configuredSourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['freezeRoot']==str(FREEZE)and root['externalOutputRoot']==str(EXTERNAL)
 assert root['nativeSourceFiles']==342 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==9
 assert root['freezeAllowed']is True and root['readOnlySourceAdmissionAllowed']is True and root['postBuildNinjaCommandsAllowed']is True
 assert root['externalParentDeadlineSeconds']==2400 and root['requiredStartFreeBytes']==2147483648 and root['gcStress']is False and root['entropyMode']=='OFF'
 for k in('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):assert root[k]is False
 for k in('actualFreezeResult','independentFreezeReview','reviewedEnginePins','runtimeAuthority'):assert root[k]is None
def peer_model(value,own):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'
 assert value['freezerSourceIndexSha256']==own['sha256']and value['taskSelectionSourceIndexSha256']==SOURCE_SHA
 assert value['sourceOnly']is True and value['sourceReviewPassed']is True
 for k in('ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked'):assert value[k]is False
def metadata_model(metadata,policy,refs):
 assert metadata['engineSha256']==ENGINE_SHA and metadata['enginePath']==refs['engine']['path']and metadata['engineBytes']==refs['engine']['bytes']
 assert metadata['buildRecipeSha256']==refs['recipeSha256']and metadata['sourceManifest']==policy['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==342
 assert metadata['componentizeSourceManifest']==refs['externalSourceManifest']and len(metadata['componentizeSourceManifest'])==3
 assert metadata['selectedModuleManifests']==refs['selectedManifests']and len(metadata['selectedModuleManifests'])==9
 assert metadata['taskSelectionPolicy']['sourcePolicy']==policy['taskSelectionSourcePolicy']and metadata['resourceOwnershipPolicy']['sourcePolicy']==policy['resourceOwnershipSourcePolicy']
 assert metadata['taskSelectionPolicy']['policyFileSha256']==refs['policySha256']and metadata['taskSelectionPolicy']['helperSha256']==refs['helperSha256']and metadata['taskSelectionPolicy']['allNativeDependentsRequireRebuild']is True
 assert metadata['taskSelectionPolicy']['nativeAllInvalidRuntimeValidation']is None and metadata['taskSelectionPolicy']['fullResetOrReuse']is False
 assert metadata['gcStress']is False and metadata['oomTesting']is False and metadata['entropyPolicy']=='off'and metadata['debuggerEnabled']is False and metadata['wptSupportEnabled']is False
 assert not metadata.get('syntheticMetadataOnly',False)and not metadata.get('diagnosticOnly',False)
 for name in('profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled'):assert metadata[name]is True
def compilation_model(database,metadata,policy,refs):
 cpp={str(SOURCE/r['path'])for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};assert len(cpp)==61
 other={str(SOURCE/p)for p in('host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/host_call.cpp','host-apis/wasi-0.2.3/sockets.cpp','host-apis/wasi-0.2.10/bindings/bindings.c','crates/rust-hooks/src/wrappers.cpp')}
 assert len(database)==len({r['file']for r in database})==67 and{r['file']for r in database}==cpp|other|{str(Path(metadata['cmakeCachePath']).parent/'starling-raw.wasm/null.cpp')}
 for field,name in(('actualHostApiCompileCommands','host-apis/wasi-0.2.0/host_api.cpp'),('actualEventLoopCompileCommands','runtime/event_loop.cpp')):assert metadata['taskSelectionPolicy'][field]==[next(r['command']for r in database if r['file']==str(SOURCE/name))]
 for values,count in((metadata['internalTickPolicy']['actualLayoutCompileCommands'],61),(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands'],4),(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands'],5)):assert len(values)==count and all(c in[r['command']for r in database]for c in values)
 assert len(metadata['actualEmbeddingCompileCommands'])==1 and not any(r['file'].endswith('/embedding/embedding.cpp')for r in database)
 assert metadata['actualEmbeddingCompileCommands']==metadata['internalTickPolicy']['actualEmbeddingCompileCommands']
 for row in database:
  words=shlex.split(row['command']);assert words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==row['file']and '-fsyntax-only'not in words
  assert[word for word in words if word.startswith('-O')]==['-O3']and '-DNDEBUG'in words
  assert not any(word.startswith(('-DDEBUG','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','@'))for word in words)
  expected_include=0 if row['file'].endswith('/starling-raw.wasm/null.cpp')else 1;assert words.count('-include')==expected_include
  if expected_include:assert words[words.index('-include')+1]==str(WORK/'spidermonkey-dist-release/include/js-confdefs.h')
def authorize(config_row):
 assert __debug__ and sys.dont_write_bytecode
 assert Path(__file__).resolve()==OWN/'entry.py'
 assert not any(os.environ.get(k)for k in('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'))
 config=read(config_row);own=config['freezerIndex'];root=read(config['rootAuthority']);root_model(root,own)
 assert own['path']==str(OWN/'index.json')and config['taskSelectionSourceIndex']==dict(path=str(PROPOSAL/'index.json'),sha256=SOURCE_SHA,bytes=5120)
 own_rows=family(own);source_rows=family(config['taskSelectionSourceIndex']);assert root['entry']in own_rows
 refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
 frame=Frame(_token=_TOKEN,config=config,configRow=config_row,root=root,refs=refs,captured={},families=[own,config['taskSelectionSourceIndex']],ownRows=own_rows,sourceRows=source_rows,modePairs=[],protectedTrees=[])
 try:
  for row in[config_row,config['rootAuthority'],*own_rows,*source_rows]:add(frame,row)
  for item in refs['families']:
   frame['families'].append(item['index'])
   for row in family(item['index']):add(frame,row)
  for row in refs['files']:add(frame,row)
  peer=root['sourceIndependentReview'];peer_rows=family(peer['index']);assert peer['result']in peer_rows;peer_model(read(peer['result']),own)
  frame['families'].append(peer['index'])
  for row in peer_rows:add(frame,row)
  assert root['actualBuildReview']==refs['actualBuildReview']and root['actualBuildContract']==refs['actualBuildContract']and root['engine']==refs['engine']and root['metadata']==refs['metadata']
  build=read(refs['actualBuildReview']['result']);contract=read(refs['actualBuildContract'])
  assert build['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1'and build['verifiedPassed']is True and build['sourceIndexSha256']==SOURCE_SHA
  for key,value in contract['requiredFixedValues'].items():assert build[key]==value,key
  for key,value in contract['requiredExactDescriptors'].items():assert build['artifacts'][key]==value,key
  assert refs['sdkAliases']==build['referenceAliases']and len(refs['sdkAliases'])==31 and refs['declaredArchiveHardlinks']==build['declaredArchiveHardlinks']and len(refs['declaredArchiveHardlinks'])==1
  assert root['actualBuildResult']==build['actualBuildResult']and root['actualBuildRootObservation']==build['rootBuildObservation']and build['configuredSourceRoot']==str(SOURCE)and build['workRoot']==str(WORK)
  # Full current original provenance, including engine as hash-only DATA, BEFORE
  # importing any genuine metadata/layer/copy/monitor module.
  ledger=read(refs['buildInputLedger']);assert len(ledger['files'])==20761
  for item in ledger['files']:add(frame,{k:item[k]for k in('path','sha256','bytes')})
  for name,count in(('actualStageResult',566),('oldResourceStage',501)):
   journal=read(refs[name]);assert len(journal['copies'])==count
   if name=='actualStageResult':assert journal['destination']==str(SOURCE)and journal['sourceIndex']['sha256']==SOURCE_SHA
   for c in journal['copies']:
    original=descriptor(c['original']);current=dict(original,path=c['path']);add(frame,original);add(frame,current)
    a,b=checked(current).stat(),checked(original).stat();assert stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
    frame['modePairs'].append(dict(path=c['path'],original=original,mode=stat.S_IMODE(a.st_mode)))
  old=read(refs['oldResourceFreeze']);oldroot=Path(refs['oldResourceFreeze']['path']).parent;assert len(old['copies'])==666 and sum(c['original']is not None for c in old['copies'])==663
  for c in old['copies']:
   add(frame,{k:c[k]for k in('path','sha256','bytes')})
   if c['original']is not None:add(frame,descriptor(c['original']))
  frame['protectedTrees'].append((oldroot,[str(Path(c['path']).relative_to(oldroot))for c in old['copies']]+['normal-off-freeze-receipt.json']))
  # ORIGINAL preparation manifests retain their declared repository contexts.
  for data in refs['preparationManifests']:
   for row in read(data)['files']:add(frame,{k:row[k]for k in('path','sha256','bytes')})
  metadata=read(refs['metadata']);policy=read(refs['policy']);database=read(refs['compileCommands'])
  metadata_model(metadata,policy,refs);compilation_model(database,metadata,policy,refs)
  assert[read(dict(path=str(SOURCE/row['path']),sha256=row['sha256'],bytes=(SOURCE/row['path']).stat().st_size))for row in metadata['selectedModuleManifests']]==refs['selectedManifestValues']
  cache={}
  for line in checked(refs['cmakeCache']).read_text().splitlines():
   key,colon,tail=line.partition(':')
   if colon and '='in tail:cache[key]=tail.partition('=')[2]
  assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions']and all(cache.get(k)==v for k,v in metadata['observedCMakeOptions'].items())
  assert cache['CMAKE_HOME_DIRECTORY']==refs['externalSourceRoot']and cache['CMAKE_BUILD_TYPE']=='Release'and cache['ENABLE_BUILTIN_WEB_TIMERS']=='ON'
  assert Path(sys.executable).resolve(strict=True)==Path(refs['python']['path']);checked(refs['python']);checked(refs['ninja'])
  for role in('configuredModel','configuredLayer'):add(frame,refs[role])
  frame.update(metadata=metadata,policy=policy,database=database);recheck(frame);return frame
 finally:
  if frame['captured']:recheck(frame)
def load_own(frame,name):
 require_frame(frame);row=next(r for r in frame['ownRows']if r['path']==str(OWN/name));checked(row);recheck(frame)
 spec=importlib.util.spec_from_file_location('task_selection_freezer_'+name.replace('.','_'),row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main(mode,config_row):
 frame=authorize(config_row)
 try:
  if mode=='parent':
   assert not EXTERNAL.exists()and not EXTERNAL.is_symlink()and not FREEZE.exists()and not FREEZE.is_symlink()
   monitor=load_own(frame,'monitor.py');EXTERNAL.mkdir(mode=0o700)
   argv=[frame['refs']['python']['path'],'-B','-I',str(OWN/'entry.py'),'freeze',json.dumps(config_row,separators=(',',':'))]
   terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},EXTERNAL,2400,frame['config']['rootAuthority']);recheck(frame)
   assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True and not terminal['forcedCleanup']and not terminal['timeout']and not terminal['errors']and not terminal['signals']and not terminal['interruptedSignals']and terminal['remainingObservedPids']==[]
   return terminal
  if mode=='freeze':return load_own(frame,'freeze.py').freeze(frame,sys.modules[__name__])
  if mode=='admit':return load_own(frame,'admission.py').admit(frame,sys.modules[__name__])
  raise ValueError('finite phase')
 finally:recheck(frame)
if __name__=='__main__':
 assert len(sys.argv)==3 and sys.argv[1]in('parent','freeze','admit')
 print(json.dumps(main(sys.argv[1],json.loads(sys.argv[2]))),flush=True)
