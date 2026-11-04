// Isolated diagnostic builtin. Never linked into a production profile.
#include "extension-api.h"
#include "js/CallAndConstruct.h"
#include "js/GCAPI.h"
#include "js/GCVector.h"
#include "js/Object.h"
#include "js/Prefs.h"
#include "js/Promise.h"
#include "js/friend/MicroTask.h"
#include "jsfriendapi.h"
#include "js/Realm.h"
#include "js/Wrapper.h"
#include <cstring>
#include <map>

using namespace JS;
namespace diagnostics::async_context {
namespace {
const JSClass TokenClass = {"ContextProbeToken", JSCLASS_HAS_RESERVED_SLOTS(1), nullptr};
PersistentRootedObject empty_token;
PersistentRootedObject current_token;
uint32_t captures = 0, enqueues = 0, with_metadata = 0, creation_choices = 0, fallbacks = 0;
uint32_t runs = 0, metadata_objects = 0, metadata_promises = 0;
bool original_microtasks = false;
JS::Realm* content_realm = nullptr;
JS::Realm* initializer_realm = nullptr;
uint32_t private_records = 0, private_nonpromise = 0;

struct Entry {
  Heap<JSObject*> job;
  Heap<JSObject*> token;
  Entry() = default;
  Entry(JSObject* j, JSObject* t) : job(j), token(t) {}
  void trace(JSTracer* trc) {
    TraceEdge(trc, &job, "probe promise job");
    TraceEdge(trc, &token, "probe context token");
  }
};
struct Storage {
  GCVector<Entry, 0, js::SystemAllocPolicy> jobs;
  size_t cursor = 0;
  void trace(JSTracer* trc) { jobs.trace(trc); }
};
PersistentRooted<Storage> storage;

class Scope {
  RootedObject previous_;
 public:
  Scope(JSContext* cx, HandleObject token) : previous_(cx, current_token) { current_token = token; }
  ~Scope() { current_token = previous_; }
};

// This builder is installed ONLY in the content realm. Tokens are created in
// that same realm, as required by Realm::setNewObjectMetadata. It allocates no
// JS object itself. The engine's metadata table uses its documented fatal-OOM
// policy; this remains an experiment, not a production ALS implementation.
class Metadata final : public js::AllocationMetadataBuilder {
 public:
  JSObject* build(JSContext*, HandleObject object, js::AutoEnterOOMUnsafeRegion&) const override {
    metadata_objects++;
    if (!JS::IsPromiseObject(object)) return nullptr;
    metadata_promises++;
    return current_token;
  }
};
Metadata metadata_builder;

class Queue final : public JS::JobQueue {
  bool draining_ = false;
 public:
  bool getHostDefinedData(JSContext*, MutableHandleObject data) const override {
    captures++;
    // Non-null EMPTY is essential: null is also SpiderMonkey's optimized-out
    // sentinel and cannot represent a pending reaction's captured empty store.
    data.set(current_token);
    return true;
  }
  bool getHostDefinedGlobal(JSContext*, MutableHandleObject global) const override {
    global.set(nullptr); // No fake incumbent global or context-bearing realm.
    return true;
  }
  bool enqueuePromiseJob(JSContext* cx, HandleObject promise, HandleObject job,
                         HandleObject, HandleObject host_data) override {
    enqueues++;
    RootedObject token(cx);
    // PRIVATE ABI, pinned to SM9dab/147: the legacy job's first native slot
    // carries the reaction record or thenable target promise. The public
    // callback intentionally replaces non-Promise result capabilities with
    // null, conflating them with await/native reactions. Inspect only after
    // validating the native-function representation, record class, slot count
    // and retained realm; never choose the execution realm from this token.
    if (js::FunctionHasNativeReserved(job)) {
      RootedValue payload(cx, js::GetFunctionNativeReserved(job, 0));
      if (payload.isObject()) {
        RootedObject holder(cx, js::CheckedUnwrapStatic(&payload.toObject()));
        if (!holder) { JS_ReportErrorASCII(cx,"dead/inaccessible probe job payload"); return false; }
        const JSClass* clasp=JS::GetClass(holder);
        if (std::strcmp(clasp->name,"PromiseReactionRecord")==0) {
          JS::Realm* record_realm=JS::GetObjectRealmOrNull(holder);
          JS::Realm* job_realm=JS::GetObjectRealmOrNull(job);
          if (JSCLASS_RESERVED_SLOTS(clasp)!=11 ||
              (record_realm!=content_realm && record_realm!=initializer_realm) ||
              (job_realm!=content_realm && job_realm!=initializer_realm)) {
            JS_ReportErrorASCII(cx,"unmatched pinned PromiseReactionRecord ABI");return false;
          }
          private_records++;
          RootedValue capability(cx,JS::GetReservedSlot(holder,0));
          if(!capability.isObjectOrNull()) {JS_ReportErrorASCII(cx,"invalid reaction capability slot");return false;}
          if(capability.isObject()) {
            RootedObject result(cx,js::CheckedUnwrapStatic(&capability.toObject()));
            if(!result){JS_ReportErrorASCII(cx,"inaccessible reaction capability");return false;}
            if(!JS::IsPromiseObject(result)) { token=empty_token;private_nonpromise++; }
          }
        }
      }
    }
    if (!token && promise && JS::IsPromiseObject(promise)) {
      JSObject* candidate = js::GetAllocationMetadata(promise);
      if (candidate && JS::GetClass(candidate) == &TokenClass) {
        token = candidate;
        creation_choices++;
      }
    }
    if (!token && host_data) { token = host_data; with_metadata++; }
    if (!token) { token = current_token; fallbacks++; }
    if (!storage.get().jobs.append(Entry(job, token))) {
      JS_ReportOutOfMemory(cx);
      return false;
    }
    JS::JobQueueMayNotBeEmpty(cx);
    return true;
  }
  bool empty() const override { return storage.get().cursor == storage.get().jobs.length(); }
  bool isDrainingStopped() const override { return false; }
  void runJobs(JSContext* cx) override {
    if (draining_) return;
    draining_ = true;
    auto& state = storage.get();
    while (!empty()) {
      RootedObject job(cx, state.jobs[state.cursor].job);
      RootedObject token(cx, state.jobs[state.cursor].token);
      state.jobs[state.cursor].job = nullptr;
      state.jobs[state.cursor].token = nullptr;
      state.cursor++;
      // Exercise the real already-resolved-await skipping path. A later
      // enqueue calls JobQueueMayNotBeEmpty, preserving SM's queue invariant.
      if (empty()) JS::JobQueueIsEmpty(cx);
      Scope scope(cx, token);
      JSAutoRealm realm(cx, job);
      RootedValue value(cx);
      runs++;
      if (!JS::Call(cx, UndefinedHandleValue, job, HandleValueArray::empty(), &value)) break;
    }
    if (empty()) { state.jobs.clear(); state.cursor = 0; }
    draining_ = false;
  }
 protected:
  class Saved final : public SavedJobQueue {
    Queue& queue_;
    PersistentRooted<Storage> saved_;
    bool draining_;
   public:
    Saved(JSContext* cx, Queue& queue) : queue_(queue), saved_(cx), draining_(queue.draining_) {
      std::swap(storage.get().jobs, saved_.get().jobs);
      std::swap(storage.get().cursor, saved_.get().cursor);
      queue.draining_ = false;
    }
    ~Saved() override {
      MOZ_RELEASE_ASSERT(queue_.empty());
      storage.get().jobs.clear(); storage.get().cursor = 0;
      std::swap(storage.get().jobs, saved_.get().jobs);
      std::swap(storage.get().cursor, saved_.get().cursor);
      queue_.draining_ = draining_;
    }
  };
  js::UniquePtr<SavedJobQueue> saveJobQueue(JSContext* cx) override {
    auto saved = js::MakeUnique<Saved>(cx, *this);
    if (!saved) JS_ReportOutOfMemory(cx);
    return saved;
  }
};
Queue queue;

bool read(JSContext*, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  args.rval().set(JS::GetReservedSlot(current_token, 0));
  return true;
}
bool with(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc < 2 || !args[1].isObject() || !JS::IsCallable(&args[1].toObject())) {
    JS_ReportErrorASCII(cx, "probe.with requires a value and callback"); return false;
  }
  RootedObject token(cx, JS_NewObject(cx, &TokenClass));
  if (!token) return false;
  JS::SetReservedSlot(token, 0, args[0]);
  Scope scope(cx, token);
  return JS::Call(cx, UndefinedHandleValue, args[1], HandleValueArray::empty(), args.rval());
}
bool native_then(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc < 2 || !args[0].isObject() || !args[1].isObject()) {
    JS_ReportErrorASCII(cx, "probe.nativeThen requires promise and callback"); return false;
  }
  RootedObject promise(cx, &args[0].toObject()), callback(cx, &args[1].toObject());
  if (!JS::AddPromiseReactions(cx, promise, callback, nullptr)) return false;
  args.rval().setUndefined(); return true;
}
bool gc(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  JS::PrepareForFullGC(cx);
  JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API);
  args.rval().setUndefined(); return true;
}
class Task;
std::map<uint32_t, RefPtr<Task>> tasks;
uint32_t next_task_id = 1;
class Task final : public api::AsyncTask {
  uint32_t index_;
  Heap<JSObject*> callback_;
  Heap<JSObject*> token_;
  bool active_ = true;
 public:
  Task(uint32_t index, HandleObject callback) : index_(index), callback_(callback), token_(current_token) {
    handle_ = IMMEDIATE_TASK_HANDLE;
  }
  bool run(api::Engine* engine) override {
    JSContext* cx=engine->cx();
    RootedObject callback(cx,callback_), token(cx,token_);
    active_=false; handle_=INVALID_POLLABLE_HANDLE;
    callback_=nullptr; token_=nullptr; tasks.erase(index_);
    engine->decr_event_loop_interest();
    Scope scope(cx,token);
    RootedValue value(cx);
    return JS::Call(cx,UndefinedHandleValue,callback,HandleValueArray::empty(),&value);
  }
  bool cancel(api::Engine* engine) override {
    if (!active_) return false;
    active_=false;handle_=INVALID_POLLABLE_HANDLE;
    callback_=nullptr;token_=nullptr;
    engine->decr_event_loop_interest();
    return true;
  }
  void trace(JSTracer* tracer) override {
    TraceEdge(tracer,&callback_,"probe async callback");
    TraceEdge(tracer,&token_,"probe async context");
  }
};
bool schedule(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);
  if(argc<1 || !args[0].isObject() || !JS::IsCallable(&args[0].toObject())) {
    JS_ReportErrorASCII(cx,"probe.schedule requires callback");return false;
  }
  RootedObject callback(cx,&args[0].toObject());
  uint32_t index=next_task_id++;
  RefPtr<Task> task=js_new<Task>(index,callback);
  if(!task) {JS_ReportOutOfMemory(cx);return false;}
  tasks.emplace(index,task);
  auto* engine=api::Engine::get(cx);
  engine->incr_event_loop_interest();engine->queue_async_task(task);
  args.rval().setNumber(index);return true;
}
bool cancel(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);uint32_t index;
  if(!JS::ToUint32(cx,args.get(0),&index))return false;
  auto it=tasks.find(index);if(it==tasks.end()){args.rval().setBoolean(false);return true;}
  RefPtr<Task> task=it->second;
  bool removed=api::Engine::get(cx)->cancel_async_task(task);
  tasks.erase(index);args.rval().setBoolean(removed);return true;
}
bool stats(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  RootedObject object(cx, JS_NewPlainObject(cx)); if (!object) return false;
  struct Count { const char* name; uint32_t value; } counts[] = {
    {"captures", captures},{"enqueues", enqueues},{"metadata",with_metadata},
    {"creationChoices",creation_choices},{"fallbacks",fallbacks},{"runs",runs},
    {"metadataObjects",metadata_objects},{"metadataPromises",metadata_promises},
    {"privateReactionRecords",private_records},{"privateNonPromiseCapabilities",private_nonpromise},
  };
  for (const auto& count : counts)
    if (!JS_DefineProperty(cx, object, count.name, count.value, JSPROP_ENUMERATE)) return false;
  if (!JS_DefineProperty(cx, object, "originalNativeMicrotaskQueue", original_microtasks, JSPROP_ENUMERATE)) return false;
  if (!JS_DefineProperty(cx, object, "nativeMicrotaskQueueNow", JS::Prefs::use_js_microtask_queue(), JSPROP_ENUMERATE)) return false;
  args.rval().setObject(*object); return true;
}
const JSFunctionSpec methods[] = {
  JS_FN("read",read,0,0),JS_FN("with",with,2,0),JS_FN("nativeThen",native_then,2,0),
  JS_FN("gc",gc,0,0),JS_FN("stats",stats,0,0),
  JS_FN("schedule",schedule,1,0),JS_FN("cancel",cancel,1,0),JS_FS_END,
};
} // namespace

bool install(api::Engine* engine) {
  JSContext* cx = engine->cx();
  content_realm=JS::GetObjectRealmOrNull(engine->global());
  initializer_realm=JS::GetObjectRealmOrNull(engine->init_script_global());
  original_microtasks = JS::Prefs::use_js_microtask_queue();
  if (!original_microtasks || JS::HasAnyMicroTasks(cx)) {
    JS_ReportErrorASCII(cx, "context probe must install before application jobs on the pinned default queue");
    return false;
  }
  empty_token.init(cx, JS_NewObject(cx, &TokenClass));
  if (!empty_token) return false;
  JS::SetReservedSlot(empty_token, 0, UndefinedValue());
  current_token.init(cx, empty_token);
  storage.init(cx);
  JS::Prefs::set_use_js_microtask_queue(false);
  JS::SetJobQueue(cx, &queue);
  js::SetAllocationMetadataBuilder(cx, &metadata_builder);
  RootedObject probe(cx, JS_NewPlainObject(cx));
  if (!probe || !JS_DefineFunctions(cx, probe, methods)) return false;
  return JS_DefineProperty(cx, engine->global(), "__asyncContextProbe", probe, 0);
}
} // namespace diagnostics::async_context
