// Extract only actual pure own-property/pin DATA functions; no observer import.
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual} from 'node:util';
import vm from 'node:vm';
const HERE=dirname(fileURLToPath(import.meta.url));
const source=await readFile(join(HERE,'ownership-secret-artifact-bootstrap-v3-root-controller.mjs'),'utf8');
const purePins=source.slice(source.indexOf('function onlyFourPinEdits('),source.indexOf('async function privateTree('));
const pureReturn=source.slice(source.indexOf('export function capturePublicReturn('),source.indexOf('async function absent(')).replace(/^export /gm,'');
if(!purePins||!pureReturn||purePins.includes('await ')||pureReturn.includes('await '))throw new Error('Only actual pure Source extraction');
const model=`
function need(v,m){if(!v)throw new Error(m);}
${purePins}
${pureReturn}
(async()=>{
 const checks=[];const check=(v,m)=>{need(v,m);checks.push(m);};
 const refuses=(fn,m)=>{try{fn();}catch{checks.push(m);return;}throw new Error('Expected refusal '+m);};
 const original={schemaVersion:3,state:'UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3',reviewRequired:true,variants:{'normal-off':{state:'unreviewed-secret-owner355-normal-off-pin-v3',reviewRequired:true,metadata:{whole:'UNCHANGED'},verifierFrame:{originalRoot:'/PURE/ORIGINAL'}},'normal-runtime':null,'gc-off':null,'disabled-off':null},operationalAdmission:false};
 const reviewed=JSON.parse(JSON.stringify(original));reviewed.state='ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3';reviewed.reviewRequired=false;reviewed.variants['normal-off'].state='reviewed-secret-owner355-normal-off-pin-v3';reviewed.variants['normal-off'].reviewRequired=false;
 onlyFourPinEdits(original,reviewed);check(original.reviewRequired===true&&reviewed.reviewRequired===false,'actual JS four-edit guard and input unchanged');
 for(const name of ['metadata','other-variant','missing-field','extra-field','wrong-flag']){
  const bad=JSON.parse(JSON.stringify(reviewed));
  if(name==='metadata')bad.variants['normal-off'].metadata.whole='REWRITTEN';
  if(name==='other-variant')bad.variants['gc-off']={};
  if(name==='missing-field')delete bad.variants['normal-off'].verifierFrame;
  if(name==='extra-field')bad.projected=true;
  if(name==='wrong-flag')bad.reviewRequired=true;
  refuses(()=>onlyFourPinEdits(original,bad),'JS full pin guard refuses '+name);
 }
 let calls=0;
 const python={schemaVersion:3,metadata:{all75:'UNCHANGED'},selectedManifests:[{whole:'manifest'}],historical:{verified:false,version:null,vernum:null},originalRoot:'/PURE/ORIGINAL',extraDataField:{retained:true}};
 const value=Object.freeze({...python,recheck:async()=>{calls++;}});
 const snapshot=capturePublicReturn(value),captured=publicDataAndCallable(snapshot,Object.isFrozen(value));
 check(same(captured.data,python),'all DATA own fields and nested metadata retained');
 check(snapshot.keys.length===Object.keys(python).length+1&&snapshot.shape.length===snapshot.keys.length,'complete own property shape');
 check(captured.callable===value.recheck,'genuine callable reference retained without execution');
 check(same(captured.callableDescriptor,{property:'recheck',valueType:'function',enumerable:true,configurable:false,writable:false,ownName:'recheck',ownLength:0,returnObjectFrozen:true}),'complete callable property descriptor');
 check(calls===0,'shape/DATA capture did not call recheck');await captured.callable();check(calls===1,'one synthetic returned callable invocation');
 refuses(()=>publicDataAndCallable(capturePublicReturn({...python,recheck:()=>{}}),false),'unfrozen public object refuses');
 refuses(()=>publicDataAndCallable(capturePublicReturn(Object.freeze({...python,recheck:'not callable'})),true),'non-callable recheck refuses');
 refuses(()=>publicDataAndCallable(capturePublicReturn(Object.freeze({...python,recheck:()=>{},omitted:undefined})),true),'undefined DATA cannot be silently omitted');
 const symbolic={...python,recheck:()=>{}};symbolic[Symbol('extra')]='observed';Object.freeze(symbolic);const symbolicSnapshot=capturePublicReturn(symbolic);check(symbolicSnapshot.shape.some(r=>r.keyType==='symbol'),'unexpected symbol key visible in raw shape');refuses(()=>publicDataAndCallable(symbolicSnapshot,true),'symbol DATA refuses');
 let getterCalls=0;const accessor={recheck:()=>{}};Object.defineProperty(accessor,'metadata',{get(){getterCalls++;return {};},enumerable:true});Object.freeze(accessor);const accessorSnapshot=capturePublicReturn(accessor);check(getterCalls===0,'capturing descriptors never invokes getters');refuses(()=>publicDataAndCallable(accessorSnapshot,true),'accessor DATA refuses');check(getterCalls===0,'refusal never invokes getter');
 const wrong={...python,metadata:{all75:'SHORTENED'}};check(!same(captured.data,wrong),'whole Python equality detects metadata changes');
 return {schemaVersion:1,state:'SECRET355_BOOTSTRAP_OBSERVER_PURE_DATA_MODELS_PASSED_V1',checks:checks.length,checkNames:checks,actualObserverImported:false,actualBootstrapCalled:false,actualPinCandidateDerived:false,syntheticDataOnly:true};
})()`;
const result=await vm.runInNewContext(model,{same:isDeepStrictEqual},{timeout:1000,filename:'actual-extracted-pure-bootstrap-functions'});
await writeFile(join(HERE,'js-pure-results.json'),JSON.stringify(result,null,2)+'\n');
process.stdout.write(JSON.stringify({checks:result.checks,sourceOnly:true})+'\n');
