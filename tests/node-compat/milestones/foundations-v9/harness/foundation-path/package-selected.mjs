// Build-only finalization for this all-features-disabled Path comparison.
// Preserve the real final stubWasi pass. A remaining CLI environment Preview1
// dependency uses a finite guest-only denial adapter, never a new host service.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { getComponentizerPins } from '../componentizer.mjs';
import { DENIED_PREVIEW1 } from './denied-preview1.mjs';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export const OFFICIAL_REACTOR_CONTROL = Object.freeze({ version: 'Wasmtime42.0.1 reactor',
  url: 'https://github.com/bytecodealliance/wasmtime/releases/download/v42.0.1/wasi_snapshot_preview1.reactor.wasm',
  sha256: '90cd5af4ca2a441b5c65a55c3e229546cc5c58264689c84578cc9a6f75df72a3', bytes: 52294 });
export async function componentizeSelectedPath(toolchain, componentize, directory, provenance, source, options, observeCore) {
  assert.deepEqual([...options.disableFeatures].sort(), ['clocks', 'fetch-event', 'http', 'random', 'stdio']);
  assert.equal(options.enableFeatures, undefined);
  assert.equal(options.finalizeComponent, undefined);
  const checkedFiles = [];
  for (const [path, expected] of Object.entries(getComponentizerPins(provenance))) {
    const sha256 = hash(await readFile(join(directory, path)));
    assert.equal(sha256, expected, 'Selected finalization requires the audited packaging bytes: ' + path);
    checkedFiles.push({ path, sha256 });
  }
  const { splicer } = await import(pathToFileURL(join(directory, 'lib/spidermonkey-embedding-splicer.js')));
  const { componentNew, metadataAdd } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
  const original = splicer.stubWasi;
  assert.equal(typeof original, 'function');
  assert.equal(Object.getOwnPropertyDescriptor(splicer, 'stubWasi').writable, true);
  let calls = 0, finalCore, coreImports;
  const adapter = await readFile(options.preview2Adapter);
  assert.equal(hash(adapter), DENIED_PREVIEW1.wasmSha256); assert.equal(adapter.length, DENIED_PREVIEW1.bytes);
  assert.deepEqual(WebAssembly.Module.imports(new WebAssembly.Module(adapter)), []);
  let adapters;
  splicer.stubWasi = (wasm, features, ...wit) => {
    assert.equal(++calls, 1, 'The original feature pass must execute exactly once');
    assert.deepEqual(features, []);
    finalCore = original(wasm, features, ...wit);
    coreImports = WebAssembly.Module.imports(new WebAssembly.Module(finalCore));
    return finalCore;
  };
  try {
    const result = await componentize(source, { ...options, finalizeComponent: async () => {
      assert.equal(calls, 1); assert(finalCore);
      if (observeCore) await observeCore(finalCore, coreImports);
      const preview1 = coreImports.filter(entry => entry.module === 'wasi_snapshot_preview1');
      const environment = new Set(['args_get', 'args_sizes_get', 'environ_get', 'environ_sizes_get']);
      assert(preview1.every(entry => entry.kind === 'function' && environment.has(entry.name)),
        'Only the four known Preview1 CLI environment operations are admitted');
      adapters = preview1.length ? [['wasi_snapshot_preview1', adapter]] : [];
      return metadataAdd(await componentNew(finalCore, adapters, false), Object.entries({ language: [['JavaScript', '']],
        'processed-by': [['ComponentizeJS', '0.23.0'], ['StarlingMonkey selected Path packaging', '0.1.0']] }));
    } });
    assert.equal(calls, 1);
    return { ...result, packagingAudit: { name: 'componentize-js-0.23-selected-path-final-core-v1',
      checkedFiles, originalStubFeatures: [], originalStubCalls: calls, coreSha256: hash(finalCore), coreImports,
      finalWrapping: 'Jco componentNew(finalCore, selectedOfficialAdapters, false) + metadataAdd',
      adapters: adapters.map(([name]) => ({ name, ...DENIED_PREVIEW1 })),
      scope: 'Single-process build-tool interception only; final original core bytes unchanged, audited final interfaces only' } };
  } finally { splicer.stubWasi = original; }
}
