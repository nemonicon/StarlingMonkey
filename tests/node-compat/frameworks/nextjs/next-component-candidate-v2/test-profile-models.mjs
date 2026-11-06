// Exact pinned Node22 default-backend differential / host realm models only.
import assert from 'node:assert/strict';
import {AsyncLocalStorage} from 'node:async_hooks';
import vm from 'node:vm';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {installNodeGlobalAlias} from './profile-prelude.mjs';
import {evaluateCapturedStoreRestoration} from './als-store-contract.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);
assert(!process.env.NODE_OPTIONS,'Require exact default Node22 backend without NODE_OPTIONS');
assert.equal(createHash('sha256').update(await readFile(process.execPath)).digest('hex'),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const cases=[];function test(name,fn){fn();cases.push({name,passed:true});}
const target={};
test('actual pinned Node main global descriptor is writable enumerable configurable self-alias',()=>{
  const d=Object.getOwnPropertyDescriptor(globalThis,'global');assert.equal(global,globalThis);assert.equal(d.value,globalThis);assert.equal(d.writable,true);assert.equal(d.enumerable,true);assert.equal(d.configurable,true);
});
test('prelude installs the same descriptor and is idempotent',()=>{
  assert.equal(installNodeGlobalAlias(target),true);assert.equal(target.global,target);
  const d=Object.getOwnPropertyDescriptor(target,'global');assert.deepEqual({...d,value:'self'},{value:'self',writable:true,enumerable:true,configurable:true});
  assert.equal(installNodeGlobalAlias(target),false);assert.equal(installNodeGlobalAlias(globalThis),false);
});
test('prelude does not mutate Object.prototype',()=>assert.equal(Object.hasOwn(Object.prototype,'global'),false));
test('accessor collision refuses without invoking the getter',()=>{
  let getters=0;const poisoned={};Object.defineProperty(poisoned,'global',{get(){getters++;throw Error('getter');},configurable:true});
  assert.throws(()=>installNodeGlobalAlias(poisoned),TypeError);assert.equal(getters,0);
});
test('wrong value or descriptor flags refuse rather than silently mask a collision',()=>{
  for(const d of [{value:{}},{value:null},{writable:false},{enumerable:false},{configurable:false}]){
    const object={};Object.defineProperty(object,'global',{value:object,writable:true,enumerable:true,configurable:true,...d});
    assert.throws(()=>installNodeGlobalAlias(object),TypeError);
  }
});
test('invalid targets refuse',()=>{for(const x of [null,undefined,0,false,'x']){
  if(x===undefined)continue; // undefined invokes the documented globalThis default.
  assert.throws(()=>installNodeGlobalAlias(x),TypeError);
}});
test('actual Node private VM context has no implicit Node global alias',()=>{
  const sandbox={process:{env:{NEXT_DEPLOYMENT_ID:'model'}}};
  assert.equal(vm.runInNewContext('typeof global',sandbox),'undefined');
  assert.equal(vm.runInNewContext('globalThis.result=process.env.NEXT_DEPLOYMENT_ID+":vm"',sandbox),'model:vm');assert.equal(sandbox.result,'model:vm');
  assert.equal(Object.hasOwn(sandbox,'global'),false);assert.equal(globalThis.global,globalThis);
});
test('explicit installation in a private VM realm stays in that realm',()=>{
  const context=vm.createContext({}),realmGlobal=vm.runInContext('globalThis',context);
  assert.notEqual(realmGlobal,globalThis);installNodeGlobalAlias(realmGlobal);
  assert.equal(vm.runInContext('global===globalThis',context),true);
  assert.equal(vm.runInContext('Object.getOwnPropertyDescriptor(globalThis,"global").enumerable',context),true);
  assert.equal(globalThis.global,globalThis);
});
let alsOracle;
test('default Node22 old snapshot/bind-inside-exit expectation is false',()=>{
  const state=new AsyncLocalStorage(),marker={request:'captured'};
  state.run(marker,()=>{
    const snapshot=AsyncLocalStorage.snapshot(),bound=AsyncLocalStorage.bind(()=>state.getStore());
    const snapshotInsideExit=state.exit(()=>snapshot(()=>state.getStore()));
    const boundInsideExit=state.exit(()=>bound());
    assert.equal(snapshotInsideExit,undefined);assert.equal(boundInsideExit,undefined);assert.equal(state.getStore(),marker);
    alsOracle={backend:'Node22 default async_hooks; no --experimental-async-context-frame',snapshotInsideExit:'undefined',boundInsideExit:'undefined',oldMarkerPredicate:false};
    const corrected=evaluateCapturedStoreRestoration(state,AsyncLocalStorage,marker);
    assert(Object.values(corrected).every(x=>x===true));alsOracle.corrected=corrected;
    assert.equal(state.exit(()=>state.getStore()),undefined);assert.equal(state.getStore(),marker);
    alsOracle.separateExitUndefined=true;alsOracle.afterExitMarkerRestored=true;
  });
  assert.equal(state.getStore(),undefined);state.disable();assert.equal(state.getStore(),undefined);
});
const result={schemaVersion:1,state:'NEXT_PROFILE_PRELUDE_AND_DEFAULT_NODE22_ALS_SOURCE_CHECKS_PASSED_V1',passed:true,
  nodeVersion:process.version,nodeExecutable:process.execPath,nodeExecArgv:process.execArgv,nodeOptionsPresent:false,
  cases,alsOracle,hostOnly:true,nativeVmOrAlsOrGuestExecuted:false,privateVMModel:'Actual host Node VM realms; not a nativeVM execution claim'};
await writeFile(new URL('./profile-model-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
