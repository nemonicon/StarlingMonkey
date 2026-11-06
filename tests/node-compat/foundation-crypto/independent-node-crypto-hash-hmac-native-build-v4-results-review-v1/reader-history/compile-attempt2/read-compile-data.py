"""Finite actual BUILD4 compiler/link DATA audit, never a BUILD acceptance gate.
No executable, helper, emitter, recheck, metadata admission or Git is invoked.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shlex,stat,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v3'
seen={};checks=0
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def verify(path,sha=None,size=None):
 p=Path(path);a=p.lstat();need(stat.S_ISREG(a.st_mode),'ordinary actual input '+str(p));h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b);n+=len(b)
 z=p.lstat();need((a.st_dev,a.st_ino,a.st_mode,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable actual input')
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=n);need((sha is None or r['sha256']==sha)and(size is None or size==n),'exact actual bytes '+str(p))
 if str(p)in seen:need(seen[str(p)]==r,'same repeated actual input')
 seen[str(p)]=r;return r
def data(r):verify(r['path'],r['sha256'],r.get('bytes'));return json.loads(Path(r['path']).read_bytes())
def content(r):verify(r['path'],r['sha256'],r.get('bytes'));return Path(r['path']).read_bytes()
def run():
 ix=verify(S/'index.json','2ebed6b8c0f9787c07ef00036e8b903f4a39cfa70f916da45e895743d097969c');index=data(ix)
 for x in index['files']:verify(S/x['path'],x['sha256'],x['bytes'])
 refs=json.loads((S/'references.json').read_bytes());policy=data(refs['policy']);source=Path(refs['configuredSourceRoot']);work=Path(refs['workRoot'])
 mr=verify(refs['enginePath']+'.build.json','2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6',731387);m=data(mr)
 er=verify(refs['enginePath'],'9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e',10024185)
 modpath=S/'metadata_model.py';tree=ast.parse(modpath.read_text());need(all(isinstance(x,(ast.Expr,ast.FunctionDef))for x in tree.body),'pure metadata shape module only')
 spec=importlib.util.spec_from_file_location('independent_build4_pure_shape',modpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 pure=mod.validate_metadata(m,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 need(pure==dict(state='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=357,engineRead=False,runtimeAccepted=False,grantsAuthority=False),'genuine pure raw83 shape')
 need(m['enginePath']==er['path']and m['engineSha256']==er['sha256']and m['engineBytes']==er['bytes'],'whole actual engine metadata binding')
 with Path(er['path']).open('rb')as f:need(f.read(8)==b'\0asm\1\0\0\0','native core Wasm header only')
 for x in m['sourceManifest']:verify(source/x['path'],x['sha256'])
 for x in m['selectedModuleManifests']:verify(source/x['path'],x['sha256'])
 need(m['selectedModuleManifests']==policy['selectedModuleManifests']and len(m['selectedModuleManifests'])==12,'all12 actual selected manifest rows')
 need([json.loads((source/x['path']).read_bytes())for x in m['selectedModuleManifests']]==policy['selectedManifestValues'],'all12 whole manifest JSON values')
 db=json.loads(content(dict(path=m['compileCommandsPath'],sha256=m['compileCommandsSha256'])));build=Path(m['cmakeCachePath']).parent
 native={x['path']for x in m['sourceManifest']};policycpp={x for x in native if x.endswith('.cpp')and x.startswith(('builtins/','runtime/'))};need(len(policycpp)==63 and len(db)==69,'genuine63 policy and69 actual DB rows')
 counts=dict(policy=0,other=0,generated=0);commands={};objects=[]
 for x in db:
  w=shlex.split(x['command']);need(w.count('-c')==w.count('-o')==1 and w[w.index('-c')+1]==x['file'],'one real compile source/output')
  need('--target=wasm32-wasi'in w and '-O3'in w and '-DNDEBUG'in w and '-fsyntax-only'not in w,'actual Release Wasm compilation')
  need(not any(t.startswith(('@','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','-DNODE_CRYPTO_AUDITED_BORROW','-DDEBUG'))for t in w),'no GC/OOM/DEBUG/runtimeentropy/borrow or response flags')
  path=Path(x['file']);relative=path.relative_to(source).as_posix()if path.is_relative_to(source)else None
  if relative:
   need(relative in native,'real configured-source input');kind='policy'if relative in policycpp else'other';need(relative not in commands,'unique configured compiler input');commands[relative]=x['command']
  else:need(path==build/'starling-raw.wasm/null.cpp','sole generated null input');kind='generated';verify(path)
  counts[kind]+=1
  if kind=='policy':
   for key in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_ENTROPY_POLICY','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER']:need('-D'+key+'=1'in w,'whole native layout/policy macro')
   for key in ['NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_STREAM_CONSUMERS','NODE_COMPAT_CRYPTO_HASH_HMAC']:need(('-D'+key+'=1'in w)==(relative in policy['privateTargetCpp']),'exact selected private macro '+key)
  o=Path(w[w.index('-o')+1]);objects.append(verify(o if o.is_absolute()else Path(x['directory'])/o))
 need(counts==dict(policy=63,other=5,generated=1),'69 exact DB split; no embedding projection')
 combined=m['combinedNativeSourcePolicy'];need(set(combined['actualPolicyCppCompileCommands'])=={commands[x]for x in policycpp},'whole63 policy witness equals actual DB')
 for values,count in [(m['strictEventExceptionPolicy']['actualNativeCompileCommands'],4),(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'],7),(m['nodeCryptoHashHmacPolicy']['actualPrivateHashHmacMacroCompileCommands'],7)]:need(len(values)==count and set(values)<=set(commands.values()),'whole strict/private/hash CPP command witness')
 need(m['nodeCryptoHashHmacPolicy']['actualKernelCompileCommands']==[commands['builtins/node-compat/hash-hmac-kernel.cpp']]and m['nodeCryptoHashHmacPolicy']['actualRegistrationCompileCommands']==[commands['builtins/node-compat/register.cpp']],'actual new kernel+registration commands')
 include=m['nodeCryptoHashHmacPolicy']['guestOpenSSLInclude'];kw=shlex.split(commands['builtins/node-compat/hash-hmac-kernel.cpp']);need(any(kw[i]=='-isystem'and kw[i+1]==include for i in range(len(kw)-1)),'real guest OpenSSL include on actual kernel')
 for name in ['openssl/evp.h','openssl/core_names.h','openssl/params.h','openssl/opensslv.h']:verify(Path(include)/name)
 ext=Path(combined['externalConfiguredSourceRoot'])
 for x in m['componentizeSourceManifest']:verify(ext/x['path'],x['sha256'])
 emb=m['actualEmbeddingCompileCommands'];need(len(emb)==1 and emb==combined['actualSeparateEmbeddingCompileCommands']==m['internalTickPolicy']['actualEmbeddingCompileCommands'],'actual separate embedding command')
 ew=shlex.split(emb[0]);need(ew[ew.index('-c')+1]==str(ext/'embedding/embedding.cpp')and not any(t.startswith(('-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_CRYPTO_AUDITED_BORROW','-DDEBUG'))for t in ew),'actual fresh separate embedding source/flags');verify(build/ew[ew.index('-o')+1])
 cache=content(dict(path=m['cmakeCachePath'],sha256=m['cmakeCacheSha256'])).decode();cachevals={}
 for l in cache.splitlines():
  k,sep,v=l.partition(':')
  if sep and '='in v:cachevals[k]=v.partition('=')[2]
 for k,v in m['observedCMakeOptions'].items():need(cachevals[k]==v and m['requestedCMakeOptions'][k]==v,'actual configured/requested option '+k)
 install=content(m['nodeCryptoHashHmacPolicy']['actualInstallationOrder']['source']).decode();need(install.count('NS_DEF(builtins::web::crypto)')==install.count('NS_DEF(builtins::node_compat)')==1 and install.index('NS_DEF(builtins::web::crypto)')<install.index('NS_DEF(builtins::node_compat)'),'real unique nativeCrypto before node installation')
 capture=m['nodeCryptoHashHmacPolicy']['actualNinjaCapture'];ninjatext=content(capture['stdout']).decode();need(content(capture['stderr'])==b''and capture['rawExitCode']==0 and capture['timeout']is False,'retained real postbuild Ninja capture')
 for x in db:
  lines=[t for t in ninjatext.splitlines()if '-c '+x['file']in t];need(len(lines)==1,'unique actual Ninja compiler source')
  nw=shlex.split(lines[0]);dw=shlex.split(x['command']);output=dw[dw.index('-o')+1]
  need(nw.count('-MD')==nw.count('-MT')==nw.count('-MF')==1 and nw[nw.index('-MT')+1]==output and nw[nw.index('-MF')+1]==output+'.d','exact additional actual Ninja dependency flags')
  clean=[];i=0
  while i<len(nw):
   if nw[i]=='-MD':i+=1
   elif nw[i]in ['-MT','-MF']:i+=2
   else:clean.append(nw[i]);i+=1
  need(clean==dw,'whole compiler argv equals DB after exact dependency-only flags')
 need(emb[0]in ninjatext,'separate embedding actual Ninja command')
 link=m['nodeCryptoHashHmacPolicy']['actualLinkEvidence'];need(link['completeNinjaLine']in ninjatext,'whole final link witness in captured Ninja text')
 parts=[shlex.split(x)for x in link['completeNinjaLine'].split(' && ')];need(len(parts)==4 and parts[0]==[':'],'actual compiler/cd/inplace optimizer structure');compiler,cd,opt=parts[1:]
 need(compiler==link['linkArgv'],'entire stored link argv equals parsed command')
 archives=[]
 for name in compiler:
  if name.endswith('.a'):archives.append(verify(Path(name)if name.startswith('/')else build/name))
 need(len(archives)==30 and len({x['path']for x in archives})==29,'30 ordered static arguments/29 unique libraries')
 ssl=m['openssl'];need(m['nodeCryptoHashHmacPolicy']['actualGuestOpenSSL']==ssl and ssl['entropy']=='OFF'and ssl['randSeed']=='none','exact actual guest OpenSSL/noentropy tuple')
 sslrow=ssl['library'];verify(sslrow['path'],sslrow['sha256'],sslrow['bytes']);need(sslrow['path']in{x['path']for x in archives},'actual guest library is linked')
 for q in [build/compiler[compiler.index('-o')+1],ext/'lib/starlingmonkey_embedding.wasm']:verify(q,er['sha256'],er['bytes'])
 need((Path(cd[1])/opt[-1]).resolve()==(build/compiler[compiler.index('-o')+1]).resolve()and opt[1:]==['--strip-debug','-O3','-o','starling-raw.wasm','starling-raw.wasm'],'same optimized native output')
 result=data(verify(Path(refs['buildOutputRoot'])/'result.json','ca052fb19f0f7ce123176f5478737b0451ee7c97227b8dc148461c3721bbde72',38473));log=content(result['buildLog']).decode();steps=[int(x)for x in re.findall(r'^\[(\d+)/109\]',log,re.M)];need(steps==list(range(1,110)),'full109 retained build steps')
 need(result['rawChildExitCode']==0 and result['launcherExitCode']==1 and result['state']=='native-build-failed-or-incomplete'and result['evidenceComplete']is False,'honest completed compilation/failed controller status')
 need(result['lifecycleComplete']is True and result['ownedGroupCleanup']['complete']is True and not result['ownedGroupCleanup']['events']and not result['ownedGroupCleanup']['errors'],'recipe clean raw0 lifecycle')
 samples=result['diskFreeSamplesDuringBuildCommand'];need(len(samples)==366 and min(x['freeBytes']for x in samples)>result['stopBelowFreeBytes'],'all actual disk samples above stop threshold')
 final=dict(schemaVersion=1,state='ACTUAL_BUILD4_COMPILER_LINK_DATA_REVIEW_ONLY',checks=checks,pureMetadataShape=pure,engine=er,metadata=mr,actualBuildResult=verify(Path(refs['buildOutputRoot'])/'result.json'),coverage=dict(rawMetadataFields=83,nativeSources=357,externalSources=3,selectedWholeManifests=12,compileDatabaseRows=69,policyCpp=63,otherConfigured=5,generatedNull=1,separateEmbedding=1,strictCpp=4,privateCpp=7,compileObjects=69,orderedStaticArchiveArguments=30,uniqueStaticLibraries=29,buildLogSteps=109,diskSamples=366),recipeExitCode=0,controllerExitCode=1,compilerAndLinkDataChecksPassed=True,wholePreservationPassed=False,buildAccepted=False,engineExecuted=False,cryptoOperationsInvoked=False,grantsAuthority=False,qualifications=['Actual raw83 model passes pure validation; operational admission was not called by reviewer.','Compile DB and actual postbuild Ninja capture establish actual command plans and current object outputs; no separate per-compiler terminal evidence is invented.','All109 raw progress steps and recipe exit0 are retained; controller launcher1/evidencefalse/preservation refusal remain unchanged.','No full SDK/distribution/complete input ledger or frozen verification claim is made by this bounded failure-oriented read.'])
 (P/'compile-data-review.json').write_text(json.dumps(final,indent=2)+'\n');(P/'compile-data-input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,scope='Finite current files actually read by failure-oriented compiler/link audit; not whole future-freezer input ledger',files=list(seen.values())),indent=2)+'\n');print(json.dumps(final))
if __name__=='__main__':run()
