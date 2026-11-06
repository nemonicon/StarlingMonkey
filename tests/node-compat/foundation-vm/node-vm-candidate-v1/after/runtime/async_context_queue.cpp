// SOURCE-ONLY DRAFT. No native compilation/execution has verified this code.
#include "async_context_queue.h"
#include "async_context_runtime.h"
#include "node_tick_queue.h"
#include "js/CallAndConstruct.h"
#include "js/Exception.h"
#include "js/Object.h"
#include "js/Realm.h"
#include "js/TracingAPI.h"
#include "js/Utility.h"
#include "js/Wrapper.h"
#include "jsapi.h"
#include "jsfriendapi.h"
#include <cstring>
#include <utility>

namespace core::async_context {
using namespace JS;
namespace {
bool unsupported(JSContext* cx, const char* message) {
  return InternalTickQueue::fail(cx, JSEXN_TYPEERR,
      "ERR_SM_NODE_ASYNC_CONTEXT_UNSUPPORTED", message);
}
// Same pending-exception/report closure operation as the pinned internal
// ReportExceptionClosure (ErrorReporting.cpp), using installed public APIs.
class ReportException final : public js::ScriptEnvironmentPreparer::Closure {
  HandleValue exception_;
public:
  explicit ReportException(HandleValue exception) : exception_(exception) {}
  bool operator()(JSContext* cx) override {
    JS_SetPendingException(cx, exception_, ExceptionStackBehavior::Capture);
    return false;
  }
};
} // namespace
void ContextJobQueue::Entry::trace(JSTracer* trc) {
  TraceEdge(trc, &job, "ALS Promise job");
  TraceEdge(trc, &resource, "ALS Promise execution resource");
}
void ContextJobQueue::realms(Realm* content, Realm* initializer) {
  MOZ_RELEASE_ASSERT(!content_realm_ && !initializer_realm_);
  content_realm_ = content;
  initializer_realm_ = initializer;
}
bool ContextJobQueue::allowed_realm(JSObject* object) const {
  Realm* realm = JS::GetObjectRealmOrNull(object);
  return realm && (realm == content_realm_ || realm == initializer_realm_);
}
bool ContextJobQueue::getHostDefinedData(JSContext* cx,
                                        MutableHandleObject data) const {
  // Only self-hosted/standard-class setup precedes ResourceStore initialization.
  // Engine integration MUST complete store/realm setup before application code.
  if (!resources_.ready()) { data.set(nullptr); return true; }
  return resources_.capture(cx, data);
}
bool ContextJobQueue::getHostDefinedGlobal(JSContext*,
                                          MutableHandleObject global) const {
  global.set(nullptr);
  return true;
}
bool ContextJobQueue::enqueuePromiseJob(JSContext* cx, HandleObject promise,
    HandleObject job, HandleObject, HandleObject host_data) {
  if (is_data_realm(JS::GetObjectRealmOrNull(job))) {
    note_data_realm_async(JS::GetObjectRealmOrNull(job));
    return unsupported(cx, "node:vm data realm async jobs are outside this profile");
  }
  if (!resources_.ready() || !allowed_realm(job))
    return unsupported(cx, "Promise job outside initialized ALS realms");
  if (storage_.get().jobs.length() - storage_.get().cursor >= MaxPendingJobs)
    return InternalTickQueue::fail(cx, JSEXN_RANGEERR,
        "ERR_SM_NODE_ASYNC_CONTEXT_LIMIT", "Pending Promise job limit exceeded");
  RootedObject resource(cx), target_promise(cx);
  // This read is deliberately private ABI at exact SM147/9dab. Never infer a
  // generic holder layout; unknown jobs refuse rather than borrow resolver ALS.
  if (!js::FunctionHasNativeReserved(job))
    return unsupported(cx, "Unknown Promise job function representation");
  RootedValue payload(cx, js::GetFunctionNativeReserved(job, 0));
  if (!payload.isObject()) return unsupported(cx, "Unknown Promise job payload");
  RootedObject holder(cx, js::CheckedUnwrapStatic(&payload.toObject()));
  if (!holder || !allowed_realm(holder))
    return unsupported(cx, "Inaccessible or foreign Promise job payload");
  const JSClass* clasp = JS::GetClass(holder);
  if (std::strcmp(clasp->name, "PromiseReactionRecord") == 0) {
    if (JSCLASS_RESERVED_SLOTS(clasp) != 11)
      return unsupported(cx, "Unmatched SM147 PromiseReactionRecord layout");
    RootedValue capability(cx, JS::GetReservedSlot(holder, 0));
    if (!capability.isObjectOrNull())
      return unsupported(cx, "Unexpected Promise reaction capability");
    if (capability.isObject()) {
      RootedObject result(cx, js::CheckedUnwrapStatic(&capability.toObject()));
      if (!result || !allowed_realm(result))
        return unsupported(cx, "Foreign Promise reaction capability");
      if (JS::IsPromiseObject(result)) target_promise = result;
      else return unsupported(cx,
          "Non-Promise species has no proved cross-request execution resource");
    }
  } else if (JS::IsPromiseObject(holder)) {
    target_promise = holder; // ResolveThenableJob's original target Promise.
  } else {
    return unsupported(cx, "Unknown native Promise job holder class");
  }
  if (!resource && !target_promise && promise) {
    RootedObject unwrapped(cx, js::CheckedUnwrapStatic(promise));
    if (!unwrapped || !allowed_realm(unwrapped) || !JS::IsPromiseObject(unwrapped))
      return unsupported(cx, "Untracked Promise enqueue argument");
    target_promise = unwrapped;
  }
  if (!resource && target_promise) {
    RootedObject metadata(cx, js::GetAllocationMetadata(target_promise));
    if (!ResourceStore::is_resource(metadata))
      return unsupported(cx, "Promise was created before ALS metadata installation");
    resource = metadata;
  }
  if (!resource && host_data) {
    RootedObject captured(cx, js::CheckedUnwrapStatic(host_data));
    if (!ResourceStore::is_resource(captured) || !allowed_realm(captured))
      return unsupported(cx, "Unmatched Promise registration resource");
    resource = captured;
  }
  // Validated optimized await/native reactions enqueue during registration;
  // null is not used for a captured empty pending registration.
  if (!resource && !resources_.capture(cx, &resource)) return false;
  if (!allowed_realm(resource) ||
      JS::GetCompartment(resource) != JS::GetCompartment(job))
    return unsupported(cx, "Promise job and execution resource compartments differ");
  if (!storage_.get().jobs.append(Entry(job, resource))) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  JS::JobQueueMayNotBeEmpty(cx);
  return true;
}
bool ContextJobQueue::empty() const {
  return storage_.get().cursor == storage_.get().jobs.length();
}
bool ContextJobQueue::require_quiescent(JSContext* cx) const {
  if (dispatch_rejected_.load())
    return unsupported(cx, "SM dispatch was attempted in the no-off-thread ALS profile");
  if (draining_ || stopped_ || !empty())
    return InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_ASYNC_CONTEXT_STATE",
        "ALS Promise queue must be empty, inactive and successful at this boundary");
  return true;
}
bool ContextJobQueue::reject_dispatch(void* closure,
    js::UniquePtr<JS::Dispatchable>&&) {
  static_cast<ContextJobQueue*>(closure)->dispatch_rejected_.store(true);
  return false; // Never accepts a runnable it cannot eventually execute.
}
bool ContextJobQueue::reject_delayed(void* closure,
    js::UniquePtr<JS::Dispatchable>&& task, uint32_t) {
  return reject_dispatch(closure, std::move(task));
}
void ContextJobQueue::runJobs(JSContext* cx) {
  if (draining_) return;
  if (JS_IsExceptionPending(cx)) { stopped_ = true; return; }
  if (dispatch_rejected_.load()) {
    unsupported(cx, "SM off-thread or delayed dispatch is outside this ALS profile");
    stopped_ = true;
    return;
  }
  draining_ = true;
  struct Exit { bool& value; ~Exit() { value = false; } } exit{draining_};
  stopped_ = false;
  auto& storage = storage_.get();
  size_t executed = 0;
  while (!empty()) {
    if (dispatch_rejected_.load()) {
      unsupported(cx, "SM off-thread or delayed dispatch is outside this ALS profile");
      stopped_ = true;
      return;
    }
    if (executed++ >= MaxJobsPerDrain) {
      InternalTickQueue::fail(cx, JSEXN_RANGEERR,
          "ERR_SM_NODE_ASYNC_CONTEXT_LIMIT", "Promise checkpoint work limit exceeded");
      stopped_ = true;
      return;
    }
    RootedObject job(cx, storage.jobs[storage.cursor].job);
    RootedObject resource(cx, storage.jobs[storage.cursor].resource);
    storage.jobs[storage.cursor].job = nullptr;
    storage.jobs[storage.cursor].resource = nullptr;
    ++storage.cursor;
    if (empty()) JS::JobQueueIsEmpty(cx);
    ResourceStore::Scope scope(cx, resources_, resource);
    JSAutoRealm realm(cx, job);
    RootedValue ignored(cx);
    if (!JS::Call(cx, UndefinedHandleValue, job, HandleValueArray::empty(), &ignored)) {
      if (!JS_IsExceptionPending(cx)) continue;
      RootedValue exception(cx);
      const bool got = JS_GetPendingException(cx, &exception);
      JS_ClearPendingException(cx);
      if (got) {
        ReportException report(exception);
        RootedObject report_global(cx, JS::CurrentGlobalOrNull(cx));
        js::PrepareScriptEnvironmentAndInvoke(cx, report_global, report);
      }
    }
  }
  storage.jobs.clear();
  storage.cursor = 0;
  if (dispatch_rejected_.load()) {
    unsupported(cx, "SM off-thread or delayed dispatch is outside this ALS profile");
    stopped_ = true;
  }
}
class ContextJobQueue::Saved final : public SavedJobQueue {
  ContextJobQueue& queue_;
  PersistentRooted<Storage> saved_;
  bool draining_, stopped_;
public:
  Saved(JSContext* cx, ContextJobQueue& queue)
      : queue_(queue), saved_(cx), draining_(queue.draining_), stopped_(queue.stopped_) {
    std::swap(queue_.storage_.get().jobs, saved_.get().jobs);
    std::swap(queue_.storage_.get().cursor, saved_.get().cursor);
    queue_.draining_ = queue_.stopped_ = false;
  }
  ~Saved() override {
    MOZ_RELEASE_ASSERT(queue_.empty());
    queue_.storage_.get().jobs.clear();
    queue_.storage_.get().cursor = 0;
    std::swap(queue_.storage_.get().jobs, saved_.get().jobs);
    std::swap(queue_.storage_.get().cursor, saved_.get().cursor);
    queue_.draining_ = draining_;
    queue_.stopped_ = stopped_;
  }
};
js::UniquePtr<JS::JobQueue::SavedJobQueue>
ContextJobQueue::saveJobQueue(JSContext* cx) {
  auto saved = js::MakeUnique<Saved>(cx, *this);
  if (!saved) JS_ReportOutOfMemory(cx);
  return saved;
}
} // namespace core::async_context
