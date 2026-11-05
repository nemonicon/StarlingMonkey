// Pure environment/formatter and source-control-flow DATA only. No worker call.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {measurementEnvironmentModel} from './environment.mjs';
import {BOOTSTRAP_STAGES,bootstrapFailureLine} from './worker.mjs';
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
let checks=0;const notes=[];
const check=(name,fn)=>{fn();checks++;notes.push(name);};
const clone=()=>({...MEASUREMENT_ENV});
const cf=uid=>'0x'+uid.toString(16).toUpperCase()+':0x0:0x0';
const accepts=(name,value,facts)=>check(name,()=>{const before=JSON.stringify(value);assert.equal(measurementEnvironmentModel(value,facts),true);assert.equal(JSON.stringify(value),before);});
const rejects=(name,value,facts)=>check(name,()=>{const before=Object.getOwnPropertyDescriptors(value);assert.throws(()=>measurementEnvironmentModel(value,facts));assert.deepEqual(Object.getOwnPropertyDescriptors(value),before);});
accepts('exact eight on Darwin',clone(),{platform:'darwin',uid:501});
accepts('exact eight on other platform',clone(),{platform:'linux',uid:501});
for(const uid of [0,501,0xffffffff])accepts('sole exact CF uid '+uid,{...clone(),__CF_USER_TEXT_ENCODING:cf(uid)},{platform:'darwin',uid});
for(const name of Object.keys(MEASUREMENT_ENV)){
 const missing=clone();delete missing[name];rejects('missing '+name,missing,{platform:'darwin',uid:501});
 rejects('changed '+name,{...clone(),[name]:'changed'}, {platform:'darwin',uid:501});
}
for(const name of ['NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH','RUST_LOG','RUST_BACKTRACE','WASMTIME_FUEL','NAPI_RS_FORCE_WASI','PYTHONPATH','UNKNOWN'])rejects('extra '+name,{...clone(),[name]:'1'},{platform:'darwin',uid:501});
for(const platform of ['linux','win32','unknown'])rejects('CF on '+platform,{...clone(),__CF_USER_TEXT_ENCODING:cf(501)},{platform,uid:501});
for(const uid of [-1,0x100000000,NaN,Infinity,undefined,null,'501',1.5])rejects('invalid uid '+String(uid),{...clone(),__CF_USER_TEXT_ENCODING:cf(501)},{platform:'darwin',uid});
for(const value of ['0x1f5:0x0:0x0','0x1F4:0x0:0x0','0x1F5:0x1:0x0','0x1F5:0x0:0x1','0X1F5:0x0:0x0','0x01F5:0x0:0x0','0x1F5:0x0:0x0\n'])rejects('wrong CF spelling '+JSON.stringify(value),{...clone(),__CF_USER_TEXT_ENCODING:value},{platform:'darwin',uid:501});
let getterReads=0;const getterMap=clone();Object.defineProperty(getterMap,'PATH',{get(){getterReads++;throw Error('must not read accessor');},enumerable:true});
rejects('reject accessor before read',getterMap,{platform:'darwin',uid:501});check('zero environment getter reads',()=>assert.equal(getterReads,0));
rejects('symbol key refuses',{...clone(),[Symbol('key')]:'1'},{platform:'darwin',uid:501});
rejects('null prototype refuses',Object.assign(Object.create(null),clone()),{platform:'darwin',uid:501});
let errorReads=0;const malicious=new Proxy({}, {get(){errorReads++;throw Error('error getter read');},ownKeys(){errorReads++;throw Error('error enumeration');},getPrototypeOf(){errorReads++;throw Error('prototype read');}});
for(const error of [malicious,undefined,null,true,0,NaN,1n,Symbol('opaque'),'not retained '.repeat(10000),()=>{}]){
 check('safe formatter typeof '+typeof error,()=>{const line=bootstrapFailureLine('execution-environment',true,error),r=JSON.parse(line);assert(Buffer.byteLength(line)<=2048);assert.equal(r.thrownType,typeof error);assert.equal(r.exceptionPropertiesRead,false);assert.equal(r.fullExceptionValueCaptured,false);assert.equal(r.uniqueFailureCauseProven,false);assert(!line.includes('not retained'));});
}
check('zero caught error property accesses',()=>assert.equal(errorReads,0));
for(const stage of BOOTSTRAP_STAGES)check('fixed label '+stage,()=>{const r=JSON.parse(bootstrapFailureLine(stage,false,malicious));assert.equal(r.stage,stage);assert.equal(r.sourceAuthenticated,false);});
check('unknown diagnostic label refuses',()=>assert.throws(()=>bootstrapFailureLine('arbitrary input',true,malicious)));
check('invalid diagnostic flag refuses',()=>assert.throws(()=>bootstrapFailureLine('body-entry',{},malicious)));
const body=await readFile(new URL('./worker-body.mjs',import.meta.url),'utf8'),worker=await readFile(new URL('./worker.mjs',import.meta.url),'utf8');
check('source families before body import',()=>assert(worker.indexOf('await captureSourceFamilies(')<worker.indexOf("await import('./worker-body.mjs')")));
check('stage retained through successful failure audit',()=>assert(worker.includes("if(!bodyFailed)markStage('wrapper-final-recheck')")));
check('failure audit still always executes',()=>assert(worker.includes('finally{try{await source.recheck();}catch(error)')));
check('stderr only diagnostics',()=>{assert(worker.includes('process.stderr.write(line'));assert(!worker.includes('error.message'));assert(!worker.includes('error.stack'));assert(!worker.includes('error.name'));});
check('actual validated environment in started record',()=>{assert(body.includes('observedEnvironment,platformFacts,environmentObservationScope:'));assert(body.indexOf('measurementEnvironmentModel(observedEnvironment')<body.indexOf("await output.write('started.json'"));});
check('no guest before started record',()=>assert(body.indexOf("await output.write('started.json'")<body.indexOf('session=await loadTimingSession(v.artifact)')));
check('full environment rechecked without mutation',()=>{assert(body.includes("same({...process.env},observedEnvironment)"));assert(!body.includes('delete process.env'));});
console.log(JSON.stringify({schemaVersion:1,state:'V4_ENVIRONMENT_AND_DIAGNOSTIC_PURE_SOURCE_CHECKS_PASSED',checks,notes,errorPropertyReads:errorReads,environmentGetterReads:getterReads,workerCalled:false,loaderCalled:false,guestOrCodecOrPreflightInvoked:false,stderrWasNotWrittenByTest:true,actualSourceRuntimeExecuted:false}));
