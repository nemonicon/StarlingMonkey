'use strict';
// Real --legacy-script bootstrap. Top-level LETs are global lexical bindings,
// not properties on globalThis. The first drained import job captures the
// content-realm private callable; a later configured --eval runs smSeed().
let smTick;
let smTrace=[];
let smSeed=()=>{
 if(typeof smTick!=='function')throw new Error('TICK_CLASSIC_CAPTURE_NOT_DRAINED');
 const nextTick=smTick;
 Promise.resolve().then(()=>{smTrace.push('promise-first');nextTick(()=>smTrace.push('tick-from-promise'));Promise.resolve().then(()=>smTrace.push('nested-promise'));});
 nextTick(()=>{smTrace.push('tick-first');nextTick(()=>smTrace.push('nested-tick'));Promise.resolve().then(()=>smTrace.push('promise-from-tick'));});
 queueMicrotask(()=>smTrace.push('microtask'));
 return {run(){return JSON.stringify({trace:smTrace,subsequentConfiguredClassicEvaluation:true,
  firstStartupPriorityProved:false,globalObjectProperties:['smTick','smTrace','smSeed'].map(name=>Object.hasOwn(globalThis,name))});}};
};
import('starling:test-internal-ticks').then(module=>{smTick=module.nextTick;});
0;
