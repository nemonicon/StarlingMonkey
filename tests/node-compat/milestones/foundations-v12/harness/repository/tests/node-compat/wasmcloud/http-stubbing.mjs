// Pinned guest-packaging adapter, not a host or guest-engine modification.
// ComponentizeJS 0.23's final feature pass cannot independently preserve manual
// HTTP bindings and remove outgoing HTTP. Compose its real stubWasi API twice.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { getComponentizerPins } from '../componentizer.mjs';
import { validateEntropySelection, RANDOM } from '../entropy/selection-policy.mjs';

const sourcePins = {
  'src/componentize.js': 'e58ef4f3b126f4a3fd07c61b368930bbf02dd0029f0f03e4c6928528e994e559',
  'lib/spidermonkey-embedding-splicer.js': '075b7e63ca2c8d9337b9a05c3aebe392c22b11ebcadbef0292f8251814c91e7d',
  'lib/spidermonkey-embedding-splicer.core.wasm': '6190193dbfefc48afa9ff191af442e27c59741a4a2b62681b4c4943a8fa7c055',
  'lib/spidermonkey-embedding-splicer.core2.wasm': '364466ad6cb6eb27aa2e6f38a15f6a986b50f0d964aa7bb838e2bb3a1259e4c2',
};

export async function componentizeSelectedHTTP(componentize, directory, source, options, provenance, finalizeCore) {
  const engineMetadata = JSON.parse(await readFile(options.engine + '.build.json'));
  const entropyPolicy = engineMetadata.entropyPolicy ?? 'off';
  assert(['off', 'runtime-only'].includes(entropyPolicy), 'Unknown HTTP engine entropy policy');
  const runtimeEntropy = entropyPolicy === 'runtime-only';
  if (engineMetadata.entropyPolicy !== undefined) {
    validateEntropySelection({ engineMetadata, disableFeatures: options.disableFeatures ?? [], selectedInterfaces: options.selectedInterfaces ?? [] });
  } else {
    // Historical R2 has no entropy policy receipt; retain its exact OFF pass.
    assert((options.disableFeatures ?? []).includes('random'));
    assert(!(options.selectedInterfaces ?? []).includes(RANDOM));
  }
  const bindingFeatures = runtimeEntropy ? ['http', 'random'] : ['http'];
  const firstStubFeatures = ['random', 'stdio', 'clocks', 'fetch-event'];
  let selectedPins = sourcePins;
  if (provenance && provenance.selection !== 'stock-legacy-diagnostic') {
    selectedPins = getComponentizerPins(provenance);
  } else if (provenance) {
    assert.equal(provenance.selection, 'stock-legacy-diagnostic');
  }
  const checkedFiles = [];
  for (const [path, expected] of Object.entries(selectedPins)) {
    const actual = createHash('sha256').update(await readFile(join(directory, path))).digest('hex');
    assert.equal(actual, expected, `HTTP packaging adapter requires exact ComponentizeJS 0.23 bytes: ${path}`);
    checkedFiles.push({ path, sha256: actual });
  }
  const { splicer } = await import(pathToFileURL(join(directory, 'lib/spidermonkey-embedding-splicer.js')));
  const original = splicer.stubWasi;
  assert.equal(typeof original, 'function');
  assert.equal(Object.getOwnPropertyDescriptor(splicer, 'stubWasi').writable, true);
  let calls = 0;
  let coreImportModules;
  let coreImports;
  let finalCore;
  splicer.stubWasi = (wasm, features, witSource, witPath, worldName) => {
    assert.equal(++calls, 1, 'Only one final packaging invocation is admitted');
    assert.deepEqual([...features].sort(), bindingFeatures, 'Manual bindgen features must match explicit HTTP entropy policy');
    // Pass one keeps RNG/clocks/stdio imports intact so pass two can stub them
    // once. fetch-event preserves HTTP types while HTTP=false removes outgoing.
    const withoutOutgoing = original(wasm, firstStubFeatures, witSource, witPath, worldName);
    // The selected final pass retains HTTP types/I/O and, only for runtime
    // entropy, secure random. It does not
    // restore the outgoing-handler function already replaced by pass one.
    const final = original(withoutOutgoing, bindingFeatures, witSource, witPath, worldName);
    coreImports = WebAssembly.Module.imports(new WebAssembly.Module(final));
    coreImportModules = [...new Set(coreImports.map(entry => entry.module))].sort();
    finalCore = final;
    return final;
  };
  try {
    const result = await componentize(source, { ...options,
      ...(finalizeCore ? { finalizeComponent: async () => {
        assert.equal(calls, 1);
        assert(finalCore, 'Final no-Preview1 core must exist before wrapping');
        return finalizeCore(finalCore);
      } } : {}),
    });
    assert.equal(calls, 1, 'Pinned final stubWasi integration point was not reached');
    return { ...result, finalCore, packagingAudit: {
      name: 'componentize-js-0.23-two-pass-selected-http', checkedFiles,
      packagingSelection: provenance?.selection ?? 'stock-legacy-diagnostic',
      entropyPolicy, initialBindingFeatures: bindingFeatures, firstStubFeatures, finalStubFeatures: bindingFeatures,
      sourceReference: 'ComponentizeJS 4d812f5a7b524cea5bcfd565cac55f3fab876a57:src/componentize.js:392 and crates/spidermonkey-embedding-splicer/src/stub_wasi.rs:157-190',
      coreImportModules, coreImports,
      scope: 'Temporary function replacement in this single build process; npm package files, native engine, Wasmtime and wasmCloud are unchanged',
    } };
  } finally { splicer.stubWasi = original; }
}
