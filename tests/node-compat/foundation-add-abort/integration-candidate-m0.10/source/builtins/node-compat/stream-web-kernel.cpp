// Private native class record for the optional bounded node:stream/web profile.
// The selected target includes the StarlingMonkey source root and depends on
// builtin_web_streams + builtin_web_text_codec. Their earlier declarations
// establish installation order. The caller enters the content realm and
// immediately roots the result, as register.cpp does for create_kernel().
#include "builtin.h"
#include "builtins/web/streams/transform-stream.h"
#include "builtins/web/streams/transform-stream-default-controller.h"
#include "builtins/web/text-codec/text-encoder.h"
#include "builtins/web/text-codec/text-decoder.h"
#include "js/CallAndConstruct.h"
#include "js/Proxy.h"
#include "js/Stream.h"
#include "jsapi.h"

namespace builtins::node_compat {
namespace {

bool define_standard_constructor(JSContext *cx, JS::HandleObject record,
                                 const char *name, JSProtoKey key) {
  JS::RootedObject constructor(cx);
  // Verified declaration: pinned jsapi.h:204. Its actual returned constructors
  // still need a compiled-component identity/operation gate for this template.
  if (!JS_GetClassObject(cx, key, &constructor)) return false;
  if (!constructor || !JS::IsCallable(constructor)) {
    JS_ReportErrorASCII(cx, "Node stream/web native constructor unavailable: %s", name);
    return false;
  }
  JS::RootedValue value(cx, JS::ObjectValue(*constructor));
  return JS_DefineProperty(cx, record, name, value, JSPROP_ENUMERATE);
}

bool define_prototype_constructor(JSContext *cx, JS::HandleObject record,
                                  const char *name, JS::HandleObject prototype) {
  if (!prototype) {
    JS_ReportErrorASCII(cx, "Node stream/web prerequisite not initialized: %s", name);
    return false;
  }
  JS::RootedValue value(cx);
  if (!JS_GetProperty(cx, prototype, "constructor", &value)) return false;
  if (!value.isObject() || !JS::IsCallable(&value.toObject())) {
    JS_ReportErrorASCII(cx, "Node stream/web retained constructor unavailable: %s", name);
    return false;
  }
  return JS_DefineProperty(cx, record, name, value, JSPROP_ENUMERATE);
}

bool is_readable_stream_byob_reader(JSContext *cx, unsigned argc, JS::Value *vp) {
  JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
  bool matches = false;
  if (args.get(0).isObject()) {
    JS::RootedObject object(cx, &args[0].toObject());
    // Bounded profile policy excludes scripted Proxy receivers. Node22 can
    // accept a Proxy of a genuine reader through its JS state representation;
    // this stronger native brand is an explicit deviation, not Node parity.
    matches = !js::IsScriptedProxy(object) && JS::IsReadableStreamBYOBReader(object);
  }
  args.rval().setBoolean(matches);
  return true;
}

} // namespace

// Proposed private guest function, not an existing embedding API or host
// service. Its result is the single argument to the future strict JS factory.
JSObject *create_stream_web_kernel(JSContext *cx) {
  JS::RootedObject record(cx, JS_NewPlainObject(cx));
  if (!record) return nullptr;
  const struct { const char *name; JSProtoKey key; } classes[] = {
      {"ReadableStream", JSProto_ReadableStream},
      {"ReadableStreamDefaultReader", JSProto_ReadableStreamDefaultReader},
      {"ReadableStreamBYOBReader", JSProto_ReadableStreamBYOBReader},
      {"ReadableStreamBYOBRequest", JSProto_ReadableStreamBYOBRequest},
      {"ReadableByteStreamController", JSProto_ReadableByteStreamController},
      {"ReadableStreamDefaultController", JSProto_ReadableStreamDefaultController},
      {"WritableStream", JSProto_WritableStream},
      {"WritableStreamDefaultWriter", JSProto_WritableStreamDefaultWriter},
      {"WritableStreamDefaultController", JSProto_WritableStreamDefaultController},
      {"ByteLengthQueuingStrategy", JSProto_ByteLengthQueuingStrategy},
      {"CountQueuingStrategy", JSProto_CountQueuingStrategy},
  };
  for (const auto &entry : classes) {
    if (!define_standard_constructor(cx, record, entry.name, entry.key)) return nullptr;
  }
  JS::RootedObject transform(cx, web::streams::TransformStream::proto_obj);
  JS::RootedObject controller(cx, web::streams::TransformStreamDefaultController::proto_obj);
  JS::RootedObject encoder(cx, web::text_codec::TextEncoder::proto_obj);
  JS::RootedObject decoder(cx, web::text_codec::TextDecoder::proto_obj);
  if (!define_prototype_constructor(cx, record, "TransformStream", transform) ||
      !define_prototype_constructor(cx, record, "TransformStreamDefaultController", controller) ||
      !define_prototype_constructor(cx, record, "TextEncoder", encoder) ||
      !define_prototype_constructor(cx, record, "TextDecoder", decoder)) return nullptr;
  if (!JS_DefineFunction(cx, record, "isReadableStreamBYOBReader",
                         is_readable_stream_byob_reader, 1, JSPROP_ENUMERATE)) return nullptr;
  // No temporary streams, writer promises, live host resources, byte pointers
  // or native compression constructors are created/retained here.
  return record;
}

} // namespace builtins::node_compat
