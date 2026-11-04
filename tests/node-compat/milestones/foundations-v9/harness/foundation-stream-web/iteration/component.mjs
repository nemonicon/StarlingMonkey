import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {createStreamWebModule} from '../candidate/factory.mjs';
import {installReadableIteration} from './algorithms.mjs';
import {iterationCases} from './cases.mjs';
import {capturedIntrinsicCases} from './intrinsics.mjs';
import expected from 'node-compat:stream-iteration-oracle';
let calls=0;
export async function run(){
  const report={calls:++calls,passed:false,cases:0};let fixture;
  try{
    fixture=await fixtureRecord();const web=createStreamWebModule(fixture.record);installReadableIteration(fixture.record);
    const actual=await iterationCases(web);
    for(let index=0;index<expected.cases.length;index++){
      if(JSON.stringify(actual[index])!==JSON.stringify(expected.cases[index]))throw{index,actual:actual[index],wanted:expected.cases[index]};
      report.cases++;
    }
    if(actual.length!==expected.cases.length)throw{actual:actual.length,wanted:expected.cases.length};
    report.nativeConstructorIdentity=web.ReadableStream===fixture.record.ReadableStream;
    report.iteratorIdentity=web.ReadableStream.prototype.values===web.ReadableStream.prototype[Symbol.asyncIterator];
    report.intrinsics=await capturedIntrinsicCases(fixture.record);
    report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined?error:{name:error?.name,message:error?.message,stack:error?.stack};}
  finally{if(fixture)report.originalDescriptorsRestored=fixture.restore();}
  return JSON.stringify(report);
}
