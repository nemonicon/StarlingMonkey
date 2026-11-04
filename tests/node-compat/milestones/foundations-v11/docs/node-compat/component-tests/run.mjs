// Real-component tests; external dependencies/binaries/output stay outside the repository.
// NODE_COMPAT_TOOLCHAIN points to npm install --prefix output.
// NODE_COMPAT_WASMTIME points to the exact Wasmtime 42.0.1 executable.
// NODE_COMPAT_ENGINE optionally selects a rebuilt ComponentizeJS embedding engine.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0', 'use the pinned Node differential oracle');
const here = dirname(fileURLToPath(import.meta.url));
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/toolchain');
const output = resolve(process.env.NODE_COMPAT_OUTPUT ?? '/tmp/starling-node-compat/component-output');
const wasmtime = process.env.NODE_COMPAT_WASMTIME;
assert(wasmtime, 'Set NODE_COMPAT_WASMTIME to Wasmtime 42.0.1');
const require = createRequire(join(toolchain, 'package.json'));
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
const { componentize } = await import(pathToFileURL(join(toolchain, 'node_modules/@bytecodealliance/componentize-js/src/componentize.js')));
const { transpile, componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
await mkdir(output, { recursive: true });
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); } catch (e) { if (e.code !== 'EEXIST') throw e; }
async function bundle(entry) {
  const build = await rolldown({ input: join(here, entry), platform: 'neutral', checks: { pluginTimings: false } });
  try {
    const result = await build.generate({ format: 'esm', codeSplitting: false });
    assert.equal(result.output.length, 1);
    return result.output[0].code;
  } finally { await build.close(); }
}
const opts = {
  witWorld: await readFile(join(here, 'profile.wit'), 'utf8'),
  worldName: 'profile',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'],
  ...(process.env.NODE_COMPAT_ENGINE ? { engine: process.env.NODE_COMPAT_ENGINE } : {}),
};
const source = await bundle('stub-check.mjs');
const { component } = await componentize(source, opts);
const componentPath = join(output, 'stub.component.wasm');
await writeFile(componentPath, component);
const wit = await componentWit(component);
await writeFile(join(output, 'emitted.wit'), wit);
const importLines = wit.split('\n').filter(line => /^\s*import /.test(line));
assert.deepEqual(importLines, [], 'capability-free fixture must have no component imports');
const { files } = await transpile(component, { name: 'stub' });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
for (const [name, value] of Object.entries(files)) {
  const path = join(output, name);
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, value);
}
const instance = await import(pathToFileURL(join(output, 'stub.js')));
const first = JSON.parse(await instance.run());
const second = JSON.parse(await instance.run());
assert.equal(first.calls, 1);
assert.equal(second.calls, 2);
assert.equal(first.invocationChecks, 9);
assert.equal(first.constructorChecks, 9);
const hostVersion = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(hostVersion.status, 0, hostVersion.stderr);
assert.match(hostVersion.stdout, /^wasmtime 42\.0\.1\b/);
const host = spawnSync(wasmtime, ['run', '--invoke', 'run()', componentPath], { encoding: 'utf8', timeout: 120000 });
assert.equal(host.status, 0, host.stderr || host.stdout);
// Wasmtime's WAVE string printer uses \u{...} for some Unicode code points.
// Normalize only that observed string escape before decoding our JSON report.
function decodeWaveReport(stdout) {
  const jsonString = stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g, (_, hex) => String.fromCodePoint(parseInt(hex, 16)));
  return JSON.parse(JSON.parse(jsonString));
}
const hostReport = decodeWaveReport(host.stdout);
assert.equal(hostReport.calls, 1);
assert.equal(hostReport.invocationChecks, 9);
assert.equal(hostReport.constructorChecks, 9);
let failure = '';
try { await componentize(await bundle('top-level-failure.mjs'), opts); }
catch (error) { failure = error.message; }
assert.match(failure, /node:child_process\.spawn is unavailable/);
// Exercise the facade in a second real component using the explicitly labeled
// JS reference kernel, including instances and TextDecoder created at snapshot.
const bufferBuild = await componentize(await bundle('buffer-check.mjs'), opts);
const bufferComponent = bufferBuild.component;
const bufferPath = join(output, 'buffer-facade.component.wasm');
await writeFile(bufferPath, bufferComponent);
const bufferWit = await componentWit(bufferComponent);
assert.deepEqual(bufferWit.split('\n').filter(line => /^\s*import /.test(line)), []);
const bufferTranspiled = await transpile(bufferComponent, { name: 'buffer-facade' });
for (const [name, value] of Object.entries(bufferTranspiled.files)) {
  const path = join(output, name);
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, value);
}
const bufferInstance = await import(pathToFileURL(join(output, 'buffer-facade.js')));
const bufferFirst = JSON.parse(await bufferInstance.run());
const bufferSecond = JSON.parse(await bufferInstance.run());
assert.equal(bufferFirst.calls, 1);
assert.equal(bufferSecond.calls, 2);
for (const example of bufferFirst.cases) {
  const expected = NodeBuffer.from(example.input, example.encoding);
  assert.deepEqual(example.bytes, [...expected]);
  assert.equal(example.text, expected.toString(example.encoding));
  assert.equal(example.byteLength, NodeBuffer.byteLength(example.input, example.encoding));
}
assert.equal(bufferFirst.snapshotText, NodeBuffer.from('\ufeffé😀').toString());
assert.equal(bufferFirst.malformedText, NodeBuffer.from([0xc0, 0xaf, 0xef, 0xbb, 0xbf]).toString());
const bufferHost = spawnSync(wasmtime, ['run', '--invoke', 'run()', bufferPath], { encoding: 'utf8', timeout: 120000 });
assert.equal(bufferHost.status, 0, bufferHost.stderr || bufferHost.stdout);
const bufferHostReport = decodeWaveReport(bufferHost.stdout);
assert.deepEqual(bufferHostReport, bufferFirst);
const summary = {
  engine: process.env.NODE_COMPAT_ENGINE ? resolve(process.env.NODE_COMPAT_ENGINE) : 'ComponentizeJS 0.23.0 released engine (not rebuilt checkout)',
  node: process.version,
  wasmtime: hostVersion.stdout.trim(),
  componentBytes: component.length,
  componentSha256: createHash('sha256').update(component).digest('hex'),
  emittedImports: importLines,
  emittedWit: wit,
  componentCalls: [first, second],
  wasmtimeRunStdout: host.stdout.trim(),
  topLevelFailureObserved: true,
  topLevelFailureExcerpt: failure.split('\n').filter(line => /child_process|Failed to initialize/.test(line)).slice(0, 4),
  bufferFacade: { componentBytes: bufferComponent.length, componentSha256: createHash('sha256').update(bufferComponent).digest('hex'), emittedWit: bufferWit, emittedImports: [], report: bufferFirst, repeatedCallCount: bufferSecond.calls, wasmtimeRunPassed: true },
  limitations: ['No rebuilt checkout or native Buffer kernel tested', 'No wasmCloud deployment tested', 'Snapshot state persistence tested; entropy, environment and live-handle policies remain untested'],
};
await writeFile(join(output, 'results.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
