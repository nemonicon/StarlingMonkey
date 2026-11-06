// Actual exported pure option helpers only; memory writer, no filesystem output,
// Jco/module/compiler/native/fixture/generated/worker/engine/guest invocation.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {plainJSON} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {mappingOptions,fatalJcoObservation} from '../combined-native-runtime-candidate-v3/models.mjs';
import {snapshotRequestedOptions,prepareRequestedOptions,typedPostCallOptions,requestedPublicationFields} from '../combined-native-runtime-candidate-v3/mapping-options.mjs';
const P=dirname(fileURLToPath(import.meta.url)),S=join(P,'../combined-native-runtime-candidate-v3'),refs=JSON.parse(await readFile(join(S,'references.json')));let checks=0,getters=0;
const request=mappingOptions(refs,'resource');
for(const id of ['pure','resource','fatal','clock-snapshot','surviving-interest']){const r=snapshotRequestedOptions(refs,id);assert.deepEqual(r,mappingOptions(refs,id));assert(Object.isFrozen(r)&&Object.isFrozen(r.map));checks+=2;}
for(const candidate of [{...request,bad:undefined},{...request,name:'../file'},{...request,wasiShim:true},{...request,map:{...request.map,extra:'x'}},{...request,map:{...request.map,'wasi:io/*':'file:///wrong#*'}}]){assert.throws(()=>snapshotRequestedOptions(refs,'resource',candidate));checks++;}
for(const id of ['init-fatal','../../wrong','unexpected']){assert.throws(()=>snapshotRequestedOptions(refs,id));checks++;}
const accessor={...request};Object.defineProperty(accessor,'map',{get(){getters++;throw Error('accessor');},enumerable:true});assert.throws(()=>snapshotRequestedOptions(refs,'resource',accessor));assert.equal(getters,0);checks+=2;
const records=[],events=[],writer={async write(path,value,{json}){assert.equal(json,true);events.push('write:'+path);const bytes=plainJSON(value),sha256=createHash('sha256').update(bytes).digest('hex');records.push({path,bytes,value});return{path,sha256,bytes:bytes.length};}};
const boundary=await prepareRequestedOptions(writer,refs,'resource');assert.deepEqual(events,['write:requested-mapping-options.json']);assert.equal(records[0].bytes.toString(),plainJSON(request).toString());assert.notEqual(boundary.workCopy,boundary.requested);assert.notEqual(boundary.workCopy.map,boundary.requested.map);checks+=4;
let fakeCalls=0;function fake(work){events.push('fake-api');fakeCalls++;assert.equal(records.length,1);work.flagsAsBigInt??=work.flagsAsBigint;work.map['fake:work-only/*']='file:///not-retained#*';}
fake(boundary.workCopy);assert.equal(fakeCalls,1);assert.deepEqual(boundary.requested,request);assert.equal(Object.hasOwn(boundary.requested,'flagsAsBigInt'),false);assert.throws(()=>plainJSON(boundary.workCopy),/Ordinary acyclic JSON only/);assert.doesNotThrow(()=>plainJSON(boundary.requested));checks+=5;
const shape=typedPostCallOptions(boundary.workCopy),u=shape.observed.properties.find(x=>x.key==='flagsAsBigInt');assert.deepEqual(u.observed,{type:'undefined'});assert.equal(shape.inputWireClaim,false);assert.equal(shape.optionsMutatedOrSanitizedByObserver,false);assert.equal(boundary.workCopy.flagsAsBigInt,undefined);checks+=4;
const post={path:'mapping-options-postcall-shape.json',sha256:'a'.repeat(64),bytes:1},pub=requestedPublicationFields(boundary,'/synthetic-model-only',post);assert.equal(pub.mappingOptions,boundary.requested);assert.deepEqual(pub.mappingOptions,request);assert.equal(pub.postCallOptionsInputWireClaim,false);assert.doesNotThrow(()=>plainJSON(pub));checks+=4;
assert.throws(()=>requestedPublicationFields({...boundary,requested:request},'/synthetic-model-only',post));assert.throws(()=>requestedPublicationFields(boundary,'/synthetic-model-only',{...post,path:'other.json'}));checks+=2;
const writerError=Object.freeze(Error('memorywriter')),throwing={async write(){throw writerError;}};await assert.rejects(prepareRequestedOptions(throwing,refs,'resource'),e=>e===writerError);checks++;
const d={get value(){getters++;throw Error('no getter');}};const before=getters,diag=typedPostCallOptions(d);assert.equal(getters,before);assert.equal(diag.observed.properties[0].kind,'accessor');const cycle={};cycle.self=cycle;assert.equal(typedPostCallOptions(cycle).observed.properties[0].observed.circular,true);checks+=3;
const template=JSON.parse(await readFile(join(S,'future-runtime-review-contract.template.json')));assert.equal(template.fatalGateReviewPassedState,null);assert.equal(template.fatalObservationRequiredFixedValues.expectedCallbackFailureProved,false);assert.equal(template.fatalObservationRequiredFixedValues.fatalCallbackGateSatisfied,false);checks+=3;
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_V3_REQUEST_WORKCOPY_PUBLICATION_PURE_CASES_PASSED',checks,pristineRequestRetainedBeforeMemoryFakeCall:true,separateMutableNestedMap:true,realPlainJSONPristineWorksMutatedCopyRefuses:true,typedOwnUndefinedPreserved:true,accessorGetterReads:getters,memoryFakeCalls:fakeCalls,actualJcoOrNativeOrGuestInvoked:false,filesystemWriterInvokedByReviewer:false,retainedAuthorRealWriterEvidenceReviewedSeparately:true}));
