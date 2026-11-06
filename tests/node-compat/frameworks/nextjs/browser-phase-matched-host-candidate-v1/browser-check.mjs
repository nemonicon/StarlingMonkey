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
const result={schemaVersion:1,suite:'nextjs-instrumented-browser-phase-v1',origin:origin.origin,playwrightVersion:null,browserVersion:null,
  executable:null,tests:[],pageerrors:[],consoleerrors:[],failedrequests:[],actionPosts:[],errors:[],
  browserClosed:false,ephemeralContexts:true,userProfileUsed:false,perTestTimeoutMs:limit,wasmBrowserRun:false,
  trace:[],traceClock:'Node process.hrtime.bigint relative nanoseconds',responseFinishedObservations:[],
  beforeCloseNetworkCompletionWait:false,responseFinishedDrainAfterCloseLimitMs:2000};
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
        const pending=(async()=>{try{const error=await response.finished();const observation={...requestData(request),status:response.status(),error:error?errorData(error):null};result.responseFinishedObservations.push({test:id,phase,...observation});trace(id,phase,'response.finished',observation);if(error)result.errors.push({stage:id+'-response-finished',requestId:requestId(request),...errorData(error)});}catch(error){trace(id,phase,'response.finished-rejected',{...requestData(request),error:errorData(error)});result.errors.push({stage:id+'-response-finished-rejected',requestId:requestId(request),...errorData(error)});}})();
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
      const observations=await body(page,mark);mark('functional-complete');
      mark('screenshot-start');const screenshot=join(output,id+'.png');await page.screenshot({path:screenshot,fullPage:true,timeout:5000});mark('screenshot-complete');
      record.screenshot=await descriptor(screenshot);record.observations=observations;
    })();
    try{
      await Promise.race([pending,new Promise((_,reject)=>{timer=setTimeout(()=>{record.timedOut=true;reject(new Error('Whole browser test exceeded20000ms'));},limit);})]);
      record.passed=true;
    }catch(error){record.error=errorData(error);}
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
  await test('client-counter',async (page,mark)=>{
    mark('client-goto');
    const response=await page.goto(new URL('/client',origin).href,{waitUntil:'domcontentloaded'});assert.equal(response?.status(),200);
    const value=page.getByTestId('counter-value');assert.equal(await value.textContent(),'NEXT_CLIENT_COUNT:0');
    mark('client-click');await page.getByTestId('counter-increment').click();mark('client-result-assert');
    await page.waitForFunction(()=>document.querySelector('[data-testid="counter-value"]')?.textContent==='NEXT_CLIENT_COUNT:1',undefined,{timeout:limit});
    assert.equal(await value.textContent(),'NEXT_CLIENT_COUNT:1');
    return{initial:'NEXT_CLIENT_COUNT:0',afterClick:await value.textContent(),url:page.url(),hydratedClickObserved:true};
  });
  await test('server-action',async (page,mark)=>{
    mark('action-goto');
    const response=await page.goto(new URL('/actions',origin).href,{waitUntil:'domcontentloaded'});assert.equal(response?.status(),200);
    mark('action-fill');const form=page.getByTestId('server-action');await form.locator('input[name="value"]').fill('browser-action');
    const hiddenInputNames=await form.locator('input[type="hidden"]').evaluateAll(nodes=>nodes.map(node=>node.name));
    mark('action-submit-and-navigation');await Promise.all([
      page.waitForURL(url=>url.pathname==='/action-result'&&url.searchParams.get('value')==='browser-action',{waitUntil:'domcontentloaded',timeout:limit}),
      form.locator('button[type="submit"]').click(),
    ]);
    mark('action-result-assert');await page.waitForFunction(()=>document.querySelector('[data-testid="action-result"]')?.textContent==='browser-action',undefined,{timeout:limit});
    assert((await page.locator('body').textContent()).includes('NEXT_ACTION_RESULT'));
    assert(result.actionPosts.some(request=>new URL(request.url).origin===origin.origin),'Actual form POST must be observed');
    return{url:page.url(),marker:'NEXT_ACTION_RESULT',value:await page.getByTestId('action-result').textContent(),hiddenInputNames,builtActionIdNotHardcoded:true,actualFormPostObserved:true};
  });
}catch(error){result.errors.push({stage:'browser-setup-or-suite',...errorData(error)});}
finally{
  if(browser)try{await browser.close();result.browserClosed=!browser.isConnected();}catch(error){result.errors.push({stage:'browser-close',...errorData(error)});}
  result.functionalPassed=result.tests.length===2&&result.tests.every(t=>t.passed);
  result.browserErrorFree=result.pageerrors.length===0&&result.consoleerrors.length===0&&result.failedrequests.length===0;
  result.passed=result.functionalPassed&&result.browserErrorFree&&result.errors.length===0&&result.browserClosed;
  result.finished=new Date().toISOString();await save();
}
process.stdout.write(JSON.stringify({output,passed:result.passed,functionalPassed:result.functionalPassed,browserErrorFree:result.browserErrorFree,tests:result.tests.map(t=>({id:t.id,passed:t.passed,timedOut:t.timedOut})),errors:result.errors})+'\n');
if(!result.passed)process.exitCode=1;
