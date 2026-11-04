import assert from 'node:assert/strict';
import { RANDOM, validateEntropySelection, validateEntropyImports } from './selection-policy.mjs';

const off = { engineMetadata: { profileEnabled: true, entropyPolicy: 'off' }, disableFeatures: ['random'], selectedInterfaces: [] };
const on = { engineMetadata: { profileEnabled: true, entropyPolicy: 'runtime-only' }, disableFeatures: [], selectedInterfaces: [RANDOM] };
let cases = 0;
for (const options of [off, on]) { assert.equal(validateEntropySelection(options), options.engineMetadata.entropyPolicy); ++cases; }
for (const options of [
  { ...off, disableFeatures: [] }, { ...off, selectedInterfaces: [RANDOM] },
  { ...on, disableFeatures: ['random'] }, { ...on, selectedInterfaces: [] },
  { ...on, selectedInterfaces: ['wasi:random/random@0.2.12'] },
  { ...on, selectedInterfaces: [RANDOM, 'wasi:random/insecure@0.2.10'] },
  { ...on, selectedInterfaces: [RANDOM, 'wasi:random/*'] },
  { ...on, engineMetadata: { profileEnabled: false, entropyPolicy: 'runtime-only' } },
  { ...on, engineMetadata: { profileEnabled: true, entropyPolicy: 'default' } },
]) { assert.throws(() => validateEntropySelection(options)); ++cases; }
for (const options of [
  { policy: 'off', emittedImports: [], coreImportModules: [], selectedInterfaces: [] },
  { policy: 'runtime-only', emittedImports: [RANDOM], coreImportModules: [RANDOM], selectedInterfaces: [RANDOM] },
]) { validateEntropyImports(options); ++cases; }
for (const options of [
  { policy: 'off', emittedImports: [RANDOM], coreImportModules: [RANDOM], selectedInterfaces: [] },
  { policy: 'runtime-only', emittedImports: [], coreImportModules: [], selectedInterfaces: [RANDOM] },
  { policy: 'runtime-only', emittedImports: [RANDOM], coreImportModules: ['wasi_snapshot_preview1'], selectedInterfaces: [RANDOM] },
  { policy: 'runtime-only', emittedImports: ['wasi:random/random@0.2.12'], coreImportModules: [], selectedInterfaces: [RANDOM] },
]) { assert.throws(() => validateEntropyImports(options)); ++cases; }
console.log(JSON.stringify({ policyCases: cases, passed: true, installedInProduction: false }));
