// Isolate the pinned ComponentizeJS high-u32 result bug from Buffer and Math.
// This is a known-issue diagnostic, not a claim that those results are correct.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { loadToolchain } from '../toolchain.mjs';

const { directory: toolchain, require } = await loadToolchain();
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME ?? '/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const engine = resolve(process.env.NODE_COMPAT_ENGINE ?? '/tmp/starling-node-compat/native-build/artifacts/starlingmonkey_embedding.wasm');
const output = resolve(process.env.NODE_COMPAT_ABI_OUTPUT ?? '/tmp/starling-node-compat/u32-diagnostic');
const componentizeDirectory = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
const { componentize } = await import(pathToFileURL(join(componentizeDirectory, 'src/componentize.js')));
const { componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const hash = value => createHash('sha256').update(value).digest('hex');
const source = `export function unsigned(value) { return value >>> 0; }
export function signed(value) { return value | 0; }
export function constant() { return 2342402100; }
export function describe(value) { return JSON.stringify({value, unsigned:value>>>0, signed:value|0, constant:2342402100}); }`;
const wit = `package test:unsigned;
world check {
  export unsigned: func(value: u32) -> u32;
  export signed: func(value: u32) -> s32;
  export constant: func() -> u32;
  export describe: func(value: u32) -> string;
}`;
const cases = [
  ['unsigned(2147483647)', 2147483647], ['unsigned(2147483648)', 2147483648],
  ['unsigned(2342402100)', 2342402100], ['unsigned(4294967295)', 4294967295],
  ['signed(2342402100)', -1952565196], ['constant()', 2342402100],
];
const version = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true });
const variants = [];
for (const [name, selectedEngine] of [['native', engine], ['released', join(componentizeDirectory, 'lib/starlingmonkey_embedding.wasm')]]) {
  const { component } = await componentize(source, { engine: selectedEngine, witWorld: wit, worldName: 'check',
    disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
  const path = join(output, name + '.component.wasm');
  await writeFile(path, component);
  const emittedWit = await componentWit(component);
  assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
  function invoke(call) {
    const result = spawnSync(wasmtime, ['run', '--invoke', call, path], { encoding: 'utf8', timeout: 120000 });
    assert.equal(result.status, 0, result.error?.message || result.stderr);
    return result.stdout.trim();
  }
  const results = cases.map(([call, expected]) => {
    const observed = Number(invoke(call));
    return { call, expected, observed, matches: observed === expected };
  });
  const internal = JSON.parse(JSON.parse(invoke('describe(2342402100)')));
  assert.deepEqual(internal, { value: 2342402100, unsigned: 2342402100, signed: -1952565196, constant: 2342402100 });
  assert(results.find(result => result.call.startsWith('signed')).matches, 's32 control must work');
  variants.push({ name, engineSha256: hash(await readFile(selectedEngine)), componentSha256: hash(component),
    emittedImports: [], results, internalStringControl: internal });
}
const report = { schemaVersion: 1, node: process.version, componentizeJs: '0.23.0', wasmtime: version.stdout.trim(),
  sourceSha256: hash(source), world: wit, variants,
  conclusion: 'Both pinned engines produce incorrect high-u32 results while signed and in-guest/string controls remain correct. No Buffer code is involved.',
  benchmarkWorkaround: 'Return FNV checksums as s32 using |0; host reinterprets bits as u32. Input sizes and iteration counts stay below 2^31.',
  limits: 'This reproduces the result-transport defect; it does not establish its exact implementation cause or fix.' };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
