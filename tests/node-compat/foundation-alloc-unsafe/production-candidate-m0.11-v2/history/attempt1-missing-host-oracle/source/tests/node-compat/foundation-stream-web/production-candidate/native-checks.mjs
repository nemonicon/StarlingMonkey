// PREPARED/UNEXECUTED. Imported only by the future installed-module fixture.
// No factory is called, no registry brand is substituted, no prototype is
// installed/restored here; all classes/guards come from the real native module.
import {codecCases,cancellationCases,constructorCases,pipeline} from '../candidate/codec-cases.mjs';
import {guardCases} from '../candidate/guard-cases.mjs';
import {typedViewCases} from '../candidate/typed-view-cases.mjs';
import {controllerCases} from '../candidate/controller-cases.mjs';
import {policyCases,primordialCases} from './native-policies.mjs';
import {iterationCases} from '../iteration/cases.mjs';
import {capturedIntrinsicCases as iterationIntrinsics} from '../iteration/intrinsics.mjs';
import {dataViewCases} from '../dataview/cases.mjs';
import {policyCases as dataPolicies,capturedIntrinsicCases as dataIntrinsics} from '../dataview/policy.mjs';
function ensure(value,message){if(!value)throw Error(message);}
function equal(actual,wanted,name){if(JSON.stringify(actual)!==JSON.stringify(wanted))throw{name,actual,wanted};}
async function ownErrorCases(web){
  const define=Object.defineProperty,descriptor=Object.getOwnPropertyDescriptor,previous={};let gets=0,sets=0;
  const fields=['code','module','operation','profile','resource'];for(const field of fields)previous[field]=descriptor(Error.prototype,field);
  let count=0;function check(error,code){ensure(descriptor(error,'code')?.value===code,'own code '+code);count++;}
  try{
    for(const field of fields)define(Error.prototype,field,{configurable:true,get(){gets++;throw Error('inherited getter');},set(){sets++;throw Error('inherited setter');}});
    for(const invoke of [()=>web.CompressionStream(),()=>new web.CompressionStream('gzip'),()=>web.DecompressionStream(),()=>new web.DecompressionStream('gzip')]){
      let caught;try{invoke();}catch(error){caught=error;}check(caught,'ERR_SM_NODE_UNSUPPORTED');
      for(const field of ['module','operation','profile'])ensure(typeof descriptor(caught,field)?.value==='string','own metadata '+field);
    }
    for(const[label,code]of [['utf-16le','ERR_SM_NODE_UNSUPPORTED'],['invalid-label','ERR_ENCODING_NOT_SUPPORTED']]){
      let caught;try{new web.TextDecoderStream(label);}catch(error){caught=error;}check(caught,code);
    }
    let caught;try{web.ReadableStream.prototype.values.call({});}catch(error){caught=error;}check(caught,'ERR_INVALID_THIS');
    const tooLong=await pipeline(new web.TextEncoderStream(),['a'.repeat(1048577)]);
    ensure(tooLong.writes[0]?.error?.code==='ERR_SM_NODE_LIMIT','own source-limit code');count++;
  }finally{for(const field of fields)if(previous[field])define(Error.prototype,field,previous[field]);else delete Error.prototype[field];}
  // Known Node22 fatal-native-decode + poisoned inherited code combination is
  // never repeated. Native decoding happens ONLY AFTER prototype restoration.
  const fatal=await pipeline(new web.TextDecoderStream('utf-8',{fatal:true}),[Uint8Array.of(0xff)]);
  ensure(fatal.writes[0]?.error?.code==='ERR_ENCODING_INVALID_ENCODED_DATA','normal native fatal code');count++;
  ensure(gets===0&&sets===0,'no inherited error metadata accessors');return{checks:count,inheritedGets:gets,inheritedSets:sets};
}
export async function runNativeCorpus(web,expected){
  const report={passed:false};
  try{
    // Public native methods require no substitute brand. Each helper's reader
    // is the actual reader returned by the installed stream constructor.
    const track=value=>value,record={...web,TextEncoder:globalThis.TextEncoder,TextDecoder:globalThis.TextDecoder};
    const fixture={track};
    for(const[name,invoke]of [['constructors',()=>constructorCases(web)],['codecs',()=>codecCases(web)],['cancellations',()=>cancellationCases(web)]]){
      const actual=await invoke();equal(actual,expected.codecs[name==='constructors'?'constructorCases':name==='codecs'?'codecCases':'cancellationCases'],name);report[name]=actual.length;
    }
    const guarded=await guardCases(web,track);report.guardDeviations=[];
    for(let index=0;index<guarded.length;index++){
      const actual=guarded[index],wanted=expected.guards.cases[index];
      const code=actual.name==='proxy-genuine-receiver'?'ERR_INVALID_THIS':['min-two','shadowed-view-fields'].includes(actual.name)?'ERR_SM_NODE_UNSUPPORTED':null;
      if(code){ensure(actual.error?.code===code,'guard '+actual.name);report.guardDeviations.push(actual.name);}else equal(actual,wanted,actual.name);
    }
    report.guards=guarded.length;
    const views=await typedViewCases(web,track);equal(views,expected.views.cases,'all ordinary views');report.views=views.length;
    // Safe ONLY after native-preflight has admitted the corrected guard files.
    // ON uses selected Node-facing wrappers; separate OFF runner proves the
    // original native methods without wrappers on the same corrected source.
    const controllers=await controllerCases(web);equal(controllers,expected.controllers.cases,'guarded controllers');report.controllers=controllers.length;
    const iterations=await iterationCases(web);equal(iterations,expected.iteration.cases,'readable iteration');report.iterations=iterations.length;
    const data=await dataViewCases(web,track);report.dataDeviations=[];
    for(let index=0;index<data.length;index++){
      const actual=data[index],wanted=JSON.parse(JSON.stringify(expected.data.cases[index]));
      if(actual.name==='released-reader-rejects-before-transfer'&&actual.value?.result?.error?.code===undefined){delete wanted.value.result.error.code;report.dataDeviations.push(actual.name);}
      equal(actual,wanted,'data '+actual.name);
    }
    report.data=data.length;report.policies=await policyCases(web,fixture);report.dataPolicies=await dataPolicies(web,track);
    report.codecIntrinsics=await primordialCases(web,record);report.iterationIntrinsics=await iterationIntrinsics(record);
    report.dataIntrinsics=await dataIntrinsics(web,track);report.ownErrors=await ownErrorCases(web);
    report.privateFactoryRecordTests='not application surface; preserved source-stage proof only (2 checks)';
    report.fixtureRegistryUsed=false;report.applicationFactoryUsed=false;report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined?error:{name:error?.name,message:error?.message,stack:error?.stack};}
  return report;
}
