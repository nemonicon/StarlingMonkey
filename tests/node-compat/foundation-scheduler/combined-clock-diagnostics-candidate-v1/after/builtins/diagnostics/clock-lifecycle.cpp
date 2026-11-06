// UNCOMPILED private read-only guest builtin; never a current355 export.
#include "extension-api.h"
#include "clock-lifecycle-diagnostics.h"
#include "js/Array.h"
#include "js/PropertyAndElement.h"
#include "js/String.h"

namespace diagnostics::clock_lifecycle {
namespace {
bool u64(JSContext* cx, JS::HandleObject object, const char* key, std::uint64_t value) {
  char bytes[21]; char* cursor = bytes + sizeof(bytes);
  do { *--cursor = static_cast<char>('0' + value % 10); value /= 10; } while (value);
  JS::RootedString string(cx, JS_NewStringCopyN(cx, cursor,
    static_cast<std::size_t>(bytes + sizeof(bytes) - cursor)));
  if (!string) return false;
  JS::RootedValue field(cx, JS::StringValue(string));
  return JS_DefineProperty(cx, object, key, field, JSPROP_ENUMERATE);
}
bool boolean(JSContext* cx, JS::HandleObject object, const char* key, bool value) {
  JS::RootedValue field(cx, JS::BooleanValue(value));
  return JS_DefineProperty(cx, object, key, field, JSPROP_ENUMERATE);
}
bool integer(JSContext* cx, JS::HandleObject object, const char* key, int value) {
  JS::RootedValue field(cx, JS::Int32Value(value));
  return JS_DefineProperty(cx, object, key, field, JSPROP_ENUMERATE);
}
bool object(JSContext* cx, JS::HandleObject parent, const char* key, JS::HandleObject child) {
  JS::RootedValue value(cx, JS::ObjectValue(*child));
  return JS_DefineProperty(cx, parent, key, value, JSPROP_ENUMERATE);
}
bool runtime(JSContext* cx, JS::HandleObject parent, const char* key, const RuntimeCounts& r) {
  JS::RootedObject out(cx, JS_NewPlainObject(cx));
  return out && u64(cx, out, "queued", r.queued) && integer(cx, out, "interest", r.interest) &&
    boolean(cx, out, "loopRunning", r.loopRunning) && u64(cx, out, "timerRegistry", r.timerRegistry) &&
    boolean(cx, out, "immediateCacheOwned", r.immediateCacheOwned) && object(cx, parent, key, out);
}
bool boundary(JSContext* cx, JS::HandleObject parent, const char* key, const Boundary& b) {
  JS::RootedObject out(cx, JS_NewPlainObject(cx));
  return out && boolean(cx, out, "present", b.present) && u64(cx, out, "callSerial", b.callSerial) &&
    u64(cx, out, "functionIndex", b.functionIndex) && runtime(cx, out, "runtime", b.runtime) &&
    boolean(cx, out, "loopResultObserved", b.loopResultObserved) &&
    boolean(cx, out, "loopReturnedSuccess", b.loopReturnedSuccess) &&
    integer(cx, out, "currentFunction", b.currentFunction) &&
    u64(cx, out, "freeListSize", b.freeListSize) && object(cx, parent, key, out);
}
bool read_snapshot(JSContext* cx, unsigned argc, JS::Value* vp) {
  const auto args = JS::CallArgsFromVp(argc, vp);
  // Capture plain native data BEFORE JS allocations/possible GC. Snapshot
  // serialization never retains a task or changes interest/registry ownership.
  const Snapshot captured = capture();
  JS::RootedObject out(cx, JS_NewPlainObject(cx)), counters(cx, JS_NewPlainObject(cx));
  JS::RootedObject leases(cx, JS::NewArrayObject(cx, captured.history.usedLeases));
  if (!out || !counters || !leases || !integer(cx, out, "schemaVersion", 1) ||
      !boolean(cx, out, "diagnosticOnly", true) ||
      !boolean(cx, out, "overflow", captured.history.overflow) ||
      !boolean(cx, out, "invariantViolation", captured.history.invariantViolation) ||
      !boolean(cx, out, "recordingComplete", !captured.history.overflow && !captured.history.invariantViolation) ||
      !boolean(cx, out, "hostResourceTableObserved", false) ||
      !boolean(cx, out, "destructionAtHostStoreExitObserved", false) ||
      !u64(cx, out, "eventSerial", captured.history.eventSerial) ||
      !u64(cx, out, "currentCallSerial", captured.history.callSerial) ||
      !runtime(cx, out, "current", captured.current) ||
      !boundary(cx, out, "afterLoop", captured.history.afterLoop) ||
      !boundary(cx, out, "afterPostCall", captured.history.afterPostCall)) return false;
  for (std::size_t i = 0; i < captured.history.counts.size(); ++i)
    if (!u64(cx, counters, CounterNames[i], captured.history.counts[i])) return false;
  for (std::size_t i = 0; i < captured.history.usedLeases; ++i) {
    const auto& r = captured.history.leases[i];
    JS::RootedObject row(cx, JS_NewPlainObject(cx));
    if (!row || !u64(cx, row, "serial", r.serial) || !integer(cx, row, "timerId", r.timerId) ||
        !u64(cx, row, "acquiredAt", r.acquiredAt) || !u64(cx, row, "invalidatedAt", r.invalidatedAt) ||
        !u64(cx, row, "dropAttemptAt", r.dropAttemptAt) || !u64(cx, row, "dropReturnedAt", r.dropReturnedAt) ||
        !boolean(cx, row, "owned", r.owned)) return false;
    JS::RootedValue value(cx, JS::ObjectValue(*row));
    if (!JS_SetElement(cx, leases, static_cast<std::uint32_t>(i), value)) return false;
  }
  if (!object(cx, out, "counters", counters) || !object(cx, out, "timerLeases", leases)) return false;
  args.rval().setObject(*out); return true;
}
const JSFunctionSpec functions[] = {JS_FN("snapshot", read_snapshot, 0, JSPROP_ENUMERATE), JS_FS_END};
} // namespace
bool install(api::Engine* engine) {
  auto* cx = engine->cx(); JSAutoRealm realm(cx, engine->global());
  JS::RootedObject record(cx, JS_NewPlainObject(cx));
  if (!record || !JS_DefineFunctions(cx, record, functions) ||
      !object(cx, record, "default", record)) return false;
  JS::RootedValue value(cx, JS::ObjectValue(*record));
  return engine->define_builtin_module("starling:test-clock-lifecycle", value);
}
} // namespace diagnostics::clock_lifecycle
