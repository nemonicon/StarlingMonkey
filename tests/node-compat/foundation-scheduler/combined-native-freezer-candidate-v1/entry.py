"""Genuine combined355-v2 freeze Frame and explicit dormant phase entry."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-freezer-candidate-v1'
PROPOSAL=REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
WORK=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
EXTERNAL=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze-external-root')
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
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
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
ENGINE_SHA='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'
META_SHA='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
COUNTS=dict(nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=80,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6)

def metadata_model(metadata,policy,refs):
 assert len(metadata)==80 and metadata['engineSha256']==ENGINE_SHA and metadata['enginePath']==refs['engine']['path'] and metadata['engineBytes']==refs['engine']['bytes']
 assert metadata['buildRecipeSha256']==refs['recipe']['sha256']
 assert metadata['sourceManifest']==policy['expectedNativeSourceManifest'] and len({r['path'] for r in metadata['sourceManifest']})==355
 assert metadata['componentizeSourceManifest']==refs['externalSourceManifest']==policy['expectedComponentizeSourceManifest'] and len(refs['externalSourceManifest'])==3
 assert metadata['selectedModuleManifests']==refs['selectedManifests']==policy['selectedModuleManifests'] and len(refs['selectedManifests'])==11
 for name in ('resourceOwnershipPolicy','taskSelectionPolicy','zlibErrorSemanticsPolicy','combinedNativeSourcePolicy'):
  assert metadata[name]['policyFileSha256']==refs['policy']['sha256'] and metadata[name]['helperSha256']==refs['layer']['sha256']
 assert metadata['combinedNativeSourcePolicy']['configuredSourceRoot']==refs['configuredSourceRoot']
 assert metadata['combinedNativeSourcePolicy']['workRoot']==refs['workRoot']
 assert metadata['privateRustupBootstrapPolicy']==refs['privateRustupBootstrapPolicy']
 rust=metadata['privateRustupBootstrapPolicy'];assert rust['persistentSetting']=='disable' and rust['oldFailedWorkResumed'] is False
 assert rust['privateHomes']==dict(rustup=refs['workRoot']+'/rustup-home',cargo=refs['workRoot']+'/cargo-home')
 # beforeInstallRecord's nested settings descriptor is historical DATA, not a live path.
 assert rust['beforeInstallRecord']==refs['rustupBeforeRecord'] and rust['settingsAtBuildCompletion']==refs['rustupCurrentSettings']
 assert refs['rustupBeforeRecord']['bytes']==368 and refs['rustupCurrentSettings']['bytes']==107
 assert metadata['gcStress'] is metadata['oomTesting'] is metadata['debuggerEnabled'] is metadata['wptSupportEnabled'] is False
 assert metadata['entropyPolicy']=='off' and not metadata.get('diagnosticOnly',False) and not metadata.get('syntheticMetadataOnly',False)

def compilation_model(database,metadata,policy,refs):
 source=Path(refs['configuredSourceRoot']);work=Path(refs['workRoot'])
 cpp={str(source/r['path']) for r in policy['expectedNativeSourceManifest'] if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/'))};assert len(cpp)==62
 other={str(source/p) for p in ('host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/host_call.cpp','host-apis/wasi-0.2.3/sockets.cpp','host-apis/wasi-0.2.10/bindings/bindings.c','crates/rust-hooks/src/wrappers.cpp')}
 null=str(Path(metadata['cmakeCachePath']).parent/'starling-raw.wasm/null.cpp')
 assert len(database)==len({r['file'] for r in database})==68 and {r['file'] for r in database}==cpp|other|{null}
 commands={r['file']:r['command'] for r in database};combined=metadata['combinedNativeSourcePolicy']
 assert set(combined['actualPolicyCppCompileCommands'])=={commands[p] for p in cpp}
 assert set(combined['actualOtherConfiguredCompileCommands'])=={commands[p] for p in other}
 assert combined['actualGeneratedNullCompileCommands']==[commands[null]]
 for name,count in (('strictEventExceptionPolicy',4),('classicStreamsPolicy',6)):
  key='actualNativeCompileCommands' if name=='strictEventExceptionPolicy' else 'actualPrivateTargetCompileCommands'
  assert len(metadata[name][key])==count and set(metadata[name][key]) <= {commands[p] for p in cpp}
 for field,name in (('actualHostApiCompileCommands','host-apis/wasi-0.2.0/host_api.cpp'),('actualEventLoopCompileCommands','runtime/event_loop.cpp')):
  assert metadata['taskSelectionPolicy'][field]==[commands[str(source/name)]]
 assert len(metadata['actualEmbeddingCompileCommands'])==1 and metadata['actualEmbeddingCompileCommands']==combined['actualSeparateEmbeddingCompileCommands']
 for row in database:
  words=shlex.split(row['command']);assert words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==row['file'] and '-fsyntax-only' not in words
  assert [w for w in words if w.startswith('-O')]==['-O3'] and '-DNDEBUG' in words
  assert not any(w.startswith(('-DDEBUG','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','@')) for w in words)
  expected_include=0 if row['file']==null else 1;assert words.count('-include')==expected_include
  if expected_include:assert words[words.index('-include')+1]==str(work/'spidermonkey-dist-release/include/js-confdefs.h')

def peer_model(value,own):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'
 assert value['freezerSourceIndexSha256']==own['sha256'] and value['nativeSourceIndexSha256']==SOURCE_SHA
 assert value['sourceOnly'] is value['sourceReviewPassed'] is True
 for name in ('ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked'):assert value[name] is False

def root_model(value,own,refs):
 assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_FREEZE_V1' and value['phase']=='freeze' and value['variant']=='normal-off'
 assert value['nativeSourceIndexSha256']==SOURCE_SHA and value['freezerIndex']==own
 for key in ('configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot'):assert value[key]==refs[key]
 for key,n in COUNTS.items():assert value[key]==n
 assert value['freezeAllowed'] is value['readOnlySourceAdmissionAllowed'] is value['postBuildNinjaCommandsAllowed'] is True
 assert value['externalParentDeadlineSeconds']==2400 and value['requiredStartFreeBytes']==2147483648 and value['gcStress'] is False and value['entropyMode']=='OFF'
 for key in ('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):assert value[key] is False
 for key in ('actualFreezeResult','independentFreezeReview','reviewedEnginePins','runtimeAuthority'):assert value[key] is None
 for key in ('actualBuildReview','actualBuildContract','actualBuildResult','actualBuildRootObservation','engine','metadata'):assert value[key]==refs[key]

def recheck(frame):
 require_frame(frame)
 for row in frame['captured'].values():checked(row)
 for ix in frame['families']:family(ix)
 for row in frame['refs']['referenceAliases']:
  p=Path(row['path']);assert p.is_symlink() and os.readlink(p)==row['linkText'] and str(p.resolve(strict=True))==row['resolved']
 for row in frame['refs']['declaredArchiveHardlinks']:
  a,b=Path(row['path']).stat(),Path(row['target']).stat();assert row['sameInode'] is True and (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)
 for row in frame['protection']['files']:
  s=checked(row['descriptor']).stat();assert stat.S_IMODE(s.st_mode)==row['mode'] and s.st_nlink==row['nlink']
 for row in frame['protection']['modePairs']:
  a,b=checked(row['copy']).stat(),checked(row['original']).stat();assert stat.S_IMODE(a.st_mode)==row['copyMode'] and stat.S_IMODE(b.st_mode)==row['originalMode'] and (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 for row in frame['protection']['trees']:
  root=Path(row['root']);assert root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==row['mode']
  files=set();links={}
  for path in root.rglob('*'):
   name=path.relative_to(root).as_posix()
   if path.is_symlink():links[name]=os.readlink(path)
   elif path.is_file():files.add(name)
  assert files==set(row['files']) and links==row['links']

def authorize(config_row):
 assert __debug__ and sys.dont_write_bytecode and Path(__file__).resolve()==OWN/'entry.py'
 assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'))
 config=read(config_row);assert config['schemaVersion']==1;own=config['freezerIndex'];assert own['path']==str(OWN/'index.json')
 own_rows=family(own);refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
 assert config['nativeSourceIndex']==refs['nativeSourceIndex'] and config['nativeSourceIndex']['path']==str(PROPOSAL/'index.json') and config['nativeSourceIndex']['sha256']==SOURCE_SHA
 root=read(config['rootAuthority']);root_model(root,own,refs);assert root['entry'] in own_rows and root['entry']['path']==str(OWN/'entry.py')
 source_rows=family(config['nativeSourceIndex'])
 frame=Frame(_token=_TOKEN,config=config,configRow=config_row,root=root,refs=refs,captured={},families=[own,config['nativeSourceIndex']],ownRows=own_rows,protection=dict(files=[],modePairs=[],trees=[]))
 try:
  for row in [config_row,config['rootAuthority'],*own_rows,*source_rows]:add(frame,row)
  for item in refs['families']:
   frame['families'].append(item['index'])
   for row in family(item['index']):add(frame,row)
  for row in refs['files']:add(frame,row)
  peer=root['sourceIndependentReview'];peer_rows=family(peer['index']);assert peer['result'] in peer_rows;peer_model(read(peer['result']),own)
  frame['families'].append(peer['index'])
  for row in peer_rows:add(frame,row)
  build=read(refs['actualBuildReview']['result']);contract=read(refs['actualBuildContract'])
  assert build['schemaVersion']==1 and build['state']=='INDEPENDENT_COMBINED355_NATIVE_BUILD_V2_RESULTS_REVIEW_PASSED_V1' and build['verifiedPassed'] is True
  assert build['nativeSourceIndexSha256']==SOURCE_SHA and build['controllerSourceIndexSha256']==refs['buildControllerIndex']['sha256']
  for key,value in contract['requiredFixedValues'].items():assert build[key]==value,key
  for key,row in refs['buildProofDescriptors'].items():assert build[key]==row,key
  assert build['coverage']==contract['requiredCoverage'] and refs['verifiedBuildReferenceCount']==build['coverage']['uniqueActualInputFiles']
  assert refs['buildInputLedger']==build['inputHashes'] and refs['referenceAliasWitness']==build['referenceAliases']
  alias_values=read(refs['referenceAliasWitness']);assert alias_values['symlinks']==refs['referenceAliases'] and alias_values['archiveHardlinks']==refs['declaredArchiveHardlinks']
  for key,value in contract['requiredExactDescriptors'].items():assert build[key]==value,key
  actual_build=read(refs['actualBuildResult']);assert actual_build['configuredSourceRoot']==str(SOURCE) and actual_build['workRoot']==str(WORK) and actual_build['freezeRoot']==str(FREEZE)
  ledger=read(refs['buildInputLedger']);assert len(ledger['files'])==refs['verifiedBuildReferenceCount']
  for item in ledger['files']:add(frame,{k:item[k] for k in ('path','sha256','bytes')})
  protection=read(next(r for r in own_rows if r['path']==str(OWN/'protection.json')))
  for row in protection['files']:add(frame,row['descriptor'])
  for row in protection['modePairs']:add(frame,row['copy']);add(frame,row['original'])
  frame['protection']=protection
  for row in refs['referenceAliases']:add(frame,next(r for r in ledger['files'] if r['path']==row['resolved']))
  plan=read(next(r for r in own_rows if r['path']==str(OWN/'capture-plan.json')));names=set()
  for row in plan['copies']:
   name=row['destination'];assert name and not name.startswith('/') and '\\' not in name and all(p not in ('','.','..') for p in name.split('/')) and name not in names;names.add(name);add(frame,row['source'])
  assert plan['baseCopies']==len(plan['copies']) and plan['verifiedReferenceCount']==refs['verifiedBuildReferenceCount']
  metadata=read(refs['metadata']);policy=read(refs['policy']);database=read(refs['compileCommands'])
  metadata_model(metadata,policy,refs);compilation_model(database,metadata,policy,refs)
  assert [read(dict(path=str(SOURCE/row['path']),sha256=row['sha256'],bytes=(SOURCE/row['path']).stat().st_size)) for row in metadata['selectedModuleManifests']]==refs['selectedManifestValues']
  cache={}
  for line in checked(refs['cmakeCache']).read_text().splitlines():
   key,colon,tail=line.partition(':')
   if colon and '=' in tail:cache[key]=tail.partition('=')[2]
  assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions'] and all(cache.get(k)==v for k,v in metadata['observedCMakeOptions'].items())
  assert cache['CMAKE_HOME_DIRECTORY']==refs['externalSourceRoot'] and cache['CMAKE_BUILD_TYPE']=='Release'
  assert Path(sys.executable).resolve(strict=True)==Path(refs['python']['path']);checked(refs['python']);checked(refs['ninja'])
  for role in ('configuredModel','layer','recipe','rustupBeforeRecord','rustupCurrentSettings'):add(frame,refs[role])
  # Treat the 368-byte before record as opaque historical JSON DATA: its nested
  # 57-byte setting was superseded by real rustup install; never rehash that path.
  before=read(refs['rustupBeforeRecord']);assert before==refs['rustupBeforeValue']
  assert checked(refs['rustupCurrentSettings']).read_bytes()==refs['rustupCurrentSettingsText'].encode('utf8')
  frame.update(metadata=metadata,policy=policy,database=database);recheck(frame);return frame
 finally:
  if frame['captured']:recheck(frame)

def load_own(frame,name):
 require_frame(frame);row=next(r for r in frame['ownRows'] if r['path']==str(OWN/name));checked(row);recheck(frame)
 spec=importlib.util.spec_from_file_location('combined355_freezer_'+name.replace('.','_'),row['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main(mode,config_row):
 frame=authorize(config_row)
 try:
  if mode=='parent':
   assert not EXTERNAL.exists() and not EXTERNAL.is_symlink() and not FREEZE.exists() and not FREEZE.is_symlink()
   monitor=load_own(frame,'monitor.py');EXTERNAL.mkdir(mode=0o700)
   argv=[frame['refs']['python']['path'],'-B','-I',str(OWN/'entry.py'),'freeze',json.dumps(config_row,separators=(',',':'))]
   terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},EXTERNAL,2400,frame['config']['rootAuthority']);recheck(frame)
   assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True and not terminal['forcedCleanup'] and not terminal['timeout'] and not terminal['errors'] and not terminal['signals'] and not terminal['interruptedSignals'] and terminal['remainingObservedPids']==[]
   return terminal
  if mode=='freeze':return load_own(frame,'freeze.py').freeze(frame,sys.modules[__name__])
  if mode=='admit':return load_own(frame,'admission.py').admit(frame,sys.modules[__name__])
  raise ValueError('finite phase')
 finally:recheck(frame)
if __name__=='__main__':
 assert len(sys.argv)==3 and sys.argv[1] in ('parent','freeze','admit')
 print(json.dumps(main(sys.argv[1],json.loads(sys.argv[2]))),flush=True)
