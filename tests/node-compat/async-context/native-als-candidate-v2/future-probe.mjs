// Future ordinary native/Node differential. NOT evaluated by Source/model checks.
// No ALS instance, timer, key or async work at module initialization.
import {AsyncLocalStorage} from 'node:async_hooks';

export async function runPublicAlsProbe(nextTick) {
  if(typeof nextTick!=='function')throw new TypeError('Supply the real native private nextTick binding');
  const a=new AsyncLocalStorage(),b=new AsyncLocalStorage(),rows=[];
  const record=(id,expected)=>{
    const value=a.getStore();
    if(!Object.is(value,expected))throw new Error(id+': context mismatch');
    rows.push({id,value:value===undefined?{type:'undefined'}:{type:typeof value,value}});
  };
  record('initial',undefined);
  await a.run('AWAIT',async()=>{record('run','AWAIT');await Promise.resolve();record('settled-await','AWAIT');});
  record('after-await',undefined);
  let resolvePending;
  const pending=new Promise(resolve=>{resolvePending=resolve;});
  const reaction=a.run('REGISTER',()=>pending.then(()=>record('pending-reaction','REGISTER')));
  a.run('RESOLVE',()=>resolvePending());await reaction;
  await a.run('TIMER',()=>new Promise(resolve=>setTimeout(()=>{record('timer','TIMER');resolve();},0)));
  await a.run('TICK',()=>new Promise(resolve=>nextTick(()=>{record('next-tick','TICK');resolve();})));
  const bound=a.run('BOUND',()=>AsyncLocalStorage.bind(()=>record('bound','BOUND')));
  a.run('CALLER',()=>bound());
  const snapshot=a.run('SNAPSHOT',()=>AsyncLocalStorage.snapshot());
  a.run('CALLER',()=>snapshot(()=>record('snapshot','SNAPSHOT')));
  a.enterWith('OLD');const old=AsyncLocalStorage.bind(()=>record('old-bound','OLD'));
  a.disable();record('disabled',undefined);a.enterWith('NEW');old();record('reenabled-current','NEW');
  let disabled;
  a.exit(()=>{record('exit',undefined);disabled=AsyncLocalStorage.bind(()=>record('exit-capture',undefined));});
  disabled();record('after-exit','NEW');
  a.run('A',()=>b.enterWith('B'));
  if(b.getStore()!=='B')throw new Error('Other instance mutation lost');
  record('other-instance-preserved','NEW');
  for(const thrown of [Object.freeze({failure:true}),null,undefined,0,false]){
    let caught=false;
    try{a.run('THROW',()=>{throw thrown;});}catch(error){if(!Object.is(error,thrown))throw new Error('Thrown value changed');caught=true;}
    if(!caught)throw new Error('Original throw lost');
    record('throw-restoration-'+rows.length,'NEW');
  }
  a.disable();b.disable();
  return JSON.stringify({schemaVersion:1,rows,nativeOrNodeRuntimeRequired:true,
    requestOwnershipOrNativeTeardownProved:false,finalizerContextPropagationProved:false});
}

// The eventual HTTP factory must supply both genuine private native functions.
// Body/stream constructors belong in requestFactory INSIDE the fresh boundary.
export function createRequestBoundaryProbe({runFreshRequest,runNeutralServer}) {
  if(typeof runFreshRequest!=='function'||typeof runNeutralServer!=='function')throw new TypeError('Real private native boundaries required');
  let readiness;
  return {ensureReady(prepare){return runNeutralServer(()=>readiness??=(prepare()),undefined);},
    enter(requestFactory,...args){return runFreshRequest(requestFactory,undefined,...args);}};
}
