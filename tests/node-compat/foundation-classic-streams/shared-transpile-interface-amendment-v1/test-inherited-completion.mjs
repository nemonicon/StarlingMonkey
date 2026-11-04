// Tiny owned text/filesystem tests only. No engine, packager, guest or host tool.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, writeFile, symlink, lstat } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { trackedWriter, publishCompletion } from './proposed/harness/completion.mjs';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const HERE = dirname(fileURLToPath(import.meta.url));
const root = await mkdtemp('/tmp/starling-node-compat/classic-completion-host-v1-');
const cases = [];
const missing = async path => assert.rejects(lstat(path), error => error.code === 'ENOENT');
const report = { status: 'OWNED_TINY_TEXT_HOST_CHECK', variant: 'host-filesystem-only' };
async function test(name, fn) { await fn(); cases.push(name); }
async function dir(name) { const path = join(root, name); await mkdir(path); return path; }

await test('reject outside output before writing', async () => {
  const output = await dir('outside'), tracked = trackedWriter(output), path = join(root, 'not-owned.txt');
  await assert.rejects(tracked.write(path, 'unwritten', { flag: 'wx' })); await missing(path);
});
await test('reject nonexclusive output mode', async () => {
  const output = await dir('nonexclusive'), tracked = trackedWriter(output), path = join(output, 'fixture.txt');
  await assert.rejects(tracked.write(path, 'unwritten', { flag: 'w' })); await missing(path);
});
await test('reject parent symlink before writing', async () => {
  const output = await dir('parent-link'), elsewhere = await dir('own-link-target');
  await symlink(elsewhere, join(output, 'link'));
  await assert.rejects(trackedWriter(output).write(join(output, 'link/fixture.txt'), 'unwritten', { flag: 'wx' }));
  await missing(join(elsewhere, 'fixture.txt'));
});
await test('failed final input recheck publishes no success files', async () => {
  const output = await dir('failed-recheck'), tracked = trackedWriter(output);
  await tracked.write(join(output, 'fixture.txt'), 'preserved partial output', { flag: 'wx' });
  async function controlledFlow() {
    try { /* semantic gate complete */ } finally { throw new Error('owned recheck failure'); }
    await publishCompletion({ output, report, paths: tracked.paths });
  }
  await assert.rejects(controlledFlow(), /owned recheck failure/);
  await missing(join(output, 'results.json')); await missing(join(output, 'completion.json'));
});
let ordinary;
await test('normal publication hashes actual writes and results', async () => {
  const output = await dir('normal'), tracked = trackedWriter(output);
  // These bytes are deliberately plain text, not executable Wasm artifacts.
  for (const name of ['fixture.component.wasm', 'fixture.core.wasm', 'fixture.js'])
    await tracked.write(join(output, name), 'owned text only: ' + name, { flag: 'wx' });
  const seal = await publishCompletion({ output, report, paths: tracked.paths });
  assert.equal(seal.files.length, 4);
  for (const row of seal.files) {
    const bytes = await readFile(join(output, row.path));
    assert.equal(hash(bytes), row.sha256); assert.equal(bytes.length, row.bytes);
  }
  assert.deepEqual(seal.componentFiles, ['fixture.component.wasm']);
  assert.deepEqual(seal.generatedWasmFiles, ['fixture.core.wasm']);
  assert.deepEqual(seal.generatedJavaScriptFiles, ['fixture.js']);
  assert.deepEqual(JSON.parse(await readFile(join(output, 'results.json'))), report);
  ordinary = { output, tracked, seal };
});
await test('completion requires independent exit zero and has no self hash', async () => {
  assert.equal(ordinary.seal.requiresIndependentTerminalExitCodeZero, true);
  assert.equal(ordinary.seal.terminalExitCodeObservedByThisHelper, null);
  assert.equal(ordinary.seal.runtimeAcceptanceClaim, false);
  assert(!ordinary.seal.files.some(row => row.path === 'completion.json'));
});
await test('existing completion is not overwritten', async () => {
  const path = join(ordinary.output, 'completion.json'), before = await readFile(path);
  await assert.rejects(publishCompletion({ output: ordinary.output, report, paths: ordinary.tracked.paths }));
  assert.deepEqual(await readFile(path), before);
});
await test('disabled shape seals text only and no component or core', async () => {
  const output = await dir('disabled'), tracked = trackedWriter(output);
  for (const name of ['disabled.mjs', 'disabled.cjs']) await tracked.write(join(output, name), 'owned fixture', { flag: 'wx' });
  const seal = await publishCompletion({ output, report, paths: tracked.paths });
  assert.equal(seal.files.length, 3); assert.deepEqual(seal.componentFiles, []); assert.deepEqual(seal.generatedWasmFiles, []);
});
await test('missing tracked file prevents success publication', async () => {
  const output = await dir('missing-file');
  await assert.rejects(publishCompletion({ output, report, paths: new Set([join(output, 'absent.txt')]) }));
  await missing(join(output, 'results.json')); await missing(join(output, 'completion.json'));
});
await test('symlink tracked file prevents success publication', async () => {
  const output = await dir('file-link'), ownTarget = join(root, 'own-target.txt');
  await writeFile(ownTarget, 'owned target', { flag: 'wx' }); await symlink(ownTarget, join(output, 'alias.txt'));
  await assert.rejects(publishCompletion({ output, report, paths: new Set([join(output, 'alias.txt')]) }));
  await missing(join(output, 'results.json')); await missing(join(output, 'completion.json'));
});
await test('existing results cannot be overwritten or gain completion', async () => {
  const output = await dir('old-results'), path = join(output, 'results.json');
  await writeFile(path, 'owned prior evidence', { flag: 'wx' });
  await assert.rejects(publishCompletion({ output, report, paths: new Set() }));
  assert.equal(await readFile(path, 'utf8'), 'owned prior evidence'); await missing(join(output, 'completion.json'));
});
await test('reserved report path cannot enter tracked writer set', async () => {
  const output = await dir('reserved-result');
  await assert.rejects(publishCompletion({ output, report, paths: new Set([join(output, 'results.json')]) }));
  await missing(join(output, 'results.json')); await missing(join(output, 'completion.json'));
});
await test('proposed driver publishes only after final recheck', async () => {
  const source = await readFile(join(HERE, 'proposed/harness/component-driver.mjs'), 'utf8');
  assert(source.indexOf('await publishCompletion(') > source.lastIndexOf('finally { await admission.recheck(); }'));
  assert(!source.includes("writeOutput(join(output,'results.json')"));
  assert(source.includes("await writeOutput(caughtComponentPath,caught.component,{flag:'wx'});"));
});
const result = {
  schemaVersion: 1, state: 'SOURCE_AND_OWNED_TEXT_COMPLETION_CHECKS_PASSED',
  passed: cases.length, failures: 0, cases, output: root,
  helperSha256: hash(await readFile(join(HERE, 'proposed/harness/completion.mjs'))),
  driverSha256: hash(await readFile(join(HERE, 'proposed/harness/component-driver.mjs'))),
  sourceScopesOnly: true, fixtureBytesArePlainTextNotWasm: true,
  enginePinsUsed: false, nativeOrGuestOrHostToolExecuted: false,
};
await writeFile(join(root, 'host-test-results.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(result));
