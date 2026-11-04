// Valid build-host public/fake-signal checks only. No native event target proof.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const source=fileURLToPath(new URL('../source/builtins/node-compat/events-factories.generated.h',import.meta.url));
const header=await readFile(source,'utf8'),literal=header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";/)[1];
const factory=new vm.Script('"use strict";'+literal).runInThisContext(),key=Symbol('host-public-hook-test-only');
const events=factory(key),results=[];
function caught(fn){try{fn();}catch(error){return error;}assert.fail('Expected error');}
{
 const trace=[],listener=()=>{},signal={aborted:false,
  addEventListener(type,callback,options){trace.push(['add',this===signal,type,callback===listener,options.once,Object.getPrototypeOf(options)===null,Reflect.ownKeys(options).filter(k=>typeof k==='symbol')[0]===key]);},
  removeEventListener(type,callback){trace.push(['remove',this===signal,type,callback===listener]);}};
 const resource=events.addAbortListener(signal,listener),descriptor=Object.getOwnPropertyDescriptor(resource,Symbol.dispose);
 assert.equal(Object.getPrototypeOf(resource),null);assert.deepEqual(Reflect.ownKeys(resource),[Symbol.dispose]);
 assert.deepEqual([descriptor.enumerable,descriptor.writable,descriptor.configurable,descriptor.value.length,Object.hasOwn(descriptor.value,'prototype')],[true,true,true,0,false]);
 assert.equal(resource.then,undefined);resource[Symbol.dispose]();resource[Symbol.dispose]();
 assert.deepEqual(trace,[['add',true,'abort',true,true,true,true],['remove',true,'abort',true],['remove',true,'abort',true]]);
 results.push({name:'dynamic-public-hooks-resource-and-repeated-disposal',trace});
}
{
 const trace=[],signal={get aborted(){trace.push('aborted');return false;},addEventListener(){trace.push('add');}};
 assert.equal(caught(()=>events.addAbortListener(signal,undefined)).code,'ERR_INVALID_ARG_TYPE');assert.deepEqual(trace,[]);
 const sentinel={marker:1},proxy=new Proxy({}, {has(){throw sentinel;}});assert.equal(caught(()=>events.addAbortListener(proxy,()=>{})),sentinel);
 results.push({name:'structural-validation-before-aborted-getter-and-proxy-error',passed:true});
}
{
 let called=0,thenReads=0,receiver,args;
 const resource=events.addAbortListener({aborted:true},function(){called++;receiver=this;args=arguments.length;return{get then(){thenReads++;throw Error('Return value must be ignored');}};});
 resource[Symbol.dispose]();assert.equal(called,0);await Promise.resolve();
 assert.deepEqual([called,thenReads,receiver,args],[1,0,undefined,0]);
 results.push({name:'already-aborted-queue-disposal-and-return-value',called,thenReads,args,receiverUndefined:receiver===undefined});
}
{
 const SavedError=Error,SavedTypeError=TypeError,define=Object.defineProperty,remove=Reflect.deleteProperty;
 const keys=['code','module','operation','profile'];let hooks=0,wrongConstructors=0;const old=keys.map(key=>Object.getOwnPropertyDescriptor(Error.prototype,key));
 try{
  for(const key of keys)define(Error.prototype,key,{configurable:true,set(){hooks++;throw new SavedError('Inherited error hook');}});
  globalThis.Error=function(){wrongConstructors++;};globalThis.TypeError=function(){wrongConstructors++;};
  const unsupported=caught(()=>events.once()),invalid=caught(()=>events.addAbortListener(null,()=>{}));
  assert(unsupported instanceof SavedError);assert(invalid instanceof SavedTypeError);
  assert.equal(unsupported.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(invalid.code,'ERR_INVALID_ARG_TYPE');
  for(const error of [unsupported,invalid])for(const key of keys)assert(Object.hasOwn(error,key));
  assert.equal(hooks,0);assert.equal(wrongConstructors,0);
 }finally{
  globalThis.Error=SavedError;globalThis.TypeError=SavedTypeError;
  for(let i=0;i<keys.length;i++)if(old[i])define(SavedError.prototype,keys[i],old[i]);else remove(SavedError.prototype,keys[i]);
 }
 results.push({name:'captured-constructors-and-own-error-fields',hooks,wrongConstructors});
}
const report={state:'HOST_SOURCE_ONLY_NO_NATIVE_PROTECTION_OR_GUEST_PROOF',node:process.version,headerSha256:createHash('sha256').update(header).digest('hex'),driverSha256:createHash('sha256').update(await readFile(fileURLToPath(import.meta.url))).digest('hex'),results,passed:results.length};
await writeFile(new URL('./source-facade-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:results.length,state:report.state}));
