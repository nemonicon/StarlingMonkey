"""Finite source/data/model checks only. Does not import native/owner modules."""
from pathlib import Path
import ast,hashlib,json,re
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
FROZEN=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
checks=0
def need(v,m):
 global checks
 checks+=1
 if not v:raise AssertionError(m)
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def j(p):return json.loads(Path(p).read_text())
metadata=j(FROZEN/'normal-off.engine.wasm.build.json')
need(len(metadata)==80 and len(metadata['sourceManifest'])==355,'actual355/raw80 parent')
need(desc(FROZEN/'normal-off.engine.wasm')['sha256']=='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b','fixed unchanged parent engine bytes')
need(desc(FROZEN/'normal-off.engine.wasm.build.json')['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3','fixed unchanged full80 metadata bytes')
need(desc(FROZEN/'normal-off-freeze-receipt.json')['sha256']=='9ce681402425f2bc59134bec5b48c98ee20fe15d42abf7ecaa1df920e05fded4','fixed unchanged freeze receipt')
need(desc(REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/index.json')['sha256']=='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65','genuine parent Source identity')
need(desc(REPO/'tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/index.json')['sha256']=='960a3b26af6c9b6fdd3e332e2d00e353feb683dfbe455855f3415ddc77f6291e','corrected lifecycle Source identity')
der=j(OWN/'derivations.json')
need(len(der['files'])==5 and der['edits']==28,'exact finite afterimages')
for row in der['files']:
 before=Path(row['before']['path']).read_text();after=Path(row['after']['path']).read_text()
 x=before
 for e in row['edits']:
  need(x.count(e['before'])==1,'forward unique');x=x.replace(e['before'],e['after'],1)
 need(x==after,'forward bytes')
 for e in reversed(row['edits']):
  need(x.count(e['after'])==1,'reverse unique');x=x.replace(e['after'],e['before'],1)
 need(x==before,'exact inverse')
 need(desc(row['before']['path'])==row['before'] and desc(row['after']['path'])==row['after'],'actual derivation descriptors')
native_delta={r['repositoryPath']:r for r in der['files'] if r['role']=='nativeAfterimage'}
need(len(native_delta)==4,'four native afterimages')
rows=[]
for row in metadata['sourceManifest']:
 p=FROZEN/'source'/row['path'];need(desc(p)['sha256']==row['sha256'],'whole current native parent origin')
 origin=Path(native_delta[row['path']]['after']['path']) if row['path'] in native_delta else p
 rows.append({'path':row['path'],'origin':desc(origin),'role':'native-afterimage' if row['path'] in native_delta else 'parent-retained'})
for name in ['include/clock-lifecycle-diagnostics.h','builtins/diagnostics/clock-lifecycle.cpp']:
 need(name not in {r['path'] for r in rows},'new path noncollision')
 rows.append({'path':name,'origin':desc(OWN/'after'/name),'role':'new-private-source'})
need(len(rows)==357 and len({r['path'] for r in rows})==357,'proposed357 not old355')
embedding=[]
for row in metadata['componentizeSourceManifest']:
 p=OWN/'after/componentize-source'/row['path']
 if not p.exists():p=FROZEN/'componentize-source'/row['path']
 embedding.append({'path':row['path'],'origin':desc(p),'role':'external-afterimage' if 'after/componentize-source' in str(p) else 'parent-external-retained'})
need(len(embedding)==3,'external3 stays separate')
put('proposed-source-inventory.json',{'schemaVersion':1,'state':'PROPOSED_UNCOMPILED_INPUT_INVENTORY_NOT_BUILD_METADATA_V1','parentNativeSourceFiles':355,'parentRetained':351,'parentNativeAfterimages':4,'newNativePaths':2,'proposedNativeSourceFiles':357,'native':rows,'externalEmbedding':embedding,'compiled':False})
cmake=(OWN/'after/cmake/builtins.cmake').read_text()
for text in ['option(NODE_COMPAT_LIFECYCLE_DIAGNOSTICS "Instrument private lifecycle snapshots" OFF)','option(ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE "Enable private lifecycle module" OFF)','target_compile_definitions(extension_api INTERFACE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)','target_compile_definitions(host_api PRIVATE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)','add_builtin(diagnostics::clock_lifecycle DISABLED_BY_DEFAULT','NODE_COMPAT_OOM_TESTING OR NODE_COMPAT_GC_STRESS']:
 need(text in cmake,'actual CMake mechanism')
header=(OWN/'after/include/clock-lifecycle-diagnostics.h').read_text()
cpp=(OWN/'after/builtins/diagnostics/clock-lifecycle.cpp').read_text()
need('MaxTimerLeases = 512' in header and 'state.usedLeases == MaxTimerLeases' in header,'bounded no overwrite ledger')
need('state.overflow = true; return 0;' in header,'sticky overflow')
need('"recordingComplete", !captured.history.overflow && !captured.history.invariantViolation' in cpp,'truthful incomplete flag')
need(cpp.count('JS_FN(')==1 and 'JS_FN("snapshot"' in cpp,'snapshot only')
need('const Snapshot captured = capture();' in cpp and cpp.index('const Snapshot captured = capture();')<cpp.index('JS::RootedObject out(cx, JS_NewPlainObject(cx)), counters'),'capture before JS allocation')
for bad in ['reset(', 'queue_async_task(', 'Call(', 'GC(', 'subscribe(', 'unsubscribe(', 'reinterpret_cast','Math.random','CryptoKey']:
 need(bad not in cpp,'observer has no control/probe operation: '+bad)
need('"privateHandle"' not in cpp,'native handles not returned')
for name,file in [('RuntimeCounts runtime_counts()', 'runtime/event_loop.cpp'),('std::size_t timer_registry_size()', 'builtins/web/timers.cpp'),('bool immediate_cache_owned()', 'host-apis/wasi-0.2.0/host_api.cpp')]:
 need(name in (OWN/'after'/file).read_text(),'new definition present, uncompiled: '+name)
# Pure mirrors test record limits/arithmetic; they do NOT execute C++ definitions.
maximum=2**64-1
for value in [0,1,9,10,2**32-1,2**53+1,maximum]:
 v=value;buf=[]
 while True:
  buf.append(chr(48+v%10));v//=10
  if not v:break
 need(''.join(reversed(buf))==str(value) and len(buf)<=20,'full u64 decimal model')
ledger=[];overflow=False
for k in range(513):
 if len(ledger)==512:overflow=True;continue
 ledger.append({'serial':len(ledger)+1,'acquiredAt':4*k+1,'invalidatedAt':4*k+2,'dropAttemptAt':4*k+3,'dropReturnedAt':4*k+4})
need(len(ledger)==512 and overflow,'513th acquisition remains incomplete without reuse')
need([r['serial'] for r in ledger]==list(range(1,513)),'no serial reuse')
for r in ledger:need(r['acquiredAt']<r['invalidatedAt']<r['dropAttemptAt']<r['dropReturnedAt'],'lease event order model')
for value,amount in [(0,1),(maximum-1,1),(maximum,1),(maximum-1,2)]:
 can=amount<=maximum-value;need((value+amount<=maximum)==can,'saturating counter predicate model')
# Exact real API declarations are read/hash evidence, not a compiler claim.
sdk=Path('/private/tmp/starling-node-compat/combined-native355-v2-build/spidermonkey-dist-release/include')
api_rows=[]
for file,anchor in [('js/String.h','JS_NewStringCopyN'),('js/Array.h','NewArrayObject(JSContext* cx, size_t length)'),('js/PropertyAndElement.h','JS_DefineProperty(JSContext* cx,'),('mozilla/HashTable.h','uint32_t count() const')]:
 p=sdk/file;need(anchor in p.read_text(),'actual147 JSAPI/header declaration');api_rows.append({'file':desc(p),'anchor':anchor})
rust=Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/source/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs')
binding=FROZEN/'source/host-apis/wasi-0.2.0/bindings/bindings.c'
need('__wasm_import_wasi_io_poll_pollable_drop(handle.__handle);' in binding.read_text(),'drop goes to imported void resource-drop')
need('"[resource-drop]pollable"' in rust.read_text(),'splicer resource-drop stub seam, not Store observability')
node=j(REPO/'tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/references.json')['nodeParserAndPureTests']
refs={'schemaVersion':1,'scope':'Finite actual parent/source/API references only; no recursive historical proof tree copy.',
 'parentSourceIndex':desc(REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/index.json'),
 'parentEngine':desc(FROZEN/'normal-off.engine.wasm'),'parentMetadata':desc(FROZEN/'normal-off.engine.wasm.build.json'),
 'parentFreezeReceipt':desc(FROZEN/'normal-off-freeze-receipt.json'),'frozenSourceRoot':str(FROZEN/'source'),
 'originalSevenCaseSource':desc(REPO/'tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/resource.mjs'),
 'lifecycleSourceIndex':desc(REPO/'tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/index.json'),
 'genuineAddBuiltin':desc(FROZEN/'source/cmake/add_builtin.cmake'),
 'genuineExternalCMake':desc(FROZEN/'componentize-source/CMakeLists.txt'),
 'genuineDefineBuiltinModule':desc(FROZEN/'source/runtime/engine.cpp'),
 'actualSdkApiDeclarations':api_rows,'nativeDropBinding':desc(binding),'rustSplicerDropSource':desc(rust),
 'historicalPrivateModuleMechanism':desc(REPO/'tests/node-compat/foundation-scheduler/diagnostic-link1-consumers-v1/test-extension.cpp'),
 'nodeForPureModelsOnly':node,'originalsModified':False}
put('references.json',refs)
put('proposed-policy.json',{'schemaVersion':1,'state':'UNCOMPILED_PRIVATE_DIAGNOSTIC_POLICY_TEMPLATE_NO_ADMISSION_V1','diagnosticOnly':True,
 'parentNativeSourceFiles':355,'proposedNativeSourceFiles':357,'externalEmbeddingSources':3,'nativeSourceDelta':{'retained':351,'afterimages':4,'newPaths':2},
 'ownInventory':'proposed-source-inventory.json','ownSourceIndex':None,'nativeVariant':'fresh-private-normal-off-diagnostic','parentSelectedWholeManifests':11,
 'privateGuestModule':'starling:test-clock-lifecycle','privateExports':['snapshot'],'publicNodeExportsAdded':False,
 'privateBundleNativeResidualImports':['node:buffer','starling:test-clock-lifecycle'],'privateSpecifierBundlerAdmissionImplemented':False,
 'macro':'NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','targetOption':'ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','defaultsOff':True,
 'requiredBuildOptions':{'CMAKE_BUILD_TYPE':'Release','ENABLE_JS_DEBUGGER':False,'NODE_COMPAT_OOM_TESTING':False,'NODE_COMPAT_GC_STRESS':False},
 'forecastPolicyCpp':63,'forecastCompilationDbRows':69,'forecastNotObservedCompileEvidence':True,
 'strictPrivateAndEmbeddingCommandsRequireNewClassification':True,'selectedExternalInterfaces':['wasi:clocks/wall-clock@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'],
 'diagnosticWit':'fixtures/profile.wit','sameComponentObserverRequired':True,'fixedLeaseRows':512,'overflowOrIncompleteMustFail':True,
 'newProducer':None,'sourceAdmissionModel':None,'buildRecipe':None,'stageController':None,'rootPhase':None,'actualNativeArtifact':None,'actualComponentArtifact':None,'actualRuntimeResults':None,
 'hostStoreDropObserved':False,'fatalFinalSnapshotReturned':False,'cachedImmediateExplicitDropImplemented':False,'sameInstanceTeardownProved':False,'resetOrReuseAllowed':False,'adoptionAuthority':None})
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));need(True,'Python grammar')
put('source-check-results.json',{'schemaVersion':1,'passed':True,'sourceAndPureChecks':checks,'actualParentNativeFilesChecked':355,'proposedNativeFiles':357,'nativeAfterimages':4,'externalAfterimages':1,'newNativePaths':2,'exactReversibleEdits':28,'declaredApiSourceObserved':True,'cppSyntaxChecked':False,'newSymbolsCompiledOrLinked':False,'nativeHelperOrCompilerOrGuestOrHostInvoked':False})
print(json.dumps({'sourceAndPureChecks':checks,'proposedNativeFiles':357,'cppSyntaxChecked':False,'passed':True}))
