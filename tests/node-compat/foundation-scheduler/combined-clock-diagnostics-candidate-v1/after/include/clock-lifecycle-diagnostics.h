// UNCOMPILED diagnostic-variant source. No current355 engine has these symbols.
#ifndef STARLING_CLOCK_LIFECYCLE_DIAGNOSTICS_H
#define STARLING_CLOCK_LIFECYCLE_DIAGNOSTICS_H
#ifndef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
#error "Private lifecycle diagnostics require their separate diagnostic generation"
#endif
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace diagnostics::clock_lifecycle {
constexpr std::size_t MaxTimerLeases = 512;
enum class Counter : std::size_t {
  QueueEnqueue, QueueDetachRun, QueueDetachCancel, InterestIncr, InterestDecr,
  SelectorCall, PrunedInvalid, SelectorEmpty, PollCall, EmptyPollAttempt,
  TimerConstruct, TimerRetire, TimerDestroy, TimerAcquire,
  TimerDropAttempt, TimerDropReturned, HostMonotonicDropAttempt,
  HostMonotonicDropReturned, ImmediateCacheAcquire, ImmediateCacheUse,
  CallEntered, LoopBoundary, PostCallBoundary, Count
};
inline constexpr const char* CounterNames[] = {
  "queueEnqueue", "queueDetachRun", "queueDetachCancel", "interestIncr", "interestDecr",
  "selectorCall", "prunedInvalid", "selectorEmpty", "pollCall", "emptyPollAttempt",
  "timerConstruct", "timerRetire", "timerDestroy", "timerAcquire",
  "timerDropAttempt", "timerDropReturned", "hostMonotonicDropAttempt",
  "hostMonotonicDropReturned", "immediateCacheAcquire", "immediateCacheUse",
  "callEntered", "loopBoundary", "postCallBoundary"
};
static_assert(sizeof(CounterNames) / sizeof(CounterNames[0]) == static_cast<std::size_t>(Counter::Count));

struct RuntimeCounts {
  std::size_t queued = 0;
  int interest = 0;
  bool loopRunning = false;
  std::size_t timerRegistry = 0;
  bool immediateCacheOwned = false;
};
// These are NEW private definitions in the corresponding afterimages.
// Their declarations are not claims of a current embedding API or linked symbol.
RuntimeCounts runtime_counts();
std::size_t timer_registry_size();
bool immediate_cache_owned();

struct TimerLease {
  std::uint64_t serial = 0;
  std::int32_t timerId = 0;
  std::int32_t privateHandle = -1; // checked internally; never returned to JS
  std::uint64_t acquiredAt = 0;
  std::uint64_t invalidatedAt = 0;
  std::uint64_t dropAttemptAt = 0;
  std::uint64_t dropReturnedAt = 0;
  bool owned = false;
};
struct Boundary {
  bool present = false;
  std::uint64_t callSerial = 0;
  std::uint32_t functionIndex = 0;
  RuntimeCounts runtime;
  bool loopResultObserved = false;
  bool loopReturnedSuccess = false;
  int currentFunction = -1;
  std::size_t freeListSize = 0;
};
struct State {
  std::array<std::uint64_t, static_cast<std::size_t>(Counter::Count)> counts{};
  std::array<TimerLease, MaxTimerLeases> leases{};
  std::size_t usedLeases = 0;
  std::uint64_t eventSerial = 0;
  std::uint64_t callSerial = 0;
  bool overflow = false;
  bool invariantViolation = false;
  Boundary afterLoop;
  Boundary afterPostCall;
};
// C++ inline variable: one diagnostic POD state across the linked translation
// units, to be confirmed by the future real compile/link gate. No JS roots,
// pointers to tasks, allocations, clocks, host calls or collection hooks.
inline State state;

inline std::uint64_t event() {
  if (state.eventSerial == std::numeric_limits<std::uint64_t>::max()) {
    state.overflow = true; return 0;
  }
  return ++state.eventSerial;
}
inline void count(Counter which, std::uint64_t amount = 1) {
  auto& value = state.counts[static_cast<std::size_t>(which)];
  if (amount > std::numeric_limits<std::uint64_t>::max() - value) {
    state.overflow = true; return;
  }
  value += amount;
}
inline std::uint64_t timer_acquired(std::int32_t id, std::int32_t handle) {
  count(Counter::TimerAcquire);
  if (state.usedLeases == MaxTimerLeases) { state.overflow = true; return 0; }
  auto& lease = state.leases[state.usedLeases++];
  lease.serial = state.usedLeases; lease.timerId = id; lease.privateHandle = handle;
  lease.acquiredAt = event(); lease.owned = true;
  if (id <= 0 || handle == -1 || handle == -2) state.invariantViolation = true;
  return lease.serial;
}
inline TimerLease* lease(std::uint64_t serial, std::int32_t handle) {
  if (serial == 0 || serial > state.usedLeases) {
    state.invariantViolation = true; return nullptr;
  }
  auto* row = &state.leases[static_cast<std::size_t>(serial - 1)];
  if (row->serial != serial || row->privateHandle != handle) state.invariantViolation = true;
  return row;
}
inline void timer_drop_begin(std::uint64_t serial, std::int32_t handle,
                             std::int32_t nowInvalid) {
  count(Counter::TimerDropAttempt);
  auto* row = lease(serial, handle);
  if (!row) return;
  if (!row->owned || row->dropAttemptAt != 0 || nowInvalid != -1)
    state.invariantViolation = true;
  row->invalidatedAt = event(); row->dropAttemptAt = event();
}
inline void timer_drop_returned(std::uint64_t serial, std::int32_t handle) {
  count(Counter::TimerDropReturned);
  auto* row = lease(serial, handle);
  if (!row) return;
  if (!row->owned || row->dropAttemptAt == 0 || row->dropReturnedAt != 0)
    state.invariantViolation = true;
  row->dropReturnedAt = event(); row->owned = false;
}
inline void entered_call() {
  count(Counter::CallEntered);
  if (state.callSerial == std::numeric_limits<std::uint64_t>::max()) state.overflow = true;
  else ++state.callSerial;
}
inline void after_loop(std::uint32_t functionIndex, bool success, int currentFunction,
                       std::size_t freeListSize) {
  count(Counter::LoopBoundary);
  state.afterLoop = {true, state.callSerial, functionIndex, runtime_counts(),
                     true, success, currentFunction, freeListSize};
}
inline void after_post_call(std::uint32_t functionIndex, int currentFunction,
                            std::size_t freeListSize) {
  count(Counter::PostCallBoundary);
  state.afterPostCall = {true, state.callSerial, functionIndex, runtime_counts(),
                         false, false, currentFunction, freeListSize};
}
struct Snapshot { State history; RuntimeCounts current; };
inline Snapshot capture() { return {state, runtime_counts()}; }
} // namespace diagnostics::clock_lifecycle
#endif
