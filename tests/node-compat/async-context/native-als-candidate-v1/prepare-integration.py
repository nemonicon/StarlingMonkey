"""Authoring-only afterimages. Never invokes an engine, helper or compiler."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
changes=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def file(name, edits):
 p=REPO/name;before=p.read_bytes();text=before.decode();rows=[]
 for old,new in edits:
  assert text.count(old)==1,(name,'nonunique anchor',old[:100],text.count(old))
  rows.append(dict(before=old,after=new));text=text.replace(old,new,1)
 out=OWN/'after'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
 restored=text
 for row in reversed(rows):
  assert restored.count(row['after'])==1,(name,'nonunique reversal')
  restored=restored.replace(row['after'],row['before'],1)
 assert restored.encode()==before
 changes.append(dict(path=name,beforeSha256=sha(before),beforeBytes=len(before),afterSha256=sha(text.encode()),afterBytes=len(text.encode()),edits=rows))
include='#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE\n#include "async_context_runtime.h"\n#endif\n'
file('include/extension-api.h',[
 ('  AsyncTask() = default;','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  JS::PersistentRootedObject async_context_;
#endif
  explicit AsyncTask(JS::HandleObject resource = JS::NullHandleObject) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    MOZ_RELEASE_ASSERT(resource);
    async_context_.init(Engine::cx(), resource);
#else
    (void)resource;
#endif
  }
  // Capture BEFORE constructors subscribe/commit host handles. Requeues retain
  // the same native cell; PersistentRooted covers every native owner/tracer.
  static bool capture_context(JSContext* cx, JS::MutableHandleObject resource);
  static bool context_from_promise(JSContext* cx, JS::HandleObject promise,
                                    JS::MutableHandleObject resource);
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  JS::HandleObject async_context() const { return async_context_; }
#endif''')])
file('runtime/engine.cpp',[
 ('#include "event_loop.h"','#include "event_loop.h"\n'+include),
 ('  if (!js::UseInternalJobQueues(cx) || !JS::InitSelfHostedCode(cx)) {','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  if (!core::async_context::prepare_before_self_hosted(cx)) return false;
#else
  if (!js::UseInternalJobQueues(cx)) return false;
#endif
  if (!JS::InitSelfHostedCode(cx)) {'''),
 ('  JSAutoRealm ar(cx, GLOBAL);\n\n  JS::SetPromiseRejectionTrackerCallback', '''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  if (!core::async_context::initialize_realms(cx, GLOBAL, INIT_SCRIPT_GLOBAL)) return false;
#endif
  JSAutoRealm ar(cx, GLOBAL);

  JS::SetPromiseRejectionTrackerCallback'''),
 ('void Engine::queue_async_task(const RefPtr<AsyncTask>& task) {','''bool api::AsyncTask::capture_context(JSContext* cx, JS::MutableHandleObject resource) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  return core::async_context::store().capture(cx, resource);
#else
  resource.set(nullptr);return true;
#endif
}
bool api::AsyncTask::context_from_promise(JSContext* cx, JS::HandleObject promise,
                                         JS::MutableHandleObject resource) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  JS::RootedObject captured(cx, js::GetAllocationMetadata(promise));
  if (!core::async_context::ResourceStore::is_resource(captured))
    return core::InternalTickQueue::fail(cx, JSEXN_TYPEERR,
        "ERR_SM_NODE_ASYNC_CONTEXT_UNSUPPORTED", "Untracked operation Promise");
  // The operation Promise was captured at actual fetch registration. Retain
  // that genuine cell without allocating after a streaming handle is closed.
  resource.set(captured);return true;
#else
  resource.set(nullptr);return true;
#endif
}
void Engine::queue_async_task(const RefPtr<AsyncTask>& task) {''')])
file('runtime/event_loop.cpp',[
 ('#include "event_loop.h"','#include "event_loop.h"\n'+include),
 ('  MOZ_ASSERT(task);\n  queue.get().tasks.emplace_back(task);','''  MOZ_ASSERT(task);
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  MOZ_RELEASE_ASSERT(task->async_context());
#endif
  queue.get().tasks.emplace_back(task);'''),
 ('      task->cancel(engine);','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
      core::async_context::ResourceStore::Scope context(engine->cx(), core::async_context::store(), task->async_context());
#endif
      task->cancel(engine);'''),
 ('    bool success = task->run(engine);','''    bool success;
    {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
      core::async_context::ResourceStore::Scope context(cx, core::async_context::store(), task->async_context());
#endif
      success = task->run(engine);
    }'''),
 ('  for (const auto& task : q.tasks) {\n    task->cancel(engine);','''  for (const auto& task : q.tasks) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    core::async_context::ResourceStore::Scope context(engine->cx(), core::async_context::store(), task->async_context());
#endif
    task->cancel(engine);''')])
file('runtime/node_tick_queue.h',[
 ('    JS::Heap<JSObject*> arguments{nullptr};','''    JS::Heap<JSObject*> arguments{nullptr};
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    JS::Heap<JSObject*> resource{nullptr};
#endif''')])
file('runtime/node_tick_queue.cpp',[
 ('#include "event_loop.h"','#include "event_loop.h"\n'+include),
 ('  TraceEdge(trc, &arguments, "internal tick private argument array");','''  TraceEdge(trc, &arguments, "internal tick private argument array");
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  TraceEdge(trc, &resource, "internal tick async resource");
#endif'''),
 ('  Tick& tick = slots_[(head_ + count_) % MaxPending];','''  RootedObject resource(cx);
  if (!api::AsyncTask::capture_context(cx, &resource)) return false;
  Tick& tick = slots_[(head_ + count_) % MaxPending];
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  tick.resource = resource;
#endif'''),
 ('for (auto& tick : slots_) { tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0; }','''for (auto& tick : slots_) {
    tick.callback = nullptr;tick.arguments = nullptr;tick.argc = 0;
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    tick.resource = nullptr;
#endif
  }'''),
 ('    const uint32_t argc = tick.argc;','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    RootedObject resource(cx, tick.resource);
#endif
    const uint32_t argc = tick.argc;'''),
 ('    head_ = (head_ + 1) % MaxPending; --count_; ++executed;','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    tick.resource = nullptr;
#endif
    head_ = (head_ + 1) % MaxPending; --count_; ++executed;'''),
 ('    JSAutoRealm realm(cx, callback);','''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    core::async_context::ResourceStore::Scope context(cx, core::async_context::store(), resource);
#endif
    JSAutoRealm realm(cx, callback);''')])
file('builtins/web/timers.cpp',[
 ('JS::HandleValueVector args)\n      : timer_id_', 'JS::HandleValueVector args, HandleObject resource)\n      : api::AsyncTask(resource), timer_id_'),
 ('  auto *const timer = js_new<TimerTask>(delay, repeat, handler, handle_args);','''  RootedObject resource(cx);
  if (!api::AsyncTask::capture_context(cx, &resource)) return false;
  auto *const timer = js_new<TimerTask>(delay, repeat, handler, handle_args, resource);''')])
file('builtins/web/streams/buf-reader.cpp',[
 ('explicit StreamTask(const HandleObject reader) : reader_(reader)', 'explicit StreamTask(const HandleObject reader, HandleObject resource) : api::AsyncTask(resource), reader_(reader)'),
 ('  api::Engine::get(cx)->queue_async_task(js_new<StreamTask>(owner));','''  RootedObject resource(cx);
  if (!api::AsyncTask::capture_context(cx, &resource)) return false;
  api::Engine::get(cx)->queue_async_task(js_new<StreamTask>(owner, resource));''')])
file('builtins/web/fetch/request-response.h',[
 ('host_api::FutureHttpIncomingResponse *future);','host_api::FutureHttpIncomingResponse *future, HandleObject resource);')])
file('builtins/web/fetch/request-response.cpp',[
 ('explicit BodyFutureTask(const HandleObject body_source) : body_source_(body_source)', 'explicit BodyFutureTask(const HandleObject body_source, HandleObject resource) : api::AsyncTask(resource), body_source_(body_source)'),
 ('    ENGINE->queue_async_task(js_new<ResponseFutureTask>(body_owner, pending_handle));','''    RootedObject promise(cx, Request::response_promise(body_owner)), resource(cx);
    if (!api::AsyncTask::context_from_promise(cx, promise, &resource)) return false;
    ENGINE->queue_async_task(js_new<ResponseFutureTask>(body_owner, pending_handle, resource));'''),
 ('  ENGINE->queue_async_task(js_new<BodyFutureTask>(source));','''  RootedObject resource(cx);
  if (!api::AsyncTask::capture_context(cx, &resource)) return false;
  ENGINE->queue_async_task(js_new<BodyFutureTask>(source, resource));'''),
 ('ResponseFutureTask::ResponseFutureTask(const HandleObject request, host_api::FutureHttpIncomingResponse *future)\n      : request_(request)', 'ResponseFutureTask::ResponseFutureTask(const HandleObject request, host_api::FutureHttpIncomingResponse *future, HandleObject resource)\n      : api::AsyncTask(resource), request_(request)'),
 ('auto res = dest_body->append(ENGINE, source_body, callback, callback_receiver);\n  if (const auto *err = res.to_err()) {', '''auto res = dest_body->append(ENGINE, source_body, callback, callback_receiver);
  if (const auto *err = res.to_err()) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    if (JS_IsExceptionPending(cx)) return false;
#endif'''),
 ('write_all_finish_callback, then_handler);\n  if (const auto *err = res.to_err()) {', '''write_all_finish_callback, then_handler);
  if (const auto *err = res.to_err()) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
    if (JS_IsExceptionPending(cx)) return false;
#endif'''),
 ('auto res = dest_body->append(ENGINE, source_body, finish_outgoing_body_streaming, nullptr);\n    if (const auto *err = res.to_err()) {', '''auto res = dest_body->append(ENGINE, source_body, finish_outgoing_body_streaming, nullptr);
    if (const auto *err = res.to_err()) {
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
      if (JS_IsExceptionPending(cx)) return false;
#endif''')])
file('builtins/web/fetch/fetch-api.cpp',[
 ('  unique_ptr<host_api::HttpHeaders> headers =','''  RootedObject resource(cx);
  if (!api::AsyncTask::context_from_promise(cx, response_promise, &resource)) return false;
  unique_ptr<host_api::HttpHeaders> headers ='''),
 ('js::MakeUnique<ResponseFutureTask>(request_obj, pending_handle)', 'js::MakeUnique<ResponseFutureTask>(request_obj, pending_handle, resource)')])
file('host-apis/wasi-0.2.0/host_api.cpp',[
 ('HandleObject callback_receiver)\n      : outgoing_body_', 'HandleObject callback_receiver, HandleObject resource)\n      : api::AsyncTask(resource), outgoing_body_'),
 ('  engine->queue_async_task(new BodyWriteAllTask(this, std::move(bytes), callback, cb_receiver));','''  JS::RootedObject resource(engine->cx());
  if (!api::AsyncTask::capture_context(engine->cx(), &resource)) return Result<Void>::err(154);
  engine->queue_async_task(new BodyWriteAllTask(this, std::move(bytes), callback, cb_receiver, resource));'''),
 ('HandleObject callback_receiver)\n      : incoming_body_', 'HandleObject callback_receiver, HandleObject resource)\n      : api::AsyncTask(resource), incoming_body_'),
 ('  engine->queue_async_task(new BodyAppendTask(engine, other, this, callback, callback_receiver));','''  JS::RootedObject resource(engine->cx());
  if (!api::AsyncTask::capture_context(engine->cx(), &resource)) return Result<Void>::err(154);
  engine->queue_async_task(new BodyAppendTask(engine, other, this, callback, callback_receiver, resource));''')])
file('CMakeLists.txt',[
 ('target_link_libraries(starling-raw.wasm PRIVATE host_api extension_api builtins spidermonkey rust-crates)', '''if(NODE_COMPAT_ASYNC_LOCAL_STORAGE)
    target_sources(starling-raw.wasm PRIVATE runtime/async_context_store.cpp
        runtime/async_context_queue.cpp runtime/async_context_runtime.cpp)
    target_compile_definitions(host_api PRIVATE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)
endif()
target_link_libraries(starling-raw.wasm PRIVATE host_api extension_api builtins spidermonkey rust-crates)''')])
file('cmake/builtins.cmake',[
 ('# UNAPPLIED classic source candidate: pure JS state machines', '''# Experimental native ALS: no JS stack emulation or new host imports.
option(NODE_COMPAT_ASYNC_LOCAL_STORAGE "Enable experimental native AsyncLocalStorage" OFF)
if(NODE_COMPAT_ASYNC_LOCAL_STORAGE AND NOT CMAKE_SCRIPT_MODE_FILE)
    if(NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_INTERNAL_TICKS)
        message(FATAL_ERROR "Native ALS requires Node compatibility and private tick checkpoints")
    endif()
    target_compile_definitions(extension_api INTERFACE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)
    target_include_directories(builtin_node_compat PRIVATE ${CMAKE_SOURCE_DIR}/runtime)
endif()

# UNAPPLIED classic source candidate: pure JS state machines''')])
file('builtins/node-compat/register.cpp',[
 ('namespace builtins::node_compat {', '''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
#include "async-hooks-factory.generated.h"
#include "async_context_runtime.h"
#endif
namespace builtins::node_compat {'''),
 ('#ifdef NODE_COMPAT_PATH\nstatic bool install_path', '''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
static bool install_async_local_storage(api::Engine* engine) {
  auto* cx = engine->cx();
  JS::RootedObject kernel(cx, core::async_context::create_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue argument(cx, JS::ObjectValue(*kernel)), module(cx);
  if (!evaluate_factory(cx, kAsyncLocalStorageFactorySource, argument, &module)) return false;
  return engine->define_builtin_module("node:async_hooks", module) &&
         engine->define_builtin_module("async_hooks", module);
}
#endif
#ifdef NODE_COMPAT_PATH
static bool install_path'''),
 ('  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);', '''#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  if (!install_async_local_storage(engine)) return false;
#endif
  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);''')])
(OWN/'integration-edits.json').write_text(json.dumps(dict(schemaVersion=1,sourceOnly=True,uncompiled=True,files=changes),indent=2)+'\n')
print(json.dumps(dict(afterimages=len(changes),edits=sum(len(x['edits'])for x in changes),nativeActions=False)))
