#include "blob.h"
#include "file.h"
#include "builtin.h"
#include "encode.h"
#include "rust-encoding.h"
#include "streams/buf-reader.h"
#include "streams/native-stream-source.h"

#include "js/UniquePtr.h"
#include "js/ArrayBuffer.h"
#include "js/ArrayBufferMaybeShared.h"
#include "js/MemoryFunctions.h"
#include "js/SharedArrayBuffer.h"
#include "js/Conversions.h"
#include "js/experimental/TypedData.h"
#include "js/TypeDecls.h"
#include "js/Value.h"

#include <cstddef>
#include <limits>

namespace {

template <typename T> bool validate_type(T *chars, size_t strlen) {
  for (size_t i = 0; i < strlen; i++) {
    T c = chars[i];
    if (c < 0x20 || c > 0x7E) {
      return false;
    }
  }

  return true;
}


// https://w3c.github.io/FileAPI/#convert-line-endings-to-native
std::string convert_line_endings_to_native(std::string_view s) {
  std::string native_line_ending = "\n";
#ifdef _WIN32
  native_line_ending = "\r\n";
#endif

  std::string result;
  result.reserve(s.size());

  size_t i = 0;
  while (i < s.size()) {
    switch (s[i]) {
    case '\r': {
      if (i + 1 < s.size() && s[i + 1] == '\n') {
        result.append(native_line_ending);
        i += 2;
      } else {
        result.append(native_line_ending);
        i += 1;
      }
      break;
    }
    case '\n': {
      result.append(native_line_ending);
      i += 1;
      break;
    }
    default: {
      result.push_back(s[i]);
      i += 1;
      break;
    }
    }
  }

  return result;
}

} // anonymous namespace



namespace builtins::web::blob {

// https://w3c.github.io/FileAPI/#dfn-type
// 1. If type contains any characters outside the range U+0020 to U+007E, then set t to the empty string.
// 2. Convert every character in type to ASCII lowercase.
JSString *Blob::normalize_type(JSContext *cx, JS::HandleValue value) {
  JS::RootedString value_str(cx);

  if (value.isObject() || value.isString()) {
    value_str = JS::ToString(cx, value);
    if (!value_str) {
      return nullptr;
    }
  } else if (value.isNull()) {
    return JS::ToString(cx, value);
  } else {
    return JS_GetEmptyString(cx);
  }

  auto *str = JS::StringToLinearString(cx, value_str);
  if (!str) {
    return nullptr;
  }

  std::string normalized;
  auto strlen = JS::GetLinearStringLength(str);

  if (strlen == 0U) {
    return JS_GetEmptyString(cx);
  }

  if (JS::LinearStringHasLatin1Chars(str)) {
    JS::AutoCheckCannotGC nogc(cx);
    const auto *chars = JS::GetLatin1LinearStringChars(nogc, str);
    if (!validate_type(chars, strlen)) {
      return JS_GetEmptyString(cx);
    }
    normalized = std::string(reinterpret_cast<const char *>(chars), strlen);
  } else {
    JS::AutoCheckCannotGC nogc(cx);
    const auto *chars = JS::GetTwoByteLinearStringChars(nogc, str);
    if (!validate_type(chars, strlen)) {
      return JS_GetEmptyString(cx);
    }
    normalized.reserve(strlen);
    for (size_t i = 0; i < strlen; ++i) {
      normalized += static_cast<unsigned char>(chars[i]);
    }
  }

  std::transform(normalized.begin(), normalized.end(), normalized.begin(),
                 [](unsigned char c) { return std::tolower(c); });

  return JS_NewStringCopyN(cx, normalized.c_str(), normalized.length());
}

using js::Vector;
using streams::BufReader;
using streams::NativeStreamSource;

namespace {

void report_oom_unless_pending(JSContext *cx) {
  if (!JS_IsExceptionPending(cx)) {
    JS_ReportOutOfMemory(cx);
  }
}

// Keep every native pointer range representable. This is a native guest bound,
// not an assertion of arbitrary-size Web/Node Blob compatibility.
constexpr size_t MAX_NATIVE_BLOB_BYTES =
    static_cast<size_t>(std::numeric_limits<std::ptrdiff_t>::max());

bool reserve_append(JSContext *cx, Blob::ByteBuffer *target, size_t additional) {
  if (target->length() > MAX_NATIVE_BLOB_BYTES ||
      additional > MAX_NATIVE_BLOB_BYTES - target->length()) {
    JS_ReportAllocationOverflow(cx);
    return false;
  }
  if (additional != 0 && !target->reserve(target->length() + additional)) {
    // SystemAllocPolicy performs no JS exception reporting.
    report_oom_unless_pending(cx);
    return false;
  }
  return true;
}

bool require_blob(JSContext *cx, HandleObject self, const char *operation) {
  if (!Blob::is_instance(self)) {
    return api::throw_error(cx, api::Errors::WrongReceiver, operation, "Blob");
  }
  return true;
}

} // namespace

#define DEFINE_BLOB_METHOD(name)                               \
bool Blob::name(JSContext *cx, unsigned argc, JS::Value *vp) { \
  METHOD_HEADER(0)                                             \
  return name(cx, self, args.rval());                          \
}

#define DEFINE_BLOB_METHOD_W_ARGS(name)                        \
bool Blob::name(JSContext *cx, unsigned argc, JS::Value *vp) { \
  METHOD_HEADER(0)                                             \
  return name(cx, self, args, args.rval());                    \
}

#define DEFINE_BLOB_PROMISE_METHOD(name)                        \
bool Blob::name(JSContext *cx, unsigned argc, JS::Value *vp) {   \
  TRACE_METHOD(#name)                                          \
  CallArgs args = CallArgsFromVp(argc, vp);                     \
  if (!check_receiver(cx, args.thisv(), #name))                 \
    return ReturnPromiseRejectedWithPendingError(cx, args);     \
  RootedObject self(cx, &args.thisv().toObject());              \
  return name(cx, self, args.rval());                           \
}

const JSFunctionSpec Blob::static_methods[] = {
    JS_FS_END,
};

const JSPropertySpec Blob::static_properties[] = {
    JS_PS_END,
};

const JSFunctionSpec Blob::methods[] = {
    JS_FN("arrayBuffer", Blob::arrayBuffer, 0, JSPROP_ENUMERATE),
    JS_FN("bytes", Blob::bytes, 0, JSPROP_ENUMERATE),
    JS_FN("slice", Blob::slice, 0, JSPROP_ENUMERATE),
    JS_FN("stream", Blob::stream, 0, JSPROP_ENUMERATE),
    JS_FN("text", Blob::text, 0, JSPROP_ENUMERATE),
    JS_FS_END,
};

const JSPropertySpec Blob::properties[] = {
    JS_PSG("size", size_get, JSPROP_ENUMERATE),
    JS_PSG("type", type_get, JSPROP_ENUMERATE),
    JS_STRING_SYM_PS(toStringTag, "Blob", JSPROP_READONLY),
    JS_PS_END,
};

JSObject *Blob::data_to_owned_array_buffer(JSContext *cx, HandleObject self) {
  if (!require_blob(cx, self, "arrayBuffer")) {
    return nullptr;
  }
  const size_t size = Blob::blob_size(self);
  // Allocate owned JS storage before acquiring its data. Rooted self keeps its
  // native vector alive through allocation/GC; that vector is not GC-movable.
  RootedObject array_buffer(cx, JS::NewArrayBuffer(cx, size));
  if (!array_buffer) {
    return nullptr;
  }
  bool invalid = false;
  if (size != 0) {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    auto *destination = JS::GetArrayBufferData(array_buffer, &shared, nogc);
    auto *source = Blob::blob(self);
    invalid = shared || !destination || source->length() != size;
    if (!invalid) {
      std::copy_n(source->begin(), size, destination);
    }
  }
  if (invalid) {
    api::throw_error(cx, api::Errors::TypeError, "Blob.arrayBuffer", "storage",
                     "remain an owned unshared buffer");
    return nullptr;
  }
  return array_buffer;
}

bool Blob::read_blob_slice(JSContext *cx, HandleObject self, std::span<uint8_t> buf,
                           size_t start, size_t *read, bool *done) {
  auto *src = Blob::blob(self);

  if (start >= src->length()) {
    *read = 0;
    *done = true;
    return true;
  }

  size_t available = src->length() - start;
  size_t to_read = std::min(buf.size(), available);

  std::copy_n(src->begin() + start, to_read, buf.data());
  *read = to_read;

 return true;
}

DEFINE_BLOB_PROMISE_METHOD(arrayBuffer)
DEFINE_BLOB_PROMISE_METHOD(bytes)
DEFINE_BLOB_METHOD(stream)
DEFINE_BLOB_PROMISE_METHOD(text)
DEFINE_BLOB_METHOD_W_ARGS(slice)

bool Blob::arrayBuffer(JSContext *cx, HandleObject self, MutableHandleValue rval) {
  if (!require_blob(cx, self, "arrayBuffer")) return false;
  JS::RootedObject promise(cx, JS::NewPromiseObject(cx, nullptr));
  if (!promise) {
    return false;
  }

  rval.setObject(*promise);

  JS::RootedObject buffer(cx, data_to_owned_array_buffer(cx, self));
  if (!buffer) {
    return RejectPromiseWithPendingError(cx, promise);
  }

  JS::RootedValue result(cx);
  result.setObject(*buffer);
  return JS::ResolvePromise(cx, promise, result);
}

bool Blob::bytes(JSContext *cx, HandleObject self, MutableHandleValue rval) {
  if (!require_blob(cx, self, "bytes")) return false;
  JS::RootedObject promise(cx, JS::NewPromiseObject(cx, nullptr));
  if (!promise) {
    return false;
  }

  rval.setObject(*promise);

  JS::RootedObject buffer(cx, data_to_owned_array_buffer(cx, self));
  if (!buffer) {
    return RejectPromiseWithPendingError(cx, promise);
  }

  auto len = JS::GetArrayBufferByteLength(buffer);
  JS::RootedObject byte_array(cx, JS_NewUint8ArrayWithBuffer(cx, buffer, 0, len));
  if (!byte_array) {
    return RejectPromiseWithPendingError(cx, promise);
  }

  JS::RootedValue result(cx);
  result.setObject(*byte_array);
  return JS::ResolvePromise(cx, promise, result);
}

bool Blob::slice(JSContext *cx, HandleObject self, const CallArgs &args, MutableHandleValue rval) {
  if (!require_blob(cx, self, "slice")) return false;
  const int64_t size = Blob::blob_size(self);
  int64_t start = 0;
  int64_t end = size;

  JS::RootedString contentType(cx, JS_GetEmptyString(cx));

  if (args.hasDefined(0)) {
    HandleValue start_val = args.get(0);
    if (!JS::ToInt64(cx, start_val, &start)) {
      return false;
    }
  }

  if (args.hasDefined(1)) {
    HandleValue end_val = args.get(1);
    if (!JS::ToInt64(cx, end_val, &end)) {
      return false;
    }
  }

  if (args.hasDefined(2)) {
    HandleValue contentType_val = args.get(2);
    if ((contentType = Blob::normalize_type(cx, contentType_val)) == nullptr) {
      return false;
    }
  }

  // A negative value is treated as an offset from the end of the Blob toward the beginning.
  start = (start < 0) ? std::max((size + start), 0LL) : std::min(start, size);
  end = (end < 0) ? std::max((size + end), 0LL) : std::min(end, size);

  const size_t slice_len = static_cast<size_t>(std::max(end - start, 0LL));
  UniqueChars dst;
  if (slice_len != 0) {
    dst.reset(static_cast<char *>(JS_malloc(cx, slice_len)));
    if (!dst) {
      report_oom_unless_pending(cx);
      return false;
    }
    // Reacquire after argument conversions and allocation. Source is immutable
    // native storage owned by rooted self, not a borrowed JS byte span.
    auto *src = Blob::blob(self);
    std::copy_n(src->begin() + start, slice_len, dst.get());
  }

  JS::RootedObject new_blob(cx, create(cx, std::move(dst), slice_len, contentType));
  if (!new_blob) {
    return false;
  }

  rval.setObject(*new_blob);
  return true;
}

bool Blob::stream(JSContext *cx, HandleObject self, MutableHandleValue rval) {
  if (!require_blob(cx, self, "stream")) return false;
  RootedObject reader(cx, BufReader::create(cx, self, read_blob_slice));
  if (!reader) {
    return false;
  }

  RootedObject native_stream(cx, BufReader::stream(reader));
  RootedObject default_stream(cx, NativeStreamSource::stream(native_stream));

  rval.setObject(*default_stream);
  return true;
}

bool Blob::text(JSContext *cx, HandleObject self, MutableHandleValue rval) {
  if (!require_blob(cx, self, "text")) return false;
  JS::RootedObject promise(cx, JS::NewPromiseObject(cx, nullptr));
  if (!promise) {
    return false;
  }

  rval.setObject(*promise);

  const size_t source_length = Blob::blob_size(self);
  if (source_length == 0) {
    JS::RootedValue result(cx, JS_GetEmptyStringValue(cx));
    return JS::ResolvePromise(cx, promise, result);
  }

  const char* utf8_label = "UTF-8";
  const auto *encoding =
      jsencoding::encoding_for_label_no_replacement(reinterpret_cast<const uint8_t *>(utf8_label), 5);

  auto deleter = [&](jsencoding::Decoder *dec) { jsencoding::decoder_free(dec); };
  std::unique_ptr<jsencoding::Decoder, decltype(deleter)> decoder(
      jsencoding::encoding_new_decoder_with_bom_removal(encoding), deleter);

  // The current Rust allocation API is not proven fallible. This null guard
  // does not turn a Rust allocator abort into a catchable JS OOM.
  if (!decoder) {
    report_oom_unless_pending(cx);
    return RejectPromiseWithPendingError(cx, promise);
  }
  const size_t maximum = jsencoding::decoder_max_utf16_buffer_length(decoder.get(), source_length);
  const size_t capacity = std::max(maximum, size_t{2});
  if (capacity > std::numeric_limits<size_t>::max() / sizeof(char16_t)) {
    JS_ReportAllocationOverflow(cx);
    return RejectPromiseWithPendingError(cx, promise);
  }
  // The pinned public allocator contract explicitly covers JS_NewUCString.
  JS::UniqueTwoByteChars dst(static_cast<char16_t *>(
      JS_string_malloc(cx, capacity * sizeof(char16_t))));
  if (!dst) {
    report_oom_unless_pending(cx);
    return RejectPromiseWithPendingError(cx, promise);
  }
  size_t consumed = source_length;
  size_t written = capacity;
  bool had_replacements = false;
  // Rooted Blob owns immutable native input; these are not GC-managed data
  // pointers. The synchronous decoder consumes them before any JS allocation.
  auto *src = Blob::blob(self);
  const uint32_t status = jsencoding::decoder_decode_to_utf16(
      decoder.get(), src->begin(), &consumed, reinterpret_cast<uint16_t *>(dst.get()),
      &written, true, &had_replacements);
  if (status != jsencoding::INPUT_EMPTY || consumed != source_length || written > capacity) {
    api::throw_error(cx, api::Errors::TypeError, "Blob.text", "UTF-8 data",
                     "decode completely within the checked output allocation");
    return RejectPromiseWithPendingError(cx, promise);
  }
  JS::RootedString str(cx, JS_NewUCString(cx, std::move(dst), written));
  if (!str) {
    return RejectPromiseWithPendingError(cx, promise);
  }

  JS::RootedValue result(cx);
  result.setString(str);
  return JS::ResolvePromise(cx, promise, result);
}

bool Blob::size_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);
  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "size get", "Blob");
  }

  auto size = Blob::blob_size(self);
  args.rval().setNumber(size);
  return true;
}

bool Blob::type_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);
  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "type get", "Blob");
  }

  auto *type = Blob::type(self);
  args.rval().setString(type);
  return true;
}

bool Blob::is_instance(const JSObject *obj) {
  if (!BuiltinImpl<Blob, FinalizableClassPolicy>::is_instance(obj)) {
    return false;
  }
  return JS::GetMaybePtrFromReservedSlot<ByteBuffer>(
      const_cast<JSObject *>(obj), std::to_underlying(Slots::Data)) != nullptr;
}

bool Blob::is_instance(Value value) {
  return value.isObject() && is_instance(&value.toObject());
}

Blob::ByteBuffer *Blob::blob(JSObject *self) {
  MOZ_ASSERT(is_instance(self));
  return JS::GetMaybePtrFromReservedSlot<ByteBuffer>(self, std::to_underlying(Slots::Data));
}

size_t Blob::blob_size(JSObject *self) {
  return blob(self)->length();
}

JSString *Blob::type(JSObject *self) {
  MOZ_ASSERT(is_instance(self));
  return JS::GetReservedSlot(self, static_cast<size_t>(Blob::Slots::Type)).toString();
}

Blob::LineEndings Blob::line_endings(JSObject *self) {
  MOZ_ASSERT(is_instance(self));
  return static_cast<LineEndings>(
      JS::GetReservedSlot(self, static_cast<size_t>(Blob::Slots::Endings)).toInt32());
}

bool Blob::append_value(JSContext *cx, HandleObject self, HandleValue val) {
  if (!require_blob(cx, self, "Blob constructor")) return false;
  auto *blob = Blob::blob(self);

  if (val.isObject()) {
    RootedObject obj(cx, &val.toObject());

    if (Blob::is_instance(obj)) {
      const size_t length = Blob::blob_size(obj);
      if (!reserve_append(cx, blob, length)) return false;
      if (length != 0) {
        // Reserve may move target data, so reacquire even for a hypothetical
        // internal self-append. Both vectors are native and rooted owners live.
        auto *src = Blob::blob(obj);
        blob->infallibleAppend(src->begin(), length);
      }
      return true;
    }
    if (JS::IsSharedArrayBufferObject(obj)) {
      return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts",
                              "use unshared ArrayBuffer storage");
    }
    const bool is_view = JS_IsArrayBufferViewObject(obj);
    if (is_view || JS::IsArrayBufferObject(obj)) {
      // Materialize/root backing before any raw borrow. This API can allocate.
      bool shared = false;
      RootedObject backing(cx, is_view ? JS_GetArrayBufferViewBuffer(cx, obj, &shared)
                                      : obj.get());
      if (!backing) return false;
      if (shared || !JS::IsArrayBufferObject(backing)) {
        return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts",
                                "use unshared ArrayBuffer storage");
      }
      // Explicit conservative policy; no atomic shared snapshot, resizable or
      // detached overload is advertised by this candidate.
      if (JS::IsResizableArrayBufferMaybeShared(backing) ||
          JS::IsDetachedArrayBufferObject(backing)) {
        return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts",
                                "use fixed attached ArrayBuffer storage");
      }
      const size_t length = is_view ? JS_GetArrayBufferViewByteLength(obj)
                                    : JS::GetArrayBufferByteLength(obj);
      if (!reserve_append(cx, blob, length)) return false;
      bool invalid = false;
      if (length != 0) {
        JS::AutoCheckCannotGC nogc(cx);
        const size_t current_length = is_view ? JS_GetArrayBufferViewByteLength(obj)
                                              : JS::GetArrayBufferByteLength(obj);
        const auto *data = is_view
            ? static_cast<const uint8_t *>(JS_GetArrayBufferViewData(obj, &shared, nogc))
            : JS::GetArrayBufferData(obj, &shared, nogc);
        invalid = shared || !data || current_length != length;
        if (!invalid) {
          // Guaranteed no allocation: capacity was reserved before the borrow.
          blob->infallibleAppend(data, length);
        }
      }
      if (invalid) {
        return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts",
                                "remain fixed attached unshared storage");
      }
      return true;
    }
  } else if (val.isString()) {
    auto chars = core::encode(cx, val);
    if (!chars) {
      return false;
    }

    if (line_endings(self) == LineEndings::Native) {
      auto converted = convert_line_endings_to_native(chars);
      auto *src = converted.data();
      auto len = converted.length();
      if (!reserve_append(cx, blob, len)) return false;
      if (len != 0) blob->infallibleAppend(src, len);
      return true;
    }
    if (!reserve_append(cx, blob, chars.len)) return false;
    if (chars.len != 0) blob->infallibleAppend(chars.ptr.get(), chars.len);
    return true;
  }

  // FALLBACK: if we ever get here convert, to string and call append again
  RootedString str(cx, JS::ToString(cx, val));
  if (!str) {
    return false;
  }

  RootedValue str_val(cx, JS::StringValue(str));
  return append_value(cx, self, str_val);
}

bool Blob::init_blob_parts(JSContext *cx, HandleObject self, HandleValue value) {
  JS::ForOfIterator it(cx);
  if (!it.init(value, JS::ForOfIterator::AllowNonIterable)) {
    return false;
  }

  bool is_iterable = value.isObject() && it.valueIsIterable();

  if (is_iterable) {
    // if the object is an iterable, walk over its elements...
    JS::Rooted<JS::Value> item(cx);
    while (true) {
      bool done = false;

      if (!it.next(&item, &done)) {
        return false;
      }
      if (done) {
        break;
      }

      if (!append_value(cx, self, item)) {
        // Append/conversion failures happen in the loop body, not next(). The
        // public closeThrow API preserves throw-completion error precedence.
        it.closeThrow();
        return false;
      }
    }

    return true;
  }
  // non-objects are not allowed for the blobParts
  return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts", "be an object");
}

bool Blob::init_options(JSContext *cx, HandleObject self, HandleValue initv) {
  JS::RootedValue init_val(cx, initv);

  if (!init_val.isObject()) {
    return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "options", "be an object");
  }

  // `options` is an object which may specify any of the properties:
  // - `type`: the MIME type of the data that will be stored into the blob,
  // - `endings`: how to interpret newline characters (\n) within the contents.
  JS::RootedObject opts(cx, init_val.toObjectOrNull());
  bool has_endings = false;
  bool has_type = false;

  if (!JS_HasProperty(cx, opts, "endings", &has_endings) ||
      !JS_HasProperty(cx, opts, "type", &has_type)) {
    return false;
  }

  if (!has_type && !has_endings) {
    // Use defaults
    return true;
  }

  if (has_endings) {
    JS::RootedValue endings_val(cx);
    bool is_transparent = false;
    bool is_native = false;
    if (!JS_GetProperty(cx, opts, "endings", &endings_val)) {
      return false;
    }

    RootedString endings_str(cx, JS::ToString(cx, endings_val));
    if (!endings_str) return false;
    if (!JS_StringEqualsLiteral(cx, endings_str, "transparent", &is_transparent) ||
        !JS_StringEqualsLiteral(cx, endings_str, "native", &is_native)) {
      return false;
    }

    if (is_transparent || is_native) {
      auto endings = is_native ? LineEndings::Native : LineEndings::Transparent;
      SetReservedSlot(self, std::to_underlying(Slots::Endings), JS::Int32Value(std::to_underlying(endings)));
    }
  }

  if (has_type) {
    JS::RootedValue type(cx);
    if (!JS_GetProperty(cx, opts, "type", &type)) {
      return false;
    }

    auto *type_str = Blob::normalize_type(cx, type);
    if (!type_str) {
      return false;
    }
    SetReservedSlot(self, std::to_underlying(Slots::Type), JS::StringValue(type_str));
  }

  return true;
}

JSObject *Blob::create(JSContext *cx, UniqueChars data, size_t data_len, HandleString type) {
  if (data_len > MAX_NATIVE_BLOB_BYTES) {
    JS_ReportAllocationOverflow(cx);
    return nullptr;
  }
  if (data_len != 0 && !data) {
    report_oom_unless_pending(cx);
    return nullptr;
  }
  if (!type.get()) {
    report_oom_unless_pending(cx);
    return nullptr;
  }
  RootedObject self(cx, JS_NewObjectWithGivenProto(cx, &class_, proto_obj));
  if (!self) {
    return nullptr;
  }

  // Publish the pointer last. Data stays undefined on allocation failure, so
  // prototype/partial-constructor finalizers never read an invalid private slot.
  SetReservedSlot(self, std::to_underlying(Slots::Type), JS::StringValue(type));
  SetReservedSlot(self, std::to_underlying(Slots::Endings), JS::Int32Value(std::to_underlying(LineEndings::Transparent)));
  auto blob = js::MakeUnique<ByteBuffer>();
  if (!blob) {
    JS_ReportOutOfMemory(cx);
    return nullptr;
  }

  if (data_len != 0) {
    // UniqueChars and SystemAllocPolicy both use JS-compatible free policy.
    blob->replaceRawBuffer(reinterpret_cast<uint8_t *>(data.release()), data_len);
  }

  SetReservedSlot(self, std::to_underlying(Slots::Data), JS::PrivateValue(blob.release()));
  return self;
}

bool Blob::init(JSContext *cx, HandleObject self, HandleValue blobParts, HandleValue opts) {
  if (blobParts.isNull()) {
    return api::throw_error(cx, api::Errors::TypeError, "Blob.constructor", "blobParts", "be an object");
  }
  MOZ_ASSERT(JS::GetReservedSlot(self, std::to_underlying(Slots::Data)).isUndefined());
  SetReservedSlot(self, std::to_underlying(Slots::Type), JS_GetEmptyStringValue(cx));
  SetReservedSlot(self, std::to_underlying(Slots::Endings), JS::Int32Value(std::to_underlying(LineEndings::Transparent)));
  auto blob = js::MakeUnique<ByteBuffer>();
  if (blob == nullptr) {
    JS_ReportOutOfMemory(cx);
    return false;
  }

  SetReservedSlot(self, std::to_underlying(Slots::Data), JS::PrivateValue(blob.release()));

  // Walk the blob parts and append them to the blob's buffer.
  if (!blobParts.isUndefined() && !init_blob_parts(cx, self, blobParts)) {
    return false;
  }

  if (!opts.isNullOrUndefined() && !init_options(cx, self, opts)) {
    return false;
  }

  return true;
}

bool Blob::constructor(JSContext *cx, unsigned argc, JS::Value *vp) {
  CTOR_HEADER("Blob", 0);

  RootedValue blobParts(cx, args.get(0));
  RootedValue opts(cx, args.get(1));
  RootedObject self(cx, JS_NewObjectForConstructor(cx, &class_, args));

  if (!self) {
    return false;
  }

  if (!init(cx, self, blobParts, opts)) {
    return false;
  }

  args.rval().setObject(*self);
  return true;
}

bool Blob::init_class(JSContext *cx, JS::HandleObject global) {
  return init_class_impl(cx, global);
}

void Blob::finalize(JS::GCContext *gcx, JSObject *self) {
  // Finalization can run off-thread. Do not consult the mutable subclass
  // registry or invoke receiver guards/getters here; the JSClass hook selects
  // this cleanup and both classes reserve at least the Blob slot prefix.
  MOZ_ASSERT(JSCLASS_RESERVED_SLOTS(JS::GetClass(self)) >= std::to_underlying(Slots::Count));
  // GetMaybePtr explicitly accepts undefined slots. File forwards here through
  // its own JSClass finalizer; no second parent finalizer is invoked by the VM.
  auto *blob = JS::GetMaybePtrFromReservedSlot<ByteBuffer>(self, std::to_underlying(Slots::Data));
  if (blob) {
    js_delete(blob);
  }
}

bool install(api::Engine *engine) {
  return Blob::init_class(engine->cx(), engine->global());
}

} // namespace builtins::web::blob


