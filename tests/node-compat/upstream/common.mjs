import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';

export const here = dirname(fileURLToPath(import.meta.url));
export const repository = resolve(here, '../../..');
export const output = resolve(process.env.NODE_COMPAT_UPSTREAM_OUTPUT ?? '/tmp/starling-node-compat/upstream-gate');
export const upstream = resolve(process.env.NODE_COMPAT_COMPONENTIZE_SOURCE ?? '/tmp/starling-node-compat/native-build/componentize');
export const hash = bytes => createHash('sha256').update(bytes).digest('hex');
// Broad upstream regression fixtures intentionally exercise capabilities that
// the zero-import Buffer profile does not select. Admit exact standard IDs;
// never treat a package/version wildcard as a capability allowlist.
export const regressionImports = [
  'wasi:io/poll@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/streams@0.2.10',
  'wasi:clocks/monotonic-clock@0.2.10', 'wasi:clocks/wall-clock@0.2.10',
  'wasi:http/types@0.2.10', 'wasi:http/outgoing-handler@0.2.10',
  'wasi:random/random@0.2.10', 'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10',
  ...['stdin', 'stdout', 'stderr', 'terminal-input', 'terminal-output', 'terminal-stdin', 'terminal-stdout', 'terminal-stderr'].map(name => `wasi:cli/${name}@0.2.10`),
];
export function auditRegressionImports(wit) {
  const ids = [...wit.matchAll(/^\s*import\s+([^;\s]+);/gm)].map(match => match[1]);
  for (const id of ids) assert(regressionImports.includes(id), `Unselected regression capability: ${id}`);
  return ids;
}
export async function verifyUpstreamSource(relative, metadata) {
  const archive = resolve(process.env.NODE_COMPAT_COMPONENTIZE_ARCHIVE ?? '/tmp/starling-node-compat/improved-build/componentize-source.tar.gz');
  assert.equal(hash(await readFile(archive)), metadata.archivePins.componentizeJsSha256);
  const member = `ComponentizeJS-${metadata.componentizeJsRevision}/${relative}`;
  const extraction = spawnSync('tar', ['-xOf', archive, member], { maxBuffer: 8 * 1024 * 1024 });
  assert.equal(extraction.status, 0, extraction.stderr.toString());
  const bytes = await readFile(join(upstream, relative));
  assert.equal(hash(bytes), hash(extraction.stdout), `Upstream fixture source drift: ${relative}`);
  return { archive, archiveSha256: metadata.archivePins.componentizeJsSha256, member, sha256: hash(bytes) };
}
export async function context() {
  assert(process.env.NODE_COMPAT_ENGINE, 'Explicit custom engine required');
  const engine = resolve(process.env.NODE_COMPAT_ENGINE);
  const metadataPath = resolve(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json');
  const metadata = JSON.parse(await readFile(metadataPath));
  const engineSha256 = hash(await readFile(engine));
  assert.equal(engineSha256, metadata.engineSha256);
  assert.equal(metadata.profileEnabled, true);
  assert.equal(metadata.componentizeJsRevision, '4d812f5a7b524cea5bcfd565cac55f3fab876a57');
  assert.equal(metadata.auditedBaseRevision, '54b3329b3ce818fd1f244e871e9c259b63667cda');
  const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
  for (const entry of metadata.sourceManifest) {
    const path = resolve(sourceRoot, entry.path);
    assert(path.startsWith(sourceRoot + '/'));
    assert.equal(hash(await readFile(path)), entry.sha256, `Engine source mismatch: ${entry.path}`);
  }
  const toolchain = await loadToolchain();
  const { directory, require } = toolchain;
  const { componentize: auditedComponentize, directory: componentizeDirectory, splicer, provenance: componentizerProvenance } = await loadComponentizer(toolchain);
  // This harness explicitly selects the finite regression world. Policy engines
  // require exact interface selection; fixture feature choices are preserved.
  // Callers testing a zero-import world supply selectedInterfaces:[] themselves.
  const componentize = (...args) => {
    const index = typeof args[0] === 'string' ? (typeof args[1] === 'string' ? 2 : 1) : 0;
    const options = args[index];
    const selectedInterfaces = options.selectedInterfaces ?? regressionImports.filter(id => metadata.entropyPolicy !== 'off' || !id.startsWith('wasi:random/'));
    args[index] = { ...options, selectedInterfaces };
    return auditedComponentize(...args);
  };
  const { transpile, componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
  assert.notEqual(engineSha256, hash(await readFile(join(directory, 'node_modules/@bytecodealliance/componentize-js/lib/starlingmonkey_embedding.wasm'))));
  await mkdir(output, { recursive: true });
  await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
  try { await symlink(join(directory, 'node_modules'), join(output, 'node_modules'), 'dir'); }
  catch (error) { if (error.code !== 'EEXIST') throw error; }
  const preview2Adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
  return { componentize, componentizeDirectory, splicer, componentizerProvenance, transpile, componentWit, require, directory, engine, engineSha256, metadataPath, metadata, sourceRoot,
    preview2Adapter, adapterSha256: hash(await readFile(preview2Adapter)) };
}

export async function saveComponent(ctx, name, component) {
  const directory = join(output, name);
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, name + '.component.wasm'), component);
  const wit = await ctx.componentWit(component);
  auditRegressionImports(wit);
  await writeFile(join(directory, 'emitted.wit'), wit);
  const { files } = await ctx.transpile(component, { name: 'fixture', wasiShim: true });
  for (const [name, bytes] of Object.entries(files)) {
    await mkdir(dirname(join(directory, name)), { recursive: true });
    await writeFile(join(directory, name), bytes);
  }
  return { directory, componentSha256: hash(component), componentBytes: component.length,
    emittedImports: wit.split('\n').filter(line => /^\s*import /.test(line)).map(line => line.trim()) };
}
