// UNCOMPILED persistent guest zlib. No JS edges/pointers retained in codec state.
#include "builtin.h"
#include "node-compat-entropy.h"
#include "js/ArrayBuffer.h"
#include <zlib.h>
#include <array>
#include <cmath>
#include <cstring>
#include <memory>
#include <new>
#if !defined(NODE_COMPAT_ZLIB) || !defined(NODE_COMPAT_ZLIB_STREAMING)
#error "Streaming codec requires both explicit optional profile flags"
#endif
#if defined(Z_PREFIX) || defined(Z_PREFIX_SET)
#error "Use only selected SpiderMonkey MOZ_Z_ codec mappings"
#endif

namespace builtins::node_compat::zlib_profile {
namespace {
constexpr size_t Staging=64*1024,MaxInput=64*1024*1024,MaxOutput=80*1024*1024;
constexpr size_t MaxSteps=65536,MaxHandles=16;
size_t live_handles=0;
DEF_ERR(StreamFailure,JSEXN_ERR,"Bounded streaming zlib operation failed",0)
DEF_ERR(StreamInit,JSEXN_TYPEERR,"Streaming zlib requires deployed execution",0)
bool text(JSContext* cx,JS::HandleObject o,const char* key,const char* value){
  JS::RootedString s(cx,JS_NewStringCopyZ(cx,value));if(!s)return false;
  JS::RootedValue v(cx,JS::StringValue(s));return JS_DefineProperty(cx,o,key,v,JSPROP_ENUMERATE);
}
bool fail(JSContext* cx,const char* code,const char* op,bool initialization=false){
  if(initialization)api::throw_error(cx,StreamInit);else api::throw_error(cx,StreamFailure);
  JS::RootedValue pending(cx);if(!JS_GetPendingException(cx,&pending)||!pending.isObject())return false;
  JS::RootedObject e(cx,&pending.toObject());JS_ClearPendingException(cx);
  if(!text(cx,e,"code",code)||!text(cx,e,"operation",op)||!text(cx,e,"module","node:zlib"))return false;
  JS_SetPendingException(cx,pending);return false;
}
bool deployed(JSContext* cx,const char* op){
  auto* engine=api::Engine::get(cx);
  return engine&&engine->state()==api::EngineState::Initialized&&entropy::deployed_execution_started()
      ?true:fail(cx,"ERR_SM_NODE_ZLIB_INITIALIZATION",op,true);
}
bool integer(JSContext* cx,JS::HandleValue v,int minimum,int maximum,int* out,const char* op){
  if(!v.isNumber())return fail(cx,"ERR_INVALID_ARG_TYPE",op);
  double n=v.toNumber();if(!std::isfinite(n)||std::floor(n)!=n||n<minimum||n>maximum)return fail(cx,"ERR_OUT_OF_RANGE",op);
  *out=static_cast<int>(n);return true;
}
struct State {
  z_stream z{};
  std::array<uint8_t,Staging> input{},output{};
  bool initialized=false,counted=false,pending=false,ended=false;
  int flush=Z_NO_FLUSH;size_t input_bytes=0,output_bytes=0,steps=0,chunk=16384;
  void end(){if(initialized){initialized=false;deflateEnd(&z);}z.next_in=nullptr;z.avail_in=0;z.next_out=nullptr;z.avail_out=0;}
  ~State(){end();if(counted){MOZ_ASSERT(live_handles>0);live_handles--;}}
};
void retire(JSObject* object){
  auto slot=JS::GetReservedSlot(object,0);
  if(!slot.isUndefined()){auto* state=static_cast<State*>(slot.toPrivate());JS::SetReservedSlot(object,0,JS::UndefinedValue());delete state;}
}
void finalize(JS::GCContext*,JSObject* object){retire(object);}
const JSClassOps Ops={.finalize=finalize};
const JSClass Class={"PrivateNodeZlibStream",JSCLASS_HAS_RESERVED_SLOTS(1)|JSCLASS_FOREGROUND_FINALIZE,&Ops};
State* get(JSContext* cx,JS::HandleValue value){
  if(!value.isObject()||JS::GetClass(&value.toObject())!=&Class){fail(cx,"ERR_SM_ZLIB_STREAM_STATE","handle");return nullptr;}
  auto slot=JS::GetReservedSlot(&value.toObject(),0);
  if(slot.isUndefined()){fail(cx,"ERR_SM_ZLIB_STREAM_STATE","closed");return nullptr;}
  return static_cast<State*>(slot.toPrivate());
}
bool phase(JSContext* cx,unsigned argc,JS::Value* vp){auto args=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"stream"))return false;args.rval().setUndefined();return true;}
bool open(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"open"))return false;
  if(!args.requireAtLeast(cx,"openZlibStream",6))return false;
  int format,level,window,mem,strategy,chunk;
  if(!integer(cx,args[0],0,1,&format,"format")||!integer(cx,args[1],-1,9,&level,"level")||
     !integer(cx,args[2],format?9:8,15,&window,"windowBits")||!integer(cx,args[3],1,9,&mem,"memLevel")||
     !integer(cx,args[4],0,4,&strategy,"strategy")||!integer(cx,args[5],64,Staging,&chunk,"chunkSize"))return false;
  const char* version=zlibVersion();if(!version||std::strcmp(version,ZLIB_VERSION))return fail(cx,"ERR_SM_ZLIB_BACKEND_MISMATCH","open");
  if(live_handles==MaxHandles)return fail(cx,"ERR_SM_ZLIB_STREAM_LIMIT","handles");
  auto state=std::unique_ptr<State>(new(std::nothrow)State());if(!state){JS_ReportOutOfMemory(cx);return false;}
  // zalloc/zfree/opaque remain NULL: selected guest zlib's allocator family.
  int status=deflateInit2(&state->z,level,Z_DEFLATED,window+(format?16:0),mem,strategy);
  if(status!=Z_OK){if(status==Z_MEM_ERROR){JS_ReportOutOfMemory(cx);return false;}return fail(cx,"ERR_SM_ZLIB_STREAM_INIT","deflateInit2");}
  state->initialized=true;state->chunk=static_cast<size_t>(chunk);
  JS::RootedObject handle(cx,JS_NewObject(cx,&Class));if(!handle)return false;
  state->counted=true;live_handles++;JS::SetReservedSlot(handle,0,JS::PrivateValue(state.release()));
  args.rval().setObject(*handle);return true;
}
bool feed(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"feed"))return false;
  if(!args.requireAtLeast(cx,"feedZlibStream",3))return false;
  auto* state=get(cx,args[0]);if(!state)return false;
  if(state->pending||state->ended)return fail(cx,"ERR_SM_ZLIB_STREAM_STATE","feed");
  int flush;if(!integer(cx,args[2],0,4,&flush,"flush"))return false;
  if(flush!=Z_NO_FLUSH&&flush!=Z_SYNC_FLUSH&&flush!=Z_FULL_FLUSH&&flush!=Z_FINISH)return fail(cx,"ERR_SM_NODE_UNSUPPORTED","flush");
  if(!args[1].isObject())return fail(cx,"ERR_INVALID_ARG_TYPE","feed");
  JS::RootedObject handle(cx,&args[0].toObject()),view(cx,&args[1].toObject()),backing(cx);
  size_t length=0;bool shared=false;uint8_t* ignored=nullptr;
  if(!JS_GetObjectAsUint8Array(view,&length,&shared,&ignored))return fail(cx,"ERR_INVALID_ARG_TYPE","feed");
  if(shared||JS::IsResizableArrayBufferView(view))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","backing");
  backing=JS_GetArrayBufferViewBuffer(cx,view,&shared);if(!backing)return false;
  if(shared||JS::IsDetachedArrayBufferObject(backing))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","backing");
  if(length>Staging||length>MaxInput-state->input_bytes)return fail(cx,"ERR_SM_ZLIB_STREAM_LIMIT","input");
  // All potential allocations/materialization precede the pointer borrow.
  bool changed=false;
  {JS::AutoCheckCannotGC nogc(cx);size_t current=0;uint8_t* data=nullptr;
    changed=!JS_GetObjectAsUint8Array(view,&current,&shared,&data)||shared||current!=length||JS::IsDetachedArrayBufferObject(backing)||(length&&!data);
    if(!changed&&length)std::memcpy(state->input.data(),data,length);
  }
  if(changed)return fail(cx,"ERR_SM_NODE_UNSUPPORTED","backing changed");
  state->input_bytes+=length;state->z.next_in=state->input.data();state->z.avail_in=static_cast<uInt>(length);
  state->flush=flush;state->pending=true;args.rval().setUndefined();return true;
}
bool pull(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"pull"))return false;
  if(!args.requireAtLeast(cx,"pullZlibStream",1))return false;
  auto* state=get(cx,args[0]);if(!state)return false;
  JS::RootedObject handle(cx,&args[0].toObject());
  if(!state->pending||state->ended)return fail(cx,"ERR_SM_ZLIB_STREAM_STATE","pull");
  if(state->steps==MaxSteps){retire(handle);return fail(cx,"ERR_SM_ZLIB_STREAM_LIMIT","work");}state->steps++;
  const uInt before=state->z.avail_in;
  state->z.next_out=state->output.data();state->z.avail_out=static_cast<uInt>(state->chunk);
  int status=deflate(&state->z,state->flush);
  const size_t count=state->chunk-state->z.avail_out;
  if(status!=Z_OK&&status!=Z_STREAM_END&&status!=Z_BUF_ERROR){retire(handle);if(status==Z_MEM_ERROR){JS_ReportOutOfMemory(cx);return false;}return fail(cx,"ERR_SM_ZLIB_STREAM_CODEC","deflate");}
  if(count>MaxOutput-state->output_bytes){retire(handle);return fail(cx,"ERR_SM_ZLIB_STREAM_LIMIT","output");}
  if(!count&&state->z.avail_in==before&&before){retire(handle);return fail(cx,"ERR_SM_ZLIB_STREAM_PROGRESS","deflate");}
  const bool ended=status==Z_STREAM_END;
  const bool done=ended||(state->flush!=Z_FINISH&&state->z.avail_in==0&&state->z.avail_out!=0);
  if(state->flush==Z_FINISH&&!ended&&!count&&state->z.avail_in==before){retire(handle);return fail(cx,"ERR_SM_ZLIB_STREAM_PROGRESS","finish");}
  state->output_bytes+=count;state->pending=!done;state->ended=ended;
  JS::RootedObject output(cx,JS_NewUint8Array(cx,count));if(!output){retire(handle);return false;}
  if(count){JS::AutoCheckCannotGC nogc(cx);bool shared=false;auto* target=JS_GetUint8ArrayData(output,&shared,nogc);MOZ_ASSERT(!shared);std::memcpy(target,state->output.data(),count);}
  JS::RootedObject record(cx,JS_NewPlainObject(cx));if(!record){retire(handle);return false;}
  JS::RootedValue bytes(cx,JS::ObjectValue(*output)),done_value(cx,JS::BooleanValue(done)),ended_value(cx,JS::BooleanValue(ended));
  if(!JS_DefineProperty(cx,record,"bytes",bytes,JSPROP_ENUMERATE)||!JS_DefineProperty(cx,record,"actionDone",done_value,JSPROP_ENUMERATE)||!JS_DefineProperty(cx,record,"ended",ended_value,JSPROP_ENUMERATE)){retire(handle);return false;}
  if(ended)state->end(); // codec release once; private handle remains idempotently closable.
  args.rval().setObject(*record);return true;
}
bool close(JSContext* cx,unsigned argc,JS::Value* vp){
  // Release also works after abort; no new context/IO is acquired.
  auto args=JS::CallArgsFromVp(argc,vp);
  if(!args.requireAtLeast(cx,"closeZlibStream",1)||!args[0].isObject()||JS::GetClass(&args[0].toObject())!=&Class)return fail(cx,"ERR_SM_ZLIB_STREAM_STATE","close");
  JS::RootedObject handle(cx,&args[0].toObject());retire(handle);args.rval().setUndefined();return true;
}
} // anonymous
JSObject* create_stream_kernel(JSContext* cx){
  JS::RootedObject result(cx,JS_NewPlainObject(cx));if(!result)return nullptr;
  static const JSFunctionSpec functions[]={JS_FN("checkPhase",phase,0,0),JS_FN("open",open,6,0),JS_FN("feed",feed,3,0),JS_FN("pull",pull,1,0),JS_FN("close",close,1,0),JS_FS_END};
  if(!JS_DefineFunctions(cx,result,functions))return nullptr;return result;
}
} // namespace builtins::node_compat::zlib_profile
