// Recheck completed host results; this script never starts a host or build.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { preflight } from '../foundation-add-abort/production-native-m0.10/preflight.mjs';
import { checkFoundationsHTTPReport } from './assert-http-report.mjs';
import { checkEntropyHTTPReport, checkEntropyHTTPSamples } from '../entropy/assert-http-report.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.env.NODE_COMPAT_HTTP_V10_ROOT ?? '/tmp/starling-node-compat/foundations-v10');
const repository = resolve(here, '../../..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = async path => JSON.parse(await readFile(path));
const sourceInputs = await json(join(root, 'http-v10-inputs.json'));
for (const file of sourceInputs.sourceFiles) assert.equal(hash(await readFile(join(repository, file.path))), file.sha256, file.path);
const admitted = await preflight();
assert.equal(admitted.report.engineSha256, 'dc5f834d84e43c34a0019176e082743e72cc9f1c284bfa3331d368d5416866a9');
const audit = await json(join(root, 'http-joint/component-audit.json'));
const wasmtime = await json(join(root, 'http-joint/wasmtime-v2/wasmtime-results.json'));
const wash = await json(join(root, 'http-joint-wasmcloud-results.json'));
const imports = ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10',
  'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10'];
const componentHash = hash(await readFile(audit.componentPath));
assert.equal(componentHash, '0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610');
assert.equal(componentHash, audit.componentSha256);
assert.equal(audit.engineSha256, admitted.report.engineSha256);
assert.equal(audit.protectedAbortFoundationsFixture, true);
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
  assert.equal(report.retainedStateObserved, false);
  assert.deepEqual(report.responses.map(value => value.body.componentInstanceRequestCount), [1,1,1]);
  for (const response of report.responses) {
    assert.equal(response.status, 200);
    assert.equal(response.body.native.foundations.schema, 5);
    checkFoundationsHTTPReport(response.body, audit);
    checkEntropyHTTPReport(response.body, audit);
  }
  checkEntropyHTTPSamples(report.responses, audit);
}
for (const key of ['allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts']) assert.deepEqual(wash.effectiveConfiguration.workload[key], []);
const oldPacket = 'tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11/';
const preserved = {
  'tests/node-compat/foundations/http-v9.mjs':'1ed1b2415ba5a84d1e024ae49cb723ed3ff473c23d0a656583f679c189664f2c',
  [oldPacket+'index.json']:'ef229fb89f768486ccc4cb142bd1defbec79e08aa091bf782d17d1592a6ba29a',
  [oldPacket+'source-receipt.json']:'740c2ea910055b1435270161c23ee80e305cd61ed806ad7d132021e80edb6d3b',
  [oldPacket+'host-results.json']:'fef08ee6f551fe999ef14fc6a34c49252ea4330e829389f40065f2d66be84ded',
};
for (const [path, sha256] of Object.entries(preserved)) assert.equal(hash(await readFile(join(repository,path))), sha256, path);
const paths = [
  'http-v10-inputs.json', 'http-v10-native-preflight.json', 'http-joint-build.log',
  'http-joint-wasmtime.log', 'http-joint-wasmtime-v2.log', 'http-joint-wasmcloud.log',
  'http-joint/native-profile-http.component.wasm', 'http-joint/native-profile-http.core.wasm',
  'http-joint/http.bundle.mjs', 'http-joint/component-audit.json', 'http-joint/packaging-audit.json',
  'http-joint/emitted.wit', 'http-joint/component-types.json', 'http-joint/wasmtime-http.log',
  'http-joint/wasmtime-v2/wasmtime-http.log', 'http-joint/wasmtime-v2/wasmtime-results.json',
  'http-joint-wasmcloud-results.json',
];
const artifacts = [];
for (const path of [...paths.map(path => join(root,path)), wash.process.logPath]) {
  const bytes = await readFile(path); artifacts.push({ path, bytes:bytes.length, sha256:hash(bytes) });
}
const sourceFiles = [...sourceInputs.sourceFiles];
for (const path of ['audit-http-v10.mjs','http-v10.md']) {
  const bytes = await readFile(join(here,path));
  sourceFiles.push({path:'tests/node-compat/foundations/'+path,bytes:bytes.length,sha256:hash(bytes)});
}
const report = {
  state:'HTTP_V10_BOTH_UNMODIFIED_HOSTS_PASSED', verifiedAtUtc:new Date().toISOString(), node:process.version,
  nativeAdmission:admitted.report, nativeSourceManifest:admitted.metadata.sourceManifest,
  component:{path:audit.componentPath,sha256:componentHash,bytes:audit.componentBytes,emittedImports:imports,
    emittedExports:audit.emittedExports,clockDependency:audit.clockDependency},
  foundationSchema:5, protectedAbortGroups:{public:16,nested:4,receivers:9,total:29},
  hosts:[
    {product:wasmtime.wasmtime,binaryPath:wasmtime.command[0],requests:3,counters:[1,1,1],process:wasmtime.process},
    {product:'official wash 2.11.0',host:wash.host,requests:3,counters:[1,1,1],process:wash.process,isolation:wash.isolation},
  ],
  instanceReuseClaim:false, sourceFilesVerified:sourceFiles, preservedSourceReceipts:preserved, artifacts,
  knownHarnessFailure:{
    attempt:1,scope:'Optional NODE_COMPAT_HTTP_REQUIRE_INTRINSICS=1 was incorrectly enabled for a fixture without body.native.intrinsics',
    componentFailureClaim:false,logsPreserved:true,correction:'Same component bytes; no source edit or repackaging; fresh Wasmtime-v2 result directory with ordinary joint-fixture checks',
  },
  sourceReceiptTiming:'The 16-file source-input receipt was captured after the builder launched, then reverified here. Native 304-source/macro preflight ran before packaging and is reverified here; the builder records the exact consumed bundle hash.',
  coordination:'Wash launched just before a parent HOLD message arrived. It reached terminal success and clean shutdown; no new jobs were launched until the third transparent-storage compaction reported terminal. Logical artifact bytes were reverified after compaction.',
  limitations:[
    'Only29positive/handled abort groups are in HTTP; fatal initialized/deployed components remain in the separate focused runner.',
    'Disposal-symbol Node registry identity/description remain explicit measured differences.',
    'No new host capability or clock function; no outgoing HTTP, filesystem, DNS, socket or TLS behavior exercised.',
    'Counters restart on both hosts. No same-instance reuse, general request lifecycle, full Node/EventTarget/stream/process or performance claim.',
    'The first m0.11 packet remains frozen/unapplied. Future promotion requires a separate additive HTTP-v10 rebase.',
  ],
};
const output = resolve(process.env.NODE_COMPAT_HTTP_V10_RESULTS ?? join(here,'http-v10-results.json'));
await writeFile(output, JSON.stringify(report,null,2)+'\n', {flag:'wx'});
console.log(JSON.stringify({state:report.state,output,componentSha256:componentHash,requestsPerHost:3,protectedAbortGroups:29,sourceFilesVerified:sourceFiles.length,nativeSources:304},null,2));
