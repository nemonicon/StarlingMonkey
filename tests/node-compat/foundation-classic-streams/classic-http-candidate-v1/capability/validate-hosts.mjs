import assert from 'node:assert/strict';
import {checkCombinedHTTPReport,checkCombinedHTTPSamples} from './validate-combined.mjs';
import {validateHTTPInterfaces} from './capabilities.mjs';
export function validateCombinedHosts({audit,wasmtime,wash}){
  validateHTTPInterfaces(audit);assert.equal(audit.classicCombinedHTTP.ordinaryGroups,19);
  assert.equal(wasmtime.componentSha256,audit.componentSha256);assert.equal(wash.component.sha256,audit.componentSha256);
  assert(wasmtime.wasmtime.startsWith('wasmtime 42.0.1 '));assert.equal(wash.host.version,'2.11.0');assert.equal(wash.host.unmodifiedOfficialBinary,true);
  for(const report of [wasmtime,wash]){
    assert.equal(report.responses.length,3);assert.equal(report.process.stopped,true);assert.deepEqual(report.process.exitStatus,{code:0,signal:null});
    for(const row of report.responses){assert.equal(row.status,200);checkCombinedHTTPReport(row.body,audit,row.requestTag??row.request);}
    checkCombinedHTTPSamples(report.responses,audit);
  }
  for(const key of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts'])assert.deepEqual(wash.effectiveConfiguration.workload[key],[]);
  return{state:'COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED',componentSha256:audit.componentSha256,requestsPerHost:3,
    ordinaryClassicGroups:19,protectedAbortGroups:29,instanceReuseClaim:false,requestIsolationClaim:false};
}
