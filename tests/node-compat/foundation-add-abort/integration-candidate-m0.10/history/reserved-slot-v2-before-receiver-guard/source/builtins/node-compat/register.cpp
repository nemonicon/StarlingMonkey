// Opt-in registration for the bounded Node v22.14.0 profile.
#include "builtin.h"
#include "js/CallAndConstruct.h"
#include "js/CompilationAndEvaluation.h"
#include "js/SourceText.h"
#include "factories.generated.h"
#ifdef NODE_COMPAT_PATH
#include "path-factories.generated.h"
#endif
#ifdef NODE_COMPAT_EVENTS
#include "events-factories.generated.h"
#include "../web/event/event-target.h"
#include "js/Symbol.h"
#endif
#ifdef NODE_COMPAT_STRING_DECODER
#include "string-decoder-factories.generated.h"
#endif
#ifdef NODE_COMPAT_ASSERT
#include "assert-factories.generated.h"
#endif
#ifdef NODE_COMPAT_QUERYSTRING
#include "querystring-factories.generated.h"
#endif
#ifdef NODE_COMPAT_UTIL
#include "util-factories.generated.h"
#endif
#ifdef NODE_COMPAT_STREAM_WEB
#include "stream-web-factories.generated.h"
#endif

namespace builtins::node_compat {
JSObject *create_kernel(JSContext *cx);
#ifdef NODE_COMPAT_STREAM_WEB
JSObject *create_stream_web_kernel(JSContext *cx);
#endif

static bool evaluate_factory(JSContext *cx, const char *source_text,
                             JS::HandleValue argument, JS::MutableHandleValue result) {
  JS::CompileOptions options(cx);
  options.setFileAndLine("<node-profile-factory>", 1);
  // Canonical facades are ESM. Their generated script form must retain strict
  // receiver semantics, particularly ordinary calls to StringDecoder().
  options.setForceStrictMode();
  JS::SourceText<mozilla::Utf8Unit> source;
  if (!source.init(cx, source_text, strlen(source_text), JS::SourceOwnership::Borrowed)) return false;
  JS::RootedValue factory(cx);
  if (!JS::Evaluate(cx, options, source, &factory)) return false;
  JS::RootedValueArray<1> arguments(cx);
  arguments[0].set(argument);
  return JS::Call(cx, JS::UndefinedHandleValue, factory, arguments, result);
}

#ifdef NODE_COMPAT_PATH
static bool install_path(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kPathFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), posix(cx), win32(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "posix", &posix) ||
      !JS_GetProperty(cx, object, "win32", &win32)) return false;
  return engine->define_builtin_module("node:path", root) &&
         engine->define_builtin_module("path", root) &&
         engine->define_builtin_module("node:path/posix", posix) &&
         engine->define_builtin_module("path/posix", posix) &&
         engine->define_builtin_module("node:path/win32", win32) &&
         engine->define_builtin_module("path/win32", win32);
}
#endif

#ifdef NODE_COMPAT_EVENTS
static bool install_events(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedSymbol key(cx, builtins::web::event::EventTarget::node_abort_resist_key());
  if (!key) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: protected EventTarget key unavailable");
    return false;
  }
  JS::RootedValue argument(cx, JS::SymbolValue(key));
  JS::RootedValue module(cx);
  if (!evaluate_factory(cx, kEventsFactorySource, argument, &module)) return false;
  return engine->define_builtin_module("node:events", module) &&
         engine->define_builtin_module("events", module);
}
#endif

#ifdef NODE_COMPAT_STRING_DECODER
static bool install_string_decoder(api::Engine *engine, JS::HandleValue buffer_constructor) {
  JS::RootedValue module(engine->cx());
  if (!evaluate_factory(engine->cx(), kStringDecoderFactorySource, buffer_constructor, &module)) return false;
  return engine->define_builtin_module("node:string_decoder", module) &&
         engine->define_builtin_module("string_decoder", module);
}
#endif

#ifdef NODE_COMPAT_ASSERT
static bool install_assert(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kAssertFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), strict(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "strict", &strict)) return false;
  return engine->define_builtin_module("node:assert", root) &&
         engine->define_builtin_module("assert", root) &&
         engine->define_builtin_module("node:assert/strict", strict) &&
         engine->define_builtin_module("assert/strict", strict);
}
#endif

#ifdef NODE_COMPAT_QUERYSTRING
static bool install_querystring(api::Engine *engine, JS::HandleValue buffer_constructor) {
  JS::RootedValue module(engine->cx());
  if (!evaluate_factory(engine->cx(), kQuerystringFactorySource, buffer_constructor, &module)) return false;
  return engine->define_builtin_module("node:querystring", module) &&
         engine->define_builtin_module("querystring", module);
}
#endif

#ifdef NODE_COMPAT_UTIL
static bool install_util(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kUtilFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), types(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "types", &types)) return false;
  return engine->define_builtin_module("node:util", root) &&
         engine->define_builtin_module("util", root) &&
         engine->define_builtin_module("node:sys", root) &&
         engine->define_builtin_module("sys", root) &&
         engine->define_builtin_module("node:util/types", types) &&
         engine->define_builtin_module("util/types", types);
}
#endif

#ifdef NODE_COMPAT_STREAM_WEB
static bool install_stream_web(api::Engine *engine) {
  auto *cx = engine->cx();
  // install() already entered the content realm; existing web prerequisites
  // precede this builtin in declaration/install order. Capture no live streams.
  JS::RootedObject kernel(cx, create_stream_web_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue argument(cx, JS::ObjectValue(*kernel));
  JS::RootedValue module(cx);
  if (!evaluate_factory(cx, kStreamWebFactorySource, argument, &module)) return false;
  return engine->define_builtin_module("node:stream/web", module) &&
         engine->define_builtin_module("stream/web", module);
}
#endif

bool install(api::Engine *engine) {
  auto *cx = engine->cx();
  // Existing install_builtins() executes in the CONTENT realm before user code.
  // Its ScriptLoader already exists. Avoid Engine::eval_toplevel() here, whose
  // lifecycle assertion requires initialization to have finished.
  JSAutoRealm realm(cx, engine->global());
  JS::RootedObject kernel(cx, create_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  JS::RootedValue buffer_module(cx);
  if (!evaluate_factory(cx, kBufferFactorySource, kernel_value, &buffer_module)) return false;
  if (!engine->define_builtin_module("node:buffer", buffer_module) ||
      !engine->define_builtin_module("buffer", buffer_module)) return false;
  JS::RootedValue child_module(cx);
  if (!evaluate_factory(cx, kChildProcessFactorySource, JS::UndefinedHandleValue, &child_module)) return false;
  if (!engine->define_builtin_module("node:child_process", child_module) ||
      !engine->define_builtin_module("child_process", child_module)) return false;
  // Public Buffer is selected explicitly for this profile. Registering both
  // specifiers preserves object/function identities; module namespace records
  // themselves are per-specifier in the existing loader.
  JS::RootedObject buffer_namespace(cx, &buffer_module.toObject());
  JS::RootedValue buffer_constructor(cx);
  if (!JS_GetProperty(cx, buffer_namespace, "Buffer", &buffer_constructor)) return false;
#ifdef NODE_COMPAT_PATH
  if (!install_path(engine)) return false;
#endif
#ifdef NODE_COMPAT_EVENTS
  if (!install_events(engine)) return false;
#endif
#ifdef NODE_COMPAT_STRING_DECODER
  if (!install_string_decoder(engine, buffer_constructor)) return false;
#endif
#ifdef NODE_COMPAT_ASSERT
  if (!install_assert(engine)) return false;
#endif
#ifdef NODE_COMPAT_QUERYSTRING
  if (!install_querystring(engine, buffer_constructor)) return false;
#endif
#ifdef NODE_COMPAT_UTIL
  if (!install_util(engine)) return false;
#endif
#ifdef NODE_COMPAT_STREAM_WEB
  if (!install_stream_web(engine)) return false;
#endif
  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);
}
} // namespace builtins::node_compat
