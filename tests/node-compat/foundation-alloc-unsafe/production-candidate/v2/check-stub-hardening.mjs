// Synchronous poison window: ONLY pure JS candidate refusal functions run.
// Never call Node's real child_process API, TextDecoder or native Node error
// oracles while inherited Error fields are poisoned.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {runInThisContext} from 'node:vm';
import * as kernel from '../../../../../docs/node-compat/templates/reference-kernel.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),root=join(here,'source/builtins/node-compat');
const hash=v=>createHash('sha256').update(v).digest('hex');
const ActualError=Error,Define=Object.defineProperty,Descriptor=Object.getOwnPropertyDescriptor;
const Keys=Reflect.ownKeys,Apply=Reflect.apply,Construct=Reflect.construct;
const manifest=JSON.parse(await readFile(join(root,'export-manifest.node-v22.14.0.json')));
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.8');
const sourceReceipt=JSON.parse(await readFile(join(here,'source-receipt.json')));
const header=await readFile(join(root,'factories.generated.h'),'utf8');
for(const item of sourceReceipt.changed){const name=item.path.slice('builtins/node-compat/'.length);assert.equal(hash(await readFile(join(root,name))),item.after);}
const variants=[];
for(const generated of [false,true]){
  // Factories/Node-backed web constructors run before any poison is installed.
  let buffer,child;
  if(generated){
    const factory=name=>{const body=new RegExp('static constexpr const char '+name+'\\[\\] = R"SM_NODE_PROFILE\\(([\\s\\S]*?)\\)SM_NODE_PROFILE";').exec(header)?.[1];assert(body);return runInThisContext('"use strict";\n'+body);};
    buffer=factory('kBufferFactorySource')(kernel);child=factory('kChildProcessFactorySource')();
  }else{
    const facade=await import(pathToFileURL(join(root,'buffer-facade.mjs')));buffer=facade.createBufferModule(kernel);
    child=await import(pathToFileURL(join(root,'child-process.mjs')));
  }
  const B=buffer.Buffer,receiver=B.alloc(1),operations=[];
  function entry(fn,module,operation,thisValue=undefined){for(const construct of [false,true])operations.push({fn,module,operation,thisValue,construct});}
  let prototypes=0;
  for(const name of Keys(B.prototype)){
    const d=Descriptor(B.prototype,name);
    if(typeof d.value!=='function'||['constructor','toString','slice','subarray'].includes(name))continue;
    const operation=typeof name==='symbol'?'Buffer.prototype[util.inspect.custom]':'Buffer.prototype.'+name;
    entry(d.value,'node:buffer',operation,receiver);prototypes++;
  }
  assert.equal(prototypes,91);
  for(const name of manifest.modules['node:buffer'].unsupportedStatic)entry(B[name],'node:buffer','Buffer.'+name);
  entry(B,'node:buffer','Buffer constructor');
  for(const name of manifest.modules['node:buffer'].importOnlyExports)entry(buffer[name],'node:buffer',name);
  for(const name of manifest.modules['node:child_process'].exports.filter(n=>n!=='default'))entry(child[name],'node:child_process',name);
  for(const name of ['spawn','kill','ref','unref'])entry(child.ChildProcess.prototype[name],'node:child_process','ChildProcess.prototype.'+name);
  entry(child.ChildProcess.prototype[Symbol.for('nodejs.dispose')],'node:child_process','ChildProcess.prototype[Symbol.dispose]');
  const originals=Object.fromEntries(['code','module','operation','profile'].map(name=>[name,Descriptor(ActualError.prototype,name)]));
  const previousError=globalThis.Error,previousDefine=Object.defineProperty;
  const sentinel=new ActualError('pure JS poison hook invoked');
  const counts={globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0};
  const caught=[];
  try{
    for(const field of ['code','module','operation','profile'])Define(ActualError.prototype,field,{
      get(){counts.inheritedGets++;throw sentinel;},set(){counts.inheritedSets++;throw sentinel;},configurable:true});
    globalThis.Error=function ReplacedError(){counts.globalError++;throw sentinel;};
    Object.defineProperty=function replacedDefineProperty(){counts.publicDefineProperty++;throw sentinel;};
    // No assertions, logging, await, native codecs or native operation oracle
    // is allowed in this window. Catch/store only, then restore all hooks.
    for(const operation of operations){let error,threw=false;
      try{if(operation.construct)Construct(operation.fn,[]);else Apply(operation.fn,operation.thisValue,[]);}
      catch(value){error=value;threw=true;}
      caught.push({operation,error,threw});
    }
  }finally{
    globalThis.Error=previousError;Object.defineProperty=previousDefine;
    for(const field of ['code','module','operation','profile']){
      if(originals[field])Define(ActualError.prototype,field,originals[field]);else delete ActualError.prototype[field];
    }
  }
  // All native assert/inspection work occurs after the poison is removed.
  assert.deepEqual(counts,{globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0});
  for(const{operation,error,threw}of caught){
    assert(threw);assert(error instanceof ActualError);assert.notEqual(error,sentinel);
    for(const[field,value]of Object.entries({code:'ERR_SM_NODE_UNSUPPORTED',module:operation.module,operation:operation.operation,profile:manifest.profileVersion}))
      assert.deepEqual(Descriptor(error,field),{value,writable:true,enumerable:true,configurable:true});
    assert.equal(error.message,operation.module+'.'+operation.operation+' is unavailable in '+manifest.profileVersion);
  }
  assert.equal(caught.length,240);
  for(const name of manifest.modules['node:child_process'].exports.filter(n=>n!=='default'))assert.equal(child[name],child.default[name]);
  assert.equal(child.then,undefined);assert.equal(child.default.then,undefined);assert.equal(buffer.then,undefined);assert.equal(buffer.default.then,undefined);
  variants.push({kind:generated?'exact-generated-strict-factories':'actual-candidate-esm',operations:caught.length,
    prototypeFunctions:prototypes,prototypeCallAndConstruct:182,finiteChildExports:9,counts,ownDataFields:['code','module','operation','profile'],
    defaultIdentityPreserved:true,identifiableErrorsPreserved:true,globalHooksRestored:true});
}
const report={schema:1,proposalVersion:'buffer-allocunsafe-zeroed-production-v2',profileVersion:manifest.profileVersion,installed:false,node:process.version,variants,
  headerSha256:hash(header),helperSha256:hash(await readFile(join(root,'unsupported.mjs'))),testSha256:hash(await readFile(fileURLToPath(import.meta.url))),
  scope:'Host ESM/strict generated-factory tests of pure JS candidate refusals only. No Node native codec/error oracle or child_process capability runs in the poison window; no native component, genuine OOM or engine hardening claim.',
  poisonPolicy:'Only synchronous pure JS stub/error constructors run while inherited fields/global Error/defineProperty are poisoned. Setup, web factory creation, inventory and assertions occur outside; all hooks restore in finally.'};
await writeFile(join(here,'stub-hardening-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({variants:variants.length,pureJsRefusalsPerVariant:240,prototypeFunctions:91,hookCalls:0,installed:false}));
