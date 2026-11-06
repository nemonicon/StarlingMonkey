// UNCOMPILED private Node FS provider. Standard WASI0.2.10 resources only.
#include "builtin.h"
#include "extension-api.h"
#include "node-compat-entropy.h"
#include "next-fs-native.h"
#include "host-apis/wasi-0.2.10/bindings/bindings.h"
#include "js/Array.h"
#include "js/ArrayBuffer.h"
#include "js/CharacterEncoding.h"
#include "js/MemoryFunctions.h"
#include "js/String.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <memory>
#include <new>
#include <string_view>

namespace builtins::node_compat::next_fs {
namespace {
using View = std::string_view;
using Borrow = wasi_filesystem_types_borrow_descriptor_t;
using Own = wasi_filesystem_types_own_descriptor_t;
using Error = wasi_filesystem_types_error_code_t;
constexpr size_t ChunkBytes = 64 * 1024;
constexpr size_t MaxPreopens = 64;
constexpr uint8_t Follow = WASI_FILESYSTEM_TYPES_PATH_FLAGS_SYMLINK_FOLLOW;
constexpr uint8_t Read = WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_READ;
constexpr uint8_t Write = WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_WRITE;
constexpr uint8_t Directory = WASI_FILESYSTEM_TYPES_OPEN_FLAGS_DIRECTORY;
// Initialized without IO. Can change only after deployed-entry authorization.
char selected_cwd[MaxPathBytes+1]{};
size_t selected_cwd_length=0;

DEF_ERR(FsInitialization, JSEXN_TYPEERR, "ERR_SM_NODE_FS_INITIALIZATION: deployed filesystem access required", 0)
DEF_ERR(FsFailure, JSEXN_ERR, "Filesystem operation failed: {0}", 1)
DEF_ERR(FsLimit, JSEXN_RANGEERR, "Bounded filesystem limit exceeded: {0}", 1)

bool property(JSContext* cx, JS::HandleObject object, const char* name, View text) {
  JS::RootedString s(cx, JS_NewStringCopyUTF8N(cx, JS::UTF8Chars(text.data(), text.size())));
  if (!s) return false;
  JS::RootedValue value(cx, JS::StringValue(s));
  return JS_DefineProperty(cx, object, name, value, JSPROP_ENUMERATE);
}
bool number(JSContext* cx, JS::HandleObject object, const char* name, double n) {
  JS::RootedValue value(cx, JS::DoubleValue(n));
  return JS_DefineProperty(cx, object, name, value, JSPROP_ENUMERATE);
}
bool boolean(JSContext* cx, JS::HandleObject object, const char* name, bool b) {
  JS::RootedValue value(cx, JS::BooleanValue(b));
  return JS_DefineProperty(cx, object, name, value, JSPROP_ENUMERATE);
}
bool decorate(JSContext* cx, const char* code, const char* operation, View path={}, View dest={}, int raw=-1) {
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception) || !exception.isObject()) return false;
  JS::RootedObject object(cx, &exception.toObject());
  JS_ClearPendingException(cx);
  if (!property(cx, object, "code", code) || !property(cx, object, "syscall", operation) ||
      !property(cx, object, "module", "node:fs") || !property(cx, object, "operation", operation)) return false;
  if (!path.empty() && !property(cx, object, "path", path)) return false;
  if (!dest.empty() && !property(cx, object, "dest", dest)) return false;
  // Raw Component Model enum, NOT a fabricated negative libuv/OS errno.
  if (raw >= 0 && !number(cx, object, "wasiError", raw)) return false;
  JS_SetPendingException(cx, exception);
  return false;
}
bool fail(JSContext* cx, const char* code, const char* operation, View path={}, View dest={}) {
  api::throw_error(cx, FsFailure, operation);
  return decorate(cx, code, operation, path, dest);
}
bool limit(JSContext* cx, const char* operation, View path={}) {
  api::throw_error(cx, FsLimit, operation);
  return decorate(cx, "ERR_SM_NODE_FS_LIMIT", operation, path);
}
const char* errno_code(Error e) {
  switch (e) {
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_ACCESS: return "EACCES";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_WOULD_BLOCK: return "EAGAIN";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_ALREADY: return "EALREADY";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_BAD_DESCRIPTOR: return "EBADF";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_BUSY: return "EBUSY";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_DEADLOCK: return "EDEADLK";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_QUOTA: return "EDQUOT";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_EXIST: return "EEXIST";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_FILE_TOO_LARGE: return "EFBIG";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_ILLEGAL_BYTE_SEQUENCE: return "EILSEQ";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_IN_PROGRESS: return "EINPROGRESS";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_INTERRUPTED: return "EINTR";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_INVALID: return "EINVAL";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_IS_DIRECTORY: return "EISDIR";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_LOOP: return "ELOOP";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_TOO_MANY_LINKS: return "EMLINK";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_MESSAGE_SIZE: return "EMSGSIZE";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NAME_TOO_LONG: return "ENAMETOOLONG";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NO_DEVICE: return "ENODEV";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NO_ENTRY: return "ENOENT";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NO_LOCK: return "ENOLCK";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_INSUFFICIENT_MEMORY: return "ENOMEM";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_INSUFFICIENT_SPACE: return "ENOSPC";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NOT_DIRECTORY: return "ENOTDIR";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NOT_EMPTY: return "ENOTEMPTY";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NOT_RECOVERABLE: return "ENOTRECOVERABLE";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_UNSUPPORTED: return "ENOTSUP";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NO_TTY: return "ENOTTY";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NO_SUCH_DEVICE: return "ENXIO";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_OVERFLOW: return "EOVERFLOW";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_NOT_PERMITTED: return "EPERM";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_PIPE: return "EPIPE";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_READ_ONLY: return "EROFS";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_INVALID_SEEK: return "ESPIPE";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_TEXT_FILE_BUSY: return "ETXTBSY";
    case WASI_FILESYSTEM_TYPES_ERROR_CODE_CROSS_DEVICE: return "EXDEV";
    default: return "EIO";
  }
}
bool host_error(JSContext* cx, Error e, const char* operation, View path={}, View dest={}) {
  api::throw_error(cx, FsFailure, operation);
  return decorate(cx, errno_code(e), operation, path, dest, e);
}
bindings_string_t string(View text) {
  return {reinterpret_cast<uint8_t*>(const_cast<char*>(text.data())), text.size()};
}
struct Descriptor {
  Own value{};
  bool active=false;
  Descriptor()=default;
  Descriptor(const Descriptor&)=delete;
  Descriptor& operator=(const Descriptor&)=delete;
  ~Descriptor(){close();}
  void close(){if(active){active=false;wasi_filesystem_types_descriptor_drop_own(value);}}
  Borrow borrow()const{return wasi_filesystem_types_borrow_descriptor(value);}
};
struct Bytes {
  bindings_tuple2_list_u8_bool_t value{};
  ~Bytes(){bindings_list_u8_free(&value.f0);}
};
struct OwnedString {
  bindings_string_t value{};
  ~OwnedString(){bindings_string_free(&value);}
};
struct Preopens {
  wasi_filesystem_preopens_list_tuple2_own_descriptor_string_t value{};
  bool loaded=false;
  Preopens(const Preopens&)=delete;
  Preopens()=default;
  ~Preopens(){
    if(loaded){
      // Generated list_free frees strings/array only; it does NOT drop owns.
      for(size_t i=0;i<value.len;i++)wasi_filesystem_types_descriptor_drop_own(value.ptr[i].f0);
      wasi_filesystem_preopens_list_tuple2_own_descriptor_string_free(&value);
    }
  }
  bool load(JSContext* cx){
    wasi_filesystem_preopens_get_directories(&value);loaded=true;
    if(value.len>MaxPreopens)return limit(cx,"preopens");
    for(size_t i=0;i<value.len;i++){
      auto& name=value.ptr[i].f1;
      if(!name.len||name.len>MaxPathBytes||!name.ptr||name.ptr[0]!='/'||std::memchr(name.ptr,0,name.len))
        return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","preopens");
    }
    return true;
  }
};
struct Path {
  char bytes[MaxPathBytes+1]{};
  size_t length=0;
  View view()const{return {bytes,length};}
};
bool owned_copy(JSContext* cx, View text, JS::UniqueChars* out) {
  out->reset(static_cast<char*>(JS_malloc(cx,text.size()+1)));
  if(!*out){JS_ReportOutOfMemory(cx);return false;}
  if(!text.empty())std::memcpy(out->get(),text.data(),text.size());
  out->get()[text.size()]=0;return true;
}
bool valid_path(JSContext* cx, View text, const char* op){
  if(text.empty())return fail(cx,"ENOENT",op,text);
  if(text.size()>MaxPathBytes)return fail(cx,"ENAMETOOLONG",op);
  if(std::memchr(text.data(),0,text.size()))return fail(cx,"ERR_INVALID_ARG_VALUE",op);
  return true;
}
bool absolute(JSContext* cx, View input, Path* out, const char* op) {
  if(!valid_path(cx,input,op))return false;
  JS::UniqueChars base;size_t n=0;
  if(input[0]!='/'){
    if(!cwd(cx,&base,&n))return false;
    if(n+1+input.size()>MaxPathBytes)return fail(cx,"ENAMETOOLONG",op);
    std::memcpy(out->bytes,base.get(),n);out->bytes[n++]='/';
  }
  std::memcpy(out->bytes+n,input.data(),input.size());n+=input.size();
  // Collapse repeated slashes only. Keep dot/dotdot and a trailing slash for
  // actual host/symlink resolution: file/. and file/ must still fail ENOTDIR.
  const bool trailing_slash=n>1&&out->bytes[n-1]=='/';
  size_t read=0,write=0;
  while(read<n){
    while(read<n&&out->bytes[read]=='/')read++;
    const size_t start=read;while(read<n&&out->bytes[read]!='/')read++;
    const size_t len=read-start;if(!len)continue;
    out->bytes[write++]='/';std::memmove(out->bytes+write,out->bytes+start,len);write+=len;
  }
  if(!write)out->bytes[write++]='/';
  if(trailing_slash&&write>1)out->bytes[write++]='/';
  out->bytes[write]=0;out->length=write;return true;
}
struct Location { Borrow root{};View name;View relative; };
bool locate(JSContext* cx, const Preopens& dirs, View path, Location* out, const char* op){
  size_t best=0;bool found=false;
  for(size_t i=0;i<dirs.value.len;i++){
    const auto& item=dirs.value.ptr[i];View name(reinterpret_cast<char*>(item.f1.ptr),item.f1.len);
    while(name.size()>1&&name.back()=='/')name.remove_suffix(1);
    if(path.size()<name.size()||path.substr(0,name.size())!=name)continue;
    if(name!="/"&&path.size()!=name.size()&&path[name.size()]!='/')continue;
    if(!found||name.size()>best){
      found=true;best=name.size();out->root=wasi_filesystem_types_borrow_descriptor(item.f0);
      out->name=name;out->relative=path.substr(name=="/"?1:name.size());
      if(!out->relative.empty()&&out->relative[0]=='/')out->relative.remove_prefix(1);
      if(out->relative.empty())out->relative=".";
    }
  }
  return found?true:fail(cx,"ENOENT",op,path);
}
bool open_file(JSContext* cx,const Location& loc,uint8_t flags,uint8_t open_flags,
               Descriptor* out,const char* op,View path){
  auto name=string(loc.relative);Error e;
  if(!wasi_filesystem_types_method_descriptor_open_at(loc.root,Follow,&name,open_flags,flags,&out->value,&e))return host_error(cx,e,op,path);
  out->active=true;return true;
}
bool metadata(JSContext* cx,const wasi_filesystem_types_descriptor_stat_t& src,Metadata* out,View path){
  if(src.type>WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_SOCKET)return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","stat",path);
  for(const auto* t:{&src.data_access_timestamp,&src.data_modification_timestamp,&src.status_change_timestamp})
    if(t->is_some&&t->val.nanoseconds>=1000000000)return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","stat",path);
  if(src.size>9007199254740991ULL||src.link_count>9007199254740991ULL)return limit(cx,"stat-number",path);
  out->type=src.type;out->size=src.size;out->links=src.link_count;
  const auto time=[](const wasi_filesystem_types_option_datetime_t& t){return double(t.val.seconds)*1000+double(t.val.nanoseconds)/1e6;};
  out->has_atime=src.data_access_timestamp.is_some;out->has_mtime=src.data_modification_timestamp.is_some;out->has_ctime=src.status_change_timestamp.is_some;
  if(out->has_atime)out->atime_ms=time(src.data_access_timestamp);
  if(out->has_mtime)out->mtime_ms=time(src.data_modification_timestamp);
  if(out->has_ctime)out->ctime_ms=time(src.status_change_timestamp);
  for(double t:{out->atime_ms,out->mtime_ms,out->ctime_ms})if(t>8640000000000000.0)return limit(cx,"stat-time",path);
  return true;
}
} // anonymous

bool check_deployed(JSContext* cx,const char* operation){
  auto* engine=api::Engine::get(cx);
  if(engine&&engine->state()==api::EngineState::Initialized&&entropy::deployed_execution_started())return true;
  api::throw_error(cx,FsInitialization);
  return decorate(cx,"ERR_SM_NODE_FS_INITIALIZATION",operation);
}
bool cwd(JSContext* cx,JS::UniqueChars* value,size_t* length){
  if(!check_deployed(cx,"cwd"))return false;
  if(selected_cwd_length){
    if(!owned_copy(cx,{selected_cwd,selected_cwd_length},value))return false;
    *length=selected_cwd_length;return true;
  }
  OwnedString result;const bool present=wasi_cli_environment_initial_cwd(&result.value);
  View text=present?View(reinterpret_cast<char*>(result.value.ptr),result.value.len):View("/");
  if(!valid_path(cx,text,"cwd"))return false;
  if(text[0]!='/')return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","cwd");
  if(!owned_copy(cx,text,value))return false;*length=text.size();return true;
}
bool chdir(JSContext* cx,const char* text,size_t length){
  if(!check_deployed(cx,"chdir"))return false;
  JS::UniqueChars canonical;size_t count=0;
  if(!realpath(cx,text,length,&canonical,&count))return false;
  Metadata stat;
  if(!stat_path(cx,canonical.get(),count,true,&stat))return false;
  if(stat.type!=WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY)return fail(cx,"ENOTDIR","chdir",{text,length});
  MOZ_ASSERT(count&&count<=MaxPathBytes);
  std::memcpy(selected_cwd,canonical.get(),count);selected_cwd[count]=0;
  selected_cwd_length=count;return true;
}
bool stat_path(JSContext* cx,const char* text,size_t length,bool follow,Metadata* out){
  if(!check_deployed(cx,"stat"))return false;
  Path path;if(!absolute(cx,{text,length},&path,"stat"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;
  if(!locate(cx,dirs,path.view(),&loc,"stat"))return false;
  auto name=string(loc.relative);wasi_filesystem_types_descriptor_stat_t raw{};Error e;
  if(!wasi_filesystem_types_method_descriptor_stat_at(loc.root,follow?Follow:0,&name,&raw,&e))return host_error(cx,e,follow?"stat":"lstat",path.view());
  return metadata(cx,raw,out,path.view());
}
bool read_bytes(JSContext* cx,const char* text,size_t length,JS::UniqueChars* bytes,size_t* count){
  if(!check_deployed(cx,"readFile"))return false;
  Path path;if(!absolute(cx,{text,length},&path,"readFile"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;Descriptor file;
  if(!locate(cx,dirs,path.view(),&loc,"readFile")||!open_file(cx,loc,Read,0,&file,"readFile",path.view()))return false;
  wasi_filesystem_types_descriptor_stat_t stat{};Error e;
  if(!wasi_filesystem_types_method_descriptor_stat(file.borrow(),&stat,&e))return host_error(cx,e,"readFile",path.view());
  if(stat.type!=WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_REGULAR_FILE)return fail(cx,stat.type==WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY?"EISDIR":"ERR_SM_NODE_UNSUPPORTED","readFile",path.view());
  if(stat.size>MaxFileBytes)return limit(cx,"readFile",path.view());
  bytes->reset(static_cast<char*>(JS_malloc(cx,size_t(stat.size)+1)));
  if(!*bytes){JS_ReportOutOfMemory(cx);return false;}
  size_t done=0;bool eof=false;
  while(done<size_t(stat.size)){
    Bytes block;const size_t want=std::min(ChunkBytes,size_t(stat.size)-done);
    if(!wasi_filesystem_types_method_descriptor_read(file.borrow(),want,done,&block.value,&e))return host_error(cx,e,"readFile",path.view());
    auto& data=block.value.f0;
    if(data.len>want||(data.len&&!data.ptr)||(!data.len&&!block.value.f1))return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","readFile",path.view());
    if(data.len)std::memcpy(bytes->get()+done,data.ptr,data.len);done+=data.len;eof=block.value.f1;
    if(eof)break;
  }
  if(!eof){
    Bytes tail;
    if(!wasi_filesystem_types_method_descriptor_read(file.borrow(),1,done,&tail.value,&e))return host_error(cx,e,"readFile",path.view());
    if(tail.value.f0.len||!tail.value.f1)return fail(cx,"ERR_SM_NODE_FS_CHANGED","readFile",path.view());
  }
  bytes->get()[done]=0;*count=done;return true;
}

bool realpath(JSContext* cx,const char* text,size_t length,JS::UniqueChars* canonical,size_t* canonical_length){
  if(!check_deployed(cx,"realpath"))return false;
  Path todo;if(!absolute(cx,{text,length},&todo,"realpath"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;
  for(size_t links=0;links<=MaxSymlinks;){
    Location loc;if(!locate(cx,dirs,todo.view(),&loc,"realpath"))return false;
    Path resolved;std::memcpy(resolved.bytes,loc.name.data(),loc.name.size());resolved.length=loc.name.size();
    View rest=loc.relative;bool restart=false;
    while(!rest.empty()){
      const size_t slash=rest.find('/');const View part=rest.substr(0,slash);rest=slash==View::npos?View{}:rest.substr(slash+1);
      if(part.empty()||part==".")continue;
      if(part==".."){
        if(resolved.length==loc.name.size()){
          if(loc.name=="/")continue;
          return fail(cx,"EPERM","realpath",todo.view()); // preopen capability boundary
        }
        while(resolved.length>loc.name.size()&&resolved.bytes[resolved.length-1]!='/')resolved.length--;
        if(resolved.length>loc.name.size())resolved.length--;continue;
      }
      const size_t parent_length=resolved.length;
      if(resolved.length>1)resolved.bytes[resolved.length++]='/';
      if(resolved.length+part.size()>MaxPathBytes)return fail(cx,"ENAMETOOLONG","realpath");
      std::memcpy(resolved.bytes+resolved.length,part.data(),part.size());resolved.length+=part.size();
      View relative=resolved.view().substr(loc.name=="/"?1:loc.name.size()+1);auto name=string(relative);
      wasi_filesystem_types_descriptor_stat_t st{};Error e;
      if(!wasi_filesystem_types_method_descriptor_stat_at(loc.root,0,&name,&st,&e))return host_error(cx,e,"realpath",todo.view());
      if(st.type==WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_SYMBOLIC_LINK){
        if(++links>MaxSymlinks)return fail(cx,"ELOOP","realpath",todo.view());
        OwnedString target;
        if(!wasi_filesystem_types_method_descriptor_readlink_at(loc.root,&name,&target.value,&e))return host_error(cx,e,"realpath",todo.view());
        View value(reinterpret_cast<char*>(target.value.ptr),target.value.len);
        if(!valid_path(cx,value,"realpath"))return false;
        Path replaced;
        size_t n=0;
        if(value[0]!='/'){
          n=parent_length;std::memcpy(replaced.bytes,resolved.bytes,n);
          if(n>1)replaced.bytes[n++]='/';
        }
        if(n+value.size()+(!rest.empty()?rest.size()+1:0)>MaxPathBytes)return fail(cx,"ENAMETOOLONG","realpath");
        std::memcpy(replaced.bytes+n,value.data(),value.size());n+=value.size();
        if(!rest.empty()){replaced.bytes[n++]='/';std::memcpy(replaced.bytes+n,rest.data(),rest.size());n+=rest.size();}
        if(!absolute(cx,{replaced.bytes,n},&todo,"realpath"))return false;
        restart=true;break;
      }
      if(!rest.empty()&&st.type!=WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY)return fail(cx,"ENOTDIR","realpath",todo.view());
    }
    if(restart)continue;
    if(!owned_copy(cx,resolved.view(),canonical))return false;*canonical_length=resolved.length;return true;
  }
  return fail(cx,"ELOOP","realpath",todo.view());
}

namespace {
bool text_arg(JSContext* cx,JS::HandleValue value,JS::UniqueChars* text,size_t* length,const char* op){
  if(!value.isString())return fail(cx,"ERR_INVALID_ARG_TYPE",op);
  JS::RootedString input(cx,value.toString());const size_t n=JS::GetStringLength(input);
  if(n>MaxPathBytes)return fail(cx,"ENAMETOOLONG",op);
  for(size_t i=0;i<n;i++){char16_t c;if(!JS_GetStringCharAt(cx,input,i,&c))return false;if(c==0)return fail(cx,"ERR_INVALID_ARG_VALUE",op);}
  *text=JS_EncodeStringToUTF8(cx,input);if(!*text)return false;
  *length=std::strlen(text->get());return valid_path(cx,{text->get(),*length},op);
}
bool args_path(JSContext* cx,const JS::CallArgs& args,size_t index,JS::UniqueChars* text,size_t* n,const char* op){
  return args.requireAtLeast(cx,op,index+1)&&text_arg(cx,args[index],text,n,op);
}
bool bytes_record(JSContext* cx,JS::UniqueChars bytes,size_t length,bool eof,JS::MutableHandleValue result){
  // The actual SDK147 owned overload consumes JS_free-compatible allocation,
  // including on failure. No borrowed inline GC pointer crosses this call.
  JS::RootedObject buffer(cx,JS::NewArrayBufferWithContents(cx,length,std::move(bytes)));
  if(!buffer)return false;
  JS::RootedObject record(cx,JS_NewPlainObject(cx));if(!record)return false;
  JS::RootedValue value(cx,JS::ObjectValue(*buffer));
  if(!JS_DefineProperty(cx,record,"buffer",value,JSPROP_ENUMERATE)||!number(cx,record,"byteOffset",0)||
     !number(cx,record,"byteLength",length)||!boolean(cx,record,"eof",eof))return false;
  result.setObject(*record);return true;
}
bool js_phase(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);
  if(!check_deployed(cx,"filesystem"))return false;args.rval().setUndefined();return true;
}
bool js_read(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"readFile"))return false;
  JS::UniqueChars path,bytes;size_t n=0,count=0;
  if(!args_path(cx,args,0,&path,&n,"readFile")||!read_bytes(cx,path.get(),n,&bytes,&count))return false;
  return bytes_record(cx,std::move(bytes),count,true,args.rval());
}
bool js_stat(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"stat"))return false;
  JS::UniqueChars path;size_t n=0;Metadata m;
  if(!args_path(cx,args,0,&path,&n,"stat")||!args.requireAtLeast(cx,"stat",2))return false;
  if(!args[1].isBoolean())return fail(cx,"ERR_INVALID_ARG_TYPE","stat");
  if(!stat_path(cx,path.get(),n,args[1].toBoolean(),&m))return false;
  JS::RootedObject record(cx,JS_NewPlainObject(cx));if(!record)return false;
  if(!number(cx,record,"type",m.type)||!number(cx,record,"size",double(m.size))||!number(cx,record,"nlink",double(m.links))||
     !boolean(cx,record,"hasAtime",m.has_atime)||!boolean(cx,record,"hasMtime",m.has_mtime)||!boolean(cx,record,"hasCtime",m.has_ctime))return false;
  if(m.has_atime&&!number(cx,record,"atimeMs",m.atime_ms))return false;
  if(m.has_mtime&&!number(cx,record,"mtimeMs",m.mtime_ms))return false;
  if(m.has_ctime&&!number(cx,record,"ctimeMs",m.ctime_ms))return false;
  args.rval().setObject(*record);return true;
}
bool fixed_u8(JSContext* cx,JS::HandleValue value,JS::MutableHandleObject view,
              JS::MutableHandleObject backing,size_t* length){
  if(!value.isObject())return fail(cx,"ERR_INVALID_ARG_TYPE","writeFile");
  view.set(&value.toObject());bool shared=false;uint8_t* ignored=nullptr;
  if(!JS_GetObjectAsUint8Array(view,length,&shared,&ignored))return fail(cx,"ERR_INVALID_ARG_TYPE","writeFile");
  if(shared||JS::IsResizableArrayBufferView(view))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","writeFile");
  backing.set(JS_GetArrayBufferViewBuffer(cx,view,&shared));if(!backing)return false;
  if(shared||JS::IsDetachedArrayBufferObject(backing))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","writeFile");
  if(*length>MaxFileBytes)return limit(cx,"writeFile");return true;
}
bool js_write(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"writeFile"))return false;
  JS::UniqueChars text;size_t n=0,length=0;
  if(!args_path(cx,args,0,&text,&n,"writeFile")||!args.requireAtLeast(cx,"writeFile",3))return false;
  if(!args[2].isInt32()||(args[2].toInt32()!=0&&args[2].toInt32()!=1))return fail(cx,"ERR_SM_NODE_UNSUPPORTED","writeFile");
  JS::RootedObject view(cx),backing(cx);if(!fixed_u8(cx,args[1],&view,&backing,&length))return false;
  JS::UniqueChars staging(static_cast<char*>(JS_malloc(cx,ChunkBytes)));
  if(!staging){JS_ReportOutOfMemory(cx);return false;}
  Path path;if(!absolute(cx,{text.get(),n},&path,"writeFile"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;Descriptor file;
  const uint8_t flags=WASI_FILESYSTEM_TYPES_OPEN_FLAGS_CREATE|
      (args[2].toInt32()==1?WASI_FILESYSTEM_TYPES_OPEN_FLAGS_EXCLUSIVE:WASI_FILESYSTEM_TYPES_OPEN_FLAGS_TRUNCATE);
  if(!locate(cx,dirs,path.view(),&loc,"writeFile")||!open_file(cx,loc,Write,flags,&file,"writeFile",path.view()))return false;
  size_t done=0;Error e;
  while(done<length){
    const size_t want=std::min(ChunkBytes,length-done);
    {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const uint8_t* data=JS_GetUint8ArrayData(view,&shared,nogc);MOZ_ASSERT(!shared);std::memcpy(staging.get(),data+done,want);}
    // The host import sees only owned staging, never a borrowed JS pointer.
    bindings_list_u8_t bytes{reinterpret_cast<uint8_t*>(staging.get()),want};uint64_t wrote=0;
    if(!wasi_filesystem_types_method_descriptor_write(file.borrow(),&bytes,done,&wrote,&e))return host_error(cx,e,"writeFile",path.view());
    if(!wrote||wrote>want)return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","writeFile",path.view());
    done+=size_t(wrote);
  }
  args.rval().setUndefined();return true;
}
bool js_mkdir(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"mkdir"))return false;
  JS::UniqueChars text;size_t n=0;
  if(!args_path(cx,args,0,&text,&n,"mkdir")||!args.requireAtLeast(cx,"mkdir",2))return false;
  if(!args[1].isBoolean())return fail(cx,"ERR_INVALID_ARG_TYPE","mkdir");
  Path path;if(!absolute(cx,{text.get(),n},&path,"mkdir"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;if(!locate(cx,dirs,path.view(),&loc,"mkdir"))return false;
  Error e;auto name=string(loc.relative);
  if(!args[1].toBoolean()){
    if(!wasi_filesystem_types_method_descriptor_create_directory_at(loc.root,&name,&e))return host_error(cx,e,"mkdir",path.view());
    args.rval().setUndefined();return true;
  }
  size_t first=0;
  if(loc.relative!=".")for(size_t i=0;i<=loc.relative.size();i++){
    if(i<loc.relative.size()&&loc.relative[i]!='/')continue;
    auto prefix=string(loc.relative.substr(0,i));
    if(wasi_filesystem_types_method_descriptor_create_directory_at(loc.root,&prefix,&e)){
      if(!first)first=i;
    }else if(e==WASI_FILESYSTEM_TYPES_ERROR_CODE_EXIST){
      wasi_filesystem_types_descriptor_stat_t st{};
      if(!wasi_filesystem_types_method_descriptor_stat_at(loc.root,Follow,&prefix,&st,&e))return host_error(cx,e,"mkdir",path.view());
      if(st.type!=WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY)return fail(cx,"ENOTDIR","mkdir",path.view());
    }else return host_error(cx,e,"mkdir",path.view());
  }
  if(first){
    const size_t root=loc.name=="/"?1:loc.name.size()+1;
    JS::RootedString value(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(path.bytes,root+first)));
    if(!value)return false;args.rval().setString(value);
  }else args.rval().setUndefined();
  return true;
}
bool mutate(JSContext* cx,unsigned argc,JS::Value* vp,int kind){
  const char* op=kind==0?"link":kind==1?"rename":"unlink";
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,op))return false;
  JS::UniqueChars a,b;size_t an=0,bn=0;
  if(!args_path(cx,args,0,&a,&an,op)||(kind!=2&&!args_path(cx,args,1,&b,&bn,op)))return false;
  Path source,dest;if(!absolute(cx,{a.get(),an},&source,op))return false;
  if(kind!=2&&!absolute(cx,{b.get(),bn},&dest,op))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location old,now;
  if(!locate(cx,dirs,source.view(),&old,op)||(kind!=2&&!locate(cx,dirs,dest.view(),&now,op)))return false;
  auto from=string(old.relative),to=string(now.relative);Error e;bool ok=false;
  if(kind==0)ok=wasi_filesystem_types_method_descriptor_link_at(old.root,0,&from,now.root,&to,&e);
  else if(kind==1)ok=wasi_filesystem_types_method_descriptor_rename_at(old.root,&from,now.root,&to,&e);
  else ok=wasi_filesystem_types_method_descriptor_unlink_file_at(old.root,&from,&e);
  if(!ok)return host_error(cx,e,op,source.view(),kind==2?View{}:dest.view());
  args.rval().setUndefined();return true;
}
bool js_link(JSContext* cx,unsigned n,JS::Value* vp){return mutate(cx,n,vp,0);}
bool js_rename(JSContext* cx,unsigned n,JS::Value* vp){return mutate(cx,n,vp,1);}
bool js_unlink(JSContext* cx,unsigned n,JS::Value* vp){return mutate(cx,n,vp,2);}
bool js_access(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"access"))return false;
  JS::UniqueChars text;size_t n=0;
  if(!args_path(cx,args,0,&text,&n,"access")||!args.requireAtLeast(cx,"access",2))return false;
  if(!args[1].isInt32()||(args[1].toInt32()&~7))return fail(cx,"ERR_INVALID_ARG_VALUE","access");
  const int mode=args[1].toInt32();
  if(mode&1)return fail(cx,"ERR_SM_NODE_UNSUPPORTED","access"); // no WASI execute-right equivalent
  Path path;if(!absolute(cx,{text.get(),n},&path,"access"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;if(!locate(cx,dirs,path.view(),&loc,"access"))return false;
  auto name=string(loc.relative);Error e;wasi_filesystem_types_descriptor_stat_t st{};
  if(!wasi_filesystem_types_method_descriptor_stat_at(loc.root,Follow,&name,&st,&e))return host_error(cx,e,"access",path.view());
  if(mode){
    const bool directory=st.type==WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY;
    const uint8_t flags=(mode&4?Read:0)|(mode&2?(directory?WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_MUTATE_DIRECTORY:Write):0);
    Descriptor probe;if(!open_file(cx,loc,flags,directory?Directory:0,&probe,"access",path.view()))return false;
  }
  args.rval().setUndefined();return true;
}
struct DirectoryStream {
  wasi_filesystem_types_own_directory_entry_stream_t value{};bool active=false;
  ~DirectoryStream(){if(active)wasi_filesystem_types_directory_entry_stream_drop_own(value);}
};
struct Entry {
  wasi_filesystem_types_option_directory_entry_t value{};
  ~Entry(){if(value.is_some)wasi_filesystem_types_directory_entry_free(&value.val);}
};
bool js_readdir(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"readdir"))return false;
  JS::UniqueChars text;size_t n=0;if(!args_path(cx,args,0,&text,&n,"readdir"))return false;
  Path path;if(!absolute(cx,{text.get(),n},&path,"readdir"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;Descriptor dir;
  if(!locate(cx,dirs,path.view(),&loc,"readdir")||!open_file(cx,loc,Read,Directory,&dir,"readdir",path.view()))return false;
  DirectoryStream stream;Error e;
  if(!wasi_filesystem_types_method_descriptor_read_directory(dir.borrow(),&stream.value,&e))return host_error(cx,e,"readdir",path.view());stream.active=true;
  JS::RootedObject array(cx,JS::NewArrayObject(cx,0));if(!array)return false;
  uint32_t index=0;
  while(true){
    Entry entry;
    if(!wasi_filesystem_types_method_directory_entry_stream_read_directory_entry(wasi_filesystem_types_borrow_directory_entry_stream(stream.value),&entry.value,&e))return host_error(cx,e,"readdir",path.view());
    if(!entry.value.is_some)break;
    auto& raw=entry.value.val;View name(reinterpret_cast<char*>(raw.name.ptr),raw.name.len);
    if(name=="."||name=="..")continue;
    if(name.empty()||!raw.name.ptr)return fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","readdir",path.view());
    if(index==MaxDirectoryEntries||name.size()>MaxPathBytes||name.find('/')!=View::npos||name.find('\0')!=View::npos)return limit(cx,"readdir",path.view());
    uint8_t type=raw.type;
    if(type==WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_UNKNOWN){
      if(loc.relative.size()+name.size()+1>MaxPathBytes)return limit(cx,"readdir",path.view());
      char joined[MaxPathBytes+1];std::memcpy(joined,loc.relative.data(),loc.relative.size());joined[loc.relative.size()]='/';std::memcpy(joined+loc.relative.size()+1,name.data(),name.size());
      auto relative=string({joined,loc.relative.size()+name.size()+1});wasi_filesystem_types_descriptor_stat_t st{};
      if(!wasi_filesystem_types_method_descriptor_stat_at(loc.root,0,&relative,&st,&e))return host_error(cx,e,"readdir",path.view());type=st.type;
    }
    JS::RootedObject record(cx,JS_NewPlainObject(cx));if(!record)return false;
    if(!property(cx,record,"name",name)||!number(cx,record,"type",type))return false;
    JS::RootedValue value(cx,JS::ObjectValue(*record));if(!JS_DefineElement(cx,array,index++,value,JSPROP_ENUMERATE))return false;
  }
  args.rval().setObject(*array);return true;
}
bool js_realpath(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"realpath"))return false;
  JS::UniqueChars path,value;size_t n=0,len=0;
  if(!args_path(cx,args,0,&path,&n,"realpath")||!realpath(cx,path.get(),n,&value,&len))return false;
  JS::RootedString result(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(value.get(),len)));if(!result)return false;
  args.rval().setString(result);return true;
}
bool js_cwd(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);JS::UniqueChars path;size_t n=0;if(!cwd(cx,&path,&n))return false;
  JS::RootedString result(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(path.get(),n)));if(!result)return false;
  args.rval().setString(result);return true;
}
bool js_readlink(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"readlink"))return false;
  JS::UniqueChars text;size_t n=0;if(!args_path(cx,args,0,&text,&n,"readlink"))return false;
  Path path;if(!absolute(cx,{text.get(),n},&path,"readlink"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;if(!locate(cx,dirs,path.view(),&loc,"readlink"))return false;
  OwnedString result;auto name=string(loc.relative);Error e;
  if(!wasi_filesystem_types_method_descriptor_readlink_at(loc.root,&name,&result.value,&e))return host_error(cx,e,"readlink",path.view());
  JS::RootedString value(cx,JS_NewStringCopyUTF8N(cx,JS::UTF8Chars(reinterpret_cast<char*>(result.value.ptr),result.value.len)));
  if(!value)return false;args.rval().setString(value);return true;
}

constexpr uint64_t MaxStreamBytes=64ULL*1024*1024;
constexpr size_t MaxOpenStreams=64;
size_t open_streams=0;
uint64_t next_stream_id=1;
struct ReadHandle {
  Descriptor file;
  uint64_t id=0,position=0,end_exclusive=0,read=0;
  bool has_end=false,registered=false;
  ~ReadHandle(){if(registered){MOZ_ASSERT(open_streams>0);open_streams--;}}
};
void retire_handle(JSObject* object){
  JS::Value slot=JS::GetReservedSlot(object,0);
  if(!slot.isUndefined()){
    auto* state=static_cast<ReadHandle*>(slot.toPrivate());
    JS::SetReservedSlot(object,0,JS::UndefinedValue());
    delete state; // Descriptor owns a real WASI resource, dropped exactly once.
  }
}
void finalize_handle(JS::GCContext*,JSObject* object){retire_handle(object);}
const JSClassOps HandleOps={.finalize=finalize_handle};
// No hidden JS heap edge. The Readable's JS WeakMap value keeps this native
// handle object traced; foreground finalization is a backstop to explicit close.
const JSClass HandleClass={"PrivateNextFsReadHandle",JSCLASS_HAS_RESERVED_SLOTS(1)|JSCLASS_FOREGROUND_FINALIZE,&HandleOps};
ReadHandle* handle_state(JSContext* cx,JS::HandleValue value){
  if(!value.isObject()||JS::GetClass(&value.toObject())!=&HandleClass){fail(cx,"EBADF","read");return nullptr;}
  JS::Value slot=JS::GetReservedSlot(&value.toObject(),0);
  if(slot.isUndefined()){fail(cx,"EBADF","read");return nullptr;}
  return static_cast<ReadHandle*>(slot.toPrivate());
}
bool integer(JSContext* cx,JS::HandleValue value,uint64_t* out,const char* op){
  if(!value.isNumber())return fail(cx,"ERR_INVALID_ARG_TYPE",op);
  const double n=value.toNumber();
  if(!std::isfinite(n)||n<0||n>9007199254740991.0||std::floor(n)!=n)return fail(cx,"ERR_OUT_OF_RANGE",op);
  *out=uint64_t(n);return true;
}
bool js_open_read(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"open"))return false;
  JS::UniqueChars text;size_t n=0;uint64_t start=0,end=0;
  if(!args_path(cx,args,0,&text,&n,"open")||!args.requireAtLeast(cx,"open",3)||!integer(cx,args[1],&start,"open"))return false;
  const bool has_end=!(args[2].isNumber()&&args[2].toNumber()==-1);
  if(has_end){
    if(!integer(cx,args[2],&end,"open"))return false;
    if(end<start)return fail(cx,"ERR_OUT_OF_RANGE","open");
  }
  if(has_end&&end-start+1>MaxStreamBytes)return limit(cx,"stream-range");
  if(open_streams==MaxOpenStreams||next_stream_id>9007199254740991ULL)return limit(cx,"open-streams");
  Path path;if(!absolute(cx,{text.get(),n},&path,"open"))return false;
  Preopens dirs;if(!dirs.load(cx))return false;Location loc;
  if(!locate(cx,dirs,path.view(),&loc,"open"))return false;
  auto state=std::unique_ptr<ReadHandle>(new(std::nothrow)ReadHandle());
  if(!state){JS_ReportOutOfMemory(cx);return false;}
  if(!open_file(cx,loc,Read,0,&state->file,"open",path.view()))return false;
  wasi_filesystem_types_descriptor_stat_t st{};Error e;
  if(!wasi_filesystem_types_method_descriptor_stat(state->file.borrow(),&st,&e))return host_error(cx,e,"open",path.view());
  if(st.type!=WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_REGULAR_FILE)return fail(cx,st.type==WASI_FILESYSTEM_TYPES_DESCRIPTOR_TYPE_DIRECTORY?"EISDIR":"ERR_SM_NODE_UNSUPPORTED","open",path.view());
  JS::RootedObject handle(cx,JS_NewObject(cx,&HandleClass));if(!handle)return false;
  state->position=start;state->has_end=has_end;state->end_exclusive=end+1;state->id=next_stream_id++;
  const uint64_t id=state->id;state->registered=true;open_streams++;
  JS::SetReservedSlot(handle,0,JS::PrivateValue(state.release()));
  JS::RootedObject result(cx,JS_NewPlainObject(cx));
  if(!result){retire_handle(handle);return false;}
  JS::RootedValue handle_value(cx,JS::ObjectValue(*handle));
  if(!JS_DefineProperty(cx,result,"handle",handle_value,JSPROP_ENUMERATE)||!number(cx,result,"id",double(id))){retire_handle(handle);return false;}
  args.rval().setObject(*result);return true;
}
bool js_close_read(JSContext* cx,unsigned argc,JS::Value* vp){
  // Release only: must also work on cleanup after Engine abort. Acquisition and
  // reads remain deployed-only; no handle can be created during INIT.
  auto args=JS::CallArgsFromVp(argc,vp);
  if(!args.requireAtLeast(cx,"close",1)||!args[0].isObject()||JS::GetClass(&args[0].toObject())!=&HandleClass)return fail(cx,"EBADF","close");
  JS::RootedObject handle(cx,&args[0].toObject());retire_handle(handle);
  args.rval().setUndefined();return true;
}
bool js_read_chunk(JSContext* cx,unsigned argc,JS::Value* vp){
  auto args=JS::CallArgsFromVp(argc,vp);if(!check_deployed(cx,"read"))return false;
  if(!args.requireAtLeast(cx,"read",2))return false;
  auto* state=handle_state(cx,args[0]);if(!state)return false;
  JS::RootedObject handle(cx,&args[0].toObject());uint64_t request=0;
  if(!integer(cx,args[1],&request,"read"))return false;
  if(request==0||request>ChunkBytes)return fail(cx,"ERR_OUT_OF_RANGE","read");
  if(state->has_end&&state->position>=state->end_exclusive){
    retire_handle(handle);JS::UniqueChars empty;if(!owned_copy(cx,"",&empty))return false;
    return bytes_record(cx,std::move(empty),0,true,args.rval());
  }
  uint64_t want=std::min(request,MaxStreamBytes-state->read);
  if(state->has_end)want=std::min(want,state->end_exclusive-state->position);
  const bool budget_check=want==0;Bytes bytes;Error e;
  if(!wasi_filesystem_types_method_descriptor_read(state->file.borrow(),budget_check?1:want,state->position,&bytes.value,&e)){
    retire_handle(handle);return host_error(cx,e,"read");
  }
  auto& raw=bytes.value.f0;
  if((budget_check&&raw.len)||raw.len>(budget_check?1:want)||(raw.len&&!raw.ptr)||(!raw.len&&!bytes.value.f1)){
    retire_handle(handle);return budget_check?limit(cx,"stream-bytes"):fail(cx,"ERR_SM_NODE_FS_HOST_RESULT","read");
  }
  JS::UniqueChars owned;
  if(!owned_copy(cx,{reinterpret_cast<char*>(raw.ptr),raw.len},&owned)){retire_handle(handle);return false;}
  state->position+=raw.len;state->read+=raw.len;
  const bool eof=bytes.value.f1||(state->has_end&&state->position==state->end_exclusive);
  if(eof)retire_handle(handle);
  return bytes_record(cx,std::move(owned),raw.len,eof,args.rval());
}

const JSFunctionSpec KernelFunctions[]={
 JS_FN("checkPhase",js_phase,0,0),JS_FN("readFile",js_read,1,0),JS_FN("stat",js_stat,2,0),
 JS_FN("writeFile",js_write,3,0),JS_FN("mkdir",js_mkdir,2,0),JS_FN("link",js_link,2,0),
 JS_FN("rename",js_rename,2,0),JS_FN("unlink",js_unlink,1,0),JS_FN("access",js_access,2,0),
 JS_FN("readdir",js_readdir,1,0),JS_FN("realpath",js_realpath,1,0),JS_FN("readlink",js_readlink,1,0),
 JS_FN("cwd",js_cwd,0,0),JS_FN("openRead",js_open_read,3,0),JS_FN("readChunk",js_read_chunk,2,0),
 JS_FN("closeRead",js_close_read,1,0),JS_FS_END
};
} // anonymous

JSObject* create_kernel(JSContext* cx){
  JS::RootedObject object(cx,JS_NewPlainObject(cx));
  if(!object||!JS_DefineFunctions(cx,object,KernelFunctions))return nullptr;
  return object;
}

} // namespace builtins::node_compat::next_fs
