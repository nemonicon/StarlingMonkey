"""Owned read/hash/JSON/compiler-text reader; no project import or subprocess.

Invoke only after Root supplies completed freeze+verification+collector evidence.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,sys,tarfile
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
PACKET=FAMILY/'native-integration-candidate-v2'
SOURCE=Path('/tmp/starling-node-compat/consumers-source-v2').resolve()
STAGED=SOURCE/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'
FROZEN=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze')
WORK=Path('/tmp/starling-node-compat/consumers-v2-build')
INDEX='9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
ENGINE='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60'
META='9668b23dbac34f3e835b59f339f9a40504153eb03cdd149f0a761cb99ed77b49'
RECIPE='3a5fa8cd58d3948c373b59ff486eae5792ae7ec1b51ed47f43f4edc5b39b4c68'
POLICY='f174d2e38cfe5f9a3de268ff04468cdc57abcdfb33f7577962690cfcbe12df98'
HELPER='21f7be307c0fd2f34ce7dbd1cfdb433a7965a5f02c45c78290b4705fd0796448'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXTERNAL={'embedding/embedding.cpp':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205','embedding/embedding.h':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e','CMakeLists.txt':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
ARCHIVE='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'
SYMBOLS=['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']
MUTABLE={}
MUTABLE_READ_REQUESTS=[]
seen={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,h=None,size=None,anchor=None,capture=True):
 p=Path(path)
 if str(p)in MUTABLE:
  MUTABLE_READ_REQUESTS.append({'originalRequestedPath':str(p),'readIndependentPreGCWitness':str(MUTABLE[str(p)])});p=MUTABLE[str(p)]
 assert p.is_absolute()and'..'not in p.parts,p
 if anchor is not None:
  anchor=Path(anchor);p.relative_to(anchor);cursor=p
  while True:
   assert not cursor.is_symlink(),cursor
   if cursor==anchor:break
   cursor=cursor.parent
 a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink(),p;digest=hashlib.sha256();chunks=[]if capture else None
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):
   digest.update(block)
   if capture:chunks.append(block)
 z=p.lstat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),p
 assert h is None or digest.hexdigest()==h,p;assert size is None or z.st_size==size,p
 row={'path':str(p),'sha256':digest.hexdigest(),'bytes':z.st_size};assert str(p)not in seen or seen[str(p)]==row,p;seen[str(p)]=row
 return b''.join(chunks)if capture else row
def doc(path,h=None,anchor=None):return json.loads(read(path,h,anchor=anchor))
def relative(n):
 assert isinstance(n,str)and n and not Path(n).is_absolute()and all(x not in('','.','..')for x in n.split('/'))and'\\'not in n and'\0'not in n
 return n
def inventory(rows,count=None):
 assert count is None or len(rows)==count;d={}
 for row in rows:
  assert set(row)=={'path','sha256'};n=relative(row['path']);assert n not in d;assert re.fullmatch('[a-f0-9]{64}',row['sha256']);d[n]=row['sha256']
 return d
def indexed(root,h,count=None):
 value=doc(root/'index.json',h,root)
 assert count is None or len(value['files'])==count
 for row in value['files']:read(root/relative(row['path']),row['sha256'],row['bytes'],root,capture=False)
 return value
def macro(words,name,enabled):
 assert '-D'not in words and'-U'not in words
 actual=[w for w in words if w=='-D'+name or w.startswith('-D'+name+'=')]
 assert actual==(['-D'+name+'=1']if enabled else[]),name
 assert '-U'+name not in words,name
def no_codec(words,include=None):
 flattened=[]
 for word in words:flattened.extend(word[4:].split(',')if word.startswith('-Wl,')else[word])
 for i,word in enumerate(flattened):
  assert word not in['-lz','-lzlib','-l:libz.a','-l:libzlib.a','--library=z','--library=zlib']
  if word in['-l','--library']:assert i+1<len(flattened)and flattened[i+1]not in['z','zlib',':libz.a',':libzlib.a']
  assert not re.search(r'(?:^|/)libz(?:lib)?\.(?:a|so|dylib)$',word)
 for word in words:
  assert not word.startswith(('-DZ_PREFIX','-UZ_PREFIX','-imacros','-Wp,','-Xclang','-Xpreprocessor'))
  if word=='-include'and include is not None:continue
  assert not word.startswith('-include')
 if include is not None:
  assert words.count('-include')==1 and words[words.index('-include')+1]==include
def compiled(command,path,private,zlib,embedding,include):
 words=shlex.split(command);assert words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==path
 assert '--target=wasm32-wasi'in words and'-fsyntax-only'not in words
 assert[w for w in words if w.startswith('-O')]==['-O3']
 assert[w for w in words if w=='-DNDEBUG'or w.startswith('-DNDEBUG=')]==['-DNDEBUG']
 assert '-UNDEBUG'not in words and'-UDEBUG'not in words and not any(w.startswith('-DDEBUG')for w in words)
 assert[w for w in words if w.startswith('-flto')]==([]if embedding else['-flto=thin'])
 for name in['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY']:macro(words,name,True)
 macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',True);macro(words,'NODE_COMPAT_OOM_TESTING',False)
 macro(words,'NODE_COMPAT_GC_STRESS',False);macro(words,'NODE_COMPAT_STREAM_CONSUMERS',private);macro(words,'NODE_COMPAT_CLASSIC_STREAMS',private);macro(words,'NODE_COMPAT_ZLIB',zlib);macro(words,'NODE_COMPAT_STREAM_WEB',zlib)
 no_codec(words,include);return words
def without_dependency_flags(words):
 out=[];i=0
 while i<len(words):
  if words[i]in['-MD','-MMD']:i+=1
  elif words[i]in['-MT','-MF','-MQ']:assert i+1<len(words);i+=2
  else:out.append(words[i]);i+=1
 return out

ROOT_SHA='0866e4b8d76a4c89225b07124874587c29b0ecce8de7c6992eaa5f164a8615b8'
FREEZE_SHA='3180f5b8a81d77cc2dab80cdeb31d6f0922c9fefb4b1ac8ee43c4ad1e70c5040'
assert not(HERE/'results.json').exists()
root=doc(FAMILY/'native-integration-v2-normal-runtime-root-results.json',ROOT_SHA)
assert root['rawExitCodes']=={'build':0,'freeze':0,'readOnlyVerify':0}
assert root['rootObservedSessions']=={'build':7122,'freezeAndReadOnlyVerify':80421}
references=root['references'];assert len(references)==12
for row in references:read(Path(row['path']).resolve(),row['sha256'],row['bytes'],capture=False)
LOGS=WORK.parent/'consumers355-v2-normal-runtime-build-root'
for name,pid in [('terminal.json',80946),('freeze.terminal.json',2217),('verify.terminal.json',2236)]:
 terminal=doc(LOGS/name);assert terminal['rawExitCode']==0 and terminal['pid']==pid and terminal['observedByRoot']is True
 for key in ['stdout','stderr']:read(Path(terminal[key]['path']),terminal[key]['sha256'],terminal[key]['bytes'],capture=False)
 assert read(Path(terminal['stderr']['path']))==b''
owner=indexed(PACKET,INDEX,59);indexed(STAGED,INDEX,59)
indexed(FAMILY/'independent-native-integration-v2-source-review-v1','283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811',8)
indexed(FAMILY/'independent-native-integration-v2-stage-review-v1','371b7880092b3c825a6ead23a75e1ac88a7c343abe3e44e28fc93461d1e1b64d',14)
normal_peer=FAMILY/'independent-native-consumers-v2-normal-off-review-v1'
indexed(normal_peer,'b80489f4f00f731e4da22ecf04b47332974649fa94c5f56d11901859a1124d6c',18)
normal_proof=doc(normal_peer/'results.json','e58bad5ccdbddd9047657a252cfe7b5a4e29a93a5885221a58c91ff0c0a7bd09')
normal_metadata=doc(FROZEN/'normal-off.engine.wasm.build.json','860e95213953e26f96ca74946495a9719253f05cbca6c221a9b4b44d83962f92')
normal_freeze=doc(FROZEN/'normal-off-freeze-receipt.json','fadc83cebd3aae34b8dc67f479ecfd3b5b1cc4294750ce98ce3b45aacf226096')
assert normal_proof['state']=='INDEPENDENT_CONSUMERS355_V2_NORMAL_OFF_NATIVE_FREEZE_PASSED_NO_GUEST'
assert normal_proof['sourceIndexSha256']==INDEX and normal_proof['opensslCompleteSourcesIndependentlyRehashed']==4650
for row in normal_freeze['copies']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
policy=doc(PACKET/'policy.json',POLICY);tools=doc(PACKET/'artifact-tools/tool-pins.json')
native=inventory(policy['expectedNativeSourceManifest'],355);assert len(tools['toolDependencies'])==767
for name,h in native.items():read(SOURCE/name,h,anchor=SOURCE,capture=False)
for row in tools['toolDependencies']:read(SOURCE/relative(row['path']),row['sha256'],row['bytes'],SOURCE,capture=False)
preparation=doc(PACKET/'input-freeze.json');assert len(preparation['inputs'])==3420 and preparation['originalPreparationRoot']==str(PACKET)
assert preparation['originalPrepRowsMustNeverBeReinterpretedInStagedActionHelpers']is True
assert len(preparation['inputs'])==3420  # Original-context proof inherited by exact source-index hash.
for name in['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(PACKET/name)['variants'].values())
f=doc(FROZEN/'normal-runtime-freeze-receipt.json',FREEZE_SHA,FROZEN)
m=doc(FROZEN/'normal-runtime.engine.wasm.build.json',META,FROZEN)
assert f['schema']==1 and f['state']=='immutable-consumers-release-engine-frozen'
for k,v in{'label':'normal-runtime','engineSha256':ENGINE,'engineBytes':10009523,'receiptSha256':META,'nativeInputsVerified':355,'externalEmbeddingInputsVerified':3,'recipeSha256':RECIPE,'actualLayoutCompileCommands':62,'actualStrictCompileCommands':4,'actualEmbeddingCompileCommands':1,'actualClassicPrivateCompileCommands':6,'entropyPolicy':'runtime-only','gcStress':False,'zlibEnabled':True,'classicStreamsEnabled':True,'guestExecutedByHelper':False,'allInputsValidatedBeforeCopies':True,'allCopiesAndOriginalsRehashed':True}.items():assert f[k]==v,k
assert m['buildRecipeSha256']==RECIPE and m['engineSha256']==ENGINE and m['engineBytes']==10009523
assert inventory(m['sourceManifest'],355)==native and inventory(m['componentizeSourceManifest'],3)==EXTERNAL
for k in['profileEnabled','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','classicStreamsEnabled','zlibEnabled','internalTicksEnabled','strictInitialization','protectedAbortListenerEnabled','sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:assert m[k]is True,k
for k in['oomTesting','debuggerEnabled','wptSupportEnabled']:assert m[k]is False,k
assert m['entropyPolicy']=='runtime-only'and m['hostApi']=='wasi-0.2.10'and not m.get('diagnosticOnly',False)and not m.get('syntheticMetadataOnly',False)
assert m['classicTraceSourcePolicy']==policy['classicTraceSourcePolicy']==f['classicTraceSourcePolicy']
assert m['zlibSourcePolicy']==policy['zlibSourcePolicy']==f['zlibSourcePolicy']
engine_path=Path(m['enginePath']);assert str(engine_path)==f['originalEngine'];assert read(engine_path,ENGINE,10009523,capture=False)
assert read(Path(f['originalMetadataPath']),META)==read(FROZEN/'normal-runtime.engine.wasm.build.json',META)
assert read(FROZEN/'normal-runtime.engine.wasm',ENGINE,10009523,FROZEN)[:8]==b'\0asm\x01\0\0\0'

copies={}
for row in f['copies']:
 name=str(Path(row['path']).relative_to(FROZEN));relative(name);assert name not in copies;copies[name]=row
 read(FROZEN/name,row['sha256'],row['bytes'],FROZEN,capture=False)
 if row['original']is not None:
  original=Path(row['original']);read(original,row['sha256'],row['bytes'],capture=False)
  assert(original.stat().st_dev,original.stat().st_ino)!=((FROZEN/name).stat().st_dev,(FROZEN/name).stat().st_ino)
 assert(FROZEN/name).stat().st_nlink==1
planned={}
def plan(name,h,original=None,shared=False):
 relative(name);value={'sha256':h,'original':str(original)if original is not None else None,'shared':shared}
 assert name not in planned or planned[name]==value,name;planned[name]=value
for suffix,h,path in[('.engine.wasm',ENGINE,engine_path),('.engine.wasm.build.json',META,Path(f['originalMetadataPath'])),('-CMakeCache.txt',m['cmakeCacheSha256'],Path(m['cmakeCachePath'])),('-compile_commands.json',m['compileCommandsSha256'],Path(m['compileCommandsPath']))]:plan('normal-runtime'+suffix,h,path)
embedding_evidence=f['postBuildEmbeddingEvidence'];assert embedding_evidence['exitCode']==0 and embedding_evidence['beforeBuildCaptureExists']is False
plan('normal-runtime-embedding.after.commands.txt',embedding_evidence['sha256'])
admission=doc(Path(f['sourceAdmission']['path']),f['sourceAdmission']['sha256'],FROZEN);plan('normal-runtime-source-admission.json',f['sourceAdmission']['sha256'])
assert admission['state']=='ACTUAL_FINITE_CONSUMERS_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'and admission['sourceFiles']==355
assert admission['validationBootstrapOnly']is True and admission['operationalAdmission']is False and admission['engineBytesRead']is admission['guestExecuted']is False
assert admission['policySha256']==POLICY and admission['toolDependenciesVerified']==767
assert admission['selectedManifestPaths']==[row['path']for row in m['selectedModuleManifests']]
assert len(m['selectedModuleManifests'])==11 and admission['coreExpectations']['coreVersion']==f['coreVersion']=='sm-node-22.14.0-m0.11'
for row in m['selectedModuleManifests']:assert native[row['path']]==row['sha256']
for name,h in f['coreSources'].items():assert native[name]==h
for name,h in native.items():plan('source/'+name,h,SOURCE/name,True)
build=Path(m['cmakeCachePath']).parent
cache={}
for line in read(FROZEN/'normal-runtime-CMakeCache.txt',m['cmakeCacheSha256']).decode().splitlines():
 key,colon,rest=line.partition(':')
 if colon and'='in rest:assert key not in cache;cache[key]=rest.partition('=')[2]
assert m['requestedCMakeOptions']==m['observedCMakeOptions']==f['observedCMakeOptions']
for k,v in m['observedCMakeOptions'].items():assert cache[k]==v,k
assert cache['CMAKE_BUILD_TYPE']=='Release'and cache['CMAKE_EXE_LINKER_FLAGS']==''and cache['WEVAL']=='OFF'and cache['USE_WASM_OPT']=='ON'
assert not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE','')and cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF')=='OFF'
external=Path(cache['CMAKE_HOME_DIRECTORY'])
for name,h in EXTERNAL.items():read(external/name,h,capture=False);plan('componentize-source/'+name,h,external/name,True)
for name,h,path in[('build-engine.sh',RECIPE,SOURCE/'tests/node-compat/build-engine.sh'),('source-policy.json',POLICY,STAGED/'policy.json'),('source-policy-helper.py',HELPER,STAGED/'layer-policy.py'),('tooling/wasi_snapshot_preview1.wasm',ADAPTER,SOURCE/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm')]:plan(name,h,path,True)
assert f['toolDependencyClosure']==[{'sourcePath':row['path'],'path':str(FROZEN/'tooling/repository'/row['path']),'sha256':row['sha256'],'bytes':row['bytes']}for row in tools['toolDependencies']]
for row in tools['toolDependencies']:plan('tooling/repository/'+row['path'],row['sha256'],SOURCE/row['path'],True)

w=m['zlibPolicy']['codecWitness'];selected=m['zlibSelectedCodecInput']
assert selected==w['selectedCompileInput']and selected['selectedDistribution']==w['selectedDistribution']
assert selected['archive']==w['archive']==f['codecArchiveReference']
assert selected['archive']['sha256']==ARCHIVE and selected['archive']['bytes']==538170426
read(Path(selected['archive']['path']),ARCHIVE,538170426,capture=False)
headers={'zlib.h':('8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829),'zconf.h':('61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600),'mozzconf.h':('c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855),'js-confdefs.h':('841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)}
assert selected['headers']==w['headers']and len(selected['headers'])==4
for row in selected['headers']:assert(row['sha256'],row['bytes'])==headers[Path(row['path']).name];read(Path(row['path']),row['sha256'],row['bytes'])
assert selected['requiredForcedInclude']==selected['headers'][-1];include=selected['requiredForcedInclude']['path']
assert w['version']=='sm-selected-moz-z-codec-source-link-witness-v1'and w['sourceInputsCheckedBeforeAndAfterBuild']is True and w['guestExecuted']is False
assert w['runtimeBackendProof']==m['zlibPolicy']['runtimeBackendProof']==f['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
before=doc(Path(w['beforeManifestPath']),w['beforeManifestSha256']);assert before['schemaVersion']==1 and before['state']=='CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD'
for k in['archive','headers','install']:assert before[k]==w[k]
codec_files=[]
for n,row in enumerate(w['witnessFiles']):
 name='normal-runtime-codec/'+str(n)+'-'+Path(row['path']).name;plan(name,row['sha256'],Path(row['path']))
 codec_files.append({'original':row['path'],'path':str(FROZEN/name),'sha256':row['sha256'],'bytes':row['bytes']})
assert len(codec_files)==9 and codec_files==f['codecWitnessFiles']
install=read(Path(w['install']['path']),w['install']['sha256'],w['install']['bytes']).decode();assert install.count('NS_DEF(builtins::node_compat)')==1
assert 'diagnostics::'not in install
assert install.count('NS_DEF(builtins::web::text_codec)')==1 and install.index('NS_DEF(builtins::web::text_codec)')<install.index('NS_DEF(builtins::node_compat)')
assert m['streamConsumersPolicy']['installationOrder']['path']==w['install']['path']and m['streamConsumersPolicy']['installationOrder']['sha256']==w['install']['sha256']
db=doc(FROZEN/'normal-runtime-compile_commands.json',m['compileCommandsSha256']);mapped={}
cpp={name for name in native if name.endswith('.cpp')and name.startswith(('builtins/','runtime/'))};assert len(cpp)==62
for row in db:
 if row['file'].startswith((str(SOURCE/'builtins')+'/',str(SOURCE/'runtime')+'/'))and row['file'].endswith('.cpp'):
  name=str(Path(row['file']).relative_to(SOURCE));assert name in cpp and name not in mapped;mapped[name]=row['command']
assert set(mapped)==cpp and len(mapped)==62
private=set(policy['privateTargetCpp']);assert len(private)==6
for name,command in mapped.items():compiled(command,str(SOURCE/name),name in private,name.startswith('builtins/node-compat/'),False,include)
layout=list(mapped.values());ticks=m['internalTickPolicy'];classic=m['classicStreamsPolicy'];strict=m['strictEventExceptionPolicy'];protected=m['protectedAbortListenerPolicy']
contract=doc(PACKET/'admission-pins.json');parent=doc(SOURCE/'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json',contract['parentPolicySha256'])
parent_pins=doc(SOURCE/'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json',contract['parentAdmissionPinsSha256'])
assert policy['parentExpectedNativeSourceManifest']==parent['expectedNativeSourceManifest']
assert strict['parentSourcePolicy']==parent_pins['parentStrict']and protected['parentSourcePolicy']==parent_pins['parentProtected']
def composed(mapping):
 value=dict(mapping)
 for layer in[parent,policy]:
  for name,h in list(value.items()):
   if name in layer['sourceLayer']:
    entry=layer['sourceLayer'][name];assert entry['beforeSha256']==h;value[name]=entry['afterSha256']
 return value
strict_sources=composed(parent_pins['parentStrict']['nativeSourceSha256'])
for name in['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h']:strict_sources[name]=parent['sourceLayer'][name]['afterSha256']
assert strict['nativeSourceSha256']==strict_sources and protected['sourceSha256']==composed(parent_pins['parentProtected']['sourceSha256'])
assert strict['version']==policy['strictPolicyVersion']and protected['version']==policy['protectedPolicyVersion']and protected['strictPolicyVersion']==strict['version']
for name in['patchSha256','basePolicy','embeddingBoundaryPatchSha256']:assert strict[name]==parent_pins['parentStrict'][name]
assert protected['patchSha256']==parent_pins['parentProtected']['patchSha256']and protected['prerequisiteCMakeOptions']==parent_pins['prerequisiteCMakeOptions']
assert ticks['version']==policy['version']and ticks['sourcePolicyInstalled']is ticks['enabled']is True
for name,value in{'parentRecipeSha256':policy['parentRecipeSha256'],'parentNativeManifestCanonicalSha256':policy['parentNativeManifestCanonicalSha256'],'parentPrivateTickPolicyFileSha256':contract['parentPolicySha256'],'parentPrivateTickHelperSha256':contract['parentHelperSha256'],'nativePatchSha256':policy['nativePatchSha256'],'embeddingPatchSha256':policy['embedding']['patchSha256'],'embeddingBeforeSha256':policy['embedding']['beforeSha256'],'embeddingAfterSha256':policy['embedding']['afterSha256'],'policyFileSha256':POLICY,'helperSha256':HELPER}.items():assert ticks[name]==value,name
assert ticks['sourceLayer']==policy['sourceLayer']and ticks['limits']==parent['limits']and ticks['addsExternalCapabilities']is ticks['publicProcessModule']is False
assert classic['version']==policy['classicPolicyVersion']and classic['enabled']is True
for name,value in{'policyFileSha256':POLICY,'helperSha256':HELPER,'parentRecipeSha256':policy['parentRecipeSha256'],'parentSourceManifestCanonicalSha256':policy['parentNativeManifestCanonicalSha256'],'nativePatchSha256':policy['nativePatchSha256'],'moduleManifest':policy['classicManifest'],'addedSourcePaths':policy['classicAddedSourcePaths']}.items():assert classic[name]==value,name
assert classic['addsExternalCapabilities']is classic['publicProcessModule']is False
assert m['zlibPolicy']['version']=='sm-bounded-zlib-install-v1'and m['zlibPolicy']['policyFileSha256']==POLICY and m['zlibPolicy']['helperSha256']==HELPER
assert m['zlibPolicy']['moduleManifest']==policy['zlibManifest']and m['zlibPolicy']['moduleManifestSha256']==policy['zlibManifestSha256']and m['zlibPolicy']['requiredHostInterfaces']==[]
assert layout==ticks['actualLayoutCompileCommands']==protected['actualLayoutCompileCommands']
assert ticks['actualQueueCompileCommands']==[mapped['runtime/node_tick_queue.cpp']]
strict_names={'runtime/engine.cpp','runtime/event_loop.cpp','runtime/node_tick_queue.cpp','builtins/web/event/event-target.cpp'}
assert sorted(strict['actualNativeCompileCommands'])==sorted(mapped[name]for name in strict_names)
assert sorted(classic['actualPrivateTargetCompileCommands'])==sorted(mapped[name]for name in private)
assert m['actualRegistrationCompileCommands']==classic['actualRegistrationCompileCommands']==[mapped['builtins/node-compat/register.cpp']]
assert m['zlibPolicy']['actualKernelCompileCommands']==w['actualKernelCompileCommands']==[mapped['builtins/node-compat/zlib/kernel.cpp']]
kernel_words=shlex.split(mapped['builtins/node-compat/zlib/kernel.cpp']);includes=[];at=0
while at<len(kernel_words):
 word=kernel_words[at]
 if word in['-I','-isystem']:at+=1;includes.append(kernel_words[at])
 elif word.startswith('-I')and len(word)>2:includes.append(word[2:])
 elif word.startswith('-isystem')and len(word)>8:includes.append(word[8:])
 at+=1
assert w['actualHeaderSearchDirectories']==[includes]
candidates=[Path(name)/'zlib.h'for name in includes if(Path(name)/'zlib.h').is_file()]
assert candidates and candidates[0]==Path(selected['selectedDistribution'])/'include/zlib.h'
assert m['actualStreamWebKernelCompileCommands']==[mapped['builtins/node-compat/stream-web-kernel.cpp']]
assert not any(row['file']==str(external/'embedding/embedding.cpp')for row in db)
embedding_raw=read(Path(embedding_evidence['path']),embedding_evidence['sha256'],embedding_evidence['bytes']).decode()
embedding=[]
for line in embedding_raw.splitlines():
 words=shlex.split(line)
 if words.count('-c')==1 and words[words.index('-c')+1]==str(external/'embedding/embedding.cpp'):embedding.append(line)
assert len(embedding)==1 and embedding==embedding_evidence['compileCommands']==m['actualEmbeddingCompileCommands']==ticks['actualEmbeddingCompileCommands']==protected['actualEmbeddingCompileCommands']
compiled(embedding[0],str(external/'embedding/embedding.cpp'),False,False,True,include)
link=w['postBuildLinkEvidence'];assert link['beforeBuildCaptureExists']is False and link['responseFiles']==[]
raw_link=read(Path(link['path']),link['sha256']);raw_lines=raw_link.decode().splitlines();matches=[(n+1,line)for n,line in enumerate(raw_lines)if'libspidermonkey.a'in line and' -c 'not in line]
assert len(matches)==1;link_number,line=matches[0];groups=[shlex.split(part)for part in line.split(' && ')];assert len(groups)==4 and groups[0]==[':']
compiler,cd,optimizer=groups[1:];assert compiler[0]==str(build/'cxx-wrapper')and compiler.count('-o')==1 and not any(word.startswith('@')for word in compiler)
no_codec(compiler);assert str(selected['archive']['path'])in compiler
output=build/compiler[compiler.index('-o')+1];assert cd==['cd',str(output.parent)]and optimizer==[str(WORK/'cache/binaryen/1b13/bin/wasm-opt'),'--strip-debug','-O3','-o',output.name,output.name]
assert[w for w in compiler if w.startswith('-O')]==['-O3']and'-DNDEBUG'in compiler and[w for w in compiler if w.startswith('-flto')]==['-flto=thin']
assert not any('--threads'in word or'--thinlto-jobs'in word for word in compiler)
expected_link={'rawCommand':line,'expandedArguments':compiler,'kind':'compiler-cd-inplace-wasm-opt-v1','compilerArguments':compiler,'compilerExpandedArguments':compiler,'compilerOutputPath':str(output),'postOptimizerArguments':optimizer,'postOptimizerWorkingDirectory':cd[1],'postOptimizerInputPath':str(output),'postOptimizerOutputPath':str(output),'sameWasmOutputProved':True}
assert link['commands']==[expected_link]
for name,command in mapped.items():
 found=[]
 for line in raw_lines:
  words=shlex.split(line)
  if words.count('-c')==1 and words[words.index('-c')+1]==str(SOURCE/name):found.append(without_dependency_flags(words))
 assert found==[without_dependency_flags(shlex.split(command))],name
assert embedding[0]in raw_lines
nm=w['archiveSymbolEvidence'];assert nm['exitCode']==0 and nm['nm']['sha256']=='0f0dfccb3778ec756b3bcbfe69574cdddfb2a6da2ae92c5bc1df1d1d6d3a591c'
read(Path(nm['nm']['path']),nm['nm']['sha256'],nm['nm']['bytes'],capture=False)
nmfile=next(row for row in w['witnessFiles']if Path(row['path']).name=='nm.stdout.txt');nm_lines=read(Path(nmfile['path']),nmfile['sha256'],nmfile['bytes']).decode().splitlines();symbols={}
for name in SYMBOLS:
 found=[line for line in nm_lines if re.search(r'(?:^|\s)MOZ_Z_'+re.escape(name)+r'\s+T\s',line)];assert len(found)==1;symbols[name]=found[0]
 assert not any(re.search(r'(?:^|\s)(?:z_)?'+re.escape(name)+r'\s+[A-Za-z]\s',line)for line in nm_lines)
assert symbols==nm['selectedDefinitions']
nm_stderr=next(row for row in w['witnessFiles']if Path(row['path']).name=='nm.stderr.txt')
nm_diagnostic=read(Path(nm_stderr['path']),nm_stderr['sha256'],nm_stderr['bytes']).decode()
assert nm_diagnostic==str(selected['archive']['path'])+'[MmapFaultHandler.o]: no symbols\n'
assert nm['command']==[nm['nm']['path'],'--defined-only','--extern-only','--format=posix','--print-file-name',selected['archive']['path']]

rust=m['generatedRustProject'];ssl=m['openssl'];audit=ssl['completeSourceAudit']
dependencies={'Cargo.toml':(rust['manifestPath'],rust['manifestSha256']),'Cargo.lock':(rust['lockPath'],rust['lockSha256']),'openssl-before.json':(audit['beforeReportPath'],audit['beforeReportSha256']),'openssl-receipt.txt':(ssl['receiptPath'],ssl['receiptSha256']),'openssl-configure.txt':(ssl['configureRecipe']['path'],ssl['configureRecipe']['sha256']),'openssl-configdata.pm':(ssl['configdata']['path'],ssl['configdata']['sha256']),'libcrypto.a':(ssl['library']['path'],ssl['library']['sha256'])}
for name,(path,h)in dependencies.items():plan('normal-runtime-'+name,h,Path(path))
assert rust['cargoBuildLocked']is rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
assert rust['lockSha256']==rust['versionedLockSha256']==native['runtime/crates/staticlib-template/Cargo.lock']
assert all('--locked'in shlex.split(command)for command in rust['actualCargoBuildCommands'])
before_ssl=doc(FROZEN/'normal-runtime-openssl-before.json',audit['beforeReportSha256']);assert audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True
for k,v in before_ssl.items():assert audit[k]==v,k
assert audit['unexpectedFiles']==audit['missingFiles']==[]
assert audit['sourceManifestSha256']==normal_metadata['openssl']['completeSourceAudit']['sourceManifestSha256']
audit_build_fields={'beforeReportPath','beforeReportSha256','buildDirectory','sourceDirectory','receiptSha256'}
assert {k:v for k,v in audit.items()if k not in audit_build_fields}=={k:v for k,v in normal_metadata['openssl']['completeSourceAudit'].items()if k not in audit_build_fields}
assert ssl['sourceDir']!=normal_metadata['openssl']['sourceDir'] and ssl['sourceKey']!=normal_metadata['openssl']['sourceKey']
assert ssl['entropy']=='RUNTIME_ONLY' and ssl['randSeed']=='none' and ssl['profile']=='ON'
assert ssl['version']==normal_metadata['openssl']['version']

read(Path(audit['archivePath']),audit['archiveSha256'],capture=False)
expected_ssl={}
with tarfile.open(audit['archivePath'])as archive:
 for member in archive.getmembers():
  if not member.isfile():assert member.isdir();continue
  prefix,slash,name=member.name.partition('/');assert prefix=='openssl-3.0.17'and slash;relative(name)
  assert name not in expected_ssl
  expected_ssl[name]=audit['patchedSources'].get(name)or sha(archive.extractfile(member).read())
actual_ssl={}
for path in sorted(Path(ssl['sourceDir']).rglob('*')):
 assert not path.is_symlink()
 if path.is_file():actual_ssl[str(path.relative_to(ssl['sourceDir']))]=read(path,capture=False)['sha256']
assert actual_ssl==expected_ssl and len(actual_ssl)==4650
assert sha(json.dumps([{'path':name,'sha256':h}for name,h in sorted(actual_ssl.items())],separators=(',',':')).encode())==audit['sourceManifestSha256']

license_rows=[]
for original in sorted((SOURCE/'builtins/node-compat').rglob('*')):
 if original.is_file()and original.name.startswith(('LICENSE','NOTICE')):
  name=str(original.relative_to(SOURCE));h=read(original,capture=False)['sha256'];plan('source/'+name,h,original,True);license_rows.append({'path':name,'sha256':h})
license_path=Path(ssl['sourceDir'])/'LICENSE.txt';plan('dependency-licenses/openssl-LICENSE.txt',read(license_path,capture=False)['sha256'],license_path,True)
license_rows.append({'path':'dependency-licenses/openssl-LICENSE.txt','sha256':seen[str(license_path)]['sha256'],'sourceAuditFiles':4650});assert f['licenses']==license_rows
for name in['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:plan('artifact-tools/'+name,read(STAGED/'artifact-tools'/name,capture=False)['sha256'],STAGED/'artifact-tools'/name,True)
for original in sorted((STAGED/'artifact-tools/ancestry/production-artifacts-v1').iterdir()):assert original.is_file();plan('artifact-tools/ancestry/production-artifacts-v1/'+original.name,read(original,capture=False)['sha256'],original,True)
assert set(copies)==set(planned)
assert len(copies)==root['frozenCopies']and sum(row['original']is not None for row in copies.values())==root['originalInputEntries']
for name,expected in planned.items():
 row=copies[name];assert all(row[k]==v for k,v in expected.items()),name
actual_frozen={str(p.relative_to(FROZEN))for p in FROZEN.rglob('*')if p.is_file()or p.is_symlink()};assert set(copies)|{'normal-runtime-freeze-receipt.json'}<=actual_frozen
assert len(m['downloadedArchives'])==1
for row in m['downloadedArchives']:read(Path(row['path']),row['sha256'],capture=False)
assert m['downloadedArchives'][0]['sha256']==m['openssl']['completeSourceAudit']['archiveSha256']
for row in m['wasiSdkVersionFiles']:assert read(Path(row['path'])).decode()==row['contents']and'llvm-version: 21.1.4'in row['contents']
semantic=f['semanticSourceProvenance'];base=FROZEN/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'
assert semantic['correctedReceiptAnnotationBase']==str(base)and semantic['primaryPinsPath']==str(base/'primary-source-pins.json')and semantic['nodeMitNoticePath']==str(base/'LICENSE.node')
primary=doc(Path(semantic['primaryPinsPath']),semantic['primaryPinsSha256']);assert primary['release']=='v22.14.0'and len(primary['sources'])==3
for row in primary['sources']:assert row['url'].startswith('https://raw.githubusercontent.com/nodejs/node/v22.14.0/');read(base/relative(row['path']),row['sha256'],row['bytes'])
read(Path(semantic['nodeMitNoticePath']),semantic['nodeMitNoticeSha256'])
assert semantic['fixSourceIndexSha256']==m['classicTraceSourcePolicy']['fixSourceIndexSha256']
stem=engine_path.stem
assert doc(WORK/('source-inputs-'+stem+'.json'),m['sourceInputManifestSha256'])==m['sourceManifest']
assert doc(WORK/('componentize-native-inputs-'+stem+'.json'),m['componentizeInputManifestSha256'])==m['componentizeSourceManifest']
assert read(WORK/('recipe-'+stem+'.sha256')).decode().strip()==RECIPE
launchroot=FROZEN.parent/'builds/normal-runtime';launch=doc(launchroot/'result.json')
assert launch['rawChildExitCode']==launch['status']==launch['launcherExitCode']==0 and launch['evidenceComplete']is True
assert launch['recipeSha256']==RECIPE and launch['ownedGroupCleanup']['complete']is True and launch['lifecycleComplete']is True
assert launch['ownedGroupCleanup']['errors']==launch['launcherErrors']==[]and launch['stoppedForDiskSpace']is False
assert launch['temporarySigtermHandlerRestored']is True and launch['sigtermReceived']==0 and launch['guestExecutionRequested']is False
assert launch['requiredStartFreeBytes']==2147483648 and launch['stopBelowFreeBytes']==838860800
for name in['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']:assert launch['explicitEnvironment'][name]=='1'
assert launch['explicitEnvironment']['NODE_COMPAT_BUILD_ROOT']==str(WORK)and launch['explicitEnvironment']['NODE_COMPAT_BUILD_TYPE']=='Release'
build_log=read(launchroot/'build.log',launch['logSha256']).decode();assert'[108/108]'in build_log
assert m['streamConsumersEnabled']is f['streamConsumersEnabled']is True
assert m['streamConsumersSourcePolicy']==f['streamConsumersSourcePolicy']==policy['streamConsumersSourcePolicy']
consumer=m['streamConsumersPolicy']
assert consumer['enabled']is True and consumer['policyFileSha256']==POLICY and consumer['helperSha256']==HELPER
assert consumer['requiredHostInterfaces']==[] and consumer['prerequisiteCMakeOptions']=={'ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON'}
assert consumer['actualPrivateTargetCompileCommands']==classic['actualPrivateTargetCompileCommands']
assert consumer['actualRegistrationCompileCommands']==m['actualRegistrationCompileCommands']
assert consumer['aliasRegistrationTransactional']is False
assert consumer['nativeTextDecoderSource']==policy['streamConsumersSourcePolicy']['nativeTextDecoderSource']
assert native[consumer['nativeTextDecoderSource']['path']]==consumer['nativeTextDecoderSource']['sha256']
assert consumer['moduleManifest']=='builtins/node-compat/export-manifest.stream-consumers.node-v22.14.0.json'
assert native[consumer['moduleManifest']]==consumer['moduleManifestSha256']
assert cache['ENABLE_BUILTIN_WEB_TEXT_CODEC']=='ON'and cache['NODE_COMPAT_STREAM_CONSUMERS']=='ON'and cache['NODE_COMPAT_ZLIB']=='ON'
assert admission['options']['streamConsumersEnabled']is True and admission['options']['zlibEnabled']is True
assert root['runtimeBackendProof']==f['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
assert len(copies)==1164 and sum(row['original']is not None for row in copies.values())==1162
assert m['gcStress']is f['gcStress']is root['gcStress']is False
assert root['consumerEnabled']is True and root['zlibEnabled']is True
assert admission['options']['gcStress']is False
assert consumer['moduleManifest']in admission['selectedManifestPaths']
assert len(admission['selectedManifestPaths'])==11
assert m['sourceManifest']==normal_metadata['sourceManifest']and m['componentizeSourceManifest']==normal_metadata['componentizeSourceManifest']
assert m['streamConsumersSourcePolicy']==normal_metadata['streamConsumersSourcePolicy']and m['classicTraceSourcePolicy']==normal_metadata['classicTraceSourcePolicy']and m['zlibSourcePolicy']==normal_metadata['zlibSourcePolicy']
rust_path_fields={'manifestPath','lockPath','actualCargoBuildCommands'}
assert {k:v for k,v in rust.items()if k not in rust_path_fields}=={k:v for k,v in normal_metadata['generatedRustProject'].items()if k not in rust_path_fields}
assert m['buildTools']==normal_metadata['buildTools']
ssl_build_fields={'entropy','sourceKey','sourceDir','installDir','completeSourceAudit','receiptPath','receiptSha256','configureRecipe','configdata','library'}
assert {k:v for k,v in ssl.items()if k not in ssl_build_fields}=={k:v for k,v in normal_metadata['openssl'].items()if k not in ssl_build_fields}
configure_raw=read(Path(ssl['configureRecipe']['path']),ssl['configureRecipe']['sha256']).decode()
assert configure_raw==ssl['configureRecipe']['contents']
assert configure_raw.replace(str(build),str(Path(normal_metadata['cmakeCachePath']).parent)).replace(ssl['sourceKey'],normal_metadata['openssl']['sourceKey'])==normal_metadata['openssl']['configureRecipe']['contents']
assert link['command']==['ninja','-C',str(build),'-t','commands','starlingmonkey_embedding']
crypto_tokens=[word for word in compiler if word.endswith('/libcrypto.a')or word=='libcrypto.a']
assert len(crypto_tokens)==1 and (build/crypto_tokens[0]).resolve()==Path(ssl['library']['path']).resolve()
assert all(command in raw_lines for command in rust['actualCargoBuildCommands'])
assert selected==normal_metadata['zlibSelectedCodecInput']
assert {k:v for k,v in consumer['installationOrder'].items()if k!='path'}=={k:v for k,v in normal_metadata['streamConsumersPolicy']['installationOrder'].items()if k!='path'}
assert '.RUNTIME_ONLY.'in str(build)and '.OFF.'in normal_metadata['cmakeCachePath']
assert build!=Path(normal_metadata['cmakeCachePath']).parent
assert root['nativeBuildStepsObserved']==108
assert launch['explicitEnvironment']['NODE_COMPAT_STREAM_CONSUMERS']=='1'and launch['explicitEnvironment']['NODE_COMPAT_ZLIB']=='1'and launch['explicitEnvironment']['NODE_COMPAT_GC_STRESS']=='0'
assert launch['explicitEnvironment']['NODE_COMPAT_ENTROPY_MODE']=='RUNTIME_ONLY'
assert cache['NODE_COMPAT_ENTROPY_MODE']=='RUNTIME_ONLY'
assert admission['options']['entropyPolicy']=='runtime-only'
assert not MUTABLE and not MUTABLE_READ_REQUESTS
gc_peer=FAMILY/'independent-native-consumers-v2-gc-off-review-v1'
indexed(gc_peer,'010fbd51860a9425e5717fe8e1f73fcf5ede25ce2cacfef61b673e84f4a9db91',8)
gc_freeze=doc(FROZEN/'gc-off-freeze-receipt.json','0268e07355eeb331c53f14841573c5f9db56724da185b844b0ca53cecba1101e')
assert len(gc_freeze['copies'])==1164
for row in gc_freeze['copies']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)

disabled_peer=FAMILY/'independent-native-consumers-v2-disabled-off-review-v1'
indexed(disabled_peer,'6b5414f6fe74948a4d0591e21c3b69d66fe3230ad88b3a9deab1411783f35908',16)
disabled_freeze=doc(FROZEN/'disabled-off-freeze-receipt.json','9d6fd22252de089370ba104d39e15431283e8ed62a26514c66ff2af181e4a4e1')
for row in disabled_freeze['copies']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
authority=doc(FAMILY/'native-integration-v2-normal-runtime-build-root-review.json','decfa0d15271459936e69e26e9cfbedd9f414b3822c91f6e665682c2fd41505c')
for key in ['nativeProducerIndex','sourceInspectionTemplate','producerSourceReview','actualSourceStageReview','oldReviewedPins','oldThreeFrozenPrebuildCheckpoint']:
 row=authority[key];read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
assert authority['argv']==doc(LOGS/'terminal.json')['argv']
assert authority['nativeCodeRecipeOrOldToolContextChangesAllowed']is False and authority['oldThreeFrozenChangesAllowed']is False
checkpoint=doc(Path(authority['oldThreeFrozenPrebuildCheckpoint']['path']),authority['oldThreeFrozenPrebuildCheckpoint']['sha256'])
assert checkpoint['frozenRows']==len(checkpoint['files'])==3492
assert checkpoint['normalTwoHistoricalMutableOriginalsNotRestored']is True
old_sets={'normal-off':normal_freeze,'gc-off':gc_freeze,'disabled-off':disabled_freeze}
expected_checkpoint=[]
for label,old in old_sets.items():
 for row in old['copies']:expected_checkpoint.append({'label':label,**{k:row[k]for k in ['path','sha256','bytes']}})
assert checkpoint['files']==expected_checkpoint
for row in checkpoint['files']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
post=doc(Path(root['oldThreePostfreezeCheckpoint']['path']),root['oldThreePostfreezeCheckpoint']['sha256'])
assert post['rowsRehashed']==3492 and post['allMatched']is True and post['prebuildCheckpoint']==authority['oldThreeFrozenPrebuildCheckpoint']
original_closure=doc(Path(root['originalInputClosure']['path']),root['originalInputClosure']['sha256'])
assert original_closure['entries']==len(original_closure['files'])==1162
expected_originals=[{'path':row['original'],'sha256':row['sha256'],'bytes':row['bytes']}for row in f['copies']if row['original']is not None]
assert original_closure['files']==expected_originals
for row in original_closure['files']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
assert doc(Path(authority['oldReviewedPins']['path']))['variants']['normal-runtime']is None
assert root['checkedInRuntimePinStillNull']is True and root['guestOrComponentExecuted']is False and root['operationalAdmission']is False
assert sha(read(HERE.parent/'release-host-plan-v1/runtime-only-build.template.json'))=='096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1'

universal=read(STAGED/'artifact-tools/artifact_common.py').decode()
import ast
fn=next(n for n in ast.parse(universal).body if isinstance(n,ast.FunctionDef)and n.name=='verify_frozen_variant')
assert ast.unparse(fn.body[1])=='tool_dependencies(REPO)'
for row in list(seen.values()):read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
result={
 'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_V2_NORMAL_RUNTIME_NATIVE_FREEZE_PASSED_NO_GUEST',
 'sourceIndexSha256':INDEX,'rootReceiptSha256':ROOT_SHA,'freezeReceiptSha256':FREEZE_SHA,'metadataSha256':META,
 'engineSha256':ENGINE,'engineBytes':10009523,'recipeSha256':RECIPE,'policySha256':POLICY,'helperSha256':HELPER,
 'nativeSources':355,'externalEmbeddingSources':3,'toolDependencyRows':767,
 'frozenCopiesObserved':1164,'allRuntimeOriginalEntryReferencesRehashed':1162,'rootOriginalClosureExact':True,
 'oldThreeFrozenEntryReferencesRehashedUnchanged':3492,'normalMutableProjectOriginalsReopened':False,
 'configuredNativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,
 'runtimeOnlyMacroOnEveryNativeAndEmbeddingCompile':True,'consumerDefineOnExactSixPrivateCppAbsentEmbedding':True,'streamConsumersEnabled':True,
 'zlibEnabled':True,'gcStress':False,'entropyPolicy':'runtime-only','selectedManifests':11,'consumerManifestSelected':True,
 'separateRuntimeOnlySourceAndCmakeProject':True,'decoderNamespaceBeforeNodeObservedInCapturedInstall':True,
 'actualBuildStepsObservedInRootLog':108,'codecWitnessFiles':len(codec_files),'rawLinkCaptureBytes':len(raw_link),
 'rawLinkSelectedLineOneBased':link_number,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,
 'selectedMozZSymbolDefinitions':7,'selectedArchiveSha256':ARCHIVE,'selectedArchiveBytes':538170426,'headers':selected['headers'],
 'opensslCompleteSourcesIndependentlyRehashed':4650,'opensslSourceDirectoryDistinctFromOff':True,
 'opensslSourceManifestMatchesOff':True,'opensslSourceKey':ssl['sourceKey'],'opensslActualLibrary':ssl['library'],
 'opensslOwnRuntimeConfigSourceArchiveAndLibcryptoChecked':True,'cargoLockedAndCurrentRawCommandBound':True,
 'originalPreparationProofInheritedRows':3420,'originalPreparationBroadRehashRepeated':False,
 'sourceAdmissionRecordAuthenticatedNotRerun':True,'universalHelperAuthenticationBeforeCustomImports':True,
 'rootEvidenceReferences':12,'rootOuterRawStatusesObservedByThisReader':False,
 'operationalAdmissionOpen':False,'runtimeBackendProof':f['runtimeBackendProof'],
 'runtimeBootstrapPinsNull':True,'newActualReviewedPinIssuedByThisReader':False,
 'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerGuestsHostsOrTimingExecuted':False,
 'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteBlockers':[],
 'limitations':['Actual Release normal-runtime native build/freeze only; no new component/guest/host result.',
  'RuntimeOnly native macro/config evidence is not an observed final component random-import or entropy behavior proof.',
  'All old3492 frozen rows remain exact; old normal two historical mutable cache/DB originals are not reopened or relabelled.',
  'The shared355/3420 preparation source proof is inherited by exact source/native review hashes; the new RuntimeOnly4650-file OpenSSL source tree is independently rehashed.',
  'No codec runtime version, GC/root isolation, reset/ALS/request reuse, TLS, full Node support, statistical or performance claim.',
  'Root outer statuses are authenticated records, not directly observed events; captured compiler driver is not a separate LLD argv/thread observation.',
  'Old3 authority and checked-in NULL documents remain unchanged; a new explicit Root overlay is still required.'],
 'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:result[k]for k in['state','frozenCopiesObserved','allRuntimeOriginalEntryReferencesRehashed','oldThreeFrozenEntryReferencesRehashedUnchanged','configuredNativeCompileCommands','selectedManifests','opensslCompleteSourcesIndependentlyRehashed']}))
