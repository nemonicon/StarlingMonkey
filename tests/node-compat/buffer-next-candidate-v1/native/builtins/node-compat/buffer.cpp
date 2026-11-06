// Native guest byte kernels for the bounded Node v22.14.0 profile.
#include "builtin.h"
#include "js/CharacterEncoding.h"
#include "js/ErrorReport.h"
#include "js/GCAPI.h"
#include "js/MemoryFunctions.h"
#include "js/String.h"
#include "js/Array.h"
#include "js/GCVector.h"
#include <algorithm>
#include <cmath>
#include <cstring>

#ifdef NODE_COMPAT_OOM_TESTING
#include "oom-testing.h"
#define NODE_BUFFER_ALLOC(cx, site, expression)                                              \
  oom_testing::allocate<oom_testing::Point::site>(cx, [&] { return (expression); })
#define NODE_BUFFER_OWNED(expression) oom_testing::track(expression)
#define NODE_BUFFER_AUDIT() oom_testing::KernelAudit ownership_audit
using KernelChars = builtins::node_compat::oom_testing::Chars;
#else
#define NODE_BUFFER_ALLOC(cx, site, expression) (expression)
#define NODE_BUFFER_OWNED(expression) (expression)
#define NODE_BUFFER_AUDIT() ((void)0)
using KernelChars = JS::UniqueChars;
#endif

namespace builtins::node_compat {
constexpr size_t MaxLength = 16 * 1024 * 1024;
constexpr size_t MaxSourceCodeUnits = 1024 * 1024;

DEF_ERR(InvalidInput, JSEXN_TYPEERR, "Invalid native Buffer kernel input", 0)
DEF_ERR(UnsupportedBacking, JSEXN_ERR, "Shared, resizable or detached Buffer backing is unsupported", 0)
DEF_ERR(AllocationLimit, JSEXN_RANGEERR, "Buffer kernel input exceeds profile allocation limit", 0)

static bool buffer_error(JSContext *cx, const JSErrorFormatString &format, const char *code) {
  api::throw_error(cx, format);
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception)) return false;
  JS_ClearPendingException(cx);
  if (exception.isObject()) {
    JS::RootedObject error(cx, &exception.toObject());
    JS::RootedString code_string(cx, JS_NewStringCopyZ(cx, code));
    if (!code_string) return false;
    JS::RootedValue code_value(cx, JS::StringValue(code_string));
    if (!JS_DefineProperty(cx, error, "code", code_value, JSPROP_ENUMERATE)) return false;
  }
  JS_SetPendingException(cx, exception);
  return false;
}

static void *allocate_staging(JSContext *cx, size_t length) {
  // JS_malloc uses the non-reporting maybe_pod_malloc allocator. Native
  // functions returning false must supply its real OOM exception explicitly.
  void *memory = JS_malloc(cx, length);
  if (!memory) JS_ReportOutOfMemory(cx);
  return memory;
}

static void stress_gc(JSContext *cx) {
#ifdef NODE_COMPAT_GC_STRESS
  // Test builds exercise moving/compacting GC only at rooted boundaries.
  // Never invoke this while a JS byte/string pointer is borrowed.
  JS::PrepareForFullGC(cx);
  JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API);
#else
  (void)cx;
#endif
}

static int hex_nibble(unsigned char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

static bool hex_decode(JSContext *cx, unsigned argc, JS::Value *vp) {
  JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
  NODE_BUFFER_AUDIT();
  if (!args.requireAtLeast(cx, "hexDecode", 1)) return false;
  if (!args[0].isString()) {
    return buffer_error(cx, InvalidInput, "ERR_INVALID_ARG_TYPE");
  }
  JS::RootedString text(cx, args[0].toString());
  const size_t code_units = JS::GetStringLength(text);
  if (code_units > MaxSourceCodeUnits) {
    return buffer_error(cx, AllocationLimit, "ERR_OUT_OF_RANGE");
  }
  stress_gc(cx);
  // This owned encoding is allocated before borrowing the destination pointer.
  // Every accepted digit is ASCII. A non-ASCII UTF-8 prefix is rejected at the
  // same first non-hex position as a UTF-16 scan; no valid later digit is read.
  KernelChars encoded = NODE_BUFFER_OWNED(
      NODE_BUFFER_ALLOC(cx, DecodeUTF8, JS_EncodeStringToUTF8(cx, text)));
  if (!encoded) return false;
  size_t length = 0;
  while (length < code_units / 2 &&
         hex_nibble(static_cast<unsigned char>(encoded[2 * length])) >= 0 &&
         hex_nibble(static_cast<unsigned char>(encoded[2 * length + 1])) >= 0) {
    ++length;
  }
  JS::RootedObject output(cx, NODE_BUFFER_ALLOC(cx, DecodeArray, JS_NewUint8Array(cx, length)));
  if (!output) return false;
  stress_gc(cx);
  {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    uint8_t *bytes = JS_GetUint8ArrayData(output, &shared, nogc);
    MOZ_ASSERT(!shared);
    for (size_t i = 0; i < length; ++i) {
      bytes[i] = (hex_nibble(static_cast<unsigned char>(encoded[2 * i])) << 4) |
                  hex_nibble(static_cast<unsigned char>(encoded[2 * i + 1]));
    }
  }
  stress_gc(cx);
  args.rval().setObject(*output);
  return true;
}

static bool hex_encode(JSContext *cx, unsigned argc, JS::Value *vp) {
  JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
  NODE_BUFFER_AUDIT();
  if (!args.requireAtLeast(cx, "hexEncode", 1)) return false;
  if (!args[0].isObject()) {
    return buffer_error(cx, InvalidInput, "ERR_INVALID_ARG_TYPE");
  }
  JS::RootedObject input(cx, &args[0].toObject());
  size_t length = 0;
  bool shared = false;
  uint8_t *ignored = nullptr;
  if (!JS_GetObjectAsUint8Array(input, &length, &shared, &ignored)) {
    return buffer_error(cx, InvalidInput, "ERR_INVALID_ARG_TYPE");
  }
  if (shared || JS::IsResizableArrayBufferView(input)) {
    return buffer_error(cx, UnsupportedBacking, "ERR_SM_NODE_UNSUPPORTED");
  }
  JS::RootedObject backing(cx, JS_GetArrayBufferViewBuffer(cx, input, &shared));
  if (!backing) return false;
  if (shared || JS::IsDetachedArrayBufferObject(backing)) {
    return buffer_error(cx, UnsupportedBacking, "ERR_SM_NODE_UNSUPPORTED");
  }
  if (length > MaxLength) return buffer_error(cx, AllocationLimit, "ERR_OUT_OF_RANGE");
  // `ignored` is NEVER dereferenced: allocations may have moved its storage.
  // Account for the temporary and final JS string in the benchmark; this
  // conservative template copies once on JS string creation.
  KernelChars output(NODE_BUFFER_OWNED(JS::UniqueChars(static_cast<char *>(
      NODE_BUFFER_ALLOC(cx, EncodeStaging, allocate_staging(cx, length * 2 + 1))))));
  if (!output) return false;
  stress_gc(cx);
  {
    JS::AutoCheckCannotGC nogc(cx);
    const uint8_t *bytes = JS_GetUint8ArrayData(input, &shared, nogc);
    constexpr char alphabet[] = "0123456789abcdef";
    for (size_t i = 0; i < length; ++i) {
      output[2 * i] = alphabet[bytes[i] >> 4];
      output[2 * i + 1] = alphabet[bytes[i] & 15];
    }
  }
  stress_gc(cx);
  output[2 * length] = 0;
  JS::RootedString result(
      cx, NODE_BUFFER_ALLOC(cx, EncodeString, JS_NewStringCopyN(cx, output.get(), length * 2)));
  if (!result) return false;
  stress_gc(cx);
  args.rval().setString(result);
  return true;
}


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

// UNCOMPILED guest kernels. Included literally in the isolated buffer.cpp
// afterimage; no extra translation unit, host service or persistent pointer.
static bool byte_view(JSContext* cx, JS::HandleValue value,
                      JS::MutableHandleObject out, size_t* length) {
  if(!value.isObject())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  out.set(&value.toObject());bool shared=false;uint8_t* ignored=nullptr;
  if(!JS_GetObjectAsUint8Array(out,length,&shared,&ignored))return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  if(shared||JS::IsResizableArrayBufferView(out))return buffer_error(cx,UnsupportedBacking,"ERR_SM_NODE_UNSUPPORTED");
  JS::RootedObject backing(cx,JS_GetArrayBufferViewBuffer(cx,out,&shared));if(!backing)return false;
  if(shared||JS::IsDetachedArrayBufferObject(backing))return buffer_error(cx,UnsupportedBacking,"ERR_SM_NODE_UNSUPPORTED");
  if(*length>MaxLength)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");
  return true;
}
static int base64_digit(char16_t c) {
  // Node decodes the low byte of each UTF-16 code unit. '=' terminates;
  // all other non-alphabet bytes are skipped, including whitespace.
  c &= 255;
  if(c>='A'&&c<='Z')return c-'A';if(c>='a'&&c<='z')return c-'a'+26;
  if(c>='0'&&c<='9')return c-'0'+52;if(c=='+'||c=='-')return 62;
  if(c=='/'||c=='_')return 63;return c=='='?-2:-1;
}
// mode0=base64 (either alphabet),1=latin1/ascii input,2=UTF16LE input.
static bool decode_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
  auto a=JS::CallArgsFromVp(argc,vp);
  if(a.length()<2||!a[0].isString()||!a[1].isInt32())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  const int mode=a[1].toInt32();if(mode<0||mode>2)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  JS::RootedString text(cx,a[0].toString());size_t units=JS::GetStringLength(text);
  if(units>MaxSourceCodeUnits)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");
  JS::UniqueTwoByteChars chars=JS_CopyStringCharsZ(cx,text);if(!chars)return false;
  size_t length=mode==2?units*2:units;
  if(mode==0){size_t digits=0;for(size_t i=0;i<units;i++){int d=base64_digit(chars[i]);if(d==-2)break;if(d>=0)digits++;}length=(digits/4)*3+(digits%4>1?digits%4-1:0);}
  if(length>MaxLength)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");
  JS::RootedObject output(cx,JS_NewUint8Array(cx,length));if(!output)return false;
  {JS::AutoCheckCannotGC nogc(cx);bool shared=false;auto* bytes=JS_GetUint8ArrayData(output,&shared,nogc);MOZ_ASSERT(!shared);
   if(mode==0){uint32_t accum=0;unsigned bits=0;size_t pos=0;for(size_t i=0;i<units;i++){int d=base64_digit(chars[i]);if(d==-2)break;if(d<0)continue;accum=(accum<<6)|static_cast<unsigned>(d);bits+=6;if(bits>=8){bits-=8;bytes[pos++]=static_cast<uint8_t>(accum>>bits);}}MOZ_ASSERT(pos==length);}
   else for(size_t i=0;i<units;i++){bytes[mode==2?i*2:i]=static_cast<uint8_t>(chars[i]);if(mode==2)bytes[i*2+1]=static_cast<uint8_t>(chars[i]>>8);}}
  a.rval().setObject(*output);return true;
}
// mode0=base64,1=base64url,2=latin1,3=ascii,4=UTF16LE.
static bool encode_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
  auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<2||!a[1].isInt32())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  int mode=a[1].toInt32();if(mode<0||mode>4)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
  JS::RootedObject input(cx);size_t n=0;if(!byte_view(cx,a[0],&input,&n))return false;
  size_t count=mode<2?((n+2)/3)*4:mode==4?n/2:n;if(mode==1&&n%3)count-=3-n%3;
  // All allocations complete before reacquiring backing bytes. Native staging
  // survives moving GC; the JS input and backing remain rooted throughout.
  JS::UniqueTwoByteChars text(static_cast<char16_t*>(allocate_staging(cx,(count+1)*sizeof(char16_t))));if(!text)return false;
  {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const auto* bytes=JS_GetUint8ArrayData(input,&shared,nogc);MOZ_ASSERT(!shared);
   if(mode<2){const char* alpha=mode==0?"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/":"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";size_t at=0;
    for(size_t i=0;i<n;i+=3){uint32_t word=uint32_t(bytes[i])<<16;if(i+1<n)word|=uint32_t(bytes[i+1])<<8;if(i+2<n)word|=bytes[i+2];text[at++]=alpha[(word>>18)&63];text[at++]=alpha[(word>>12)&63];if(i+1<n)text[at++]=alpha[(word>>6)&63];else if(mode==0)text[at++]='=';if(i+2<n)text[at++]=alpha[word&63];else if(mode==0)text[at++]='=';}MOZ_ASSERT(at==count);}
   else if(mode==4){for(size_t i=0;i<count;i++)text[i]=char16_t(bytes[i*2])|(char16_t(bytes[i*2+1])<<8);}
   else for(size_t i=0;i<n;i++)text[i]=bytes[i]&(mode==3?127:255);}
  text[count]=0;JS::RootedString result(cx,JS_NewUCStringCopyN(cx,text.get(),count));if(!result)return false;a.rval().setString(result);return true;
}
static bool index_arg(JSContext* cx,JS::HandleValue v,size_t max,size_t* out) {
 if(!v.isNumber()||!std::isfinite(v.toNumber())||v.toNumber()<0||std::floor(v.toNumber())!=v.toNumber()||v.toNumber()>max)return buffer_error(cx,AllocationLimit,"ERR_OUT_OF_RANGE");*out=static_cast<size_t>(v.toNumber());return true;
}
// Source and destination are real visible U8 windows. memmove handles either
// direction of overlapping views on one backing, including nonzero offsets.
static bool copy_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
 auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<5)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");
 JS::RootedObject source(cx),target(cx);size_t sn=0,tn=0,so=0,to=0,n=0;
 if(!byte_view(cx,a[0],&source,&sn)||!byte_view(cx,a[1],&target,&tn)||!index_arg(cx,a[2],sn,&so)||!index_arg(cx,a[3],tn,&to)||!index_arg(cx,a[4],std::min(sn-so,tn-to),&n))return false;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;auto* s=JS_GetUint8ArrayData(source,&shared,nogc);MOZ_ASSERT(!shared);auto* t=JS_GetUint8ArrayData(target,&shared,nogc);MOZ_ASSERT(!shared);if(n)std::memmove(t+to,s+so,n);}
 a.rval().setNumber(n);return true;
}
// Bounded native byte comparison/search; no JS iteration over a payload.
static bool compare_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
 auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<2)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");JS::RootedObject x(cx),y(cx);size_t xn=0,yn=0;if(!byte_view(cx,a[0],&x,&xn)||!byte_view(cx,a[1],&y,&yn))return false;int result=0;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const auto* xp=JS_GetUint8ArrayData(x,&shared,nogc);const auto* yp=JS_GetUint8ArrayData(y,&shared,nogc);size_t n=std::min(xn,yn);int c=n?std::memcmp(xp,yp,n):0;result=c<0?-1:c>0?1:xn<yn?-1:xn>yn?1:0;}
 a.rval().setInt32(result);return true;
}
static bool search_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
 auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<3)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");JS::RootedObject hay(cx),needle(cx);size_t hn=0,nn=0,start=0;if(!byte_view(cx,a[0],&hay,&hn)||!byte_view(cx,a[1],&needle,&nn)||!index_arg(cx,a[2],hn,&start))return false;
 // A finite comparison budget prevents adversarial O(16MiB^2) searches. This
 // refusal is explicit; ordinary multipart needles remain within the budget.
 if(nn&&hn-start>64*1024*1024/nn)return buffer_error(cx,AllocationLimit,"ERR_SM_NODE_LIMIT");double result=-1;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const auto* hp=JS_GetUint8ArrayData(hay,&shared,nogc);const auto* np=JS_GetUint8ArrayData(needle,&shared,nogc);if(!nn)result=start;else if(nn<=hn-start)for(size_t i=start;i<=hn-nn;i++)if(!std::memcmp(hp+i,np,nn)){result=i;break;}}
 a.rval().setNumber(result);return true;
}
static bool fill_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
 auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<4)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");JS::RootedObject target(cx),pattern(cx);size_t tn=0,pn=0,start=0,end=0;if(!byte_view(cx,a[0],&target,&tn)||!byte_view(cx,a[1],&pattern,&pn)||!index_arg(cx,a[2],tn,&start)||!index_arg(cx,a[3],tn,&end))return false;if(end<start||!pn)return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_VALUE");
 // Snapshot pattern before mutating possibly overlapping destination backing.
 JS::UniqueChars saved(static_cast<char*>(allocate_staging(cx,pn)));if(!saved)return false;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const auto* p=JS_GetUint8ArrayData(pattern,&shared,nogc);std::memcpy(saved.get(),p,pn);auto* t=JS_GetUint8ArrayData(target,&shared,nogc);for(size_t i=start;i<end;i++)t[i]=static_cast<uint8_t>(saved[(i-start)%pn]);}
 a.rval().setObject(*target);return true;
}

// Strict Unicode scalar UTF8 validation, including overlongs/surrogates/range.
static bool validate_bytes(JSContext* cx,unsigned argc,JS::Value* vp) {
 auto a=JS::CallArgsFromVp(argc,vp);if(a.length()<2||!a[1].isBoolean())return buffer_error(cx,InvalidInput,"ERR_INVALID_ARG_TYPE");JS::RootedObject input(cx);size_t n=0;if(!byte_view(cx,a[0],&input,&n))return false;bool valid=true;
 {JS::AutoCheckCannotGC nogc(cx);bool shared=false;const auto* p=JS_GetUint8ArrayData(input,&shared,nogc);bool ascii=a[1].toBoolean();
  for(size_t i=0;i<n&&valid;){uint8_t c=p[i++];if(c<128)continue;if(ascii){valid=false;break;}unsigned need=0;uint32_t value=0,min=0;if(c>=0xc2&&c<=0xdf){need=1;value=c&31;min=0x80;}else if(c>=0xe0&&c<=0xef){need=2;value=c&15;min=0x800;}else if(c>=0xf0&&c<=0xf4){need=3;value=c&7;min=0x10000;}else{valid=false;break;}if(need>n-i){valid=false;break;}for(unsigned j=0;j<need;j++){uint8_t d=p[i++];if((d&0xc0)!=0x80){valid=false;break;}value=(value<<6)|(d&63);}if(value<min||value>0x10ffff||(value>=0xd800&&value<=0xdfff))valid=false;}}
 a.rval().setBoolean(valid);return true;
}
JSObject *create_kernel(JSContext *cx) {
  JS::RootedObject result(cx, JS_NewPlainObject(cx));
  if (!result) return nullptr;
  static const JSFunctionSpec functions[] = {
    JS_FN("hexEncode", hex_encode, 1, JSPROP_ENUMERATE),
    JS_FN("hexDecode", hex_decode, 1, JSPROP_ENUMERATE),
    JS_FN("concat", concat_bytes, 2, JSPROP_ENUMERATE),
    JS_FN("decode", decode_bytes, 2, JSPROP_ENUMERATE),
    JS_FN("encode", encode_bytes, 2, JSPROP_ENUMERATE),
    JS_FN("copy", copy_bytes, 5, JSPROP_ENUMERATE),
    JS_FN("compare", compare_bytes, 2, JSPROP_ENUMERATE),
    JS_FN("search", search_bytes, 3, JSPROP_ENUMERATE),
    JS_FN("fill", fill_bytes, 4, JSPROP_ENUMERATE),
    JS_FN("validate", validate_bytes, 2, JSPROP_ENUMERATE),
    JS_FS_END,
  };
  if (!JS_DefineFunctions(cx, result, functions)) return nullptr;
  return result;
}
} // namespace builtins::node_compat
