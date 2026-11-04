import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {createStreamWebModule} from '../candidate/factory.mjs';
import {installDataViewBYOB} from './adapter.mjs';
import {dataViewCases} from './cases.mjs';
import {policyCases,capturedIntrinsicCases} from './policy.mjs';
import {guardCases} from '../candidate/guard-cases.mjs';
import {typedViewCases} from '../candidate/typed-view-cases.mjs';
import expected from 'node-compat:stream-dataview-oracle';
let calls=0;
export async function run(){
  const report={calls:++calls,passed:false,cases:0};let fixture;
  try{
    fixture=await fixtureRecord();const nativeRead=fixture.record.ReadableStreamBYOBReader.prototype.read;
    const apply=Reflect.apply,typedName=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(Uint8Array.prototype),Symbol.toStringTag).get;
    const nativeKinds={};let dataViewNativeCalls=0;
    function checkedNativeRead(view){const kind=apply(typedName,view,[]);
      if(kind===undefined){dataViewNativeCalls++;throw Error('DataView must never enter old native branch');}
      nativeKinds[kind]=(nativeKinds[kind]??0)+1;return apply(nativeRead,this,[view]);}
    const web=createStreamWebModule(fixture.record);installDataViewBYOB(fixture.record,checkedNativeRead);
    const actual=await dataViewCases(web,fixture.track);
    report.deviations=[];
    for(let index=0;index<expected.cases.length;index++){
      const wanted=JSON.parse(JSON.stringify(expected.cases[index]));
      if(actual[index].name==='released-reader-rejects-before-transfer'){
        if(actual[index].value?.result?.error?.code!==undefined)throw{index,actual:actual[index],wanted:'native error code absent'};
        delete wanted.value.result.error.code;report.deviations.push({name:actual[index].name,nodeCode:'ERR_INVALID_STATE',candidateCode:'absent'});
      }
      if(JSON.stringify(actual[index])!==JSON.stringify(wanted))throw{index,actual:actual[index],wanted};
      report.cases++;
    }
    if(actual.length!==expected.cases.length)throw{actual:actual.length,wanted:expected.cases.length};
    report.nativeReaderIdentity=web.ReadableStreamBYOBReader===fixture.record.ReadableStreamBYOBReader;
    const typedViews=await typedViewCases(web,fixture.track);
    if(JSON.stringify(typedViews)!==JSON.stringify(expected.typedViews.cases))throw{actual:typedViews,wanted:expected.typedViews.cases};
    report.typedViews=typedViews.length;
    const guarded=await guardCases(web,fixture.track);report.guardDeviations=[];
    for(let index=0;index<guarded.length;index++){
      const actual=guarded[index],wanted=expected.guards.cases[index];
      const code=actual.name==='proxy-genuine-receiver'?'ERR_INVALID_THIS':
        ['min-two','shadowed-view-fields'].includes(actual.name)?'ERR_SM_NODE_UNSUPPORTED':null;
      if(code){if(actual.error?.code!==code)throw{actual,wanted:code};report.guardDeviations.push(actual.name);}
      else if(JSON.stringify(actual)!==JSON.stringify(wanted))throw{actual,wanted};
    }
    report.guardCases=guarded.length;report.policies=await policyCases(web,fixture.track);report.intrinsics=await capturedIntrinsicCases(web,fixture.track);
    report.originalNativeDataViewCalls=dataViewNativeCalls;report.originalNativeInputKinds=nativeKinds;
    if(dataViewNativeCalls!==0)throw{actual:dataViewNativeCalls,wanted:0};
    report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined?error:{name:error?.name,message:error?.message,stack:error?.stack};}
  finally{if(fixture)report.originalDescriptorsRestored=fixture.restore();}
  return JSON.stringify(report);
}
