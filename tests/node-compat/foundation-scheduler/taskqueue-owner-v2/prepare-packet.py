#!/usr/bin/env python3
"""Generate source-only diffs/receipt. Never apply, copy source trees, build or run guests."""
import difflib, hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = HERE.parent / 'source-audit.json'
ADOPTION = REPO / 'tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json'
EMBEDDING = Path('/tmp/starling-node-compat/foundations-v10/native-freeze/componentize-source/embedding/embedding.cpp')
def sha(data): return hashlib.sha256(data).hexdigest()
def pin(path, label=None):
    assert path.is_file() and not path.is_symlink(), path
    return {'path': label or str(path), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
def change(text, before, after):
    assert text.count(before) == 1, before[:100]
    return text.replace(before, after)
def diff(path, before, after):
    return ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                      fromfile='a/'+path if before else '/dev/null', tofile='b/'+path))
assert pin(AUDIT)['sha256'] == '8322ce146c405cca6148b0080b07525f2dd6a9241c2024d8804c1f3762526258'
assert pin(ADOPTION)['sha256'] == '3cba5d2b5830127bde9e585cdefa2c69b09b583fad3225cd3ae068da6efed326'
original=json.loads(AUDIT.read_text()); adoption=json.loads(ADOPTION.read_text())
for entry in original['proposalFiles']:
    assert sha((HERE.parent/entry['path']).read_bytes())==entry['sha256'], entry['path']
headers=Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include')
api_headers=['js/CallArgs.h','js/Array.h','js/CallAndConstruct.h','js/ErrorReport.h',
             'js/GCPolicyAPI.h','js/GCVector.h','js/Realm.h','js/RootingAPI.h',
             'js/TracingAPI.h','js/ValueArray.h','jsfriendapi.h']
expected={i['path']:i['sha256'] for i in original['sourceManifest']}
assert len(expected)==304
native_deltas=[]
for i in adoption['changes']:
    if i['path'] in expected:
        assert expected[i['path']]==i['before']
        expected[i['path']]=i['after']; native_deltas.append(i)
assert len(native_deltas)==4
for name,digest in expected.items():
    p=REPO/name
    assert not p.is_symlink() and p.is_file() and sha(p.read_bytes())==digest, name
canonical=[{'path':p,'sha256':d} for p,d in sorted(expected.items())]
changes={}
def native(path, transform):
    before=(REPO/path).read_text(); after=transform(before)
    assert before!=after
    changes[path]=(before,after)

native('runtime/event_loop.h',lambda s:change(change(s,
 '#include "jsapi.h"','#include "jsapi.h"\n#ifdef NODE_COMPAT_INTERNAL_TICKS\n#include "node_tick_queue.h"\n#endif'),
 '  static bool run_event_loop(api::Engine *engine, double total_compute);',
'''  static bool run_event_loop(api::Engine *engine, double total_compute);
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // Existing two-argument entry remains the TaskOrExport wrapper.
  static bool run_event_loop(api::Engine *engine, double total_compute, TickCheckpointOrigin origin);
  // Internal captured factory argument; no public process/module/global API.
  static JSObject* create_internal_next_tick(JSContext* cx);
  static bool require_internal_ticks_quiescent(JSContext* cx);
  static bool internal_tick_checkpoint_active();
  static bool require_internal_tick_reset_allowed(JSContext* cx);
  static bool run_internal_tick_checkpoint(JSContext* cx, TickCheckpointOrigin origin);
#endif'''))

def event_loop(s):
    s=change(s,'  bool event_loop_running = false;\n\n  void trace(JSTracer *trc) const {',
'''  bool event_loop_running = false;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  core::InternalTickQueue ticks;
#endif

  void trace(JSTracer *trc) {''')
    s=change(s,'      task->trace(trc);\n    }\n  }\n};',
'''      task->trace(trc);
    }
#ifdef NODE_COMPAT_INTERNAL_TICKS
    ticks.trace(trc);
#endif
  }
};''')
    s=change(s,'inline void exit_event_loop() { queue.get().event_loop_running = false; }',
'''inline void exit_event_loop(bool success = false) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  if (!success) queue.get().ticks.discard();
#endif
  queue.get().event_loop_running = false;
}

#ifdef NODE_COMPAT_INTERNAL_TICKS
static bool enqueue_internal_tick(JSContext* cx, unsigned argc, JS::Value* vp) {
  return queue.get().ticks.enqueue(cx, JS::CallArgsFromVp(argc, vp));
}
JSObject* EventLoop::create_internal_next_tick(JSContext* cx) {
  JS::RootedFunction function(cx, JS_NewFunction(cx, enqueue_internal_tick, 1, 0, "nextTick"));
  return function ? JS_GetFunctionObject(function) : nullptr;
}
bool EventLoop::internal_tick_checkpoint_active() { return queue.get().ticks.checkpoint_running(); }
bool EventLoop::require_internal_ticks_quiescent(JSContext* cx) {
  if (queue.get().event_loop_running || !queue.get().ticks.empty_and_inactive())
    return InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_STATE", "tick FIFO must be empty and inactive at this boundary");
  return true;
}
bool EventLoop::require_internal_tick_reset_allowed(JSContext* cx) {
  if (queue.get().event_loop_running || queue.get().ticks.checkpoint_running())
    return InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "cannot reset an active tick/task checkpoint");
  return true;
}
bool EventLoop::run_internal_tick_checkpoint(JSContext* cx, TickCheckpointOrigin origin) {
  return queue.get().ticks.checkpoint(cx, origin);
}
#endif''')
    s=change(s,'''bool EventLoop::run_event_loop(api::Engine *engine, double total_compute) {
  if (queue.get().event_loop_running) {
    std::print(stderr, "cannot run event loop as it is already running");
    return false;
  }''',
'''bool EventLoop::run_event_loop(api::Engine *engine, double total_compute) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  return run_event_loop(engine, total_compute, TickCheckpointOrigin::TaskOrExport);
}
bool EventLoop::run_event_loop(api::Engine *engine, double total_compute, TickCheckpointOrigin origin) {
  if (queue.get().event_loop_running || queue.get().ticks.checkpoint_running())
    return InternalTickQueue::fail(engine->cx(), JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "event loop is already running");
#else
  if (queue.get().event_loop_running) {
    std::print(stderr, "cannot run event loop as it is already running");
    return false;
  }
#endif''')
    s=change(s,'''    // Run a microtask checkpoint
    js::RunJobs(cx);''',
'''    // Complete existing Promise checkpoint, optionally bracketed by guest ticks.
#ifdef NODE_COMPAT_INTERNAL_TICKS
    if (!run_internal_tick_checkpoint(cx, origin)) { exit_event_loop(); return false; }
    origin = TickCheckpointOrigin::TaskOrExport;
#else
    js::RunJobs(cx);
#endif''')
    s=change(s,'''    if (ran_cleanups) {
      continue;
    }''',
'''    if (ran_cleanups) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
      origin = TickCheckpointOrigin::FinalizerBatch;
#endif
      continue;
    }''')
    s=change(s,'''    if (interest_complete()) {
      exit_event_loop();
      return true;''',
'''    if (interest_complete()) {
      exit_event_loop(true);
      return true;''')
    s=change(s,'''    js::RunJobs(cx);
#ifdef NODE_COMPAT_STRICT_INITIALIZATION''',
'''#ifdef NODE_COMPAT_INTERNAL_TICKS
    // Existing strict cleanup-error check ABOVE remains before dispatch.
    if (!run_internal_tick_checkpoint(cx, TickCheckpointOrigin::FinalizerBatch)) return false;
#else
    js::RunJobs(cx);
#endif
#ifdef NODE_COMPAT_STRICT_INITIALIZATION''')
    s=change(s,'''void EventLoop::reset(api::Engine *engine) {
  auto &q = queue.get();''',
'''void EventLoop::reset(api::Engine *engine) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  if (!require_internal_tick_reset_allowed(engine->cx())) {
    engine->abort("resetting an active internal tick checkpoint");
    return;
  }
#endif
  auto &q = queue.get();''')
    s=change(s,'''  q.tasks.clear();
  q.interest_cnt = 0;''',
'''  q.tasks.clear();
  q.interest_cnt = 0;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  q.ticks.reset_storage();
#endif''')
    return s
native('runtime/event_loop.cpp',event_loop)

def engine(s):
    s=change(s,'''void Engine::finish_pre_initialization() {
  MOZ_ASSERT(state_ == EngineState::ScriptPreInitializing);''',
'''void Engine::finish_pre_initialization() {
  MOZ_ASSERT(state_ == EngineState::ScriptPreInitializing);
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // EARLY boundary only: embedding must also check AFTER bindExports.
  if (!core::EventLoop::require_internal_ticks_quiescent(cx()))
    abort("finishing pre-initialization with pending internal ticks");
#endif''')
    s=change(s,'''  RootedValue result(cx);
  return JS_ExecuteScript(cx, script, &result);
}''',
'''  RootedValue result(cx);
  if (!JS_ExecuteScript(cx, script, &result)) return false;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // Actual initializer is a classic script in INIT_SCRIPT_GLOBAL.
  return core::EventLoop::run_internal_tick_checkpoint(cx, core::TickCheckpointOrigin::InitializerScript);
#else
  return true;
#endif
}''')
    s=change(s,'''  SCRIPT_VALUE = ns;
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  if (!this->run_event_loop()) {''',
'''  SCRIPT_VALUE = ns;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // Classify using actual configuration; preserve Engine's public no-arg ABI.
  if (!core::EventLoop::run_event_loop(this, 0, config_->module_mode
          ? core::TickCheckpointOrigin::ModuleEvaluation
          : core::TickCheckpointOrigin::ClassicEvaluation)) return false;
#elif defined(NODE_COMPAT_STRICT_INITIALIZATION)
  if (!this->run_event_loop()) {''')
    s=change(s,'''void Engine::reset() {
  clear_unhandled_promise_rejections();''',
'''void Engine::reset() {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // Establish idle state BEFORE changing existing reset-owned state.
  if (!core::EventLoop::require_internal_tick_reset_allowed(cx())) {
    abort("resetting an active internal tick checkpoint");
    return;
  }
#endif
  clear_unhandled_promise_rejections();''')
    return s
native('runtime/engine.cpp',engine)
native('CMakeLists.txt',lambda s:change(s,'add_executable(starling-raw.wasm ${SOURCES})',
'''add_executable(starling-raw.wasm ${SOURCES})
if(NODE_COMPAT_INTERNAL_TICKS)
    target_sources(starling-raw.wasm PRIVATE runtime/node_tick_queue.cpp)
endif()'''))
native('cmake/builtins.cmake',lambda s:s+'''
# Private scheduler proposal: no public process namespace or host capability.
option(NODE_COMPAT_INTERNAL_TICKS "Enable private bounded guest nextTick queue" OFF)
if(NODE_COMPAT_INTERNAL_TICKS AND NOT CMAKE_SCRIPT_MODE_FILE)
    if(NOT TARGET builtin_node_compat)
        message(FATAL_ERROR "NODE_COMPAT_INTERNAL_TICKS requires ENABLE_BUILTIN_NODE_COMPAT=ON")
    endif()
    target_compile_definitions(extension_api INTERFACE NODE_COMPAT_INTERNAL_TICKS=1)
endif()
''')
for name in ['node_tick_queue.h','node_tick_queue.cpp']:
    changes['runtime/'+name]=('',(HERE/'proposed/runtime'/name).read_text())
(HERE/'starling-taskqueue-ticks.UNAPPLIED.patch').write_text(''.join(diff(p,*v) for p,v in changes.items()))
assert pin(EMBEDDING)['sha256']=='9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977'
before=EMBEDDING.read_text()
after=change(before,'#include "js/Conversions.h"','#include "js/Conversions.h"\n#ifdef NODE_COMPAT_INTERNAL_TICKS\n#include "event_loop.h"\n#endif')
after=change(after,'''  Runtime.cur_fn_idx = fn_idx;
  if (argptr) {''',
'''#ifdef NODE_COMPAT_INTERNAL_TICKS
  // BEFORE a fresh export: never silently discard stale callbacks/arguments.
  if (!core::EventLoop::require_internal_ticks_quiescent(Runtime.cx))
    Runtime.engine->abort("entering an export with a nonempty internal tick FIFO");
#endif
  Runtime.cur_fn_idx = fn_idx;
  if (argptr) {''')
after=change(after,'''  if (Runtime.engine->has_unhandled_promise_rejections()) {
    JS_ReportErrorASCII(Runtime.cx, "ERR_SM_NODE_INITIALIZATION_REJECTION: unhandled promise rejection after export binding");
    Runtime.engine->abort("finalizing export bindings with an unhandled rejection");
  }
#endif''',
'''  if (Runtime.engine->has_unhandled_promise_rejections()) {
    JS_ReportErrorASCII(Runtime.cx, "ERR_SM_NODE_INITIALIZATION_REJECTION: unhandled promise rejection after export binding");
    Runtime.engine->abort("finalizing export bindings with an unhandled rejection");
  }
#endif
#ifdef NODE_COMPAT_INTERNAL_TICKS
  // ACTUAL final snapshot boundary, after bindExports/getters/jobs.
  if (!core::EventLoop::require_internal_ticks_quiescent(Runtime.cx))
    Runtime.engine->abort("finalizing export bindings with pending internal ticks");
#endif''')
(HERE/'componentize-taskqueue-ticks.UNAPPLIED.patch').write_text(diff('embedding/embedding.cpp',before,after))
receipt={
 'schemaVersion':1,'status':'unapplied-source-only-awaiting-review-before-SDK-syntax',
 'nativeBaseRevision':original['head'],'componentizeRevision':original['componentizeJsRevision'],
 'nodeCompatibilityRelease':'v22.14.0','spiderMonkeyRevision':original['spiderMonkey']['revision'],
 'm11SourceAdoption':pin(ADOPTION),'original304ManifestEvidence':pin(AUDIT),
 'nativeInputsChecked':304,'expectedNativeInputListCanonicalSha256':sha(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()),
 'm11NativeDeltas':native_deltas,'all304CurrentInputsMatchV10PlusFourApprovedM11Deltas':True,
 'buildRecipe':pin(REPO/'tests/node-compat/build-engine.sh'),
 'originalSchedulerPacketUnchanged':[pin(HERE.parent/i['path']) for i in original['proposalFiles']]+[pin(AUDIT)],
 'oldPacketSourcesChecked':len(original['proposalFiles']),
 'spiderMonkeyApiHeadersReadNotCompiled':[pin(headers/i) for i in api_headers],
 'nodeOrderingEvidence':pin(HERE.parent/'node-results.json'),
 'resetStatus':'OPEN; idle precondition only, no safe reset/reuse proof',
 'nativePatch':pin(HERE/'starling-taskqueue-ticks.UNAPPLIED.patch'),
 'embeddingPatch':pin(HERE/'componentize-taskqueue-ticks.UNAPPLIED.patch'),
 'embeddingBefore':pin(EMBEDDING),'embeddingAfterSha256':sha(after.encode()),
 'changedNativeFiles':[{'path':p,'beforeSha256':sha(b.encode()) if b else None,'afterSha256':sha(a.encode())} for p,(b,a) in changes.items()],
 'selectedWasiInterfaces':[],'hostChanges':[],'extraStaticPersistentRoots':0,
 'publicProcessOrGlobalAdded':False,'sourceTreeCopied':False,'sdkSyntaxCompiled':False,'engineBuilt':False,'guestExecuted':False,
 'limits':{'pendingCallbacks':4096,'argumentsEach':1024,'pendingArgumentValues':65536,'callbacksPerCheckpoint':65536},
 'pending':['root source review','private sparse materialization after review','actual SDK/SM syntax','new Release/GC engines and ordinary tests','snapshot/repeated-entry/import acceptance']}
(HERE/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'checkedNativeInputs':304,'nativePatchSha256':receipt['nativePatch']['sha256'],'embeddingPatchSha256':receipt['embeddingPatch']['sha256'],'nativeSourceChanged':False,'sdkSyntaxCompiled':False}))
