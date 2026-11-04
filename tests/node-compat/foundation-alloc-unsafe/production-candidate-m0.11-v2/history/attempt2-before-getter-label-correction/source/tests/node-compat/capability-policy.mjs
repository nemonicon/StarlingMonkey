// Build-time capability policy, not a host service or a ComponentizeJS API.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const catalogueBytes = await readFile(new URL('./wasi-0.2.10-interfaces.json', import.meta.url));
export const WASI_CATALOGUE_SHA256 = 'a9b23a7158e4cfc1951ac166511a2b3d4b8d8b3714794a8757f5198597f80d01';
assert.equal(hash(catalogueBytes), WASI_CATALOGUE_SHA256);
const catalogue = JSON.parse(catalogueBytes);
const knownInterfaces = new Set(catalogue.interfaces);
export const SECURE_RANDOM_INTERFACE = 'wasi:random/random@0.2.10';
export const ENTROPY_ENTRY_PATCH_SHA256 = 'a12c00a0913a2a03e4cea3ab0e525c5cec56d4e0101d33076d6a3687df824f99';

function fail(message) {
  const error = new Error(message);
  error.code = 'ERR_SM_NODE_CAPABILITY_SELECTION';
  throw error;
}
// These are the exact default feature names in pinned ComponentizeJS 0.23.0.
const featureNames = new Set(['stdio', 'random', 'clocks', 'http', 'fetch-event']);
function record(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
function featureList(value, name) {
  if (value === undefined) return [];
  if (!Array.isArray(value) || value.some(id => typeof id !== 'string')) fail(`${name} must be an array of feature names`);
  if (new Set(value).size !== value.length) fail(`Duplicate ${name} entry`);
  for (const id of value) if (!featureNames.has(id)) fail(`Unknown pinned ComponentizeJS feature: ${id}`);
  return value;
}
function interfaceList(value) {
  if (!Array.isArray(value) || value.some(id => typeof id !== 'string')) fail('selectedInterfaces must be an array of exact interface names');
  if (new Set(value).size !== value.length) fail('Duplicate selected interface');
  for (const id of value) {
    if (!knownInterfaces.has(id)) fail(`Not a pinned standard WASI0.2.10 interface: ${id}`);
    if (id.startsWith('wasi:random/') && id !== SECURE_RANDOM_INTERFACE) fail('This profile selects only secure WASI random, never insecure random/seed');
  }
  return value;
}
export function selectedInterfacePolicy(metadata, options) {
  if (metadata !== undefined && !record(metadata)) fail('Engine metadata must be an object');
  if (!record(options)) fail('Component options must be an object');
  const entropyPolicy = metadata?.entropyPolicy;
  const observed = metadata?.observedCMakeOptions;
  if (observed !== undefined && !record(observed)) fail('observedCMakeOptions must be an object');
  const patches = metadata?.componentizeJsPatches;
  if (patches !== undefined && (!Array.isArray(patches) || patches.some(p => !record(p) || typeof p.name !== 'string'))) fail('componentizeJsPatches must be an array of named patch receipts');
  const entryPatches = (patches ?? []).filter(p => p.name === 'node-compat-runtime-entry-v1');
  const modern = observed?.NODE_COMPAT_ENTROPY_MODE !== undefined || metadata?.entropyEntryPatchApplied !== undefined || entryPatches.length > 0;
  if (modern && entropyPolicy === undefined) fail('Modern entropy configuration requires an explicit entropyPolicy');
  if (entropyPolicy !== undefined && !['off', 'runtime-only'].includes(entropyPolicy)) fail('Unknown engine entropy policy');
  const disabled = featureList(options.disableFeatures, 'disableFeatures');
  const enabled = featureList(options.enableFeatures, 'enableFeatures');
  const selected = options.selectedInterfaces;
  if (selected === undefined) {
    if (entropyPolicy !== undefined) fail('Policy engines require explicit selectedInterfaces');
    return null; // Only receipts without modern entropy fields retain historical contracts.
  }
  interfaceList(selected);
  if (entropyPolicy !== undefined) {
    if (metadata.profileEnabled !== true || observed?.ENABLE_BUILTIN_NODE_COMPAT !== 'ON') fail('Entropy policy requires the actually configured Node profile');
    const expectedMode = entropyPolicy === 'off' ? 'OFF' : 'RUNTIME_ONLY';
    if (observed?.NODE_COMPAT_ENTROPY_MODE !== expectedMode) fail('Entropy metadata disagrees with actual configured option');
    const patch = entryPatches[0];
    if (metadata.entropyEntryPatchApplied !== true || entryPatches.length !== 1 || patch?.applied !== true || patch.sha256 !== ENTROPY_ENTRY_PATCH_SHA256) fail('Actual private deployed-entry patch is required exactly once');
    if (entropyPolicy === 'off' && (!disabled.includes('random') || selected.includes(SECURE_RANDOM_INTERFACE))) fail('OFF entropy requires disabled random and no random import selection');
    if (entropyPolicy === 'runtime-only' && (disabled.includes('random') || !selected.includes(SECURE_RANDOM_INTERFACE))) fail('Runtime entropy requires the selected secure random interface and retained random feature');
    if (enabled.length) fail('Do not override the explicit disabled-feature contract');
  }
  return Object.freeze({ schemaVersion: 1, entropyPolicy: entropyPolicy ?? 'historical-unspecified',
    selectedInterfaces: Object.freeze([...selected].sort()), catalogueSha256: WASI_CATALOGUE_SHA256 });
}

export async function auditSelectedInterfaces(toolchain, component, policy) {
  if (policy === null) return null;
  if (!record(policy) || policy.schemaVersion !== 1 || policy.catalogueSha256 !== WASI_CATALOGUE_SHA256 ||
      !['off', 'runtime-only', 'historical-unspecified'].includes(policy.entropyPolicy)) fail('Malformed selected-interface policy');
  interfaceList(policy.selectedInterfaces);
  if (policy.entropyPolicy === 'off' && policy.selectedInterfaces.includes(SECURE_RANDOM_INTERFACE)) fail('OFF policy cannot select random');
  if (policy.entropyPolicy === 'runtime-only' && !policy.selectedInterfaces.includes(SECURE_RANDOM_INTERFACE)) fail('Runtime policy must select secure random');
  if (!(component instanceof Uint8Array)) fail('Final component must be bytes');
  const { componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
  const wit = await componentWit(component);
  const emittedImports = [...wit.matchAll(/^\s*import\s+([^;]+);/gm)].map(match => match[1].trim()).sort();
  for (const id of emittedImports) {
    if (!knownInterfaces.has(id) || !policy.selectedInterfaces.includes(id)) fail(`Unselected emitted host interface: ${id}`);
  }
  if (policy.entropyPolicy === 'off' && emittedImports.some(id => id.startsWith('wasi:random/'))) fail('OFF engine emitted a random capability');
  if (policy.entropyPolicy === 'runtime-only' && !emittedImports.includes(SECURE_RANDOM_INTERFACE)) fail('Runtime entropy engine did not emit its required secure random interface');
  return { ...policy, state: 'verified-final-component', componentSha256: hash(component), emittedImports,
    unusedSelectedInterfaces: policy.selectedInterfaces.filter(id => !emittedImports.includes(id)),
    scope: 'Exact component interface names/versions; type-only versus callable dependencies remain a separate type-graph audit' };
}
