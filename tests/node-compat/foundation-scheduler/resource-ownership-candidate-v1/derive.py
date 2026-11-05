"""Create unapplied afterimages from exact current source, never alter production."""
from pathlib import Path
import difflib,hashlib,json,os
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
edits=[]
def replace(text,before,after,label):
    assert text.count(before)==1,label;edits.append(dict(label=label,before=before,after=after));return text.replace(before,after)
p=HERE/'base/builtins/web/timers.cpp';base=p.read_text();text=base
text=replace(text,'#include "event_loop.h"','#include "event_loop.h"\n#include "js/HashTable.h"\n#include "js/Vector.h"','fallible SM container headers')
text=replace(text,'#include <map>\n#include <vector>','#include <limits>\n#include <utility>','bounded ID and move/exchange headers')
text=replace(text,'''  std::map<int32_t, api::AsyncTask *> timers_;
  int32_t next_timer_id = 1;
  void trace(JSTracer *trc) {
    for (auto &[id, timer] : timers_) {
      timer->trace(trc);
    }
  }''','''  // Native ownership and JS-edge tracing last until explicit retirement.
  js::HashMap<int32_t, RefPtr<api::AsyncTask>, js::DefaultHasher<int32_t>,
              js::SystemAllocPolicy> timers_;
  uint64_t next_timer_id = 1;
  void trace(JSTracer *trc) {
    for (auto iter = timers_.iter(); !iter.done(); iter.next()) {
      iter.get().value()->trace(trc);
    }
  }''','strong traced fallible registry, never rewind IDs')
start=text.index('class TimerTask final');end=text.index('\nnamespace builtins::web::timers',start)
new='''class TimerTask final : public api::AsyncTask {
public:
  using TimerArgumentsVector = js::Vector<JS::Heap<JS::Value>, 0, js::SystemAllocPolicy>;

private:
  int32_t timer_id_;
  uint64_t delay_;
  uint64_t deadline_ = 0;
  bool repeat_;
  bool retired_ = false;
  Heap<JSObject *> callback_;
  TimerArgumentsVector arguments_;

  void drop_pollable() {
    // Invalidate ownership before the host drop; all terminal paths share this.
    const auto owned = std::exchange(handle_, INVALID_POLLABLE_HANDLE);
    if (owned != INVALID_POLLABLE_HANDLE) {
      host_api::MonotonicClock::unsubscribe(owned);
    }
  }

  void retire() {
    if (retired_) return;
    const RefPtr<TimerTask> keep_alive(this);
    retired_ = true;
    drop_pollable();
    auto entry = TIMERS_MAP->timers_.lookup(timer_id_);
    if (entry && entry->value() == this) TIMERS_MAP->timers_.remove(entry);
    callback_ = nullptr;
    arguments_.clear();
  }

public:
  TimerTask(int32_t id, uint64_t delay, bool repeat, HandleObject callback,
            TimerArgumentsVector&& args)
      : timer_id_(id), delay_(delay), repeat_(repeat), callback_(callback),
        arguments_(std::move(args)) {}

  ~TimerTask() override { drop_pollable(); }

  void subscribe() {
    const uint64_t now = host_api::MonotonicClock::now();
    const uint64_t maximum = std::numeric_limits<uint64_t>::max();
    deadline_ = now > maximum - delay_ ? maximum : now + delay_;
    handle_ = host_api::MonotonicClock::subscribe(deadline_, true);
  }

  [[nodiscard]] bool run(api::Engine *engine) override {
    if (retired_) return true;
    JSContext *cx = engine->cx();
    const RootedObject callback(cx, callback_);
    JS::RootedValueVector argv(cx);
    if (!argv.initCapacity(arguments_.length())) {
      retire();
      JS_ReportOutOfMemory(cx);
      return false;
    }
    for (auto &arg : arguments_) argv.infallibleAppend(arg);
    RootedValue rval(cx);
    if (!Call(cx, NullHandleValue, callback, argv, &rval)) {
      // Native retirement does not clear or replace the original JS exception.
      retire();
      return false;
    }
    if (retired_) return true; // clearTimeout/clearInterval during callback
    drop_pollable();
    if (repeat_) {
      // Existing enqueue is void/fatal-on-allocation, not recoverably fallible.
      // No new pollable is acquired until that native queue commit returns.
      engine->queue_async_task(this);
      subscribe();
    } else {
      retire();
    }
    return true;
  }

  [[nodiscard]] bool cancel(api::Engine *) override {
    retire();
    return true;
  }

  [[nodiscard]] uint64_t deadline() override { return deadline_; }
  [[nodiscard]] int32_t timer_id() const { return timer_id_; }

  void trace(JSTracer *trc) override {
    TraceEdge(trc, &callback_, "Timer callback");
    for (auto &arg : arguments_) TraceEdge(trc, &arg, "Timer callback arguments");
  }

  static bool clear(int32_t timer_id) {
    auto entry = TIMERS_MAP->timers_.lookup(timer_id);
    if (!entry) return false;
    // Retain a native owner before queue or registry removal. A running timer
    // is no longer queued, so retire it even when queue lookup returns false.
    RefPtr<api::AsyncTask> timer = entry->value();
    ENGINE->cancel_async_task(timer);
    return timer->cancel(ENGINE);
  }
};
'''
text=replace(text,text[start:end],new,'single timer terminalization and owned pollable/edge retirement')
text=replace(text,'''  const int64_t delay = static_cast<int64_t>(delay_ms) * 1000000;
  auto *const timer = js_new<TimerTask>(delay, repeat, handler, handle_args);
  ENGINE->queue_async_task(timer);

  *timer_id = timer->timer_id();
  return true;''','''  const uint64_t delay = static_cast<uint64_t>(delay_ms) * 1000000;
  if (TIMERS_MAP->next_timer_id > static_cast<uint64_t>(std::numeric_limits<int32_t>::max())) {
    JS_ReportErrorASCII(cx, "Timer identifier space exhausted");
    return false;
  }
  TimerTask::TimerArgumentsVector arguments;
  if (!arguments.reserve(handle_args.length())) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  for (const auto &arg : handle_args) arguments.infallibleAppend(arg);
  const int32_t id = static_cast<int32_t>(TIMERS_MAP->next_timer_id);
  RefPtr<TimerTask> timer = js_new<TimerTask>(id, delay, repeat, handler, std::move(arguments));
  if (!timer || !TIMERS_MAP->timers_.putNew(id, RefPtr<api::AsyncTask>(timer))) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  // All recoverable allocation checks precede publication/host acquisition.
  // The legacy void queue's native allocation failure remains fatal, not false.
  ENGINE->queue_async_task(timer);
  timer->subscribe();
  ++TIMERS_MAP->next_timer_id;
  *timer_id = id;
  return true;''','prepare fallible args/task/map before queue and host acquisition')
text=replace(text,'''  for (auto &[id, timer] : TIMERS_MAP->timers_) {
    timer->cancel(ENGINE);
  }
  TIMERS_MAP->timers_.clear();
  TIMERS_MAP->next_timer_id = 1;''','''  // Each cancel removes its own registry entry; never retain an iterator across it.
  while (!TIMERS_MAP->timers_.empty()) {
    RefPtr<api::AsyncTask> timer = TIMERS_MAP->timers_.iter().get().value();
    (void)timer->cancel(ENGINE);
  }
  // Do not alias old IDs. This does not make Engine::reset safe or supported.''','retire owned timer entries without iterator invalidation or stale ID reuse')
timer_edits=list(edits);(HERE/'afterimages/builtins/web/timers.cpp').write_text(text)
edits=[];p=HERE/'base/runtime/event_loop.cpp';base_loop=p.read_text();loop=base_loop
loop=replace(loop,'struct TaskQueue {','''// A native RefPtr alone is not a JS root after detaching from TaskQueue.
// Each local root traces the actual task throughout run/cancel, including nesting.
struct TracedAsyncTask {
  RefPtr<api::AsyncTask> task;
  void trace(JSTracer *trc) {
    if (task) task->trace(trc);
  }
};

struct TaskQueue {''','actual detached run/cancel task rooting')
loop=replace(loop,'''      tasks->erase(it);
      task->cancel(engine);''','''      JS::Rooted<TracedAsyncTask> retiring(engine->cx());
      retiring.get().task = task; // copy before erase, including an aliased RefPtr argument
      tasks->erase(it);
      (void)retiring.get().task->cancel(engine);''','retain and trace cancellation target before vector erase')
loop=replace(loop,'''    auto task = tasks->at(task_idx);
    tasks->erase(tasks->begin() + task_idx);
    bool success = task->run(engine);''','''    JS::Rooted<TracedAsyncTask> running(cx);
    running.get().task = tasks->at(task_idx);
    tasks->erase(tasks->begin() + task_idx);
    bool success = running.get().task->run(engine);''','trace actual running task through arbitrary callbacks')
(HERE/'afterimages/runtime/event_loop.cpp').write_text(loop)
records=[]
for name,steps in [('builtins/web/timers.cpp',timer_edits),('runtime/event_loop.cpp',edits)]:
    before=(HERE/'base'/name).read_bytes();after=(HERE/'afterimages'/name).read_bytes();reverse=after.decode()
    for e in reversed(steps):assert reverse.count(e['after'])==1;reverse=reverse.replace(e['after'],e['before'])
    assert reverse.encode()==before
    records.append(dict(path=name,beforeSha256=sha(before),beforeBytes=len(before),afterSha256=sha(after),afterBytes=len(after),edits=steps,exactReversePassed=True))
patch=''.join(''.join(difflib.unified_diff((HERE/'base'/r['path']).read_text().splitlines(True),(HERE/'afterimages'/r['path']).read_text().splitlines(True),fromfile='a/'+r['path'],tofile='b/'+r['path']))for r in records)
(HERE/'resource-ownership.UNAPPLIED.patch').write_text(patch)
(HERE/'derivations.json').write_text(json.dumps(dict(schemaVersion=1,state='UNAPPLIED_SOURCE_AFTERIMAGES',files=records,productionApplied=False),indent=2)+'\n')
print(json.dumps(dict(files=len(records),exactReversibleEdits=sum(len(r['edits'])for r in records),productionApplied=False)))
