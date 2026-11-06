// UNCOMPILED UTF16 CompileFunction correction on the actual V7 direct-P2 provider.
#include "builtin.h"
#include "encode.h"
#include "script_loader.h"
#include "next-fs-native.h"
#include "node-compat-entropy.h"
#include "js/CallAndConstruct.h"
#include "js/CharacterEncoding.h"
#include "js/CompilationAndEvaluation.h"
#include "js/EnvironmentChain.h"
#include "js/SourceText.h"
#include "js/String.h"
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <sys/stat.h>
#include <unistd.h>

namespace builtins::node_compat {
namespace {
constexpr size_t MaxSource=16*1024*1024,MaxPath=4096;
static bool require_io(JSContext *cx,const char *operation){
 auto *engine=api::Engine::get(cx);
 if(engine&&engine->state()==api::EngineState::Initialized&&entropy::deployed_execution_started())return true;
 JS_ReportErrorASCII(cx,"ERR_SM_NODE_MODULE_INITIALIZATION: %s requires deployed execution",operation);
 JS::RootedValue exception(cx);if(!JS_GetPendingException(cx,&exception)||!exception.isObject())return false;
 JS::RootedObject object(cx,&exception.toObject());JS::RootedString code(cx,JS_NewStringCopyZ(cx,"ERR_SM_NODE_MODULE_INITIALIZATION"));if(!code)return false;
 JS::RootedValue value(cx,JS::StringValue(code));JS_ClearPendingException(cx);
 if(!JS_DefineProperty(cx,object,"code",value,JSPROP_ENUMERATE))return false;
 JS_SetPendingException(cx,exception);return false;
}
static host_api::HostString path_arg(JSContext *cx,JS::CallArgs &args){
 if(args.length()<1||!args[0].isString()){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_TYPE: module provider path must be a string");return {};}
 auto path=core::encode(cx,args[0]);if(!path)return {};
 if(!path.len||path.len>MaxPath||path.ptr.get()[0]!='/'||std::memchr(path.ptr.get(),0,path.len)){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_VALUE: module provider needs a bounded absolute POSIX path");return {};}
 return path;
}
// Genuine direct-P2 FS provider, same cwd/preopen rights as process and fs.
static bool missing_stat(JSContext *cx) {
 JS::RootedValue exception(cx);if(!JS_GetPendingException(cx,&exception)||!exception.isObject())return false;
 JS::RootedObject object(cx,&exception.toObject());bool own=false;
 if(!JS_HasOwnProperty(cx,object,"code",&own)||!own)return false;
 JS::RootedValue code(cx);if(!JS_GetProperty(cx,object,"code",&code)||!code.isString())return false;
 bool missing=false,notdir=false;
 if(!JS_StringEqualsLiteral(cx,code.toString(),"ENOENT",&missing)||!JS_StringEqualsLiteral(cx,code.toString(),"ENOTDIR",&notdir))return false;
 if(missing||notdir){JS_ClearPendingException(cx);return true;}return false;
}
static bool kind(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.stat"))return false;auto path=path_arg(cx,args);if(!path)return false;
 next_fs::Metadata st{};if(!next_fs::stat_path(cx,path.ptr.get(),path.len,true,&st)){if(missing_stat(cx)){args.rval().setNull();return true;}return false;}
 const char *value=st.type==6?"file":st.type==3?"directory":"other";
 JS::RootedString result(cx,JS_NewStringCopyZ(cx,value));if(!result)return false;args.rval().setString(result);return true;
}
static bool read_text(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.readText"))return false;auto path=path_arg(cx,args);if(!path)return false;
 JS::UniqueChars bytes;size_t length=0;if(!next_fs::read_bytes(cx,path.ptr.get(),path.len,&bytes,&length))return false;
 if(length>MaxSource){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: module source exceeds16MiB");return false;}
 // Node fs.readFileSync(path,'utf8') replaces malformed UTF8, then the JS
 // Module core strips a BOM. Use the actual pinned JSAPI lossy decoder, with
 // separately owned malloc bytes across GC; no ArrayBuffer pointer is borrowed.
 size_t units=0;auto decoded=JS::LossyUTF8CharsToNewTwoByteCharsZ(cx,JS::UTF8Chars(bytes.get(),length),&units,js::MallocArena);
 JS::UniqueTwoByteChars owned(decoded.get());if(!owned)return false;
 JS::RootedString result(cx,JS_NewUCStringCopyN(cx,owned.get(),units));if(!result)return false;args.rval().setString(result);return true;
}
static bool real_path(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.realpath"))return false;auto path=path_arg(cx,args);if(!path)return false;
 JS::UniqueChars value;size_t length=0;if(!next_fs::realpath(cx,path.ptr.get(),path.len,&value,&length))return false;
 JS::RootedString result(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(value.get(),length)));if(!result)return false;args.rval().setString(result);return true;
}
static bool cwd(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.cwd"))return false;JS::UniqueChars path;size_t length=0;if(!next_fs::cwd(cx,&path,&length))return false;
 JS::RootedString result(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(path.get(),length)));if(!result)return false;args.rval().setString(result);return true;
}
static bool builtin(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!args.requireAtLeast(cx,"module.getBuiltin",1))return false;if(!args[0].isString()){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_TYPE: builtin ID must be a string");return false;}
 JS::RootedString id(cx,args[0].toString());JS::RootedValue value(cx);if(!ScriptLoader::lookup_registered_builtin(cx,id,&value))return false;
 if(value.isUndefined()){args.rval().setUndefined();return true;}
 if(!value.isObject()){JS_ReportErrorASCII(cx,"ERR_SM_NODE_MODULE_PROVIDER: builtin record must be an object");return false;}
 JS::RootedObject record(cx,&value.toObject());bool has=false;if(!JS_HasOwnProperty(cx,record,"default",&has))return false;
 if(has&&!JS_GetProperty(cx,record,"default",&value))return false;
 // Return the actual installed CJS default value; no namespace clone or adapter.
 args.rval().set(value);return true;
}
static bool compile(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!args.requireAtLeast(cx,"module.compile",2))return false;if(!args[0].isString()||!args[1].isString()){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_TYPE: source and filename must be strings");return false;}
 JS::RootedString source(cx,args[0].toString());
 const size_t sourceUnits=JS_GetStringLength(source);
 if(sourceUnits>MaxSource){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: source/filename limit");return false;}
 JSLinearString *linear=JS_EnsureLinearString(cx,source);if(!linear)return false;
 if(JS::GetDeflatedUTF8StringLength(linear)>MaxSource){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: source/filename limit");return false;}
 auto filename=core::encode(cx,args[1]);if(!filename)return false;
 if(!filename.len||filename.len>MaxPath||std::memchr(filename.ptr.get(),0,filename.len)){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: source/filename limit");return false;}
 // Own a UTF16 copy across compilation/GC. The pinned SM147 Utf8 overload
 // appends its char* as Latin1 inside FunctionCompiler::addFunctionBody.
 JS::UniqueTwoByteChars owned=JS_CopyStringCharsZ(cx,source);if(!owned)return false;
 JS::CompileOptions options(cx);options.setFileAndLine(filename.ptr.get(),1);
 JS::EnvironmentChain chain(cx,JS::SupportUnscopables::No);
 JS::SourceText<char16_t> text;if(!text.init(cx,owned.get(),sourceUnits,JS::SourceOwnership::Borrowed))return false;
 const char *names[]={"exports","require","module","__filename","__dirname"};
 JS::RootedFunction fn(cx,JS::CompileFunction(cx,chain,options,nullptr,5,names,text));if(!fn)return false;
 args.rval().setObject(*JS_GetFunctionObject(fn));return true;
}
const JSFunctionSpec functions[]={JS_FN("kind",kind,1,0),JS_FN("readText",read_text,1,0),JS_FN("realpath",real_path,1,0),JS_FN("cwd",cwd,0,0),JS_FN("getBuiltin",builtin,1,0),JS_FN("compile",compile,2,0),JS_FS_END};
} // namespace
JSObject *create_module_kernel(JSContext *cx){JS::RootedObject result(cx,JS_NewPlainObject(cx));if(!result||!JS_DefineFunctions(cx,result,functions))return nullptr;return result;}
} // namespace builtins::node_compat
