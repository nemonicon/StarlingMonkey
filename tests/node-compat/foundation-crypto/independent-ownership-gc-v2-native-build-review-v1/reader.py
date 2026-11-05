"""PRIVATE UNSEALED future BUILD-only data reader. Do not run on partial output.
Read/hash/JSON/tar/archive/compiler-text only. No owner imports or subprocess.
Produces intermediate DATA only; manual completed-outcome review seals any peer.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,struct,tarfile,sys
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto'
NATIVE=K/'ownership-gc-native-candidate-v2';SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source')
WORK=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build');BUILDOUT=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root')
SOURCE_SHA='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05';RECIPE='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3'
POLICY='5a3bd48ebac975f7a3fd72691432b34c0e4afb9eec33bd2ad6273d78225193f9';HELPER='4e5a1019ceffea629f2ec0b42322e17444cb877519596cb273ea34464d15bd78'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXTERNAL={'embedding/embedding.cpp':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205','embedding/embedding.h':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e','CMakeLists.txt':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
checks=0;seen={};cache={}
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def alias(p):return Path('/private'+str(p))if str(p).startswith('/tmp/')else Path(p)
def read(p,h=None,size=None,capture=True):
 p=Path(p);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute input');a=p.stat();real=str(p.resolve());digest=hashlib.sha256();parts=[]if capture else None
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):
   digest.update(b)
   if capture:parts.append(b)
 b=p.stat();need(identity(a)==identity(b),'stable input during stream');need(h is None or digest.hexdigest()==h,'exact SHA '+str(p));need(size is None or b.st_size==size,'exact bytes '+str(p))
 v=dict(path=str(p),sha256=digest.hexdigest(),bytes=b.st_size);need(str(p)not in seen or seen[str(p)]==v,'one exact descriptor per path');seen[str(p)]=v;cache[real]=identity(b)
 return b''.join(parts)if capture else v
def verify(r):return read(r['path'],r['sha256'],r['bytes'],False)
def data(r):return json.loads(read(r['path'],r['sha256'],r['bytes']))
def descriptor(p):return read(p,capture=False)
def family(r):
 x=data(r);names=set()
 for e in x['files']:
  n=e['path'];need(n and not n.startswith('/')and all(q not in ('','.','..')for q in n.split('/'))and n not in names,'safe unique source family member');names.add(n);read(Path(r['path']).parent/n,e['sha256'],e['bytes'],False)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'complete source family membership')
 return x

def macro(words,name,enabled):
 actual=[w for w in words if w=='-D'+name or w.startswith('-D'+name+'=')];need(actual==(['-D'+name+'=1']if enabled else[]),'exact macro '+name);need('-U'+name not in words,'no undef '+name)
def no_second_codec(words,include=None):
 flat=[]
 for w in words:flat.extend(w[4:].split(',')if w.startswith('-Wl,')else[w])
 for i,w in enumerate(flat):
  need(w not in ['-lz','-lzlib','-l:libz.a','-l:libzlib.a','--library=z','--library=zlib'],'no second zlib link')
  if w in ['-l','--library']:need(i+1<len(flat)and flat[i+1]not in ['z','zlib',':libz.a',':libzlib.a'],'no split second zlib link')
  need(not re.search(r'(?:^|/)libz(?:lib)?\.(?:a|so|dylib)$',w),'no second zlib archive')
 for w in words:
  need(not w.startswith(('-DZ_PREFIX','-UZ_PREFIX','-imacros','-Wp,','-Xclang','-Xpreprocessor')),'no compile context injection')
  if w=='-include'and include is not None:continue
  need(not w.startswith('-include'),'no unknown forced include')
 if include is not None:need(words.count('-include')==1 and words[words.index('-include')+1]==include,'exact selected header forced include')
def compiled(command,path,private,zlib,embedding,include):
 w=shlex.split(command);need(w.count('-c')==w.count('-o')==1 and w[w.index('-c')+1]==path,'exact compile input/output')
 need('--target=wasm32-wasi'in w and '-fsyntax-only'not in w,'actual wasm compile')
 need([v for v in w if v.startswith('-O')]==['-O3']and [v for v in w if v=='-DNDEBUG'or v.startswith('-DNDEBUG=')]==['-DNDEBUG'],'ordinary Release flags')
 need('-UNDEBUG'not in w and '-UDEBUG'not in w and not any(v.startswith('-DDEBUG')for v in w),'no debug')
 need([v for v in w if v.startswith('-flto')]==([]if embedding else['-flto=thin']),'native thinLTO/separate embedding noLTO')
 for n in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY']:macro(w,n,True)
 for n in ['NODE_COMPAT_ENTROPY_RUNTIME_ONLY','NODE_COMPAT_OOM_TESTING']:macro(w,n,False)
 for n in ['NODE_COMPAT_GC_STRESS','NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_STREAM_CONSUMERS']:macro(w,n,private)
 for n in ['NODE_COMPAT_ZLIB','NODE_COMPAT_STREAM_WEB']:macro(w,n,zlib)
 no_second_codec(w,include);return w
def strip_deps(w):
 out=[];i=0
 while i<len(w):
  if w[i]in ['-MD','-MMD']:i+=1
  elif w[i]in ['-MT','-MF','-MQ']:i+=2
  else:out.append(w[i]);i+=1
 return out

def audit(spec):
 need(spec['actualBuildOutcomeSuppliedByRoot']is True and spec['rootObservedToolRawExitCode']==0,'wait for real Root build completion')
 need(spec['sourceIndex']['sha256']==SOURCE_SHA,'exact native source');family(spec['sourceIndex']);family(spec['sourceReview']['index']);family(spec['controllerSourceIndex']);family(spec['controllerReview']['index']);family(spec['stageReview']['index'])
 authority=data(spec['rootBuildAuthority']);config=data(spec['rootBuildConfig']);outer=data(spec['externalParentTerminal']);built=data(spec['actualBuildResult']);root_observation=data(spec['rootBuildObservation'])
 need(config['sourceIndex']==spec['sourceIndex']and config['rootAuthority']==spec['rootBuildAuthority'],'exact config/source/Root binding')
 need(authority['phase']=='build'and authority['buildAllowed']is True and authority['sourceIndexSha256']==SOURCE_SHA and authority['configuredSourceRoot']==str(SOURCE)and authority['workRoot']==str(WORK)and authority['externalParentDeadlineSeconds']==7200,'actual Root build-only context/deadline')
 for n in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','normalMutationAllowed','nativeSourceChangesAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(authority[n]is False,'other actions closed '+n)
 need(outer['rawExitCode']==0 and outer['parentOwnedGroupGone']and outer['allObservedOwnedGroupsGone']and not outer['timeout']and not outer['forcedCleanup']and outer['remainingObservedPids']==[]and outer['signals']==outer['errors']==outer['interruptedSignals']==[],'actual7200 owned outer raw0/no forced cleanup')
 need(outer['authority']==spec['rootBuildAuthority'],'external terminal bound exact build Root')
 for n in ['stdout','stderr']:verify(outer[n])
 need(outer['stderr']['bytes']==0,'complete empty external stderr')
 need(built['state']=='native-build-completed-runtime-pending'and built['rawChildExitCode']==built['status']==built['launcherExitCode']==0 and built['evidenceComplete']and built['lifecycleComplete']and built['ownedGroupCleanup']['complete'],'actual inner owned native builder/bash raw0 and complete lifecycle')
 need(built['ownedGroupCleanup']['events']==[] and built['ownedGroupCleanup']['rawChildExitCode']==0 and built['temporarySigtermHandlerRestored']is True and built['stopReason']is None and built['childStarted']is True,'inner raw0 without forced signal/stop')
 need(json.loads(Path(outer['stdout']['path']).read_bytes())==dict(output=str(BUILDOUT),result=built),'whole raw native builder stdout equals actual result')
 need(built['rootAuthority']==spec['rootBuildAuthority']and built['sourceIndexSha256']==SOURCE_SHA and built['configuredSourceRoot']==str(SOURCE)and built['workRoot']==str(WORK),'inner source/Root/physical contexts')
 need(built['allOriginalNormalAndStageBytesPreserved']and built['ownedGroupCleanup']['errors']==built['launcherErrors']==[]and not built['stoppedForDiskSpace']and built['sigtermReceived']==0,'inner source protection/clean termination')
 need(built['requiredStartFreeBytes']==2*1024**3 and built['stopBelowFreeBytes']==800*1024**2 and built['parallelBuilds']==1 and built['guestExecutionRequested']is False,'single-job2GiB/800MiB native-only policy')
 for n in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']:need(built['explicitEnvironment'][n]=='1','actual concurrency guard '+n)
 need(built['explicitEnvironment']['NODE_COMPAT_BUILD_ROOT']==str(WORK)and built['explicitEnvironment']['NODE_COMPAT_GC_STRESS']=='1'and built['explicitEnvironment']['NODE_COMPAT_BUILD_TYPE']=='Release'and built['explicitEnvironment']['NODE_COMPAT_OOM_TESTING']=='0','actual isolated ReleaseGC env')
 log=read(spec['buildLog']['path'],spec['buildLog']['sha256'],spec['buildLog']['bytes']);need(spec['buildLog']['sha256']==built['logSha256'],'full actual build log')
 m=data(spec['metadata']);verify(spec['engine']);need(alias(m['enginePath']).resolve()==alias(spec['engine']['path']).resolve()and m['engineSha256']==spec['engine']['sha256']and m['engineBytes']==spec['engine']['bytes'],'actual metadata/engine tuple')
 need(read(spec['engine']['path'],spec['engine']['sha256'],spec['engine']['bytes'])[:8]==b'\0asm\x01\0\0\0','core engine binary header only/no execution')
 need(m['buildRecipeSha256']==RECIPE and m['gcStress']is True and m['entropyPolicy']=='off'and m['oomTesting']is False and m['debuggerEnabled']is False and m['wptSupportEnabled']is False,'genuine ordinary GC/OFF metadata')
 for n in ['sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild','streamConsumersEnabled','zlibEnabled','classicStreamsEnabled','internalTicksEnabled','strictInitialization','protectedAbortListenerEnabled']:need(m[n]is True,'actual metadata gate '+n)
 need(not m.get('diagnosticOnly',False)and not m.get('syntheticMetadataOnly',False),'no diagnostic/projection')
 policy=json.loads(read(SOURCE/'tests/node-compat/foundation-crypto/native-integration-candidate-v2/policy.json',POLICY));tools=json.loads(read(SOURCE/'tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/tool-pins.json'))
 native={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']};need(len(native)==355 and m['sourceManifest']==policy['expectedNativeSourceManifest'],'all actual native355 sources')
 for n,h in native.items():read(SOURCE/n,h,capture=False)
 need(len(tools['toolDependencies'])==922,'complete actual tools922')
 for r in tools['toolDependencies']:read(SOURCE/r['path'],r['sha256'],r['bytes'],False)
 for n in ['bootstrap-pins.json','runtime-pins.json']:
  v=json.loads(read(SOURCE/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'/n));need(all(v is None for v in v['variants'].values()),'ordinary runtime/bootstrap templates stillNULL')
 cachetext=read(m['cmakeCachePath'],m['cmakeCacheSha256']).decode();cmake={}
 for line in cachetext.splitlines():
  key,sep,rest=line.partition(':')
  if sep and '='in rest:cmake[key]=rest.partition('=')[2]
 need(m['requestedCMakeOptions']==m['observedCMakeOptions']and all(cmake[k]==v for k,v in m['observedCMakeOptions'].items()),'actual cache equals requested/observed complete options')
 required={'CMAKE_BUILD_TYPE':'Release','CMAKE_EXE_LINKER_FLAGS':'','WEVAL':'OFF','USE_WASM_OPT':'ON','NODE_COMPAT_GC_STRESS':'ON','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_COMPAT_OOM_TESTING':'OFF','ENABLE_BUILTIN_WEB_CRYPTO':'ON','ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON','NODE_COMPAT_STREAM_CONSUMERS':'ON','NODE_COMPAT_ZLIB':'ON'}
 need(all(cmake[k]==v for k,v in required.items())and not cmake.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE',''),'no extension/debug plus actual native configuration')
 build=Path(m['cmakeCachePath']).parent;need(str(build).startswith(str(WORK)+'/'),'isolated actual CMake root')
 ext=Path(cmake['CMAKE_HOME_DIRECTORY']);need({r['path']:r['sha256']for r in m['componentizeSourceManifest']}==EXTERNAL,'actual external3 manifest')
 for n,h in EXTERNAL.items():read(ext/n,h,capture=False)
 selected=m['zlibSelectedCodecInput'];w=m['zlibPolicy']['codecWitness'];need(selected==w['selectedCompileInput']and selected['archive']==w['archive'],'actual selected SM codec descriptor')
 read(w['archive']['path'],w['archive']['sha256'],w['archive']['bytes'],False);need(w['archive']['sha256']=='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc','actual selected MOZ_Z archive')
 need(len(selected['headers'])==4 and selected['headers']==w['headers'],'actual4 selected headers')
 for r in selected['headers']:verify(r)
 include=selected['requiredForcedInclude']['path'];need(selected['requiredForcedInclude']==selected['headers'][-1]and selected['headers'][-1]['sha256']=='841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6','exact forced js-confdefs header')
 need(w['runtimeBackendProof']==m['zlibPolicy']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None),'backend proof remainsfalse/null/null')
 for r in w['witnessFiles']:verify(r)
 before=json.loads(read(w['beforeManifestPath'],w['beforeManifestSha256']));need(before['state']=='CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD'and all(before[k]==w[k]for k in ['archive','headers','install']),'codec input before/after witness')
 db=json.loads(read(m['compileCommandsPath'],m['compileCommandsSha256']));cpp={n for n in native if n.endswith('.cpp')and n.startswith(('builtins/','runtime/'))};mapped={}
 for r in db:
  for n in cpp:
   if r['file']==str(SOURCE/n):need(n not in mapped,'one actual compile per native TU');mapped[n]=r['command']
 need(set(mapped)==cpp and len(mapped)==62,'actual native62 compile commands')
 private=set(policy['privateTargetCpp']);need(len(private)==6,'actual private6')
 for n,c in mapped.items():compiled(c,str(SOURCE/n),n in private,n.startswith('builtins/node-compat/'),False,include)
 layout=list(mapped.values());need(layout==m['internalTickPolicy']['actualLayoutCompileCommands']==m['protectedAbortListenerPolicy']['actualLayoutCompileCommands'],'actual62 layout proof relationships')
 strict=['runtime/engine.cpp','runtime/event_loop.cpp','runtime/node_tick_queue.cpp','builtins/web/event/event-target.cpp'];need(sorted(m['strictEventExceptionPolicy']['actualNativeCompileCommands'])==sorted(mapped[n]for n in strict),'actual strict4')
 need(sorted(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])==sorted(mapped[n]for n in private),'actual private6 command evidence')
 embedding=m['actualEmbeddingCompileCommands'];need(len(embedding)==1 and embedding==m['internalTickPolicy']['actualEmbeddingCompileCommands']==m['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands'],'actual separate parent embedding1')
 compiled(embedding[0],str(ext/'embedding/embedding.cpp'),False,False,True,include)
 link=w['postBuildLinkEvidence'];raw=read(link['path'],link['sha256']);lines=raw.decode().splitlines();candidates=[s for s in lines if 'libspidermonkey.a'in s and ' -c 'not in s];need(len(candidates)==1,'one actual raw selected SM link command')
 groups=[shlex.split(v)for v in candidates[0].split(' && ')];need(len(groups)==4 and groups[0]==[':'],'actual compiler/cd/optimizer grammar');compiler,cd,optimizer=groups[1:];need(compiler[0]==str(build/'cxx-wrapper')and compiler.count('-o')==1 and w['archive']['path']in compiler and not any(v.startswith('@')for v in compiler),'one actual compiler output/selected archive/no responses')
 no_second_codec(compiler);output=build/compiler[compiler.index('-o')+1];need(cd==['cd',str(output.parent)]and optimizer==[str(WORK/'cache/binaryen/1b13/bin/wasm-opt'),'--strip-debug','-O3','-o',output.name,output.name],'compiler output equals optimizer input/output')
 for n,c in mapped.items():
  matches=[]
  for line in lines:
   ws=shlex.split(line)
   if ws.count('-c')==1 and ws[ws.index('-c')+1]==str(SOURCE/n):matches.append(strip_deps(ws))
  need(matches==[strip_deps(shlex.split(c))],'raw Ninja/compile DB actual command equality '+n)
 need(embedding[0]in lines,'raw parent embedding command captured')
 nm=w['archiveSymbolEvidence'];need(nm['exitCode']==0,'actual retained nm exit0');verify(nm['nm'])
 nmrow=next(r for r in w['witnessFiles']if Path(r['path']).name=='nm.stdout.txt');nmtext=read(nmrow['path'],nmrow['sha256'],nmrow['bytes']).decode();symbols={}
 for name in ['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']:
  matches=[v for v in nmtext.splitlines()if re.search(r'(?:^|\s)MOZ_Z_'+re.escape(name)+r'\s+T\s',v)];need(len(matches)==1,'one selected MOZ_Z definition '+name);symbols[name]=matches[0]
 need(symbols==nm['selectedDefinitions'],'all7 actual retained prefixed symbol records')
 install=read(w['install']['path'],w['install']['sha256'],w['install']['bytes']).decode();need(install.count('NS_DEF(builtins::web::text_codec)')==install.count('NS_DEF(builtins::node_compat)')==install.count('NS_DEF(builtins::web::crypto)')==1 and install.index('NS_DEF(builtins::web::text_codec)')<install.index('NS_DEF(builtins::node_compat)'),'actual WebCrypto/textcodec/Node installation namespaces')
 crypto=policy['cryptoKeyOwnershipSourcePolicy'];need(m['cryptoKeyOwnershipPolicy']==crypto and crypto['sourceFiles']==355 and crypto['changedSourceFiles']==5 and crypto['unchangedParentFiles']==350 and crypto['exactComposedEdits']==20,'real owner355 five-changed source identity')
 ce=m['cryptoKeyOwnershipBuildEvidence'];need(ce['cryptoBuiltinEnabled']and ce['cacheSha256']==m['cmakeCacheSha256']and ce['installationSource']['sha256']==w['install']['sha256']and ce['installationSource']['count']==1,'actual crypto enabled/cache/install proof')
 changed=[mapped[r['path']]for r in crypto['changes']if r['path'].endswith('.cpp')];need(len(changed)==3 and sorted(ce['changedNativeCompileCommands'])==sorted(changed),'three actual changed crypto CPP commands')
 rust=m['generatedRustProject'];need(rust['cargoBuildLocked']and rust['manifestAndLockCheckedBeforeAndAfterBuild']and rust['lockSha256']==rust['versionedLockSha256']==native['runtime/crates/staticlib-template/Cargo.lock'],'actual locked Rust source')
 read(rust['manifestPath'],rust['manifestSha256']);read(rust['lockPath'],rust['lockSha256']);need(all('--locked'in shlex.split(c)for c in rust['actualCargoBuildCommands']),'actual locked cargo command')
 ssl=m['openssl'];audit=ssl['completeSourceAudit'];need(ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']and audit['unexpectedFiles']==audit['missingFiles']==[],'actual OpenSSL3.0.17 source policy')
 bef=json.loads(read(audit['beforeReportPath'],audit['beforeReportSha256']));need(all(audit[k]==v for k,v in bef.items()),'OpenSSL before/after source audit equality')
 read(audit['archivePath'],audit['archiveSha256'],capture=False);expected_ssl={}
 with tarfile.open(audit['archivePath'])as tar:
  for member in tar.getmembers():
   if not member.isfile():need(member.isdir(),'ordinary OpenSSL archive member');continue
   prefix,sep,n=member.name.partition('/');need(prefix=='openssl-3.0.17'and sep and n not in expected_ssl,'finite exact archive member');expected_ssl[n]=audit['patchedSources'].get(n)or hashlib.sha256(tar.extractfile(member).read()).hexdigest()
 actual_ssl={}
 for p in sorted(Path(ssl['sourceDir']).rglob('*')):
  need(not p.is_symlink(),'ordinary actual OpenSSL source')
  if p.is_file():actual_ssl[str(p.relative_to(ssl['sourceDir']))]=read(p,capture=False)['sha256']
 need(actual_ssl==expected_ssl and len(actual_ssl)==4650,'all4650 actual patched OpenSSL source bytes')
 for r in [ssl['configureRecipe'],ssl['configdata'],ssl['library']]:read(r['path'],r['sha256'],r.get('bytes'),False)
 crypto_link=[x for x in compiler if x.endswith('/libcrypto.a')];need(len(crypto_link)==1 and (build/crypto_link[0]).resolve()==Path(ssl['library']['path']).resolve() and 'starling-raw.wasm/libbuiltin_web_crypto.a'in compiler,'actual WebCrypto/libcrypto exact link context')
 # Parse the static GNU archive symbol table; never invoke nm or crypto.
 library=read(ssl['library']['path'],ssl['library']['sha256'],ssl['library']['bytes']);need(library[:8]==b'!<arch>\n','actual libcrypto archive magic');pos=8;members={};symtab=None;longnames=b''
 while pos<len(library):
  h=library[pos:pos+60];need(len(h)==60 and h[58:60]==b'`\n','complete archive header');name=h[:16].decode().strip();size=int(h[48:58]);payload=library[pos+60:pos+60+size];need(len(payload)==size,'complete archive member');members[pos]=(name,payload)
  if name=='/':symtab=payload
  if name=='//':longnames=payload
  pos+=60+size+(size%2)
 need(pos==len(library)and symtab is not None,'complete GNU symbol table');count=struct.unpack('>I',symtab[:4])[0];offsets=struct.unpack('>'+str(count)+'I',symtab[4:4+4*count]);names=symtab[4+4*count:].split(b'\0')
 for name in ['OPENSSL_cleanse','EVP_PKEY_free']:
  ix=[i for i,x in enumerate(names[:count])if x==name.encode()];need(len(ix)==1,'actual linked cleanup symbol '+name);member,payload=members[offsets[ix[0]]];need(payload[:8]==b'\0asm\x01\0\0\0','cleanup symbol points to actual core-Wasm archive member')
 for r in m['downloadedArchives']:read(r['path'],r['sha256'],capture=False)
 for r in m['wasiSdkVersionFiles']:need(read(r['path']).decode()==r['contents']and 'llvm-version: 21.1.4'in r['contents'],'actual SDK30/LLVM21 data')
 need(cmake['WASI_SDK_VERSION']=='30','actual selected SDK30')
 sdk=WORK/'cache/wasi-sdk/85e6';wrapper=read(build/'cxx-wrapper').decode();need(str(sdk/'bin/clang++')in wrapper and str(SOURCE/'scripts')in wrapper,'actual compiler wrapper selects currentSDK and source scripts')
 sdk_archive=next(r for r in m['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz')
 with tarfile.open(sdk_archive['path'])as tar:
  for n in ['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/llvm-nm']:
   member=tar.getmember('wasi-sdk-30.0-arm64-macos/'+n);target=sdk/n
   if member.issym():need(target.is_symlink()and os.readlink(target)==member.linkname,'actual declared SDK leaf alias')
   else:
    blob=tar.extractfile(member).read();read(target.resolve(),hashlib.sha256(blob).hexdigest(),len(blob),False)
 # Exact prebuild manifest and recipe seals, protected old normal plus actual stage inputs.
 stem=Path(spec['engine']['path']).stem
 need(json.loads(read(WORK/('source-inputs-'+stem+'.json'),m['sourceInputManifestSha256']))==m['sourceManifest'],'actual prebuild native source seal')
 need(json.loads(read(WORK/('componentize-native-inputs-'+stem+'.json'),m['componentizeInputManifestSha256']))==m['componentizeSourceManifest'],'actual prebuild external seal')
 need(read(WORK/('recipe-'+stem+'.sha256')).decode().strip()==RECIPE,'actual recipe pre/post seal')
 prot=json.loads(read(NATIVE/'normal-protection.json'));need(len(prot['originals'])==1387 and len(prot['frozenCopyEntries'])==1390,'all protected normal rows')
 for r in prot['originals']:verify(r['original']);verify(r['frozen'])
 for r in prot['frozenCopyEntries']:verify({k:r[k]for k in ['path','sha256','bytes']})
 verify(prot['freezeReceipt']);normal=Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze');need({str(p.relative_to(normal))for p in normal.rglob('*')if p.is_file()}==set(prot['requiredNormalFreezeMembership']),'unchanged exact1391 normal freeze membership')
 stage=json.loads(read(NATIVE/'stage-inputs.json'))
 for r in stage['files']:
  verify(r['original']);d=read(SOURCE/r['path'],r['original']['sha256'],r['original']['bytes'],False);need(stat.S_IMODE((SOURCE/r['path']).stat().st_mode)==r['mode'],'actual stage source mode preserved')
 for real,i in cache.items():need(identity(Path(real).stat())==i,'all current inputs stable at final read')
 return dict(schemaVersion=1,state='UNSEALED_BUILD_ONLY_NATIVE_PROVENANCE_AUDIT_DATA',sourceIndexSha256=SOURCE_SHA,variant='gc-off',configuredSourceRoot=str(SOURCE),workRoot=str(WORK),nativeSourceFiles=355,externalEmbeddingSources=3,nativeCompileCommands=62,strictCompileCommands=4,privateCompileCommands=6,embeddingCompileCommands=1,gcMacroPrivateTargetOnly=True,selectedMozZDefinitions=7,opensslSources=4650,cargoLocked=True,webCryptoEnabled=True,changedCryptoCppCommands=3,normalOriginalEntries=1387,normalFrozenMembers=1391,actualFreezeVerified=False,engineExecuted=False,guestKeyCryptoGcActionsInvoked=False,sourceAndNormalProtectionRechecked=True,externalParentExitCode=0,innerBuilderExitCode=0,allOwnedGroupsGone=True,noForcedCleanup=True,finalPeerPassIssued=False,checks=checks,inputs=list(seen.values()))

if __name__=='__main__':
 need(len(sys.argv)==3,'Actual completed Root evidence spec and fresh audit DATA path required')
 spec=json.loads(Path(sys.argv[1]).read_bytes());result=audit(spec);out=Path(sys.argv[2]);need(not out.exists(),'new exclusive intermediate data output');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(intermediateAuditComplete=True,finalPeerPassIssued=False,checks=checks)))
