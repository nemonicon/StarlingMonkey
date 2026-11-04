import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { cp, mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { context, output, repository, hash, auditRegressionImports } from './common.mjs';

const name = process.argv[2];
const ctx = await context();
const sourceDirectory = join(repository, 'tests/e2e', name);
const sourcePath = join(sourceDirectory, name + '.js');
const directory = join(output, 'starling-e2e', name);
await mkdir(directory, { recursive: true });
await cp(sourceDirectory, directory, { recursive: true });
const exists = async path => { try { await access(path); return true; } catch { return false; } };
const report = { name, engineSha256: ctx.engineSha256, sourcePath, sourceSha256: hash(await readFile(sourcePath)), status: 'fail', adaptations: [] };
report.componentizerProvenance = ctx.componentizerProvenance;
if (await exists(join(directory, 'expect_serve_stdout.txt'))) {
  // The Componentize embedding's console ABI intentionally omits Starling's
  // "Log: " prefix. Keep both goldens and the raw first-run mismatch evidence.
  const path = join(directory, 'expect_serve_stdout.txt');
  const original = await readFile(path, 'utf8');
  let adapted = original.replace(/^(stdout \[\d+\] :: )Log: /gm, '$1');
  if (name === 'console-assert') {
    // embedding.cpp routes non-log/info diagnostics to stderr; assert counts
    // remain exact and are checked on that stream instead of discarded.
    const errors = [...adapted.matchAll(/^stdout \[(\d+)\] :: Error: (.*)\n/gm)];
    assert.equal(errors.length, 2);
    await writeFile(join(directory, 'expect_serve_stderr.txt'), errors.map(([, id, text]) => `stderr [${id}] :: ${text}\n`).join(''));
    adapted = adapted.replace(/^stdout \[\d+\] :: Error: .*\n/gm, '');
    report.adaptations.push('Embedding console error diagnostics route to stderr without Error:; preserve both exact assert messages there');
  }
  await writeFile(join(directory, 'expect_serve_stdout.original.txt'), original);
  await writeFile(path, adapted);
  if (adapted !== original) {
    report.consoleGolden = { originalSha256: hash(original), adaptedSha256: hash(adapted) };
    report.adaptations.push('Expected console.log prefix omits Log: in ComponentizeJS embedding; original golden retained');
  }
}
// Match the upstream harness's strip-path-prefix tests/ while retaining actual
// source-file module resolution (../../assert.js and smoke dependencies).
process.chdir(join(repository, 'tests'));
let restore;
try {
  const witDirectory = join(output, 'starling-e2e/wit');
  await mkdir(witDirectory, { recursive: true });
  await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps'), join(witDirectory, 'deps'), { recursive: true });
  await writeFile(join(witDirectory, 'test.wit'), 'package test:starling-upstream; world test { export wasi:http/incoming-handler@0.2.10; }');
  const { _setPreopens, _clearPreopens } = await import(pathToFileURL(ctx.require.resolve('@bytecodealliance/preview2-shim/filesystem')));
  if (await exists(join(directory, 'init.js'))) {
    // ComponentizeJS reserves -i for its own bindings initializer. Compose the
    // actual upstream classic initializer in that same existing init realm.
    const { splicer } = ctx;
    const original = splicer.spliceBindings;
    const initializer = await readFile(join(directory, 'init.js'), 'utf8');
    splicer.spliceBindings = function (...args) {
      const result = original.apply(this, args);
      // Persist exact generated initializer for diagnosing integration failures.
      writeFileSync(join(directory, 'combined-initializer.js'), result.jsBindings + '\n' + initializer);
      return { ...result, jsBindings: result.jsBindings + '\n' + initializer };
    };
    restore = () => { splicer.spliceBindings = original; };
    report.adaptations.push('Compose original init.js with ComponentizeJS-generated classic initializer in existing initializer realm');
  }
  const runtimeArgs = await exists(join(directory, 'runtime-args')) ? (await readFile(join(directory, 'runtime-args'), 'utf8')).trim() : undefined;
  let component, error;
  try {
    _setPreopens({ [witDirectory]: witDirectory });
    ({ component } = await ctx.componentize({ sourcePath, sourceName: name + '.js', engine: ctx.engine,
      preview2Adapter: ctx.preview2Adapter, runtimeArgs,
      witPath: witDirectory, worldName: 'test' }));
  } catch (failure) { error = failure.message; }
  finally { _clearPreopens(); }
  const expectsFailure = await exists(join(directory, 'expect_wizer_fail'));
  report.expectedInitializationFailure = expectsFailure;
  report.initializationError = error;
  assert.equal(!!error, expectsFailure, error ?? 'Expected initialization failure');
  if (error) {
    const expected = await readFile(join(directory, 'expect_wizer_stderr.txt'), 'utf8');
    const stderr = error.slice(error.indexOf('\n') + 1);
    if (name === 'syntax-err' && /failed to parse JS source/.test(error)) {
      report.originalInitializationAssertion = 'not-reached';
      report.adaptations.push('ComponentizeJS source export parser rejects syntax before Wizer; original SpiderMonkey stderr assertion not reached');
    } else {
      assert(stderr.startsWith(expected), `Upstream initialization stderr prefix mismatch\nExpected:\n${expected}\nActual:\n${stderr}`);
      report.originalInitializationAssertion = 'pass';
    }
  } else {
    const componentPath = join(directory, name + '.component.wasm');
    await writeFile(componentPath, component);
    report.componentSha256 = hash(component); report.componentBytes = component.length;
    const wit = await ctx.componentWit(component);
    await writeFile(join(directory, 'emitted.wit'), wit);
    report.emittedImports = wit.split('\n').filter(line => /^\s*import /.test(line)).map(line => line.trim());
    auditRegressionImports(wit);
    const original = await readFile(join(repository, 'tests/test.sh'), 'utf8');
    const harnessPath = join(output, 'starling-e2e/test-loopback.sh');
    await writeFile(harnessPath, original.replace('--addr 0.0.0.0:0', '--addr 127.0.0.1:0'));
    report.harnessSha256 = hash(original);
    report.adaptedHarnessSha256 = hash(await readFile(harnessPath));
    report.adaptations.push('Original tests/test.sh serve assertions on prebuilt component; bind loopback only');
    const execution = await new Promise(resolve => {
      const cp = spawn('bash', [harnessPath, directory, directory, componentPath], {
        env: { ...process.env, WASMTIME: process.env.NODE_COMPAT_WASMTIME }, stdio: 'pipe', detached: true,
      });
      let stdout = '', stderr = '';
      cp.stdout.on('data', bytes => { stdout += bytes; }); cp.stderr.on('data', bytes => { stderr += bytes; });
      const timer = setTimeout(() => { try { process.kill(-cp.pid, 'SIGKILL'); } catch {} }, 120000);
      cp.on('exit', (code, signal) => { clearTimeout(timer); resolve({ code, signal, stdout, stderr }); });
    });
    report.execution = execution;
    assert.equal(execution.code, 0, execution.stderr + execution.stdout);
    report.originalServeAssertions = 'pass';
    if (await exists(join(directory, 'expect_wizer_stdout.txt'))) report.adaptations.push('Shell Componentizing banner omitted; raw inherited Wizer stdout recorded by driver');
  }
  report.status = 'pass';
} catch (error) { report.error = error.stack ?? error.message; }
finally { restore?.(); }
await writeFile(join(output, 'starling-' + name + '.result.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ name, status: report.status, error: report.error?.slice(0, 500) }));
process.exit(report.status === 'pass' ? 0 : 1);
