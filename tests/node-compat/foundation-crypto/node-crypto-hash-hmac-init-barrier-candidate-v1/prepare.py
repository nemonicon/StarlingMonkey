"""UNAPPLIED Source derivation; no compiler/engine/crypto/snapshot action."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')
EMBED=WORK/'componentize-abi-fixed-bigint-v1-hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/embedding/embedding.cpp'
def row(path):
 path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(path):return json.loads(Path(path).read_bytes())
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
 metadata_path=WORK/'artifacts/starlingmonkey_embedding.abi-i32-i64-v1.hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.hashhmac357v3.wasm.build.json'
 metadata=read(metadata_path);assert len(metadata)==83 and row(metadata_path)['sha256']=='2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
 parent={r['path']:r for r in metadata['sourceManifest']};assert len(parent)==357
 edits={
  'include/node-compat-entropy.h':[("void begin_engine(bool pre_initialize);","void begin_engine(bool pre_initialize);\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\n// Read-only private lifecycle state, independent of entropy availability.\nbool deployed_execution_started();\n#endif",1)],
  'builtins/node-compat/entropy-policy.cpp':[("void begin_engine(bool pre_initialize) { deployed = !pre_initialize; }","void begin_engine(bool pre_initialize) { deployed = !pre_initialize; }\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nbool deployed_execution_started() { return deployed; }\n#endif",1)],
  'builtins/node-compat/hash-hmac-kernel.cpp':[
   ('#include "builtin.h"','#include "builtin.h"\n#include "extension-api.h"\n#include "node-compat-entropy.h"',1),
   ('DEF_ERR(CryptoLimit, JSEXN_RANGEERR, "Native SHA256 profile limit exceeded", 0)',
    'DEF_ERR(CryptoLimit, JSEXN_RANGEERR, "Native SHA256 profile limit exceeded", 0)\nDEF_ERR(CryptoInitialization, JSEXN_TYPEERR,\n        "ERR_SM_NODE_CRYPTO_INITIALIZATION: {0} requires deployed execution", 1)',1),
   ('struct MdFree {', '''// A completed Engine pre-init is earlier than the embedding's FINAL snapshot
// boundary. Only the existing real deployed-export hook opens this barrier.
// No state/provider/key/output access is permitted before it opens.
static bool require_runtime(JSContext *cx, const char *operation) {
  auto *engine = api::Engine::get(cx);
  if (engine && engine->state() == api::EngineState::Initialized &&
      entropy::deployed_execution_started()) return true;
  api::throw_error(cx, CryptoInitialization, operation);
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception) || !exception.isObject()) return false;
  JS::RootedObject object(cx, &exception.toObject());
  JS::RootedString name(cx, JS_NewStringCopyZ(cx, "TypeError"));
  if (!name) return false;
  JS::RootedString code(cx, JS_NewStringCopyZ(cx, "ERR_SM_NODE_CRYPTO_INITIALIZATION"));
  if (!code) return false;
  JS::RootedString op(cx, JS_NewStringCopyZ(cx, operation));
  if (!op) return false;
  JS::RootedValue name_value(cx, JS::StringValue(name));
  JS::RootedValue code_value(cx, JS::StringValue(code));
  JS::RootedValue operation_value(cx, JS::StringValue(op));
  // Match the existing entropy diagnostic helper: strings are allocated before
  // clearing the pending error, and OOM while decorating remains pending.
  JS_ClearPendingException(cx);
  if (!JS_DefineProperty(cx, object, "name", name_value, 0) ||
      !JS_DefineProperty(cx, object, "code", code_value, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, object, "operation", operation_value, JSPROP_ENUMERATE)) return false;
  JS_SetPendingException(cx, exception);
  return false;
}
struct MdFree {''',1),
   ('static bool create_hash(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);','static bool create_hash(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);\n  if (!require_runtime(cx, "createHash")) return false;',1),
   ('static bool create_hmac(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);','static bool create_hmac(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);\n  if (!require_runtime(cx, "createHmac")) return false;',1),
   ('static bool update(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);','static bool update(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);\n  if (!require_runtime(cx, "Hash/Hmac.update")) return false;',1),
   ('static bool digest(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);','static bool digest(JSContext *cx, unsigned argc, JS::Value *vp) {\n  auto args = JS::CallArgsFromVp(argc, vp);\n  if (!require_runtime(cx, "Hash/Hmac.digest")) return false;',1)]}
 changes=[];proposed=dict(parent)
 for name,patches in edits.items():
  before=SOURCE/name;d=row(before);assert d['sha256']==parent[name]['sha256'];text=before.read_text();out=text
  for old,new,count in patches:assert out.count(old)==count;out=out.replace(old,new)
  inverse=out
  for old,new,count in reversed(patches):assert inverse.count(new)==count;inverse=inverse.replace(new,old)
  assert inverse==text
  after=OWN/'after'/name;after.parent.mkdir(parents=True,exist_ok=True);after.write_text(out)
  changes.append(dict(path=name,before=d,after=row(after),edits=[dict(before=a,after=b,count=c)for a,b,c in patches],forwardAndInverseVerified=True));proposed[name]=dict(path=name,sha256=row(after)['sha256'])
 assert len(proposed)==357 and sum(proposed[p]==parent[p]for p in parent)==354
 save('derivations.json',dict(schemaVersion=1,files=changes))
 save('inventory.json',dict(schemaVersion=1,nativeSourceFiles=357,retainedParentNativeFiles=354,changedNativeFiles=3,newNativePaths=0,externalEmbeddingSources=3,externalEmbeddingChanges=0,expectedNativeManifest=sorted(proposed.values(),key=lambda r:r['path']),unchangedExternalManifest=metadata['componentizeSourceManifest'],newNativeBuildClaim=False))
 refs=dict(schemaVersion=1,parentEngine=row(Path(str(metadata_path).removesuffix('.build.json'))),parentMetadata=row(metadata_path),parentConfiguredSourceRoot=str(SOURCE),parentWorkRoot=str(WORK),parentSourceIndex=row(OWN.parent/'node-crypto-hash-hmac-native-integration-candidate-v1/index.json'),parentProducerIndex=row(OWN.parent/'node-crypto-hash-hmac-native-controller-candidate-v3/index.json'),changedBeforeRows=[r['before']for r in changes],embeddingHook=row(EMBED),bindingGenerator=row(EMBED.parents[1]/'crates/spidermonkey-embedding-splicer/src/bindgen.rs'),engineLifecycle=row(SOURCE/'runtime/engine.cpp'),engineApi=row(SOURCE/'include/extension-api.h'),wizerHook=row(SOURCE/'runtime/js.cpp'),existingRequestGuard=row(SOURCE/'include/builtin.h'),existingErrorApi=row(SOURCE/'runtime/builtin.cpp'),factory=row(SOURCE/'builtins/node-compat/crypto-factory.generated.h'),install=row(SOURCE/'builtins/node-compat/register.cpp'),cmake=row(SOURCE/'cmake/builtins.cmake'),node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024),actualNewNativeIntegration=None,actualNewProducer=None,actualNewBuild=None,actualSnapshotRefusal=None,rootAuthority=None,sourcePeer=None,runtimeAuthority=None)
 save('references.json',refs)
 print(json.dumps(dict(changedFiles=3,newPaths=0,retained=354,nativeFiles=357)))
if __name__=='__main__':main()
