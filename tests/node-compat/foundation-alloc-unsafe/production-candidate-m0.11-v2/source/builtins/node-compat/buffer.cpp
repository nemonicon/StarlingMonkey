// Native guest byte kernels for the bounded Node v22.14.0 profile.
#include "builtin.h"
#include "js/CharacterEncoding.h"
#include "js/ErrorReport.h"
#include "js/GCAPI.h"
#include "js/MemoryFunctions.h"

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

JSObject *create_kernel(JSContext *cx) {
  JS::RootedObject result(cx, JS_NewPlainObject(cx));
  if (!result) return nullptr;
  static const JSFunctionSpec functions[] = {
    JS_FN("hexEncode", hex_encode, 1, JSPROP_ENUMERATE),
    JS_FN("hexDecode", hex_decode, 1, JSPROP_ENUMERATE),
    JS_FS_END,
  };
  if (!JS_DefineFunctions(cx, result, functions)) return nullptr;
  return result;
}
} // namespace builtins::node_compat
