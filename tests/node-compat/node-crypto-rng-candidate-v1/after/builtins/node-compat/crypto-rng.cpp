// UNCOMPILED guest RNG provider. No provider object or entropy at install/INIT.
#include "builtin.h"
#include "host_api.h"
#include "node-compat-entropy.h"
#include "../web/crypto/uuid.h"
#include "js/ArrayBuffer.h"
#include "js/experimental/TypedData.h"
#include <cmath>
#include <cstring>
#ifndef NODE_COMPAT_ENTROPY_RUNTIME_ONLY
#error NODE_COMPAT_CRYPTO_RANDOM requires genuine RUNTIME_ONLY entropy
#endif
namespace builtins::node_compat {
namespace {
constexpr size_t MaxRandomBytes=16*1024*1024;
DEF_ERR(RandomType,JSEXN_TYPEERR,"Invalid native RNG argument",0)
DEF_ERR(RandomRange,JSEXN_RANGEERR,"Native RNG range exceeds bounded input",0)
DEF_ERR(RandomState,JSEXN_ERR,"Native RNG operation unavailable in this state",0)
bool failure(JSContext* cx,JSExnType kind,const char* code,const char* message){
 (void)message;api::throw_error(cx,kind==JSEXN_TYPEERR?RandomType:kind==JSEXN_RANGEERR?RandomRange:RandomState);
 JS::RootedValue exception(cx);if(!JS_GetPendingException(cx,&exception)||!exception.isObject())return false;
 JS_ClearPendingException(cx);JS::RootedObject error(cx,&exception.toObject());JS::RootedString cs(cx,JS_NewStringCopyZ(cx,code));if(!cs)return false;
 JS::RootedValue cv(cx,JS::StringValue(cs));if(!JS_DefineProperty(cx,error,"code",cv,JSPROP_ENUMERATE))return false;JS_SetPendingException(cx,exception);return false;
}
bool deployed(JSContext* cx,const char* op){
 auto* engine=api::Engine::get(cx);
 if(!engine||engine->state()!=api::EngineState::Initialized||!entropy::deployed_execution_started())return failure(cx,JSEXN_ERR,"ERR_SM_ENTROPY_INITIALIZATION","node crypto RNG requires deployed execution");
 return entropy::require(cx,op);
}
bool check(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"node:crypto.random"))return false;a.rval().setUndefined();return true;}
bool integer(JSContext* cx,JS::HandleValue value,size_t max,size_t* n){if(!value.isNumber())return failure(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","random range must be a number");double v=value.toNumber();if(!std::isfinite(v)||v<0||v>max||std::floor(v)!=v)return failure(cx,JSEXN_RANGEERR,"ERR_OUT_OF_RANGE","random range outside bounded buffer");*n=static_cast<size_t>(v);return true;}
bool fill_view(JSContext* cx,JS::HandleObject view,size_t offset,size_t size){
 // This standard host random boundary is the same genuine primitive used by
 // native WebCrypto. Acquire no JS data pointer until AFTER the host call.
 if(!size)return true;
 auto result=host_api::Random::get_bytes(size);if(const auto* error=result.to_err()){HANDLE_ERROR(cx,*error);return false;}
 auto bytes=std::move(result.unwrap());
 struct Wipe {uint8_t* p;size_t n;~Wipe(){if(p)entropy::clear(p,n);}} wipe{bytes.begin(),bytes.size()};
 if(bytes.size()!=size||!bytes.begin())return entropy::invalid_result(cx,"node:crypto.random");
 bool unchanged=false;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;auto* target=JS_GetUint8ArrayData(view,&shared,nogc);unchanged=!shared&&JS_GetTypedArrayByteLength(view)>=offset+size;if(unchanged)std::memcpy(target+offset,bytes.begin(),size);}
 if(!unchanged)return failure(cx,JSEXN_ERR,"ERR_SM_NODE_UNSUPPORTED","random target backing changed");
 return true;
}
bool random_bytes(JSContext* cx,unsigned argc,JS::Value* vp){
 auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"node:crypto.randomBytes"))return false;size_t n=0;if(a.length()<1)return failure(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","size is required");if(!integer(cx,a[0],MaxRandomBytes,&n))return false;
 JS::RootedObject view(cx,JS_NewUint8Array(cx,n));if(!view||!fill_view(cx,view,0,n))return false;a.rval().setObject(*view);return true;
}
bool random_fill(JSContext* cx,unsigned argc,JS::Value* vp){
 auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"node:crypto.randomFillSync"))return false;if(a.length()<3||!a[0].isObject())return failure(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","random target requires fixed Uint8Array");
 JS::RootedObject view(cx,&a[0].toObject());size_t length=0,offset=0,n=0;bool shared=false;uint8_t* ignored=nullptr;
 if(!JS_GetObjectAsUint8Array(view,&length,&shared,&ignored))return failure(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","random target requires Uint8Array");
 if(shared||JS::IsResizableArrayBufferView(view))return failure(cx,JSEXN_ERR,"ERR_SM_NODE_UNSUPPORTED","shared/resizable random backing refused");JS::RootedObject backing(cx,JS_GetArrayBufferViewBuffer(cx,view,&shared));if(!backing)return false;
 if(shared||JS::IsDetachedArrayBufferObject(backing))return failure(cx,JSEXN_ERR,"ERR_SM_NODE_UNSUPPORTED","detached random backing refused");
 if(length>MaxRandomBytes)return failure(cx,JSEXN_RANGEERR,"ERR_OUT_OF_RANGE","random view exceeds16MiB");if(!integer(cx,a[1],length,&offset)||!integer(cx,a[2],length-offset,&n)||!fill_view(cx,view,offset,n))return false;a.rval().setObject(*view);return true;
}
bool random_uuid(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed(cx,"node:crypto.randomUUID"))return false;auto uuid=builtins::web::crypto::random_uuid_v4(cx,"node:crypto.randomUUID");if(!uuid)return false;JS::RootedString s(cx,JS_NewStringCopyN(cx,uuid->data(),uuid->size()));if(!s)return false;a.rval().setString(s);return true;}
const JSFunctionSpec functions[]={JS_FN("check",check,0,0),JS_FN("bytes",random_bytes,1,0),JS_FN("fill",random_fill,3,0),JS_FN("uuid",random_uuid,0,0),JS_FS_END};
}
JSObject* create_crypto_random_kernel(JSContext* cx){JS::RootedObject out(cx,JS_NewPlainObject(cx));return out&&JS_DefineFunctions(cx,out,functions)?out.get():nullptr;}
}
