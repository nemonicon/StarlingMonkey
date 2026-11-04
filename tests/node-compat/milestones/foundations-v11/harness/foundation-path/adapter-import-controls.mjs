// Negative packaging controls. Capture unchanged candidate bytes, then require
// the shared final-interface audit to refuse them. Never instantiate these.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, cp } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { OFFICIAL_REACTOR_CONTROL } from './package-selected.mjs';
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const output = resolve(process.env.NODE_COMPAT_PATH_ADAPTER_CONTROLS_OUTPUT ?? '/tmp/starling-node-compat/foundations-v3/path-adapter-controls');
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
for (const entry of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, entry.path))), entry.sha256);
const tools = await loadToolchain(), { componentize, provenance } = await loadComponentizer(tools);
const { componentWit, preview1AdapterReactorPath } = await import(pathToFileURL(tools.require.resolve('@bytecodealliance/jco')));
const { _setPreopens, _clearPreopens } = await import(pathToFileURL(tools.require.resolve('@bytecodealliance/preview2-shim/filesystem')));
await mkdir(output, { recursive: true });
const witPath = join(output, 'wit'); await mkdir(witPath, { recursive: true });
await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps'), join(witPath, 'deps'), { recursive: true });
await writeFile(join(witPath, 'profile.wit'), await readFile(join(here, 'benchmark.mjs.wit')));
const source = 'import path from "node:path"; export function run(iterations){return path.join("a","b").length+iterations;}';
const controls = [
  { name: 'npm-default', path: fileURLToPath(preview1AdapterReactorPath()) },
  { name: 'repository-legacy', path: join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),
    sha256: '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0' },
  { name: 'official-wasmtime42', path: resolve(process.env.NODE_COMPAT_PATH_OFFICIAL_ADAPTER ?? '/tmp/starling-node-compat/foundation-adapters/wasmtime42.0.1-reactor.wasm'),
    ...OFFICIAL_REACTOR_CONTROL },
];
const results = [];
for (const control of controls) {
  const adapter = await readFile(control.path), sha256 = hash(adapter);
  if (control.sha256) assert.equal(sha256, control.sha256);
  let observed, refusal;
  _setPreopens({ [witPath]: witPath });
  try {
    await componentize(source, { engine, witPath, worldName: 'profile', preview2Adapter: control.path,
      disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: ['wasi:cli/environment@0.2.10'],
      finalizeComponent: async result => {
        const componentPath = join(output, control.name + '.refused.component.wasm');
        await writeFile(componentPath, result.component);
        const wit = await componentWit(result.component);
        await writeFile(join(output, control.name + '.wit'), wit);
        observed = { componentPath, componentSha256: hash(result.component), bytes: result.component.length,
          emittedWit: wit, emittedImports: [...wit.matchAll(/^\s*import\s+([^;]+);/gm)].map(match => match[1].trim()).sort() };
        return result.component; // No modification or policy bypass.
      } });
  } catch (error) { refusal = { name: error.name, code: error.code, message: error.message }; }
  finally { _clearPreopens(); }
  assert(observed, 'Candidate must be captured before refusal');
  assert.equal(refusal?.code, 'ERR_SM_NODE_CAPABILITY_SELECTION');
  if (control.name === 'npm-default') assert(observed.emittedImports.includes('wasi:cli/environment@0.2.12'));
  else assert(observed.emittedImports.some(id => id !== 'wasi:cli/environment@0.2.10'));
  results.push({ name: control.name, adapter: { ...control, sha256, bytes: adapter.length }, ...observed, refusal, instantiated: false });
  console.log(JSON.stringify({ name: control.name, refused: refusal.message, interfaces: observed.emittedImports.length }));
}
const report = { schema: 1, engine, engineSha256: metadata.engineSha256, sourceRoot,
  componentizer: provenance, selectedInterfaces: ['wasi:cli/environment@0.2.10'],
  source, sourceSha256: hash(source), results,
  scope: 'Unmodified components correctly refused by the final capability audit; no refused component is instantiated' };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
await writeFile(join(here, 'adapter-control-results.json'), JSON.stringify(report, null, 2) + '\n');
