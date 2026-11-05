// Pure synthetic contract/parser tests only. No helper, package, guest or process.
import assert from 'node:assert/strict';
import {fixtureModel,authorityModel,optionsModel,checkInterfaces,scalarAbiFromWit,checkTranspileMetadata,TIMER_INTERFACES,OUTPUT_BASE} from './models.mjs';
let checks=0;const yes=v=>{assert(v);checks++;};const no=fn=>{assert.throws(fn);checks++;};
const sha='a'.repeat(64);
function root(name){return {schemaVersion:1,state:'ROOT_REVIEWED_SCHEDULER_RESOURCE342_COMPONENT_CONSTRUCTION_PHASE_V1',sourceIndexSha256:sha,fixture:name,phase:'construct-component',componentConstructionAllowed:true,initializationOnly:true,outputRoot:OUTPUT_BASE+'-'+name,workerTimeoutMs:600000,maxComponentBytes:64*1024*1024,maxBundleBytes:32*1024*1024,...Object.fromEntries(['nativeBuildAllowed','nativeFreezeAllowed','sourcePromotionAllowed','ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','hostRequestsAllowed','gcAllowed','keyOrCryptoAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed'].map(k=>[k,false]))};}
for(const name of ['resource','pure','fatal','init-fatal']){
 const model=fixtureModel(name),r=root(name);yes(authorityModel(r,sha).name===name);
 const cb=()=>{},options=optionsModel({engine:{path:'/actual/engine.wasm'},adapter:{path:'/actual/53512.wasm'},fixture:name,wit:'declared scalar WIT',finalizeComponent:cb});
 yes(options.engine==='/actual/engine.wasm'&&options.preview2Adapter==='/actual/53512.wasm'&&options.finalizeComponent===cb);
 yes(JSON.stringify(options.selectedInterfaces)===JSON.stringify(model.clocks?TIMER_INTERFACES:[]));yes(options.disableFeatures.includes('clocks')===!model.clocks);
 const imports=model.clocks?[...TIMER_INTERFACES]:[];yes(checkInterfaces({state:'verified-final-component',emittedImports:imports},name));
 for(const extra of ['wasi:clocks/wall-clock@0.2.10','wasi:io/error@0.2.10','wasi:io/streams@0.2.10','wasi:io/poll@0.2.12','custom:clock/now'])no(()=>checkInterfaces({state:'verified-final-component',emittedImports:[...imports,extra]},name));
 if(model.clocks)no(()=>checkInterfaces({state:'verified-final-component',emittedImports:[TIMER_INTERFACES[0]]},name));
 no(()=>checkInterfaces({state:'not-an-actual-audit',emittedImports:imports},name));
 const body=[...imports.map(v=>'import '+v+';'),...Object.entries(model.expectedAbi).map(([key,value])=>'export '+key+': func('+(value.startsWith('(u32)')?'case-id: u32':'')+') -> string;')].join('\n');
 const wit='package root:component;\nworld root {\n'+body+'\n}\n';assert.deepEqual(scalarAbiFromWit(wit,name),model.expectedAbi);checks++;
 no(()=>scalarAbiFromWit(wit.replace('-> string','-> u32'),name));no(()=>scalarAbiFromWit(wit.replace('world root','world other'),name));
 no(()=>scalarAbiFromWit(wit.replace('world root {','world root { export extra: func() -> string;'),name));
 const meta={imports:imports,exports:Object.keys(model.expectedAbi).map(n=>[n,'function'])};yes(checkTranspileMetadata(meta,name));
 no(()=>checkTranspileMetadata({...meta,exports:[...meta.exports,['then','function']]},name));
 no(()=>checkTranspileMetadata({...meta,exports:meta.exports.map(([n])=>[n,'instance'])},name));
 no(()=>authorityModel({...r,sourceIndexSha256:'b'.repeat(64)},sha));no(()=>authorityModel({...r,outputRoot:'/some/old/output'},sha));
 for(const field of ['ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','gcAllowed','runtimeAcceptanceClaim'])no(()=>authorityModel({...r,[field]:true},sha));
 yes(model.expectedInitializationRefusal===(name==='init-fatal'));
}
no(()=>fixtureModel('unknown'));no(()=>authorityModel(root('resource'),'b'.repeat(64)));
no(()=>optionsModel({engine:{path:'/e'},fixture:'pure',wit:'x',finalizeComponent:()=>{}}));
console.log(JSON.stringify({schemaVersion:1,state:'PURE_RESOURCE_COMPONENT_MODELS_PASSED_V1',checks,syntheticOnly:true,sourceModelsOnly:true,ownerHelperOrBootstrapOrPackagerOrGuestInvoked:false}));
