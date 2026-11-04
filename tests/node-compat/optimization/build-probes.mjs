import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { createProbes, operations } from './probes.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_OPTIMIZATION_OUTPUT ?? '/tmp/starling-node-compat/optimization');
const engine = resolve(process.env.NODE_COMPAT_BASELINE_ENGINE ?? join(output, 'baseline.engine.wasm'));
const { directory: toolchain, require, rolldown } = await loadToolchain();
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const engineBytes = await readFile(engine);
assert.equal(hash(engineBytes), 'da69618da72315c3b3f20d105708fd625a3b7c0691f49329201036c3c2fd5796', 'Probes require the immutable measured baseline engine');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(metadata.engineSha256, hash(engineBytes));
assert.equal(metadata.gcStress, false);
assert.equal(metadata.profileEnabled, true);
await mkdir(output, { recursive: true });
const { componentize } = await import(pathToFileURL(join(toolchain, 'node_modules/@bytecodealliance/componentize-js/src/componentize.js')));
const { componentWit, transpile } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const entry = join(here, 'probes.virtual-entry.mjs');
const source = `import {Buffer} from 'node:buffer';import {createProbes} from './probes.mjs';const p=createProbes(Buffer);export const setup=p.setup;export const run=p.run;export const facts=p.facts;`;
const builder = await rolldown({ input: entry, platform: 'neutral', treeshake: true, plugins: [{ name: 'native-allocation-probes',
  resolveId(id) { if (id === entry) return entry; if (id === 'node:buffer') return { id, external: true }; },
  load(id) { if (id === entry) return source; },
}] });
let bundle;
try { const result = await builder.generate({ format: 'esm', codeSplitting: false }); assert.equal(result.output.length, 1); bundle = result.output[0]; }
finally { await builder.close(); }
assert.deepEqual(bundle.imports, ['node:buffer']);
await writeFile(join(output, 'probes.bundle.mjs'), bundle.code);
const { component } = await componentize(bundle.code, { engine, witWorld: await readFile(join(here, 'probes.wit'), 'utf8'), worldName: 'probes',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
const componentPath = join(output, 'probes.component.wasm');
await writeFile(componentPath, component);
const emittedWit = await componentWit(component);
assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
await writeFile(join(output, 'probes.emitted.wit'), emittedWit);
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
const { files } = await transpile(component, { name: 'probes' });
for (const [name, contents] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), contents); }
const instance = await import(pathToFileURL(join(output, 'probes.js')));
const facts = JSON.parse(instance.facts());
assert.equal(facts.productionBrandRejectsPrototypeSpoof, true);
assert.equal(facts.productionBrandRejectsPseudoTaggedU8, true);
assert.equal(facts.uint8FromHex, 'function', 'Guest native intrinsic control must exist');
const scenarios = [];
// The Node oracle's prototype-based brand differs. Probe output brand checks
// are irrelevant to the bytes; use a facade over Node solely for oracle bytes.
const oracleBuffer = new Proxy(NodeBuffer, { get(target, key) { return key === 'isBuffer' ? () => false : Reflect.get(target, key); } });
const byteOracle = createProbes(oracleBuffer);
for (const operation of operations) for (const size of [64, 4096]) {
  const iterations = size === 64 ? 10000 : 256;
  const expectedSetupChecksum = byteOracle.setup(operation, size) >>> 0;
  const expectedRunChecksum = byteOracle.run(iterations) >>> 0;
  assert.equal(instance.setup(operation, size) >>> 0, expectedSetupChecksum, operation);
  assert.equal(instance.run(iterations) >>> 0, expectedRunChecksum, operation);
  scenarios.push({ operation, size, iterations, expectedSetupChecksum, expectedRunChecksum });
}
const manifest = { schema: 1, baselineEngine: engine, baselineEngineSha256: hash(engineBytes), componentPath,
  componentSha256: hash(component), componentBytes: component.length, emittedImports: [], emittedWit, facts, scenarios,
  sourceManifest: await Promise.all(['probes.mjs', 'probes.wit', 'build-probes.mjs'].map(async path => ({ path, sha256: hash(await readFile(join(here, path))) }))),
  protocol: 'Single baseline engine/component, same already-materialized source and fingerprint. Only per-output stages vary. Controls are NOT public Buffer implementations.',
};
await writeFile(join(output, 'probe-build.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({ componentPath, componentSha256: manifest.componentSha256, cases: scenarios.length, facts }, null, 2));
