// Official wash dev, isolated config/volumes. Real C component; not Next/SM.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createServer} from 'node:net';
import {spawn, spawnSync} from 'node:child_process';
import {mkdir, readFile, writeFile, chmod, open} from 'node:fs/promises';
import {resolve, join} from 'node:path';
const wash = '/private/tmp/starling-node-compat/wasmcloud/bin/wash-2.11.0-aarch64-apple-darwin';
const output = resolve(process.argv[2]), build = resolve(process.argv[3]);
assert.equal(process.version, 'v22.14.0');
assert(output.startsWith('/private/tmp/starling-node-compat/deployment-host-'));
await mkdir(output, {mode: 0o700});
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(wash)), '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954');
const audit = JSON.parse(await readFile(join(build, 'component-audit.json'), 'utf8'));
assert.equal(hash(await readFile(audit.component.path)), '32830d393ceccc7aaf7f399bd6816ab54928cc240db9b228352b3f16d2f1d720');
const app = join(output, 'app'), cache = join(output, 'cache'), project = join(output, 'project');
await mkdir(app); await mkdir(cache); await mkdir(join(project, '.wash'), {recursive: true});
await writeFile(join(app, 'message.txt'), 'app-readable\n');
await chmod(join(app, 'message.txt'), 0o444); await chmod(app, 0o555);
const probe = createServer(); await new Promise(resolve => probe.listen(0, '127.0.0.1', resolve));
const port = probe.address().port; await new Promise(resolve => probe.close(resolve));
const address = '127.0.0.1:' + port;
const configuration = {
  version: '2.11.0',
  build: {command: 'test -f "$WASH_COMPONENT_PATH"', component_path: audit.component.path},
  dev: {address, command: 'test -f "$WASH_COMPONENT_PATH"', component_path: audit.component.path,
    service: false, components: [], plugins: [], host_plugins: [], volumes: [
      {host_path: app, guest_path: '/app'}, {host_path: cache, guest_path: '/cache'},
    ]},
  workload: {allowedHosts: [], allowedIpNameLookups: [], allowedHostLoopbackPorts: [], config: {},
    environment: {config: {STARLING_NEXT_PROBE: 'capabilities-v1'}}},
  wit: {skip_fetch: true},
};
await writeFile(join(project, '.wash/config.json'), JSON.stringify(configuration, null, 2) + '\n');
const userConfig = join(output, 'empty-user-config.json'); await writeFile(userConfig, '{}\n');
const env = {...process.env, XDG_CACHE_HOME: join(output, 'xdg-cache'), XDG_CONFIG_HOME: join(output, 'xdg-config'), XDG_DATA_HOME: join(output, 'xdg-data')};
const configArgs = ['--user-config', userConfig, '-C', project, '--output', 'json', 'config', 'show'];
const inspected = spawnSync(wash, configArgs, {cwd: project, env, encoding: 'utf8', timeout: 30000});
await writeFile(join(output, 'config-show.stdout.json'), inspected.stdout);
await writeFile(join(output, 'config-show.stderr.txt'), inspected.stderr);
assert.equal(inspected.status, 0, inspected.stderr);
const effective = JSON.parse(inspected.stdout).data;
assert.deepEqual(effective.dev.volumes, configuration.dev.volumes);
for (const field of ['allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts']) assert.deepEqual(effective.workload[field], []);
assert.deepEqual(effective.workload.environment.config, configuration.workload.environment.config);
const args = ['--user-config', userConfig, '-C', project, '--log-level', 'info', '--meters', 'duration', 'dev'];
const result = {schemaVersion: 1, suite: 'ACTUAL_WASMCLOUD_STANDARD_WASI_DEPLOYMENT_PROBE_V1',
  component: audit.component, imports: audit.imports, exports: audit.exports,
  command: [wash, ...args], effectiveConfiguration: effective,
  responses: [], readinessFailures: [], errors: [], realComponentExecuted: false,
  starlingMonkeyExecuted: false, nextExecuted: false, forcedCleanup: false,
  limitations: ['wash dev main component is configured with UNSET_LIMIT/ephemeral policy; warm-instance deployment is a separate unexecuted gate.',
    'Read-only app uses owned Unix permissions; no per-mount narrowed WASI rights claimed.']};
const save = () => writeFile(join(output, 'result.json'), JSON.stringify(result, null, 2) + '\n');
await save();
const log = await open(join(output, 'wash.log'), 'wx');
const host = spawn(wash, args, {cwd: project, env, stdio: ['ignore', log.fd, log.fd]});
let exited = false, exitStatus;
const exit = new Promise(resolve => host.once('exit', (code, signal) => { exited = true; exitStatus = {code, signal}; resolve(); }));
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
try {
  const origin = 'http://' + address; result.origin = origin;
  const deadline = Date.now() + 60000;
  while (result.responses.length < 3 && Date.now() < deadline) {
    if (exited) throw new Error('wash exited before all responses: ' + await readFile(join(output, 'wash.log'), 'utf8'));
    try {
      const response = await fetch(origin + '/probe?request=' + result.responses.length, {headers: {connection: 'close'}, signal: AbortSignal.timeout(5000)});
      const text = await response.text();
      if (response.status !== 200) { result.readinessFailures.push({status: response.status, text}); await pause(100); continue; }
      const body = JSON.parse(text);
      await writeFile(join(output, 'response-' + result.responses.length + '.json'), text);
      result.responses.push({status: response.status, body}); result.realComponentExecuted = true; await save();
    } catch (error) {
      result.readinessFailures.push({name: error.name, message: error.message}); await pause(100);
    }
  }
  assert.equal(result.responses.length, 3, 'did not receive three complete component responses');
  for (const {body} of result.responses) {
    assert.equal(body.probe, 'standard-wasi-deployment-v1'); assert.equal(body.environmentMarker, 'capabilities-v1');
    assert(BigInt(body.monotonicAfter) > BigInt(body.monotonicBefore));
    assert(body.wallSeconds > 1700000000 && body.wallNanoseconds < 1000000000); assert.match(body.randomHex, /^[0-9a-f]{16}$/);
    const app = body.preopens.find(row => row.name === '/app'), cache = body.preopens.find(row => row.name === '/cache');
    assert(app && cache); assert.equal(app.readFixture, true); assert.equal(app.createAllowed, false);
    for (const key of ['create', 'write', 'read', 'link', 'rename', 'unlink']) assert.equal(cache[key], true, key);
    assert.equal(cache.secondLink, false); assert.equal(cache.secondLinkError, 7);
  }
  assert.deepEqual(result.responses.map(row => row.body.counter), [1, 1, 1]);
  assert.equal(new Set(result.responses.map(row => row.body.randomHex)).size, 3);
  result.passed = true;
} catch (error) { result.passed = false; result.errors.push({name: error.name, message: error.message, stack: error.stack}); }
finally {
  if (!exited) host.kill('SIGINT'); await Promise.race([exit, pause(5000)]);
  if (!exited) { result.forcedCleanup = true; host.kill('SIGKILL'); await exit; }
  result.process = exitStatus; await log.close(); await chmod(app, 0o755); await save();
}
assert.equal(result.forcedCleanup, false); assert.deepEqual(result.process, {code: 0, signal: null});
console.log(JSON.stringify({passed: result.passed, counts: result.responses.map(row => row.body.counter),
  realComponentExecuted: result.realComponentExecuted, starlingMonkeyExecuted: false, nextExecuted: false}));
if (!result.passed) process.exitCode = 1;
