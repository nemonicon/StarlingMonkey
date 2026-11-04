// Host ESM/exact generated strict-factory semantics, not a native engine gate.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {runInThisContext} from 'node:vm';
import * as kernel from '../../../../docs/node-compat/templates/reference-kernel.mjs';
import {allocationChecks} from '../checks.mjs';
import {allocationProfile,stubPoisonChecks} from '../installed/checks.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),hash=value=>createHash('sha256').update(value).digest('hex');
const receipt=JSON.parse(await readFile(join(here,'source-receipt.json'))),oracle=JSON.parse(await readFile(join(here,'../node-results.json')));
const OriginalError=Error,Apply=Reflect.apply,Define=Object.defineProperty,Descriptor=Object.getOwnPropertyDescriptor,Keys=Reflect.ownKeys;
const shape=value=>Keys(value).map(key=>{const d=Descriptor(value,key);return{key:String(key),type:typeof d.value,get:typeof d.get,set:typeof d.set,writable:d.writable,enumerable:d.enumerable,configurable:d.configurable};});
for(const file of receipt.files)for(const variant of ['ancestry','baseline','candidate'])assert.equal(hash(await readFile(join(here,variant,file.path))),file[variant]);
async function load(variant,generated){
  const root=join(here,variant,'builtins/node-compat');
  if(!generated){const facade=await import(pathToFileURL(join(root,'buffer-facade.mjs')));return{buffer:facade.createBufferModule(kernel),child:await import(pathToFileURL(join(root,'child-process.mjs')))};}
  const header=await readFile(join(root,'factories.generated.h'),'utf8');
  const factory=name=>{const source=new RegExp('static constexpr const char '+name+'\\[\\] = R"SM_NODE_PROFILE\\(([\\s\\S]*?)\\)SM_NODE_PROFILE";').exec(header)?.[1];assert(source);return runInThisContext('"use strict";\n'+source);};
  return{buffer:factory('kBufferFactorySource')(kernel),child:factory('kChildProcessFactorySource')()};
}
function mutationCases(B,variant){
  const observed=[];
  for(const name of ['isInteger','isFinite'])for(const behavior of ['throw-sentinel','return-false','return-true']){
    const old=Descriptor(Number,name),sentinel=new OriginalError('Ordinary pure JS mutable '+name+' hook');let calls=0,value,error;
    try{
      Define(Number,name,{...old,value(){calls++;if(behavior==='throw-sentinel')throw sentinel;return behavior==='return-true';}});
      // No assertions/native codecs/await while the numeric hook is changed.
      try{value=B.allocUnsafe(3.75);}catch(caught){error=caught;}
    }finally{Define(Number,name,old);}
    const row={name,behavior,hookCalls:calls};
    if(variant==='candidate'){
      assert.equal(calls,0);assert.equal(error,undefined);assert.equal(value.length,3);assert(B.isBuffer(value));assert.deepEqual([...value],[0,0,0]);row.result='zeroed-length-3';
    }else{
      assert.equal(calls,1);
      if(behavior==='throw-sentinel'){assert.equal(error,sentinel);row.result='same-sentinel';}
      else if(behavior==='return-false'){
        assert(error);assert.equal(error.code,name==='isInteger'?'ERR_SM_NODE_UNSUPPORTED':'ERR_OUT_OF_RANGE');
        if(name==='isInteger'){assert.equal(error.operation,'fractional size');assert.equal(error.profile,'sm-node-22.14.0-m0.11');}
        row.result={name:error.name,code:error.code,operation:error.operation??null,profile:error.profile??null};
      }else{assert.equal(error,undefined);assert.equal(value.length,3);row.result='zeroed-length-3';}
    }
    observed.push(row);
  }return observed;
}
const variants=[];let commonShape;
for(const generated of[false,true])for(const variant of['baseline','candidate']){
  // Web constructors/factory creation occur before all scoped poison checks.
  const{buffer,child}=await load(variant,generated),B=buffer.Buffer;
  const manifest=JSON.parse(await readFile(join(here,variant,'builtins/node-compat/export-manifest.node-v22.14.0.json')));
  const contract={coreVersion:manifest.profileVersion,unsupportedStatic:manifest.modules['node:buffer'].unsupportedStatic,
    importOnlyExports:manifest.modules['node:buffer'].importOnlyExports,childExports:manifest.modules['node:child_process'].exports.filter(name=>name!=='default')};
  assert.equal(contract.coreVersion,'sm-node-22.14.0-m0.11');
  assert.deepEqual(allocationChecks(B,B.allocUnsafe),oracle.cases);
  const profile=allocationProfile(B);assert.equal(profile.length,5);
  const poison=stubPoisonChecks(buffer,child,contract);assert.equal(poison.operations,240);
  const shapes={module:shape(buffer),statics:shape(B),prototype:shape(B.prototype)};
  if(commonShape)assert.deepEqual(shapes,commonShape);else commonShape=shapes;
  assert(Object.isFrozen(buffer)&&Object.isFrozen(buffer.default)&&Object.isFrozen(buffer.constants));
  for(const name of Keys(buffer).filter(name=>name!=='default'))assert.equal(buffer[name],buffer.default[name]);
  const descriptor=Descriptor(B,Symbol.species);assert.equal(typeof descriptor.value,'function');assert.equal(descriptor.writable,false);assert.equal(descriptor.configurable,false);
  // Positive buffer species path remains the common existing implementation.
  const b=B.allocUnsafe(4),species=Reflect.construct(descriptor.value,[2]);assert(B.isBuffer(species));assert.equal(species.length,2);
  const mapped=Apply(Uint8Array.prototype.map,b,[(_,index)=>index+1]);assert(B.isBuffer(mapped));assert.deepEqual([...mapped],[1,2,3,4]);
  variants.push({variant,form:generated?'exact-generated-strict-factories':'actual-private-esm',differentialGroups:10,profile,refusals:poison,
    species:{arity:descriptor.value.length,writable:false,configurable:false,positiveBrand:true,mappedBrand:true},
    mutationCases:mutationCases(B,variant),defaultGraphAndDescriptorOrderPreserved:true});
}
const report={schema:1,state:'unapplied-private-source-host-semantics-passed',atUtc:new Date().toISOString(),node:process.version,
  profileVersion:receipt.profileVersion,ancestryEngineSha256:receipt.ancestryEngineSha256,sourceReceiptSha256:hash(await readFile(join(here,'source-receipt.json'))),
  testSha256:hash(await readFile(fileURLToPath(import.meta.url))),sharedCorpusSha256:{allocation:hash(await readFile(join(here,'../checks.mjs'))),installedPolicyAndPoison:hash(await readFile(join(here,'../installed/checks.mjs')))},variants,
  kernel:'Explicit host-only reference-kernel test double; allocator uses real host Uint8Array, kernel crypto/hex not involved',
  scope:'Four host forms: baseline/candidate ESM and exact generated strict script. No native engine/component, timing, OOM/fault/DEBUG or production edit.'};
await writeFile(join(here,'host-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,forms:variants.length,differentialGroupsPerForm:10,profileGroupsPerForm:5,pureJsRefusalsPerForm:240,mutationCasesPerForm:6,productionApplied:false}));
