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
#endif

namespace builtins::node_compat {
JSObject *create_kernel(JSContext *cx);

static bool evaluate_factory(JSContext *cx, const char *source_text,
                             JS::HandleValue argument, JS::MutableHandleValue result) {
  JS::CompileOptions options(cx);
  options.setFileAndLine("<node-profile-factory>", 1);
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
  JS::RootedValue module(engine->cx());
  if (!evaluate_factory(engine->cx(), kEventsFactorySource, JS::UndefinedHandleValue, &module)) return false;
  return engine->define_builtin_module("node:events", module) &&
         engine->define_builtin_module("events", module);
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
  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);
}
} // namespace builtins::node_compat
