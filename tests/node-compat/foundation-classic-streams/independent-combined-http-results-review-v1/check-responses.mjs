// Persisted JSON validation only. No preflight, host, component or guest import.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const root='/tmp/starling-node-compat/production-classic-http-v1/http';
const read=async name=>JSON.parse(await readFile(resolve(root,name)));
assert.notEqual(process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1');
const source=resolve(here,'../classic-http-candidate-v1/capability/validate-hosts.mjs');
assert.equal(createHash('sha256').update(await readFile(source)).digest('hex'),'4c6fb72b6d0f7e7054771e922180e809a92ea8a8c59856d3a7d3af010c2d8e6c');
const {validateCombinedHosts}=await import(source);
const audit=await read('http-joint/component-audit.json');
const wasmtime=await read('http-joint/wasmtime-v2/wasmtime-results.json');
const wash=await read('http-joint-wasmcloud-results.json');
const report=validateCombinedHosts({audit,wasmtime,wash});
assert.deepEqual(report,{state:'COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED',
  componentSha256:'25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d',
  requestsPerHost:3,ordinaryClassicGroups:19,protectedAbortGroups:29,instanceReuseClaim:false,requestIsolationClaim:false});
const observations=[];
for(const [host,value] of [['wasmtime',wasmtime],['wash',wash]])for(const row of value.responses){
  const body=row.body,foundation=body.native.baseline.foundations,protectedAbort=foundation.protectedAbort;
  assert.equal(foundation.schema,5);assert.equal(body.native.classic.ordinary.length,19);
  assert.equal(protectedAbort.publicCases.length,16);assert.equal(protectedAbort.nestedOnceCases.length,4);assert.equal(protectedAbort.receiverCases.length,9);
  assert.equal(protectedAbort.symbol.sameAsNodeRegistry,false);
  observations.push({host,request:row.requestTag??row.request,status:row.status,counter:body.componentInstanceRequestCount,
    baselineSchema:foundation.schema,classicGroups:19,protectedGroups:29,
    symbol:protectedAbort.symbol,classicIdentity:body.native.classic.identity});
}
const output=resolve(here,'response-check-results.json');
await writeFile(output,JSON.stringify({schemaVersion:1,state:'PERSISTED_COMBINED_HTTP_ALL_RESPONSE_ASSERTIONS_PASSED',
  ...report,responsesChecked:6,ordinaryGroupOccurrences:114,protectedGroupOccurrences:174,observations,
  executionScope:'Data-only functions on persisted JSON; no preflight, host, component or guest execution'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:'PERSISTED_COMBINED_HTTP_ALL_RESPONSE_ASSERTIONS_PASSED',responses:6,output}));
