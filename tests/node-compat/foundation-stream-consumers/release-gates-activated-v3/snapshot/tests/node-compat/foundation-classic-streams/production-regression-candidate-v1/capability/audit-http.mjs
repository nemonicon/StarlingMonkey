// Recheck completed host results; this script never starts a host or build.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { selectCoreExpectations, validateCoreRuntimeReport } from '../../../core-expectations.mjs';
import {verifyHTTPReady} from './http-contract.mjs';
import { checkFoundationsHTTPReport } from '../../../foundations/assert-http-report.mjs';
import { checkEntropyHTTPReport, checkEntropyHTTPSamples } from '../../../entropy/assert-http-report.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const ready=await verifyHTTPReady();
const root=ready.pin.root;
const repository = resolve(here, '../../../../..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = async path => JSON.parse(await readFile(path));
const sourceInputs = await json(join(root, 'http-inputs.json'));
assert.equal(sourceInputs.sourceInputClosure.sha256,ready.admission.report.inputClosure.sha256);
const admitted=ready.admission;
assert.equal(admitted.report.engineSha256,ready.pin.engineSha256);
assert.equal(admitted.pin.receiptSha256,ready.pin.engineReceiptSha256);
const core = selectCoreExpectations(admitted.metadata,{sourceRoot:admitted.sourceRoot});
assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
const audit = await json(join(root, 'http-joint/component-audit.json'));
const wasmtime = await json(join(root, 'http-joint/wasmtime-v1/wasmtime-results.json'));
const wash = await json(join(root, 'http-joint-wasmcloud-results.json'));
const imports = ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10',
  'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10'];
const componentHash = hash(await readFile(audit.componentPath));
const fixedComponent=ready.pin;
assert.equal(fixedComponent.state,'reviewed-real-runtime-http-component');
assert.equal(componentHash,fixedComponent.componentSha256);assert.equal(fixedComponent.engineSha256,admitted.report.engineSha256);
assert.equal(fixedComponent.applicationBundleSha256,audit.applicationBundleSha256);
assert.equal(componentHash, audit.componentSha256);
assert.equal(audit.engineSha256, admitted.report.engineSha256);
assert.deepEqual(audit.coreExpectations,core);
assert.equal(audit.protectedAbortFoundationsFixture, true);
assert.equal(audit.httpEntry,join(here,'http-component.mjs'));
assert.equal(audit.entropyPolicy, 'runtime-only');
assert.deepEqual(audit.emittedImports, imports);
assert.deepEqual(audit.emittedExports, ['wasi:http/incoming-handler@0.2.10']);
assert.equal(audit.clockDependency.typeOnly, true);
assert.deepEqual(audit.clockDependency.callableImports, []);
assert.deepEqual(audit.clockDependency.coreClockImports, []);
assert.equal(wasmtime.componentSha256, componentHash);
assert.equal(wash.component.sha256, componentHash);
assert.equal(hash(await readFile(wash.component.deployedPath)), componentHash);
assert.equal(wasmtime.wasmtime.startsWith('wasmtime 42.0.1 '), true);
assert.equal(wash.host.version, '2.11.0');
assert.equal(wash.host.unmodifiedOfficialBinary, true);
assert.equal(hash(await readFile(wasmtime.command[0])), 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
assert.equal(hash(await readFile(wash.host.binaryPath)), '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954');
for (const report of [wasmtime, wash]) {
  assert.equal(report.responses.length, 3);
  assert.equal(report.process.stopped, true);
  assert.deepEqual(report.process.exitStatus, { code:0, signal:null });
  const counters=report.responses.map(value=>value.body.componentInstanceRequestCount);
  assert(counters.every(value=>Number.isInteger(value)&&value>=1));
  assert.equal(report.retainedStateObserved,counters.some(value=>value>1));
  for (const response of report.responses) {
    assert.equal(response.status, 200);
    assert.equal(response.body.native.foundations.schema, 5);
    validateCoreRuntimeReport(response.body.native, core);
    checkFoundationsHTTPReport(response.body, audit);
    checkEntropyHTTPReport(response.body, audit);
  }
  checkEntropyHTTPSamples(report.responses, audit);
}
for (const key of ['allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts']) assert.deepEqual(wash.effectiveConfiguration.workload[key], []);
const paths = [
  'http-inputs.json', 'observed-http-component-seal.json', 'http-joint-build.log',
  'http-joint-wasmtime-v1.log', 'http-joint-wasmcloud.log',
  'http-joint/native-profile-http.component.wasm', 'http-joint/native-profile-http.core.wasm',
  'http-joint/http.bundle.mjs', 'http-joint/component-audit.json', 'http-joint/packaging-audit.json',
  'http-joint/emitted.wit', 'http-joint/component-types.json',
  'http-joint/wasmtime-v1/wasmtime-http.log', 'http-joint/wasmtime-v1/wasmtime-results.json',
  'http-joint-wasmcloud-results.json',
];
const artifacts = [];
for (const path of [...paths.map(path => join(root,path)), wash.process.logPath]) {
  const bytes = await readFile(path); artifacts.push({ path, bytes:bytes.length, sha256:hash(bytes) });
}
const sourceManifestBytes=await readFile(admitted.report.inputClosure.path);
assert.equal(hash(sourceManifestBytes),admitted.report.inputClosure.sha256,'Source seal changed before JSON parsing');
const sourceFiles=JSON.parse(sourceManifestBytes).inputs;
const report = {
  state:'CLASSIC342_HTTP_BOTH_UNMODIFIED_HOSTS_PASSED', verifiedAtUtc:new Date().toISOString(), node:process.version,
  nativeAdmission:admitted.report, coreExpectations:core, nativeSourceManifest:admitted.metadata.sourceManifest,
  component:{path:audit.componentPath,sha256:componentHash,bytes:audit.componentBytes,emittedImports:imports,
    emittedExports:audit.emittedExports,clockDependency:audit.clockDependency},
  foundationSchema:5, protectedAbortGroups:{public:16,nested:4,receivers:9,total:29},
  hosts:[
    {product:wasmtime.wasmtime,binaryPath:wasmtime.command[0],requests:3,counters:wasmtime.responses.map(value=>value.body.componentInstanceRequestCount),process:wasmtime.process},
    {product:'official wash 2.11.0',host:wash.host,requests:3,counters:wash.responses.map(value=>value.body.componentInstanceRequestCount),process:wash.process,isolation:wash.isolation},
  ],
  instanceReuseClaim:false, sourceFilesVerified:sourceFiles, artifacts,
  sourceReceiptTiming:'The complete sealed source closure was authenticated before packaging and reverified after both hosts; native342/config/macro admission, fixed Runtime engine and independently reviewed component pins are reverified here.',
  limitations:[
    'Only 29 positive/handled abort groups are in HTTP; fatal initialized/deployed components remain in the separate focused runner.',
    'Disposal-symbol Node registry identity/description remain explicit measured differences.',
    'No new host capability or clock function; no outgoing HTTP, filesystem, DNS, socket or TLS behavior exercised.',
    'Recorded counters do not establish general safe instance reuse or request lifecycle; no full Node/EventTarget/stream/process or performance claim.',
    'Fresh callback-return then-getter read counts remain Node ordinary/protected/already-aborted 1/1/0 vs native 0/0/0; this core change does not close the inherited Events gap.',
    'Correctness artifacts include test oracles; no performance, memory or component-size advantage follows.',
  ],
};
await ready.recheck();
const output=resolve(process.env.NODE_COMPAT_PRODUCTION_HTTP_RESULTS??join(root,'http-results.json'));
await writeFile(output, JSON.stringify(report,null,2)+'\n', {flag:'wx'});
console.log(JSON.stringify({state:report.state,output,componentSha256:componentHash,requestsPerHost:3,protectedAbortGroups:29,sourceFilesVerified:sourceFiles.length,nativeSources:342},null,2));
