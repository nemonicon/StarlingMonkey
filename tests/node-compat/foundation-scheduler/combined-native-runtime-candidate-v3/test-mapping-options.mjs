// Bounded benign host filesystem regression only. No Jco/guest/native API.
import assert from 'node:assert/strict';
import {readFile,mkdtemp,lstat} from 'node:fs/promises';
import {join} from 'node:path';
import {DurableOutput,finish} from './output.mjs';
import {plainJSON} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {mappingOptions} from './models.mjs';
import {snapshotRequestedOptions,prepareRequestedOptions,typedPostCallOptions,requestedPublicationFields} from './mapping-options.mjs';
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url)));let checks=0,getters=0,fakeCalls=0;
const request=mappingOptions(refs,'resource'),clone=structuredClone;
function refuse(v,id='resource',r=refs){assert.throws(()=>snapshotRequestedOptions(r,id,v));checks++;}
for(const id of ['resource','pure','fatal','clock-snapshot','surviving-interest']){assert.deepEqual(snapshotRequestedOptions(refs,id),mappingOptions(refs,id));checks++;}
refuse(request,'unknown');refuse(request,'../resource');refuse(request,'init-fatal');refuse({...request,name:'../escape'});refuse({...request,wasiShim:true});refuse({...request,flagsAsBigInt:undefined});refuse({...request,map:{...request.map,'unknown:interface/*':'file:///unknown.js#*'}});refuse({...request,map:{...request.map,'wasi:io/*':'file:///wrong/path.js#*'}});
const nonenum=clone(request);Object.defineProperty(nonenum,'hidden',{value:1});refuse(nonenum);const symbol=clone(request);symbol[Symbol('hidden')]=1;refuse(symbol);const accessor={name:request.name,wasiShim:false,get map(){getters++;throw Error('getter');}};refuse(accessor);const nested=clone(request);Object.defineProperty(nested.map,'wasi:io/*',{get(){getters++;throw Error('nested getter');},enumerable:true});refuse(nested);assert.equal(getters,0);checks++;
refuse(request,'resource',{...refs,shimClocksUrl:refs.shimClocksUrl+'?query=1'});refuse(request,'resource',{...refs,shimIoUrl:'https://example.invalid/io.js'});
const diagnostic=clone(request);Object.defineProperty(diagnostic,'addedAccessor',{get(){getters++;throw Error('must not read');},enumerable:true});const diagnosticShape=typedPostCallOptions(diagnostic);assert.equal(diagnosticShape.observed.properties.find(x=>x.key==='addedAccessor').kind,'accessor');assert.equal(getters,0);checks+=2;
let writes=0;await assert.rejects(prepareRequestedOptions({write:async()=>{writes++;}},refs,'resource',{...request,bad:undefined}));assert.equal(writes,0);checks++;
const container=await mkdtemp('/private/tmp/starling-node-compat/combined-runtime-v3-source-options-'),out=await DurableOutput.create(join(container,'observation'));assert.equal((await lstat(container)).mode&0o777,0o700);
try{
 const boundary=await prepareRequestedOptions(out,refs,'resource');assert.notEqual(boundary.requested,boundary.workCopy);assert.notEqual(boundary.requested.map,boundary.workCopy.map);checks+=2;
 const fake={async transpile(bytes,opts){fakeCalls++;assert.equal(fakeCalls,1);assert.deepEqual(JSON.parse(await readFile(join(out.root,'requested-mapping-options.json'))),request);assert(bytes instanceof Uint8Array);assert(!Object.hasOwn(opts,'flagsAsBigInt'));
  // Exact nullish assignments from pinned Jco prepOpts, on synthetic work DATA.
  opts.flagsAsBigInt ??= opts.flagsAsBigint;
  opts.noComponentErrorWrapping ??= opts.componentErrorWrapping === false;
  opts.map={...opts.map,'fake:work-only/*':'file:///not-the-request.js#*'};
  return{imports:[],exports:[['run','function']],files:{'model.core.wasm':Uint8Array.from([0,97,115,109,1,0,0,0])}};
 }};
 const generated=await fake.transpile(new Uint8Array([1,2,3]),boundary.workCopy);assert.equal(fakeCalls,1);assert.equal(Object.hasOwn(boundary.workCopy,'flagsAsBigInt'),true);assert.equal(boundary.workCopy.flagsAsBigInt,undefined);assert.deepEqual(boundary.requested,request);assert.throws(()=>plainJSON({mappingOptions:boundary.workCopy}));checks+=5;
 const shape=typedPostCallOptions(boundary.workCopy);const flag=shape.observed.properties.find(x=>x.key==='flagsAsBigInt');assert.deepEqual(flag.observed,{type:'undefined'});assert.equal(shape.inputWireClaim,false);assert.equal(shape.optionsMutatedOrSanitizedByObserver,false);checks+=3;
 const failed=await DurableOutput.create(join(container,'old-publication-reproducer'));let oldFailure;
 try{await failed.write('typed-model-output/model.core.wasm',generated.files['model.core.wasm']);await failed.write('postcall-options-shape.json',shape,{json:true});let rejected=false;try{await finish(failed,{schemaVersion:1,state:'HOST_SYNTHETIC_OLD_MUTABLE_OPTIONS_FINISH_MODEL_ONLY',mappingOptions:boundary.workCopy,fakeApi:true});}catch(error){rejected=true;oldFailure=Object.getOwnPropertyDescriptor(error,'message')?.value;assert.equal(oldFailure,'Ordinary acyclic JSON only');}assert.equal(rejected,true);checks+=2;for(const name of ['result.json','index.json','completion.json']){await assert.rejects(lstat(join(failed.root,name)),e=>e.code==='ENOENT');checks++;}await failed.write('expected-serialization-refusal.json',{schemaVersion:1,realFinishInvoked:true,actualWriterFailure:oldFailure,resultIndexCompletionPublished:false,hostSyntheticOnly:true,actualJcoInvoked:false},{json:true});await failed.recheck();}finally{await failed.close();}
 const postRow=await out.write('mapping-options-postcall-shape.json',shape,{json:true});for(const[name,bytes]of Object.entries(generated.files))await out.write('typed-model-output/'+name,bytes);await out.write('typed-model-api-return.json',{imports:generated.imports,exports:generated.exports,fileNames:Object.keys(generated.files),allFileValuesUint8Array:true,fakeApi:true},{json:true});
 const result={schemaVersion:1,state:'HOST_SYNTHETIC_OPTIONS_MUTATION_PUBLICATION_MODEL_ONLY_V3',...requestedPublicationFields(boundary,out.root,postRow),fakeApi:true,actualJcoInvoked:false,generatedApplicationImported:false};const completed=await finish(out,result),actual=JSON.parse(await readFile(join(out.root,'result.json')));assert.deepEqual(actual.mappingOptions,request);assert.equal(actual.postCallOptionsInputWireClaim,false);assert.equal(completed.completeUnreviewed,true);assert.equal(Object.hasOwn(actual.mappingOptions,'flagsAsBigInt'),false);assert.deepEqual([...await readFile(join(out.root,'typed-model-output/model.core.wasm'))],[0,97,115,109,1,0,0,0]);checks+=5;await out.recheck();
 console.log(JSON.stringify({schemaVersion:1,checks,passed:true,realDurableOutputAndFinishUsed:true,fakeApiCalls:fakeCalls,requestedOptionsDurableBeforeFakeApi:true,deepWorkcopySeparate:true,undefinedMutationRejectedIfSerialized:true,realFinishMutatedCopyRejected:true,oldModelFailureOutputRoot:join(container,'old-publication-reproducer'),postCallTypedUndefinedRetained:true,gettersRead:getters,sourceOnlyModelOutput:completed,actualJcoOrNativeOrGeneratedOrGuestInvoked:false}));
}finally{await out.close();}
