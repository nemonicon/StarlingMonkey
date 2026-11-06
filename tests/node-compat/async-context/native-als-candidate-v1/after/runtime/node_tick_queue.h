// UNAPPLIED, UNCOMPILED proposal: owned/traced by the existing TaskQueue root.
#ifndef STARLING_INTERNAL_NODE_TICK_QUEUE_H
#define STARLING_INTERNAL_NODE_TICK_QUEUE_H
#include "js/CallArgs.h"
#include "js/ErrorReport.h"
#include "js/GCVector.h"
#include "js/RootingAPI.h"
#include "js/TypeDecls.h"
#include <cstddef>
#include <cstdint>

namespace core {
enum class TickCheckpointOrigin { TaskOrExport, ClassicEvaluation, ModuleEvaluation,
                                  InitializerScript, FinalizerBatch };
class InternalTickQueue {
  struct Tick {
    JS::Heap<JSObject*> callback{nullptr};
    JS::Heap<JSObject*> arguments{nullptr};
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    JS::Heap<JSObject*> resource{nullptr};
#endif
    uint32_t argc = 0;
    void trace(JSTracer* trc);
  };
  JS::GCVector<Tick, 0, js::SystemAllocPolicy> slots_;
  size_t head_ = 0, count_ = 0, argument_count_ = 0;
  bool checkpoint_running_ = false;
  bool drain_ticks(JSContext* cx, size_t& executed);
public:
  static constexpr size_t MaxPending = 4096, MaxArgumentsPerTick = 1024;
  static constexpr size_t MaxPendingArguments = 65536, MaxCallbacksPerCheckpoint = 65536;
  void trace(JSTracer* trc) { slots_.trace(trc); }
  bool enqueue(JSContext* cx, const JS::CallArgs& args);
  bool checkpoint(JSContext* cx, TickCheckpointOrigin origin);
  bool empty_and_inactive() const { return count_ == 0 && !checkpoint_running_; }
  bool checkpoint_running() const { return checkpoint_running_; }
  void discard();
  // Caller must establish the TaskQueue is idle BEFORE cancelling tasks/resetting.
  void reset_storage();
  static bool fail(JSContext* cx, JSExnType type, const char* code, const char* text);
};
} // namespace core
#endif
