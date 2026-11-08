// Real browser checks for the owned stock-Node Next fixture. No action at import
// is promised: this is a standalone worker, launched only by the experiment.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {mkdir,readFile,writeFile,realpath,open,lstat} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {join,resolve,relative,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';

assert.equal(process.version,'v22.14.0');
const args=process.argv.slice(2),options={};
assert.equal(args.length,6,'--origin URL --tools DIR --output FRESH');
for(let i=0;i<args.length;i+=2){assert(['--origin','--tools','--output'].includes(args[i])&&!Object.hasOwn(options,args[i]));options[args[i]]=args[i+1];}
const origin=new URL(options['--origin']);
assert(['http:','https:'].includes(origin.protocol)&&origin.pathname==='/'&&!origin.search&&!origin.hash&&!origin.username&&!origin.password,'Plain origin URL required');
const tools=resolve(options['--tools']),output=resolve(options['--output']);
const chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',limit=20000;
await mkdir(output,{mode:0o700}); // Exclusive fresh output; never overwrite a prior run.
const netlogPath=join(output,'netlog.json'),netlogReadLimit=20*1024*1024;
async function descriptor(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
const result={schemaVersion:1,suite:'nextjs-hydration-browser-diagnostic-v2',origin:origin.origin,playwrightVersion:null,browserVersion:null,
  executable:null,tests:[],pageerrors:[],consoleerrors:[],failedrequests:[],actionPosts:[],errors:[],
  browserClosed:false,ephemeralContexts:true,userProfileUsed:false,perTestTimeoutMs:limit,wasmBrowserRun:null,targetRuntimeProvenance:'Parent Root records actual host; the browser origin alone does not identify it',
  cdpEvents:[],cdpCorrelations:[],cdpScope:{events:['Network.requestWillBeSent','Network.responseReceived','Network.dataReceived','Network.loadingFinished','Network.loadingFailed','Page.navigatedWithinDocument','Page.frameNavigated'],payloads:'Complete semantic protocol JSON; not original wire bytes',protocolClock:'CDP timestamps/monotonic seconds and wallTime retain original values; no conversion to Node hrtime',arrivalClock:'Node process.hrtime relative nanoseconds shared with Playwright trace',idCorrelation:'CDP IDs and per-test Playwright WeakMap IDs are distinct; URL/method matches are candidates only'},
  assetBodies:[],bodyCaptures:[],responseHeaders:[],trace:[],traceClock:'Node process.hrtime.bigint relative nanoseconds',responseFinishedObservations:[],
  beforeCloseNetworkCompletionWait:false,responseCaptureDrainBeforeCloseLimitMs:500,responseFinishedDrainAfterCloseLimitMs:2000};
result.netlog={requestedSizeMegabytes:16,finalReadLimitBytes:netlogReadLimit,captureMode:'default Strip private information; no capture-mode flag',normalBrowserCloseRequired:true,completeJson:false,fsynced:false,file:null,circularCaptureConfigured:true,historyCompleteProved:false,evictionStatus:'not determined from this format',errors:[]};
// Exact unchanged app's five client chunks. response.body gives decoded entity
// bytes; request.sizes reports encoded transfer size, not wire bytes/digest.
const assetPins=[{"path":"/_next/static/chunks/webpack-44d8aec3c26a0cdc.js","sha256":"d0a82fed8b37553509fe37aa7c8dfa791ba125f47b8a45899e0fd6a03936a339","bytes":3253},{"path":"/_next/static/chunks/4bd1b696-c7408084347438ae.js","sha256":"7d5ccf185a6f85ab38ce400a7f10aa0a3496eb4e9aee1e500a85e01c4222fcec","bytes":203721},{"path":"/_next/static/chunks/794-ceeb732a1a81bc27.js","sha256":"55e42a1727ceefd5974b3ba5d35ce152d56f1a46f73f038d82b7fe8c1fe7f8fc","bytes":241744},{"path":"/_next/static/chunks/main-app-3c5fdbb8b7eab329.js","sha256":"73b4610d4d390a6906eba5a2c3555671c08deae1a5c0f8eb30917a52a535b6c1","bytes":513},{"path":"/_next/static/chunks/app/client/page-b0c3fc49684db039.js","sha256":"a60609e1626ebb5728ce2a599b9bea3f28d2d779ff1ca0896cc9c97837f35587","bytes":511}];
function domReadiness({test,readyOnly=false}) {
  function props(node,keyName) {
    if(!node)return [];
    return Reflect.ownKeys(node).filter(k=>typeof k==='string'&&k.startsWith('__reactProps$')).map(key=>{
      const d=Object.getOwnPropertyDescriptor(node,key);
      const data=!!d&&Object.hasOwn(d,'value');
      const value=data?d.value:undefined;
      const p=value!==null&&(typeof value==='object'||typeof value==='function')?Object.getOwnPropertyDescriptor(value,keyName):undefined;
      return {key,ownData:data,propsType:typeof value,member:keyName,memberOwnData:!!p&&Object.hasOwn(p,'value'),memberType:p&&Object.hasOwn(p,'value')?typeof p.value:null};
    });
  }
  const button=document.querySelector('[data-testid="counter-increment"]');
  const counter=document.querySelector('[data-testid="counter-value"]');
  const form=document.querySelector('[data-testid="server-action"]');
  const buttonProps=props(button,'onClick'),formProps=props(form,'action');
  const clickable=buttonProps.length===1&&buttonProps[0].ownData&&buttonProps[0].memberOwnData&&buttonProps[0].memberType==='function';
  const actionable=formProps.length===1&&formProps[0].ownData&&formProps[0].memberOwnData&&formProps[0].memberType==='function';
  const ready=test==='client-counter'?clickable:actionable;
  if(readyOnly)return ready;
  return {ready,readyState:document.readyState,url:location.href,counterText:counter?.textContent??null,buttonPresent:!!button,buttonDisabled:button?.disabled??null,buttonProps,formPresent:!!form,formProps,handlerInvoked:false};
}
// Inert observer bookkeeping. Inlined unchanged into the standalone worker.
// Operations are supplied by the browser worker; importing this file runs none.
function createNetworkObserver({now,onCdp,onLimit,limits}) {
  const states=new WeakMap();
  const stats={events:0,payloadBytes:0,stopped:false,eventsAfterStop:0,overflow:null};
  for(const key of ['maxEvents','maxEventBytes','maxPayloadBytes'])
    if(!Number.isSafeInteger(limits[key])||limits[key]<1)throw new TypeError('Finite observer limit required');
  function state(request,data){
    if((typeof request!=='object'&&typeof request!=='function')||request===null)
      throw new TypeError('Real request object identity required');
    let value=states.get(request);
    if(!value){
      let resolveFailed;const failed=new Promise(resolve=>{resolveFailed=resolve;});
      value={data:{...data},failed,resolveFailed,terminal:null};states.set(request,value);
    }else if(value.data.requestId!==data.requestId)throw new Error('Request identity changed');
    return value;
  }
  function requestFailed(request,data,failure){
    const value=state(request,data);
    if(value.terminal===null){
      value.terminal={kind:'requestfailed',...value.data,failure,arrivalNs:now()};
      value.resolveFailed({kind:'requestfailed',terminal:value.terminal,underlyingPromiseHandled:true});
    }
    return value.terminal;
  }
  async function raceFailure(request,data,operation){
    const value=state(request,data);
    // Attach BOTH settlement handlers immediately. If the failed terminal wins,
    // later target-close rejection is consumed, not invented as a second error.
    const observed=Promise.resolve().then(operation).then(
      result=>({kind:'fulfilled',value:result,underlyingPromiseHandled:true}),
      error=>({kind:'rejected',error,underlyingPromiseHandled:true}));
    return Promise.race([observed,value.failed]);
  }
  function requireValue(outcome){
    if(outcome.kind==='fulfilled')return outcome.value;
    if(outcome.kind==='rejected')throw outcome.error;
    if(outcome.kind!=='requestfailed')throw new Error('Unknown observer outcome');
    const error=new Error(outcome.terminal.failure?.errorText??'Browser request failed');
    error.code='ERR_BROWSER_REQUEST_FAILED';error.observationSource='Playwright.requestfailed';
    error.requestFailedTerminal=outcome.terminal;throw error;
  }
  function cdp(event,payload,context){
    if(stats.stopped){stats.eventsAfterStop++;return;}
    let text,bytes;
    try{text=JSON.stringify(payload);if(typeof text!=='string')throw new TypeError('CDP JSON payload required');bytes=Buffer.byteLength(text,'utf8');}
    catch(error){return stop('payload-serialization',{event,message:String(error)});}
    if(stats.events>=limits.maxEvents||bytes>limits.maxEventBytes||stats.payloadBytes+bytes>limits.maxPayloadBytes)
      return stop('bounded-cdp-limit',{event,nextPayloadBytes:bytes,eventsRetained:stats.events,payloadBytesRetained:stats.payloadBytes,limits});
    stats.events++;stats.payloadBytes+=bytes;
    // CDP supplies JSON. Retain every field, including unknown future fields;
    // this is semantic JSON data, not a claim to original transport wire bytes.
    onCdp({sequence:stats.events,...context,event,arrivalNs:now(),payloadBytes:bytes,payload:JSON.parse(text)});
  }
  function stop(reason,detail){
    if(stats.stopped)return;
    stats.stopped=true;stats.overflow={reason,...detail,arrivalNs:now()};
    const error=new Error('CDP observation stopped: '+reason);error.code='ERR_BROWSER_CDP_OBSERVER_LIMIT';
    onLimit(error,stats.overflow);
  }
  return {noteRequest:state,requestFailed,raceFailure,requireValue,cdp,stats};
}

const traceStart=process.hrtime.bigint();let sequence=0;
function trace(test,phase,event,data={}){if(result.trace.length>=4000){if(!result.errors.some(x=>x.stage==='trace-limit'))result.errors.push({stage:'trace-limit',message:'4000 trace records exceeded'});return;}result.trace.push({sequence:++sequence,ns:(process.hrtime.bigint()-traceStart).toString(),test,phase,event,...data});}
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});
const errorData=e=>({name:typeof e?.name==='string'?e.name:'Error',message:typeof e?.message==='string'?e.message:String(e),stack:typeof e?.stack==='string'?e.stack:null});
let browser;
await save();
try{
  const fromTools=createRequire(join(tools,'package.json'));
  const packagePath=fromTools.resolve('playwright-core/package.json'),entry=fromTools.resolve('playwright-core');
  const physicalTools=await realpath(tools);
  for(const path of [packagePath,entry]){const rel=relative(physicalTools,await realpath(path));assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel),'Playwright must resolve inside explicit tools directory');}
  const pkg=JSON.parse(await readFile(packagePath,'utf8'));assert.equal(pkg.name,'playwright-core');assert.equal(pkg.version,'1.64.1');
  result.playwrightVersion=pkg.version;result.playwrightPackage=await descriptor(packagePath);result.playwrightEntry=await descriptor(entry);
  result.executable=await descriptor(chrome);result.executableSHA256=result.executable.sha256;
  result.executableHashScope='Selected Chrome executable only; not an entire application-bundle hash';await save();
  const module=await import(pathToFileURL(entry).href),chromium=module.chromium??module.default?.chromium;
  assert(chromium,'Actual Playwright Chromium API');
  browser=await chromium.launch({executablePath:chrome,headless:true,timeout:limit,args:['--log-net-log='+netlogPath,'--net-log-max-size-mb=16']});result.browserVersion=browser.version();assert.equal(result.browserVersion,'156.0.8078.81','Matched controls require the retained Chrome version');await save();
  async function test(id,body){
    const record={id,passed:false,timedOut:false,screenshot:null,error:null};const started=Date.now();
    let context,page,timer,phase='context-setup';const finishes=new Set(),ids=new WeakMap();let nextRequest=0;
    let rejectObserver;
    const observerFailed=new Promise((_,reject)=>{rejectObserver=reject;});void observerFailed.catch(()=>{});
    const observer=createNetworkObserver({now:()=>(process.hrtime.bigint()-traceStart).toString(),
      onCdp:event=>result.cdpEvents.push(event),
      onLimit:(error,overflow)=>{result.errors.push({stage:id+'-cdp-observer',...errorData(error),overflow});rejectObserver(error);},
      limits:{maxEvents:8000,maxEventBytes:262144,maxPayloadBytes:8388608}});
    record.cdpObserver=observer.stats;
    const mark=name=>{phase=name;trace(id,phase,'phase');};
    record.domSnapshots=[];
    const snapshot=async name=>{const value=await page.evaluate(domReadiness,{test:id});record.domSnapshots.push({name,phase,value});trace(id,phase,'dom-readiness',{name,...value});return value;};
    const requestId=request=>{if(!ids.has(request))ids.set(request,++nextRequest);return ids.get(request);};
    const requestData=request=>({requestId:requestId(request),url:request.url(),method:request.method(),resourceType:request.resourceType(),isNavigationRequest:request.isNavigationRequest(),redirectedFrom:request.redirectedFrom()?requestId(request.redirectedFrom()):null});
    mark('context-setup');
    const pending=(async()=>{
      context=await browser.newContext({viewport:{width:1280,height:800},acceptDownloads:false});
      context.setDefaultTimeout(limit);context.setDefaultNavigationTimeout(limit);
      page=await context.newPage();
      page.on('request',request=>{const data=requestData(request);observer.noteRequest(request,data);trace(id,phase,'request',data);});
      page.on('requestfinished',request=>trace(id,phase,'requestfinished',requestData(request)));
      page.on('response',response=>{
        const request=response.request();trace(id,phase,'response',{...requestData(request),status:response.status(),statusText:response.statusText()});
        const pending=(async()=>{
          const data=requestData(request),path=new URL(data.url).pathname,pin=assetPins.find(x=>x.path===path);
          try{const headers=observer.requireValue(await observer.raceFailure(request,data,()=>response.headersArray()));const observation={test:id,phase,...data,status:response.status(),headers};result.responseHeaders.push(observation);trace(id,phase,'response-headers',observation);}catch(error){result.errors.push({stage:id+'-response-headers',requestId:requestId(request),...errorData(error)});}
          const bodyTask=(pin||(id==='server-action'&&request.method()==='POST'))?(async()=>{
            const capture={test:id,...data,status:response.status(),decodedBody:null,encodedSizes:null,wireBodySha256:null,wireBodyCapture:'Playwright response.body is decoded; request.sizes supplies encoded byte count only'};
            result.bodyCaptures.push(capture);
            try{const bodyOutcome=await observer.raceFailure(request,data,()=>response.body());capture.bodyCompletion={kind:bodyOutcome.kind,requestFailedTerminal:bodyOutcome.terminal??null,underlyingPromiseHandled:bodyOutcome.underlyingPromiseHandled};const body=observer.requireValue(bodyOutcome);capture.decodedBytes=body.length;capture.decodedSha256=createHash('sha256').update(body).digest('hex');if(body.length>8*1024*1024)throw Error('Decoded diagnostic body exceeds8MiB');const name=id+'-r'+requestId(request)+'.body';await writeFile(join(output,name),body,{flag:'wx',mode:0o600});capture.decodedBody=await descriptor(join(output,name));if(pin){capture.expected=pin;capture.sourceMatch=body.length===pin.bytes&&capture.decodedSha256===pin.sha256;result.assetBodies.push(capture);if(!capture.sourceMatch||response.status()!==200)result.errors.push({stage:id+'-asset-body-mismatch',requestId:requestId(request),path,expected:pin,actual:{bytes:body.length,sha256:capture.decodedSha256},status:response.status()});}trace(id,phase,'response-body-captured',capture);}catch(error){capture.bodyError=errorData(error);trace(id,phase,'response-body-unavailable',capture);result.errors.push({stage:id+'-response-body',requestId:requestId(request),...errorData(error)});}
            try{const sizesOutcome=await observer.raceFailure(request,data,()=>request.sizes());capture.sizesCompletion={kind:sizesOutcome.kind,requestFailedTerminal:sizesOutcome.terminal??null,underlyingPromiseHandled:sizesOutcome.underlyingPromiseHandled};capture.encodedSizes=observer.requireValue(sizesOutcome);trace(id,phase,'request-sizes',{...data,sizes:capture.encodedSizes});}catch(error){capture.sizesError=errorData(error);result.errors.push({stage:id+'-request-sizes',requestId:requestId(request),...errorData(error)});}
          })():Promise.resolve();
          try{
            const completion=await observer.raceFailure(request,data,()=>response.finished());
            const failure=completion.kind==='requestfailed'?{name:'RequestFailed',message:completion.terminal.failure?.errorText??'Browser request failed',stack:null,source:'Playwright.requestfailed'}:
              completion.kind==='rejected'?errorData(completion.error):completion.value?errorData(completion.value):null;
            const observation={...data,status:response.status(),completion:completion.kind,error:failure,requestFailedTerminal:completion.terminal??null,underlyingPromiseHandled:completion.underlyingPromiseHandled};
            result.responseFinishedObservations.push({test:id,phase,...observation});trace(id,phase,'response.finished',observation);
            if(failure)result.errors.push({stage:id+'-response-finished',requestId:requestId(request),...failure});
          }catch(error){trace(id,phase,'response.finished-rejected',{...data,error:errorData(error)});result.errors.push({stage:id+'-response-finished-rejected',requestId:requestId(request),...errorData(error)});}
          await bodyTask;
        })();
        finishes.add(pending);void pending.then(()=>finishes.delete(pending),error=>{finishes.delete(pending);result.errors.push({stage:id+'-response-observer',...errorData(error)});});
      });
      page.on('framenavigated',frame=>{if(frame===page.mainFrame())trace(id,phase,'main-frame-navigated',{url:frame.url()});});
      page.on('domcontentloaded',()=>trace(id,phase,'domcontentloaded',{url:page.url()}));
      page.on('load',()=>trace(id,phase,'load',{url:page.url()}));
      page.on('close',()=>trace(id,phase,'page-close'));
      page.on('crash',()=>trace(id,phase,'page-crash'));
      page.on('pageerror',error=>result.pageerrors.push({test:id,...errorData(error)}));
      page.on('console',message=>{if(message.type()==='error')result.consoleerrors.push({test:id,text:message.text(),location:message.location()});});
      page.on('requestfailed',request=>{const data=requestData(request),terminal=observer.requestFailed(request,data,request.failure());const failure={test:id,...data,failure:terminal.failure,phase,ns:terminal.arrivalNs};result.failedrequests.push(failure);trace(id,phase,'requestfailed',failure);});
      if(id==='server-action')page.on('request',request=>{if(request.method()==='POST'){const bytes=request.postDataBuffer();result.actionPosts.push({url:request.url(),headers:request.headers(),bodyBase64:bytes?.toString('base64')??null,bytes:bytes?.length??null});}});
      mark('cdp-observer-setup');
      const cdp=await context.newCDPSession(page);
      for(const event of result.cdpScope.events)cdp.on(event,payload=>observer.cdp(event,payload,{test:id,phase}));
      cdp.on('close',()=>trace(id,phase,'cdp-session-close'));
      await cdp.send('Network.enable');await cdp.send('Page.enable');
      record.cdpEnabledBeforeFirstAppRequest=true;trace(id,phase,'cdp-enabled',{domains:['Network','Page'],interception:false});
      const observations=await body(page,mark,snapshot);mark('functional-complete');
      mark('screenshot-start');const screenshot=join(output,id+'.png');await page.screenshot({path:screenshot,fullPage:true,timeout:5000});mark('screenshot-complete');
      record.screenshot=await descriptor(screenshot);record.observations=observations;
      // Bounded diagnostic capture drain, still INSIDE the original whole20s
      // deadline. It does not filter failed requests or require network-idle.
      mark('capture-drain-before-close');let captureTimer;
      try{record.captureDrainBeforeCloseComplete=await Promise.race([Promise.allSettled([...finishes]).then(()=>true),new Promise(resolve=>{captureTimer=setTimeout(()=>resolve(false),500);})]);}finally{clearTimeout(captureTimer);}
    })();
    try{
      await Promise.race([pending,observerFailed,new Promise((_,reject)=>{timer=setTimeout(()=>{record.timedOut=true;reject(new Error('Whole browser test exceeded20000ms'));},limit);})]);
      record.passed=true;
    }catch(error){
      record.error=errorData(error);
      if(page){let snapshotTimer;try{await Promise.race([snapshot('failure'),new Promise((_,reject)=>{snapshotTimer=setTimeout(()=>reject(Error('Failure DOM snapshot exceeded500ms')),500);})]);}catch(snapshotError){record.failureSnapshotError=errorData(snapshotError);}finally{clearTimeout(snapshotTimer);}}
    }
    finally{
      clearTimeout(timer);
      mark('context-close-start');if(context)try{await context.close();}catch(error){result.errors.push({stage:id+'-context-close',...errorData(error)});}mark('context-close-end');
      // Observe response.finished, but do not alter the original pre-close wait.
      mark('response-finished-drain-after-close');let drainTimer;
      try{const settled=await Promise.race([Promise.allSettled([...finishes]).then(()=>true),new Promise(resolve=>{drainTimer=setTimeout(()=>resolve(false),2000);})]);if(!settled)result.errors.push({stage:id+'-response-finished-drain',message:'Response completion observations did not settle within2000ms after context close'});}finally{clearTimeout(drainTimer);}
      mark('test-terminal');
      // Closing the ephemeral context cancels pending browser operations after a
      // whole-test timeout. The race already observes their eventual rejection.
      record.elapsedMs=Date.now()-started;result.tests.push(record);await save();
    }
  }
  await test('client-counter',async (page,mark,snapshot)=>{
    mark('client-goto');
    const response=await page.goto(new URL('/client',origin).href,{waitUntil:'domcontentloaded'});assert.equal(response?.status(),200);
    const value=page.getByTestId('counter-value');assert.equal(await value.textContent(),'NEXT_CLIENT_COUNT:0');
    await snapshot('after-domcontentloaded');
    mark('client-load-wait');await page.waitForLoadState('load',{timeout:limit});await snapshot('after-load');
    mark('client-hydration-wait');await(await page.waitForFunction(domReadiness,{test:'client-counter',readyOnly:true},{timeout:limit})).dispose();
    const beforeClick=await snapshot('before-click');assert.equal(beforeClick.ready,true);assert.equal(beforeClick.counterText,'NEXT_CLIENT_COUNT:0');
    mark('client-click');await page.getByTestId('counter-increment').click();mark('client-result-assert');
    await page.waitForFunction(()=>document.querySelector('[data-testid="counter-value"]')?.textContent==='NEXT_CLIENT_COUNT:1',undefined,{timeout:limit});
    assert.equal(await value.textContent(),'NEXT_CLIENT_COUNT:1');
    return{initial:'NEXT_CLIENT_COUNT:0',afterClick:await value.textContent(),url:page.url(),hydratedClickObserved:true,readiness:beforeClick};
  });
  await test('server-action',async (page,mark,snapshot)=>{
    mark('action-goto');
    const response=await page.goto(new URL('/actions',origin).href,{waitUntil:'domcontentloaded'});assert.equal(response?.status(),200);
    await snapshot('after-domcontentloaded');
    mark('action-load-wait');await page.waitForLoadState('load',{timeout:limit});await snapshot('after-load');
    mark('action-hydration-wait');await(await page.waitForFunction(domReadiness,{test:'server-action',readyOnly:true},{timeout:limit})).dispose();
    const beforeAction=await snapshot('before-action');assert.equal(beforeAction.ready,true);
    mark('action-fill');const form=page.getByTestId('server-action');await form.locator('input[name="value"]').fill('browser-action');
    const hiddenInputNames=await form.locator('input[type="hidden"]').evaluateAll(nodes=>nodes.map(node=>node.name));
    mark('action-submit-and-navigation');await Promise.all([
      page.waitForURL(url=>url.pathname==='/action-result'&&url.searchParams.get('value')==='browser-action',{waitUntil:'domcontentloaded',timeout:limit}),
      form.locator('button[type="submit"]').click(),
    ]);
    mark('action-result-assert');await page.waitForFunction(()=>document.querySelector('[data-testid="action-result"]')?.textContent==='browser-action',undefined,{timeout:limit});
    assert((await page.locator('body').textContent()).includes('NEXT_ACTION_RESULT'));
    assert(result.actionPosts.some(request=>new URL(request.url).origin===origin.origin),'Actual form POST must be observed');
    return{url:page.url(),marker:'NEXT_ACTION_RESULT',value:await page.getByTestId('action-result').textContent(),hiddenInputNames,builtActionIdNotHardcoded:true,actualFormPostObserved:true,readiness:beforeAction};
  });
}catch(error){result.errors.push({stage:'browser-setup-or-suite',...errorData(error)});}
finally{
  if(browser)try{await browser.close();result.browserClosed=!browser.isConnected();}catch(error){result.errors.push({stage:'browser-close',...errorData(error)});}
  // NetLog is finalized only after the unchanged normal browser close. The
  // requested circular16MiB cap can omit earlier events; complete JSON is not
  // proof of a complete event history. Never truncate, repair or regenerate it.
  if(result.browserClosed){
    let handle;
    try{
      const before=await lstat(netlogPath);
      assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1,'Regular unique NetLog required');
      assert(before.size>0&&before.size<=netlogReadLimit,'NetLog exceeds20MiB final-file bound');
      assert.equal(await realpath(netlogPath),netlogPath,'Canonical NetLog path');
      handle=await open(netlogPath,'r+');
      const opened=await handle.stat();assert(opened.dev===before.dev&&opened.ino===before.ino&&opened.size===before.size,'NetLog identity changed');
      await handle.chmod(0o600);await handle.sync();result.netlog.fsynced=true;
      const guarded=await handle.stat();
      assert(guarded.size>0&&guarded.size<=netlogReadLimit,'NetLog exceeds20MiB immediately before read');
      const bytes=await handle.readFile();
      assert.equal(bytes.length,guarded.size);
      const parsed=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      assert(parsed&&typeof parsed==='object'&&!Array.isArray(parsed)&&parsed.constants&&typeof parsed.constants==='object'&&!Array.isArray(parsed.constants)&&Array.isArray(parsed.events),'Complete NetLog constants/events JSON required');
      const after=await handle.stat(),pathAfter=await lstat(netlogPath);
      for(const key of ['dev','ino','size','mode','nlink','mtimeMs','ctimeMs'])assert.equal(after[key],guarded[key],'NetLog changed while reading');
      assert(pathAfter.dev===after.dev&&pathAfter.ino===after.ino&&pathAfter.size===after.size&&pathAfter.nlink===1&&!pathAfter.isSymbolicLink(),'NetLog path changed');
      result.netlog.completeJson=true;result.netlog.eventCount=parsed.events.length;
      result.netlog.file={path:netlogPath,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};
    }catch(error){const data={stage:'netlog-retention',...errorData(error)};result.netlog.errors.push(data);result.errors.push(data);}
    finally{if(handle)try{await handle.close();}catch(error){const data={stage:'netlog-close',...errorData(error)};result.netlog.errors.push(data);result.errors.push(data);}}
  }else{const data={stage:'netlog-retention',message:'Normal browser close not observed; no finalized NetLog claim'};result.netlog.errors.push(data);result.errors.push(data);}
  // URL/method matching supplies candidates only. Never merge protocol IDs,
  // redirects, clocks or arrival order into a causal request identity claim.
  for(const event of result.cdpEvents.filter(x=>x.event==='Network.requestWillBeSent')){
    const p=event.payload,candidates=result.trace.filter(x=>x.test===event.test&&x.event==='request'&&x.url===p.request?.url&&x.method===p.request?.method);
    result.cdpCorrelations.push({test:event.test,cdpRequestId:p.requestId,cdpSequence:event.sequence,cdpTimestamp:p.timestamp,cdpArrivalNs:event.arrivalNs,
      url:p.request?.url??null,method:p.request?.method??null,playwrightCandidates:candidates.map(x=>({requestId:x.requestId,arrivalNs:x.ns})),identityProved:false,policy:'URL/method candidates only; independent ID and clock namespaces'});
  }
  const counterAssets=result.assetBodies.filter(x=>x.test==='client-counter');
  result.assetCapturePassed=counterAssets.length===5&&assetPins.every(p=>counterAssets.filter(a=>new URL(a.url).pathname===p.path&&a.sourceMatch===true).length===1);
  if(!result.assetCapturePassed)result.errors.push({stage:'client-asset-capture',message:'All five exact decoded script bodies required'});
  result.functionalPassed=result.tests.length===2&&result.tests.every(t=>t.passed);
  result.browserErrorFree=result.pageerrors.length===0&&result.consoleerrors.length===0&&result.failedrequests.length===0;
  result.passed=result.functionalPassed&&result.browserErrorFree&&result.errors.length===0&&result.browserClosed;
  result.finished=new Date().toISOString();await save();
}
process.stdout.write(JSON.stringify({output,passed:result.passed,functionalPassed:result.functionalPassed,browserErrorFree:result.browserErrorFree,tests:result.tests.map(t=>({id:t.id,passed:t.passed,timedOut:t.timedOut})),errors:result.errors})+'\n');
if(!result.passed)process.exitCode=1;
