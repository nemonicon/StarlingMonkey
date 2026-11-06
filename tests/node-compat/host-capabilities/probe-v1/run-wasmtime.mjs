// Run the exact small C component on stock Wasmtime. No StarlingMonkey/Next.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {mkdir, readFile, writeFile, chmod, open} from 'node:fs/promises';
import {resolve, join} from 'node:path';
const executable = '/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime';
const output = resolve(process.argv[2]);
const build = resolve(process.argv[3]);
assert.equal(process.version, 'v22.14.0');
assert(output.startsWith('/private/tmp/starling-node-compat/deployment-host-'));
await mkdir(output, {mode: 0o700});
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const audit = JSON.parse(await readFile(join(build, 'component-audit.json'), 'utf8'));
assert.equal(hash(await readFile(audit.component.path)), audit.component.sha256);
assert.equal(audit.component.sha256, '32830d393ceccc7aaf7f399bd6816ab54928cc240db9b228352b3f16d2f1d720');
assert.equal(hash(await readFile(executable)), 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
const app = join(output, 'app'), cache = join(output, 'cache');
await mkdir(app); await mkdir(cache);
await writeFile(join(app, 'message.txt'), 'app-readable\n');
await chmod(join(app, 'message.txt'), 0o444); await chmod(app, 0o555);
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const result = {schemaVersion: 1, suite: 'ACTUAL_WASMTIME_STANDARD_WASI_DEPLOYMENT_PROBE_V1',
  component: audit.component, imports: audit.imports, exports: audit.exports, modes: [],
  realComponentExecuted: false, starlingMonkeyExecuted: false, nextExecuted: false, errors: []};
const save = () => writeFile(join(output, 'result.json'), JSON.stringify(result, null, 2) + '\n');
await save();
try {
  for (const reuse of [false, true]) {
    const id = reuse ? 'explicit-reuse' : 'default-lifetime';
    const args = ['serve', '--addr', '127.0.0.1:0', '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n',
      '--env', 'STARLING_NEXT_PROBE=capabilities-v1', '--dir', app + '::/app', '--dir', cache + '::/cache',
      ...(reuse ? ['--max-instance-reuse-count', '32', '--idle-instance-timeout', '60s'] : []), audit.component.path];
    const logPath = join(output, id + '.log'); const log = await open(logPath, 'wx');
    const host = spawn(executable, args, {stdio: ['ignore', log.fd, log.fd], env: {...process.env,
      XDG_CACHE_HOME: join(output, 'xdg-cache'), XDG_CONFIG_HOME: join(output, 'xdg-config'), XDG_DATA_HOME: join(output, 'xdg-data')}});
    let exited = false, exitStatus;
    const exit = new Promise(resolve => host.once('exit', (code, signal) => { exited = true; exitStatus = {code, signal}; resolve(); }));
    const row = {id, command: [executable, ...args], log: logPath, responses: [], forcedCleanup: false};
    result.modes.push(row); await save();
    try {
      let origin;
      const deadline = Date.now() + 30000;
      while (Date.now() < deadline) {
        const text = await readFile(logPath, 'utf8');
        if (exited) throw new Error('Wasmtime exited before ready: ' + text);
        origin = /Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];
        if (origin) break;
        await pause(50);
      }
      assert(origin, 'Wasmtime did not report readiness'); row.origin = origin;
      for (let i = 0; i < 3; i++) {
        const response = await fetch(origin + '/probe?request=' + i, {headers: {connection: 'close'}, signal: AbortSignal.timeout(10000)});
        const text = await response.text();
        await writeFile(join(output, id + '-' + i + '.json'), text);
        const body = JSON.parse(text);
        row.responses.push({status: response.status, body}); await save();
        result.realComponentExecuted = true;
        assert.equal(response.status, 200);
        assert.equal(body.probe, 'standard-wasi-deployment-v1');
        assert.equal(body.environmentMarker, 'capabilities-v1');
        assert(BigInt(body.monotonicAfter) > BigInt(body.monotonicBefore));
        assert(body.wallSeconds > 1700000000 && body.wallNanoseconds < 1000000000);
        assert.match(body.randomHex, /^[0-9a-f]{16}$/);
        const app = body.preopens.find(row => row.name === '/app');
        const cache = body.preopens.find(row => row.name === '/cache');
        assert(app && cache);
        assert.equal(app.readFixture, true); assert.equal(app.createAllowed, false);
        assert([0, 31, 33].includes(app.createError));
        for (const key of ['create', 'write', 'read', 'link', 'rename', 'unlink']) assert.equal(cache[key], true, key);
        assert.equal(cache.secondLink, false); assert.equal(cache.secondLinkError, 7);
      }
      assert.deepEqual(row.responses.map(row => row.body.counter), reuse ? [1, 2, 3] : [1, 1, 1]);
      assert.equal(new Set(row.responses.map(row => row.body.randomHex)).size, 3);
      row.passed = true;
    } finally {
      if (!exited) host.kill('SIGINT');
      await Promise.race([exit, pause(5000)]);
      if (!exited) { row.forcedCleanup = true; host.kill('SIGKILL'); await exit; }
      row.process = exitStatus;
      await log.close(); await save();
    }
    assert.equal(row.forcedCleanup, false);
    assert.deepEqual(row.process, {code: 0, signal: null});
  }
  result.passed = true;
} catch (error) {
  result.errors.push({name: error.name, message: error.message, stack: error.stack}); result.passed = false;
} finally { await chmod(app, 0o755); await save(); }
console.log(JSON.stringify({passed: result.passed, counts: result.modes.map(row => ({id: row.id, counts: row.responses.map(row => row.body.counter)})),
  realComponentExecuted: result.realComponentExecuted, starlingMonkeyExecuted: false, nextExecuted: false}));
if (!result.passed) process.exitCode = 1;
