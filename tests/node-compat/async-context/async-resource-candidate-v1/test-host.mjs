import assert from 'node:assert/strict';
import {AsyncLocalStorage, AsyncResource as NodeAsyncResource} from 'node:async_hooks';
import {installAsyncResourceFacade} from './async-resource.mjs';
assert.equal(process.version, 'v22.14.0');
const records = [], root = {AsyncLocalStorage, AsyncResource:NodeAsyncResource};
const oldNamed = root.AsyncResource;
const installed = installAsyncResourceFacade(root), Candidate = root.AsyncResource;
async function test(name, fn) { const value = await fn(); records.push({name, passed:true, value}); }
function catchExact(fn, expected) { let threw=false; try { fn(); } catch (e) { threw=true; assert.equal(e, expected); } assert(threw); }
async function compare(name, scenario) {
  await test(name, async () => {
    const native = await scenario(NodeAsyncResource), candidate = await scenario(Candidate);
    assert.deepEqual(candidate, native); return {node:native, candidate};
  });
}
await test('installation does not capture context and retains the old named binding', () => {
  let calls=0; class ALS extends AsyncLocalStorage { static snapshot(){calls++;return super.snapshot();} }
  const module={AsyncLocalStorage:ALS, AsyncResource:NodeAsyncResource};
  const a=installAsyncResourceFacade(module); assert.equal(calls,0); assert.equal(a,installAsyncResourceFacade(module));
  assert.equal(calls,0); new module.AsyncResource('ordinary-host-test'); assert.equal(calls,1);
  assert.equal(oldNamed,NodeAsyncResource); assert.notEqual(Candidate,oldNamed); return {captureAtInstall:0,captureAtConstruction:1,esmNamedUpdated:false};
});
await compare('registration capture, receiver, arguments, synchronous return and restoration', R => {
  const als=new AsyncLocalStorage(), a={name:'captured'}, b={name:'caller'}, receiver={n:3}; let resource;
  als.run(a,()=>resource=new R('send-cleanup'));
  return als.run(b,()=>{
    const value=resource.runInAsyncScope(function(x,y){assert.equal(this,receiver);assert.equal(als.getStore(),a);return this.n+x+y;},receiver,4,5);
    assert.equal(als.getStore(),b);return {value,callerRestored:true,outer:als.getStore().name};
  });
});
await compare('null/undefined/primitive receivers preserve strict callback semantics', R => {
  const resource=new R('receivers'); return [null,undefined,0,false,'x'].map(value=>resource.runInAsyncScope(function(){return this;},value));
});
await compare('zero arguments and returned object identity', R => {
  const x={},r=new R('return-object');assert.equal(r.runInAsyncScope(()=>x),x);return {identity:true,argc:r.runInAsyncScope(function(){return arguments.length;},null)};
});
await compare('original thrown objects and falsy values restore caller context', R => {
  const als=new AsyncLocalStorage(),a={},b={};let r;als.run(a,()=>r=new R('throws'));
  return als.run(b,()=>{for(const value of [undefined,null,false,0,'',NaN,new Error('original')]){catchExact(()=>r.runInAsyncScope(()=>{assert.equal(als.getStore(),a);throw value;}),value);assert.equal(als.getStore(),b);}return {throws:7,restored:true};});
});
await compare('nested resources restore each captured cell', R => {
  const als=new AsyncLocalStorage(),a={},b={},c={};let ra,rb;als.run(a,()=>ra=new R('a'));als.run(b,()=>rb=new R('b'));
  return als.run(c,()=>{const observations=[];ra.runInAsyncScope(()=>{observations.push(als.getStore()===a);rb.runInAsyncScope(()=>observations.push(als.getStore()===b));observations.push(als.getStore()===a);});observations.push(als.getStore()===c);return observations;});
});
await compare('await and timer descendants inherit real captured ALS', async R => {
  const als=new AsyncLocalStorage(),a={},b={};let r;als.run(a,()=>r=new R('async'));
  return als.run(b,async()=>{const promise=r.runInAsyncScope(async()=>{const before=als.getStore()===a;await Promise.resolve();const after=als.getStore()===a;await new Promise(resolve=>setTimeout(resolve,1));return [before,after,als.getStore()===a];});assert.equal(als.getStore(),b);const result=await promise;return {result,callerAfterAwait:als.getStore()===b};});
});
await compare('Promise rejection preserves original value and captured callback context', async R => {
  const als=new AsyncLocalStorage(),a={},b={},reason={};let r;als.run(a,()=>r=new R('reject'));
  return als.run(b,async()=>{try{await r.runInAsyncScope(async()=>{await Promise.resolve();assert.equal(als.getStore(),a);throw reason;});assert.fail();}catch(e){assert.equal(e,reason);}return {identity:true,callerRestored:als.getStore()===b};});
});
await compare('disable and re-enable follow actual ALS global enable policy', R => {
  const als=new AsyncLocalStorage(),a={},b={};let r;als.run(a,()=>r=new R('disable'));als.disable();
  const disabled=r.runInAsyncScope(()=>als.getStore())===undefined;
  const enabled=als.run(b,()=>{const captured=r.runInAsyncScope(()=>als.getStore())===a;return [captured,als.getStore()===b];});return {disabled,enabled};
});
await compare('capture while exit-disabled excludes store on later enabled caller', R => {
  const als=new AsyncLocalStorage(),a={},b={};let r;als.run(a,()=>als.exit(()=>r=new R('disabled')));
  return als.run(b,()=>[r.runInAsyncScope(()=>als.getStore())===undefined,als.getStore()===b]);
});
await compare('multiple ALS instances preserve mutations within captured resource', R => {
  const a=new AsyncLocalStorage(),b=new AsyncLocalStorage(),aa={},bb={},cc={};let r;
  a.run(aa,()=>b.run(bb,()=>r=new R('two-stores')));
  const first=r.runInAsyncScope(()=>{assert.equal(a.getStore(),aa);assert.equal(b.getStore(),bb);b.enterWith(cc);return true;});
  return [first,r.runInAsyncScope(()=>a.getStore()===aa&&b.getStore()===cc),a.getStore()===undefined,b.getStore()===undefined];
});
await compare('Next on-finished exact lazy constructor and bound cleanup shape', async R => {
  const hooks={AsyncResource:R},als=new AsyncLocalStorage(),marker={},caller={};let wrapped,seen;
  function wrap(fn){let resource;if(hooks.AsyncResource)resource=new hooks.AsyncResource(fn.name||'bound-anonymous-fn');if(!resource||!resource.runInAsyncScope)return fn;return resource.runInAsyncScope.bind(resource,fn,null);}
  als.run(marker,()=>wrapped=wrap(function(error,response){seen={receiver:this===null,context:als.getStore()===marker,error:error===null,response:response.ok};}));
  await als.run(caller,()=>new Promise(resolve=>setImmediate(()=>{wrapped(null,{ok:true});assert.equal(als.getStore(),caller);resolve();})));
  return seen;
});
await test('invalid constructor types and callback/receiver codes',()=>{
  for(const R of [NodeAsyncResource,Candidate])for(const x of [undefined,null,1,{},Symbol('x')])assert.throws(()=>new R(x),e=>e.code==='ERR_INVALID_ARG_TYPE');
  for(const x of [null,{},1]){
    assert.throws(()=>new NodeAsyncResource('valid').runInAsyncScope(x),e=>e instanceof TypeError&&e.code===undefined);
    assert.throws(()=>new Candidate('valid').runInAsyncScope(x),e=>e instanceof TypeError&&e.code==='ERR_INVALID_ARG_TYPE');
  }
  assert.throws(()=>Candidate.prototype.runInAsyncScope.call({},()=>0),e=>e.code==='ERR_INVALID_ARG_TYPE');return true;
});
await test('unsupported IDs, hooks, bind, destroy and options refuse explicitly',()=>{
  const r=new Candidate('refusals');for(const name of ['bind','emitDestroy','asyncId','triggerAsyncId'])assert.throws(()=>r[name](),e=>e.code==='ERR_SM_NODE_UNSUPPORTED'&&e.operation==='AsyncResource.'+name);
  assert.throws(()=>Candidate.bind(()=>0),e=>e.code==='ERR_SM_NODE_UNSUPPORTED');assert.throws(()=>new Candidate('x',{}),e=>e.code==='ERR_SM_NODE_UNSUPPORTED');assert.throws(()=>new Candidate('x',1),e=>e.code==='ERR_SM_NODE_UNSUPPORTED');return {noFakeIds:true,noHookDeliveryClaim:true};
});
await test('bounded type and argument limits are explicit deviations',()=>{assert.throws(()=>new Candidate('x'.repeat(4097)),e=>e.code==='ERR_SM_NODE_ASYNC_CONTEXT_LIMIT');assert.throws(()=>new Candidate('x').runInAsyncScope(()=>0,null,...Array(1024)),e=>e.code==='ERR_SM_NODE_ASYNC_CONTEXT_LIMIT');return true;});
await test('installation refuses immutable bindings and tampering',()=>{
  assert.equal(installed,installAsyncResourceFacade(root));assert.throws(()=>installAsyncResourceFacade(Object.freeze({AsyncLocalStorage,AsyncResource:NodeAsyncResource})),TypeError);
  const module={AsyncLocalStorage,AsyncResource:NodeAsyncResource};installAsyncResourceFacade(module);module.AsyncResource=NodeAsyncResource;assert.throws(()=>installAsyncResourceFacade(module),TypeError);return true;
});
console.log(JSON.stringify({schemaVersion:1,state:'ASYNC_RESOURCE_SELECTED_HOST_DIFFERENTIALS_PASSED_V1',passed:true,hostOnly:true,guestOrNativeExecuted:false,backend:'actual pinned Node22 AsyncLocalStorage.snapshot; no JS context stack',records,cases:records.length}));
