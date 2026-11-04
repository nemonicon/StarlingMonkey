// Uses a diagnostic native context primitive, never Promise.then monkeypatches.
const p=globalThis.__asyncContextProbe;
if(!p)throw new Error('Missing separate native context probe extension');
let calls=0;
const empty='<undefined>';
const label=()=>p.read()===undefined?empty:p.read();
const deferred=()=>{let resolve;const promise=new Promise(done=>resolve=done);return{promise,resolve};};
function eq(observed,expected,operation){if(observed!==expected)throw new Error(`${operation}: ${String(observed)} != ${String(expected)}`);}
async function runChecks(){
  calls++;
  const observations=[];
  const note=(name,expected)=>{const observed=label();eq(observed,expected,name);observations.push({name,observed});};
  note('entry',empty);
  p.with('A',()=>{note('nested:A','A');p.with('B',()=>note('nested:B','B'));note('nested:restore-A','A');try{p.with('THROW',()=>{throw 17;});}catch(error){eq(error,17,'identity');}note('throw:restore-A','A');});
  note('nested:root',empty);
  const a=deferred(),b=deferred();
  const worker=(name,gate)=>p.with(name,async()=>{note(name+':before',name);await gate;note(name+':pending',name);await Promise.resolve(1);note(name+':settled',name);await 1;note(name+':primitive',name);});
  const wa=worker('WA',a.promise),wb=worker('WB',b.promise);
  p.with('RESOLVER',()=>{b.resolve();a.resolve();});
  await Promise.all([wa,wb]);note('workers:root',empty);
  const native=deferred();let rootNative=false,scopedNative=false;
  p.nativeThen(native.promise,()=>{note('native:root',empty);rootNative=true;});
  p.with('NATIVE',()=>p.nativeThen(native.promise,()=>{note('native:scoped','NATIVE');scopedNative=true;}));
  p.with('OTHER',()=>native.resolve());
  await native.promise;await 0;
  eq(rootNative,true,'native root callback');eq(scopedNative,true,'native scoped callback');
  let settledNative=false;
  p.with('SETTLED-NATIVE',()=>p.nativeThen(Promise.resolve(),()=>{note('native:settled','SETTLED-NATIVE');settledNative=true;}));
  await 0;eq(settledNative,true,'settled native callback');
  await new Promise(done=>p.with('MICRO',()=>queueMicrotask(()=>{note('queueMicrotask','MICRO');done();})));
  const target=p.with('CREATED',deferred);
  const waiting=p.with('WAITER',async()=>{await target.promise;note('thenable:waiter','WAITER');});
  p.with('RESOLVED',()=>target.resolve({then(done){note('thenable:then','CREATED');done(7);}}));
  await waiting;
  const species=deferred();
  function Species(executor){return p.with('SPECIES',()=>new Promise(executor));}
  species.promise.constructor={[Symbol.species]:Species};
  const speciesDone=p.with('REGISTER',()=>species.promise.then(()=>note('species:real-promise','SPECIES')));
  p.with('SPECIES-RESOLVE',()=>species.resolve());await speciesDone;
  const live={value:'retained'};const moving=deferred();
  const afterGC=p.with(live,async()=>{await moving.promise;eq(p.read(),live,'context token survived moving GC');});
  p.gc();p.with('GC-RESOLVER',()=>moving.resolve());await afterGC;
  observations.push({name:'movingGC',observed:true});
  const taskDone=deferred();
  p.with('TASK',()=>p.schedule(()=>{note('guest-task:callback','TASK');taskDone.resolve();}));
  let cancelledRan=false;const cancelled=p.with('CANCEL',()=>p.schedule(()=>{cancelledRan=true;}));
  eq(p.cancel(cancelled),true,'cancel queued resource');eq(p.cancel(cancelled),false,'cancel idempotence');
  await p.with('TASK-WAITER',async()=>{await taskDone.promise;note('guest-task:await','TASK-WAITER');});
  eq(cancelledRan,false,'cancelled callback not run');
  await p.with('OPTIMIZED',async()=>{await 0;const before=p.stats();for(let i=0;i<16;i++){await 0;note('optimized:'+i,'OPTIMIZED');}const after=p.stats();observations.push({name:'optimizedAwaitMetric',noAdditionalEnqueues:after.enqueues===before.enqueues,before:before.enqueues,after:after.enqueues});});
  // Deliberate known gap: plain-object Promise species has no Node promise
  // execution resource. Generic SM hooks cannot distinguish this from await.
  const plain=Promise.resolve();
  function PlainSpecies(executor){executor(()=>{},()=>{});return{};}
  plain.constructor={[Symbol.species]:PlainSpecies};
  let plainObserved;
  p.with('PLAIN-REGISTER',()=>plain.then(()=>{plainObserved=label();}));
  await 0;
  note('final',empty);
  return JSON.stringify({calls,observations,stats:p.stats(),knownGaps:[{case:'non-Promise species reaction',nodeExpected:empty,observed:plainObserved,matchesNode:plainObserved===empty}],scope:'Native registration-time Promise context experiment; not a production AsyncLocalStorage implementation. Guest immediate task exercises existing event loop without external I/O.'});
}

export async function run(){try{return await runChecks();}catch(error){return JSON.stringify({failure:String(error),stack:error.stack,calls,stats:p.stats()});}}
