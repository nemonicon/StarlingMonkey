// Synthetic event callbacks extracted verbatim from the new browser Source.
// No Playwright import, page/browser, application, request or crypto executes.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {EventEmitter} from 'node:events';
const source=await readFile(new URL('./browser-check.mjs',import.meta.url),'utf8');
const slice=(a,b)=>{const at=source.indexOf(a),end=source.indexOf(b,at);assert(at>=0&&end>at);return source.slice(at,end);};
const traceCode=slice('const traceStart=process.hrtime.bigint();','const save=');
const locals=slice("    let context,page,timer,phase='context-setup';",'    const pending=(async()=>{');
const callbacks=slice("      page.on('request',request=>", "      page.on('pageerror',error=>");
const failed=slice("      page.on('requestfailed',request=>", "      if(id==='server-action')");
const errorFree=source.match(/result\.browserErrorFree=([^;]+);/)[1];
const observations=[];
function harness(){
 const result={trace:[],errors:[],failedrequests:[],responseFinishedObservations:[],pageerrors:[],consoleerrors:[]};
 const page=new EventEmitter();page.mainFrame=()=>page.frame;page.frame={url:()=>'/action-result'};page.url=()=>'/actions';
 const errorData=e=>({name:e.name,message:e.message});
 const api=new Function('result','givenPage','errorData',`${traceCode}\nconst id='server-action';\n${locals}\npage=givenPage;\n${callbacks}\n${failed}\nreturn {mark,finishes,errorFree:()=>(${errorFree})};`)(result,page,errorData);
 const request=(url='/actions',from=null)=>({url:()=>url,method:()=> 'POST',resourceType:()=> 'fetch',isNavigationRequest:()=>false,redirectedFrom:()=>from,failure:()=>({errorText:'net::ERR_ABORTED'})});
 return {result,page,api,request};
}
const tick=()=>new Promise(r=>setImmediate(r));
{
 const {result,page,api,request}=harness(),r=request();api.mark('action-submit-and-navigation');page.emit('request',r);page.emit('requestfailed',r);assert.equal(result.failedrequests.length,1);assert.equal(result.failedrequests[0].phase,'action-submit-and-navigation');assert.equal(api.errorFree(),false);observations.push('pre-close request failure remains failing');
}
{
 const {result,page,api,request}=harness(),r=request();page.emit('request',r);api.mark('context-close-start');page.emit('requestfailed',r);api.mark('context-close-end');assert.equal(result.failedrequests.length,1);assert.equal(result.failedrequests[0].phase,'context-close-start');assert.equal(api.errorFree(),false);assert.deepEqual(result.trace.filter(x=>x.event==='requestfailed').map(x=>x.requestId),[1]);observations.push('during-close request failure also remains failing');
}
{
 const {result,page,api,request}=harness(),r=request();let finish;const pending=new Promise(resolve=>finish=resolve);page.emit('request',r);page.emit('response',{request:()=>r,status:()=>200,statusText:()=> 'OK',finished:()=>pending});assert.equal(api.finishes.size,1);api.mark('context-close-start');finish(new Error('aborted response'));await tick();assert.equal(api.finishes.size,0);assert.equal(result.responseFinishedObservations[0].phase,'context-close-start');assert.equal(result.errors[0].stage,'server-action-response-finished');assert.equal(result.trace.find(x=>x.event==='response.finished').error.message,'aborted response');observations.push('response.finished error retains actual processing phase and error');
}
{
 const {result,page,api,request}=harness(),r=request();page.emit('request',r);page.emit('response',{request:()=>r,status:()=>303,statusText:()=> 'See Other',finished:async()=>null});page.emit('requestfinished',r);await tick();assert.equal(result.errors.length,0);assert.equal(result.responseFinishedObservations[0].error,null);assert.equal(api.errorFree(),true);assert.equal(result.trace.find(x=>x.event==='requestfinished').requestId,1);observations.push('finished response and request IDs correlate');
}
{
 const {result,page,api,request}=harness(),a=request(),b=request('/action-result',a);page.emit('request',a);page.emit('request',b);api.mark('action-result-assert');page.emit('framenavigated',page.frame);assert.equal(result.trace.filter(x=>x.event==='request')[1].redirectedFrom,1);assert.equal(result.trace.find(x=>x.event==='main-frame-navigated').url,'/action-result');observations.push('redirect IDs and navigation recorded');
}
{
 const {result,page,api,request}=harness(),r=request();for(let i=0;i<4002;i++)page.emit('request',r);assert.equal(result.trace.length,4000);assert.equal(result.errors.filter(x=>x.stage==='trace-limit').length,1);observations.push('trace bound is explicit failing error');
}
{
 const {result,page,api,request}=harness(),r=request();api.mark('action-goto');page.emit('request',r);api.mark('context-close-start');page.emit('close');api.mark('context-close-end');const ns=result.trace.map(x=>BigInt(x.ns));assert(ns.every((n,i)=>i===0||n>=ns[i-1]));assert(result.trace.every((r,i)=>r.sequence===i+1));assert(source.includes('beforeCloseNetworkCompletionWait:false'));assert(source.includes('response-finished-drain-after-close'));observations.push('monotonic ordered trace and no pre-close network wait');
}
console.log(JSON.stringify({state:'BROWSER_PHASE_SYNTHETIC_CALLBACK_TESTS_PASSED',tests:observations.length,observations,actualCallbacksExtracted:true,playwrightImported:false,browserOrApplicationExecuted:false}));
