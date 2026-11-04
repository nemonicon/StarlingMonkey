"""Owned read/hash/JSON/compiler-text reader; no project import or subprocess.

Invoke only after Root supplies completed freeze+verification+collector evidence.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,sys,tarfile
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
PACKET=FAMILY/'native-integration-candidate-v4'
SOURCE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve()
STAGED=SOURCE/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
FROZEN=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze')
WORK=Path('/tmp/starling-node-compat/zlib-v4-build')
INDEX='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
ENGINE='cd4df58c9c7cd13d93f42e4a3435ee17429d6b52445e02476aae0208ae9141df'
META='ebcdc404694d95663eb95a7c70609ccd62e99ec97818e156cf147c031da8c1a7'
RECIPE='4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'
POLICY='687298738c518e878cb17cf122b3979e2f58ea0ff14ac48f85146e8bf730fc8e'
HELPER='2c7ebd5841f50bebf4092275f64f698e909202b60db78e9f24b3725cdfae6747'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXTERNAL={'embedding/embedding.cpp':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205','embedding/embedding.h':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e','CMakeLists.txt':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
ARCHIVE='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'
SYMBOLS=['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']
seen={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,h=None,size=None,anchor=None,capture=True):
 p=Path(path);assert p.is_absolute()and'..'not in p.parts,p
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
 for name in['NODE_COMPAT_ENTROPY_RUNTIME_ONLY','NODE_COMPAT_OOM_TESTING']:macro(words,name,False)
 macro(words,'NODE_COMPAT_GC_STRESS',private)
 macro(words,'NODE_COMPAT_CLASSIC_STREAMS',private);macro(words,'NODE_COMPAT_ZLIB',zlib);macro(words,'NODE_COMPAT_STREAM_WEB',zlib)
 no_codec(words,include);return words
def without_dependency_flags(words):
 out=[];i=0
 while i<len(words):
  if words[i]in['-MD','-MMD']:i+=1
  elif words[i]in['-MT','-MF','-MQ']:assert i+1<len(words);i+=2
  else:out.append(words[i]);i+=1
 return out

assert len(sys.argv)==4,'Completed Root collector path, its caller SHA, and final freeze SHA required'
ROOT_PATH=Path(sys.argv[1]).resolve();ROOT_SHA=sys.argv[2];FREEZE_SHA=sys.argv[3]
assert all(re.fullmatch('[0-9a-f]{64}',h)for h in[ROOT_SHA,FREEZE_SHA])
assert not(HERE/'results.json').exists()
root=doc(ROOT_PATH,ROOT_SHA)
assert ROOT_SHA=='cd1ecea072b7a695092bfb09c448a3e934b6b5aec330a45d6d1c9ceb46aa0aef'
assert FREEZE_SHA=='91ab0b9ad5cf38d9c5812f1f528dc2f33f43250418cec3109f4835a3b8e09857'
assert root['state']=='ROOT_ZLIB_V4_GC_OFF_BUILD_FREEZE_AND_BOTH_FROZEN_VARIANTS_VERIFIED'
for name,value in{'buildRootSession':44299,'freezeRootSession':71826,'verifyRootSession':23840,'buildRawExit':0,'freezeRawExit':0,'verifyRawExit':0,'sourceIndexSha256':INDEX,'engineSha256':ENGINE,'engineBytes':9996844,'metadataReceiptSha256':META,'freezeReceiptSha256':FREEZE_SHA}.items():assert root[name]==value,name
assert root.get('guestExecuted',False)is False and root.get('runtimeAcceptanceClaim',False)is False
references=root.get('evidence',root.get('files'))
assert isinstance(references,list)and references
assert len(references)==15
for row in references:read(Path(row['path']).resolve(),row['sha256'],row['bytes'],capture=False)
for name in['build','freeze']:
 terminal=doc(WORK.parent/('zlib-v4-gc-off-'+name+'-v1.terminal.json'));assert terminal['returncode']==0
assert doc(WORK.parent/'zlib-v4-gc-normal-verify-v1.terminal.json')['returncode']==0
owner=indexed(PACKET,INDEX,85);indexed(STAGED,INDEX,85)
indexed(FAMILY/'independent-native-integration-v4-source-review-v1','31d5408eb5567f4e5e925811b33c4e8ec32ad28bb90bc3f844f23c65393145af',12)
indexed(FAMILY/'independent-native-integration-v4-stage-review-v1','5d857788b961eaab725959f6c262818b6b08dc2f32b49aa9c8edc6d9a8dd6273',9)
policy=doc(PACKET/'policy.json',POLICY);tools=doc(PACKET/'artifact-tools/tool-pins.json')
native=inventory(policy['expectedNativeSourceManifest'],350);assert len(tools['toolDependencies'])==632
for name,h in native.items():read(SOURCE/name,h,anchor=SOURCE,capture=False)
for row in tools['toolDependencies']:read(SOURCE/relative(row['path']),row['sha256'],row['bytes'],SOURCE,capture=False)
preparation=doc(PACKET/'input-freeze.json');assert len(preparation['inputs'])==2261 and preparation['originalPreparationRoot']==str(PACKET)
assert preparation['relocatedActionsMustNotReinterpretThesePaths']is True
for row in preparation['inputs']:read((PACKET/row['path']).resolve(),row['sha256'],row['bytes'],capture=False)
for name in['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(PACKET/name)['variants'].values())
f=doc(FROZEN/'gc-off-freeze-receipt.json',FREEZE_SHA,FROZEN)
m=doc(FROZEN/'gc-off.engine.wasm.build.json',META,FROZEN)
assert f['schema']==1 and f['state']=='immutable-zlib-release-engine-frozen'
for k,v in{'label':'gc-off','engineSha256':ENGINE,'engineBytes':9996844,'receiptSha256':META,'nativeInputsVerified':350,'externalEmbeddingInputsVerified':3,'recipeSha256':RECIPE,'actualLayoutCompileCommands':62,'actualStrictCompileCommands':4,'actualEmbeddingCompileCommands':1,'actualClassicPrivateCompileCommands':6,'entropyPolicy':'off','gcStress':True,'zlibEnabled':True,'classicStreamsEnabled':True,'guestExecutedByHelper':False,'allInputsValidatedBeforeCopies':True,'allCopiesAndOriginalsRehashed':True}.items():assert f[k]==v,k
assert m['buildRecipeSha256']==RECIPE and m['engineSha256']==ENGINE and m['engineBytes']==9996844
assert inventory(m['sourceManifest'],350)==native and inventory(m['componentizeSourceManifest'],3)==EXTERNAL
for k in['profileEnabled','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','classicStreamsEnabled','zlibEnabled','internalTicksEnabled','strictInitialization','protectedAbortListenerEnabled','sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:assert m[k]is True,k
for k in['oomTesting','debuggerEnabled','wptSupportEnabled']:assert m[k]is False,k
assert m['gcStress']is True and root['gcStress']is True
assert m['entropyPolicy']=='off'and m['hostApi']=='wasi-0.2.10'and not m.get('diagnosticOnly',False)and not m.get('syntheticMetadataOnly',False)
assert m['classicTraceSourcePolicy']==policy['classicTraceSourcePolicy']==f['classicTraceSourcePolicy']
assert m['zlibSourcePolicy']==policy['zlibSourcePolicy']==f['zlibSourcePolicy']
engine_path=Path(m['enginePath']);assert str(engine_path)==f['originalEngine'];assert read(engine_path,ENGINE,9996844,capture=False)
assert read(Path(f['originalMetadataPath']),META)==read(FROZEN/'gc-off.engine.wasm.build.json',META)
assert read(FROZEN/'gc-off.engine.wasm',ENGINE,9996844,FROZEN)[:8]==b'\0asm\x01\0\0\0'

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
for suffix,h,path in[('.engine.wasm',ENGINE,engine_path),('.engine.wasm.build.json',META,Path(f['originalMetadataPath'])),('-CMakeCache.txt',m['cmakeCacheSha256'],Path(m['cmakeCachePath'])),('-compile_commands.json',m['compileCommandsSha256'],Path(m['compileCommandsPath']))]:plan('gc-off'+suffix,h,path)
embedding_evidence=f['postBuildEmbeddingEvidence'];assert embedding_evidence['exitCode']==0 and embedding_evidence['beforeBuildCaptureExists']is False
plan('gc-off-embedding.after.commands.txt',embedding_evidence['sha256'])
admission=doc(Path(f['sourceAdmission']['path']),f['sourceAdmission']['sha256'],FROZEN);plan('gc-off-source-admission.json',f['sourceAdmission']['sha256'])
assert admission['state']=='ACTUAL_FINITE_ZLIB_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'and admission['sourceFiles']==350
assert admission['validationBootstrapOnly']is True and admission['operationalAdmission']is False and admission['engineBytesRead']is admission['guestExecuted']is False
assert admission['policySha256']==POLICY and admission['toolDependenciesVerified']==632
assert admission['selectedManifestPaths']==[row['path']for row in m['selectedModuleManifests']]
assert len(m['selectedModuleManifests'])==10 and admission['coreExpectations']['coreVersion']==f['coreVersion']=='sm-node-22.14.0-m0.11'
for row in m['selectedModuleManifests']:assert native[row['path']]==row['sha256']
for name,h in f['coreSources'].items():assert native[name]==h
for name,h in native.items():plan('source/'+name,h,SOURCE/name,True)
build=Path(m['cmakeCachePath']).parent
cache={}
for line in read(FROZEN/'gc-off-CMakeCache.txt',m['cmakeCacheSha256']).decode().splitlines():
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
 name='gc-off-codec/'+str(n)+'-'+Path(row['path']).name;plan(name,row['sha256'],Path(row['path']))
 codec_files.append({'original':row['path'],'path':str(FROZEN/name),'sha256':row['sha256'],'bytes':row['bytes']})
assert len(codec_files)==9 and codec_files==f['codecWitnessFiles']
install=read(Path(w['install']['path']),w['install']['sha256'],w['install']['bytes']).decode();assert install.count('NS_DEF(builtins::node_compat)')==1
assert 'diagnostics::'not in install
db=doc(FROZEN/'gc-off-compile_commands.json',m['compileCommandsSha256']);mapped={}
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
for name,(path,h)in dependencies.items():plan('gc-off-'+name,h,Path(path))
assert rust['cargoBuildLocked']is rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
assert rust['lockSha256']==rust['versionedLockSha256']==native['runtime/crates/staticlib-template/Cargo.lock']
assert all('--locked'in shlex.split(command)for command in rust['actualCargoBuildCommands'])
before_ssl=doc(FROZEN/'gc-off-openssl-before.json',audit['beforeReportSha256']);assert audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True
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
for name in['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:plan('artifact-tools/'+name,read(STAGED/'artifact-tools'/name,capture=False)['sha256'],STAGED/'artifact-tools'/name,True)
for original in sorted((STAGED/'artifact-tools/ancestry/production-artifacts-v1').iterdir()):assert original.is_file();plan('artifact-tools/ancestry/production-artifacts-v1/'+original.name,read(original,capture=False)['sha256'],original,True)
assert set(copies)==set(planned)
assert len(copies)==root['actualFrozenCopiesRehashed']and sum(row['original']is not None for row in copies.values())==root['actualCurrentOriginalReferencesRehashed']
for name,expected in planned.items():
 row=copies[name];assert all(row[k]==v for k,v in expected.items()),name
normal_receipt=doc(FROZEN/'normal-off-freeze-receipt.json','e5e705c886392bc5db137581b3492d72080e101460ec670f27281a1dbd964f11')
normal_meta=doc(FROZEN/'normal-off.engine.wasm.build.json','59942584d9aed799776913f158904abf6b4beb8feac04b56f28a813dfdced46e')
normal_expected_mutable={m['cmakeCachePath']:m['cmakeCacheSha256'],m['compileCommandsPath']:m['compileCommandsSha256']}
assert normal_meta['cmakeCachePath']==m['cmakeCachePath']and normal_meta['compileCommandsPath']==m['compileCommandsPath']
assert set(root['normalBuildCacheOriginalReferencesChangedByExpectedGCReconfiguration'])==set(normal_expected_mutable)
normal_copies={};normal_cache_changes=[];normal_unchanged_originals=0
for row in normal_receipt['copies']:
 name=str(Path(row['path']).relative_to(FROZEN));assert name not in normal_copies;normal_copies[name]=row
 read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
 if row['original']is not None:
  original=Path(row['original'])
  if row['original']in normal_expected_mutable:
   current=read(original,normal_expected_mutable[row['original']],capture=False)
   assert current['sha256']!=row['sha256']
   normal_cache_changes.append({'path':row['original'],'previousNormalHashPreservedInFrozenCopy':row['sha256'],'currentGcConfiguredHash':current['sha256'],'normalFrozenCopyPath':row['path']})
  else:
   read(original,row['sha256'],row['bytes'],capture=False);normal_unchanged_originals+=1
assert len(normal_copies)==root['normalFrozenCopiesRehashedAfterGC']==1024 and len(normal_cache_changes)==2 and normal_unchanged_originals==1020
assert normal_receipt['engineSha256']=='fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'and normal_meta['gcStress']is False
read(Path(normal_receipt['originalEngine']),normal_receipt['engineSha256'],9995295,capture=False)
indexed(FAMILY/'independent-native-zlib-v4-normal-off-review-v1','ba0451db576ed7ede8c39c6dadf7b22e37238c9c0ec0028edf019641467aeec0',8)
normal_root=doc(FAMILY/'native-integration-v4-normal-off-root-results.json','355f50b3a902d7d1d695ed8be10316ff3accb552af5b4d8ba867f6bb40aa947b')
for row in normal_root['evidence']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
actual_frozen={str(p.relative_to(FROZEN))for p in FROZEN.rglob('*')if p.is_file()or p.is_symlink()}
assert actual_frozen==set(copies)|set(normal_copies)|{'gc-off-freeze-receipt.json','normal-off-freeze-receipt.json'}
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
launchroot=FROZEN.parent/'builds/gc-off';launch=doc(launchroot/'result.json')
assert launch['rawChildExitCode']==launch['status']==launch['launcherExitCode']==0 and launch['evidenceComplete']is True
assert launch['recipeSha256']==RECIPE and launch['ownedGroupCleanup']['complete']is True and launch['lifecycleComplete']is True
assert launch['ownedGroupCleanup']['errors']==launch['launcherErrors']==[]and launch['stoppedForDiskSpace']is False
assert launch['temporarySigtermHandlerRestored']is True and launch['sigtermReceived']==0 and launch['guestExecutionRequested']is False
assert launch['requiredStartFreeBytes']==2147483648 and launch['stopBelowFreeBytes']==838860800
for name in['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']:assert launch['explicitEnvironment'][name]=='1'
assert launch['explicitEnvironment']['NODE_COMPAT_BUILD_ROOT']==str(WORK)and launch['explicitEnvironment']['NODE_COMPAT_BUILD_TYPE']=='Release'
assert launch['explicitEnvironment']['NODE_COMPAT_GC_STRESS']=='1'
assert launch['normalOffFrozenBeforeGCReconfigure']=={'path':str(FROZEN/'normal-off-freeze-receipt.json'),'sha256':'e5e705c886392bc5db137581b3492d72080e101460ec670f27281a1dbd964f11','engineSha256':'fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'}
build_log=read(launchroot/'build.log',launch['logSha256']).decode();assert'[17/17]'in build_log
failure=doc(FAMILY/'native-integration-v3-build-attempt1-failure-root-results.json','accf4b054401f214fae62feba67bacce0ead71ac3eead31187830c26550c9875')
for row in failure['evidence']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
assert failure['rawEngineAdmitted']is False
for row in list(seen.values()):read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_V4_GC_OFF_NATIVE_FREEZE_REVIEW_PASSED_NO_GUEST','sourceIndexSha256':INDEX,'rootReceiptSha256':ROOT_SHA,'freezeReceiptSha256':FREEZE_SHA,'metadataSha256':META,'engineSha256':ENGINE,'engineBytes':9996844,'recipeSha256':RECIPE,'policySha256':POLICY,'helperSha256':HELPER,'nativeSources':350,'externalEmbeddingSources':3,'toolDependencyRows':632,'frozenCopiesObserved':len(copies),'originalCopiesRehashed':sum(row['original']is not None for row in copies.values()),'nativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,'codecWitnessFiles':len(codec_files),'rawLinkCaptureBytes':len(raw_link),'rawLinkSelectedLineOneBased':link_number,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,'selectedMozZSymbolDefinitions':7,'selectedArchiveSha256':ARCHIVE,'selectedArchiveBytes':538170426,'headers':selected['headers'],'opensslCompleteSourcesIndependentlyRehashed':len(actual_ssl),'sourcePreparationInputs':2261,'rootEvidenceReferences':len(references),'gcStress':True,'gcMacroCompileCommands':sum('-DNODE_COMPAT_GC_STRESS=1'in shlex.split(command)for command in mapped.values()),'normalFrozenCopiesRehashedAfterGC':len(normal_copies),'normalUnchangedCurrentOriginalReferencesRehashed':normal_unchanged_originals,'normalMutableCacheOriginalExceptions':normal_cache_changes,'normalFrozenAndOriginalEngineUnchanged':True,'rootOuterRawStatusesObservedByThisReader':False,'sourceAdmissionRecordAuthenticatedNotRerun':True,'normalOperationalAdmissionOpen':False,'runtimeBackendProof':f['runtimeBackendProof'],'runtimeBootstrapPinsNull':True,'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerGuestsHostsOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteBlockers':[],'limitations':['This verifies completed GC native build/freeze and preserved normal frozen evidence, not guest GC ownership or codec execution, linked runtime version, component imports/exports, Node parity, GC/root isolation, reset/ALS/reuse or performance.','Raw Root build/freeze/verification terminal events are authenticated saved records, not observed by this reader.','Captured compiler/post-optimizer argv is checked; spawned LLD child argv/thread count is not independently observed.','The selected SM archive remains an external rehashed reference rather than a frozen archive copy.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:result[k]for k in['state','frozenCopiesObserved','originalCopiesRehashed','nativeCompileCommands','opensslCompleteSourcesIndependentlyRehashed']}))
