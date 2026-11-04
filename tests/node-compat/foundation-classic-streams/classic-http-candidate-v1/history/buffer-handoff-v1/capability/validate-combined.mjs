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
  assert.equal(body.native.combinedSchema,1);assert.equal(body.native.failure,undefined);
  const report=body.native.classic;
  assert.equal(report.schema,1);assert.equal(report.calls,body.componentInstanceRequestCount);
  assert(Number.isInteger(report.calls)&&report.calls>=1);
  assert.deepEqual(report.ordinary,expected);
  assert.deepEqual(report.identity,{esmAliases:true,rootDefault:true,promises:true,globalBuffer:true});
  assert.equal(body.native.baseline.foundations.calls,report.calls);
  return {...body,native:body.native.baseline};
}
export function checkCombinedHTTPReport(body,audit){
  const baseline=projectCombinedHTTPBody(body,audit);
  validateCoreRuntimeReport(baseline.native,validateCoreExpectations(audit.coreExpectations));
  checkEntropyHTTPReport(baseline,audit);checkFoundationsHTTPReport(baseline,audit);
  return baseline;
}
export function checkCombinedHTTPSamples(responses,audit){
  return checkEntropyHTTPSamples(responses.map(row=>({...row,body:projectCombinedHTTPBody(row.body,audit)})),audit);
}
