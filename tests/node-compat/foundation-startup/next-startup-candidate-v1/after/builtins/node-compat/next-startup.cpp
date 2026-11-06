// UNCOMPILED native guest startup provider. Standard WASI only; no host service.
#include "builtin.h"
#include "encode.h"
#include "event_loop.h"
#include "node-compat-entropy.h"
#include "next-fs-native.h"
#include "script_loader.h"
#include "host-apis/wasi-0.2.10/bindings/bindings.h"
#include "js/Array.h"
#include "js/ArrayBuffer.h"
#include "js/BigInt.h"
#include "js/CharacterEncoding.h"
#include "js/MemoryFunctions.h"
#include "js/experimental/TypedData.h"
#include "js/String.h"
#include <algorithm>
#include <cerrno>
#include <utility>
#include <cstring>
#include <memory>

namespace builtins::node_compat {
namespace {
constexpr size_t MaxInitialEntries=4096,MaxInitialBytes=1024*1024,MaxWriteBytes=4*1024*1024;
bool fail(JSContext* cx,const char* code,const char* text,JSExnType kind=JSEXN_ERR){return core::InternalTickQueue::fail(cx,kind,code,text);}
bool deployed(JSContext* cx){auto* e=api::Engine::get(cx);if(e&&e->state()==api::EngineState::Initialized&&entropy::deployed_execution_started())return true;return fail(cx,"ERR_SM_NODE_STARTUP_INITIALIZATION","startup environment/FS/clock/stdio requires deployed execution");}
bool check(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;a.rval().setUndefined();return true;}
bool put(JSContext* cx,JS::HandleObject o,const char* name,JS::HandleValue v){return JS_DefineProperty(cx,o,name,v,JSPROP_ENUMERATE);}
bool text(JSContext* cx,const bindings_string_t& s,JS::MutableHandleValue v){JS::RootedString x(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(s.ptr?reinterpret_cast<const char*>(s.ptr):"",s.len)));if(!x)return false;v.setString(x);return true;}
struct Environment {bindings_list_tuple2_string_string_t v{};~Environment(){bindings_list_tuple2_string_string_free(&v);}};
struct Arguments {bindings_list_string_t v{};~Arguments(){bindings_list_string_free(&v);}};
bool initial(JSContext* cx,unsigned argc,JS::Value* vp){
 auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;
 // No calls, cached preopens, stream descriptors or native handles at install/INIT.
 Environment env;wasi_cli_environment_get_environment(&env.v);
 if(env.v.len>MaxInitialEntries)return fail(cx,"ERR_SM_NODE_LIMIT","environment count exceeds4096",JSEXN_RANGEERR);
 size_t total=0;for(size_t i=0;i<env.v.len;i++){auto& p=env.v.ptr[i];if(!p.f0.len||p.f0.len>MaxInitialBytes||p.f1.len>MaxInitialBytes||std::memchr(p.f0.ptr,0,p.f0.len)||std::memchr(p.f0.ptr,'=',p.f0.len)||(p.f1.len&&std::memchr(p.f1.ptr,0,p.f1.len)))return fail(cx,"ERR_SM_NODE_STARTUP_INPUT","invalid bounded CLI environment");if(p.f0.len>MaxInitialBytes-total)return fail(cx,"ERR_SM_NODE_LIMIT","environment byte budget exceeded",JSEXN_RANGEERR);total+=p.f0.len;if(p.f1.len>MaxInitialBytes-total)return fail(cx,"ERR_SM_NODE_LIMIT","environment byte budget exceeded",JSEXN_RANGEERR);total+=p.f1.len;}
 Arguments args;wasi_cli_environment_get_arguments(&args.v);
 if(args.v.len>MaxInitialEntries)return fail(cx,"ERR_SM_NODE_LIMIT","argument count exceeds4096",JSEXN_RANGEERR);
 total=0;for(size_t i=0;i<args.v.len;i++){auto& p=args.v.ptr[i];if(p.len>MaxInitialBytes-total||(p.len&&std::memchr(p.ptr,0,p.len)))return fail(cx,"ERR_SM_NODE_LIMIT","argument byte budget exceeded",JSEXN_RANGEERR);total+=p.len;}
 JS::RootedObject e(cx,JS::NewArrayObject(cx,env.v.len)),av(cx,JS::NewArrayObject(cx,args.v.len)),result(cx,JS_NewPlainObject(cx));if(!e||!av||!result)return false;
 JS::RootedValue value(cx),v0(cx),v1(cx);JS::RootedObject pair(cx);
 for(size_t i=0;i<env.v.len;i++){if(!text(cx,env.v.ptr[i].f0,&v0)||!text(cx,env.v.ptr[i].f1,&v1))return false;pair=JS::NewArrayObject(cx,2);if(!pair||!JS_SetElement(cx,pair,0,v0)||!JS_SetElement(cx,pair,1,v1))return false;value.setObject(*pair);if(!JS_SetElement(cx,e,i,value))return false;}
 for(size_t i=0;i<args.v.len;i++){if(!text(cx,args.v.ptr[i],&value)||!JS_SetElement(cx,av,i,value))return false;}
 value.setObject(*e);if(!put(cx,result,"environment",value))return false;value.setObject(*av);if(!put(cx,result,"arguments",value))return false;a.rval().setObject(*result);return true;
}
bool cwd(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;JS::UniqueChars bytes;size_t n=0;if(!next_fs::cwd(cx,&bytes,&n))return false;JS::RootedString s(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(bytes.get(),n)));if(!s)return false;a.rval().setString(s);return true;}
bool chdir(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;if(a.length()<1||!a[0].isString())return fail(cx,"ERR_INVALID_ARG_TYPE","chdir path must be a string",JSEXN_TYPEERR);if(JS::GetStringLength(a[0].toString())>next_fs::MaxPathBytes)return fail(cx,"ERR_SM_NODE_FS_LIMIT","chdir path budget exceeded",JSEXN_RANGEERR);auto path=core::encode(cx,a[0]);if(!path)return false;if(!next_fs::chdir(cx,path.ptr.get(),path.len))return false;a.rval().setUndefined();return true;}
bool monotonic(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;const uint64_t value=wasi_clocks_monotonic_clock_now();JS::Rooted<JS::BigInt*> n(cx,JS::NumberToBigInt(cx,value));if(!n)return false;a.rval().setBigInt(n);return true;}
struct Stream {wasi_io_streams_own_output_stream_t value;~Stream(){wasi_io_streams_output_stream_drop_own(value);}};
bool write(JSContext* cx,unsigned argc,JS::Value* vp){
 auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx))return false;
 if(a.length()<2||!a[0].isInt32()||(a[0].toInt32()!=1&&a[0].toInt32()!=2))return fail(cx,"ERR_INVALID_ARG_TYPE","stdio needs logical stream1or2",JSEXN_TYPEERR);
 JS::UniqueChars bytes;size_t n=0;
 if(a[1].isString()){if(JS::GetStringLength(a[1].toString())>MaxWriteBytes/4)return fail(cx,"ERR_SM_NODE_LIMIT","stdio string budget exceeded",JSEXN_RANGEERR);auto encoded=core::encode(cx,a[1]);if(!encoded)return false;n=encoded.len;bytes=std::move(encoded.ptr);}
 else {
  if(!a[1].isObject())return fail(cx,"ERR_INVALID_ARG_TYPE","stdio needs string or Uint8Array",JSEXN_TYPEERR);
  JS::RootedObject view(cx,&a[1].toObject());bool shared=false;uint8_t* ignored=nullptr;
  if(!JS_GetObjectAsUint8Array(view,&n,&shared,&ignored))return fail(cx,"ERR_INVALID_ARG_TYPE","stdio needs Uint8Array",JSEXN_TYPEERR);
  if(shared||JS::IsResizableArrayBufferView(view))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","shared/resizable stdio backing refused");
  JS::RootedObject backing(cx,JS_GetArrayBufferViewBuffer(cx,view,&shared));if(!backing)return false;
  if(shared||JS::IsDetachedArrayBufferObject(backing))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","detached stdio backing refused");
  if(n>MaxWriteBytes)return fail(cx,"ERR_SM_NODE_LIMIT","stdio write budget exceeded",JSEXN_RANGEERR);
  bytes=JS::UniqueChars(static_cast<char*>(JS_malloc(cx,n?n:1)));if(!bytes){JS_ReportOutOfMemory(cx);return false;}
  // Never retain a borrowed GC backing pointer across allocation/host calls.
  bool unchanged=false;{JS::AutoCheckCannotGC nogc(cx);const auto* p=JS_GetUint8ArrayData(view,&shared,nogc);unchanged=!shared&&JS_GetArrayBufferViewByteLength(view)==n;if(unchanged&&n)std::memcpy(bytes.get(),p,n);}
  if(!unchanged)return fail(cx,"ERR_SM_NODE_UNSUPPORTED","stdio backing changed");
 }
 if(n>MaxWriteBytes)return fail(cx,"ERR_SM_NODE_LIMIT","stdio byte budget exceeded",JSEXN_RANGEERR);
 Stream stream{a[0].toInt32()==1?wasi_cli_stdout_get_stdout():wasi_cli_stderr_get_stderr()};
 // WASI blocking-write-and-flush takes at most4096 bytes per call. Resources
 // are acquired after copying input and dropped on every C++ return path.
 for(size_t at=0;at<n;){size_t amount=std::min<size_t>(4096,n-at);bindings_list_u8_t chunk{reinterpret_cast<uint8_t*>(bytes.get()+at),amount};wasi_io_streams_stream_error_t err{};if(!wasi_io_streams_method_output_stream_blocking_write_and_flush(wasi_io_streams_borrow_output_stream(stream.value),&chunk,&err)){wasi_io_streams_stream_error_free(&err);return fail(cx,"ERR_SM_NODE_STDIO_WRITE","standard output stream write failed");}at+=amount;}
 a.rval().setUndefined();return true;
}
bool get_builtin(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<1||!a[0].isString())return fail(cx,"ERR_INVALID_ARG_TYPE","builtin id must be string",JSEXN_TYPEERR);JS::RootedString id(cx,a[0].toString());JS::RootedValue v(cx);if(!ScriptLoader::lookup_registered_builtin(cx,id,&v))return false;if(v.isObject()){JS::RootedObject record(cx,&v.toObject());bool has=false;if(!JS_HasOwnProperty(cx,record,"default",&has))return false;if(has&&!JS_GetProperty(cx,record,"default",&v))return false;}a.rval().set(v);return true;}
const JSFunctionSpec functions[]={JS_FN("checkDeployed",check,0,0),JS_FN("initial",initial,0,0),JS_FN("cwd",cwd,0,0),JS_FN("chdir",chdir,1,0),JS_FN("monotonic",monotonic,0,0),JS_FN("write",write,2,0),JS_FN("getBuiltin",get_builtin,1,0),JS_FS_END};
}
JSObject* create_next_startup_kernel(JSContext* cx){
 JS::RootedObject out(cx,JS_NewPlainObject(cx)),constants(cx,JS_NewPlainObject(cx)),numbers(cx,JS_NewPlainObject(cx));if(!out||!constants||!numbers||!JS_DefineFunctions(cx,out,functions))return nullptr;
 // Numeric errno constants come from THIS guest compiler's errno.h, never
 // Darwin/Linux Node observations or raw WASI enum values relabeled libuv.
 #define ERRNO(n) if(!JS_DefineProperty(cx,numbers,#n,static_cast<int32_t>(n),JSPROP_ENUMERATE))return nullptr;
 ERRNO(EACCES) ERRNO(EAGAIN) ERRNO(EBADF) ERRNO(EEXIST) ERRNO(EINVAL) ERRNO(EIO) ERRNO(EISDIR) ERRNO(ENOENT) ERRNO(ENOSPC) ERRNO(ENOTDIR) ERRNO(ENOTEMPTY) ERRNO(ENOTSUP) ERRNO(EPERM) ERRNO(EPIPE) ERRNO(EROFS)
 #undef ERRNO
 JS::RootedValue v(cx,JS::ObjectValue(*numbers));if(!put(cx,constants,"errno",v))return nullptr;v.setObject(*constants);if(!put(cx,out,"errnoConstants",v))return nullptr;return out;
}
} // namespace builtins::node_compat
