#include "next-imports.h"
#include "next-imports-factory.generated.h"
#include "js/CompilationAndEvaluation.h"
#include "js/CallAndConstruct.h"
#include "js/SourceText.h"
#include <cstring>
#include <string>

namespace builtins::node_compat {
bool install_next_imports(api::Engine* engine) {
  auto* cx = engine->cx();
  JS::CompileOptions options(cx); options.setFileAndLine("<next-imports>", 1).setForceStrictMode();
  JS::SourceText<mozilla::Utf8Unit> source;
  if (!source.init(cx, kNextImportsFactorySource, strlen(kNextImportsFactorySource), JS::SourceOwnership::Borrowed)) return false;
  JS::RootedValue factory(cx), graph_value(cx);
  if (!JS::Evaluate(cx, options, source, &factory) ||
      !JS::Call(cx, JS::UndefinedHandleValue, factory, JS::HandleValueArray::empty(), &graph_value) ||
      !graph_value.isObject()) return false;
  JS::RootedObject graph(cx, &graph_value.toObject()); JS::RootedValue record(cx);
  for (const char* id : {"tty", "inspector", "v8", "dns/promises"}) {
    const std::string canonical = std::string("node:") + id;
    if (!JS_GetProperty(cx, graph, canonical.c_str(), &record) ||
        !engine->define_builtin_module(canonical.c_str(), record) ||
        !engine->define_builtin_module(id, record)) return false;
  }
  return true;
}
}
