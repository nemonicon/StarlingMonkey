"""Generate owned UNAPPLIED source afterimages; no factory/native/guest execution."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
PARENT=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
PROFILE='sm-node-22.14.0-m0.14'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(path,raw):
 p=HERE/path;p.parent.mkdir(parents=True,exist_ok=True)
 raw=raw if isinstance(raw,bytes)else raw.encode()
 with p.open('xb')as f:f.write(raw)
def jsonput(path,value):put(path,json.dumps(value,indent=2)+'\n')
def replacement(path,edits):
 raw=(BASE/path).read_text();value=raw;proof=[]
 for old,new in edits:
  assert value.count(old)==1,(path,old);value=value.replace(old,new);proof.append({'old':old,'new':new,'count':1})
 reverse=value
 for row in reversed(proof):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==raw
 put('proposed/'+path,value)
 return {'path':path,'beforeSha256':sha(raw.encode()),'afterSha256':sha(value.encode()),'edits':proof,'reverseExact':True}

def main():
 assert sha((PARENT/'index.json').read_bytes())=='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
 parent=json.loads((PARENT/'policy.json').read_bytes())
 before={row['path']:row['sha256']for row in parent['expectedNativeSourceManifest']};assert len(before)==350
 for name,digest in before.items():assert sha((BASE/name).read_bytes())==digest,name
 original=REPO/'tests/node-compat/foundation-stream-consumers/metadata-v2/create-module.mjs'
 facade=original.read_text().replace('// ISOLATED SOURCE CANDIDATE ONLY. Native guest/registration gates have not run.','// UNAPPLIED optional production text/JSON source. Fresh355 native/registration/guest gates pending.').replace("export const CONTRACT_VERSION = 'stream-consumers-prototype-v1';",f"export const CONTRACT_VERSION = '{PROFILE}';")
 facade=facade.replace('export function createConsumersModule(web = globalThis) {','export function createConsumersModule(web) {')
 assert 'globalThis'not in facade
 base='builtins/node-compat/stream-consumers/'
 put('proposed/'+base+'facade.mjs',facade)
 put('proposed/'+base+'LICENSE.node',(REPO/'tests/node-compat/foundation-stream-consumers/LICENSE.node').read_bytes())
 manifest={'schemaVersion':1,'profileVersion':PROFILE,'nodeVersion':'v22.14.0','status':'UNAPPLIED optional bounded native-TextDecoder consumer factory; no installed355 or runtime proof.','moduleContract':'Real six-binding record, same functions/default object under canonical and bare IDs. Mutable ordinary default object; mutation does not rewrite named bindings. Literal static CJS lowering returns that default object.','modules':{'node:stream/consumers':{'aliases':['stream/consumers'],'status':'partial','exports':['arrayBuffer','blob','buffer','default','json','text'],'supportedStatic':['text','json'],'importOnlyExports':['arrayBuffer','blob','buffer'],'callablePolicy':'text/json are async arity1/nonconstructible; three ordinary arity1 Blob-dependent functions synchronously refuse call/new with own identifiable fields.','limits':{'byteInput':1048576,'stringInputCodeUnits':1048576,'outputCodeUnits':1048576,'chunks':4096},'deviations':['No Blob, Buffer-output, arrayBuffer-output, Node24 bytes, Web reader adapter, public process or ALS.','Fixed attached unshared BufferSource/string/undefined chunks and ordinary finite sync/async iterables only; arbitrary Proxy/coercion/cross-realm domains are not claimed.','Selected classic and node:stream/web wrapper inputs need separate fresh355 gates. Raw native-global ReadableStream lacks async iteration and is not implicitly adapted.','Profile cap errors close through standard for-await; a pending next/return Promise has no facade timeout. No external resource ownership/reuse/reset guarantee.','Output code-unit cap is not a JSON parser heap/object-count or total peak-memory bound.','Default object deliberately remains mutable with Node order arrayBuffer,blob,buffer,text,json; frozen binding record does not freeze default.']}},'requiredHostInterfaces':[]}
 manifest_name='builtins/node-compat/export-manifest.stream-consumers.node-v22.14.0.json'
 jsonput('proposed/'+manifest_name,manifest)
 sources=[('facade.mjs',facade),(Path(manifest_name).name,json.dumps(manifest,indent=2)+'\n')]
 script=facade.replace('export const ','const ').replace('export function ','function ')
 assert not any(line.startswith(('import ','export '))for line in script.splitlines())
 factory="(function(argument){\n'use strict';\n"+script+'\nreturn createConsumersModule(argument);\n})'
 assert ')SM_NODE_PROFILE"'not in factory
 digest=hashlib.sha256()
 for name,source in sources:digest.update((name+'\0'+source+'\0').encode())
 header='// Generated UNAPPLIED stream-consumers factory.\n// Canonical-source SHA-256: '+digest.hexdigest()+'\nstatic constexpr const char kStreamConsumersFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\n'
 put('proposed/'+base+'factories.generated.h',header)
 generator="""// Source/schema/parse checks only; never invoke the consumer factory.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),at=process.argv.indexOf('--repository');assert(at>=0);const repository=resolve(process.argv[at+1]);
const {validateManifest}=await import(pathToFileURL(join(repository,'builtins/node-compat/validate-manifest.mjs')));
const name='export-manifest.stream-consumers.node-v22.14.0.json',manifestSource=await readFile(join(here,'../'+name),'utf8'),manifest=JSON.parse(manifestSource);
validateManifest(manifest,JSON.parse(await readFile(join(repository,'builtins/node-compat/manifest.schema.json'),'utf8')));
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.14');assert.deepEqual(Object.keys(manifest.modules),['node:stream/consumers']);assert.deepEqual(manifest.modules['node:stream/consumers'].exports,['arrayBuffer','blob','buffer','default','json','text']);
const facade=await readFile(join(here,'facade.mjs'),'utf8');assert(!facade.includes('globalThis'));const script=facade.replace(/^export const /gm,'const ').replace(/^export function /gm,'function ');assert(!/^\\s*(?:import|export)\\b/m.test(script));
const factory="(function(argument){\\n'use strict';\\n"+script+'\\nreturn createConsumersModule(argument);\\n})';assert(!factory.includes(')SM_NODE_PROFILE"'));new vm.Script(factory,{filename:'<unapplied-stream-consumers-factory>'});
const digest=createHash('sha256');for(const[n,s]of[['facade.mjs',facade],[name,manifestSource]])digest.update(n+'\\0'+s+'\\0');
const output='// Generated UNAPPLIED stream-consumers factory.\\n// Canonical-source SHA-256: '+digest.digest('hex')+'\\nstatic constexpr const char kStreamConsumersFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\\n';
const target=join(here,'factories.generated.h');if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),output);else await writeFile(target,output,{flag:'wx'});
console.log(JSON.stringify({state:'STREAM_CONSUMERS_SCHEMA_SOURCE_PARSE_ONLY_PASSED',bindings:6,factoryInvoked:false,guestExecuted:false}));
"""
 put('proposed/'+base+'generate-factory.mjs',generator)
 installer='''#ifdef NODE_COMPAT_STREAM_CONSUMERS
static bool install_stream_consumers(api::Engine *engine) {
  auto *cx = engine->cx(); // install() already entered CONTENT before user code.
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument) return false;
  JS::RootedValue value(cx);
  for (const char *name : {"TextDecoder", "ArrayBuffer", "Uint8Array", "DataView"}) {
    if (!JS_GetProperty(cx, engine->global(), name, &value)) return false;
    if (!value.isObject()) {
      JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: stream consumers native dependency unavailable");
      return false;
    }
    if (!JS_DefineProperty(cx, argument, name, value, 0)) return false;
  }
  JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kStreamConsumersFactorySource, argument_value, &module)) return false;
  return engine->define_builtin_module("node:stream/consumers", module) &&
         engine->define_builtin_module("stream/consumers", module);
}
#endif

'''
 register=replacement('builtins/node-compat/register.cpp',[( '#ifdef NODE_COMPAT_ZLIB\n#include "zlib/factories.generated.h"\n#endif', '#ifdef NODE_COMPAT_ZLIB\n#include "zlib/factories.generated.h"\n#endif\n#ifdef NODE_COMPAT_STREAM_CONSUMERS\n#include "stream-consumers/factories.generated.h"\n#endif'),('bool install(api::Engine *engine) {',installer+'bool install(api::Engine *engine) {'),('  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);','#ifdef NODE_COMPAT_STREAM_CONSUMERS\n  if (!install_stream_consumers(engine)) return false;\n#endif\n  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);')])
 cmake='''
# Independent optional consumers: existing native decoder, no new C++ kernel.
option(NODE_COMPAT_STREAM_CONSUMERS "Enable bounded node:stream/consumers text/json" OFF)
if(NODE_COMPAT_STREAM_CONSUMERS AND NOT CMAKE_SCRIPT_MODE_FILE)
    if(NOT TARGET builtin_node_compat OR NOT TARGET builtin_web_text_codec)
        message(FATAL_ERROR "NODE_COMPAT_STREAM_CONSUMERS requires existing Node and native TextCodec builtins")
    endif()
    target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_STREAM_CONSUMERS=1)
    add_dependencies(builtin_node_compat builtin_web_text_codec)
    target_link_libraries(builtin_node_compat PRIVATE builtin_web_text_codec)
endif()
'''
 cmake_before=(BASE/'cmake/builtins.cmake').read_text();put('proposed/cmake/builtins.cmake',cmake_before+cmake)
 cmake_proof={'path':'cmake/builtins.cmake','beforeSha256':sha(cmake_before.encode()),'afterSha256':sha((cmake_before+cmake).encode()),'edits':[{'old':'','new':cmake,'count':1,'kind':'append'}],'reverseExact':True}
 added=[base+n for n in['facade.mjs','factories.generated.h','generate-factory.mjs','LICENSE.node']]+[manifest_name]
 after=dict(before)
 for row in[register,cmake_proof]:assert before[row['path']]==row['beforeSha256'];after[row['path']]=row['afterSha256']
 for name in added:assert name not in before;after[name]=sha((HERE/'proposed'/name).read_bytes())
 assert len(after)==355 and sum(after[p]==before[p]for p in before)==348
 changes=[register,cmake_proof]
 jsonput('native-derivations.json',{'schemaVersion':1,'parentSources':350,'afterSources':355,'unchangedParentSources':348,'changes':changes,'addedSources':added,'newCppTranslationUnits':0,'actualNativeCompileCountUnchangedUntilFutureBuild':True})
 jsonput('expected-native-source-manifest.json',[{'path':name,'sha256':digest}for name,digest in sorted(after.items())])
 patch=''
 for name in added+['builtins/node-compat/register.cpp','cmake/builtins.cmake']:
  before_text=(BASE/name).read_text()if name in before else'';after_text=(HERE/'proposed'/name).read_text()
  patch+=''.join(difflib.unified_diff(before_text.splitlines(True),after_text.splitlines(True),fromfile='a/'+name if name in before else'/dev/null',tofile='b/'+name))
 put('native.UNAPPLIED.patch',patch)
 print(json.dumps({'nativeSources':355,'added':5,'replaced':2,'unchanged':348,'cppUnitsAdded':0,'factoryInvoked':False,'nativeOrGuestExecuted':False}))
if __name__=='__main__':main()
