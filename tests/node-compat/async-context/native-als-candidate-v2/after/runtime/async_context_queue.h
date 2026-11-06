// SOURCE-ONLY DRAFT; exact SM147 legacy-queue interface, not a guest result.
#ifndef STARLING_ASYNC_CONTEXT_QUEUE_H
#define STARLING_ASYNC_CONTEXT_QUEUE_H
#include "async_context_store.h"
#include "js/GCVector.h"
#include "js/Promise.h"
#include <atomic>

namespace core::async_context {
class ContextJobQueue final : public JS::JobQueue {
  struct Entry {
    JS::Heap<JSObject*> job{nullptr};
    JS::Heap<JSObject*> resource{nullptr};
    Entry() = default;
    Entry(JSObject* j, JSObject* r) : job(j), resource(r) {}
    void trace(JSTracer* trc);
  };
  struct Storage {
    JS::GCVector<Entry, 0, js::SystemAllocPolicy> jobs;
    size_t cursor = 0;
    void trace(JSTracer* trc) { jobs.trace(trc); }
  };
  class Saved;
  ResourceStore& resources_;
  JS::PersistentRooted<Storage> storage_;
  JS::Realm* content_realm_ = nullptr;
  JS::Realm* initializer_realm_ = nullptr;
  std::atomic<bool> dispatch_rejected_{false};
  bool draining_ = false;
  bool stopped_ = false;
  bool allowed_realm(JSObject* object) const;
public:
  static constexpr size_t MaxPendingJobs = 4096, MaxJobsPerDrain = 65536;
  ContextJobQueue(JSContext* cx, ResourceStore& resources)
      : resources_(resources), storage_(cx) {}
  void realms(JS::Realm* content, JS::Realm* initializer);
  bool getHostDefinedData(JSContext*, JS::MutableHandleObject) const override;
  bool getHostDefinedGlobal(JSContext*, JS::MutableHandleObject) const override;
  bool enqueuePromiseJob(JSContext*, JS::HandleObject, JS::HandleObject,
                         JS::HandleObject, JS::HandleObject) override;
  void runJobs(JSContext*) override;
  bool empty() const override;
  bool require_quiescent(JSContext*) const;
  bool isDrainingStopped() const override { return stopped_; }
  // No GC/JS/host work on a foreign thread. All submissions are refused;
  // the owning JS checkpoint observes the sticky unsupported-feature flag.
  static bool reject_dispatch(void*, js::UniquePtr<JS::Dispatchable>&&);
  static bool reject_delayed(void*, js::UniquePtr<JS::Dispatchable>&&, uint32_t);
protected:
  js::UniquePtr<SavedJobQueue> saveJobQueue(JSContext*) override;
};
} // namespace core::async_context
#endif
