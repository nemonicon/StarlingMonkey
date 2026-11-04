// UNAPPLIED / UNCOMPILED benchmark-only guest binding. Never a Node API.
// This callable uses the existing traced TaskQueue FIFO; no extra root/queue,
// clock, AsyncTask, public process object, reset hook or host service is added.
#include "event_loop.h"
#include "extension-api.h"
#include "js/PropertyAndElement.h"
#include "jsapi.h"

#ifndef NODE_COMPAT_INTERNAL_TICKS
#error "Classic benchmark binding requires the existing private tick queue"
#endif

namespace diagnostics::classic_benchmark {
bool install(api::Engine* engine) {
  auto* cx = engine->cx();
  JSAutoRealm realm(cx, engine->global());
  JS::RootedObject record(cx, JS_NewPlainObject(cx));
  if (!record) return false;
  JS::RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));
  if (!next_tick) return false;
  if (!JS_DefineProperty(cx, record, "nextTick", next_tick, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, record, "default", record, JSPROP_ENUMERATE)) return false;
  JS::RootedValue module(cx, JS::ObjectValue(*record));
  return engine->define_builtin_module("starling:test-classic-benchmark", module);
}
} // namespace diagnostics::classic_benchmark
