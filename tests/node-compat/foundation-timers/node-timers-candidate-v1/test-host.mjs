import assert from 'node:assert/strict';
import * as nodeTimers from 'node:timers';
import * as nodePromises from 'node:timers/promises';
import {promisify} from 'node:util';
import {AsyncLocalStorage} from 'node:async_hooks';
import {readFile,writeFile} from 'node:fs/promises';
import {createTimersFacade} from './timers-core.mjs';
import {createHostBackend} from './host-backend.mjs';
assert.equal(process.version,'v22.14.0');
const inventory=JSON.parse(await readFile(new URL('./node22-inventory.json',import.meta.url),'utf8'));
const backend=createHostBackend(),g=createTimersFacade({kernel:backend.kernel,promisifyCustom:promisify.custom,disposeSymbol:Symbol.dispose,AbortSignal,EventTarget,inventory});
const t=g.root.default,p=g.promises.default,results=[];let checks=0;
async function test(id,fn){await fn();checks++;results.push({id,passed:true});}
function err(fn){try{fn();return null;}catch(e){return{name:e.name,code:e.code??null};}}
try{
 await test('factory-no-scheduling',()=>assert.equal(backend.active(),0));
 await test('exact-pinned-names',()=>{assert.deepEqual(Object.keys(g.root).sort(),Object.keys(nodeTimers).sort());assert.deepEqual(Object.keys(g.promises).sort(),Object.keys(nodePromises).sort());});
 await test('default-named-global-identity',()=>{for(const n of Object.keys(g.globals)){assert.equal(g.globals[n],t[n]);assert.equal(g.root[n],t[n]);}assert.equal(t.promises,p);assert.equal(g.root.promises,p);});
 await test('actual-Next-mutable-CJS-patch',()=>{const old=t.setImmediate,patch=function(){};const localGlobal={...g.globals};localGlobal.setImmediate=t.setImmediate=patch;assert.equal(localGlobal.setImmediate,t.setImmediate);t.setImmediate=old;const pi=p.setImmediate;p.setImmediate=patch;assert.equal(t.promises.setImmediate,patch);p.setImmediate=pi;});
 for(const name of ['setTimeout','setInterval','setImmediate'])await test('invalid-callback-'+name,()=>assert.deepEqual(err(()=>t[name](null)),err(()=>nodeTimers[name](null))));
 await test('native-immediate-separate-from-timeout',async()=>{let value;await new Promise(resolve=>t.setImmediate(function(a,b){value=[a,b,this.constructor.name];resolve();},3,'x'));assert.deepEqual(value,[3,'x','Immediate']);assert.equal(backend.events.at(-1)[2],2);});
 await test('immediate-retires-reference-before-callback',async()=>{await new Promise(resolve=>t.setImmediate(function(){assert.equal(this.hasRef(),false);assert.equal(this.ref().hasRef(),false);assert.equal(backend.referenced(),0);resolve();}));});
 await test('actual-callback-receiver-timeout',async()=>{const result=await new Promise(resolve=>t.setTimeout(function(x){resolve([this.constructor.name,x]);},1,7));assert.deepEqual(result,['Timeout',7]);});
 await test('numeric-timeout-clear',async()=>{let called=false;const h=t.setTimeout(()=>called=true,2);t.clearTimeout(+h);await nodePromises.setTimeout(5);assert.equal(called,false);assert.equal(backend.active(),0);});
 await test('clear-immediate-and-dispose',async()=>{let called=false;const a=t.setImmediate(()=>called=true);a[Symbol.dispose]();const b=t.setImmediate(()=>called=true);t.clearImmediate(b);await nodePromises.setImmediate();assert.equal(called,false);assert.equal(a.hasRef(),false);});
 await test('ref-unref-real-host-handle-interest',()=>{const h=t.setTimeout(()=>{},60000);assert.equal(backend.referenced(),1);assert.equal(h.unref(),h);assert.equal(h.hasRef(),false);assert.equal(backend.referenced(),0);assert.equal(h.ref(),h);assert.equal(h.hasRef(),true);assert.equal(backend.referenced(),1);h.close();assert.equal(backend.active(),0);});
 await test('closed-timeout-reference-semantics',()=>{const h=t.setTimeout(()=>{},60000);h.close();assert.equal(h.hasRef(),true);assert.equal(h.unref().hasRef(),false);assert.equal(h.ref().hasRef(),true);assert.equal(backend.referenced(),0);});
 await test('closed-immediate-does-not-revive',()=>{const h=t.setImmediate(()=>{});t.clearImmediate(h);assert.equal(h.hasRef(),false);assert.equal(h.ref().hasRef(),false);assert.equal(backend.active(),0);});
 await test('interval-self-clear',async()=>{const got=await new Promise(resolve=>{let n=0;const h=t.setInterval(()=>{if(++n===3){t.clearInterval(h);resolve(n);}},1);});assert.equal(got,3);assert.equal(backend.active(),0);});
 await test('active-timeout-refresh',async()=>{let calls=0;const h=t.setTimeout(()=>calls++,4);assert.equal(h.refresh(),h);await nodePromises.setTimeout(10);assert.equal(calls,1);assert.equal(backend.active(),0);});
 await test('refresh-during-callback-retains-original-ALS-cell',async()=>{const als=new AsyncLocalStorage(),values=[];await new Promise(resolve=>als.run('A',()=>{let count=0;const h=t.setTimeout(()=>{values.push(als.getStore());if(++count===1)als.run('B',()=>h.refresh());else resolve();},1);}));assert.deepEqual(values,['A','A']);assert.equal(backend.active(),0);});
 await test('retired-refresh-explicit-deviation',async()=>{const h=t.setTimeout(()=>{},1);await nodePromises.setTimeout(5);assert.equal(err(()=>h.refresh()).code,'ERR_SM_NODE_TIMER_INACTIVE');});
 await test('foreign-prototype-guards',()=>{const h=t.setTimeout(()=>{},60000);assert.equal(err(()=>Object.getPrototypeOf(h).unref.call({})).code,'ERR_INVALID_THIS');t.clearTimeout(h);});
 await test('nextTick-promise-immediate-handshake-host-only',async()=>{const order=[];await new Promise(resolve=>{t.setImmediate(()=>{order.push('a');process.nextTick(()=>order.push('tick'));Promise.resolve().then(()=>order.push('micro'));t.setImmediate(()=>{order.push('b');resolve();});});});assert.deepEqual(order,['a','tick','micro','b']);});
 await test('actual-host-ALS-registration-cell',async()=>{const als=new AsyncLocalStorage();const values=await new Promise(resolve=>{const out=[];als.run('A',()=>t.setImmediate(()=>{out.push(als.getStore());if(out.length===2)resolve(out);}));als.run('B',()=>t.setTimeout(()=>{out.push(als.getStore());if(out.length===2)resolve(out);},1));});assert.deepEqual(values.sort(),['A','B']);});
 for(const name of ['setTimeout','setImmediate'])await test('promisify-custom-'+name,()=>{assert.equal(t[name][promisify.custom],p[name]);assert.equal(promisify(t[name]),p[name]);});
 await test('promises-timeout-value',async()=>assert.deepEqual(await p.setTimeout(1,{x:7}),await nodePromises.setTimeout(1,{x:7})));
 await test('promises-immediate-value',async()=>assert.equal(await p.setImmediate('v'),await nodePromises.setImmediate('v')));
 for(const name of ['setTimeout','setImmediate']){
  await test('already-aborted-'+name,async()=>{const ac=new AbortController();ac.abort(null);const before=backend.active();let error;try{await(name==='setImmediate'?p[name]('v',{signal:ac.signal}):p[name](1,'v',{signal:ac.signal}));}catch(e){error=e;}assert.equal(error.name,'AbortError');assert.equal(error.code,'ABORT_ERR');assert.equal(error.cause,null);assert.equal(backend.active(),before);});
  await test('later-abort-clears-native-'+name,async()=>{const ac=new AbortController(),reason={id:9};const value=name==='setImmediate'?p[name]('v',{signal:ac.signal}):p[name](60000,'v',{signal:ac.signal});ac.abort(reason);await assert.rejects(value,e=>e.name==='AbortError'&&e.code==='ABORT_ERR'&&e.cause===reason);assert.equal(backend.active(),0);});
 }
 await test('promise-unref-has-other-real-refed-activity',async()=>{const guard=nodeTimers.setTimeout(()=>{},15);try{const result=await p.setTimeout(1,'ok',{ref:false});assert.equal(result,'ok');}finally{nodeTimers.clearTimeout(guard);}});
 for(const opts of [null,7,{ref:1},{signal:{aborted:false}}])await test('promise-invalid-options-'+JSON.stringify(opts),async()=>{await assert.rejects(p.setTimeout(1,0,opts),e=>e.code==='ERR_INVALID_ARG_TYPE');assert.equal(backend.active(),0);});
 await test('scheduler-real-native-promises',async()=>{assert.equal(await p.scheduler.yield(),undefined);assert.equal(await p.scheduler.wait(1),undefined);});
 for(const name of ['_unrefActive','active','enroll','unenroll'])for(const ctor of [false,true])await test('deferred-'+name+'-'+ctor,()=>assert.equal(err(()=>ctor?new t[name]():t[name]()).code,'ERR_SM_NODE_UNSUPPORTED'));
 await test('promises-interval-deferred',()=>assert.equal(err(()=>p.setInterval()).code,'ERR_SM_NODE_UNSUPPORTED'));
 backend.phase(false);await test('INIT-acquisition-refused',()=>{assert.equal(err(()=>t.setTimeout(()=>{},1)).code,'ERR_SM_NODE_TIMERS_INITIALIZATION');assert.equal(err(()=>t.setImmediate(()=>{})).code,'ERR_SM_NODE_TIMERS_INITIALIZATION');assert.equal(backend.active(),0);});backend.phase(true);
 const out={schemaVersion:1,passed:true,checks,results,backend:'TEST-ONLY actual stock Node timers/refcounts/ALS',node:process.version,actualGuest:false,nativeCppExecuted:false,qualification:'Real Node differential/facade orchestration tests do not prove target queues, event-loop no-block policy, pollable drops, ALS native roots, Native GC, link, snapshot or Store teardown.'};
 await writeFile(new URL('./host-tests.json',import.meta.url),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({passed:true,checks,active:backend.active()}));
}finally{backend.close();}
