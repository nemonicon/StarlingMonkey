#include "text-encoder.h"
#include "js/CharacterEncoding.h"
#include "js/GCAPI.h"
#include "js/String.h"
#include <tuple>

#include "js/ArrayBuffer.h"
#include "js/experimental/TypedData.h"
#include "mozilla/Span.h"

namespace builtins::web::text_codec {

bool TextEncoder::encode(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);

  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "encode", "TextEncoder");
  }

  // Default to empty string if no input is given.
  if (args.get(0).isUndefined()) {
    JS::RootedObject byte_array(cx, JS_NewUint8Array(cx, 0));
    if (!byte_array) {
      return false;
    }

    args.rval().setObject(*byte_array);
    return true;
  }

  // Coercion can invoke application code; linearization and allocation can
  // collect. Keep the string rooted and end its pointer scope before allocating.
  JS::RootedString input(cx, JS::ToString(cx, args[0]));
  if (!input) return false;
  size_t length;
  {
    JSLinearString *linear = JS_EnsureLinearString(cx, input);
    if (!linear) return false;
    length = JS::GetDeflatedUTF8StringLength(linear);
  }

  // Short outputs can stay inline in the GC-owned typed array. No malloc-backed
  // staging buffer or separate ArrayBuffer ownership transfer is necessary.
  JS::RootedObject byte_array(cx, JS_NewUint8Array(cx, length));
  if (!byte_array) return false;
  size_t written = 0;
  if (length != 0) {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    uint8_t *data = JS_GetUint8ArrayData(byte_array, &shared, nogc);
    MOZ_ASSERT(data && !shared);
    // Reacquire both pointers after every MayGC operation. Deflation is
    // infallible and does not allocate or invoke JavaScript.
    written = JS::DeflateStringToUTF8Buffer(
        JS_ASSERT_STRING_IS_LINEAR(input),
        mozilla::Span(reinterpret_cast<char *>(data), length));
  }
  if (written != length) {
    JS_ReportErrorASCII(cx, "TextEncoder UTF-8 length invariant failed");
    return false;
  }

  args.rval().setObject(*byte_array);
  return true;
}

bool TextEncoder::encodeInto(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(2);

  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "encodeInto", "TextEncoder");
  }

  JS::RootedString source(cx, JS::ToString(cx, args.get(0)));
  if (!source) {
    return false;
  }
  auto destination_value = args.get(1);

  if (!destination_value.isObject()) {
    return api::throw_error(cx, api::Errors::TypeError, "TextEncoder.encodeInto",
      "destination", "be a Uint8Array");
  }
  JS::RootedObject destination(cx, &destination_value.toObject());

  uint8_t *data = nullptr;
  bool is_shared = false;
  size_t len = 0;
  // JS_GetObjectAsUint8Array returns nullptr without throwing if the object is not
  // a Uint8Array, so we don't need to do explicit checks before calling it.
  if (!JS_GetObjectAsUint8Array(destination, &len, &is_shared, &data)) {
    return api::throw_error(cx, api::Errors::TypeError, "TextEncoder.encodeInto",
      "destination", "be a Uint8Array");
  }
  size_t read = 0;
  size_t written = 0;
  if (len != 0) {
    // A detached/out-of-bounds or empty view can have null data. Do not pass
    // that empty span to the underlying codec's non-null slice interface.
    auto span = AsWritableChars(mozilla::Span(data, len));
    auto maybe = JS_EncodeStringToUTF8BufferPartial(cx, source, span);
    if (!maybe) {
      // This public API explicitly returns Nothing on OOM without setting an
      // exception. The JS native must report it before returning false.
      JS_ReportOutOfMemory(cx);
      return false;
    }
    std::tie(read, written) = *maybe;
  }

  MOZ_ASSERT(written <= len);

  JS::RootedObject obj(cx, JS_NewPlainObject(cx));
  if (!obj) {
    return false;
  }
  JS::RootedValue read_value(cx, JS::NumberValue(read));
  JS::RootedValue written_value(cx, JS::NumberValue(written));
  if (!JS_SetProperty(cx, obj, "read", read_value)) {
    return false;
  }
  if (!JS_SetProperty(cx, obj, "written", written_value)) {
    return false;
  }

  args.rval().setObject(*obj);
  return true;
}

bool TextEncoder::encoding_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);

  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "encoding get", "TextEncoder");
  }

  JS::RootedString str(cx, JS_NewStringCopyN(cx, "utf-8", 5));
  if (!str) {
    return false;
  }

  args.rval().setString(str);
  return true;
}

const JSFunctionSpec TextEncoder::static_methods[] = {
    JS_FS_END,
};

const JSPropertySpec TextEncoder::static_properties[] = {
    JS_PS_END,
};

const JSFunctionSpec TextEncoder::methods[] = {
    JS_FN("encode", encode, 0, JSPROP_ENUMERATE),
    JS_FN("encodeInto", encodeInto, 2, JSPROP_ENUMERATE),
    JS_FS_END,
};

const JSPropertySpec TextEncoder::properties[] = {
    JS_PSG("encoding", encoding_get, JSPROP_ENUMERATE),
    JS_STRING_SYM_PS(toStringTag, "TextEncoder", JSPROP_READONLY),
    JS_PS_END,
};

bool TextEncoder::constructor(JSContext *cx, unsigned argc, JS::Value *vp) {
  CTOR_HEADER("TextEncoder", 0);

  JS::RootedObject self(cx, JS_NewObjectForConstructor(cx, &class_, args));
  if (!self) {
    return false;
  }

  args.rval().setObject(*self);
  return true;
}

bool TextEncoder::init_class(JSContext *cx, JS::HandleObject global) {
  return init_class_impl(cx, global);
}

} // namespace builtins::web::text_codec


