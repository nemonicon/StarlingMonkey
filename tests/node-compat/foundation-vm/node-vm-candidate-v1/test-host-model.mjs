// TEST ONLY Node VM provider. Never deployed or used as a guest/kernel fallback.
import assert from 'node:assert/strict';
import * as nodeVm from 'node:vm';
import {isProxy,isPromise} from 'node:util/types';
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createVmModule} from './after/builtins/node-compat/vm-data-factory.mjs';
assert.equal(process.version,'v22.14.0');
const own=fileURLToPath(new URL('.',import.meta.url));
const host='/private/tmp/starling-node-compat/next-http-bridge-module-v1/application';
const original='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/application/.next/standalone';
const hash=b=>createHash('sha256').update(b).digest('hex');
const descriptor=(path,b)=>({path,sha256:hash(b),bytes:b.length});
const failure=(message,code='ERR_SM_NODE_VM_UNSUPPORTED')=>Object.assign(new TypeError(message),{code});
function copier(prototypes){
  const seen=new Map(),active=new Set();let nodes=0,properties=0,bytes=0;
  return function copy(value,depth=0){
    if(depth>48)throw failure('depth','ERR_SM_NODE_VM_LIMIT');
    if(value===undefined||value===null||typeof value==='boolean')return value;
    if(typeof value==='number'){if(!Number.isFinite(value))throw failure('nonfinite');return value;}
    if(typeof value==='string'){bytes+=Buffer.byteLength(value);if(bytes>16777216)throw failure('bytes','ERR_SM_NODE_VM_LIMIT');return value;}
    if(typeof value!=='object'||isProxy(value))throw failure('functions/proxies/exotics');
    if(active.has(value))throw failure('cycle');if(seen.has(value))return seen.get(value);
    const proto=Object.getPrototypeOf(value),array=Array.isArray(value);
    if(proto!==null&&!prototypes.has(proto))throw failure('prototype');
    if(++nodes>8192)throw failure('nodes','ERR_SM_NODE_VM_LIMIT');
    if(array&&(value.length>131072||!Object.getOwnPropertyDescriptor(value,'length').writable))throw failure('array');
    const result=array?new Array(value.length):Object.create(proto===null?null:Object.prototype);
    seen.set(value,result);active.add(value);
    for(const key of Reflect.ownKeys(value)){
      if(array&&key==='length')continue;
      if(typeof key!=='string')throw failure('symbol key');
      bytes+=Buffer.byteLength(key);if(bytes>16777216||++properties>32768)throw failure('budget','ERR_SM_NODE_VM_LIMIT');
      const d=Object.getOwnPropertyDescriptor(value,key);
      if(!Object.hasOwn(d,'value')||!d.writable||!d.enumerable||!d.configurable)throw failure('descriptor');
      Object.defineProperty(result,key,{value:copy(d.value,depth+1),enumerable:true,writable:true,configurable:true});
    }
    active.delete(value);return result;
  };
}
function options(value){
  if(value===undefined)return {filename:'<node:vm>',timeout:1000};
  if(typeof value==='string')return {filename:value,timeout:1000};
  if(!value||typeof value!=='object'||isProxy(value)||![null,Object.prototype].includes(Object.getPrototypeOf(value)))throw failure('options');
  for(const key of Reflect.ownKeys(value))if(key!=='filename')throw failure('deferred option');
  const d=Object.getOwnPropertyDescriptor(value,'filename');
  if(d&&(!Object.hasOwn(d,'value')||typeof d.value!=='string'))throw failure('filename getter/type');
  return {filename:d?.value??'<node:vm>',timeout:1000};
}
let modelCalls=0;
const kernel={run(code,sandbox,opts){
  if(typeof code!=='string'||!sandbox||typeof sandbox!=='object'||Array.isArray(sandbox)||isProxy(sandbox)||!Object.isExtensible(sandbox))throw failure('arguments');
  const settings=options(opts);if(Buffer.byteLength(code)>1048576)throw failure('code','ERR_SM_NODE_VM_LIMIT');
  const input=copier(new Set([Object.prototype,Array.prototype]))(sandbox);modelCalls++;
  let value,threw=false;
  try{value=nodeVm.runInNewContext(code,input,settings);}catch(error){threw=true;value=error;}
  if(!threw&&isPromise(value)){threw=true;value=failure('async result','ERR_SM_NODE_VM_ASYNC');}
  let context,copyOutError,copyOutFailed=false;
  try{
    const proto=nodeVm.runInContext('Object.prototype',input,{timeout:1000});
    const arrayProto=nodeVm.runInContext('Array.prototype',input,{timeout:1000});
    const copy=copier(new Set([Object.prototype,Array.prototype,proto,arrayProto]));
    context=copy(input);if(!threw)value=copy(value);
  }catch(error){copyOutFailed=true;copyOutError=error;}
  return {threw,value,context,copyOutFailed,copyOutError};
}};
const graph=createVmModule(kernel),vm=graph.default;
let checks=0;const equal=(a,b)=>{assert.deepEqual(a,b);checks++;};
equal(Object.keys(graph).sort(),JSON.parse(await readFile(join(own,'node22-surface.json'),'utf8')).exports);
for(const name of Object.keys(vm)){equal(graph[name],vm[name]);}
equal(typeof vm.constants.DONT_CONTEXTIFY,'symbol');equal(typeof vm.constants.USE_MAIN_CONTEXT_DEFAULT_LOADER,'symbol');
equal(vm.runInNewContext('1+2'),3);
equal(Object.is(vm.runInNewContext('-0'),-0),true);
assert.throws(()=>vm.runInNewContext('1',vm.constants.DONT_CONTEXTIFY),e=>e.code==='ERR_SM_NODE_VM_UNSUPPORTED');checks++;
const context={process:{env:{NEXT_DEPLOYMENT_ID:undefined}}};
equal(vm.runInNewContext('globalThis.answer=42',context),42);equal(context.answer,42);
equal(Object.hasOwn(context.process.env,'NEXT_DEPLOYMENT_ID'),true);
const names={'*':1,'004':2,'/__path__[x]':3};equal(vm.runInNewContext('value', {value:names}),names);
const erased={gone:1};vm.runInNewContext('delete globalThis.gone; globalThis.newValue=0',erased);equal(erased,{newValue:0});
for(const thrown of ['undefined','null','false','0','Object.freeze({original:true})']){
  let caught=false;try{vm.runInNewContext(`globalThis.before=1;throw ${thrown}`,{});}catch(error){caught=true;if(thrown==='undefined')equal(error,undefined);}
  equal(caught,true);
}
let getterCalls=0;
for(const [code,sandbox,opts]of [['1',{get x(){getterCalls++;return 1;}},undefined],['1',{f(){}},undefined],
  ['1',{}, {get filename(){getterCalls++;return 'wrong';}}],['1',{}, {timeout:1}],['1',{}, {microtaskMode:'afterEvaluate'}],
  ['()=>1',{},undefined],['Promise.resolve(1)',{},undefined],['1',new Proxy({},{}),undefined]]){
  assert.throws(()=>vm.runInNewContext(code,sandbox,opts),error=>['ERR_SM_NODE_VM_UNSUPPORTED','ERR_SM_NODE_VM_ASYNC'].includes(error.code));checks++;
}
equal(getterCalls,0);
const cyclic={};cyclic.self=cyclic;assert.throws(()=>vm.runInNewContext('1',cyclic));checks++;
for(const name of ['Script','createContext','createScript','runInContext','runInThisContext','isContext','compileFunction','measureMemory']){
  assert.throws(()=>vm[name](),e=>e.code==='ERR_SM_NODE_VM_UNSUPPORTED');checks++;
}
const frozen=Object.freeze({original:true});
const failureVm=createVmModule({run:()=>({threw:true,value:frozen,copyOutFailed:true,copyOutError:new Error('copy failure')})}).default;
assert.throws(()=>failureVm.runInNewContext('x',{}),e=>e===frozen);checks++;

function typed(value){
  if(value===undefined)return {type:'undefined'};
  if(value===null)return {type:'null'};
  if(typeof value!=='object')return {type:typeof value,value};
  return {type:Array.isArray(value)?'array':'object',entries:Reflect.ownKeys(value).map(key=>[key,typed(Object.getOwnPropertyDescriptor(value,key).value)])};
}
async function walk(directory){let rows=[];for(const item of await readdir(directory,{withFileTypes:true})){
 const path=join(directory,item.name);if(item.isDirectory())rows.push(...await walk(path));
 else if(item.name.endsWith('_client-reference-manifest.js'))rows.push(path);
}return rows.sort();}
const manifests=[];
for(const path of await walk(join(host,'.next/server'))){
  const bytes=await readFile(path),source=bytes.toString('utf8'),rel=relative(host,path),originalPath=join(original,rel);
  equal(hash(await readFile(originalPath)),hash(bytes));
  const expected={process:{env:{NEXT_DEPLOYMENT_ID:undefined}}},actual={process:{env:{NEXT_DEPLOYMENT_ID:undefined}}};
  const returned=nodeVm.runInNewContext(source,expected,{timeout:1000});
  const modeled=vm.runInNewContext(source,actual);
  equal(typed(actual),typed(expected));equal(typed(modeled),typed(returned));
  const route=Object.keys(expected.__RSC_MANIFEST)[0];
  assert.equal(returned,expected.__RSC_MANIFEST[route]);checks++;
  assert.equal(modeled,actual.__RSC_MANIFEST[route]);checks++;
  equal(Object.hasOwn(actual.process.env,'NEXT_DEPLOYMENT_ID'),true);
  const json=JSON.stringify({context:typed(expected),completion:typed(returned)});
  const target=join(own,'manifest-oracles',rel.slice('.next/server/'.length)+'.json');
  await mkdir(fileURLToPath(new URL('.',new URL('file://'+target))),{recursive:true});
  await writeFile(target,json+'\n');
  manifests.push({source:descriptor(path,bytes),original:descriptor(originalPath,bytes),
    oracle:{path:relative(own,target),sha256:hash(Buffer.from(json+'\n')),bytes:Buffer.byteLength(json+'\n')},
    routes:Object.keys(expected.__RSC_MANIFEST),wholeDataMatch:true,nativeVmProved:false});
}
equal(manifests.length,19);
const result={schemaVersion:1,state:'NODE_VM_REAL_MANIFEST_AND_DATA_FACADE_MODEL_CHECKS_PASSED',node:process.version,
  checks,modelCalls,manifests,totalManifestSourceBytes:manifests.reduce((n,r)=>n+r.source.bytes,0),
  actualHostNodeVmUsed:true,hostWatchdogMilliseconds:1000,hostWatchdogIsNativeProfileTimeout:false,
  currentInputEqualityIsHistoricalExecutedByteAttestation:false,nativeKernelInvoked:false,
  discardedAsyncPromiseDetectionOnlySourceInspectedNotHostModelProved:true,
  guestEngineCompilerOrAppServerInvoked:false};
await writeFile(join(own,'host-model-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:result.state,checks,manifests:manifests.length,bytes:result.totalManifestSourceBytes,nativeKernelInvoked:false}));
