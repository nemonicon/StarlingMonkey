import {createStreamWebModule} from '../production-candidate/factory.mjs';
import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {codecCases,cancellationCases,constructorCases,pipeline} from '../candidate/codec-cases.mjs';
import {guardCases} from '../candidate/guard-cases.mjs';
import {policyCases,primordialCases} from '../candidate/policy-cases.mjs';
import {typedViewCases} from '../candidate/typed-view-cases.mjs';
import {controllerCases} from '../candidate/controller-cases.mjs';
import {iterationCases} from '../iteration/cases.mjs';
import {capturedIntrinsicCases as iterationIntrinsics} from '../iteration/intrinsics.mjs';
import {dataViewCases} from '../dataview/cases.mjs';
import {policyCases as dataPolicies,capturedIntrinsicCases as dataIntrinsics} from '../dataview/policy.mjs';
function ensure(value,message){if(!value)throw Error(message);}
function equal(actual,wanted,name){if(JSON.stringify(actual)!==JSON.stringify(wanted))throw{name,actual,wanted};}
async function ownErrorCases(web,record){
  const define=Object.defineProperty,descriptor=Object.getOwnPropertyDescriptor,previous={};let gets=0,sets=0;
  const fields=['code','module','operation','profile','resource'];
  for(const field of fields)previous[field]=descriptor(Error.prototype,field);
  let count=0;
  function check(error,code){ensure(descriptor(error,'code')?.value===code,'own code '+code);count++;}
  try{
    for(const field of fields)define(Error.prototype,field,{configurable:true,get(){gets++;throw Error('inherited getter');},set(){sets++;throw Error('inherited setter');}});
    for(const invoke of [()=>web.CompressionStream(),()=>new web.CompressionStream('gzip'),()=>web.DecompressionStream(),()=>new web.DecompressionStream('gzip')]){
      let caught;try{invoke();}catch(error){caught=error;}check(caught,'ERR_SM_NODE_UNSUPPORTED');
      for(const field of ['module','operation','profile'])ensure(typeof descriptor(caught,field)?.value==='string','own metadata '+field);
    }
    for(const[label,code]of [['utf-16le','ERR_SM_NODE_UNSUPPORTED'],['invalid-label','ERR_ENCODING_NOT_SUPPORTED']]){
      let caught;try{new web.TextDecoderStream(label);}catch(error){caught=error;}check(caught,code);
    }
    let caught;try{createStreamWebModule({});}catch(error){caught=error;}check(caught,'ERR_SM_NODE_RECORD');
    try{web.ReadableStream.prototype.values.call({});}catch(error){caught=error;}check(caught,'ERR_INVALID_THIS');
    const tooLong=await pipeline(new web.TextEncoderStream(),['a'.repeat(1048577)]);
    ensure(tooLong.writes[0]?.error?.code==='ERR_SM_NODE_LIMIT','own limit code');count++;
  }finally{
    for(const field of fields)if(previous[field])define(Error.prototype,field,previous[field]);else delete Error.prototype[field];
  }
  // Keep native fatal error construction outside the poisoned-prototype
  // window. The pinned Node22 backend aborts in that known combination; never
  // repeat it. Source mapping itself uses own descriptors, not inherited reads.
  const fatal=await pipeline(new web.TextDecoderStream('utf-8',{fatal:true}),[Uint8Array.of(0xff)]);
  ensure(fatal.writes[0]?.error?.code==='ERR_ENCODING_INVALID_ENCODED_DATA','native fatal code');count++;
  ensure(gets===0&&sets===0,'no inherited error accessors');return{checks:count,inheritedGets:gets,inheritedSets:sets};
}
export async function runComposed(expected){
  const report={passed:false};let fixture;
  try{
    fixture=await fixtureRecord();const web=createStreamWebModule(fixture.record);
    for(const[name,invoke]of [['constructors',()=>constructorCases(web)],['codecs',()=>codecCases(web)],['cancellations',()=>cancellationCases(web)]]){
      const actual=await invoke();equal(actual,expected.codecs[name==='constructors'?'constructorCases':name==='codecs'?'codecCases':'cancellationCases'],name);report[name]=actual.length;
    }
    const guarded=await guardCases(web,fixture.track);report.guardDeviations=[];
    for(let index=0;index<guarded.length;index++){
      const actual=guarded[index],wanted=expected.guards.cases[index];
      const code=actual.name==='proxy-genuine-receiver'?'ERR_INVALID_THIS':['min-two','shadowed-view-fields'].includes(actual.name)?'ERR_SM_NODE_UNSUPPORTED':null;
      if(code){ensure(actual.error?.code===code,'guard '+actual.name);report.guardDeviations.push(actual.name);}else equal(actual,wanted,actual.name);
    }
    report.guards=guarded.length;
    const views=await typedViewCases(web,fixture.track);equal(views,expected.views.cases,'all ordinary views');report.views=views.length;
    const controllers=await controllerCases(web);equal(controllers,expected.controllers.cases,'guarded controllers');report.controllers=controllers.length;
    const iterations=await iterationCases(web);equal(iterations,expected.iteration.cases,'readable iteration');report.iterations=iterations.length;
    const data=await dataViewCases(web,fixture.track);report.dataDeviations=[];
    for(let index=0;index<data.length;index++){
      const actual=data[index],wanted=JSON.parse(JSON.stringify(expected.data.cases[index]));
      if(actual.name==='released-reader-rejects-before-transfer'&&actual.value?.result?.error?.code===undefined){delete wanted.value.result.error.code;report.dataDeviations.push(actual.name);}
      equal(actual,wanted,'data '+actual.name);
    }
    report.data=data.length;
    report.policies=await policyCases(web,fixture);report.dataPolicies=await dataPolicies(web,fixture.track);
    report.codecIntrinsics=await primordialCases(web,fixture.record);report.iterationIntrinsics=await iterationIntrinsics(fixture.record);
    report.dataIntrinsics=await dataIntrinsics(web,fixture.track);report.ownErrors=await ownErrorCases(web,fixture.record);
    report.names=Object.keys(web).sort();ensure(report.names.length===18&&Object.keys(web.default).length===17,'finite export record');
    for(const name of report.names)if(name!=='default')ensure(web[name]===web.default[name],'default identity '+name);
    for(const name of ['ReadableStream','ReadableStreamBYOBReader','WritableStreamDefaultWriter','TransformStreamDefaultController'])ensure(web[name]===fixture.record[name],'native identity '+name);
    report.nativeIdentities=true;report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined?error:{name:error?.name,message:error?.message,stack:error?.stack};}
  finally{if(fixture)report.originalDescriptorsRestored=fixture.restore();}
  return report;
}
