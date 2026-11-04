// Host validation only. Preserves the raw combined body in host reports.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {checkFoundationsHTTPReport} from '../../../foundations/assert-http-report.mjs';
import {checkEntropyHTTPReport,checkEntropyHTTPSamples} from '../../../entropy/assert-http-report.mjs';
import {validateCoreExpectations,validateCoreRuntimeReport} from '../../../core-expectations.mjs';
const raw=readFileSync(new URL('../../implementation-candidate-v1/node-final-acceptance-results.json',import.meta.url));
assert.equal(createHash('sha256').update(raw).digest('hex'),'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');
const expected=JSON.parse(raw).expected;assert.equal(expected.length,19);
export function projectCombinedHTTPBody(body,audit){
  assert.equal(body.schema,1);assert.equal(body.failure,undefined);
  assert.equal(audit.classicCombinedHTTP.schema,1);assert.equal(audit.classicCombinedHTTP.ordinaryGroups,19);
  assert.equal(body.native.combinedSchema,1);assert.equal(body.native.failure,undefined);
  assert.equal(body.native.baseline.failure,undefined);
  const report=body.native.classic;
  assert.equal(report.schema,1);assert.equal(report.failure,undefined);assert.equal(report.calls,body.componentInstanceRequestCount);
  assert(Number.isInteger(report.calls)&&report.calls>=1);
  assert.deepEqual(report.ordinary,expected);
  assert.deepEqual(report.identity,{esmAliases:true,rootDefault:true,promises:true,globalBuffer:true});
  assert.equal(body.native.baseline.foundations.calls,report.calls);
  return {...body,native:body.native.baseline};
}
export function checkCombinedHTTPReport(body,audit,expectedRequestTag=body.requestTag){
  const baseline=projectCombinedHTTPBody(body,audit);
  const coreExpectations=validateCoreExpectations(audit.coreExpectations);
  assert.equal(baseline.requestTag,expectedRequestTag);assert(baseline.componentInstanceRequestCount>=1);
  validateCoreRuntimeReport(baseline.native,coreExpectations);
  assert.equal(baseline.native.allocUnsafePolicy,coreExpectations.allocUnsafePolicy);
  for(const[key,value]of Object.entries({strings:381,bytes:250,stubCalls:9,stubConstructors:9,unavailableMethods:91,globalBufferIdentity:true,staticCommonJS:true}))assert.equal(baseline.native[key],value);
  assert.equal(baseline.snapshotMarker,'HTTP module initialized during componentization');
  for(const[field,operation]of [['unsupported','spawn'],['unsupportedConstructor','ChildProcess']]){
    assert.equal(baseline[field].code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(baseline[field].module,'node:child_process');
    assert.equal(baseline[field].operation,operation);assert.equal(baseline[field].profile,coreExpectations.coreVersion);
  }
  if(process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS==='1'){
    assert.equal(baseline.native.intrinsics.nativeModule,true);assert.equal(baseline.native.intrinsics.sizesChecked,8);
    assert.equal(baseline.native.intrinsics.publicReplacementCalls,0);assert.equal(baseline.native.intrinsics.capturedProducerAndBrandChecksPassed,true);
  }
  checkEntropyHTTPReport(baseline,audit);checkFoundationsHTTPReport(baseline,audit);
  return baseline;
}
export function checkCombinedHTTPSamples(responses,audit){
  return checkEntropyHTTPSamples(responses.map(row=>({...row,body:projectCombinedHTTPBody(row.body,audit)})),audit);
}
