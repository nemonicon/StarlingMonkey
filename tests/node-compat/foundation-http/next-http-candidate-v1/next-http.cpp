// Experimental native registration of real guest HTTP module bindings.
#include "next-http.h"
#include "next-http-factory.generated.h"
#include "script_loader.h"
#include "async_context_runtime.h"
#include "node-compat-entropy.h"
#include "node_tick_queue.h"
#include "js/CallAndConstruct.h"
#include "js/CompilationAndEvaluation.h"
#include "js/SourceText.h"
#include <cstring>
#include <string>

namespace builtins::node_compat {
namespace {
bool deployed(JSContext* cx, unsigned argc, JS::Value* vp) {
  auto args = JS::CallArgsFromVp(argc, vp);
  auto* engine = api::Engine::get(cx);
  if (!engine || engine->state() != api::EngineState::Initialized ||
      !entropy::deployed_execution_started())
    return core::InternalTickQueue::fail(cx, JSEXN_ERR,
        "ERR_SM_NODE_HTTP_INITIALIZATION", "HTTP server preparation requires deployed execution");
  args.rval().setUndefined(); return true;
}
bool dependency(JSContext* cx, JS::HandleObject argument, const char* name,
                const char* module, const char* member) {
  JS::RootedString id(cx, JS_NewStringCopyZ(cx, module));
  JS::RootedValue record(cx), value(cx);
  if (!id || !ScriptLoader::lookup_registered_builtin(cx, id, &record) || !record.isObject()) return false;
  JS::RootedObject object(cx, &record.toObject());
  if (!JS_GetProperty(cx, object, member, &value)) return false;
  return JS_DefineProperty(cx, argument, name, value, JSPROP_ENUMERATE);
}
}
bool install_next_http(api::Engine* engine) {
  auto* cx = engine->cx();
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument ||
      !dependency(cx, argument, "Readable", "node:stream", "Readable") ||
      !dependency(cx, argument, "Writable", "node:stream", "Writable") ||
      !dependency(cx, argument, "EventEmitter", "node:events", "EventEmitter") ||
      !dependency(cx, argument, "Buffer", "node:buffer", "Buffer")) return false;
  if (!JS_DefineFunction(cx, argument, "runFreshRequest", core::async_context::run_fresh_request_native, 2, 0) ||
      !JS_DefineFunction(cx, argument, "runNeutralServer", core::async_context::run_neutral_server_native, 2, 0) ||
      !JS_DefineFunction(cx, argument, "checkDeployed", deployed, 0, 0)) return false;
  JS::CompileOptions options(cx);
  options.setFileAndLine("<next-http-factory>", 1).setForceStrictMode();
  JS::SourceText<mozilla::Utf8Unit> source;
  if (!source.init(cx, kNextHttpFactorySource, strlen(kNextHttpFactorySource), JS::SourceOwnership::Borrowed)) return false;
  JS::RootedValue factory(cx), graph_value(cx);
  if (!JS::Evaluate(cx, options, source, &factory)) return false;
  JS::RootedValueArray<1> args(cx); args[0].setObject(*argument);
  if (!JS::Call(cx, JS::UndefinedHandleValue, factory, args, &graph_value) || !graph_value.isObject()) return false;
  JS::RootedObject graph(cx, &graph_value.toObject()); JS::RootedValue record(cx);
  for (const char* id : {"http", "https"}) {
    if (!JS_GetProperty(cx, graph, id, &record)) return false;
    const std::string canonical = std::string("node:") + id;
    if (!engine->define_builtin_module(canonical.c_str(), record) || !engine->define_builtin_module(id, record)) return false;
  }
  return JS_GetProperty(cx, graph, "hosting", &record) &&
      engine->define_builtin_module("starling:node-http", record);
}
} // namespace builtins::node_compat
