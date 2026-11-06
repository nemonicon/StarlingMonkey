"""Own Buffer.concat afterimages only; no native/frontend/guest action."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[2];BASE=REPO/'builtins/node-compat';OUT=OWN/'native/builtins/node-compat'
assert not(OWN/'index.json').exists();OUT.mkdir(parents=True,exist_ok=True)
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
for n in ['unsupported.mjs','child-process.mjs','manifest.schema.json','validate-manifest.mjs']:(OUT/n).write_bytes((BASE/n).read_bytes())
facade=r'''
  // Native copying is private; all user list/property activity finishes before
  // its pointer-borrowing phase. Promote only the existing concat slot below.
  const concatApply=Reflect.apply,concatIsArray=Array.isArray,ConcatArray=Array;
  const concatOwn=Object.getOwnPropertyDescriptor,concatDefine=Object.defineProperty,concatHasOwn=Object.hasOwn;
  const concatFinite=Number.isFinite,concatInteger=Number.isInteger;
  const ConcatTypeError=TypeError,ConcatRangeError=RangeError;
  const concatKernel=kernel.concat,MaxConcatItems=65536;
  function concatFail(Ctor,code,message) {
    const e=new Ctor(message);
    concatDefine(e,'code',{__proto__:null,value:code,writable:true,configurable:true,enumerable:true});
    concatDefine(e,'module',{__proto__:null,value:'node:buffer',writable:true,configurable:true,enumerable:true});
    concatDefine(e,'operation',{__proto__:null,value:'Buffer.concat',writable:true,configurable:true,enumerable:true});
    throw e;
  }
  function concatUnsupported(message) { concatFail(ConcatTypeError,'ERR_SM_NODE_UNSUPPORTED',message); }
  function concatView(view,index) {
    let name,buffer,length;
    try { name=concatApply(typedName,view,[]);length=concatApply(typedByteLength,view,[]);buffer=concatApply(typedBuffer,view,[]); }
    catch { concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE',`list[${index}] must be a Buffer or Uint8Array`); }
    if(name!=='Uint8Array')concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE',`list[${index}] must be a Buffer or Uint8Array`);
    for(const key of ['length','byteLength','byteOffset','buffer'])if(concatOwn(view,key))concatUnsupported('Shadowed typed-array metadata is outside Buffer.concat');
    try { concatApply(abByteLength,buffer,[]); }
    catch { concatUnsupported('Shared or invalid Buffer.concat backing'); }
    if(abResizable&&concatApply(abResizable,buffer,[]))concatUnsupported('Resizable Buffer.concat backing');
    if(abDetached&&concatApply(abDetached,buffer,[]))concatUnsupported('Detached Buffer.concat backing');
    if(!abDetached&&length===0)try{new U8(buffer,0,0);}catch{concatUnsupported('Detached Buffer.concat backing');}
    if(length>MAX_LENGTH)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','Buffer.concat input exceeds16MiB');
    return length;
  }
  function concat(list,length) {
    if(!concatIsArray(list))concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE','list must be an Array');
    const count=concatOwn(list,'length').value;
    // Node ignores length completely for an empty array, even if it is invalid.
    if(count===0)return tagTrusted(new U8(0));
    if(count>MaxConcatItems)concatFail(ConcatRangeError,'ERR_SM_NODE_LIMIT','Buffer.concat chunk count exceeds65536');
    if(length!==undefined) {
      if(typeof length!=='number')concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE','length must be a number');
      if(!concatFinite(length)||!concatInteger(length)||length<0||length>MAX_LENGTH)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','length must be an integer between0and16777216');
    }
    const snapshot=new ConcatArray(count);let sum=0;
    for(let i=0;i<count;i++) {
      const item=concatOwn(list,i);
      if(!item||!concatHasOwn(item,'value'))concatUnsupported('Sparse/accessor Buffer.concat list is outside this profile');
      const value=item.value;
      // Preserve Node's uncoded null/undefined .length TypeError in omitted-
      // length calls; invalid non-null element kinds use ERR_INVALID_ARG_TYPE.
      if(length===undefined&&value==null)value.length;
      const bytes=concatView(value,i);
      if(length===undefined) {if(bytes>MAX_LENGTH-sum)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','Buffer.concat total exceeds16MiB');sum+=bytes;}
      concatDefine(snapshot,i,{__proto__:null,value,writable:false,configurable:false,enumerable:true});
    }
    return tagTrusted(concatApply(concatKernel,undefined,[snapshot,length===undefined?sum:length]));
  }
'''
kernel=r'''
// Facade supplies an inaccessible dense snapshot, but native types/backing and
// arithmetic are checked independently. No pointer survives an allocation.
static bool concat_bytes(JSContext *cx,unsigned argc,JS::Value *vp) {
  auto args=JS::CallArgsFromVp(argc,vp);
  if(!args.requireAtLeast(cx,"concat",2))return false;
  if(!args[0].isObject()||!args[1].isNumber())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  JS::RootedObject list(cx,&args[0].toObject());bool array=false;
  if(!JS::IsArrayObject(cx,list,&array))return false;
  if(!array)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  double number=args[1].toNumber();
  if(!std::isfinite(number)||number<0||number>MaxLength||std::floor(number)!=number)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");
  size_t length=static_cast<size_t>(number);uint32_t count=0;
  if(!JS::GetArrayLength(cx,list,&count))return false;
  if(count>65536)return buffer_error(cx,AllocationLimit,"ERR_SM_NODE_LIMIT");
  JS::RootedObjectVector sources(cx);
  for(uint32_t i=0;i<count;i++) {
    JS::RootedValue value(cx);if(!JS_GetElement(cx,list,i,&value))return false;
    if(!value.isObject())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
    JS::RootedObject view(cx,&value.toObject());size_t bytes=0;bool shared=false;uint8_t *ignored=nullptr;
    if(!JS_GetObjectAsUint8Array(view,&bytes,&shared,&ignored))return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
    if(shared||JS::IsResizableArrayBufferView(view))return buffer_error(cx,UnsupportedBacking,"ERR_SM_NODE_UNSUPPORTED");
    JS::RootedObject backing(cx,JS_GetArrayBufferViewBuffer(cx,view,&shared));if(!backing)return false;
    if(shared||JS::IsDetachedArrayBufferObject(backing))return buffer_error(cx,UnsupportedBacking,"ERR_SM_NODE_UNSUPPORTED");
    if(bytes>MaxLength)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");
    if(!sources.append(view)){JS_ReportOutOfMemory(cx);return false;}
  }
  JS::RootedObject output(cx,JS_NewUint8Array(cx,length));if(!output)return false;
  // Recheck after result allocation/possible moving GC, before any borrow.
  for(size_t i=0;i<sources.length();i++) {
    JS::RootedObject view(cx,sources[i]);bool shared=false;
    JS::RootedObject backing(cx,JS_GetArrayBufferViewBuffer(cx,view,&shared));if(!backing)return false;
    if(shared||JS::IsResizableArrayBufferView(view)||JS::IsDetachedArrayBufferObject(backing))return buffer_error(cx,UnsupportedBacking,"ERR_SM_NODE_UNSUPPORTED");
  }
  {
    JS::AutoCheckCannotGC nogc(cx);bool shared=false;
    uint8_t *destination=JS_GetUint8ArrayData(output,&shared,nogc);MOZ_ASSERT(!shared);
    if(length)std::memset(destination,0,length);
    size_t position=0;
    for(size_t i=0;i<sources.length();i++) {
      size_t bytes=JS_GetTypedArrayByteLength(sources[i]);
      size_t take=std::min(bytes,length-position);
      if(take){const uint8_t *source=JS_GetUint8ArrayData(sources[i],&shared,nogc);MOZ_ASSERT(!shared);std::memcpy(destination+position,source,take);}
      position+=take;
    }
  }
  args.rval().setObject(*output);return true;
}
'''
deriv=[]
def edit(name,changes):
 src=BASE/name;text=src.read_text();old=text
 for a,b in changes:assert text.count(a)==1,(name,a[:80]);text=text.replace(a,b)
 (OUT/name).write_text(text);inverse=text
 for a,b in reversed(changes):assert inverse.count(b)==1;inverse=inverse.replace(b,a)
 assert inverse==old
 deriv.append(dict(path='builtins/node-compat/'+name,before=d(src),after=d(OUT/name),edits=[dict(before=a,after=b,count=1)for a,b in changes]))
edit('buffer-facade.mjs',[("  for (const name of ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']) {",facade+"\n  for (const name of ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']) {"),("Buffer[name] = name === 'allocUnsafe' ? allocUnsafe : unavailable", "Buffer[name] = name === 'allocUnsafe' ? allocUnsafe : name === 'concat' ? concat : unavailable")])
edit('buffer.cpp',[( '#include "js/MemoryFunctions.h"','#include "js/MemoryFunctions.h"\n#include "js/Array.h"\n#include "js/GCVector.h"\n#include <algorithm>\n#include <cmath>\n#include <cstring>'),('JSObject *create_kernel(JSContext *cx) {',kernel+'\nJSObject *create_kernel(JSContext *cx) {'),('    JS_FN("hexDecode", hex_decode, 1, JSPROP_ENUMERATE),','    JS_FN("hexDecode", hex_decode, 1, JSPROP_ENUMERATE),\n    JS_FN("concat", concat_bytes, 2, JSPROP_ENUMERATE),')])
edit('generate-factories.mjs',[("// The optional Path header is independent:","// --core-only skips optional generators only for isolated core Source packaging.\nif (!process.argv.includes('--core-only')) {\n// The optional Path header is independent:"),("  import('./generate-stream-web-factory.mjs'),\n]);","  import('./generate-stream-web-factory.mjs'),\n]);\n}")])
manifest=json.loads((BASE/'export-manifest.node-v22.14.0.json').read_bytes());manifest['profileVersion']='sm-node-22.14.0-m0.18';manifest['status']='UNCOMPILED isolated Buffer.concat Source successor; no native runtime/adoption claim.'
b=manifest['modules']['node:buffer'];b['unsupportedStatic'].remove('concat');b['supportedStatic'].append('concat(dense Array<fixed Buffer|Uint8Array>, integerTotalLength?): copy visible windows; truncate/zero-pad; empty ignores length')
b['limits']['MAX_CONCAT_ITEMS']=65536
b['deviations'] += ['concat output and every visible input are bounded to16MiB; at most65536 dense own-data items.','concat rejects sparse/accessor lists, shadowed typed metadata, shared/resizable/detached backing. Proxy/custom prototype/metadata getter timing is not Node parity.','concat snapshots validated input references before allocation; Node list access/allocation/error-message timing and caller-replaced allocUnsafe semantics are not reproduced.','concat preserves its existing constructor property slot; output is fresh exact zeroed fixed backing, never Node slab storage.']
(OUT/'export-manifest.node-v22.14.0.json').write_text(json.dumps(manifest,indent=2)+'\n')
save('derivations.json',dict(schemaVersion=1,files=deriv,manifestBefore=d(BASE/'export-manifest.node-v22.14.0.json'),manifestAfter=d(OUT/'export-manifest.node-v22.14.0.json'),generatedHeaderPending=True))
sdk=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/spidermonkey-dist-release/include')
save('inputs.json',dict(schemaVersion=1,productionFiles=[d(BASE/n)for n in ['buffer.cpp','buffer-facade.mjs','factories.generated.h','generate-factories.mjs','export-manifest.node-v22.14.0.json','unsupported.mjs','child-process.mjs','manifest.schema.json','validate-manifest.mjs']],apiHeaders=[d(sdk/n)for n in ['js/Array.h','js/GCVector.h','js/experimental/TypedData.h','js/ArrayBuffer.h','js/ArrayBufferMaybeShared.h']],nodeSource=d(OWN/'node22-buffer-source.txt'),productionSourceEdited=False))
save('future-authority.json',dict(schemaVersion=1,sourcePeer=None,rootAuthority=None,nativeCompilerAllowed=None,nativeBuildAllowed=None,guestAllowed=None))
print(json.dumps({'state':'OWN_SOURCE_AFTERIMAGES_ONLY','nativeActionsInvoked':False}))
