"""Create UNAPPLIED afterimages only. Never patch the native/source/build tree."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
ROOT=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
records=[]
def desc(p):
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def derive(relative,edits,external=False):
 base=ROOT/('componentize-source' if external else 'source')/relative
 before=base.read_text();after=before
 for a,b in edits:
  assert after.count(a)==1,(relative,a[:90],after.count(a))
  after=after.replace(a,b,1)
 inverse=after
 for a,b in reversed(edits):
  assert inverse.count(b)==1,(relative,'inverse',b[:90])
  inverse=inverse.replace(b,a,1)
 assert inverse==before
 out=OWN/'after'/('componentize-source' if external else '')/relative
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(after)
 records.append({'role':'externalEmbeddingAfterimage' if external else 'nativeAfterimage','repositoryPath':relative,'before':desc(base),'after':desc(out),'edits':[{'before':a,'after':b} for a,b in edits],'inverseExact':True})
guard='''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
#include "clock-lifecycle-diagnostics.h"
namespace lifecycle_diag = diagnostics::clock_lifecycle;
#endif
'''
derive('runtime/event_loop.cpp',[
 ('#include "event_loop.h"\n','#include "event_loop.h"\n'+guard),
 ('  queue.get().tasks.emplace_back(task);','  queue.get().tasks.emplace_back(task);\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n  lifecycle_diag::count(lifecycle_diag::Counter::QueueEnqueue);\n#endif'),
 ('      tasks->erase(it);','      tasks->erase(it);\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n      lifecycle_diag::count(lifecycle_diag::Counter::QueueDetachCancel);\n#endif'),
 ('void EventLoop::incr_event_loop_interest() { queue.get().interest_cnt++; }','''void EventLoop::incr_event_loop_interest() {
  queue.get().interest_cnt++;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::InterestIncr);
#endif
}'''),
 ('  queue.get().interest_cnt--;','  queue.get().interest_cnt--;\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n  lifecycle_diag::count(lifecycle_diag::Counter::InterestDecr);\n#endif'),
 ('    tasks->erase(tasks->begin() + task_idx);','    tasks->erase(tasks->begin() + task_idx);\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n    lifecycle_diag::count(lifecycle_diag::Counter::QueueDetachRun);\n#endif'),
 ('} // namespace core','''} // namespace core
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace diagnostics::clock_lifecycle {
RuntimeCounts runtime_counts() {
  return {queue.get().tasks.size(), queue.get().interest_cnt,
    queue.get().event_loop_running, timer_registry_size(), immediate_cache_owned()};
}
} // namespace diagnostics::clock_lifecycle
#endif''')])
derive('builtins/web/timers.cpp',[
 ('#include "timers.h"\n','#include "timers.h"\n'+guard),
 ('  bool retired_ = false;','  bool retired_ = false;\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n  uint64_t diagnostic_lease_ = 0;\n#endif'),
 ('      host_api::MonotonicClock::unsubscribe(owned);','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
      lifecycle_diag::timer_drop_begin(diagnostic_lease_, owned, handle_);
#endif
      host_api::MonotonicClock::unsubscribe(owned);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
      lifecycle_diag::timer_drop_returned(diagnostic_lease_, owned);
      diagnostic_lease_ = 0;
#endif'''),
 ('    retired_ = true;','    retired_ = true;\n#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS\n    lifecycle_diag::count(lifecycle_diag::Counter::TimerRetire);\n#endif'),
 ('        arguments_(std::move(args)) {}','''        arguments_(std::move(args)) {
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    lifecycle_diag::count(lifecycle_diag::Counter::TimerConstruct);
#endif
  }'''),
 ('  ~TimerTask() override { drop_pollable(); }','''  ~TimerTask() override {
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    lifecycle_diag::count(lifecycle_diag::Counter::TimerDestroy);
#endif
    drop_pollable();
  }'''),
 ('    handle_ = host_api::MonotonicClock::subscribe(deadline_, true);','''    handle_ = host_api::MonotonicClock::subscribe(deadline_, true);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    if (diagnostic_lease_ != 0) lifecycle_diag::state.invariantViolation = true;
    diagnostic_lease_ = lifecycle_diag::timer_acquired(timer_id_, handle_);
#endif'''),
 ('} // namespace builtins::web::timers','''} // namespace builtins::web::timers
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace diagnostics::clock_lifecycle {
std::size_t timer_registry_size() { return TIMERS_MAP->timers_.count(); }
} // namespace diagnostics::clock_lifecycle
#endif''')])
derive('host-apis/wasi-0.2.0/host_api.cpp',[
 ('#include "host_api.h"\n','#include "host_api.h"\n'+guard),
 ('  auto list = list_borrow_pollable_t{handles.data(), handles.size()};','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::PollCall);
  if (handles.empty()) lifecycle_diag::count(lifecycle_diag::Counter::EmptyPollAttempt);
#endif
  auto list = list_borrow_pollable_t{handles.data(), handles.size()};'''),
 ('  // Remove tasks whose pollable handles have been invalidated (e.g. by abort).','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::SelectorCall);
  const auto diagnostic_before_prune = tasks.size();
#endif
  // Remove tasks whose pollable handles have been invalidated (e.g. by abort).'''),
 ('  if (tasks.empty()) {\n    return std::nullopt;','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  if (tasks.size() > diagnostic_before_prune) lifecycle_diag::state.invariantViolation = true;
  else lifecycle_diag::count(lifecycle_diag::Counter::PrunedInvalid, diagnostic_before_prune - tasks.size());
#endif
  if (tasks.empty()) {
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    lifecycle_diag::count(lifecycle_diag::Counter::SelectorEmpty);
#endif
    return std::nullopt;'''),
 ('          immediately_ready = wasi_clocks_monotonic_clock_subscribe_duration(0);','''          immediately_ready = wasi_clocks_monotonic_clock_subscribe_duration(0);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
          lifecycle_diag::count(lifecycle_diag::Counter::ImmediateCacheAcquire);
#endif'''),
 ('        handles.emplace_back(immediately_ready.value().__handle);','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
        lifecycle_diag::count(lifecycle_diag::Counter::ImmediateCacheUse);
#endif
        handles.emplace_back(immediately_ready.value().__handle);'''),
 ('  wasi_io_poll_pollable_drop_own(own_pollable_t{handle_id});','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::HostMonotonicDropAttempt);
#endif
  wasi_io_poll_pollable_drop_own(own_pollable_t{handle_id});
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::HostMonotonicDropReturned);
#endif'''),
 ('\nstatic std::optional<wasi_clocks_monotonic_clock_own_pollable_t> immediately_ready;','''
static std::optional<wasi_clocks_monotonic_clock_own_pollable_t> immediately_ready;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace diagnostics::clock_lifecycle {
bool immediate_cache_owned() { return immediately_ready.has_value(); }
} // namespace diagnostics::clock_lifecycle
#endif''')])
cmake='''
# SOURCE-ONLY separate diagnostic variant. Both flags are OFF by default.
option(NODE_COMPAT_LIFECYCLE_DIAGNOSTICS "Instrument private lifecycle snapshots" OFF)
option(ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE "Enable private lifecycle module" OFF)
if(ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE AND NOT NODE_COMPAT_LIFECYCLE_DIAGNOSTICS)
    message(FATAL_ERROR "Private lifecycle module requires its instrumentation flag")
endif()
if(NODE_COMPAT_LIFECYCLE_DIAGNOSTICS)
    if(NOT ENABLE_BUILTIN_NODE_COMPAT OR NOT ENABLE_BUILTIN_WEB_TIMERS)
        message(FATAL_ERROR "Lifecycle diagnostics require the genuine Node and timer targets")
    endif()
    if(NOT CMAKE_BUILD_TYPE STREQUAL "Release" OR ENABLE_JS_DEBUGGER OR NODE_COMPAT_OOM_TESTING OR NODE_COMPAT_GC_STRESS)
        message(FATAL_ERROR "Lifecycle diagnostics require ordinary Release without debugger/OOM/GC stress")
    endif()
    if(NOT ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE)
        message(FATAL_ERROR "Instrumented lifecycle variant requires its explicit private module")
    endif()
    target_compile_definitions(extension_api INTERFACE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)
    target_compile_definitions(host_api PRIVATE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)
    target_include_directories(host_api PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")
    add_builtin(diagnostics::clock_lifecycle DISABLED_BY_DEFAULT
        SRC builtins/diagnostics/clock-lifecycle.cpp)
endif()
'''
path=ROOT/'source/cmake/builtins.cmake';text=path.read_text()
derive('cmake/builtins.cmake',[(text,text+cmake)])
derive('embedding/embedding.cpp',[
 ('#include "embedding.h"\n','#include "embedding.h"\n'+guard),
 ('  Runtime.cur_fn_idx = fn_idx;','''  Runtime.cur_fn_idx = fn_idx;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::entered_call();
#endif'''),
 ('  if (!Runtime.engine->run_event_loop()) {\n    Runtime.engine->abort("(call) event loop error");','''#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  const bool diagnostic_loop_success = Runtime.engine->run_event_loop();
  lifecycle_diag::after_loop(fn_idx, diagnostic_loop_success, Runtime.cur_fn_idx, Runtime.free_list.size());
  if (!diagnostic_loop_success) {
#else
  if (!Runtime.engine->run_event_loop()) {
#endif
    Runtime.engine->abort("(call) event loop error");'''),
 ('  Runtime.free_list.clear();','''  Runtime.free_list.clear();
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::after_post_call(fn_idx, Runtime.cur_fn_idx, Runtime.free_list.size());
#endif''')],True)
(OWN/'derivations.json').write_text(json.dumps({'schemaVersion':1,'scope':'UNAPPLIED native/external embedding afterimages only','files':records,'edits':sum(len(r['edits']) for r in records),'allReverseExact':True},indent=2)+'\n')
print(json.dumps({'afterimages':len(records),'edits':sum(len(r['edits']) for r in records),'reverseExact':True}))
