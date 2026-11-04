// Test-only use of SpiderMonkey's genuine allocator failure simulator.
// Never included in a normal profile build; no JavaScript control is exposed.
#ifndef STARLING_NODE_COMPAT_OOM_TESTING_H
#define STARLING_NODE_COMPAT_OOM_TESTING_H

#if !defined(NODE_COMPAT_OOM_TESTING)
#error "oom-testing.h is only for the dedicated fault-instrumented engine"
#endif
#if !defined(DEBUG) && !defined(JS_OOM_BREAKPOINT)
#error "NODE_COMPAT_OOM_TESTING requires SpiderMonkey DEBUG or JS_OOM_BREAKPOINT artifacts"
#endif

#include "js/Exception.h"
#include "js/Utility.h"

#include <array>
#include <cstdint>
#include <utility>

namespace builtins::node_compat::oom_testing {

enum class Point : uint8_t { DecodeUTF8, DecodeArray, EncodeStaging, EncodeString, Count };
inline std::array<bool, static_cast<size_t>(Point::Count)> fired{};
inline size_t live_owned_chars = 0;
inline size_t owned_acquisitions = 0;
inline size_t owned_releases = 0;

// Delegate the real deallocation used by JS::UniqueChars. Counters turn an
// early-return leak or a second owner into a failing assertion.
struct TrackedFreePolicy {
  void operator()(char *pointer) const {
    if (!pointer) return;
    MOZ_RELEASE_ASSERT(live_owned_chars > 0, "unbalanced Buffer temporary ownership");
    JS::FreePolicy{}(pointer);
    --live_owned_chars;
    ++owned_releases;
  }
};
using Chars = mozilla::UniquePtr<char[], TrackedFreePolicy>;

inline Chars track(JS::UniqueChars pointer) {
  if (pointer) {
    ++live_owned_chars;
    ++owned_acquisitions;
  }
  return Chars(pointer.release());
}

// Declare before per-call owners, so their destructors execute first.
struct KernelAudit {
  KernelAudit() {
    MOZ_RELEASE_ASSERT(live_owned_chars == 0, "previous Buffer call leaked a temporary");
  }
  ~KernelAudit() {
    MOZ_RELEASE_ASSERT(live_owned_chars == 0, "Buffer failure/success path leaked a temporary");
    MOZ_RELEASE_ASSERT(owned_acquisitions == owned_releases,
                       "Buffer temporary allocation/free counters differ");
  }
};

class FaultScope {
  JSContext *cx_;
  uint32_t previous_thread_ = 0;
  bool armed_ = false;

public:
  FaultScope(JSContext *cx, Point point) : cx_(cx) {
    // Snapshot calls remain normal. The first deployed use of each site fails
    // once; subsequent uses exercise recovery without any JavaScript hook.
    auto index = static_cast<size_t>(point);
    if (api::Engine::get(cx)->state() != api::EngineState::Initialized || fired[index]) return;
    previous_thread_ = js::oom::GetThreadType();
    MOZ_RELEASE_ASSERT(js::oom::simulator.targetThread() == js::THREAD_TYPE_NONE,
                       "nested or pre-existing OOM simulation");
    js::oom::SetThreadType(js::THREAD_TYPE_MAIN);
    fired[index] = true;
    armed_ = true;
    js::oom::simulator.simulateFailureAfter(js::oom::FailureSimulator::Kind::OOM,
                                            1, js::THREAD_TYPE_MAIN, true);
  }

  void finish(bool failed) {
    if (!armed_) return;
    const bool tripped = js::oom::HadSimulatedOOM();
    // Reset before native owners unwind and before JS catches the real pending
    // OOM. Manufacturing an Error here would itself require allocation.
    js::oom::simulator.reset();
    js::oom::SetThreadType(static_cast<js::ThreadType>(previous_thread_));
    armed_ = false;
    MOZ_RELEASE_ASSERT(tripped, "selected Buffer site did not reach an allocator checkpoint");
    MOZ_RELEASE_ASSERT(failed, "selected Buffer allocator failure was unexpectedly recovered");
    MOZ_RELEASE_ASSERT(JS_IsThrowingOutOfMemory(cx_), "Buffer failure was not a real pending OOM");
  }

  ~FaultScope() {
    MOZ_RELEASE_ASSERT(!armed_, "Buffer OOM scope did not finish");
  }
};

template <Point point, typename Operation>
auto allocate(JSContext *cx, Operation operation) {
  FaultScope fault(cx, point);
  auto result = operation();
  fault.finish(!result);
  return result;
}

} // namespace builtins::node_compat::oom_testing

#endif
