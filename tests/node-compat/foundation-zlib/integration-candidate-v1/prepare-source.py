"""Finite source afterimages only. No application, compiler, codec or guest."""
from pathlib import Path
import copy,difflib,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ZLIB=HERE.parent
TRACE=ROOT/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
SCOPE='sm-node-22.14.0-m0.13'
def sha(data):return hashlib.sha256(data).hexdigest()
def enc(value):return(json.dumps(value,indent=2)+'\n').encode()
def put(name,data):
    data=data.encode()if isinstance(data,str)else data;p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data,name
    else:p.write_bytes(data)
PROOFS=[]
def derive(origin,name,edits):
    raw=origin.read_bytes();text=raw.decode();steps=[]
    for old,new,count in edits:
        assert old and text.count(old)==count,(name,old[:80],text.count(old),count)
        positions=[];at=0
        while True:
            at=text.find(old,at)
            if at<0:break
            positions.append(at);at+=len(old)
        positions=[v+i*(len(new)-len(old))for i,v in enumerate(positions)]
        text=text.replace(old,new);steps.append({'old':old,'new':new,'count':count,'afterOffsets':positions})
    reverse=text
    for edit in reversed(steps):
        for at in reversed(edit['afterOffsets']):
            assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
    assert reverse.encode()==raw
    put(name,text)
    before_name='ancestry/'+str(origin.relative_to(ROOT)).replace('/','__');put(before_name,raw)
    PROOFS.append({'origin':str(origin.relative_to(ROOT)),'preimage':before_name,'beforeSha256':sha(raw),'afterimage':name,'afterSha256':sha(text.encode()),'edits':steps,'forwardAndReverseExact':True})
    return text
def main():
    parents={'jsapi-candidate-v1':'448e3349b30b1a742c072569219838db864eceece81eda63b332054ed7de3f40',
      'facade-candidate-v1':'3227c5de4d87a024ba35111b865b8713b9d4660ab3be1a385d59fa04c5034c4f',
      'facade-candidate-independent-review-v1':'f70d510e8dc465efb0800fd5b0b828b4bf68b4fe8e5d629deedecd908ba1ac88',
      'backend-policy-v1':'fadfc6af09b20718a50d953f94b38ba53ca664dc4e48f1aa26eee2d16823b220'}
    for name,digest in parents.items():
        raw=(ZLIB/name/'index.json').read_bytes();assert sha(raw)==digest
        for row in json.loads(raw)['files']:
            data=(ZLIB/name/row['path']).read_bytes();assert sha(data)==row['sha256']and len(data)==row['bytes']
    assert sha((TRACE/'index.json').read_bytes())=='224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
    inventory=json.loads((ZLIB/'inventory.node-v22.14.0.json').read_bytes())
    names=[row['name']for row in inventory['exports']];assert len(names)==40 and names.count('default')==1
    sync=['deflateSync','inflateSync','gzipSync','gunzipSync','deflateRawSync','inflateRawSync']
    deferred=[row['name']for row in inventory['exports']if row['type']=='function'and row['name']not in sync];assert len(deferred)==31
    backend_check='''static bool verify_backend(JSContext *cx) {
  // The selected linked guest codec is the authority, never Node's inventory.
  const char *runtime = zlibVersion();
  if (!runtime || std::strcmp(runtime, ZLIB_VERSION) != 0)
    return fail(cx, BackendMismatch, "ERR_SM_ZLIB_BACKEND_MISMATCH", Z_VERSION_ERROR);
  return true;
}

static bool backend_info(JSContext *cx, unsigned argc, JS::Value *vp) {
  JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
  if (!verify_backend(cx)) return false;
  JS::RootedObject info(cx, JS_NewPlainObject(cx));
  if (!info) return false;
  if (!string_property(cx, info, "headerVersion", ZLIB_VERSION) ||
      !string_property(cx, info, "runtimeVersion", zlibVersion())) return false;
  static_assert(ZLIB_VERNUM > 0 && ZLIB_VERNUM <= std::numeric_limits<int32_t>::max());
  JS::RootedValue vernum(cx, JS::Int32Value(static_cast<int32_t>(ZLIB_VERNUM)));
  if (!JS_DefineProperty(cx, info, "vernum", vernum, JSPROP_ENUMERATE)) return false;
  args.rval().setObject(*info);
  return true;
}

'''
    derive(ZLIB/'jsapi-candidate-v1/kernel.template.cpp','source/builtins/node-compat/zlib/kernel.cpp',[
      ('// UNINSTALLED JSAPI proposal. No registry, CMake, public module or host imports.','// UNAPPLIED bounded zlib integration source. Link/runtime identity remains open.',1),
      ('#include "../bounded-zlib.template.h"','#include "bounded-codec.h"\n#ifndef NODE_COMPAT_ZLIB\n#error "Compile this source only for the explicit optional zlib target"\n#endif\n#if defined(Z_PREFIX) || defined(Z_PREFIX_SET)\n#error "Selected SM147 MOZ_Z_ ABI must not mix generic Z_PREFIX mappings"\n#endif',1),
      ('builtins::node_compat::zlib_jsapi_candidate','builtins::node_compat::zlib_profile',2),
      ('DEF_ERR(InvalidArgument,','DEF_ERR(BackendMismatch, JSEXN_ERR, "Linked zlib disagrees with its compiled header", 0)\nDEF_ERR(InvalidArgument,',1),
      ('sm-node-22.14.0-zlib-jsapi-template-v1',SCOPE,1),
      ('static bool codec_failure(',backend_check+'static bool codec_failure(',1),
      ('  if (!args.requireAtLeast(cx, "boundedZlibRun", 4))','  if (!verify_backend(cx)) return false;\n  if (!args.requireAtLeast(cx, "boundedZlibRun", 4))',1),
      ('JSObject *create_kernel(JSContext *cx) {','JSObject *create_kernel(JSContext *cx) {\n  if (!verify_backend(cx)) return nullptr;',1),
      ('    JS_FN("run", run, 4, JSPROP_ENUMERATE),','    JS_FN("run", run, 4, JSPROP_ENUMERATE),\n    JS_FN("backendInfo", backend_info, 0, JSPROP_ENUMERATE),',1)])
    put('source/builtins/node-compat/zlib/bounded-codec.h',(ZLIB/'bounded-zlib.template.h').read_bytes())
    values={kind:{name:row['value']for name,row in inventory[kind].items()}for kind in ['constants','codes']}
    assert values['constants']['ZLIB_VERNUM']==4865 and values['constants']['Z_MAX_CHUNK']is None
    data=json.dumps(values['constants'],separators=(',',':')).replace('"ZLIB_VERNUM":4865','"ZLIB_VERNUM":backend.vernum').replace('"Z_MAX_CHUNK":null','"Z_MAX_CHUNK":Infinity')
    assert '4865'not in data and '"Z_MAX_CHUNK":Infinity'in data
    constants='''// Node baseline shape with a private native-backend version overlay.
// No guest version value is selected by this source proposal.
export function createZlibData(backend) {
  if (!backend || typeof backend.headerVersion !== 'string' ||
      backend.headerVersion.length === 0 || backend.runtimeVersion !== backend.headerVersion ||
      !Number.isInteger(backend.vernum) || backend.vernum <= 0 || backend.vernum > 0x7fffffff) {
    const error = new Error('Unverified bounded zlib backend');
    Object.defineProperty(error, 'code', {value:'ERR_SM_ZLIB_BACKEND_MISMATCH', enumerable:true});
    throw error;
  }
  const constants = Object.freeze(Object.assign(Object.create(null), CONSTANTS));
  const codes = Object.freeze(Object.assign(Object.create(null), CODES));
  return Object.freeze({constants, codes});
}
'''.replace('CONSTANTS',data).replace('CODES',json.dumps(values['codes'],separators=(',',':')))
    put('source/builtins/node-compat/zlib/constant-data.generated.mjs',constants)
    derive(ZLIB/'facade-candidate-v1/zlib-facade.generated.mjs','source/builtins/node-compat/zlib/facade.mjs',[
      ("import {constants, codes} from './constant-data.generated.mjs';","import {createZlibData} from './constant-data.generated.mjs';",1),
      ('sm-node-22.14.0-zlib-facade-template-v1',SCOPE,1),
      ('export function createZlibModule(kernel, Buffer, web = globalThis) {','export function createZlibModule(kernel, Buffer, web = globalThis) {\n  const {constants, codes} = createZlibData(kernel.backendInfo());',1)])
    put('source/builtins/node-compat/zlib/LICENSE.node',(ZLIB/'source-freeze/node/LICENSE').read_bytes())
    manifest={'schemaVersion':1,'profileVersion':SCOPE,'nodeVersion':'v22.14.0',
      'status':'UNAPPLIED optional bounded six-sync zlib integration proposal; no linked codec, guest result or installed support.',
      'moduleContract':'One finite binding record registered with existing define_builtin_module under node:zlib and zlib; same named/default function and data identities. CommonJS uses existing literal selected-builtin lowering only.',
      'modules':{'node:zlib':{'aliases':['zlib'],'status':'partial','exports':names,
        'callablePolicy':'Six synchronous byte-only codec calls; all31 other callables explicitly refuse call/new. Implemented sync functions also refuse construction. No public backend hook.',
        'supportedStatic':sync,'importOnlyExports':deferred,'limits':{'inputBytes':1048576,'outputBytes':16777216},
        'deviations':['Byte-only fixed attached unshared ArrayBuffer/view inputs; strings/shared/resizable/detached data refused.',
          'Options only undefined or ordinary own-data maxOutputLength, integer1..16MiB. Unknown keys/symbols/accessors/prototypes explicitly refused; arbitrary Proxy reflection outside contract.',
          'Exactly one zlib/gzip/raw member, no trailing bytes, dictionary, concatenation, streaming, async, auto-detect, Brotli or CRC32 support.',
          'constants.ZLIB_VERNUM and legacy default.ZLIB_VERNUM use the same native header numeric value only after linked zlibVersion() matches; actual guest value remains unverified. Node baseline4865 is not fabricated for a different codec.',
          'Frozen null-prototype constants/codes and frozen default differ from Node mutability; Z_MAX_CHUNK remains numeric Infinity.',
          'Native staging/codec buffers and JS output are distinct allocator owners; output cap is not a peak-memory bound. GC/Node error-coercion/target behavior remain unproved.']}},'requiredHostInterfaces':[]}
    put('source/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json',enc(manifest))
    register='''#ifdef NODE_COMPAT_ZLIB
static bool install_zlib(api::Engine *engine, JS::HandleValue buffer_constructor) {
  auto *cx = engine->cx(); // install() already entered the content realm.
  JS::RootedObject kernel(cx, zlib_profile::create_kernel(cx));
  if (!kernel) return false;
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  if (!JS_DefineProperty(cx, argument, "kernel", kernel_value, 0) ||
      !JS_DefineProperty(cx, argument, "Buffer", buffer_constructor, 0)) return false;
  JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kZlibFactorySource, argument_value, &module)) return false;
  return engine->define_builtin_module("node:zlib", module) &&
         engine->define_builtin_module("zlib", module);
}
#endif

'''
    derive(ROOT/'builtins/node-compat/register.cpp','source/builtins/node-compat/register.cpp',[
      ('#include "factories.generated.h"','#include "factories.generated.h"\n#ifdef NODE_COMPAT_ZLIB\n#include "zlib/factories.generated.h"\n#endif',1),
      ('JSObject *create_kernel(JSContext *cx);','JSObject *create_kernel(JSContext *cx);\n#ifdef NODE_COMPAT_ZLIB\nnamespace zlib_profile { JSObject *create_kernel(JSContext *cx); }\n#endif',1),
      ('bool install(api::Engine *engine) {',register+'bool install(api::Engine *engine) {',1),
      ('  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);','#ifdef NODE_COMPAT_ZLIB\n  if (!install_zlib(engine, buffer_constructor)) return false;\n#endif\n  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);',1)])
    cmake='''
# Optional bounded zlib proposal; no second codec or find_package(ZLIB) fallback.
option(NODE_COMPAT_ZLIB "Enable bounded synchronous node:zlib source proposal" OFF)
if(NODE_COMPAT_ZLIB AND NOT CMAKE_SCRIPT_MODE_FILE)
    if(NOT TARGET builtin_node_compat OR NOT TARGET spidermonkey)
        message(FATAL_ERROR "NODE_COMPAT_ZLIB requires the existing native Node and SpiderMonkey targets")
    endif()
    if(NOT CMAKE_BUILD_TYPE STREQUAL "Release" OR NODE_COMPAT_OOM_TESTING)
        message(FATAL_ERROR "Bounded zlib proposal selects ordinary Release only")
    endif()
    foreach(ZLIB_REQUIRED "${SM_INCLUDE_DIR}/zlib.h" "${SM_INCLUDE_DIR}/zconf.h" "${SM_INCLUDE_DIR}/mozzconf.h" "${SM_LIB_DIR}/libspidermonkey.a")
        if(NOT EXISTS "${ZLIB_REQUIRED}")
            message(FATAL_ERROR "Selected guest codec input missing: ${ZLIB_REQUIRED}; no system codec fallback")
        endif()
    endforeach()
    # Existing add_builtin already links this target to spidermonkey. Actual
    # header/archive/link and zlibVersion() identity still require new evidence.
    target_include_directories(builtin_node_compat BEFORE PRIVATE "${SM_INCLUDE_DIR}")
    target_sources(builtin_node_compat PRIVATE builtins/node-compat/zlib/kernel.cpp)
    target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_ZLIB=1)
endif()
'''
    # A unique end anchor leaves every existing declaration and order unchanged.
    cmake_before=(ROOT/'cmake/builtins.cmake').read_text()
    derive(ROOT/'cmake/builtins.cmake','source/cmake/builtins.cmake',[(cmake_before,cmake_before+cmake,1)])
    # Production admission remains deliberately closed until a separately
    # reviewed full child manifest/recipe and real codec linkage proof exist.
    put('source/tests/node-compat/zlib-admission.mjs','''// Source proposal guard only. No positive artifact authority exists.
export function validateZlibSourceAdmission(metadata) {
  const hinted = Object.hasOwn(metadata, 'zlibEnabled') || Object.hasOwn(metadata, 'zlibPolicy') ||
    Object.hasOwn(metadata.observedCMakeOptions ?? {}, 'NODE_COMPAT_ZLIB') ||
    (Array.isArray(metadata.sourceManifest) && metadata.sourceManifest.some(row => row.path?.startsWith('builtins/node-compat/zlib/')));
  if (!hinted) return null;
  const error = new Error('Bounded zlib activation awaits full child-source, recipe, linked-codec and actual guest review');
  error.code = 'ERR_SM_NODE_ZLIB_ACTIVATION_PENDING';
  throw error;
}
''')
    derive(ROOT/'tests/node-compat/module-selection.mjs','source/tests/node-compat/module-selection.mjs',[
      ("import {validateClassicSourceAdmission} from './classic-streams-admission.mjs';","import {validateClassicSourceAdmission} from './classic-streams-admission.mjs';\nimport {validateZlibSourceAdmission} from './zlib-admission.mjs';",1),
      ("export const CLASSIC_STREAMS_MANIFEST =", "export const ZLIB_MANIFEST = 'builtins/node-compat/export-manifest.zlib.node-v22.14.0.json';\nexport const CLASSIC_STREAMS_MANIFEST =",1),
      ('  const classic = validateClassicSourceAdmission(metadata,','  validateZlibSourceAdmission(metadata); // Closed for both ON/OFF new lineages until actual proof.\n  const classic = validateClassicSourceAdmission(metadata,',1),
      ("    ['classicStreamsEnabled', 'NODE_COMPAT_CLASSIC_STREAMS', CLASSIC_STREAMS_MANIFEST],","    ['classicStreamsEnabled', 'NODE_COMPAT_CLASSIC_STREAMS', CLASSIC_STREAMS_MANIFEST],\n    ['zlibEnabled', 'NODE_COMPAT_ZLIB', ZLIB_MANIFEST],",1)])
    baseline={'schemaVersion':1,'state':'NODE_BASELINE_AND_ACTUAL_GUEST_OVERLAY_PROPOSAL_ONLY','node':'v22.14.0',
      'inventorySha256':sha((ZLIB/'inventory.node-v22.14.0.json').read_bytes()),'nonfiniteSupplementSha256':sha((ZLIB/'facade-candidate-v1/nonfinite-supplement.json').read_bytes()),
      'nodeObservedZlibVernum':{'type':'number','value':4865},'nodeObservedBackend':'1.3.0.1-motley-82a5fec',
      'historicalGuestHeaderObservation':{'version':'1.3.1','vernum':4880,'sha256':'8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c','scope':'Header observation only, no linked codec proof'},
      'actualGuest':{'headerSha256':None,'archiveSha256':None,'linkCommandSha256':None,'runtimeVersion':None,'ZLIB_VERNUM':None,'verified':False},
      'constantPolicy':'Both exported constants.ZLIB_VERNUM and legacy default.ZLIB_VERNUM come from private native backendInfo after exact header/runtime version comparison; source never substitutes Node value.',
      'nonfinitePolicy':{'Z_MAX_CHUNK':{'type':'number','valueEncoding':'positive-infinity'}},'requiredHostInterfaces':[]}
    put('backend-profile.proposal.json',enc(baseline))
    put('source-derivations.json',enc({'schemaVersion':1,'state':'EXACT_CONDITIONAL_UNAPPLIED_SOURCE_DERIVATIONS','files':PROOFS,'noLiveFilesChanged':True}))
    put('contract.json',enc({'schemaVersion':1,'state':'UNAPPLIED_BOUNDED_SIX_SYNC_ZLIB_SOURCE_INTEGRATION_LINKAGE_OPEN','profileVersion':SCOPE,
      'parentIndices':parents,'classicSourceIndexSha256':'224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b','classicSourcePolicySha256':'891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c',
      'nativeModuleIds':['node:zlib','zlib'],'syncOperations':sync,'namedBindings':39,'namespaceBindingsIncludingDefault':40,'deferredCallables':deferred,
      'inputLimit':1048576,'outputLimit':16777216,'strictSingleMemberAndNoTrailingData':True,'selectedBackend':'existing-selected-guest-SpiderMonkey-zlib-if-link-and-runtime-identity-succeed',
      'newCodecDependency':False,'newHostServiceOrCapability':False,'linkedArchiveSha256':None,'actualGuestZlibVersion':None,'actualGuestZlibVernum':None,
      'newProducerRecipeSha256':None,'reviewedEnginePins':None,'productionAdmissionOpen':False,'installedSupport':False,'nativeOrGuestExecuted':False}))
    print(json.dumps({'state':'UNAPPLIED_ZLIB_SOURCE_AFTERIMAGES_PREPARED','exports':40,'sync':6,'deferred':31,'derivations':len(PROOFS),'guestVersion':None}))
if __name__=='__main__':main()
