// Read completed actual outputs only; never starts a host, compiler or guest.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {verifyHTTPReady} from '../classic-http-candidate-v1/capability/http-contract.mjs';
import {hash} from '../classic-http-candidate-v1/capability/preflight.mjs';
import {validateCombinedHosts} from '../classic-http-candidate-v1/capability/validate-hosts.mjs';
const ready=await verifyHTTPReady(),root=ready.pin.root;
const wasmtimePath=join(root,'http-joint/wasmtime-v2/wasmtime-results.json');
const washPath=join(root,'http-joint-wasmcloud-results.json');
const wasmtime=JSON.parse(await readFile(wasmtimePath)),wash=JSON.parse(await readFile(washPath));
const checks=validateCombinedHosts({audit:ready.audit,wasmtime,wash});
assert.equal(hash(await readFile(wash.component.deployedPath)),ready.pin.componentSha256);
assert.equal(hash(await readFile(wasmtime.command[0])),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
assert.equal(hash(await readFile(wash.host.binaryPath)),'365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954');
const config=JSON.parse(await readFile(wash.configPath));assert.deepEqual(config,wash.configuration);
const userIndex=wash.configInspectionCommand.indexOf('--user-config');assert(userIndex>=0);
const userConfig=wash.configInspectionCommand[userIndex+1];assert.deepEqual(JSON.parse(await readFile(userConfig)),{});
for(const name of ['components','plugins','host_plugins','volumes'])assert.deepEqual(config.dev[name],[]);
assert.equal(config.dev.service,false);
for(const key of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']){
  assert.deepEqual(config.workload[key],[]);assert.deepEqual(wash.effectiveConfiguration.workload[key],[]);
}
assert.equal(wash.isolation.globalInstallationModified,false);assert.equal(wash.isolation.isolatedXdgDirectories,true);
for(const key of ['customHostPlugins','sidecars','volumes'])assert.deepEqual(wash.isolation[key],[]);
assert.equal(wash.isolation.dockerUsed,false);assert.equal(wash.isolation.natsUsed,false);
const paths=[ready.pin.componentPath,ready.pin.auditPath,ready.pin.bundlePath,ready.pin.inputsPath,
  wasmtimePath,washPath,wasmtime.process.logPath,wash.process.logPath,wash.configPath,userConfig,
  join(dirname(dirname(wash.configPath)),'../host-results.json'),
  join(root,'http-joint/native-profile-http.core.wasm'),
  join(root,'http-joint/component-types.json'),join(root,'http-joint/emitted.wit'),join(root,'http-joint/packaging-audit.json'),
  join(root,'http-joint/production-admission-complete.json'),
  join(root,'http-joint/wasmtime-v2/production-admission-complete.json'),join(root,'wash/production-admission-complete.json')];
const artifacts=[];
for(const path of [...new Set(paths.map(value=>resolve(value)))]){const bytes=await readFile(path);artifacts.push({path,bytes:bytes.length,sha256:hash(bytes)});}
const sourceBytes=await readFile(ready.admission.report.inputClosure.path);assert.equal(hash(sourceBytes),ready.admission.report.inputClosure.sha256);
const counters=[wasmtime,wash].map(value=>value.responses.map(row=>row.body.componentInstanceRequestCount));
await ready.recheck();
const report={schemaVersion:1,state:'CLASSIC_COMBINED_HTTP_RESPONSES_AND_ARTIFACTS_AUDIT_PASSED_REQUIRES_OUTER_EXIT_ZERO',
  verifiedAtUtc:new Date().toISOString(),...checks,nativeAdmission:ready.admission.report,
  component:{...ready.pin,emittedImports:ready.audit.emittedImports,emittedExports:ready.audit.emittedExports,clockDependency:ready.audit.clockDependency},sourceFilesVerified:JSON.parse(sourceBytes).inputs,artifacts,
  counters,rawCombinedBodiesPreserved:true,baselineValidationProjection:'Data-only input to unchanged baseline checks; persisted raw reports retain baseline+classic.',
  sourceEntryPath:ready.pin.sourceEntryPath,coreExpectations:ready.audit.coreExpectations,
  instanceReuseClaim:false,requestIsolationClaim:false,requiresIndependentBuildAndWrapperTerminalExitZero:true,
  limitations:['Only baseline schema5/protected29 and ordinary classic19 with bounded literal identities.',
    'No classic initializer/fatal/limit/CJS/GC/Web bridge or complete Node streams claim.',
    'Known then-getter and Symbol gaps, GC coowners, ALS/reset/cancellation remain open.',
    'No outgoing HTTP, filesystem, DNS, sockets, TLS, callable clock or performance claim.']};
const output=resolve(process.env.NODE_COMPAT_CLASSIC_HTTP_RESULTS??join(root,'combined-http-results.json'));
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,output,componentSha256:ready.pin.componentSha256,requestsPerHost:3,ordinaryGroups:19}));
