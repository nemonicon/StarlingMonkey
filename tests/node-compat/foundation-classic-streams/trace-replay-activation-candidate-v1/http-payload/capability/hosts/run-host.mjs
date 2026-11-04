import { checkFoundationsHTTPReport } from '../../../../foundations/assert-http-report.mjs';
import { checkEntropyHTTPReport } from '../../../../entropy/assert-http-report.mjs';
// Run the native profile through the released, unmodified wasmCloud 2.11 CLI.
// Uses its supported `wash dev` deployment workflow, bound to loopback only.
import assert from 'node:assert/strict';
import {projectCombinedHTTPBody,checkCombinedHTTPSamples as checkEntropyHTTPSamples} from '../validate-combined.mjs';
import { validateCoreExpectations, validateCoreRuntimeReport } from '../../../../core-expectations.mjs';
import { createHash } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { open, readFile, writeFile, mkdir, mkdtemp, chmod } from 'node:fs/promises';
import { createServer } from 'node:net';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

assert.equal(process.version, 'v22.14.0', 'run with the pinned Node.js oracle');
const here = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../wasmcloud');
const workRoot = resolve(process.env.NODE_COMPAT_WASMCLOUD_OUTPUT ?? '/tmp/starling-node-compat/wasmcloud');
const componentPath = resolve(process.env.NODE_COMPAT_HTTP_COMPONENT ?? '/tmp/starling-node-compat/wasmcloud-http/native-profile-http.component.wasm');
const auditPath = resolve(process.env.NODE_COMPAT_HTTP_AUDIT ?? '/tmp/starling-node-compat/wasmcloud-http/component-audit.json');
const targets = {
  'darwin-arm64': ['aarch64-apple-darwin', '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954'],
  'darwin-x64': ['x86_64-apple-darwin', '9c287ea9e027f0c2d391400e7897c8e8225109cfee6efaf2e7b238afea233f17'],
  'linux-arm64': ['aarch64-unknown-linux-gnu', 'c3b2204dd99ae2bc46c1236967f4a328cebe3b57d3d5a1605091618eff66bcad'],
  'linux-x64': ['x86_64-unknown-linux-gnu', '701e6cd698e33916315cb6e1fcbd2e28cabeafe20800e4bd99d231dee09bfd37'],
};
const target = targets[`${process.platform}-${process.arch}`];
assert(target, 'supported download platforms are macOS and glibc Linux, arm64/x64');
const [releaseTarget, releaseHash] = target;
const releaseUrl = `https://github.com/wasmCloud/wasmCloud/releases/download/v2.11.0/wash-${releaseTarget}`;
const wash = resolve(process.env.NODE_COMPAT_WASH ?? join(workRoot, 'bin', `wash-2.11.0-${releaseTarget}`));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
await mkdir(dirname(wash), { recursive: true });
let washBytes;
try { washBytes = await readFile(wash); }
catch (error) {
  if (error.code !== 'ENOENT' || process.env.NODE_COMPAT_WASH) throw error;
  const download = spawnSync('curl', ['-fL', '--retry', '3', '-o', wash, releaseUrl], { encoding: 'utf8', timeout: 180000 });
  assert.equal(download.status, 0, download.stderr);
  washBytes = await readFile(wash);
}
assert.equal(digest(washBytes), releaseHash, 'wash binary must match the official 2.11.0 release digest');
if (!process.env.NODE_COMPAT_WASH) await chmod(wash, 0o755);
const version = spawnSync(wash, ['--version'], { encoding: 'utf8', timeout: 30000 });
assert.equal(version.status, 0, version.stderr);
assert.equal(version.stdout.trim(), 'wash 2.11.0');
const componentBytes = await readFile(componentPath);
const componentHash = digest(componentBytes);
const audit = JSON.parse(await readFile(auditPath, 'utf8'));
const coreExpectations = validateCoreExpectations(audit.coreExpectations);
// The independent component builder audits WIT and the native engine provenance.
// Check the artifact hash again here before the host receives those same bytes.
assert.equal(audit.componentSha256, componentHash, 'HTTP component must match its audit');
assert(Array.isArray(audit.emittedImports), 'audit must record emitted imports');
const runtimeEntropy = audit.entropyPolicy === 'runtime-only';
const allowedImports = new Set([
  'wasi:http/types@0.2.10',
  'wasi:clocks/monotonic-clock@0.2.10',
  'wasi:io/error@0.2.10',
  'wasi:io/streams@0.2.10',
  'wasi:io/poll@0.2.10',
  ...(runtimeEntropy ? ['wasi:random/random@0.2.10'] : []),
]);
assert.deepEqual(audit.emittedImports.filter(id => id.startsWith('wasi:random/')), runtimeEntropy ? ['wasi:random/random@0.2.10'] : []);
for (const name of audit.emittedImports) assert(allowedImports.has(name), `unselected host interface: ${name}`);
assert(audit.emittedImports.includes('wasi:http/types@0.2.10'), 'HTTP component types interface');
// HTTP types name duration from monotonic-clock. The component builder verifies
// this nominal type dependency imports no callable clock function.
assert.equal(audit.clockDependency?.typeOnly, true, 'clock dependency must be structurally type-only');
assert.deepEqual(audit.clockDependency.callableImports, []);
assert.deepEqual(audit.clockDependency.coreClockImports, []);
// Independently ask the released host CLI to inspect the very same component.
const inspectionArgs = ['--output', 'json', 'inspect', componentPath];
const inspectionProcess = spawnSync(wash, inspectionArgs, { encoding: 'utf8', timeout: 30000 });
assert.equal(inspectionProcess.status, 0, inspectionProcess.stderr);
const inspection = JSON.parse(inspectionProcess.stdout);
assert.equal(inspection.success, true);
const inspectedWit = inspection.data.wit;
const inspectedImports = [...inspectedWit.matchAll(/^\s*import\s+([^;\s]+);/gm)].map(match => match[1]).sort();
const inspectedExports = [...inspectedWit.matchAll(/^\s*export\s+([^;\s]+);/gm)].map(match => match[1]).sort();
assert.deepEqual(inspectedImports, [...audit.emittedImports].sort());
assert.deepEqual(inspectedExports, ['wasi:http/incoming-handler@0.2.10']);
for (const name of inspectedImports) assert(allowedImports.has(name), `Host inspector found unselected interface: ${name}`);


await mkdir(workRoot, { recursive: true });
const runRoot = await mkdtemp(join(workRoot, 'run-'));
const project = join(runRoot, 'project');
await mkdir(join(project, '.wash'), { recursive: true });
// Deploy an immutable per-run copy of the already-audited bytes.
const deployedComponentPath = join(project, 'native-profile-http.component.wasm');
await writeFile(deployedComponentPath, componentBytes);
const portProbe = createServer();
await new Promise((resolve, reject) => portProbe.once('error', reject).listen(0, '127.0.0.1', resolve));
const port = portProbe.address().port;
await new Promise((resolve, reject) => portProbe.close(error => error ? reject(error) : resolve()));
const address = `127.0.0.1:${port}`;
const config = {
  version: '2.11.0',
  build: { command: 'test -f "$WASH_COMPONENT_PATH"', component_path: deployedComponentPath },
  dev: { address, command: 'test -f "$WASH_COMPONENT_PATH"', component_path: deployedComponentPath, service: false, volumes: [], components: [], plugins: [], host_plugins: [] },
  workload: { allowedHosts: [], allowedIpNameLookups: [], allowedHostLoopbackPorts: [], config: {} },
  wit: { skip_fetch: true },
};
const configPath = join(project, '.wash', 'config.json');
await writeFile(configPath, JSON.stringify(config, null, 2) + '\n');
const userConfig = join(runRoot, 'empty-user-config.json');
await writeFile(userConfig, '{}\n');
// Preserve the user's installation and configuration. XDG variables are used
// for their intended purpose to isolate this process's CLI caches and state.
const environment = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('WASH_') && !key.startsWith('OTEL_')));
Object.assign(environment, { XDG_CACHE_HOME: join(runRoot, 'cache'), XDG_CONFIG_HOME: join(runRoot, 'config'), XDG_DATA_HOME: join(runRoot, 'data') });
// Check the effective configuration with the host CLI before opening a socket.
const configInspectionArgs = ['--user-config', userConfig, '-C', project, '--output', 'json', 'config', 'show'];
const configInspection = spawnSync(wash, configInspectionArgs, { cwd: project, env: environment, encoding: 'utf8', timeout: 30000 });
assert.equal(configInspection.status, 0, configInspection.stderr);
const effectiveConfiguration = JSON.parse(configInspection.stdout).data;
assert.equal(effectiveConfiguration.dev.address, address);
assert.deepEqual(effectiveConfiguration.workload.allowedHosts, []);
assert.deepEqual(effectiveConfiguration.workload.allowedIpNameLookups, []);
assert.deepEqual(effectiveConfiguration.workload.allowedHostLoopbackPorts, []);
assert.deepEqual(effectiveConfiguration.dev.volumes ?? [], []);
assert.deepEqual(effectiveConfiguration.dev.plugins ?? [], []);
assert.deepEqual(effectiveConfiguration.dev.components ?? [], []);
const commandArgs = ['--user-config', userConfig, '-C', project, '--log-level', 'info', '--meters', 'duration', 'dev'];
const logPath = join(runRoot, 'wash.log');
const log = await open(logPath, 'w');
const host = spawn(wash, commandArgs, { cwd: project, env: environment, stdio: ['ignore', log.fd, log.fd] });
let exited = false;
let exitStatus;
const exitPromise = new Promise(resolve => host.once('exit', (code, signal) => { exited = true; exitStatus = { code, signal }; resolve(exitStatus); }));
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const url = `http://${address}`;
const responses = [];
let hostLog = '';
try {
  const deadline = Date.now() + 120000;
  let firstResponse;
  while (Date.now() < deadline) {
    if (exited) throw new Error(`wash exited during deployment: ${JSON.stringify(exitStatus)}\n${await readFile(logPath, 'utf8')}`);
    try {
      const response = await fetch(url + '/node-compat?request=1', { signal: AbortSignal.timeout(5000), redirect: 'error' });
      const text = await response.text();
      if (response.status === 200) { firstResponse = { response, text }; break; }
      assert([404, 503].includes(response.status), `host deployment returned ${response.status}: ${text}`);
    } catch (error) {
      if (!(error instanceof TypeError) && error.name !== 'TimeoutError') throw error;
    }
    await pause(150);
  }
  assert(firstResponse, `host deployment timed out; see ${logPath}`);
  for (let i = 0; i < 3; i++) {
    const tag = `/node-compat?request=${i + 1}`;
    const response = i === 0 ? firstResponse.response : await fetch(url + tag, { signal: AbortSignal.timeout(30000), redirect: 'error' });
    const text = i === 0 ? firstResponse.text : await response.text();
    assert.equal(response.status, 200, text);
    assert.match(response.headers.get('content-type'), /^application\/json/);
    assert.equal(response.headers.get('cache-control'), 'no-store');
    const combinedBody = JSON.parse(text);
    const body = projectCombinedHTTPBody(combinedBody,audit);
    assert.equal(body.schema, 1);
    checkEntropyHTTPReport(body, audit);
    checkFoundationsHTTPReport(body, audit);
    assert.equal(body.requestTag, tag);
    validateCoreRuntimeReport(body.native, coreExpectations);
    assert.equal(body.native.allocUnsafePolicy, coreExpectations.allocUnsafePolicy);
    assert.equal(body.native.strings, 381);
    assert.equal(body.native.bytes, 250);
    assert.equal(body.native.stubCalls, 9);
    assert.equal(body.native.stubConstructors, 9);
    assert.equal(body.native.globalBufferIdentity, true);
    assert.equal(body.native.staticCommonJS, true);
    assert.equal(body.native.unavailableMethods, 91);
    assert(body.componentInstanceRequestCount >= 1);
    for (const [field, operation] of [['unsupported', 'spawn'], ['unsupportedConstructor', 'ChildProcess']]) {
      assert.equal(body[field].code, 'ERR_SM_NODE_UNSUPPORTED');
      assert.equal(body[field].module, 'node:child_process');
      assert.equal(body[field].operation, operation);
      assert.equal(body[field].profile, coreExpectations.coreVersion);
    }
    responses.push({ request: tag, status: response.status, headers: { contentType: response.headers.get('content-type'), cacheControl: response.headers.get('cache-control') }, body: combinedBody });
  }
} finally {
  if (!exited) host.kill('SIGINT');
  await Promise.race([exitPromise, pause(8000)]);
  if (!exited) { host.kill('SIGTERM'); await Promise.race([exitPromise, pause(3000)]); }
  if (!exited) { host.kill('SIGKILL'); await exitPromise; }
  await log.close();
  hostLog = await readFile(logPath, 'utf8');
}
assert.equal(responses.length, 3);
assert.equal(digest(await readFile(deployedComponentPath)), componentHash);
assert.equal(exitStatus.code, 0, `host shutdown failed: ${JSON.stringify(exitStatus)}`);
assert.equal(exited, true, 'host process stopped after SIGINT');
checkEntropyHTTPSamples(responses, audit);
const retainedStateObserved = responses.some(result => result.body.componentInstanceRequestCount > 1);
const summary = {
  schema: 1, verifiedAtUtc: new Date().toISOString(), node: process.version, runnerSha256: digest(await readFile(fileURLToPath(import.meta.url))),
  host: { product: 'wasmCloud wash dev', version: '2.11.0', sourceCommit: 'bc5acfb8e15f7d6d199ca940354d82e590c2d5ff', embeddedWasmtimeVersion: '48.0.7', binaryPath: wash, binarySha256: releaseHash, officialBinaryUrl: releaseUrl, unmodifiedOfficialBinary: true },
  component: { path: componentPath, deployedPath: deployedComponentPath, sha256: componentHash, bytes: componentBytes.length, auditPath, emittedImports: audit.emittedImports, allowedImports: [...allowedImports] },
  componentAudit: audit,
  command: [wash, ...commandArgs], configPath, configuration: config, effectiveConfiguration, configInspectionCommand: [wash, ...configInspectionArgs],
  hostInspection: { command: [wash, ...inspectionArgs], success: true, emittedImports: inspectedImports, emittedExports: inspectedExports, emittedWit: inspectedWit },
  isolation: { address, publicListener: false, userConfigOverridden: true, globalInstallationModified: false, isolatedXdgDirectories: true, customHostPlugins: [], sidecars: [], dockerUsed: false, natsUsed: false, outgoingHostAllowlist: [], ipNameLookupAllowlist: [], hostLoopbackPortAllowlist: [], volumes: [] },
  responses, retainedStateObserved,
  readinessProtocol: 'HTTP 200 and validated application JSON, independent of optional CLI log output',
  process: { pid: host.pid, shutdown: 'SIGINT followed by exit code 0', exitStatus, stopped: exited, logPath, deploymentLogExcerpt: hostLog.split('\n').filter(line => /development session|building and deploying|listening for HTTP|Stopping|workload started|workload stopped/.test(line)) },
  limitations: ['This is the released wasmCloud local development host, not a Kubernetes/NATS cluster deployment.', 'Three HTTP requests do not by themselves establish component instance reuse; counters are recorded.', `The monotonic-clock interface is a nominal duration type dependency, with no clock functions; no outgoing networking, filesystem, DNS, sockets or TLS exercised. Secure entropy ${audit.entropyIntegrationFixture ? 'fixture exercised under '+audit.entropyPolicy : 'behavior not exercised'}.`],
};
await writeFile(join(runRoot, 'host-results.json'), JSON.stringify(summary, null, 2) + '\n');
const resultPath = resolve(process.env.NODE_COMPAT_WASMCLOUD_RESULTS ?? join(here, 'host-results.json'));
await writeFile(resultPath, JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify({ resultPath, address, hostVersion: version.stdout.trim(), requestsPassed: responses.length, retainedStateObserved, componentSha256: componentHash, hostBinarySha256: releaseHash, stopped: exited }, null, 2));
