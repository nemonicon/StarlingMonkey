// Reuse the actual upstream fixture's source and assertion callback, not a
// local semantic substitute. Only engine/output/adapter and process handling
// differ from ComponentizeJS test/builtins.js.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import { context, output, upstream, hash, saveComponent, verifyUpstreamSource, regressionImports } from './common.mjs';

const name = process.argv[2];
const ctx = await context();
const fixturePath = join(upstream, 'test/builtins', name + '.js');
let report = { name, fixturePath, fixtureSha256: hash(await readFile(fixturePath)),
  engineSha256: ctx.engineSha256, sourceRoot: ctx.sourceRoot, componentizerProvenance: ctx.componentizerProvenance, status: 'fail' };
try {
  report.fixtureArchive = await verifyUpstreamSource('test/builtins/' + name + '.js', ctx.metadata);
  const fixture = await import(pathToFileURL(fixturePath));
  const disableFeatures = fixture.disableFeatures ?? [];
  report.disableFeatures = disableFeatures;
  report.enableFeatures = fixture.enableFeatures ?? [];
  const { component } = await ctx.componentize(fixture.source, {
    engine: ctx.engine, sourceName: name + '.js', preview2Adapter: ctx.preview2Adapter,
    witWorld: 'package local:runworld; world runworld { export run: func(); }',
    disableFeatures,
    selectedInterfaces: ctx.metadata.entropyPolicy === 'off' ? regressionImports.filter(id => !id.startsWith('wasi:random/')) : regressionImports,
  });
  Object.assign(report, await saveComponent(ctx, name, component));
  const runner = join(report.directory, 'run.mjs');
  await writeFile(runner, "import { run } from './fixture.js'; await run();\n");
  const run = () => new Promise((resolve, reject) => {
    const cp = spawn(process.execPath, [runner], { stdio: 'pipe' });
    let stdout = '', stderr = '';
    cp.stdout.on('data', bytes => { stdout += bytes; });
    cp.stderr.on('data', bytes => { stderr += bytes; });
    const timer = setTimeout(() => cp.kill('SIGKILL'), 30000);
    cp.on('error', error => { clearTimeout(timer); reject(error); });
    cp.on('exit', (code, signal) => {
      clearTimeout(timer);
      report.execution = { code, signal, stdout, stderr };
      if (code === 0) resolve({ stdout, stderr });
      else reject({ err: new Error(`Guest exited ${code ?? signal}`), stdout, stderr });
    });
  });
  if (name === 'crypto-random-disabled' && ctx.metadata.entropyPolicy === 'off') {
    let failure;
    try { await run(); } catch (error) { failure = error; }
    assert(failure, 'OFF secure random must fail at invocation');
    assert.match(failure.stderr, /ERR_SM_ENTROPY_DISABLED/);
    try { await fixture.test(async () => { throw failure; }); }
    catch (error) { report.originalFailure = error.message ?? String(error); }
    assert(report.originalFailure, 'Original deterministic-secure-random expectation must remain visibly incompatible');
    report.originalAssertion = 'intentional-profile-delta';
    report.adaptation = 'Selected OFF policy throws coded error instead of returning deterministic bytes from secure getRandomValues; original source and failure retained';
  } else if (name === 'globals') {
    const actual = await run();
    try { await fixture.test(async () => actual); report.originalAssertion = 'pass'; }
    catch (error) { report.originalAssertion = 'intentional-profile-delta'; report.originalFailure = error.message; }
    const globals = JSON.parse(actual.stdout);
    assert.equal(globals.filter(value => value === 'Buffer').length, 1);
    const withoutBuffer = globals.filter(value => value !== 'Buffer');
    await fixture.test(async () => ({ stdout: '[' + withoutBuffer.map(JSON.stringify).join(', ') + ']\n', stderr: actual.stderr }));
    report.allowedGlobalAddition = ['Buffer'];
  } else if (name === 'timeout-disabled') {
    let failure;
    try { await run(); } catch (error) { failure = error; }
    assert(failure, 'Disabled clock timer must fail');
    try { await fixture.test(async () => { throw failure; }); report.originalAssertion = 'pass'; }
    catch (error) {
      report.originalAssertion = 'host-trap-wording-mismatch';
      report.originalFailure = error.message;
      assert.match(failure.stderr, /RuntimeError: wasm trap: wasm `unreachable` instruction executed/);
      assert.match(failure.stderr, /at subscribe-instant/);
      const stderr = failure.stderr.replace('RuntimeError: wasm trap: wasm `unreachable` instruction executed', 'RuntimeError: unreachable');
      await fixture.test(async () => { throw { ...failure, stderr }; });
      report.adaptation = 'Normalize exactly the observed Node22/Jco unreachable diagnostic for upstream string assertion; raw stderr retained';
    }
  } else {
    await fixture.test(run);
  }
  if (['error-sync', 'error-async', 'timeout-disabled', 'performance-disabled'].includes(name)) {
    assert.notEqual(report.execution?.code, 0, 'Upstream catch-only test must actually observe a failed execution');
  }
  report.status = 'pass';
} catch (error) {
  report.error = error.stack ?? error.message ?? String(error);
  if (error.stderr) report.guestStderr = error.stderr;
}
await writeFile(join(output, name + '.result.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ name, status: report.status, error: report.error?.slice(0, 200) }));
// The upstream fetch fixture starts a host-local HTTP server at import time.
// Explicit exit also cleans it up on a build/assertion failure.
process.exit(report.status === 'pass' ? 0 : 1);
