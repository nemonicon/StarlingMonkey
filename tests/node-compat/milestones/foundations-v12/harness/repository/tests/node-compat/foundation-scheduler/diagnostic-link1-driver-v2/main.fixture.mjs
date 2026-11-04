// UNEXECUTED guest template. Host replaces only the oracle declaration below.
import diagnostic,* as namespace from 'starling:test-internal-ticks';
import {nextTick,scheduleTask,attemptReentry,checkResetGuard} from 'starling:test-internal-ticks';
import {Buffer} from 'node:buffer';
const ORACLE = null; // __PINNED_NODE_PHASE_ORACLE__
function check(ok,message){if(!ok)throw new Error('TICK_CHECK:'+message);}
function same(a,b,message){check(JSON.stringify(a)===JSON.stringify(b),message);}
function ownError(operation,code){
 let caught;try{operation();}catch(error){caught=error;}
 check(caught&&Object.hasOwn(caught,'code')&&caught.code===code,'own '+code);
 check(typeof Object.getOwnPropertyDescriptor(caught,'code').value==='string','code data property');
 return caught.name;
}
function scenario(trace){
 Promise.resolve().then(()=>{trace.push('promise-first');nextTick(()=>trace.push('tick-from-promise'));Promise.resolve().then(()=>trace.push('nested-promise'));});
 nextTick(()=>{trace.push('tick-first');nextTick(()=>trace.push('nested-tick'));Promise.resolve().then(()=>trace.push('promise-from-tick'));});
 queueMicrotask(()=>trace.push('microtask'));
}
const initialTrace=[];scenario(initialTrace);let calls=0;
const complete=body=>new Promise(resolve=>{body();scheduleTask(resolve);});
export async function run(){
 ++calls;
 same(Object.getOwnPropertyNames(namespace).sort(),['attemptReentry','checkResetGuard','default','nextTick','scheduleTask'],'finite ESM names');
 check(namespace.default===diagnostic,'default identity');
 for(const name of ['nextTick','scheduleTask','attemptReentry','checkResetGuard'])check(typeof namespace[name]==='function'&&namespace[name]===diagnostic[name],'real named/default function identity: '+name);
 check(typeof namespace.then==='undefined','not thenable');
 same(initialTrace,ORACLE.esm,'initial ESM snapshot');
 const exported=[];await complete(()=>scenario(exported));same(exported,ORACLE.task,'deployed-entry phase');
 check((await import('starling:test-internal-ticks'))===namespace,'cached dynamic namespace');
 const task=[];await new Promise(resolve=>scheduleTask(()=>{scenario(task);scheduleTask(resolve);}));same(task,ORACLE.task,'native task phase');
 const job=[];await new Promise(resolve=>Promise.resolve().then(()=>{scenario(job);scheduleTask(resolve);}));same(job,ORACLE.job,'full jobs before new ticks');
 const observations=[];let object={marker:'rooted-argument'};const weak=new WeakRef(object),symbol=Symbol('argument');
 await new Promise(resolve=>{
  check(nextTick(function(value,s,n){
   observations.push(this===undefined,arguments.length===3,value.marker==='rooted-argument',weak.deref()===value,s===symbol,n===17);
   ownError(attemptReentry,'ERR_SM_NODE_SCHEDULER_REENTRY');ownError(checkResetGuard,'ERR_SM_NODE_SCHEDULER_REENTRY');
   scheduleTask(resolve);
  },object,symbol,17)===undefined,'undefined enqueue result');
  object=null;
 });
 check(observations.every(Boolean),'shared argument identity/strict receiver');
 let queueOnlyCompleted=false;
 await new Promise(resolve=>{
  // No application variable or closure owns this inline callback, object or
  // unregistered Symbol. Only the queue's callback/argument Array retains them;
  // VM temporary-slot retention itself is not instrumented by this fixture.
  nextTick(function(value,token){
   check(value.marker==='queue-only-object'&&typeof token==='symbol'&&token.description==='queue-only-symbol','queue-only GC arguments');
   queueOnlyCompleted=true;scheduleTask(resolve);
  },{marker:'queue-only-object'},Symbol('queue-only-symbol'));
  for(let i=0;i<8;i++)Buffer.from('0011aa','hex');
 });
 check(queueOnlyCompleted,'queue-only callback survived pending-entry hex operations');
 let returnGetterReads=0;
 await complete(()=>nextTick(()=>({get then(){returnGetterReads++;return undefined;}})));
 check(returnGetterReads===0,'tick return-object then getter is ignored');
 for(const value of [undefined,null,1,'callback',{},[]])same(ownError(()=>nextTick(value),'ERR_INVALID_ARG_TYPE'),'TypeError','invalid callback type');
 const foreign=(await import('starling:test-initializer-ticks')).nextTick;
 same(ownError(()=>scheduleTask(foreign),'ERR_SM_NODE_UNSUPPORTED'),'TypeError','guarded foreign diagnostic callback');
 const fifo=[],fifoIdentity={marker:'shared-ring-identity'};
 for(const[start,count]of [[0,3000],[3000,2000]]){
  // A real diagnostic native task separates the batches. Promise.resolve()
  // alone would not flush ticks during the full native job checkpoint.
  await complete(()=>{for(let i=0;i<count;i++)nextTick((value,identity)=>{check(identity===fifoIdentity,'ring argument identity');fifo.push(value);},start+i,fifoIdentity);});
 }
 check(fifo.length===5000&&fifo.every((value,i)=>value===i),'FIFO/ring wrap across native task boundaries');
 let pending=0;
 await complete(()=>{for(let i=0;i<4096;i++)nextTick(()=>{pending++;});ownError(()=>nextTick(()=>{pending+=10000;}),'ERR_SM_NODE_SCHEDULER_LIMIT');});
 check(pending===4096,'pending callback limit/no partial insertion');
 ownError(()=>nextTick(()=>{},...new Array(1025).fill(1)),'ERR_SM_NODE_SCHEDULER_LIMIT');
 const shared={marker:'many-args'},args=new Array(1024).fill(shared);let argumentCalls=0,noArgs=0;
 await complete(()=>{
  for(let n=0;n<64;n++)nextTick(function(){check(arguments.length===1024&&arguments[0]===shared&&arguments[1023]===shared,'argument values');argumentCalls++;},...args);
  ownError(()=>nextTick(()=>{argumentCalls+=10000;},shared),'ERR_SM_NODE_SCHEDULER_LIMIT');
  nextTick(()=>{noArgs++;});
 });
 check(argumentCalls===64&&noArgs===1,'pending argument limit/no partial insertion');
 let recovered=0;await complete(()=>nextTick(()=>{recovered++;}));check(recovered===1,'caught error continuation');
 return JSON.stringify({passed:true,calls,initialTrace,exported,task,job,observations,
   fifo:5000,pendingCallbacks:pending,argumentCalls,noArgs,recovered,returnGetterReads,queueOnlyCompleted,
   snapshotCompleted:true,engineResetExecuted:false,classicInitialProved:false,
   gcScope:'inline callback/object/unregistered Symbol have no app strong co-owner; VM temporary retention uninstrumented; eight valid hex operations while pending; Release-GC selected by actual kernel flags'});
}
