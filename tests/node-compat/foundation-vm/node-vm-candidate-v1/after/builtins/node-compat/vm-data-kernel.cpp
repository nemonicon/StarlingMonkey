// Uncompiled Source: real SM realm + Evaluate, bounded finite-data copy only.
#include "vm-data-kernel.h"
#include "extension-api.h"
#include "async_context_runtime.h"
#include "node_tick_queue.h"
#include "node-compat-entropy.h" // Genuine reviewed INIT-barrier successor required.
#include "encode.h"
#include "js/Array.h"
#include "js/CompilationAndEvaluation.h"
#include "js/Exception.h"
#include "js/GlobalObject.h"
#include "js/Object.h"
#include "js/PropertyAndElement.h"
#include "js/PropertyDescriptor.h"
#include "js/Proxy.h"
#include "js/Realm.h"
#include "js/RealmOptions.h"
#include "js/SourceText.h"
#include "js/ScriptPrivate.h"
#include "jsapi.h"
#include "jsfriendapi.h"
#include <cmath>
#include <cstring>

namespace builtins::node_compat {
using namespace JS;
namespace {
constexpr size_t MaxCode=1024*1024, MaxData=16*1024*1024, MaxObjects=8192;
constexpr size_t MaxProperties=32768, MaxArray=131072, MaxDepth=48, MaxNesting=4;
size_t nesting=0;
const JSClass GlobalClass={"NodeVmDataGlobal",JSCLASS_GLOBAL_FLAGS_WITH_SLOTS(1),&JS::DefaultGlobalClassOps};
bool fail(JSContext* cx,const char* text,const char* code="ERR_SM_NODE_VM_UNSUPPORTED") {
  return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,code,text);
}
bool plain(JSContext* cx,HandleObject object,bool* array,bool* null_proto) {
  if(js::IsProxy(object)||JS_IsGlobalObject(object))return fail(cx,"VM data cannot contain proxies or globals");
  JSAutoRealm source_realm(cx,object);
  if(!JS::IsArrayObject(cx,object,array))return false;
  if(!*array&&std::strcmp(JS::GetClass(object)->name,"Object")!=0)
    return fail(cx,"VM data supports plain objects/arrays, not functions or exotic objects");
  RootedObject proto(cx);
  if(!JS_GetPrototype(cx,object,&proto))return false;
  *null_proto=!proto;
  JSObject* expected=*array?JS::GetRealmArrayPrototype(cx):JS::GetRealmObjectPrototype(cx);
  if(proto&&proto.get()!=expected)return fail(cx,"Custom data prototypes are unsupported");
  return true;
}
bool data_descriptor(JSContext* cx,HandleObject object,HandleId id,MutableHandleValue value) {
  Rooted<mozilla::Maybe<PropertyDescriptor>> desc(cx);
  if(!JS_GetOwnPropertyDescriptorById(cx,object,id,&desc))return false;
  if(desc.isNothing()||!desc->isDataDescriptor()||!desc->enumerable()||!desc->writable()||!desc->configurable())
    return fail(cx,"VM copy requires writable enumerable configurable own data properties");
  value.set(desc->value());return true;
}
bool keys(JSContext* cx,HandleObject object,MutableHandleIdVector out,bool intrinsic_global=false) {
  if(!js::GetPropertyKeys(cx,object,JSITER_OWNONLY|JSITER_HIDDEN|JSITER_SYMBOLS,out))return false;
  if(out.length()>MaxProperties)return fail(cx,"VM property limit exceeded","ERR_SM_NODE_VM_LIMIT");
  if(!intrinsic_global)for(size_t i=0;i<out.length();i++)if(out[i].isSymbol())return fail(cx,"Symbol data keys are unsupported");
  return true;
}
class Copy {
  JSContext* cx_;
  RootedObject destination_;
  RootedObjectVector sources_,copies_;
  RootedValueVector active_;
  size_t bytes_=0,properties_=0;
public:
  Copy(JSContext* cx,HandleObject destination):cx_(cx),destination_(cx,destination),sources_(cx),copies_(cx),active_(cx){}
  bool value(HandleValue input,MutableHandleValue output,size_t depth=0) {
    if(depth>MaxDepth)return fail(cx_,"VM depth limit exceeded","ERR_SM_NODE_VM_LIMIT");
    if(input.isUndefined()||input.isNull()||input.isBoolean()||input.isNumber()) {
      if(input.isNumber()&&!std::isfinite(input.toNumber()))return fail(cx_,"Nonfinite VM numbers are unsupported");
      output.set(input);return true;
    }
    if(input.isString()) {
      if(JS::GetStringLength(input.toString())>MaxData-bytes_)return fail(cx_,"VM string limit exceeded","ERR_SM_NODE_VM_LIMIT");
      RootedString string(cx_,input.toString());auto encoded=core::encode(cx_,string);
      if(!encoded)return false;
      if(encoded.len>MaxData-bytes_)return fail(cx_,"VM string/data limit exceeded","ERR_SM_NODE_VM_LIMIT");
      bytes_+=encoded.len;output.set(input);return true;
    }
    if(!input.isObject())return fail(cx_,"VM symbols/BigInts/private data are unsupported");
    RootedObject source(cx_,&input.toObject());
    for(size_t i=0;i<sources_.length();i++)if(sources_[i].get()==source.get()) {
      if(active_[i].get().toBoolean())return fail(cx_,"Cyclic VM data is unsupported");
      output.setObject(*copies_[i]);return true;
    }
    if(sources_.length()>=MaxObjects)return fail(cx_,"VM object limit exceeded","ERR_SM_NODE_VM_LIMIT");
    bool array=false,null_proto=false;uint32_t length=0;
    RootedIdVector own(cx_);
    {
      JSAutoRealm ar(cx_,source);
      if(!plain(cx_,source,&array,&null_proto)||!keys(cx_,source,&own))return false;
      if(array&&(!JS::GetArrayLength(cx_,source,&length)||length>MaxArray))return fail(cx_,"VM array limit exceeded","ERR_SM_NODE_VM_LIMIT");
      if(array) {
        Rooted<mozilla::Maybe<PropertyDescriptor>> desc(cx_);
        if(!JS_GetOwnPropertyDescriptor(cx_,source,"length",&desc))return false;
        if(desc.isNothing()||!desc->isDataDescriptor()||!desc->writable())return fail(cx_,"Readonly VM array length is unsupported");
      }
    }
    JSAutoRealm target(cx_,destination_);
    if(array){const size_t slots=size_t(length)*sizeof(Value);
      if(slots>MaxData-bytes_)return fail(cx_,"VM array storage limit exceeded","ERR_SM_NODE_VM_LIMIT");
      bytes_+=slots;}
    RootedObject copy(cx_,array?JS::NewArrayObject(cx_,length):
        null_proto?JS_NewObjectWithGivenProto(cx_,nullptr,nullptr):JS_NewPlainObject(cx_));
    if(!copy)return false;
    if(!sources_.append(source)||!copies_.append(copy)||!active_.append(BooleanValue(true))){JS_ReportOutOfMemory(cx_);return false;}
    const size_t slot=sources_.length()-1;
    for(size_t i=0;i<own.length();i++) {
      RootedId id(cx_,own[i]);RootedValue item(cx_),converted(cx_);
      if(array&&id.isString()) {
        RootedString key(cx_,id.toString());auto encoded=core::encode(cx_,key);if(!encoded)return false;
        if(encoded.len==6&&std::memcmp(encoded.ptr.get(),"length",6)==0)continue;
      }
      if(id.isString()) {
        RootedString key(cx_,id.toString());auto encoded=core::encode(cx_,key);if(!encoded)return false;
        if(encoded.len>MaxData-bytes_)return fail(cx_,"VM key/data limit exceeded","ERR_SM_NODE_VM_LIMIT");
        bytes_+=encoded.len;
      }
      if(++properties_>MaxProperties)return fail(cx_,"VM property limit exceeded","ERR_SM_NODE_VM_LIMIT");
      {
        JSAutoRealm ar(cx_,source);
        if(!data_descriptor(cx_,source,id,&item))return false;
      }
      if(!value(item,&converted,depth+1)||!JS_DefinePropertyById(cx_,copy,id,converted,JSPROP_ENUMERATE))return false;
    }
    active_[slot].setBoolean(false);output.setObject(*copy);return true;
  }
};
bool contains(HandleIdVector list,HandleId id) {
  for(size_t i=0;i<list.length();i++)if(list[i]==id)return true;
  return false;
}
bool filename(JSContext* cx,HandleValue options,MutableHandleString output) {
  if(options.isUndefined()){output.set(JS_NewStringCopyZ(cx,"<node:vm>"));return output.get()!=nullptr;}
  if(options.isString()){output.set(options.toString());return true;}
  if(!options.isObject())return fail(cx,"VM options must be a filename or plain options object","ERR_INVALID_ARG_TYPE");
  RootedObject object(cx,&options.toObject());bool array=false,null_proto=false;
  if(!plain(cx,object,&array,&null_proto)||array)return fail(cx,"VM options must be plain data");
  RootedIdVector own(cx);if(!keys(cx,object,&own))return false;
  output.set(JS_NewStringCopyZ(cx,"<node:vm>"));if(!output)return false;
  for(size_t i=0;i<own.length();i++) {
    RootedId id(cx,own[i]);RootedValue key(cx),value(cx);
    if(!JS_IdToValue(cx,id,&key))return false;
    auto encoded=core::encode(cx,key);if(!encoded)return false;
    if(encoded.len!=8||std::memcmp(encoded.ptr.get(),"filename",8)!=0)return fail(cx,"VM option is explicitly deferred");
    Rooted<mozilla::Maybe<PropertyDescriptor>> desc(cx);
    if(!JS_GetOwnPropertyDescriptorById(cx,object,id,&desc))return false;
    if(desc.isNothing()||!desc->isDataDescriptor()||!desc->value().isString())return fail(cx,"VM filename must be own string data");
    output.set(desc->value().toString());
  }
  return true;
}
bool run(JSContext* cx,unsigned argc,Value* vp) {
  auto* engine=api::Engine::get(cx);
  if(!engine||engine->state()!=api::EngineState::Initialized||!entropy::deployed_execution_started())
    return fail(cx,"runInNewContext requires deployed execution","ERR_SM_NODE_VM_INITIALIZATION");
  CallArgs args=CallArgsFromVp(argc,vp);
  if(argc!=3||!args[0].isString()||!args[1].isObject())return fail(cx,"VM source must be string and sandbox a plain object","ERR_INVALID_ARG_TYPE");
  if(nesting>=MaxNesting)return fail(cx,"VM nesting limit exceeded","ERR_SM_NODE_VM_LIMIT");
  ++nesting;struct Exit{~Exit(){--nesting;}}exit;
  RootedObject caller(cx,JS::CurrentGlobalOrNull(cx)),sandbox(cx,&args[1].toObject());
  bool array=false,null_proto=false,extensible=false;
  if(!plain(cx,sandbox,&array,&null_proto)||array)return fail(cx,"VM sandbox must be a plain object");
  if(!JS_IsExtensible(cx,sandbox,&extensible)||!extensible)return fail(cx,"VM sandbox must be extensible");
  RootedString file(cx);if(!filename(cx,args[2],&file))return false;
  if(JS::GetStringLength(args[0].toString())>MaxCode||JS::GetStringLength(file)>4096)
    return fail(cx,"VM source/filename limit exceeded","ERR_SM_NODE_VM_LIMIT");
  auto file_bytes=core::encode(cx,file),code=core::encode(cx,args[0]);
  if(!file_bytes||!code)return false;
  if(code.len>MaxCode||!file_bytes.len||file_bytes.len>4096||std::memchr(file_bytes.ptr.get(),0,file_bytes.len))
    return fail(cx,"VM source/filename limit exceeded","ERR_SM_NODE_VM_LIMIT");
  JS::RealmOptions realm_options;realm_options.creationOptions().setExistingCompartment(engine->global());
  RootedObject global(cx,JS_NewGlobalObject(cx,&GlobalClass,nullptr,JS::DontFireOnNewGlobalHook,realm_options));
  if(!global||!api::Engine::initialize_data_realm(cx,global))return false;
  RootedIdVector baseline(cx),input_keys(cx);RootedValueVector baseline_values(cx);
  RootedValue copied_input(cx),completion(cx),snapshot_value(cx),copy_error(cx);
  bool threw=false,copy_failed=false;
  bool delivered=false;
  struct PreserveThrow {
    JSContext* cx;bool& threw;bool& delivered;HandleValue value;
    ~PreserveThrow(){if(threw&&!delivered)JS_SetPendingException(cx,value,ExceptionStackBehavior::DoNotCapture);}
  } preserve{cx,threw,delivered,completion};
  {
    JSAutoRealm ar(cx,global);
    if(!keys(cx,global,&baseline,true))return false;
    for(size_t i=0;i<baseline.length();i++) {
      RootedId id(cx,baseline[i]);Rooted<mozilla::Maybe<PropertyDescriptor>> desc(cx);
      if(!JS_GetOwnPropertyDescriptorById(cx,global,id,&desc))return false;
      if(desc.isNothing()||!desc->isDataDescriptor())return fail(cx,"Unmatched native global descriptor");
      if(!baseline_values.append(desc->value())){JS_ReportOutOfMemory(cx);return false;}
    }
    Copy incoming(cx,global);RootedValue original(cx,ObjectValue(*sandbox));
    if(!incoming.value(original,&copied_input))return false;
    RootedObject input(cx,&copied_input.toObject());
    if(!keys(cx,input,&input_keys))return false;
    for(size_t i=0;i<input_keys.length();i++) {
      RootedId id(cx,input_keys[i]);RootedValue value(cx);
      if(!data_descriptor(cx,input,id,&value)||!JS_DefinePropertyById(cx,global,id,value,JSPROP_ENUMERATE))return false;
    }
    JS::CompileOptions options(cx);options.setFileAndLine(file_bytes.ptr.get(),1);
    JS::SourceText<mozilla::Utf8Unit> source;
    if(!source.init(cx,code.ptr.get(),code.len,JS::SourceOwnership::Borrowed))return false;
    RootedScript script(cx,JS::Compile(cx,options,source));
    if(script)JS::SetScriptPrivate(script,ObjectValue(*global));
    if(!script||!JS_ExecuteScript(cx,script,&completion)) {
      if(!JS_IsExceptionPending(cx))return false; // Preserve uncatchable termination.
      if(!JS_GetPendingException(cx,&completion))return false;
      JS_ClearPendingException(cx);threw=true;
    }
    if(core::async_context::data_realm_async_attempted(global)&&!threw) {
      fail(cx,"VM Promise/async creation or job is explicitly unsupported","ERR_SM_NODE_VM_ASYNC");
      if(!JS_GetPendingException(cx,&completion))return false;
      JS_ClearPendingException(cx);threw=true;
    }
    RootedObject snapshot(cx,JS_NewPlainObject(cx));RootedIdVector final_keys(cx);
    if(!snapshot||!keys(cx,global,&final_keys,true))return false;
    for(size_t i=0;i<final_keys.length();i++) {
      RootedId id(cx,final_keys[i]);
      if(contains(baseline,id)&&!contains(input_keys,id)) {
        Rooted<mozilla::Maybe<PropertyDescriptor>> desc(cx);
        if(!JS_GetOwnPropertyDescriptorById(cx,global,id,&desc))return false;
        bool unchanged=false;
        if(desc.isSome()&&desc->isDataDescriptor())for(size_t j=0;j<baseline.length();j++)
          if(baseline[j]==id&&desc->value()==baseline_values[j].get())unchanged=true;
        if(unchanged)continue;
        fail(cx,"Overwriting intrinsic global bindings is outside VM data profile");
        if(!JS_GetPendingException(cx,&copy_error))return false;
        JS_ClearPendingException(cx);copy_failed=true;break;
      }
      RootedValue value(cx);
      if(!data_descriptor(cx,global,id,&value)||!JS_DefinePropertyById(cx,snapshot,id,value,JSPROP_ENUMERATE)) {
        if(!JS_IsExceptionPending(cx)||!JS_GetPendingException(cx,&copy_error))return false;
        JS_ClearPendingException(cx);copy_failed=true;break;
      }
    }
    snapshot_value.setObject(*snapshot);
  }
  RootedValue context(cx),result(cx);
  Copy outgoing(cx,caller);
  if(!copy_failed&&(!outgoing.value(snapshot_value,&context)||(!threw&&!outgoing.value(completion,&result)))) {
    if(!JS_IsExceptionPending(cx)||!JS_GetPendingException(cx,&copy_error))return false;
    JS_ClearPendingException(cx);copy_failed=true;context.setUndefined();
  }
  if(threw)result.set(completion); // Original object/primitive identity, no coercion.
  RootedObject envelope(cx,JS_NewPlainObject(cx));
  if(!envelope||!JS_DefineProperty(cx,envelope,"threw",threw,JSPROP_ENUMERATE)||
     !JS_DefineProperty(cx,envelope,"value",result,JSPROP_ENUMERATE)||
     !JS_DefineProperty(cx,envelope,"context",context,JSPROP_ENUMERATE)||
     !JS_DefineProperty(cx,envelope,"copyOutFailed",copy_failed,JSPROP_ENUMERATE)||
     !JS_DefineProperty(cx,envelope,"copyOutError",copy_error,JSPROP_ENUMERATE))return false;
  args.rval().setObject(*envelope);delivered=true;return true;
}
const JSFunctionSpec functions[]={JS_FN("run",run,3,0),JS_FS_END};
} // namespace
JSObject* create_vm_data_kernel(JSContext* cx) {
  RootedObject object(cx,JS_NewPlainObject(cx));
  return object&&JS_DefineFunctions(cx,object,functions)?object.get():nullptr;
}
} // namespace builtins::node_compat
