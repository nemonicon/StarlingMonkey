"""Only own afterimages/manifests; no native action or production source edit."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[3]
FROZEN=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
assert not(OWN/'index.json').exists()
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
metadata=read(FROZEN/'normal-off.engine.wasm.build.json');assert d(FROZEN/'normal-off.engine.wasm.build.json')['sha256']=='2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
assert len(metadata['sourceManifest'])==357 and len(metadata)==83
edits=[]
def afterimage(path,changes):
 src=FROZEN/'source'/path;text=src.read_text();original=text
 for before,after in changes:
  assert text.count(before)==1,(path,before);text=text.replace(before,after)
 target=OWN/'after'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
 inverse=text
 for before,after in reversed(changes):assert inverse.count(after)==1;inverse=inverse.replace(after,before)
 assert inverse==original
 edits.append(dict(path=path,before=d(src),after=d(target),edits=[dict(before=a,after=b,count=1)for a,b in changes],forwardAndInverseVerified=True))
afterimage('runtime/script_loader.h',[(
 '  static bool define_builtin_module(const char* id, HandleValue builtin);',
 '  static bool define_builtin_module(const char* id, HandleValue builtin);\n#ifdef NODE_COMPAT_MODULE\n  // New private guest CJS provider seam; no new component/host export.\n  static bool lookup_registered_builtin(JSContext *cx, JS::HandleString id,\n                                         JS::MutableHandleValue result);\n#endif')])
afterimage('runtime/script_loader.cpp',[(
 'bool ScriptLoader::define_builtin_module(const char *id, HandleValue builtin) {',
 '#ifdef NODE_COMPAT_MODULE\nbool ScriptLoader::lookup_registered_builtin(JSContext *cx, JS::HandleString id,\n                                              JS::MutableHandleValue result) {\n  JS::RootedValue key(cx, JS::StringValue(id));\n  return JS::MapGet(cx, builtinModules, key, result);\n}\n#endif\n\nbool ScriptLoader::define_builtin_module(const char *id, HandleValue builtin) {')])
afterimage('builtins/node-compat/register.cpp',[
 ('#include "factories.generated.h"','#include "factories.generated.h"\n#ifdef NODE_COMPAT_MODULE\n#include "module-factory.generated.h"\n#endif'),
 ('JSObject *create_kernel(JSContext *cx);','JSObject *create_kernel(JSContext *cx);\n#ifdef NODE_COMPAT_MODULE\nJSObject *create_module_kernel(JSContext *cx);\n#endif'),
 ('#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nstatic bool install_crypto_hash_hmac',
 '#ifdef NODE_COMPAT_MODULE\nstatic bool install_module(api::Engine *engine) {\n  auto *cx=engine->cx();\n  JS::RootedObject kernel(cx,create_module_kernel(cx));if(!kernel)return false;\n  JS::RootedValue value(cx,JS::ObjectValue(*kernel)),record(cx);\n  if(!evaluate_factory(cx,kModuleFactorySource,value,&record))return false;\n  return engine->define_builtin_module("node:module",record) &&\n         engine->define_builtin_module("module",record);\n}\n#endif\n\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nstatic bool install_crypto_hash_hmac'),
 ('  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);',
 '#ifdef NODE_COMPAT_MODULE\n  if (!install_module(engine)) return false;\n#endif\n  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);')])
afterimage('cmake/builtins.cmake',[(
 'if(TARGET builtin_node_compat)\n    option(NODE_COMPAT_CRYPTO_HASH_HMAC',
 'option(NODE_COMPAT_MODULE "Experimental synchronous CommonJS node:module" OFF)\nif(NODE_COMPAT_MODULE AND NOT TARGET builtin_node_compat AND NOT CMAKE_SCRIPT_MODE_FILE)\n    message(FATAL_ERROR "NODE_COMPAT_MODULE requires ENABLE_BUILTIN_NODE_COMPAT=ON")\nendif()\nif(TARGET builtin_node_compat)\n    if(NODE_COMPAT_MODULE)\n        target_sources(builtin_node_compat PRIVATE builtins/node-compat/module-kernel.cpp)\n        target_compile_definitions(extension_api INTERFACE NODE_COMPAT_MODULE=1)\n    endif()\n    option(NODE_COMPAT_CRYPTO_HASH_HMAC')])
inv=read(OWN/'node-inventory.json');supported=['Module','createRequire','isBuiltin','_cache','_extensions','_load','_nodeModulePaths','_resolveFilename','_resolveLookupPaths','_pathCache','_initPaths','builtinModules','globalPaths','default','constants']
manifest=dict(schemaVersion=1,profileVersion='sm-node-22.14.0-m0.17',nodeVersion='v22.14.0',status='UNEXECUTED native-provider candidate; host-only loader tests do not establish linked guest support.',moduleContract='Real guest CommonJS +JSON loader over native JSAPI/standard-WASI filesystem; mutable Next require hooks; finite POSIX scope, no npm ESM/native addons.',modules={'node:module':dict(aliases=['module'],status='partial',exports=inv['namespaceKeys'],supportedStatic=supported,supportedPrototype=['require','load','_compile'],importOnlyExports=[n for n in inv['namespaceKeys']if n not in supported],callablePolicy='Synchronous CJS and JSON; actual native defaults for registered Node builtins, real Module cache/cycles and resolver interposition. Unimplemented operations throw ERR_SM_NODE_UNSUPPORTED.',limits=dict(pathCodeUnits=4096,sourceBytes=16777216,moduleCacheEntries=8192),deviations=['POSIX only; NODE_PATH/global home search is not provided.','Synchronous npm ESM, package imports (#), source-map/loader hooks, TypeScript, compile cache and native addon execution are not implemented.','Prefix-only Node builtins are known, but unavailable installed native bindings refuse; no builtin JS adapter or empty success stub.','CJS circular-warning Proxy behavior is not implemented; partial cached exports are preserved.','Native provider currently requires valid UTF8 files and uses generic IO errors for nonmissing native filesystem errors.','Static Node constants describe enum values only, not operational compile-cache support.'])},requiredHostInterfaces=['wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10'])
save('export-manifest.module.node-v22.14.0.json',manifest)
license=REPO/'builtins/node-compat/classic-streams/LICENSE.node';(OWN/'module.LICENSE.node').write_bytes(license.read_bytes())
new=[('module-kernel.cpp','module-kernel.cpp'),('module-core.mjs','module-core.mjs'),('module-factory.generated.h','module-factory.generated.h'),('generate-module-factory.mjs','generate-module-factory.mjs'),('export-manifest.module.node-v22.14.0.json','export-manifest.module.node-v22.14.0.json'),('module.LICENSE.node','module.LICENSE.node')]
sources={r['path']:r['sha256']for r in metadata['sourceManifest']};old=sources.copy()
for r in edits:assert sources[r['path']]==r['before']['sha256'];sources[r['path']]=r['after']['sha256']
new_rows=[]
for name,origin in new:
 path='builtins/node-compat/'+name;assert path not in sources;row=d(OWN/origin);sources[path]=row['sha256'];new_rows.append(dict(path=path,origin=row))
save('derivations.json',dict(schemaVersion=1,files=edits,newSourcePaths=new_rows))
save('prospective-source-manifest.json',dict(schemaVersion=1,parentMetadata=d(FROZEN/'normal-off.engine.wasm.build.json'),nativeSourceFiles=len(sources),retainedNativeFiles=sum(old[k]==sources[k]for k in old),changedNativeFiles=len(edits),newNativeFiles=len(new_rows),files=[dict(path=k,sha256=sources[k])for k in sorted(sources)],externalEmbeddingSources=metadata['componentizeSourceManifest'],externalEmbeddingChanges=0,actualBuilt=False,actualMetadataSchema=None))
api_headers=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/spidermonkey-dist-release/include')
inputs=[d(FROZEN/'source'/r['path'])for r in metadata['sourceManifest']]
inputs += [d(api_headers/n)for n in ['js/CompilationAndEvaluation.h','js/EnvironmentChain.h','js/MapAndSet.h','js/String.h','jsapi.h']]
inputs += [d(REPO/'runtime/script_loader.cpp'),d(REPO/'runtime/script_loader.h'),d(REPO/'builtins/node-compat/manifest.schema.json'),d(REPO/'builtins/node-compat/validate-manifest.mjs'),d(license)]
k=REPO/'tests/node-compat/foundation-crypto'
refs=dict(schemaVersion=1,parentFrozenReviewIndex=d(k/'independent-node-crypto-hash-hmac-frozen-artifact-review-v1/index.json'),parentFrozenReviewResult=d(k/'independent-node-crypto-hash-hmac-frozen-artifact-review-v1/results.json'),parentFrozenReceipt=d(FROZEN/'normal-off-freeze-receipt.json'),parentFrozenEngine=d(FROZEN/'normal-off.engine.wasm'),parentFrozenMetadata=d(FROZEN/'normal-off.engine.wasm.build.json'),parentEngineRole='Revalidated/frozen artifact from original recipe0/parent1+1/preservationfalse, not a successful original BUILD receipt.',nativeProvider='Own uncompiled module-kernel.cpp +new private ScriptLoader::lookup_registered_builtin; no host service.',hostTestProvider='test-provider.mjs only; never packaged into native sources',sourcePeer=None,rootAuthority=None,actualNativeIntegration=None,actualNativeBuild=None,actualComponent=None,actualRuntime=None,operationalAdmission=False)
save('references.json',refs);save('input-hashes.json',dict(schemaVersion=1,scope='357 actual frozen native beforeimages +finite genuine API headers/schema/live common loader files. No SDK/history tree duplication.',files=inputs))
save('future-authority.json',dict(schemaVersion=1,state='UNISSUED_NODE_MODULE_CJS_SOURCE_TEMPLATE',sourcePeer=None,rootAuthority=None,nativeCompileAllowed=None,nativeBuildAllowed=None,sourceStageAllowed=None,componentizationAllowed=None,guestAllowed=None))
print(json.dumps({"state":"OWN_UNCOMPILED_SOURCE_ONLY",'nativeSources':len(sources),'retained':sum(old[k]==sources[k]for k in old),'changed':len(edits),'new':len(new_rows),'externalEmbedding':3,'actionsInvoked':False}))
