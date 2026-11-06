// UNCOMPILED private guest provider. No host service or stored FILE/native JS edge.
#include "builtin.h"
#include "encode.h"
#include "script_loader.h"
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
struct CloseFile {void operator()(FILE *f)const{if(f)fclose(f);}};
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
static bool failure(JSContext *cx,const char *operation){JS_ReportErrorUTF8(cx,"ERR_SM_NODE_MODULE_IO: %s: %s",operation,std::strerror(errno));return false;}
static host_api::HostString path_arg(JSContext *cx,JS::CallArgs &args){
 if(args.length()<1||!args[0].isString()){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_TYPE: module provider path must be a string");return {};}
 auto path=core::encode(cx,args[0]);if(!path)return {};
 if(!path.len||path.len>MaxPath||path.ptr.get()[0]!='/'||std::memchr(path.ptr.get(),0,path.len)){JS_ReportErrorASCII(cx,"ERR_INVALID_ARG_VALUE: module provider needs a bounded absolute POSIX path");return {};}
 return path;
}
static bool kind(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.stat"))return false;auto path=path_arg(cx,args);if(!path)return false;struct stat st{};
 if(stat(path.ptr.get(),&st)!=0){if(errno==ENOENT||errno==ENOTDIR){args.rval().setNull();return true;}return failure(cx,"stat");}
 const char *value=S_ISREG(st.st_mode)?"file":S_ISDIR(st.st_mode)?"directory":"other";
 JS::RootedString result(cx,JS_NewStringCopyZ(cx,value));if(!result)return false;args.rval().setString(result);return true;
}
static bool read_text(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.readText"))return false;auto path=path_arg(cx,args);if(!path)return false;
 std::unique_ptr<FILE,CloseFile> file(fopen(path.ptr.get(),"rb"));if(!file)return failure(cx,"open module");
 struct stat st{};if(fstat(fileno(file.get()),&st)!=0)return failure(cx,"fstat module");
 if(!S_ISREG(st.st_mode)||st.st_size<0||static_cast<uint64_t>(st.st_size)>MaxSource){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: module must be a regular file of at most16MiB");return false;}
 size_t length=static_cast<size_t>(st.st_size);std::unique_ptr<char[]> bytes(new(std::nothrow)char[length?length:1]);if(!bytes){JS_ReportOutOfMemory(cx);return false;}
 if(fread(bytes.get(),1,length,file.get())!=length||ferror(file.get()))return failure(cx,"read module");
 // A changed/growing source cannot silently become a truncated accepted module.
 if(fgetc(file.get())!=EOF||ferror(file.get())){JS_ReportErrorASCII(cx,"ERR_SM_NODE_MODULE_IO: source changed during read");return false;}
 if(fclose(file.release())!=0)return failure(cx,"close module");
 JS::RootedString result(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(bytes.get(),length)));if(!result)return false;args.rval().setString(result);return true;
}
static bool real_path(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.realpath"))return false;auto path=path_arg(cx,args);if(!path)return false;
 std::unique_ptr<char,decltype(&std::free)> value(::realpath(path.ptr.get(),nullptr),&std::free);if(!value)return failure(cx,"realpath module");
 if(std::strlen(value.get())>MaxPath){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: canonical path too long");return false;}
 JS::RootedString result(cx,JS_NewStringCopyZ(cx,value.get()));if(!result)return false;args.rval().setString(result);return true;
}
static bool cwd(JSContext *cx,unsigned argc,JS::Value *vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_io(cx,"module.cwd"))return false;char path[MaxPath+1];if(!getcwd(path,sizeof(path)))return failure(cx,"getcwd");
 JS::RootedString result(cx,JS_NewStringCopyZ(cx,path));if(!result)return false;args.rval().setString(result);return true;
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
 auto source=core::encode(cx,args[0]),filename=core::encode(cx,args[1]);if(!source||!filename)return false;
 if(source.len>MaxSource||!filename.len||filename.len>MaxPath||std::memchr(filename.ptr.get(),0,filename.len)){JS_ReportErrorASCII(cx,"ERR_SM_NODE_LIMIT: source/filename limit");return false;}
 JS::CompileOptions options(cx);options.setFileAndLine(filename.ptr.get(),1);
 JS::EnvironmentChain chain(cx,JS::SupportUnscopables::No);
 JS::SourceText<mozilla::Utf8Unit> text;if(!text.init(cx,source.ptr.get(),source.len,JS::SourceOwnership::Borrowed))return false;
 const char *names[]={"exports","require","module","__filename","__dirname"};
 JS::RootedFunction fn(cx,JS::CompileFunction(cx,chain,options,nullptr,5,names,text));if(!fn)return false;
 args.rval().setObject(*JS_GetFunctionObject(fn));return true;
}
const JSFunctionSpec functions[]={JS_FN("kind",kind,1,0),JS_FN("readText",read_text,1,0),JS_FN("realpath",real_path,1,0),JS_FN("cwd",cwd,0,0),JS_FN("getBuiltin",builtin,1,0),JS_FN("compile",compile,2,0),JS_FS_END};
} // namespace
JSObject *create_module_kernel(JSContext *cx){JS::RootedObject result(cx,JS_NewPlainObject(cx));if(!result||!JS_DefineFunctions(cx,result,functions))return nullptr;return result;}
} // namespace builtins::node_compat
