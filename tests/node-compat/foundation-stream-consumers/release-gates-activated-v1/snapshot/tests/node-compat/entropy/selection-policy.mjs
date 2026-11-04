// Shared entropy checks used by the production HTTP packaging helper and the
// staged model tests. Full receipt/catalogue/final-component enforcement lives
// in ../capability-policy.mjs; the old comment/source is archived in staged-sources/.
import assert from 'node:assert/strict';
export const RANDOM = 'wasi:random/random@0.2.10';

export function validateEntropySelection({ engineMetadata, disableFeatures, selectedInterfaces }) {
  assert.equal(engineMetadata.profileEnabled, true);
  assert(['off', 'runtime-only'].includes(engineMetadata.entropyPolicy));
  assert(Array.isArray(disableFeatures) && Array.isArray(selectedInterfaces));
  const off = engineMetadata.entropyPolicy === 'off';
  if (off) {
    assert(disableFeatures.includes('random'), 'OFF engine must disable upstream random feature');
    assert(!selectedInterfaces.some(id => id.startsWith('wasi:random/')), 'OFF world cannot admit random host interfaces');
  } else {
    assert(!disableFeatures.includes('random'), 'Runtime-only engine cannot use deterministic upstream random stubs');
    assert(selectedInterfaces.includes(RANDOM), 'Explicit standard random@0.2.10 selection required');
    assert(selectedInterfaces.every(id => !id.startsWith('wasi:random/') || id === RANDOM), 'No alternate random version, insecure interface or wildcard admitted');
  }
  return engineMetadata.entropyPolicy;
}

export function validateEntropyImports({ policy, emittedImports, coreImportModules, selectedInterfaces }) {
  assert(!coreImportModules.includes('wasi_snapshot_preview1'), 'No final Preview1 imports');
  for (const id of emittedImports) assert(selectedInterfaces.includes(id), `Unselected host interface: ${id}`);
  const random = emittedImports.filter(id => id.startsWith('wasi:random/'));
  if (policy === 'off') assert.deepEqual(random, []);
  else { assert.equal(policy, 'runtime-only'); assert.deepEqual(random, [RANDOM]); }
}
