#include "text-decoder.h"
#include "encode.h"
#include "rust-encoding.h"
#include "js/ArrayBuffer.h"
#include "js/MemoryFunctions.h"
#include "js/experimental/TypedData.h"
#include <limits>

#include "text-codec-errors.h"

namespace builtins::web::text_codec {

bool TextDecoder::decode(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "decode", "TextDecoder");
  }

  // Preserve the existing BufferSource type check before dictionary getters.
  // Do not borrow its data until every observable conversion has completed.
  JS::RootedObject input(cx);
  bool is_view = false;
  auto source_value = args.get(0);
  if (!source_value.isUndefined()) {
    if (!source_value.isObject() ||
        (!(is_view = JS_IsArrayBufferViewObject(&source_value.toObject())) &&
         !JS::IsArrayBufferObject(&source_value.toObject()))) {
      return api::throw_error(cx, api::Errors::InvalidBuffer, "TextDecoder#decode: input");
    }
    input = &source_value.toObject();
  }

  bool stream = false;
  if (args.hasDefined(1) && !args.get(1).isNull()) {
    auto options_value = args.get(1);
    if (!options_value.isObject()) {
      return api::throw_error(cx, api::Errors::TypeError, "TextDecoder.decode",
                              "options", "be an object or undefined");
    }
    JS::RootedObject options(cx, &options_value.toObject());
    JS::RootedValue stream_value(cx);
    if (!JS_GetProperty(cx, options, "stream", &stream_value)) return false;
    stream = JS::ToBoolean(stream_value);
  }

  // Re-read native lengths AFTER stream getters may have changed the source.
  size_t source_length = input ? (is_view ? JS_GetArrayBufferViewByteLength(input)
                                        : JS::GetArrayBufferByteLength(input)) : 0;
  if (input && is_view) {
    bool shared = false;
    {
      JS::AutoCheckCannotGC nogc(cx);
      (void)JS_GetArrayBufferViewData(input, &shared, nogc);
    }
    // Selected policy: shared views require a separately audited atomic
    // snapshot path and are rejected. This is not full WebIDL conformance.
    if (shared) {
      return api::throw_error(cx, api::Errors::TypeError, "TextDecoder.decode",
                              "input", "use unshared backing memory");
    }
  }

  bool fatal = JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Fatal)).toBoolean();
  bool ignoreBOM = JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::IgnoreBOM)).toBoolean();
  auto *decoder = reinterpret_cast<jsencoding::Decoder *>(
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Decoder)).toPrivate());
  MOZ_ASSERT(decoder);
  size_t destLen = jsencoding::decoder_max_utf16_buffer_length(decoder, source_length);
  if (destLen > std::numeric_limits<size_t>::max() / sizeof(char16_t) - 1) {
    JS_ReportAllocationOverflow(cx);
    return false;
  }
  // Fallible JS allocator, matched with JS::FreePolicy. No input pointer is
  // live across allocation, and null must install the actual OOM exception.
  JS::UniqueTwoByteChars dest(static_cast<char16_t *>(JS_malloc(cx, (destLen + 1) * sizeof(char16_t))));
  if (!dest) { JS_ReportOutOfMemory(cx); return false; }

  uint32_t result = 0;
  bool invalid_source = false;
  const uint8_t empty = 0; // Addressable nonnull storage for an empty Rust slice.
  {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    size_t current_length = input ? (is_view ? JS_GetArrayBufferViewByteLength(input)
                                            : JS::GetArrayBufferByteLength(input)) : 0;
    const uint8_t *src_ptr = input ? (is_view
        ? static_cast<uint8_t *>(JS_GetArrayBufferViewData(input, &shared, nogc))
        : JS::GetArrayBufferData(input, &shared, nogc)) : nullptr;
    // Rust slices require nonnull even for empty or detached input.
    if (current_length == 0) src_ptr = &empty;
    invalid_source = shared || current_length != source_length || !src_ptr;
    if (!invalid_source) {
      // encoding_c/encoding_rs consume these slices synchronously, copy pending
      // bytes into Decoder-owned fields and invoke no JSAPI or host callbacks.
      size_t consumed = source_length;
      if (fatal) {
        result = jsencoding::decoder_decode_to_utf16_without_replacement(
            decoder, src_ptr, &consumed, reinterpret_cast<uint16_t *>(dest.get()), &destLen, !stream);
      } else {
        bool replacements = false;
        result = jsencoding::decoder_decode_to_utf16(
            decoder, src_ptr, &consumed, reinterpret_cast<uint16_t *>(dest.get()), &destLen, !stream, &replacements);
      }
    }
  }
  if (invalid_source) {
    return api::throw_error(cx, api::Errors::TypeError, "TextDecoder.decode",
                            "input", "remain an unshared buffer source");
  }
  if (result != 0) return api::throw_error(cx, TextCodecErrors::DecodingFailed);

  auto *encoding = reinterpret_cast<jsencoding::Encoding *>(
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Encoding)).toPrivate());
  if (!stream) {
    if (ignoreBOM) jsencoding::encoding_new_decoder_without_bom_handling_into(encoding, decoder);
    else jsencoding::encoding_new_decoder_with_bom_removal_into(encoding, decoder);
  }
  JS::RootedString str(cx, JS_NewUCStringCopyN(cx, dest.get(), destLen));
  if (!str) return false; // Preserve pending OOM instead of replacing it.
  args.rval().setString(str);
  return true;
}

bool TextDecoder::encoding_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);
  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "encoding get", "TextDecoder");
  }

  auto *encoding = reinterpret_cast<jsencoding::Encoding *>(
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Encoding)).toPrivate());
  MOZ_ASSERT(encoding);

  std::unique_ptr<uint8_t[]> name(new uint8_t[jsencoding::ENCODING_NAME_MAX_LENGTH]);
  if (!name) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  size_t length = jsencoding::encoding_name(encoding, name.get());
  // encoding_rs/jsencoding returns the name uppercase but we need to have it lowercased
  for (size_t i = 0; i < length; i++) {
    name[i] = std::tolower(name[i]);
  }
  JS::RootedString str(cx, JS_NewStringCopyN(cx, reinterpret_cast<char *>(name.get()), length));
  if (!str) {
    JS_ReportOutOfMemory(cx);
    return false;
  }

  args.rval().setString(str);
  return true;
}

bool TextDecoder::fatal_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);

  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "fatal get", "TextDecoder");
  }

  auto fatal =
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Fatal)).toBoolean();

  args.rval().setBoolean(fatal);
  return true;
}

bool TextDecoder::ignoreBOM_get(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);

  // TODO: Change this class so that its prototype isn't an instance of the class
  if (self == proto_obj) {
    return api::throw_error(cx, api::Errors::WrongReceiver, "ignoreBOM get", "TextDecoder");
  }

  auto ignoreBOM =
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::IgnoreBOM)).toBoolean();

  args.rval().setBoolean(ignoreBOM);
  return true;
}

const JSFunctionSpec TextDecoder::static_methods[] = {
    JS_FS_END,
};

const JSPropertySpec TextDecoder::static_properties[] = {
    JS_PS_END,
};

const JSFunctionSpec TextDecoder::methods[] = {
    JS_FN("decode", decode, 0, JSPROP_ENUMERATE),
    JS_FS_END,
};

const JSPropertySpec TextDecoder::properties[] = {
    JS_PSG("encoding", encoding_get, JSPROP_ENUMERATE),
    JS_PSG("fatal", fatal_get, JSPROP_ENUMERATE),
    JS_PSG("ignoreBOM", ignoreBOM_get, JSPROP_ENUMERATE),
    JS_STRING_SYM_PS(toStringTag, "TextDecoder", JSPROP_READONLY),
    JS_PS_END,
};

// constructor(optional DOMString label = "utf-8", optional TextDecoderOptions options = {});
bool TextDecoder::constructor(JSContext *cx, unsigned argc, JS::Value *vp) {
  CTOR_HEADER("TextDecoder", 0);
  // 1. Let encoding be the result of getting an encoding from label.
  auto label_value = args.get(0);
  // https://encoding.spec.whatwg.org/#concept-encoding-get
  // To get an encoding from a string label, run these steps:
  // 1. Remove any leading and trailing ASCII whitespace from label.
  // 2. If label is an ASCII case-insensitive match for any of the labels listed in the table
  // below, then return the corresponding encoding; otherwise return failure. JS-Compute-Runtime:
  const jsencoding::Encoding *encoding = nullptr;
  if (label_value.isUndefined()) {
    const char *utf8_label = "UTF-8";
    encoding = jsencoding::encoding_for_label_no_replacement(
        reinterpret_cast<const uint8_t *>(utf8_label), 5);
  } else {
    auto label_chars = core::encode(cx, label_value);
    if (!label_chars) {
      return false;
    }
    encoding = jsencoding::encoding_for_label_no_replacement(
        reinterpret_cast<uint8_t *>(label_chars.begin()), label_chars.len);
  }
  if (!encoding) {
    return api::throw_error(cx, TextCodecErrors::InvalidEncoding);
  }
  bool fatal = false;
  bool ignoreBOM = false;
  if (args.hasDefined(1)) {
    auto options_val = args.get(1);
    if (options_val.isObject()) {
      JS::RootedObject options(cx, &options_val.toObject());
      JS::RootedValue fatal_value(cx);
      if (!JS_GetProperty(cx, options, "fatal", &fatal_value)) {
        return false;
      }
      fatal = JS::ToBoolean(fatal_value);
      JS::RootedValue ignoreBOM_value(cx);
      if (!JS_GetProperty(cx, options, "ignoreBOM", &ignoreBOM_value)) {
        return false;
      }
      ignoreBOM = JS::ToBoolean(ignoreBOM_value);
    } else if (!options_val.isNull()) {
      return api::throw_error(cx, api::Errors::TypeError, "TextDecoder constructor",
        "options", "be an object or undefined");
    }
  }
  JS::RootedObject self(cx, JS_NewObjectForConstructor(cx, &class_, args));
  if (!self) return false;
  JS::SetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Decoder), JS::PrivateValue(nullptr));
  jsencoding::Decoder *decoder = nullptr;
  if (ignoreBOM) {
    decoder = jsencoding::encoding_new_decoder_without_bom_handling(encoding);
  } else {
    decoder = jsencoding::encoding_new_decoder_with_bom_removal(encoding);
  }

  // Defensive only: encoding_c currently uses infallible Box::new, whose real
  // allocator exhaustion abort is NOT converted into a recoverable JS OOM here.
  if (!decoder) { JS_ReportOutOfMemory(cx); return false; }

  // NOLINTNEXTLINE(cppcoreguidelines-pro-type-const-cast): drop const to store encoding in the slot
  auto *encoding_ptr = const_cast<jsencoding::Encoding *>(encoding);

  JS::SetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Decoder),
                      JS::PrivateValue(decoder));
  JS::SetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Encoding),
                      JS::PrivateValue(encoding_ptr));
  JS::SetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Fatal),
                      JS::BooleanValue(fatal));
  JS::SetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::IgnoreBOM),
                      JS::BooleanValue(ignoreBOM));

  args.rval().setObject(*self);
  return true;
}

bool TextDecoder::init_class(JSContext *cx, JS::HandleObject global) {
  return init_class_impl(cx, global);
}

void TextDecoder::finalize(JS::GCContext *gcx, JSObject *self) {
  if (JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Decoder)).isUndefined()) return;
  auto *decoder = reinterpret_cast<jsencoding::Decoder *>(
      JS::GetReservedSlot(self, static_cast<uint32_t>(TextDecoder::Slots::Decoder)).toPrivate());

  if (decoder) {
    jsencoding::decoder_free(decoder);
  }
}

} // namespace builtins::web::text_codec


