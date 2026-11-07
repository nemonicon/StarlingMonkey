"""Pure ownership-state models. No WASI objects, native code or actors execute."""
import json

checks = 0

def check(value):
    global checks
    if value is not True:
        raise AssertionError('ownership model check ' + str(checks + 1))
    checks += 1

class Body:
    def __init__(self):
        self.events = []
        self.pending = None
        self.subscription = None
        self.terminal = False
        self.cancel_requested = False
        self.append_selected = False

    def queue(self):
        if self.terminal or self.cancel_requested or self.pending is not None or self.append_selected:
            return None
        task = Read(self)
        self.pending = self.subscription = task
        self.events.append('subscribe')
        return task

    def dispose(self, eof):
        if self.terminal:
            return
        if self.pending is not None or self.subscription is not None or self.append_selected:
            raise ValueError('live read/subscription')
        self.terminal = True
        self.events.append('input-stream.drop')
        if eof:
            self.events += ['body.finish', 'uninspected-trailers-future.drop']
        else:
            self.events.append('body.drop')

    def cancel(self):
        if self.append_selected:
            return 'deferred-append'
        self.cancel_requested = True
        if self.pending is not None:
            if self.pending.running:
                return 'deferred'
            self.events.append('task.erase')
            self.pending.retire()
        self.dispose(False)
        return 'complete'

    def select_append(self):
        if self.pending is not None:
            return 'read-fallback'
        self.append_selected = True
        return 'append-selected'

class Read:
    def __init__(self, body):
        self.body, self.retired, self.running = body, False, False

    def retire(self):
        if self.retired:
            return
        self.retired = True
        if self.body.pending is self:
            self.body.pending = None
        if self.body.subscription is self:
            self.body.subscription = None
            self.body.events.append('pollable.drop')

    def complete(self, eof=False, error=False, primary=None):
        self.running = True
        self.retire()
        if self.body.cancel_requested or error:
            self.body.dispose(False)
        elif eof:
            self.body.dispose(True)
        else:
            self.body.events.append('enqueue-owned-bytes')
        return primary

class Future:
    def __init__(self, streamed=False):
        self.owner = 'slot' if streamed else 'task'
        self.events = ['slot.owns'] if streamed else ['slot.null', 'task.owns', 'subscribe']

    def transfer(self):
        if self.owner != 'slot':
            raise ValueError('not slot-owned')
        self.events += ['slot.null', 'task.owns', 'subscribe']
        self.owner = 'task'

    def not_ready(self):
        if self.owner != 'task':
            raise ValueError('not task-owned')
        self.events.append('requeue')

    def retire(self):
        if self.owner == 'retired':
            return
        if self.owner != 'task':
            raise ValueError('pending-upload terminal state deferred')
        self.owner = 'retired'
        self.events += ['task.null', 'pollable.drop', 'future.drop', 'wrapper.delete']

for size in [0, 1, 8192]:
    body = Body(); task = body.queue(); task.complete()
    check(body.terminal is False)
    check(body.events == ['subscribe', 'pollable.drop', 'enqueue-owned-bytes'])
    check(body.pending is None and body.subscription is None)
    task.retire()
    check(body.events.count('pollable.drop') == 1)
    next_task = body.queue(); task.retire()
    check(body.pending is next_task and body.subscription is next_task)
    next_task.complete(eof=True)
    check(body.events[-3:] == ['input-stream.drop', 'body.finish', 'uninspected-trailers-future.drop'])
    check(body.events.count('body.finish') == 1 and 'body.drop' not in body.events)
    snapshot = body.events.copy(); body.dispose(True); body.dispose(False)
    check(body.events == snapshot)

body = Body(); task = body.queue()
try:
    body.dispose(False)
except ValueError:
    check(body.terminal is False and body.events == ['subscribe'])
else:
    raise AssertionError('active borrow was dropped')
check(body.cancel() == 'complete')
check(body.events == ['subscribe', 'task.erase', 'pollable.drop', 'input-stream.drop', 'body.drop'])
snapshot = body.events.copy(); body.cancel(); task.retire()
check(body.events == snapshot)

body = Body(); task = body.queue(); task.running = True
check(body.cancel() == 'deferred' and body.events == ['subscribe'])
task.complete()
check(body.events == ['subscribe', 'pollable.drop', 'input-stream.drop', 'body.drop'])
check('enqueue-owned-bytes' not in body.events)

for primary in [None, False, 0, '', object()]:
    body = Body(); task = body.queue()
    check(task.complete(error=True, primary=primary) is primary)
    check(body.events[-2:] == ['input-stream.drop', 'body.drop'])
    check('body.finish' not in body.events)

for streamed in [False, True]:
    for terminal in ['ready', 'get-error', 'cancel', 'preheader-abort', 'destructor']:
        future = Future(streamed)
        if streamed:
            future.transfer()
            check(future.events.index('slot.null') < future.events.index('task.owns'))
        future.not_ready()
        check(future.owner == 'task' and 'future.drop' not in future.events)
        future.retire(); before = future.events.copy(); future.retire()
        check(future.events == before)
        check(future.events[-4:] == ['task.null', 'pollable.drop', 'future.drop', 'wrapper.delete'])
        check(future.events.count('future.drop') == 1 and future.events.count('pollable.drop') == 1)

future = Future(True)
try:
    future.retire()
except ValueError:
    check(future.owner == 'slot')
else:
    raise AssertionError('deferred pending-upload terminal cleanup was invented')

body = Body(); pending = body.queue()
check(body.select_append() == 'read-fallback')
check(body.pending is pending and body.append_selected is False)
pending.complete()
check(body.select_append() == 'append-selected')
before = body.events.copy()
check(body.cancel() == 'deferred-append' and body.cancel_requested is False)
check(body.events == before and body.queue() is None)
try:
    body.dispose(False)
except ValueError:
    check(body.events == before and body.terminal is False)
else:
    raise AssertionError('deferred append owner was dropped by read cleanup')
print(json.dumps(dict(pureOwnershipModels=True, checks=checks, nativeOrWasiOrActorExecuted=False,
                      normativeOrderingModelsNotExecutionProof=True)))
