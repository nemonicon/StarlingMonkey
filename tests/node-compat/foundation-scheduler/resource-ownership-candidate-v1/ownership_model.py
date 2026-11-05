"""Meaningful pure ownership protocol checks; no native/JS/timer/host execution."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
CHECKS=0;CASES=[]
def need(v,label):
    global CHECKS
    CHECKS+=1
    if not v:raise AssertionError(label)
class Model:
    def __init__(self):self.next_id=1;self.registry={};self.queue=[];self.live=set();self.drops={};self.last_handle=0;self.roots=[];self.events=[]
    def acquire(self,t):
        self.last_handle+=1;t.handle=self.last_handle;self.live.add(t.handle);self.events.append(('acquire',t.handle))
    def drop(self,t):
        h=t.handle;t.handle=None
        if h is None:return
        need(h in self.live,'never double-drop a host pollable');self.live.remove(h);self.drops[h]=self.drops.get(h,0)+1;self.events.append(('drop',h))
    def create(self,repeat=False,fail=None):
        if self.next_id>2**31-1:return None
        if fail in ['arguments','task','registry']:return None
        t=Timer(self,self.next_id,repeat);self.registry[t.id]=t;self.queue.append(t);self.acquire(t);self.next_id+=1;return t
    def trace(self):
        edges=set()
        for t in [*self.registry.values(),*self.queue,*self.roots]:edges.update(t.edges)
        return edges
    def clear(self,ident):
        t=self.registry.get(ident)
        if t is None:return False
        self.roots.append(t)
        if t in self.queue:self.queue.remove(t);t.retire()
        t.retire();self.roots.pop();return True
    def run(self,t,callback=lambda t:None,argv_fail=False):
        self.roots.append(t)
        if t in self.queue:self.queue.remove(t)
        need(t.retired or t.edges<=self.trace(),'detached running task edges remain traced')
        try:
            if t.retired:return True
            if argv_fail:t.retire();return False
            # Actual C++ Rooted callback/argv retain the copied call values even
            # if clear() retires task edges during the callback.
            call_edges=set(t.edges)
            try:callback(t)
            except BaseException as e:t.retire();return e
            need(call_edges=={'callback-'+str(t.id),'argument-'+str(t.id)},'callback local roots are independent from task clearing')
            if t.retired:return True
            self.drop(t)
            if t.repeat:self.queue.append(t);self.acquire(t)
            else:t.retire()
            return True
        finally:self.roots.pop()
    def clean(self):
        for ident in list(self.registry):self.clear(ident)
        need(not self.registry and not self.queue and not self.live,'all timer owners and pollables retired')
        need(all(n==1 for n in self.drops.values()),'every acquired pollable drops exactly once')
class Timer:
    def __init__(self,m,ident,repeat):self.m=m;self.id=ident;self.repeat=repeat;self.retired=False;self.handle=None;self.edges={'callback-'+str(ident),'argument-'+str(ident)}
    def retire(self):
        if self.retired:return
        self.retired=True;self.m.drop(self)
        if self.m.registry.get(self.id)is self:self.m.registry.pop(self.id)
        self.edges.clear()
def case(name,f):
    before=CHECKS;f();CASES.append(dict(name=name,checks=CHECKS-before,passed=True))
def failure_point(point):
    m=Model();need(m.create(fail=point)is None,'recoverable failure reported');need(m.next_id==1 and not m.registry and not m.queue and not m.live,'recoverable failure publishes/acquires/consumes nothing')
for point in ['arguments','task','registry']:case('registration rollback '+point,lambda point=point:failure_point(point))
def exhaustion():
    m=Model();m.next_id=2**31-1;t=m.create();need(t.id==2**31-1,'last positive int32 ID accepted');m.clear(t.id);need(m.create()is None and m.next_id==2**31,'no signed overflow or ID recycling');m.clean()
case('positive ID exhaustion',exhaustion)
def once():
    m=Model();t=m.create();need(m.run(t)is True,'one-shot success');need(t.retired and not t.edges,'normal completion clears callback/argument roots');m.clean()
case('one-shot successful completion',once)
def failed_argv():
    m=Model();t=m.create();need(m.run(t,argv_fail=True)is False,'argv allocation error propagated');need(t.retired and not t.edges,'argv failure retires native registration and JS edges');m.clean()
case('ordinary argv allocation failure cleanup',failed_argv)
class Thrown(Exception):pass
def callback_throw():
    m=Model();t=m.create(repeat=True);original=Thrown('original')
    def callback(_):raise original
    need(m.run(t,callback)is original,'callback exception identity preserved by cleanup model');need(t.retired and not t.edges,'thrown interval cannot requeue or retain roots');m.clean()
case('callback failure retirement and original exception',callback_throw)
def clear_queued():
    m=Model();t=m.create();need(m.clear(t.id),'queued clear');need(not m.clear(t.id),'already cleared public ID absent');t.retire();t.retire();need(m.run(t)is True,'late invalid task has no callback');m.clean()
case('clear queued/double cancel/late invalid run',clear_queued)
def clear_running():
    m=Model();t=m.create(repeat=True);seen=[]
    def callback(t):seen.append(t.id);need(m.clear(t.id),'running task cancelled despite no queued entry');need(not t.edges,'running task releases saved edges');need(not m.clear(t.id),'second clear is absent')
    need(m.run(t,callback)is True and seen==[t.id],'one in-flight call only');need(not m.queue,'cleared interval never requeues');m.clean()
case('clear running interval exact-once',clear_running)
def repeat():
    m=Model();t=m.create(repeat=True)
    for n in range(4):need(m.run(t)is True and m.registry[t.id]is t and not t.retired,'repeat retains same registered native owner');need(len(m.live)==1,'one current subscription per interval')
    need(len(m.drops)==4,'each old subscription released per turn');m.clear(t.id);m.clean()
case('interval four turns then clear',repeat)
def nested():
    m=Model();a=m.create();b=m.create(repeat=True)
    def callback(t):need(m.clear(b.id),'nested other-task cancel');need(t.edges<=m.trace(),'outer task remains traced across nested cancellation')
    need(m.run(a,callback)is True,'nested cleanup preserves current call');m.clean()
case('nested cancellation keeps outer task traced',nested)
def reset_timer_registry_only():
    m=Model();old=[m.create(),m.create(repeat=True)];old_id=m.next_id;m.clean();new=m.create();need(new.id==old_id and all(new.id!=t.id for t in old),'timer retirement does not rewind IDs');m.clean()
case('timer-only retirement and monotonic IDs',reset_timer_registry_only)
# A counterexample is retained for the old ordinary callback-error sequence:
# dequeue -> callback throws -> early return before unsubscribe/map erase.
baseline=dict(queueOwnerRemoved=True,registryRawPointerRetained=True,pollableDropped=False,callbackErrorReturnedBeforeCleanup=True,nativeTaskMayBeDestroyed=True)
need(baseline['registryRawPointerRetained']and not baseline['pollableDropped']and baseline['nativeTaskMayBeDestroyed'],'baseline ordinary-error model violates ownership invariant')
value=dict(schemaVersion=1,state='PURE_RESOURCE_OWNERSHIP_MODEL_CHECKS_PASSED_NOT_NATIVE_RUNTIME',cases=CASES,checks=CHECKS,baselineCounterexample=baseline,nativeGcOrHostProof=False,queueAllocationFatalNotModeledAsRecoverable=True,hostTrapRollbackNotClaimed=True,fullResetOrRequestReuseUnsupported=True,ownerHelpersOrWorkloadsInvoked=False)
with(HERE/'model-results.json').open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
print(json.dumps(dict(pureCases=len(CASES),checks=CHECKS,nativeRuntimeActions=False)))
