// Host-only orchestration/resource models. Never imports a guest entry or Next.
import assert from 'node:assert/strict';
import {AsyncLocalStorage} from 'node:async_hooks';
import {readFile,writeFile} from 'node:fs/promises';
import {createNeutralReadyHandler,readRoutingOrigin} from './lifecycle.mjs';
import {createWasiHttpHandler} from './adapter-descendant.mjs';
let checks=0;const equal=(a,b)=>{assert.equal(a,b);checks++;};
const context=new AsyncLocalStorage(),events=[];
const neutral=(callback,receiver,...args)=>context.run('neutral',()=>Reflect.apply(callback,receiver,args));
function resource(id){return{id,drops:0,[Symbol.dispose](){this.drops++;}};}
const release=(a,b)=>{a[Symbol.dispose]();b[Symbol.dispose]();};
let prepared=0,unblock;
const gate=new Promise(resolve=>{unblock=resolve;});
const entry=createNeutralReadyHandler({runNeutralServer:neutral,disposeBeforeEntry:release,
  async prepareServer(){equal(context.getStore(),'neutral');prepared++;events.push('prepare');
    await gate;events.push('prepared');return{handle(a,b){
      equal(context.getStore(),'neutral');equal(events.includes('prepared'),true);
      return context.run('fresh-'+a.id,()=>{events.push('body-'+a.id);equal(context.getStore(),'fresh-'+a.id);release(a,b);return a.id;});
    }};},
});
const a=resource('a'),b=resource('b'),oa=resource('oa'),ob=resource('ob');
const first=context.run('first-request-must-not-own-server',()=>entry.handle(a,oa));
const second=context.run('second-request-must-not-own-server',()=>entry.handle(b,ob));
await Promise.resolve();equal(prepared,1);equal(events.some(x=>x.startsWith('body-')),false);
unblock();assert.deepEqual(await Promise.all([first,second]),['a','b']);checks++;
for(const x of [a,b,oa,ob])equal(x.drops,1);
await entry.handle(resource('c'),resource('oc'));equal(prepared,1);
const failureResults=[];
for(const reason of [new Error('preparation'),undefined,null,0,false,Object.freeze({failure:true})]){
  let attempts=0;const failed=createNeutralReadyHandler({runNeutralServer:neutral,disposeBeforeEntry:release,
    prepareServer(){attempts++;throw reason;}});
  const r1=resource('r1'),r2=resource('r2'),p1=resource('p1'),p2=resource('p2');
  const results=await Promise.allSettled([failed.handle(r1,p1),failed.handle(r2,p2)]);
  equal(attempts,1);for(const result of results){equal(result.status,'rejected');equal(result.reason,reason);}
  for(const r of [r1,r2,p1,p2])equal(r.drops,1);
  failureResults.push({reasonType:typeof reason,sticky:true,disposedPairs:2});
}
for(const value of [undefined,{}, {handle:3}]){
  const malformed=createNeutralReadyHandler({runNeutralServer:neutral,disposeBeforeEntry:release,prepareServer:()=>value});
  const r=resource('r'),p=resource('p');await assert.rejects(malformed.handle(r,p),TypeError);checks++;
  equal(r.drops,1);equal(p.drops,1);
}
const refusal=Object.freeze({nativeRefusal:true});
for(const wrapper of ['neutral','fresh']){
  const r=resource('r'),p=resource('p');let entered=0,actual,threw=false;
  const handler=wrapper==='neutral'?createNeutralReadyHandler({runNeutralServer(){throw refusal;},
    disposeBeforeEntry:release,prepareServer(){entered++;}}):createWasiHttpHandler(()=>{entered++;},{},()=>{throw refusal;});
  try{handler.handle(r,p);}catch(error){threw=true;actual=error;}
  equal(threw,true);equal(actual,refusal);equal(entered,0);equal(r.drops,1);equal(p.drops,1);
}
// Once native entry called the body, its original finally owns both drops.
const enteredFailure=new Error('headers');const incoming=resource('incoming'),outparam=resource('outparam');
incoming.headers=()=>{throw enteredFailure;};
const entered=createWasiHttpHandler(()=>{}, {},(callback,receiver,...args)=>Reflect.apply(callback,receiver,args));
const observed=await Promise.allSettled([entered.handle(incoming,outparam)]);
equal(observed[0].reason,enteredFailure);equal(incoming.drops,1);equal(outparam.drops,1);
// Disposal failure still attempts the second resource and preserves original.
const bad=resource('bad'),good=resource('good');bad[Symbol.dispose]=()=>{bad.drops++;throw new Error('dispose');};
const diagnostic=console.error;let disposalDiagnostics=0;
try{console.error=(code,n)=>{equal(code,'NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE');equal(n,1);disposalDiagnostics++;};
  const h=createWasiHttpHandler(()=>{}, {},()=>{throw refusal;});
  let actual;try{h.handle(bad,good);}catch(error){actual=error;}equal(actual,refusal);
}finally{console.error=diagnostic;}
equal(bad.drops,1);equal(good.drops,1);equal(disposalDiagnostics,1);
for(const [text,hostname,port]of [['http://127.0.0.1:8080','127.0.0.1',8080],['https://example.test','example.test',443],['http://localhost','localhost',80]]){
  const x=readRoutingOrigin(text);equal(x.origin,text);equal(x.hostname,hostname);equal(x.port,port);
}
for(const invalid of [undefined,null,3,'','file:///app','ftp://example.test','http://user@x','http://x/path',
  'http://x?query','http://x#fragment','http://x/','http://x:0','http://x:65536','http://x:80','HTTP://X',
  ' http://x','https://user:secret@example.test']){
  assert.throws(()=>readRoutingOrigin(invalid));checks++;
}
const parent=await readFile(new URL('./references.json',import.meta.url),'utf8');assert(JSON.parse(parent).actualComponent===null);checks++;
const result={schemaVersion:1,sourceOnly:true,checks,concurrentFirstRequests:2,preparationAttempts:prepared,
  stickyFailureModels:failureResults.length,nativePreEntryRefusalCases:2,enteredFailureDisposalOnce:true,
  actualGuestOrNextOrNativeContextExecuted:false,contextProvider:'Host Node AsyncLocalStorage; model only',
  currentNativeSemanticProof:false};
await writeFile(new URL('./model-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
