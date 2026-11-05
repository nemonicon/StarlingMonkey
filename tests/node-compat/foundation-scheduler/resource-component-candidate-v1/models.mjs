// Pure construction contracts. No IO, tools, native helpers or guest imports.
export const TIMER_INTERFACES=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10']);
export const OUTPUT_BASE='/private/tmp/starling-node-compat/scheduler-resource-component-v1';
export function need(value,message){if(!value)throw new Error(message);}
export function fixtureModel(name){
 need(['resource','pure','fatal','init-fatal'].includes(name),'Finite exact fixture');
 return Object.freeze({name,clocks:name!=='pure',expectedResidualImports:name==='resource'||name==='pure'?['node:buffer']:[],
  expectedAbi:name==='resource'?{inspect:'() -> string',run:'(u32) -> string',validate:'() -> string'}:{run:'() -> string'},
  expectedInitializationRefusal:name==='init-fatal'});
}
export function authorityModel(root,sourceSha){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_SCHEDULER_RESOURCE342_COMPONENT_CONSTRUCTION_PHASE_V1'&&root.sourceIndexSha256===sourceSha,'New exact Root construction frame');
 const fixture=fixtureModel(root.fixture);
 need(root.phase==='construct-component'&&root.componentConstructionAllowed===true&&root.initializationOnly===true,'Construction and initialization only');
 need(root.outputRoot===OUTPUT_BASE+'-'+fixture.name&&root.workerTimeoutMs===600000&&root.maxComponentBytes===64*1024*1024&&root.maxBundleBytes===32*1024*1024,'Exact bounded fresh fixture namespace');
 for(const key of ['nativeBuildAllowed','nativeFreezeAllowed','sourcePromotionAllowed','ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','hostRequestsAllowed','gcAllowed','keyOrCryptoAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed'])need(root[key]===false,'No additional authority '+key);
 return fixture;
}
export function optionsModel({engine,adapter,fixture,wit,finalizeComponent}){
 const selected=fixtureModel(fixture);
 need(typeof engine?.path==='string'&&typeof adapter?.path==='string'&&typeof wit==='string'&&typeof finalizeComponent==='function','Actual native/adapter/WIT/finalizer inputs');
 return {engine:engine.path,preview2Adapter:adapter.path,witWorld:wit,worldName:'validation',selectedInterfaces:selected.clocks?[...TIMER_INTERFACES]:[],
  disableFeatures:['stdio','random','http','fetch-event',...(selected.clocks?[]:['clocks'])],enableAot:false,env:{},finalizeComponent};
}
export function checkInterfaces(audit,fixture){
 const selected=fixtureModel(fixture),expected=selected.clocks?[...TIMER_INTERFACES]:[];
 need(audit?.state==='verified-final-component'&&Array.isArray(audit.emittedImports),'Actual selected final-interface audit');
 need(JSON.stringify([...audit.emittedImports].sort())===JSON.stringify(expected.sort()),'Exact two timer interfaces or pure imports[]; never widen');
 return true;
}
export function scalarAbiFromWit(text,fixture){
 need(typeof text==='string'&&Buffer.byteLength(text)<=2*1024*1024,'Finite actual WIT');
 const clean=text.replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,'');
 const markers=[...clean.matchAll(/\bworld\s+root\s*\{/g)];need(markers.length===1,'One finite root world');
 const start=markers[0].index+markers[0][0].length;let depth=1,end=start;
 for(;end<clean.length&&depth;end++){if(clean[end]==='{')depth++;if(clean[end]==='}')depth--;}
 need(depth===0,'Closed root world');const body=clean.slice(start,end-1),abi={},imports=[];
 for(const part of body.split(';').map(s=>s.trim()).filter(Boolean)){
  if(part.startsWith('import ')){const m=/^import\s+([^\s;{}]+)$/.exec(part);need(m,'Only finite exact named root interfaces');imports.push(m[1]);continue;}
  const m=/^export\s+([a-z]+):\s*func\(([^)]*)\)\s*->\s*string$/.exec(part);need(m&&!Object.hasOwn(abi,m[1]),'Only unique scalar string exports');
  need(!m[2].trim()||/^[a-z][a-z-]*:\s*u32$/.test(m[2].trim()),'Only one named u32 parameter');abi[m[1]]='('+(m[2].trim()?'u32':'')+') -> string';
 }
 const selected=fixtureModel(fixture),expected=selected.clocks?[...TIMER_INTERFACES]:[];
 need(JSON.stringify([...imports].sort())===JSON.stringify(expected.sort()),'Actual root imports must match the fixed selection');
 need(JSON.stringify(Object.entries(abi).sort())===JSON.stringify(Object.entries(selected.expectedAbi).sort()),'Exact public scalar ABI');return abi;
}
export function checkTranspileMetadata(value,fixture){
 const names=Object.keys(fixtureModel(fixture).expectedAbi);
 need(Array.isArray(value?.imports)&&Array.isArray(value?.exports)&&value.exports.length===names.length&&new Set(value.exports.map(v=>v[0])).size===names.length&&value.exports.every(v=>Array.isArray(v)&&v.length===2&&names.includes(v[0])&&v[1]==='function'),'Actual finite public Jco function metadata');
 // The raw import list and generated file graph are retained, not relabelled.
 // Actual shim/glue/core/clock type graphs and ESM/TLA loading need independent review.
 return true;
}
