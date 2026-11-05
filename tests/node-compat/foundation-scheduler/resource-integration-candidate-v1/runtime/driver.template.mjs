// UNEXECUTED SOURCE TEMPLATE. Dynamic packager/guest loading is hard-closed below.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const ACTIVATION=null; // Requires a separately reviewed genuine preflight/loader successor.
const CASE_CALLBACKS=[2,1,4,2,2,2,1],CASE_IDS=[2,2,2,3,2,2,33];
function envelope(value){const type=typeof value;if(type==='string'||type==='boolean')return{type,value};if(type==='undefined')return{type};if(type==='number')return{type,value:Number.isNaN(value)?'NaN':Object.is(value,-0)?'-0':value===Infinity?'Infinity':value===-Infinity?'-Infinity':value};if(type==='bigint')return{type,value:value.toString()};if(value===null)return{type:'object',value:null};return{type,opaque:true,fullOpaqueValueClaim:false};}

// This is a source seam, not an existing embedding API or an issued authority.
// The separately reviewed future resource342 preflight must authenticate the
// complete native freeze/tool trees/links/live adapter+WIT before returning it.
export async function constructResourceFixtures(admission,writeExclusive){
 assert(ACTIVATION,'SOURCE_ONLY: actual native/packaging/clock-closure activation is unissued');
 assert(admission&&admission.resourceSourceContract==='sm-web-timer-resource-owner-source-v1');
 assert(admission.rootComponentAuthority&&admission.actualNativeReview&&admission.packagingClosureReview);
 assert.equal(admission.sourceFiles,342);assert.equal(admission.nativeReplacements,2);
 assert.equal(typeof admission.recheck,'function');assert.equal(typeof writeExclusive,'function');
 await admission.recheck();
 const {loadToolchain}=await import(pathToFileURL(join(admission.packagingRoot,'tests/node-compat/toolchain.mjs')));
 const {loadComponentizer}=await import(pathToFileURL(join(admission.packagingRoot,'tests/node-compat/componentizer.mjs')));
 const toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
 const {componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
 const wit=await readFile(new URL('./profile.wit',import.meta.url),'utf8');
 const timerInterfaces=['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'];
 const ordinarySource=await readFile(new URL('./guest.UNEXECUTED.mjs',import.meta.url),'utf8');
 // This is a registered native import, not a Node fallback or guest factory bundle.
 assert.deepEqual([...ordinarySource.matchAll(/^import .* from '([^']+)';/gm)].map(m=>m[1]),['node:buffer']);
 const scalarWit='package test:scheduler-resource-scalar; world validation { export run: func() -> string; }';
 const fixtures=[{name:'resource',source:ordinarySource,wit,clocks:true},
  {name:'pure',source:await readFile(new URL('./pure.UNEXECUTED.mjs',import.meta.url),'utf8'),wit:scalarWit,clocks:false},
  {name:'fatal',source:await readFile(new URL('./fatal.UNEXECUTED.mjs',import.meta.url),'utf8'),wit:scalarWit,clocks:true},
  {name:'init-fatal',source:await readFile(new URL('./init-fatal.UNEXECUTED.mjs',import.meta.url),'utf8'),wit:scalarWit,clocks:true,expectedInitFailure:true}];
 const records=[];
 for(const fixture of fixtures){
  const interfaces=fixture.clocks?timerInterfaces:[];let captured=false,built,failure,threw=false;
  const options={engine:admission.enginePath,preview2Adapter:admission.adapterPath,witWorld:fixture.wit,worldName:'validation',disableFeatures:['stdio','random','http','fetch-event',...(fixture.clocks?[]:['clocks'])],selectedInterfaces:interfaces,
   // Actual repository wrapper API: retain unmodified bytes before its final import audit.
   finalizeComponent:async result=>{await writeExclusive(fixture.name+'/component.wasm',result.component);await writeExclusive(fixture.name+'/emitted.wit',await componentWit(result.component));captured=true;return result.component;}};
  try{built=await selected.componentize(fixture.source,options);}catch(error){threw=true;failure=error;await writeExclusive(fixture.name+'/construction-error.json',JSON.stringify({returned:envelope(error),componentCaptured:captured})+'\n');}
  await admission.recheck();
  if(fixture.expectedInitFailure){assert.equal(threw,true);assert.equal(captured,false);records.push({name:fixture.name,expectedInitializationFailure:true,componentCaptured:captured,uniqueErrorCauseProved:false});continue;}
  if(threw)throw failure;assert(captured);
  await writeExclusive(fixture.name+'/interface-audit.json',JSON.stringify(built.interfaceAudit,null,2)+'\n');
  // Coarse clocks may keep extra interfaces; never silently widen the contract.
  assert.deepEqual([...built.interfaceAudit.emittedImports].sort(),[...interfaces].sort());
  const lowered=await transpile(built.component,{name:'resource',wasiShim:true});
  // Real returned file list, isolated per fixture; no guessed core/glue names or loader API.
  for(const[name,bytes]of Object.entries(lowered.files))await writeExclusive(fixture.name+'/transpiled/'+name,bytes);
  await writeExclusive(fixture.name+'/transpile-metadata.json',JSON.stringify({imports:lowered.imports,exports:lowered.exports},null,2)+'\n');
  records.push({name:fixture.name,interfaceAudit:built.interfaceAudit,generatedModuleImported:false});
 }
 await admission.recheck();
 return{state:'RESOURCE342_COMPONENTS_CONSTRUCTED_UNREVIEWED',records,ordinaryExports:['inspect','run','validate'],generatedModuleImported:false,rootGuestAuthority:null};
}

// Invoke only after independent actual component/core/glue/d.ts/type-graph review.
// The future loader must use the observed real ESM/TLA protocol, not a guessed
// instantiate()/compile() shape; its exact implementation remains NULL here.
export async function collectResourceCase(module,caseId,persistRaw,admission){
 assert(ACTIVATION,'SOURCE_ONLY: actual component/loader/export activation is unissued');
 assert(admission?.rootGuestAuthority&&admission.actualComponentReview);
 assert(Number.isInteger(caseId)&&caseId>=0&&caseId<7);
 let raw;try{raw=module.run(caseId);}catch(error){await persistRaw({caseId,threw:true,returned:envelope(error)});throw error;}
 await persistRaw({caseId,threw:false,returned:envelope(raw)});
 assert.equal(typeof raw,'string');const value=JSON.parse(raw);
 assert.equal(value.kind,'scheduler-resource-run-v1');assert.equal(value.caseId,caseId);assert.equal(value.completed,true);
 assert.equal(value.after.ownPendingNativeHandleCountInstrumented,false);
 assert.equal(value.after.counters.timerCallbacks-value.before.counters.timerCallbacks,CASE_CALLBACKS[caseId]);
 assert.equal(value.after.counters.completedCases,value.before.counters.completedCases+1);
 assert.equal(value.after.registeredIds.length-value.before.registeredIds.length,CASE_IDS[caseId]);
 assert.deepEqual(value.after.registeredIds.slice(0,value.before.registeredIds.length),value.before.registeredIds);
 assert.equal(new Set(value.after.registeredIds).size,value.after.registeredIds.length);
 assert(value.after.registeredIds.every(id=>Number.isInteger(id)&&id>0));
 assert.equal(value.after.resetCalled,false);assert.equal(value.nativeResourceCountsObserved,false);
 if(caseId===0){assert.equal(value.result.pressureChecksum,3192);assert.deepEqual(value.result.events,[{kind:'one-shot',value:'queued-'+value.current,strictReceiverNull:true}]);}
 if(caseId===1){assert.equal(value.result.fired,0);assert.equal(value.result.doubleClear,true);}
 if(caseId===2){assert.equal(value.result.ticks,3);assert.deepEqual(value.result.events,[1,2,3]);}
 if(caseId===3){assert.equal(value.result.victimCalls,0);assert.deepEqual(value.result.events,['outer']);}
 if(caseId===4){assert.equal(value.result.token,'active-'+value.current);assert.equal(value.result.pressureChecksum,3192);assert.equal(value.result.soleTemporaryRootProved,false);}
 if(caseId===5){assert.equal(value.result.same,true);assert.equal(value.result.message,'RESOURCE_HANDLED_CALLBACK');}
 if(caseId===6){assert.equal(value.result.fired,0);assert.equal(value.result.cleared.length,32);assert.equal(value.result.allocationFailureInjected,false);}
 return value;
}
