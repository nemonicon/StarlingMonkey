// UNINSTALLED JSAPI proposal. No registry, CMake, public module or host imports.
// Input is staged; malloc-owned codec output is copied into JS-owned storage.
#include "builtin.h"
#include "js/ErrorReport.h"
#include "js/MemoryFunctions.h"
#include "../bounded-zlib.template.h"

#include <cmath>
#include <cstring>

namespace builtins::node_compat::zlib_jsapi_candidate {
namespace codec = node_compat_zlib_candidate;

DEF_ERR(InvalidArgument, JSEXN_TYPEERR, "Invalid bounded zlib kernel argument", 0)
DEF_ERR(InvalidRange, JSEXN_RANGEERR, "Invalid bounded zlib kernel range", 0)
DEF_ERR(UnsupportedBacking, JSEXN_ERR, "Shared, resizable or detached zlib input is unsupported", 0)
DEF_ERR(InputLimit, JSEXN_RANGEERR, "Zlib input exceeds the 1 MiB profile limit", 0)
DEF_ERR(OutputLimit, JSEXN_RANGEERR, "Zlib output exceeds the selected profile limit", 0)
DEF_ERR(InvalidData, JSEXN_ERR, "Invalid compressed data", 0)
DEF_ERR(IncompleteData, JSEXN_ERR, "Unexpected end of compressed input", 0)
DEF_ERR(NeedsDictionary, JSEXN_ERR, "Zlib dictionaries are not supported by this profile", 0)
DEF_ERR(TrailingData, JSEXN_ERR, "Multiple compressed members or trailing data are unsupported", 0)
DEF_ERR(InternalFailure, JSEXN_ERR, "Bounded zlib operation failed", 0)

static bool string_property(JSContext *cx, JS::HandleObject object,
                            const char *name, const char *text) {
  JS::RootedString string(cx, JS_NewStringCopyZ(cx, text));
  if (!string) return false;
  JS::RootedValue value(cx, JS::StringValue(string));
  return JS_DefineProperty(cx, object, name, value, JSPROP_ENUMERATE);
}

static bool fail(JSContext *cx, const JSErrorFormatString &format,
                 const char *code, int status = Z_OK) {
  api::throw_error(cx, format);
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception)) return false;
  JS_ClearPendingException(cx);
  if (exception.isObject()) {
    JS::RootedObject error(cx, &exception.toObject());
    if (!string_property(cx, error, "code", code) ||
        !string_property(cx, error, "module", "node:zlib") ||
        !string_property(cx, error, "profile", "sm-node-22.14.0-zlib-jsapi-template-v1"))
      return false;
    JS::RootedValue number(cx, JS::Int32Value(status));
    if (!JS_DefineProperty(cx, error, "errno", number, JSPROP_ENUMERATE)) return false;
  }
  JS_SetPendingException(cx, exception);
  return false;
}

static bool codec_failure(JSContext *cx, const codec::Result &result) {
  switch (result.status) {
  case codec::Status::OutOfMemory:
    JS_ReportOutOfMemory(cx);
    return false;
  case codec::Status::InputLimit:
    return fail(cx, InputLimit, "ERR_OUT_OF_RANGE", result.zlib_status);
  case codec::Status::OutputLimit:
    return fail(cx, OutputLimit, "ERR_BUFFER_TOO_LARGE", result.zlib_status);
  case codec::Status::InvalidData:
    return fail(cx, InvalidData, "Z_DATA_ERROR", result.zlib_status);
  case codec::Status::IncompleteData:
    return fail(cx, IncompleteData, "Z_BUF_ERROR", result.zlib_status);
  case codec::Status::DictionaryRequired:
    return fail(cx, NeedsDictionary, "ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED", result.zlib_status);
  case codec::Status::TrailingData:
    return fail(cx, TrailingData, "ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED", result.zlib_status);
  case codec::Status::InternalError:
  case codec::Status::Ok: // Caller must not use this error path for success.
    return fail(cx, InternalFailure, "ERR_SM_ZLIB_INTERNAL", result.zlib_status);
  }
  return fail(cx, InternalFailure, "ERR_SM_ZLIB_INTERNAL", result.zlib_status);
}

// Private factory contract only: run(Uint8Array, format 0|1|2, encode:boolean,
// outputLimit:integer). The future public facade must normalize strings/views
// and validate observable options before invoking this function.
static bool run(JSContext *cx, unsigned argc, JS::Value *vp) {
  JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, "boundedZlibRun", 4)) return false;
  if (!args[0].isObject() || !args[1].isInt32() || !args[2].isBoolean() ||
      !args[3].isNumber())
    return fail(cx, InvalidArgument, "ERR_INVALID_ARG_TYPE");
  const int format_value = args[1].toInt32();
  const double limit_value = args[3].toNumber();
  if (format_value < 0 || format_value > 2 || !std::isfinite(limit_value) ||
      limit_value < 0 || std::floor(limit_value) != limit_value ||
      limit_value > codec::MaxOutput)
    return fail(cx, InvalidRange, "ERR_OUT_OF_RANGE");
  const auto format = format_value == 0 ? codec::Format::Zlib :
                      format_value == 1 ? codec::Format::Gzip : codec::Format::Raw;
  JS::RootedObject input(cx, &args[0].toObject());
  size_t length = 0;
  bool shared = false;
  uint8_t *ignored = nullptr;
  if (!JS_GetObjectAsUint8Array(input, &length, &shared, &ignored))
    return fail(cx, InvalidArgument, "ERR_INVALID_ARG_TYPE");
  if (shared || JS::IsResizableArrayBufferView(input))
    return fail(cx, UnsupportedBacking, "ERR_SM_NODE_UNSUPPORTED");
  JS::RootedObject backing(cx, JS_GetArrayBufferViewBuffer(cx, input, &shared));
  if (!backing) return false;
  if (shared || JS::IsDetachedArrayBufferObject(backing))
    return fail(cx, UnsupportedBacking, "ERR_SM_NODE_UNSUPPORTED");
  if (length > codec::MaxInput) return fail(cx, InputLimit, "ERR_OUT_OF_RANGE");

  // Allocate before borrowing. The earlier pointer is deliberately ignored.
  JS::UniqueChars staging;
  if (length) {
    staging.reset(static_cast<char *>(JS_malloc(cx, length)));
    if (!staging) {
      JS_ReportOutOfMemory(cx);
      return false;
    }
  }
  bool changed = false;
  {
    JS::AutoCheckCannotGC no_gc(cx);
    size_t current_length = 0;
    bool current_shared = false;
    uint8_t *bytes = nullptr;
    changed = !JS_GetObjectAsUint8Array(input, &current_length, &current_shared, &bytes) ||
              current_shared || current_length != length ||
              JS::IsDetachedArrayBufferObject(backing) || (length && !bytes);
    if (!changed && length) std::memcpy(staging.get(), bytes, length);
  }
  if (changed) return fail(cx, UnsupportedBacking, "ERR_SM_NODE_UNSUPPORTED");

  auto result = codec::run(
      {reinterpret_cast<const uint8_t *>(staging.get()), length}, format,
      args[2].toBoolean(), static_cast<size_t>(limit_value));
  if (result.status != codec::Status::Ok) return codec_failure(cx, result);

  // Result bytes use malloc/free; JS storage uses SpiderMonkey's allocator.
  // One explicit copy avoids an unsupported cross-allocator ownership transfer.
  const auto bytes = result.output.view();
  JS::RootedObject output(cx, JS_NewUint8Array(cx, bytes.size()));
  if (!output) return false;
  if (!bytes.empty()) {
    JS::AutoCheckCannotGC no_gc(cx);
    bool output_shared = false;
    uint8_t *destination = JS_GetUint8ArrayData(output, &output_shared, no_gc);
    std::memcpy(destination, bytes.data(), bytes.size());
  }
  args.rval().setObject(*output);
  return true;
}

JSObject *create_kernel(JSContext *cx) {
  JS::RootedObject object(cx, JS_NewPlainObject(cx));
  if (!object) return nullptr;
  static const JSFunctionSpec functions[] = {
    JS_FN("run", run, 4, JSPROP_ENUMERATE),
    JS_FS_END,
  };
  if (!JS_DefineFunctions(cx, object, functions)) return nullptr;
  return object;
}
} // namespace builtins::node_compat::zlib_jsapi_candidate
