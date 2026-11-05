// Host toy-module lifecycle/interop checks only; no framework or Wasm execution.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
const HERE = dirname(fileURLToPath(import.meta.url)), require = createRequire('/private/tmp/starling-node-compat/toolchain/package.json');
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
assert.equal(process.version, 'v22.14.0');
const root = join(HERE, 'lifecycle-evidence'); await mkdir(root);
const cases = [
  { name: 'conditional-lazy-once', files: {
    'entry.mjs': "import load from './pkg.cjs';export function observe(){const before=globalThis.__auditCount??0;const skipped=load(false);const afterSkip=globalThis.__auditCount??0;const a=load(true);const afterLoad=globalThis.__auditCount;const b=load(true);return {before,skipped,afterSkip,afterLoad,afterAgain:globalThis.__auditCount,same:a===b};}",
    'pkg.cjs': "module.exports=function(flag){if(flag)return require('./lazy.cjs');return 'skip';};",
    'lazy.cjs': "globalThis.__auditCount=(globalThis.__auditCount??0)+1;module.exports={id:globalThis.__auditCount};",
  } },
  { name: 'cyclic-partial-exports', files: {
    'entry.mjs': "import a from './a.cjs';import b from './b.cjs';export function observe(){return {a,b};}",
    'a.cjs': "exports.name='a';exports.b=require('./b.cjs').name;",
    'b.cjs': "exports.name='b';exports.a=require('./a.cjs').name;",
  } },
  { name: 'mutable-cjs-named-import', files: {
    'entry.mjs': "import {number,change}from './pkg.cjs';export function observe(){const before=number;change();return {before,after:number};}",
    'pkg.cjs': 'exports.number=1;exports.change=function(){exports.number=2;};',
  } },
];
const results = [];
for (const item of cases) {
  const folder = join(root, item.name); await mkdir(folder);
  for (const [name, source] of Object.entries({ 'package.json': '{"type":"module"}', ...item.files })) await writeFile(join(folder, name), source + '\n', { flag: 'wx' });
  const build = await rolldown({ input: join(folder, 'entry.mjs'), platform: 'neutral', treeshake: false });
  let output; try { output = await build.generate({ format: 'esm', codeSplitting: false }); } finally { await build.close(); }
  assert.equal(output.output.length, 1); await writeFile(join(folder, 'bundle.mjs'), output.output[0].code, { flag: 'wx' });
  const result = { name: item.name, nativeEngineExecuted: false, frameworkPackageExecuted: false, imports: output.output[0].imports, observations: {} };
  for (const [role, name] of [['rawNode', 'entry.mjs'], ['bundledNode', 'bundle.mjs']]) {
    const script = `import{observe}from ${JSON.stringify(pathToFileURL(join(folder, name)).href)};process.stdout.write(JSON.stringify(observe())+'\\n');`;
    const args = ['--input-type=module', '--eval', script], child = spawnSync(process.execPath, args, { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
    await writeFile(join(folder, role + '.stdout.txt'), child.stdout ?? '', { flag: 'wx' }); await writeFile(join(folder, role + '.stderr.txt'), child.stderr ?? '', { flag: 'wx' });
    result.observations[role] = { executable: process.execPath, args, status: child.status, signal: child.signal, error: child.error?.message ?? null,
      ...(child.status === 0 ? { value: JSON.parse(child.stdout) } : {}) };
  }
  result.sameStructuredValue = JSON.stringify(result.observations.rawNode.value) === JSON.stringify(result.observations.bundledNode.value);
  await writeFile(join(folder, 'result.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' }); results.push(result);
}
await writeFile(join(root, 'results.json'), JSON.stringify({ schemaVersion: 1, node: process.version, cases: results, hostToyModulesOnly: true, nativeEngineExecuted: false, guestExecuted: false }, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify(results.map(x => ({ name: x.name, sameStructuredValue: x.sameStructuredValue, observations: Object.fromEntries(Object.entries(x.observations).map(([k, v]) => [k, { status: v.status, value: v.value }])) })), null, 2) + '\n');
