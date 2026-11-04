// Separate known-issue diagnostic. This does not extend the scalar export fix.
// The helper is another guest component; final composition has zero host imports.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';

assert(process.env.NODE_COMPAT_ENGINE, 'Select the ABI-fixed engine explicitly');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(metadata.abiFixEnabled, true);
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_CALLBACK_OUTPUT ?? '/tmp/starling-node-compat/callback-diagnostic');
const { directory: toolchain, require } = await loadToolchain();
const { componentize } = await import(pathToFileURL(join(toolchain, 'node_modules/@bytecodealliance/componentize-js/src/componentize.js')));
const { componentWit, transpile } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const tools = resolve(process.env.NODE_COMPAT_WASM_TOOLS ?? '/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools');
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME ?? '/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(metadata.engineSha256, hash(await readFile(engine)));
const world = `package starling:abi-helper@0.1.0;
interface identity { echo: func(value: u32) -> u32; constant: func() -> u32; }
world profile {
  import identity;
  export forward: func(value: u32) -> u32;
  export helper-constant: func() -> u32;
  export describe-forward: func(value: u32) -> string;
}`;
const source = `import { echo, constant } from 'starling:abi-helper/identity@0.1.0';
export function forward(value) { return echo(value); }
export function helperConstant() { return constant(); }
export function describeForward(value) { return JSON.stringify({ input: value, echo: echo(value), constant: constant() }); }`;
const version = spawnSync(tools, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^wasm-tools 1\.235\.0\b/);
const hostVersion = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(hostVersion.status, 0, hostVersion.stderr);
assert.match(hostVersion.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
const { component } = await componentize(source, { engine, witWorld: world, worldName: 'profile',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
const appPath = join(output, 'forwarding-guest.wasm');
await writeFile(appPath, component);
const helperPath = join(output, 'helper.wasm');
const parsed = spawnSync(tools, ['parse', join(here, 'callback-helper.wat'), '-o', helperPath], { encoding: 'utf8' });
assert.equal(parsed.status, 0, parsed.stderr);
const finalPath = join(output, 'composed.wasm');
const composeArgs = ['compose', '--no-imports', '-d', helperPath, '-o', finalPath, appPath];
const composed = spawnSync(tools, composeArgs, { encoding: 'utf8' });
assert.equal(composed.status, 0, composed.stderr);
const final = await readFile(finalPath);
const emittedWit = await componentWit(final);
assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), [], 'No custom or standard host service is required');
const { files } = await transpile(final, { name: 'callback-diagnostic' });
for (const [name, bytes] of Object.entries(files)) {
  const path = join(output, name); await mkdir(dirname(path), { recursive: true }); await writeFile(path, bytes);
}
const guest = await import(pathToFileURL(join(output, 'callback-diagnostic.js')));
const cases = [0, 1, 0x7fffffff, 0x80000000, 2342402100, 0xffffffff].map(value => {
  const observed = guest.forward(value);
  const internal = JSON.parse(guest.describeForward(value));
  assert.equal(internal.input, value);
  assert.equal(internal.echo, observed);
  assert.equal(internal.constant, 0xffffffff);
  assert.equal(guest.helperConstant(), 0xffffffff, 'High-u32 callback returns and fixed scalar exports must remain correct');
  if (value <= 0x7fffffff) assert.equal(observed, value);
  return { input: value, expected: value, observed, matches: observed === value, internal };
});
assert(cases.some(example => !example.matches), 'This pinned diagnostic must reproduce the separate imported-argument defect');
const wasmtimeCases = [];
for (const [call, expected] of [['forward(2147483648)', 2147483648], ['helper-constant()', 0xffffffff]]) {
  const run = spawnSync(wasmtime, ['run', '--invoke', call, finalPath], { encoding: 'utf8', timeout: 120000 });
  assert.equal(run.status, 0, run.stderr);
  const observed = Number(run.stdout.trim());
  if (call.startsWith('helper')) assert.equal(observed, expected);
  else assert.notEqual(observed, expected);
  wasmtimeCases.push({ call, expected, observed, matches: observed === expected });
}
const report = {
  schema: 1, node: process.version, engine, engineSha256: metadata.engineSha256,
  componentizeJsRevision: metadata.componentizeJsRevision, exportResultFixEnabled: true,
  tools: { version: version.stdout.trim(), sha256: hash(await readFile(tools)) }, wasmtime: hostVersion.stdout.trim(),
  source, world, helperSourceSha256: hash(await readFile(join(here, 'callback-helper.wat'))),
  compositionCommand: [tools, ...composeArgs], finalPath, componentSha256: hash(final), emittedWit, emittedImports: [],
  cases, wasmtimeCases,
  conclusion: 'The separate imported CoreTy::I32 argument reader still misreads boxed high-u32 Numbers. Guest-only composition reproduces it with no external host capability. Callback return values and the patched scalar export are controls that pass.',
  sourceLocation: 'ComponentizeJS 4d812f5a7b524cea5bcfd565cac55f3fab876a57:crates/spidermonkey-embedding-splicer/src/splice.rs:598-606',
  scope: 'Known limitation only; no imported-callback fix is applied by componentize-u32-result.patch.',
};
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
await writeFile(join(here, 'callback-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ emittedImports: [], reproducedImportedArgumentDefect: cases.filter(example => !example.matches).length, callbackReturnAndExportControlsPassed: true, output }, null, 2));
