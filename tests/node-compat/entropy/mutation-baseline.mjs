// Safe mutation-only baseline: no detached buffer, forced GC or pointer probe.
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_ENTROPY_MUTATION_OUTPUT ?? '/tmp/starling-node-compat/entropy-mutation-baseline');
const engine = resolve(process.env.NODE_COMPAT_ENGINE ?? '/tmp/starling-node-compat/allocation-r2-native-freeze/engine.wasm');
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? '/tmp/starling-node-compat/allocation-r2-native-freeze/source');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
for (const entry of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, entry.path))), entry.sha256);
async function exercise(crypto) {
  const input = new Uint8Array([1, 2, 3]);
  const algorithm = { get name() { input.fill(0); return 'SHA-256'; } };
  const digest = await crypto.subtle.digest(algorithm, input);
  return { mutatedInput: [...input], digest: Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('') };
}
const source = `const exercise=${exercise.toString()}; export async function run(){ return JSON.stringify(await exercise(crypto)); }`;
const wit = 'package test:entropy-mutation; world test { export run: func() -> string; }';
const toolchain = await loadToolchain();
const { componentize, provenance } = await loadComponentizer(toolchain);
const { transpile, componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const { component } = await componentize(source, { engine, witWorld: wit, worldName: 'test',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
const emittedWit = await componentWit(component);
assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
await writeFile(join(output, 'mutation.component.wasm'), component);
const { files } = await transpile(component, { name: 'mutation' });
for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
const instance = await import(pathToFileURL(join(output, 'mutation.js')));
const oracle = await exercise(webcrypto);
const observed = JSON.parse(await instance.run());
const baseline = process.env.NODE_COMPAT_EXPECT_COPY_FIX !== '1';
assert.deepEqual(observed.mutatedInput, [0, 0, 0]);
assert.equal(oracle.digest, '709e80c88487a2411e1ee4dfb9f22a861492d20c4765150c0c794abd70f8147c');
assert.deepEqual(observed, oracle, 'Node profile must preserve pinned Node22 normalization/copy order');
const result = { schema: 1, verifiedAtUtc: new Date().toISOString(), engine, engineSha256: metadata.engineSha256,
  sourceRoot, sourceFilesVerified: metadata.sourceManifest.length, provenance, componentSha256: hash(component),
  emittedImports: [], emittedWit, source, sourceSha256: hash(source), wit, oracle, observed,
  matchesOracle: observed.digest === oracle.digest, baseline,
  finding: 'Pinned Node22 observes algorithm-getter mutation before digest input copy; mutation alone does not reproduce the native borrowed-pointer lifetime hazard',
  scope: 'Safe mutation only through the documented algorithm.name getter; no detach, raw pointer read or forced GC' };
await writeFile(join(output, 'results.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output, baseline, oracle, observed, matchesOracle: result.matchesOracle }));
