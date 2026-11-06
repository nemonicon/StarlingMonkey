"""Own Source/host checking only. Never imports target helper/engine or runs C++."""
from pathlib import Path
import ast,hashlib,json,difflib,subprocess,time,shutil
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[2];NATIVE=OWN/'after/builtins/node-compat';PARENT=REPO/'tests/node-compat/foundation-timers/node-timers-candidate-v1';BYTE=REPO/'tests/node-compat/buffer-next-candidate-v1';HASH=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-candidate-v1'
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists();assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
parents=[PARENT/'index.json',BYTE/'index.json',REPO/'tests/node-compat/foundation-startup/next-startup-candidate-v1/index.json',REPO/'tests/node-compat/async-context/native-als-candidate-v2/index.json',HASH/'index.json']
parent_before=[row(p)for p in parents]
inputs=[NODE,REPO/'builtins/web/crypto/crypto.cpp',REPO/'builtins/web/crypto/uuid.cpp',REPO/'builtins/web/crypto/uuid.h',REPO/'host-apis/wasi-0.2.0/host_api.cpp',REPO/'cmake/node-compat-policy.cmake',PARENT/'after/runtime/event_loop.cpp',PARENT/'after/runtime/event_loop.h',PARENT/'after/include/extension-api.h',PARENT/'after/builtins/node-compat/register.cpp',PARENT/'after/builtins/node-compat/generate-factories.mjs',PARENT/'after/cmake/builtins.cmake',HASH/'crypto-facade.mjs']
inputs_before=[row(p)for p in inputs]
commands=[]
def run(args,name):
 start=time.monotonic();p=subprocess.run([str(NODE),*map(str,args)],capture_output=True,timeout=90)
 (OWN/(name+'.stdout.log')).write_bytes(p.stdout);(OWN/(name+'.stderr.log')).write_bytes(p.stderr)
 commands.append(dict(argv=[str(NODE),*map(str,args)],rawExitCode=p.returncode,stdout=row(OWN/(name+'.stdout.log')),stderr=row(OWN/(name+'.stderr.log')),elapsedOperationalSeconds=time.monotonic()-start));assert p.returncode==0,p.stderr.decode(errors='replace');assert not p.stderr;return p.stdout
run([NATIVE/'generate-crypto-random-factory.mjs'],'generate')
run([NATIVE/'generate-crypto-random-factory.mjs','--check'],'generator-check')
for p in [NATIVE/'crypto-rng.mjs',NATIVE/'crypto-facade.mjs',NATIVE/'generate-crypto-random-factory.mjs',NATIVE/'generate-factories.mjs',OWN/'test-host.mjs',OWN/'capture-node-source.mjs']:run(['--check',p],'grammar-'+p.name)
host=read(OWN/'host-tests-attempt2.stdout.log')
host=json.loads(run([OWN/'test-host.mjs'],'final-host-tests'));assert host['nativeRngExecuted']is host['guestExecuted']is False
# Source structure only; compiler/link/actual target guards remain open.
cpp=(NATIVE/'crypto-rng.cpp').read_text();facade=(NATIVE/'crypto-rng.mjs').read_text();reg=(NATIVE/'register.cpp').read_text();cmake=(OWN/'after/cmake/builtins.cmake').read_text();checks=[]
def check(n,v):assert v,n;checks.append(n)
check('actual same-TU deployed accessor+Engine state+entropy status','engine->state()!=api::EngineState::Initialized' in cpp and 'entropy::deployed_execution_started()'in cpp and 'return entropy::require(cx,op)'in cpp)
fill=cpp[cpp.index('bool fill_view('):cpp.index('\nbool random_bytes(')]
check('host random call before no-GC backing pointer acquisition',fill.index('Random::get_bytes')<fill.index('JS::AutoCheckCannotGC')<fill.index('JS_GetUint8ArrayData')<fill.index('std::memcpy'))
check('owned host scope wipe','~Wipe(){if(p)entropy::clear(p,n);}'in fill)
check('genuine existing uuid native API','builtins::web::crypto::random_uuid_v4(cx,"node:crypto.randomUUID")'in cpp)
check('no user JS error constructor dispatch','JS::Construct'not in cpp and 'api::throw_error' in cpp)
check('all private controls real deployed guard',all(('if(!deployed(cx,"node:crypto.'+n+'"))')in cpp for n in ['randomBytes','randomFillSync','randomUUID']))
check('capture private backend once','kcheck=rng.check,kbytes=rng.bytes,kfill=rng.fill,kuuid=rng.uuid' in facade)
check('actual guest Tick factory passed', 'core::EventLoop::create_internal_next_tick(cx)'in reg and 'argument,"rng",random_value' in reg and 'argument,"nextTick",random_tick_value'in reg)
check('dynamic standard webcrypto delegation', 'apply(webcrypto.getRandomValues,webcrypto,[value])'in facade)
check('falsy callback failures have presence flag','failed=false' in facade and 'failed=true;error=e' in facade)
check('Node zero callback before nextTick','if(n===0)' in facade and facade.index('if(n===0)')<facade.index('apply(nativeTick'))
check('RNG defaultOFF/runtimeONLY/ALS explicit','option(NODE_COMPAT_CRYPTO_RANDOM "Experimental deployed-only Node random bytes/UUID" OFF)'in cmake and 'NODE_COMPAT_ENTROPY_MODE STREQUAL "RUNTIME_ONLY"'in cmake and 'OR NOT NODE_COMPAT_ASYNC_LOCAL_STORAGE)'in cmake)
# Main canonical Source body and factory are actual active files, not pseudo APIs.
check('Hash logic preserved except explicit argument/binding/default edits', (NATIVE/'crypto-facade.mjs').read_text().count('function createHash(')==1)
# Fresh installed sibling generator test is entirely own data; no native tool.
installed=OWN/'installed-layout';installed.mkdir(exist_ok=True)
for p in NATIVE.iterdir():
 if p.name in ['crypto-rng.mjs','crypto-facade.mjs','generate-crypto-random-factory.mjs','crypto-factory.generated.h','export-manifest.crypto-random.node-v22.14.0.json','manifest.schema.json','validate-manifest.mjs']:shutil.copyfile(p,installed/p.name)
run([installed/'generate-crypto-random-factory.mjs','--check'],'installed-generator-check')
# Actual Source overlay arithmetic; no metadata fields or operational frame.
base=read(PARENT/'prospective-source-manifest.json');union={r['path']:r for r in base['files']};initial=set(union);overlays=[]
for r in read(BYTE/'derivations.json')['changedExistingFiles']:
 p=r['installedPath'];assert p in union;union[p]=dict(path=p,sha256=r['after']['sha256'],afterimage=r['after'],sourceRole='held Byte09ac Source overlay');overlays.append(p)
changes=[];added=[];support=[]
befores={'builtins/node-compat/register.cpp':PARENT/'after/builtins/node-compat/register.cpp','builtins/node-compat/generate-factories.mjs':PARENT/'after/builtins/node-compat/generate-factories.mjs','builtins/node-compat/crypto-factory.generated.h':Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze/source/builtins/node-compat/crypto-factory.generated.h'),'cmake/builtins.cmake':PARENT/'after/cmake/builtins.cmake'}
for p in sorted((OWN/'after').rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(OWN/'after').as_posix()
 if p.name in ['validate-manifest.mjs','manifest.schema.json']:support.append(row(p));continue
 r=row(p);entry=dict(installedPath=rel,after=r)
 if rel in befores:
  b=befores[rel];entry['before']=row(b);diff=''.join(difflib.unified_diff(b.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=rel+'.before',tofile=rel+'.after'));dest=OWN/(p.name+'.diff');dest.write_text(diff);entry['unifiedDiff']=row(dest)
 if rel not in union:
  if rel=='cmake/builtins.cmake':entry['role']='existing packaging CMake outside native inventory'
  else:assert rel not in initial;added.append(rel)
 else:changes.append(rel)
 if rel!='cmake/builtins.cmake':union[rel]=dict(path=rel,sha256=r['sha256'],afterimage=r,sourceRole='uncompiled RNG Source overlay')
 entry['nativeInventoryMember']=rel in union;overlays.append(entry)
assert len(union)==len(initial)+len(added) and len(initial)==397
save('integration.json',dict(schemaVersion=1,state='UNCOMPILED_SOURCE_OVERLAY_NOT_METADATA',parentTimerSource=row(PARENT/'index.json'),parentByteSource=row(BYTE/'index.json'),nativeParentFiles=len(initial),newNativePaths=added,existingNativeAfterimages=changes,prospectiveNativeSourceFiles=len(union),externalEmbeddingSources=3,externalEmbeddingChanged=False,overlays=overlays,supportCopiesNotNewNativeRows=support,selectedCryptoManifest=row(NATIVE/'export-manifest.crypto-random.node-v22.14.0.json'),newFlag='NODE_COMPAT_CRYPTO_RANDOM',defaultFlag=False,requiredEntropyMode='RUNTIME_ONLY',oldRaw83MetadataUnchanged=True,actualMetadata=None,actualEngine=None,newClassifierRecipeAndMetadataRequired=True))
# Source citations only, never fabricated runtime method counts.
app=Path('/private/tmp/starling-node-compat/next-http-bridge-module-v1/application');paths=['node_modules/next/dist/trace/shared.js','node_modules/next/dist/compiled/nanoid/index.cjs','node_modules/next/dist/server/node-environment-extensions/node-crypto.js','node_modules/next/dist/server/node-environment-extensions/web-crypto.js','node_modules/next/dist/server/lib/node-fs-methods.js','node_modules/next/dist/server/lib/router-utils/filesystem.js','node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js','node_modules/next/dist/compiled/next-server/app-route.runtime.prod.js'];demands=[]
import re
for name in paths:
 p=app/name;t=p.read_text();sites=[]
 for m in re.finditer(r'randomBytes|randomFillSync|randomUUID|getRandomValues',t):
  sites.append(dict(line=t.count('\n',0,m.start())+1,offset=m.start(),token=m.group(),source=t[max(0,m.start()-60):m.start()+160].replace('\n',' '),runtimeInvocationObserved=False))
 demands.append(dict(source=row(p),sites=sites))
save('demand.json',dict(schemaVersion=1,retained406Report=row(REPO/'tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/module-results/next-http-bridge-module-v1/result.json'),sourceBased=True,methodCallTraceRecorded=False,files=demands,actionKey='Existing server-reference-manifest base64 key; no key value recorded. Generation/encryption/preview branches conditional.'))
assert parent_before==[row(p)for p in parents];assert inputs_before==[row(p)for p in inputs]
save('references.json',dict(schemaVersion=1,parentFamilies=parent_before,currentInputs=inputs_before,currentInputsRechecked=True,stdlibOrHostOnlyCommands=commands,activeTargetFunctionsInvoked=False))
save('checks.json',dict(schemaVersion=1,hostChecks=host['checks'],commands=commands,staticSourcePredicates=checks,installedGeneratorLayoutPassed=True,nativeFrontendInvoked=False,nativeRngExecuted=False,guestExecuted=False))
save('future-authority.json',dict(schemaVersion=1,sourcePeer=None,rootAuthority=None,sourceStage=None,nativeFrontend=None,nativeBuild=None,actualMetadata=None,actualEngine=None,component=None,guest=None,adoption=None,operationalActionsAllowed=False))
save('results.json',dict(schemaVersion=1,state='NODE_CRYPTO_RUNTIME_ONLY_RNG_SOURCE_PREPARED_UNCOMPILED_V1',sourceOnly=True,sourcePrepared=True,sourceReviewPassed=False,profileVersion='sm-node-22.14.0-m0.23',hostTests=host['checks'],fullNodeNamespaceInventoryPreserved=True,newFlagDefault=False,entropyRequired='RUNTIME_ONLY',mutableCjsDefaultOnlyWhenRngEnabled=True,prospectiveNativeFiles=len(union),nativeParentFiles=len(initial),newNativePaths=len(added),externalEmbeddingSources=3,nativeCompilerInvoked=False,nativeBuildInvoked=False,nativeEntropyExecuted=False,hostNodeRandomnessTestsExecuted=True,keyWorkloadExecuted=False,guestExecuted=False,adoption=False))
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(row(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_NODE_CRYPTO_RANDOM_V1',files=files))
for n in ['index.json','results.json','integration.json','checks.json']:print(json.dumps(row(OWN/n)))
