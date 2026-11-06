// Real browser checks for the owned stock-Node Next fixture. No action at import
// is promised: this is a standalone worker, launched only by the experiment.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {mkdir,readFile,writeFile,realpath} from 'node:fs/promises';
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
async function descriptor(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
const result={schemaVersion:1,suite:'nextjs-hydration-browser-diagnostic-v1',origin:origin.origin,playwrightVersion:null,browserVersion:null,
  executable:null,tests:[],pageerrors:[],consoleerrors:[],failedrequests:[],actionPosts:[],errors:[],
  browserClosed:false,ephemeralContexts:true,userProfileUsed:false,perTestTimeoutMs:limit,wasmBrowserRun:null,targetRuntimeProvenance:'Parent Root records actual host; the browser origin alone does not identify it',
  assetBodies:[],bodyCaptures:[],responseHeaders:[],trace:[],traceClock:'Node process.hrtime.bigint relative nanoseconds',responseFinishedObservations:[],
  beforeCloseNetworkCompletionWait:false,responseCaptureDrainBeforeCloseLimitMs:500,responseFinishedDrainAfterCloseLimitMs:2000};
// Exact unchanged app's five client chunks. response.body gives decoded entity
// bytes; request.sizes reports encoded transfer size, not wire bytes/digest.
const assetPins=[{"path":"/_next/static/chunks/webpack-44d8aec3c26a0cdc.js","sha256":"d0a82fed8b37553509fe37aa7c8dfa791ba125f47b8a45899e0fd6a03936a339","bytes":3253},{"path":"/_next/static/chunks/4bd1b696-c7408084347438ae.js","sha256":"7d5ccf185a6f85ab38ce400a7f10aa0a3496eb4e9aee1e500a85e01c4222fcec","bytes":203721},{"path":"/_next/static/chunks/794-ceeb732a1a81bc27.js","sha256":"55e42a1727ceefd5974b3ba5d35ce152d56f1a46f73f038d82b7fe8c1fe7f8fc","bytes":241744},{"path":"/_next/static/chunks/main-app-fc59c260965b537c.js","sha256":"b61335053ada1875ed5fb424883dcf32ae3f74ec8fe4518192f468b417e573e4","bytes":513},{"path":"/_next/static/chunks/app/client/page-1d3eef49152dd249.js","sha256":"d5c7b30c2616f0723a93bb21393adaa437c53b37ba1cad669ea55b1250719fce","bytes":511}];
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
  browser=await chromium.launch({executablePath:chrome,headless:true,timeout:limit});result.browserVersion=browser.version();assert.equal(result.browserVersion,'156.0.8078.81','Matched controls require the retained Chrome version');await save();
  async function test(id,body){
    const record={id,passed:false,timedOut:false,screenshot:null,error:null};const started=Date.now();
    let context,page,timer,phase='context-setup';const finishes=new Set(),ids=new WeakMap();let nextRequest=0;
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
      page.on('request',request=>trace(id,phase,'request',requestData(request)));
      page.on('requestfinished',request=>trace(id,phase,'requestfinished',requestData(request)));
      page.on('response',response=>{
        const request=response.request();trace(id,phase,'response',{...requestData(request),status:response.status(),statusText:response.statusText()});
        const pending=(async()=>{
          const data=requestData(request),path=new URL(data.url).pathname,pin=assetPins.find(x=>x.path===path);
          try{const headers=await response.headersArray();const observation={test:id,phase,...data,status:response.status(),headers};result.responseHeaders.push(observation);trace(id,phase,'response-headers',observation);}catch(error){result.errors.push({stage:id+'-response-headers',requestId:requestId(request),...errorData(error)});}
          const bodyTask=(pin||(id==='server-action'&&request.method()==='POST'))?(async()=>{
            const capture={test:id,...data,status:response.status(),decodedBody:null,encodedSizes:null,wireBodySha256:null,wireBodyCapture:'Playwright response.body is decoded; request.sizes supplies encoded byte count only'};
            result.bodyCaptures.push(capture);
            try{const body=await response.body();capture.decodedBytes=body.length;capture.decodedSha256=createHash('sha256').update(body).digest('hex');if(body.length>8*1024*1024)throw Error('Decoded diagnostic body exceeds8MiB');const name=id+'-r'+requestId(request)+'.body';await writeFile(join(output,name),body,{flag:'wx',mode:0o600});capture.decodedBody=await descriptor(join(output,name));if(pin){capture.expected=pin;capture.sourceMatch=body.length===pin.bytes&&capture.decodedSha256===pin.sha256;result.assetBodies.push(capture);if(!capture.sourceMatch||response.status()!==200)result.errors.push({stage:id+'-asset-body-mismatch',requestId:requestId(request),path,expected:pin,actual:{bytes:body.length,sha256:capture.decodedSha256},status:response.status()});}trace(id,phase,'response-body-captured',capture);}catch(error){capture.bodyError=errorData(error);trace(id,phase,'response-body-unavailable',capture);result.errors.push({stage:id+'-response-body',requestId:requestId(request),...errorData(error)});}
            try{capture.encodedSizes=await request.sizes();trace(id,phase,'request-sizes',{...data,sizes:capture.encodedSizes});}catch(error){capture.sizesError=errorData(error);result.errors.push({stage:id+'-request-sizes',requestId:requestId(request),...errorData(error)});}
          })():Promise.resolve();
          try{const error=await response.finished();const observation={...data,status:response.status(),error:error?errorData(error):null};result.responseFinishedObservations.push({test:id,phase,...observation});trace(id,phase,'response.finished',observation);if(error)result.errors.push({stage:id+'-response-finished',requestId:requestId(request),...errorData(error)});}catch(error){trace(id,phase,'response.finished-rejected',{...data,error:errorData(error)});result.errors.push({stage:id+'-response-finished-rejected',requestId:requestId(request),...errorData(error)});}
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
      page.on('requestfailed',request=>{const failure={test:id,...requestData(request),failure:request.failure(),phase,ns:(process.hrtime.bigint()-traceStart).toString()};result.failedrequests.push(failure);trace(id,phase,'requestfailed',failure);});
      if(id==='server-action')page.on('request',request=>{if(request.method()==='POST'){const bytes=request.postDataBuffer();result.actionPosts.push({url:request.url(),headers:request.headers(),bodyBase64:bytes?.toString('base64')??null,bytes:bytes?.length??null});}});
      const observations=await body(page,mark,snapshot);mark('functional-complete');
      mark('screenshot-start');const screenshot=join(output,id+'.png');await page.screenshot({path:screenshot,fullPage:true,timeout:5000});mark('screenshot-complete');
      record.screenshot=await descriptor(screenshot);record.observations=observations;
      // Bounded diagnostic capture drain, still INSIDE the original whole20s
      // deadline. It does not filter failed requests or require network-idle.
      mark('capture-drain-before-close');let captureTimer;
      try{record.captureDrainBeforeCloseComplete=await Promise.race([Promise.allSettled([...finishes]).then(()=>true),new Promise(resolve=>{captureTimer=setTimeout(()=>resolve(false),500);})]);}finally{clearTimeout(captureTimer);}
    })();
    try{
      await Promise.race([pending,new Promise((_,reject)=>{timer=setTimeout(()=>{record.timedOut=true;reject(new Error('Whole browser test exceeded20000ms'));},limit);})]);
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
