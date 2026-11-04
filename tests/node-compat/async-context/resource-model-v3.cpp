// Isolated mutable-resource prototype. Never linked into a production profile.
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
const JSClass StateClass = {"ContextPrototypeState", JSCLASS_HAS_RESERVED_SLOTS(1), nullptr};
const JSClass NodeClass = {"ContextPrototypeStoreNode", JSCLASS_HAS_RESERVED_SLOTS(3), nullptr};
const JSClass ResourceClass = {"ContextPrototypeResource", JSCLASS_HAS_RESERVED_SLOTS(1), nullptr};
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

// Each resource owns a private store list. Child creation copies only enabled
// entries: no mutable nodes are shared. Reusing the resource retains mutations.
// Nodes, states and resources are ordinary traced JS objects with private slots.
JSObject* new_resource(JSContext* cx, HandleObject source, bool enabled_only) {
  RootedObject resource(cx,JS_NewObject(cx,&ResourceClass));
  if(!resource)return nullptr;
  RootedValue head(cx,source?JS::GetReservedSlot(source,0):NullValue());
  RootedObject result(cx);
  while(head.isObject()) {
    RootedObject node(cx,&head.toObject());
    RootedObject state(cx,&JS::GetReservedSlot(node,0).toObject());
    bool duplicate=false;
    for(JSObject* cursor=result;cursor;) {
      if(&JS::GetReservedSlot(cursor,0).toObject()==state){duplicate=true;break;}
      const Value& next=JS::GetReservedSlot(cursor,2);cursor=next.isObject()?&next.toObject():nullptr;
    }
    if(!duplicate && (!enabled_only || JS::GetReservedSlot(state,0).toBoolean())) {
      RootedObject copy(cx,JS_NewObject(cx,&NodeClass));if(!copy)return nullptr;
      JS::SetReservedSlot(copy,0,ObjectValue(*state));
      JS::SetReservedSlot(copy,1,JS::GetReservedSlot(node,1));
      JS::SetReservedSlot(copy,2,ObjectOrNullValue(result));result=copy;
    }
    head=JS::GetReservedSlot(node,2);
  }
  JS::SetReservedSlot(resource,0,ObjectOrNullValue(result));return resource;
}
bool state_argument(JSContext* cx,const CallArgs& args,MutableHandleObject state) {
  if(args.length()<1 || !args[0].isObject() || JS::GetClass(&args[0].toObject())!=&StateClass){JS_ReportErrorASCII(cx,"invalid prototype storage state");return false;}
  state.set(&args[0].toObject());return true;
}
Value find_store(HandleObject state,bool raw) {
  if(!raw && !JS::GetReservedSlot(state,0).toBoolean())return UndefinedValue();
  const Value* head=&JS::GetReservedSlot(current_token,0);
  while(head->isObject()) {
    JSObject* node=&head->toObject();
    if(&JS::GetReservedSlot(node,0).toObject()==state)return JS::GetReservedSlot(node,1);
    head=&JS::GetReservedSlot(node,2);
  }
  return UndefinedValue();
}
class Metadata final : public js::AllocationMetadataBuilder {
 public:
  JSObject* build(JSContext* cx, HandleObject object, js::AutoEnterOOMUnsafeRegion& oom) const override {
    metadata_objects++;
    if(!JS::IsPromiseObject(object))return nullptr;
    metadata_promises++;
    // Supported builder API explicitly makes allocation errors fatal. This
    // experimental allocation cost/policy is NOT approved production behavior.
    JSObject* resource=new_resource(cx,current_token,true);
    if(!resource)oom.crash("async resource prototype metadata");
    return resource;
  }
};
Metadata metadata_builder;

class Queue final : public JS::JobQueue {
  bool draining_ = false;
 public:
  bool getHostDefinedData(JSContext* cx, MutableHandleObject data) const override {
    captures++;
    data.set(new_resource(cx,current_token,true));
    return !!data;
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
      if (candidate && JS::GetClass(candidate) == &ResourceClass) {
        token = candidate;
        creation_choices++;
      }
    }
    if (!token && host_data) { token = host_data; with_metadata++; }
    if (!token) { token = new_resource(cx,current_token,true); if(!token)return false; fallbacks++; }
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

bool create_state(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);RootedObject state(cx,JS_NewObject(cx,&StateClass));
  if(!state)return false;JS::SetReservedSlot(state,0,BooleanValue(false));args.rval().setObject(*state);return true;
}
bool enabled(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);RootedObject state(cx);if(!state_argument(cx,args,&state))return false;
  if(argc>1)JS::SetReservedSlot(state,0,BooleanValue(JS::ToBoolean(args[1])));
  args.rval().set(JS::GetReservedSlot(state,0));return true;
}
bool get_store(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);RootedObject state(cx);if(!state_argument(cx,args,&state))return false;
  args.rval().set(find_store(state,argc>1 && JS::ToBoolean(args[1])));return true;
}
bool set_store(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);RootedObject state(cx);if(!state_argument(cx,args,&state))return false;
  const Value* head=&JS::GetReservedSlot(current_token,0);
  while(head->isObject()) {
    JSObject* node=&head->toObject();
    if(&JS::GetReservedSlot(node,0).toObject()==state){JS::SetReservedSlot(node,1,args.get(1));args.rval().setUndefined();return true;}
    head=&JS::GetReservedSlot(node,2);
  }
  // Existing-entry restoration allocates nothing; a new binding commits only
  // after successful allocation. Children have their own copied list nodes.
  RootedObject node(cx,JS_NewObject(cx,&NodeClass));if(!node)return false;
  JS::SetReservedSlot(node,0,ObjectValue(*state));JS::SetReservedSlot(node,1,args.get(1));
  JS::SetReservedSlot(node,2,JS::GetReservedSlot(current_token,0));
  JS::SetReservedSlot(current_token,0,ObjectValue(*node));args.rval().setUndefined();return true;
}
bool capture_resource(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);RootedObject resource(cx,new_resource(cx,current_token,true));
  if(!resource)return false;args.rval().setObject(*resource);return true;
}
bool run_resource(JSContext* cx,unsigned argc,Value* vp) {
  CallArgs args=CallArgsFromVp(argc,vp);
  if(argc<3 || !args[0].isObject() || JS::GetClass(&args[0].toObject())!=&ResourceClass || !args[1].isObject() || !JS::IsCallable(&args[1].toObject())){JS_ReportErrorASCII(cx,"invalid prototype resource invocation");return false;}
  RootedObject resource(cx,&args[0].toObject());Scope scope(cx,resource);
  return JS::Call(cx,args[2],args[1],HandleValueArray::subarray(HandleValueArray(args),3,argc-3),args.rval());
}
bool native_then(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc < 2 || !args[0].isObject() || !args[1].isObject() || !JS::IsCallable(&args[1].toObject())) {
    JS_ReportErrorASCII(cx, "probe.nativeThen requires promise and callback"); return false;
  }
  RootedObject promise(cx, &args[0].toObject()), callback(cx, &args[1].toObject());
  if(!JS::IsPromiseObject(promise)){JS_ReportErrorASCII(cx,"nativeThen needs an unwrapped Promise");return false;}
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
  Task(uint32_t index, HandleObject callback, HandleObject resource) : index_(index), callback_(callback), token_(resource) {
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
  RootedObject resource(cx,new_resource(cx,current_token,true));if(!resource)return false;
  RefPtr<Task> task=js_new<Task>(index,callback,resource);
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
  JS_FN("createState",create_state,0,0),JS_FN("enabled",enabled,1,0),JS_FN("get",get_store,1,0),JS_FN("set",set_store,2,0),
  JS_FN("capture",capture_resource,0,0),JS_FN("runResource",run_resource,3,0),JS_FN("nativeThen",native_then,2,0),
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
  empty_token.init(cx, new_resource(cx,nullptr,true));
  if (!empty_token) return false;
  // The persistent ROOT resource is mutable and distinct from child captures.
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
