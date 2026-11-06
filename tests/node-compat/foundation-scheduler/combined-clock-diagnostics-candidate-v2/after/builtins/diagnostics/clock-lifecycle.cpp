// UNCOMPILED private read-only guest builtin; never a current355 export.
#include "extension-api.h"
#include "builtin.h"
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
bool snapshot_object(JSContext* cx, const Snapshot& captured, JS::MutableHandleObject result) {
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
  result.set(out); return true;
}
bool read_snapshot(JSContext* cx, unsigned argc, JS::Value* vp) {
  const auto args = JS::CallArgsFromVp(argc, vp);
  const Snapshot captured = capture(); // before JS allocation, unchanged V1 ABI
  JS::RootedObject result(cx);
  if (!snapshot_object(cx, captured, &result)) return false;
  args.rval().setObject(*result); return true;
}
bool i64(JSContext* cx, JS::HandleObject object, const char* key, std::int64_t value) {
  char bytes[21]; char* cursor = bytes + sizeof(bytes);
  auto magnitude = value < 0 ? static_cast<std::uint64_t>(-(value + 1)) + 1 : static_cast<std::uint64_t>(value);
  do { *--cursor = static_cast<char>('0' + magnitude % 10); magnitude /= 10; } while (magnitude);
  if (value < 0) *--cursor = '-';
  JS::RootedString string(cx, JS_NewStringCopyN(cx, cursor, static_cast<std::size_t>(bytes + sizeof(bytes) - cursor)));
  if (!string) return false;
  JS::RootedValue field(cx, JS::StringValue(string));
  return JS_DefineProperty(cx, object, key, field, JSPROP_ENUMERATE);
}
bool probe_counts(JSContext* cx, JS::HandleObject parent, const char* key, const SelectorProbeCounts& v) {
  JS::RootedObject out(cx, JS_NewPlainObject(cx));
  return out && u64(cx, out, "constructed", v.constructed) && u64(cx, out, "invalidated", v.invalidated) &&
    u64(cx, out, "destroyed", v.destroyed) && u64(cx, out, "unexpectedRun", v.unexpectedRun) &&
    u64(cx, out, "unexpectedCancel", v.unexpectedCancel) && object(cx, parent, key, out);
}
bool read_clock_state_v2(JSContext* cx, unsigned argc, JS::Value* vp) {
  const auto args = JS::CallArgsFromVp(argc, vp);
  // All captures are POD reads; no added clock call or JS allocation precedes them.
  const auto clock = native_clock_state();
  const auto performance = native_performance_state();
  const auto embedding = state.embeddingClock;
  const auto current_call = state.callSerial;
  const bool complete = !state.overflow && !state.invariantViolation && !clock.overflow && !clock.adjustmentOverflow;
  JS::RootedObject out(cx, JS_NewPlainObject(cx)), c(cx, JS_NewPlainObject(cx));
  JS::RootedObject p(cx, JS_NewPlainObject(cx)), e(cx, JS_NewPlainObject(cx));
  if (!out || !c || !p || !e || !integer(cx, out, "schemaVersion", 2) ||
      !boolean(cx, out, "diagnosticOnly", true) || !u64(cx, out, "currentCallSerial", current_call) || !boolean(cx, out, "recordingComplete", complete) ||
      !boolean(cx, out, "hostStoreDeathObserved", false) || !boolean(cx, out, "resumeEpochObserved", false)) return false;
  if (!boolean(cx, c, "overflow", clock.overflow) || !boolean(cx, c, "monotonicSamplePresent", clock.monotonicSamplePresent) ||
      !boolean(cx, c, "adjustmentOverflow", clock.adjustmentOverflow) || !boolean(cx, c, "wizenSamplePresent", clock.wizenSamplePresent) ||
      !u64(cx, c, "offsetNs", clock.offsetNs) || !u64(cx, c, "monotonicCalls", clock.monotonicCalls) ||
      !u64(cx, c, "lastMonotonicRawNs", clock.lastMonotonicRawNs) || !u64(cx, c, "lastOffsetAppliedNs", clock.lastOffsetAppliedNs) ||
      !u64(cx, c, "lastMonotonicAdjustedNs", clock.lastMonotonicAdjustedNs) || !u64(cx, c, "wizenTransitions", clock.wizenTransitions) ||
      !u64(cx, c, "lastWizenRawNs", clock.lastWizenRawNs) || !u64(cx, c, "lastWizenOffsetBeforeNs", clock.lastWizenOffsetBeforeNs) ||
      !u64(cx, c, "lastWizenOffsetAfterNs", clock.lastWizenOffsetAfterNs)) return false;
  if (!boolean(cx, p, "originPresent", performance.originPresent) || !i64(cx, p, "originCount", performance.originCount) ||
      !u64(cx, p, "periodNumerator", performance.periodNumerator) || !u64(cx, p, "periodDenominator", performance.periodDenominator)) return false;
  if (!u64(cx, e, "callEntries", embedding.callEntries) || !u64(cx, e, "firstCallClears", embedding.firstCallClears) ||
      !u64(cx, e, "originEmplacements", embedding.originEmplacements) || !boolean(cx, e, "entryObserved", embedding.entryObserved) ||
      !boolean(cx, e, "lastEntryHadFirstCall", embedding.lastEntryHadFirstCall) || !boolean(cx, e, "lastEntryHadClocks", embedding.lastEntryHadClocks)) return false;
  if (!object(cx, out, "clock", c) || !object(cx, out, "performance", p) || !object(cx, out, "embedding", e)) return false;
  args.rval().setObject(*out); return true;
}
bool run_selector_probe_v2(JSContext* cx, unsigned argc, JS::Value* vp) {
  REQUEST_HANDLER_ONLY("starling:test-clock-lifecycle.probeAllInvalidV2");
  const auto args = JS::CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, "probeAllInvalidV2", 1)) return false;
  if (!args[0].isInt32() || args[0].toInt32() < 1 || args[0].toInt32() > static_cast<std::int32_t>(MaxInvalidSelectorTasks)) {
    JS_ReportErrorASCII(cx, "PRIVATE_SELECTOR_V2: primitive integer count1..8 required"); return false;
  }
  SelectorProbeResult captured;
  if (!probe_all_invalid_selector(api::Engine::get(cx), static_cast<std::uint32_t>(args[0].toInt32()), captured)) return false;
  JS::RootedObject out(cx, JS_NewPlainObject(cx)), before(cx), queued(cx), after(cx);
  if (!out || !snapshot_object(cx, captured.before, &before) || !snapshot_object(cx, captured.queued, &queued) ||
      !snapshot_object(cx, captured.after, &after) || !integer(cx, out, "schemaVersion", 2) ||
      !integer(cx, out, "requestedCount", static_cast<int>(captured.requested)) || !boolean(cx, out, "diagnosticOnly", true) ||
      !boolean(cx, out, "selectedNone", captured.selectedNone) || !boolean(cx, out, "actualEngineQueueUsed", true) ||
      !boolean(cx, out, "selectorOnly", true) || !boolean(cx, out, "naturalEventLoopSettlementObserved", false) ||
      !boolean(cx, out, "hostPollableResourcesCreated", false) || !boolean(cx, out, "timerResourceDropsObserved", false) ||
      !object(cx, out, "before", before) || !object(cx, out, "queued", queued) || !object(cx, out, "after", after) ||
      !probe_counts(cx, out, "probeBefore", captured.probeBefore) || !probe_counts(cx, out, "probeAfter", captured.probeAfter)) return false;
  args.rval().setObject(*out); return true;
}
const JSFunctionSpec functions[] = {
  JS_FN("snapshot", read_snapshot, 0, JSPROP_ENUMERATE),
  JS_FN("clockStateV2", read_clock_state_v2, 0, JSPROP_ENUMERATE),
  JS_FN("probeAllInvalidV2", run_selector_probe_v2, 1, JSPROP_ENUMERATE), JS_FS_END};
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
