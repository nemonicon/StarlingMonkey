import { checkFoundationsHTTPReport } from '../../../../foundations/assert-http-report.mjs';
import assert from 'node:assert/strict';
import {projectCombinedHTTPBody,checkCombinedHTTPSamples as checkEntropyHTTPSamples} from '../validate-combined.mjs';
import { validateCoreExpectations, validateCoreRuntimeReport } from '../../../../core-expectations.mjs';
import { createHash } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { mkdir, open, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { checkEntropyHTTPReport } from '../../../../entropy/assert-http-report.mjs';

assert.equal(process.version, 'v22.14.0');
assert(process.env.NODE_COMPAT_WASMTIME, 'Set NODE_COMPAT_WASMTIME to Wasmtime 42.0.1');
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME);
const output = resolve(process.env.NODE_COMPAT_HTTP_OUTPUT ?? '/tmp/starling-node-compat/wasmcloud-http');
const auditPath = resolve(process.env.NODE_COMPAT_HTTP_AUDIT ?? join(output, 'component-audit.json'));
const audit = JSON.parse(await readFile(auditPath));
const coreExpectations = validateCoreExpectations(audit.coreExpectations);
const component = await readFile(audit.componentPath);
assert.equal(createHash('sha256').update(component).digest('hex'), audit.componentSha256);
for (const id of audit.emittedImports) assert(audit.allowedImports.includes(id), `Unselected host interface: ${id}`);
const version = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.error?.message || version.stderr);
assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true });
const logPath = join(output, 'wasmtime-http.log');
const log = await open(logPath, 'w');
const args = ['serve', '--addr', '127.0.0.1:0', audit.componentPath];
const host = spawn(wasmtime, args, { stdio: ['ignore', log.fd, log.fd] });
let exited = false;
let exitStatus;
const exit = new Promise(resolve => host.once('exit', (code, signal) => { exited = true; exitStatus = { code, signal }; resolve(); }));
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const responses = [];
let url;
try {
  const deadline = Date.now() + 60000;
  while (Date.now() < deadline) {
    const text = await readFile(logPath, 'utf8');
    if (exited) throw new Error(`Wasmtime exited before listening: ${JSON.stringify(exitStatus)}\n${text}`);
    const address = /Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text);
    if (address) { url = address[1]; break; }
    await pause(100);
  }
  assert(url, `Wasmtime did not start HTTP listener; see ${logPath}`);
  for (let i = 1; i <= 3; i++) {
    const requestTag = `/node-compat?request=${i}`;
    const response = await fetch(url + requestTag, { signal: AbortSignal.timeout(30000), redirect: 'error' });
    const text = await response.text();
    assert.equal(response.status, 200, text);
    assert.match(response.headers.get('content-type'), /^application\/json/);
    assert.equal(response.headers.get('cache-control'), 'no-store');
    const combinedBody = JSON.parse(text);
    const body = projectCombinedHTTPBody(combinedBody,audit);
    assert.equal(body.schema, 1);
    assert.equal(body.requestTag, requestTag);
    assert(body.componentInstanceRequestCount >= 1);
    validateCoreRuntimeReport(body.native, coreExpectations);
    assert.equal(body.native.allocUnsafePolicy, coreExpectations.allocUnsafePolicy);
    assert.equal(body.native.strings, 381);
    assert.equal(body.native.bytes, 250);
    assert.equal(body.native.stubCalls, 9);
    assert.equal(body.native.stubConstructors, 9);
    assert.equal(body.native.unavailableMethods, 91);
    assert.equal(body.native.globalBufferIdentity, true);
    assert.equal(body.native.staticCommonJS, true);
    if (process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS === '1') {
      assert.equal(body.native.intrinsics.nativeModule, true);
      assert.equal(body.native.intrinsics.sizesChecked, 8);
      assert.equal(body.native.intrinsics.publicReplacementCalls, 0);
      assert.equal(body.native.intrinsics.capturedProducerAndBrandChecksPassed, true);
    }
    assert.equal(body.snapshotMarker, 'HTTP module initialized during componentization');
    for (const [field, operation] of [['unsupported', 'spawn'], ['unsupportedConstructor', 'ChildProcess']]) {
      assert.equal(body[field].code, 'ERR_SM_NODE_UNSUPPORTED');
      assert.equal(body[field].module, 'node:child_process');
      assert.equal(body[field].operation, operation);
      assert.equal(body[field].profile, coreExpectations.coreVersion);
    }
    checkEntropyHTTPReport(body, audit);
    checkFoundationsHTTPReport(body, audit);
    responses.push({ requestTag, status: response.status, body: combinedBody });
  }
} finally {
  if (!exited) host.kill('SIGINT');
  await Promise.race([exit, pause(5000)]);
  if (!exited) { host.kill('SIGKILL'); await exit; }
  await log.close();
}
checkEntropyHTTPSamples(responses, audit);
const summary = {
  schema: 1, wasmtime: version.stdout.trim(), componentSha256: audit.componentSha256,
  componentBytes: component.length, emittedImports: audit.emittedImports, emittedExports: audit.emittedExports,
  command: [wasmtime, ...args], address: url, responses,
  retainedStateObserved: responses.some(result => result.body.componentInstanceRequestCount > 1),
  process: { stopped: exited, exitStatus, logPath },
  limitations: ['Repeated HTTP success does not establish same-instance reuse when counters restart', 'This verifies the explicit standard HTTP handler, not StarlingMonkey fetch-event request reuse'],
};
await writeFile(join(output, 'wasmtime-results.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
