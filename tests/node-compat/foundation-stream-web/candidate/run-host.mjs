import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fixtureRecord} from './fixture-record.mjs';
import {createStreamWebModule} from './factory.mjs';
import {codecCases,cancellationCases,constructorCases} from './codec-cases.mjs';
import {guardCases} from './guard-cases.mjs';
import {policyCases,primordialCases} from './policy-cases.mjs';
import {typedViewCases} from './typed-view-cases.mjs';
import {controllerCases} from './controller-cases.mjs';
assert.equal(process.version,'v22.14.0');
const before={encoder:globalThis.TextEncoderStream,decoder:globalThis.TextDecoderStream};
const fixture=await fixtureRecord();let module,result;
try{
module=createStreamWebModule(fixture.record);
const node=JSON.parse(await readFile(new URL('./codec-node-results.json',import.meta.url)));
const actual={constructorCases:constructorCases(module),codecCases:await codecCases(module),cancellationCases:await cancellationCases(module)};
await writeFile(new URL('./codec-host-observations.json',import.meta.url),JSON.stringify(actual,null,2)+'\n');
for(const key of ['constructorCases','codecCases','cancellationCases'])assert.deepEqual(actual[key],node[key],key);
const nodeGuard=JSON.parse(await readFile(new URL('./byob-node-results.json',import.meta.url)));
const guarded=await guardCases(module,fixture.track),guardDeviations=[];
for(let index=0;index<guarded.length;index++){
  const entry=guarded[index],expected=nodeGuard.cases[index];assert.equal(entry.name,expected.name);
  const code=entry.name==='proxy-genuine-receiver'?'ERR_INVALID_THIS':
    ['min-two','shadowed-view-fields'].includes(entry.name)?'ERR_SM_NODE_UNSUPPORTED':null;
  if(code){assert.equal(entry.error?.code,code);guardDeviations.push({name:entry.name,node:expected,candidate:entry});}
  else assert.deepEqual(entry,expected,entry.name);
}
assert.equal(module.ReadableStream,fixture.record.ReadableStream);assert.equal(module.ReadableStreamBYOBReader,fixture.record.ReadableStreamBYOBReader);
assert.equal(module.ReadableStreamBYOBReader.prototype,fixture.record.ReadableStreamBYOBReader.prototype);
assert.equal(globalThis.TextEncoderStream,before.encoder);assert.equal(globalThis.TextDecoderStream,before.decoder);
const names=Object.keys(module).sort();assert.equal(names.length,18);assert.deepEqual(Object.keys(module.default).sort(),names.filter(value=>value!=='default'));
for(const name of ['CompressionStream','DecompressionStream'])for(const action of [()=>module[name](),()=>new module[name]()]){
  assert.throws(action,error=>error.code==='ERR_SM_NODE_UNSUPPORTED');
}
const policies=await policyCases(module,fixture),primordials=await primordialCases(module,fixture.record);
const typedViews=await typedViewCases(module,fixture.track);
const typedNode=JSON.parse(await readFile(new URL('./typed-view-node-results.json',import.meta.url))).cases;
assert.deepEqual(typedViews.slice(0,11),typedNode.slice(0,11));
assert.equal(typedViews[11].name,'DataView');assert.equal(typedViews[11].error?.code,'ERR_SM_NODE_UNSUPPORTED');
assert.equal(typedViews[11].oldBufferLength,32);assert.deepEqual(typedViews[11].recovery,[...Array(16).keys()]);
const controllers=await controllerCases(module);
assert.deepEqual(controllers,JSON.parse(await readFile(new URL('./controller-node-results.json',import.meta.url))).cases);
for(const invoke of [()=>module.ReadableStream.from([]),()=>module.ReadableStream.prototype.values.call({}),
  ()=>module.ReadableStream.prototype[Symbol.asyncIterator].call({})])assert.throws(invoke,error=>error.code==='ERR_SM_NODE_UNSUPPORTED');
assert.equal(module.ReadableStream.prototype.values,module.ReadableStream.prototype[Symbol.asyncIterator]);
result={node:process.version,scope:'Isolated host candidate only; fixture-scoped registry brand, no compiled public API integration',
  sourceSha256:createHash('sha256').update(await readFile(new URL('./factory.mjs',import.meta.url))).digest('hex'),
  constructors:actual.constructorCases.length,codecs:actual.codecCases.length,cancellations:actual.cancellationCases.length,
  codecNodeExact:true,compressionAlwaysDeferred:true,globalCodecsUnchanged:true,nativeConstructorIdentities:true,fixture:fixture.audit,
  guardCases:guarded.length,guardDeviations,policies,primordials,typedViews:typedViews.length,typedViewDeviations:['DataView'],
  guardedControllerCases:controllers.length,deferredIterableSlots:true};
}finally{const restored=fixture.restore();if(result)result.originalDescriptorsRestored=restored;assert(restored,'Restore all isolated prototype/static mutations');}
await writeFile(new URL('./host-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
