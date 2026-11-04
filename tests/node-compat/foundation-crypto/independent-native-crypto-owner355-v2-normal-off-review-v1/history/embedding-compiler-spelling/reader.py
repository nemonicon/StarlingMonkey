"""Owned read/hash/JSON/compiler-text reader; no project import or subprocess.

Invoke only after Root supplies completed freeze+verification+collector evidence.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,sys,tarfile,struct
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
PACKET=FAMILY/'native-integration-candidate-v2'
SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')
STAGED=SOURCE/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
FROZEN=Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
WORK=Path('/tmp/starling-node-compat/crypto-owner-v2-build')
INDEX='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
ENGINE='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05'
META='8bafca1a1a76168eebe2bbbb6cd774215db43a3c44c3a8ce9253d0152373ca37'
RECIPE='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3'
POLICY='5a3bd48ebac975f7a3fd72691432b34c0e4afb9eec33bd2ad6273d78225193f9'
HELPER='4e5a1019ceffea629f2ec0b42322e17444cb877519596cb273ea34464d15bd78'
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
 for name in['NODE_COMPAT_GC_STRESS','NODE_COMPAT_ENTROPY_RUNTIME_ONLY','NODE_COMPAT_OOM_TESTING']:macro(words,name,False)
 macro(words,'NODE_COMPAT_STREAM_CONSUMERS',private);macro(words,'NODE_COMPAT_CLASSIC_STREAMS',private);macro(words,'NODE_COMPAT_ZLIB',zlib);macro(words,'NODE_COMPAT_STREAM_WEB',zlib)
 no_codec(words,include);return words
def without_dependency_flags(words):
 out=[];i=0
 while i<len(words):
  if words[i]in['-MD','-MMD']:i+=1
  elif words[i]in['-MT','-MF','-MQ']:assert i+1<len(words);i+=2
  else:out.append(words[i]);i+=1
 return out

ROOT_SHA='88cfe19d16f09f0dba109d6e0b3923000116be286102ee6d4c20ca60d48d4bba'
FREEZE_SHA='d088286c6eadc20a7262a06fd804c9e2c597c7959a2d15762306c442161f7760'
assert not(HERE/'results.json').exists()
root=doc(FAMILY/'native-freezer-v1-normal-off-root-results.json',ROOT_SHA)
def descriptors(value):
 if isinstance(value,dict):
  if set(value)=={'path','sha256','bytes'}:read(Path(value['path']),value['sha256'],value['bytes'],capture=False)
  else:
   for child in value.values():descriptors(child)
 elif isinstance(value,list):
  for child in value:descriptors(child)
descriptors(root)
buildroot=doc(Path(root['completedBuildResult']['path']),root['completedBuildResult']['sha256']);descriptors(buildroot)
terminals=[]
for role,descriptor in [('build',buildroot['externalTerminal']),('freeze',root['actualFreezeTerminal']),('verify',root['actualVerificationTerminal'])]:
 terminal=doc(Path(descriptor['path']),descriptor['sha256']);descriptors(terminal)
 assert terminal['rawExitCode']==0 and terminal['timeout']is False
 assert read(Path(terminal['stderr']['path']),terminal['stderr']['sha256'],terminal['stderr']['bytes'])==b''
 terminals.append({'role':role,**terminal,'observedByThisReader':False})
assert [t['pid']for t in terminals]==[53008,79054,80524]
assert root['freezeRootSessionId']==25578 and root['verifyRootSessionId']==43902 and buildroot['rootSessionId']==62629
owner=indexed(PACKET,INDEX,44);indexed(STAGED,INDEX,44)
indexed(FAMILY/'independent-crypto-owner355-native-integration-v2-source-review-v1','ebbfda800fc288ea249b9c2e3af2f77a6a0ae1153bc9586b9aab91999a060dac',8)
indexed(FAMILY/'independent-native-integration-v2-stage-review-v1','8c0583a4863bc33b74b500ffe026d67fce2258985eb562b5f895a76636541c79',8)
amendment=FAMILY/'native-freezer-source-amendment-v1'
indexed(amendment,'0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd',13)
indexed(FAMILY/'independent-native-freezer-source-review-v1','aa25647e8d918b23d3b13d8d14d3da566d42ad9921d174d3dcbd87e1c8b4a06b',7)
policy=doc(PACKET/'policy.json',POLICY);tools=doc(PACKET/'artifact-tools/tool-pins.json')
native=inventory(policy['expectedNativeSourceManifest'],355);assert len(tools['toolDependencies'])==922
for name,h in native.items():read(SOURCE/name,h,anchor=SOURCE,capture=False)
for row in tools['toolDependencies']:read(SOURCE/relative(row['path']),row['sha256'],row['bytes'],SOURCE,capture=False)
preparation=doc(PACKET/'input-freeze.json');assert len(preparation['files'])==1323 and preparation['parentPreparationManifestsFollowed']is False
for row in preparation['files']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
for name in['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(PACKET/name)['variants'].values())
f=doc(FROZEN/'normal-off-freeze-receipt.json',FREEZE_SHA,FROZEN)
m=doc(FROZEN/'normal-off.engine.wasm.build.json',META,FROZEN)
assert f['schema']==1 and f['state']=='immutable-crypto-owner-release-engine-frozen'
for k,v in{'label':'normal-off','engineSha256':ENGINE,'engineBytes':10002820,'receiptSha256':META,'nativeInputsVerified':355,'externalEmbeddingInputsVerified':3,'recipeSha256':RECIPE,'actualLayoutCompileCommands':62,'actualStrictCompileCommands':4,'actualEmbeddingCompileCommands':1,'actualClassicPrivateCompileCommands':6,'entropyPolicy':'off','gcStress':False,'zlibEnabled':True,'classicStreamsEnabled':True,'guestExecutedByHelper':False,'allInputsValidatedBeforeCopies':True,'allCopiesAndOriginalsRehashed':True}.items():assert f[k]==v,k
assert m['buildRecipeSha256']==RECIPE and m['engineSha256']==ENGINE and m['engineBytes']==10002820
assert inventory(m['sourceManifest'],355)==native and inventory(m['componentizeSourceManifest'],3)==EXTERNAL
for k in['profileEnabled','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','classicStreamsEnabled','zlibEnabled','internalTicksEnabled','strictInitialization','protectedAbortListenerEnabled','sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:assert m[k]is True,k
for k in['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:assert m[k]is False,k
assert m['entropyPolicy']=='off'and m['hostApi']=='wasi-0.2.10'and not m.get('diagnosticOnly',False)and not m.get('syntheticMetadataOnly',False)
assert m['classicTraceSourcePolicy']==policy['classicTraceSourcePolicy']==f['classicTraceSourcePolicy']
assert m['zlibSourcePolicy']==policy['zlibSourcePolicy']==f['zlibSourcePolicy']
engine_path=Path(f['originalEngine']);assert engine_path.resolve()==Path(m['enginePath']).resolve();assert read(engine_path,ENGINE,10002820,capture=False)
assert read(Path(f['originalMetadataPath']),META)==read(FROZEN/'normal-off.engine.wasm.build.json',META)
assert read(FROZEN/'normal-off.engine.wasm',ENGINE,10002820,FROZEN)[:8]==b'\0asm\x01\0\0\0'

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
for suffix,h,path in[('.engine.wasm',ENGINE,engine_path),('.engine.wasm.build.json',META,Path(f['originalMetadataPath'])),('-CMakeCache.txt',m['cmakeCacheSha256'],Path(m['cmakeCachePath'])),('-compile_commands.json',m['compileCommandsSha256'],Path(m['compileCommandsPath']))]:plan('normal-off'+suffix,h,path)
embedding_evidence=f['postBuildEmbeddingEvidence'];assert embedding_evidence['exitCode']==0 and embedding_evidence['beforeBuildCaptureExists']is False
plan('normal-off-embedding.after.commands.txt',embedding_evidence['sha256'])
admission=doc(Path(f['sourceAdmission']['path']),f['sourceAdmission']['sha256'],FROZEN);plan('normal-off-source-admission.json',f['sourceAdmission']['sha256'])
assert admission['state']=='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'and admission['sourceFiles']==355
assert admission['validationBootstrapOnly']is True and admission['operationalAdmission']is False and admission['engineBytesRead']is admission['guestExecuted']is False
assert admission['policySha256']==POLICY and admission['toolDependenciesVerified']==922
assert admission['selectedManifestPaths']==[row['path']for row in m['selectedModuleManifests']]
assert len(m['selectedModuleManifests'])==11 and admission['coreExpectations']['coreVersion']==f['coreVersion']=='sm-node-22.14.0-m0.11'
for row in m['selectedModuleManifests']:assert native[row['path']]==row['sha256']
for name,h in f['coreSources'].items():assert native[name]==h
for name,h in native.items():plan('source/'+name,h,SOURCE/name,True)
build=Path(m['cmakeCachePath']).parent
cache={}
for line in read(FROZEN/'normal-off-CMakeCache.txt',m['cmakeCacheSha256']).decode().splitlines():
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
 name='normal-off-codec/'+str(n)+'-'+Path(row['path']).name;plan(name,row['sha256'],Path(row['path']))
 codec_files.append({'original':row['path'],'path':str(FROZEN/name),'sha256':row['sha256'],'bytes':row['bytes']})
assert len(codec_files)==9 and codec_files==f['codecWitnessFiles']
install=read(Path(w['install']['path']),w['install']['sha256'],w['install']['bytes']).decode();assert install.count('NS_DEF(builtins::node_compat)')==1
assert 'diagnostics::'not in install
assert install.count('NS_DEF(builtins::web::text_codec)')==1 and install.index('NS_DEF(builtins::web::text_codec)')<install.index('NS_DEF(builtins::node_compat)')
assert m['streamConsumersPolicy']['installationOrder']['path']==w['install']['path']and m['streamConsumersPolicy']['installationOrder']['sha256']==w['install']['sha256']
db=doc(FROZEN/'normal-off-compile_commands.json',m['compileCommandsSha256']);mapped={}
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
for name,(path,h)in dependencies.items():plan('normal-off-'+name,h,Path(path))
assert rust['cargoBuildLocked']is rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
assert rust['lockSha256']==rust['versionedLockSha256']==native['runtime/crates/staticlib-template/Cargo.lock']
assert all('--locked'in shlex.split(command)for command in rust['actualCargoBuildCommands'])
before_ssl=doc(FROZEN/'normal-off-openssl-before.json',audit['beforeReportSha256']);assert audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True
for k,v in before_ssl.items():assert audit[k]==v,k
assert audit['unexpectedFiles']==audit['missingFiles']==[]
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
for name in['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:
 target='artifact-tools/donor-data/freeze-engine.py'if name=='freeze-engine.py'else'artifact-tools/'+name
 plan(target,read(STAGED/'artifact-tools'/name,capture=False)['sha256'],STAGED/'artifact-tools'/name,True)
plan('artifact-tools/freeze-engine.py',read(amendment/'freeze-engine.py',capture=False)['sha256'],amendment/'freeze-engine.py',True)
plan('artifact-tools/active-freezer/freezer-guard.py',read(amendment/'freezer-guard.py',capture=False)['sha256'],amendment/'freezer-guard.py',True)
correction=doc(FROZEN/'normal-off-freezer-correction-control.json',f['freezerSourceCorrection']['sha256'])
assert correction['state']=='ACTUAL_AUTHORIZED_CRYPTO_FREEZER_SOURCE_CORRECTION_CAPTURE'
assert correction['amendmentSourceIndex']['sha256']=='0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd'
assert correction['donorSourceIndexSha256']==INDEX and correction['configuredSourceRoot']==str(SOURCE) and correction['stagedArtifactToolsRoot']==str(STAGED/'artifact-tools') and correction['freezeRoot']==str(FROZEN)
assert correction['nativeRecipePolicyHelperAnd922ToolsUnchanged']is True and correction['engineExecuted']is False
descriptors(correction)
control_expected=[]
for source_index in[correction['amendmentSourceIndex'],{'path':str(PACKET/'index.json'),'sha256':INDEX,'bytes':(PACKET/'index.json').stat().st_size},correction['independentSourceReview']['index']]:
 control_expected.append(source_index)
 ix=doc(Path(source_index['path']),source_index['sha256']);base=Path(source_index['path']).parent
 for row in ix['files']:control_expected.append({'path':str(base/row['path']),'sha256':row['sha256'],'bytes':row['bytes']})
control_expected.append(correction['rootAuthority'])
assert len(correction['copies'])==len(control_expected)
for n,row in enumerate(control_expected):
 name='normal-off-freezer-correction-control/'+str(n)+'-'+Path(row['path']).name
 expected={'original':row['path'],'path':str(FROZEN/name),'sha256':row['sha256'],'bytes':row['bytes']}
 assert correction['copies'][n]==expected;plan(name,row['sha256'],Path(row['path']))
plan('normal-off-freezer-correction-control.json',f['freezerSourceCorrection']['sha256'])
for key,target,role in [('activeFreezerTooling','artifact-tools/freeze-engine.py','ACTUAL_ACTIVE_CORRECTED_FREEZER'),('donorFreezerTooling','artifact-tools/donor-data/freeze-engine.py','IMMUTABLE_STAGED_DONOR_DATA_NOT_ACTIVE')]:
 value=f[key];assert value['role']==role and Path(value['path']).resolve()==(FROZEN/target).resolve() and copies[target]['sha256']==value['sha256']
assert f['helperSha256']==f['activeFreezerTooling']['sha256']==correction['activeSource']['sha256']=='dc479abf2b703080dbaa7b8013a7be531ccd54015955afb1d48c645a89169613'
assert f['donorFreezerTooling']['sha256']==correction['donorSourceData']['sha256']=='44dd669ab05349514108dadf1a8a72eaae60d969335c8caaa80985a09eacc25f'
assert f['freezerSourceCorrection']['sourceIndexSha256']==correction['amendmentSourceIndex']['sha256']
assert root['activeFreezerTooling']==f['activeFreezerTooling']and root['donorFreezerTooling']==f['donorFreezerTooling']

for original in sorted((STAGED/'artifact-tools/ancestry/production-artifacts-v1').iterdir()):assert original.is_file();plan('artifact-tools/ancestry/production-artifacts-v1/'+original.name,read(original,capture=False)['sha256'],original,True)
assert set(copies)==set(planned)
assert len(copies)==root['frozenCopies']and sum(row['original']is not None for row in copies.values())==root['originalRowsRehashed']
for name,expected in planned.items():
 row=copies[name];assert all(row[k]==v for k,v in expected.items()),name
actual_frozen={str(p.relative_to(FROZEN))for p in FROZEN.rglob('*')if p.is_file()or p.is_symlink()};assert set(copies)|{'normal-off-freeze-receipt.json'}==actual_frozen
assert len(actual_frozen)==1391
assert not any(p.is_symlink()for p in FROZEN.rglob('*'))
for row in m['downloadedArchives']:read(Path(row['path']),row['sha256'],capture=False)
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
launchroot=FROZEN.parent/'builds/normal-off';launch=doc(launchroot/'result.json')
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
assert len(copies)==1390 and sum(row['original']is not None for row in copies.values())==1387
assert m['cryptoKeyOwnershipPolicy']==f['cryptoKeyOwnershipPolicy']==policy['cryptoKeyOwnershipSourcePolicy']
crypto=policy['cryptoKeyOwnershipSourcePolicy'];assert crypto['sourceFiles']==355 and crypto['changedSourceFiles']==5 and crypto['unchangedParentFiles']==350 and crypto['exactComposedEdits']==20
parent355=doc(SOURCE/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/policy.json',crypto['parent355PolicySha256'])
parent_native=inventory(parent355['expectedNativeSourceManifest'],355)
assert {name for name in native if native[name]!=parent_native[name]}=={row['path']for row in crypto['changes']}
for row in crypto['changes']:
 assert parent_native[row['path']]==row['beforeSha256']and native[row['path']]==row['afterSha256']
 read(Path(row['afterimage']),row['afterSha256'],row['bytes'],capture=False)
crypto_evidence=m['cryptoKeyOwnershipBuildEvidence']
assert cache['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'and crypto_evidence['cryptoBuiltinEnabled']is True
assert crypto_evidence['cachePath']==m['cmakeCachePath']and crypto_evidence['cacheSha256']==m['cmakeCacheSha256']
assert install.count('NS_DEF(builtins::web::crypto)')==1 and crypto_evidence['installationSource']=={'path':w['install']['path'],'sha256':w['install']['sha256'],'namespace':'NS_DEF(builtins::web::crypto)','count':1}
assert sorted(crypto_evidence['changedNativeCompileCommands'])==sorted(mapped[row['path']]for row in crypto['changes']if row['path'].endswith('.cpp'))and len(crypto_evidence['changedNativeCompileCommands'])==3
# Pure static GNU archive-index decoding, not nm, compiler or crypto execution.
archive_bytes=read(FROZEN/'normal-off-libcrypto.a',ssl['library']['sha256'],ssl['library']['bytes'])
assert archive_bytes[:8]==b'!<arch>\n';offset=8;ar_members={};symbol_index=None;long_names=b''
while offset<len(archive_bytes):
 header=archive_bytes[offset:offset+60];assert len(header)==60 and header[58:60]==b'`\n'
 name=header[:16].decode().strip();size=int(header[48:58]);payload=archive_bytes[offset+60:offset+60+size];assert len(payload)==size
 ar_members[offset]=(name,payload)
 if name=='/':symbol_index=payload
 if name=='//':long_names=payload
 offset+=60+size+(size%2)
assert offset==len(archive_bytes)and symbol_index is not None
symbol_count=struct.unpack('>I',symbol_index[:4])[0];member_offsets=struct.unpack('>'+str(symbol_count)+'I',symbol_index[4:4+4*symbol_count]);symbol_names=symbol_index[4+4*symbol_count:].split(b'\0')
crypto_archive_symbols={}
for name in['OPENSSL_cleanse','EVP_PKEY_free']:
 matches=[i for i,symbol in enumerate(symbol_names[:symbol_count])if symbol==name.encode()];assert len(matches)==1
 member_offset=member_offsets[matches[0]];member_name,payload=ar_members[member_offset]
 if member_name.startswith('/')and member_name[1:].isdigit():member_name=long_names[int(member_name[1:]):].split(b'/\n',1)[0].decode()
 assert payload[:8]==b'\0asm\x01\0\0\0'
 crypto_archive_symbols[name]={'archiveSha256':ssl['library']['sha256'],'gnuArchiveIndexSymbol':name,'memberOffset':member_offset,'memberName':member_name,'memberCoreWasmMagic':True,'runtimeExecuted':False}
link_crypto=[word for word in compiler if word.endswith('/libcrypto.a')];assert len(link_crypto)==1 and(build/link_crypto[0]).resolve()==Path(ssl['library']['path']).resolve()
assert 'starling-raw.wasm/libbuiltin_web_crypto.a'in compiler
assert ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and ssl['profile']=='ON'
assert audit['patchedSources']=={'crypto/uid.c':'86b53aecb1046e81dfbfe74d779704b408cbaa70abfb9a7d1cc98211bdc8ba08','crypto/rand/rand_lib.c':'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95'}
assert ssl['randPatchSha256']==native['deps/patches/rand.patch']
assert cache['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'and cache['CMAKE_EXE_LINKER_FLAGS']==''
verification=doc(Path(root['genuineVerificationResult']['path']),root['genuineVerificationResult']['sha256'])
assert verification['freezeReceipt']['sha256']==FREEZE_SHA and verification['engine']['sha256']==ENGINE and verification['metadata']['sha256']==META
assert verification['genuineConfiguredApiInvoked']=='verify_frozen_variant(normal-off,return_receipt_digest=True)'and verification['configuredSourceRoot']==str(SOURCE)
verify_source=read(Path(root['verificationEntrySource']['path']),root['verificationEntrySource']['sha256']).decode()
assert 'verify_frozen_variant'in verify_source and 'return_receipt_digest=True'in verify_source
root_reader_history=doc(Path(buildroot['priorRootReaderPreparationFailure']['path']),buildroot['priorRootReaderPreparationFailure']['sha256'])
assert root_reader_history['state'].find('READER')>=0 or 'reader'in str(root_reader_history).lower()
universal=read(STAGED/'artifact-tools/artifact_common.py').decode()
import ast
fn=next(n for n in ast.parse(universal).body if isinstance(n,ast.FunctionDef)and n.name=='verify_frozen_variant')
assert ast.unparse(fn.body[1])=='tool_dependencies(REPO)'
for name in['bootstrap-pins.json','runtime-pins.json']:assert all(value is None for value in doc(STAGED/name)['variants'].values())
# Additional current-SDK and original-stage binding; ordinary data reads only.
assert m['auditedBaseRevision']==m['starlingMonkeyRevision']=='54b3329b3ce818fd1f244e871e9c259b63667cda'and m['componentizeJsRevision']=='4d812f5a7b524cea5bcfd565cac55f3fab876a57'
assert m['archivePins']=={'componentizeJsSha256':'8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10','spiderMonkeySha256':'c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'}
read(WORK/'spidermonkey-release.tar.gz',m['archivePins']['spiderMonkeySha256'],capture=False)
wrapper=read(build/'cxx-wrapper').decode()
sdk=WORK/'cache/wasi-sdk/85e6'
assert 'PATH="'+str(SOURCE/'scripts')+':$PATH" '+str(sdk/'bin/clang++')+' "$@"'in wrapper
assert 'CMAKE_CXX_COMPILER'not in cache and cache['WASI_SDK_VERSION']=='30'
assert Path(cache['CMAKE_CXX_COMPILER_AR']).resolve()==(sdk/'bin/llvm-ar').resolve()
assert all(shlex.split(command)[0]==str(build/'cxx-wrapper')for command in list(mapped.values())+embedding)
sdk_archive=next(row for row in m['downloadedArchives']if Path(row['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz')
sdk_members={}
with tarfile.open(sdk_archive['path'])as archive:
 for name in['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/llvm-nm']:
  member=archive.getmember('wasi-sdk-30.0-arm64-macos/'+name)
  target=sdk/name
  if member.issym():assert target.is_symlink()and os.readlink(target)==member.linkname;sdk_members[name]={'symlinkTarget':member.linkname}
  else:
   assert member.isfile();raw=archive.extractfile(member).read();actual=read(target.resolve(),sha(raw),len(raw));sdk_members[name]={'sha256':sha(actual),'bytes':len(actual)}
assert sdk_members['bin/llvm-nm']['sha256']==nm['nm']['sha256']and sdk_members['bin/clang++']=={'symlinkTarget':'clang'}and sdk_members['bin/clang']=={'symlinkTarget':'clang-21'}
binaryen_archive=next(row for row in m['downloadedArchives']if Path(row['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
with tarfile.open(binaryen_archive['path'])as archive:
 member=next(row for row in archive.getmembers()if row.name.endswith('/bin/wasm-opt'));assert member.isfile();tool=archive.extractfile(member).read()
 optimizer_tool=read(Path(optimizer[0]),sha(tool),len(tool),capture=False)
stage_record=doc(Path(buildroot['sourceStageResult']['path']),buildroot['sourceStageResult']['sha256'])
assert len(stage_record['files'])==1311
for row in stage_record['files']:
 path=SOURCE/row['path'];original=Path(row['original']);assert stat.S_IMODE(path.stat().st_mode)==stat.S_IMODE(original.stat().st_mode)==row['sourceMode']==row['outputMode']
 assert(path.stat().st_dev,path.stat().st_ino)!=(original.stat().st_dev,original.stat().st_ino)
 read(path,row['sha256'],row['bytes'],SOURCE,capture=False)
assert verify_source.index('indexed(v[\'amendmentSource\'])')<verify_source.index('spec.loader.exec_module(common)')<verify_source.index("common.verify_frozen_variant('normal-off',return_receipt_digest=True)")
assert verify_source.index("for row in pins['toolDependencies']:")<verify_source.index('spec.loader.exec_module(common)')
extra={'selectedSdkVersion':m['wasiSdkVersionFiles'],'selectedSdkWrapper':seen[str(build/'cxx-wrapper')],'selectedSdkArchiveTools':sdk_members,'actualPostOptimizerTool':optimizer_tool,'staged1311SourceBytesModesAndDistinctInodesRechecked':True,'metadataOriginalEnginePathSpelling':m['enginePath'],'freezeOriginalEnginePathSpelling':f['originalEngine'],'enginePhysicalPathsEqual':Path(m['enginePath']).resolve()==Path(f['originalEngine']).resolve(),'rootGenuineVerifierControlFlowInspectedBeforeImportAndCall':True}
for row in list(seen.values()):read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
result={'schemaVersion':1,'state':'INDEPENDENT_CRYPTO_OWNER355_V2_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1','sourceIndexSha256':INDEX,'rootReceiptSha256':ROOT_SHA,'freezeReceiptSha256':FREEZE_SHA,'metadataSha256':META,'receiptSha256':META,'engineSha256':ENGINE,'engineBytes':10002820,'recipeSha256':RECIPE,'policySha256':POLICY,'helperSha256':HELPER,'nativeSources':355,'externalEmbeddingSources':3,'toolDependencyRows':922,'frozenCopiesObserved':1390,'actualFrozenRegularFiles':1391,'originalEntriesVerified':1387,'nativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,'changedNativePayloads':5,'unchangedParentNativePaths':350,'composedNativeEdits':20,'webCryptoEnabled':True,'cryptoInstallNamespaceCount':1,'changedCryptoCppCommands':3,'streamConsumersEnabled':True,'zlibEnabled':True,'entropyPolicy':'off','gcStress':False,'decoderNamespaceBeforeNodeObservedInCapturedInstall':True,'codecWitnessFiles':len(codec_files),'rawLinkCaptureBytes':len(raw_link),'rawLinkSelectedLineOneBased':link_number,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,'selectedMozZSymbolDefinitions':7,'selectedArchiveSha256':ARCHIVE,'selectedArchiveBytes':538170426,'headers':selected['headers'],'opensslCompleteSourcesIndependentlyRehashed':len(actual_ssl),'selectedLibcryptoArchiveSymbols':crypto_archive_symbols,'cargoBuildLocked':True,'sourcePreparationInputs':1323,'sourceAdmissionRecordAuthenticatedNotRerun':True,'universalHelperAuthenticationBeforeCustomImports':True,'rootOuterRawStatusesObservedByThisReader':False,'rootProcessRecords':terminals,'activeFreezerTooling':f['activeFreezerTooling'],'donorFreezerTooling':f['donorFreezerTooling'],'freezerSourceCorrection':f['freezerSourceCorrection'],'runtimeBackendProof':f['runtimeBackendProof'],'runtimeBootstrapPinsNull':True,'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerEnginesKeysCryptoGcGuestsHostsOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'performanceClaim':False,'sourcePromotionAllowed':False,'concreteBlockers':[],'limitations':['Completed native build/freeze/source/command provenance only; no key or crypto behavior, finalizer, complete zeroization, component/guest/host or runtime acceptance proof.','Root outer raw0 events are authenticated retained records, not directly observed terminals.','Selected SM archive is a current rehashed external reference, not duplicated in frozen copies.','GNU libcrypto archive index plus actual raw link records establishes static symbol/link provenance; it is not function execution or a private runtime proof.','Compiler/post-optimizer argv is independently reconstructed; spawned LLD child argv/thread count is not independently observed.','BIGNUM/private-copy/allocation-bound followons remain open.','No old355/350/classic runtime or Node parity proof is transferred.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
result.update(extra)
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:result[k]for k in['state','frozenCopiesObserved','originalEntriesVerified','nativeCompileCommands','opensslCompleteSourcesIndependentlyRehashed']}))
