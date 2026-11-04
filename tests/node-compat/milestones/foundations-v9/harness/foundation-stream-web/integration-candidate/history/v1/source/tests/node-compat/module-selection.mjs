// Build-time native module admission. A manifest declares bindings; an engine
// receipt selects which optional manifests were actually compiled/installed.
import assert from 'node:assert/strict';
import { builtinModules } from 'node:module';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateManifest } from '../../builtins/node-compat/validate-manifest.mjs';

export const CORE_MANIFEST = 'builtins/node-compat/export-manifest.node-v22.14.0.json';
export const PATH_MANIFEST = 'builtins/node-compat/export-manifest.path.node-v22.14.0.json';
export const EVENTS_MANIFEST = 'builtins/node-compat/export-manifest.events.node-v22.14.0.json';
export const STRING_DECODER_MANIFEST = 'builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json';
export const ASSERT_MANIFEST = 'builtins/node-compat/export-manifest.assert.node-v22.14.0.json';
export const QUERYSTRING_MANIFEST = 'builtins/node-compat/export-manifest.querystring.node-v22.14.0.json';
export const UTIL_MANIFEST = 'builtins/node-compat/export-manifest.util.node-v22.14.0.json';
export const STREAM_WEB_MANIFEST = 'builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json';
assert.equal(process.version, 'v22.14.0', 'Native module admission uses the pinned Node release inventory');
const repository = fileURLToPath(new URL('../../', import.meta.url));
const schema = JSON.parse(readFileSync(new URL('../../builtins/node-compat/manifest.schema.json', import.meta.url)));
const knownCanonical = new Set([...builtinModules.map(id => `node:${id.replace(/^node:/, '')}`),
  'node:test', 'node:test/reporters', 'node:sea', 'node:sqlite']);
const bareAliases = new Set(builtinModules.filter(id => !id.startsWith('node:')));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
export const coreManifest = validateManifest(JSON.parse(readFileSync(resolve(repository, CORE_MANIFEST))), schema);
// Missing new-feature fields are accepted solely for exact immutable historical
// engine + compiled-input + recipe identities. This is not a future default.
const streamWebLegacy = JSON.parse(readFileSync(new URL('./legacy-stream-web-receipts.json', import.meta.url)));
assert.equal(streamWebLegacy.schemaVersion, 1);
function canonicalSourceManifestDigest(entries) {
  assert(Array.isArray(entries), 'Legacy receipt needs compiled sourceManifest');
  const seen = new Set();
  const canonical = entries.map(entry => {
    assert(entry && typeof entry.path === 'string' && /^[0-9a-f]{64}$/.test(entry.sha256), 'Invalid legacy source entry');
    assert(!seen.has(entry.path), 'Duplicate legacy source path'); seen.add(entry.path);
    return { path: entry.path, sha256: entry.sha256 };
  }).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return digest(JSON.stringify(canonical));
}
function knownLegacyStreamWebOff(metadata) {
  if (!/^[0-9a-f]{64}$/.test(metadata.engineSha256) || !/^[0-9a-f]{64}$/.test(metadata.buildRecipeSha256)) return false;
  const sourceDigest = canonicalSourceManifestDigest(metadata.sourceManifest);
  return streamWebLegacy.engines.some(entry => entry.engineSha256 === metadata.engineSha256 &&
    entry.canonicalSourceManifestSha256 === sourceDigest && entry.buildRecipeSha256 === metadata.buildRecipeSha256);
}


export function builtinMap(selectedManifests = [coreManifest]) {
  assert(Array.isArray(selectedManifests) && selectedManifests.length, 'Select at least one explicit native module manifest');
  const result = Object.create(null);
  for (const selected of selectedManifests) {
    validateManifest(selected, schema);
    for (const [canonical, module] of Object.entries(selected.modules)) {
      assert(knownCanonical.has(canonical), `Unknown Node release module: ${canonical}`);
      assert(!Object.hasOwn(result, canonical), `Duplicate native module selection: ${canonical}`);
      result[canonical] = canonical;
      for (const alias of module.aliases) {
        assert(bareAliases.has(alias), `Not a bare builtin alias in Node22.14.0: ${alias}`);
        assert(!Object.hasOwn(result, alias), `Native module alias collision: ${alias}`);
        result[alias] = canonical;
      }
    }
  }
  return Object.freeze(result);
}

export function selectedManifestsForEngine(metadata, { sourceRoot = repository } = {}) {
  assert.equal(metadata.profileEnabled, true);

  const streamWebDeclared = Object.hasOwn(metadata, 'streamWebEnabled');
  if (streamWebDeclared) {
    assert.equal(typeof metadata.streamWebEnabled, 'boolean', 'streamWebEnabled must be a boolean');
    assert.equal(metadata.observedCMakeOptions?.NODE_COMPAT_STREAM_WEB, metadata.streamWebEnabled ? 'ON' : 'OFF', 'Engine streamWebEnabled disagrees with actual CMake option');
  } else {
    assert(!Object.hasOwn(metadata.observedCMakeOptions ?? {}, 'NODE_COMPAT_STREAM_WEB') && knownLegacyStreamWebOff(metadata),
      'Absent streamWebEnabled is OFF only for pinned immutable legacy engine/source/recipe identities');
  }

  const expectedPaths = [CORE_MANIFEST];
  for (const [field, option, path] of [
    ['pathEnabled', 'NODE_COMPAT_PATH', PATH_MANIFEST],
    ['eventsEnabled', 'NODE_COMPAT_EVENTS', EVENTS_MANIFEST],
    ['stringDecoderEnabled', 'NODE_COMPAT_STRING_DECODER', STRING_DECODER_MANIFEST],
    ['assertEnabled', 'NODE_COMPAT_ASSERT', ASSERT_MANIFEST],
    ['querystringEnabled', 'NODE_COMPAT_QUERYSTRING', QUERYSTRING_MANIFEST],
    ['utilEnabled', 'NODE_COMPAT_UTIL', UTIL_MANIFEST],
    ['streamWebEnabled', 'NODE_COMPAT_STREAM_WEB', STREAM_WEB_MANIFEST],
  ]) {
    assert(metadata[field] === undefined || typeof metadata[field] === 'boolean', `${field} must be a boolean`);
    const enabled = metadata[field] === true;
    const observed = metadata.observedCMakeOptions?.[option];
    assert((observed === undefined && metadata[field] === undefined) || observed === (enabled ? 'ON' : 'OFF'), `Engine ${field} selection disagrees with actual CMake option`);
    if (enabled) expectedPaths.push(path);
  }
  // Older core-only receipts predate explicit optional manifest selection.
  const selected = metadata.selectedModuleManifests ?? (expectedPaths.length > 1 ? null : [{ path: CORE_MANIFEST }]);
  assert(Array.isArray(selected), 'Optional native modules require explicit selectedModuleManifests');
  assert.deepEqual(selected.map(entry => entry.path).sort(), [...expectedPaths].sort(), 'Unselected or omitted native module manifest');
  assert(Array.isArray(metadata.sourceManifest), 'Engine must record its compiled inputs');
  const sources = new Map(metadata.sourceManifest.map(entry => [entry.path, entry.sha256]));
  const manifests = selected.map(entry => {
    const expected = sources.get(entry.path);
    assert(expected, `Engine input receipt omits selected manifest: ${entry.path}`);
    if (entry.sha256 !== undefined) assert.equal(entry.sha256, expected, 'Manifest receipt conflicts with engine inputs');
    const bytes = readFileSync(resolve(sourceRoot, entry.path));
    assert.equal(digest(bytes), expected, `Selected manifest differs from built engine: ${entry.path}`);
    const manifest = validateManifest(JSON.parse(bytes), schema);
    if (entry.profileVersion !== undefined) assert.equal(entry.profileVersion, manifest.profileVersion);
    return manifest;
  });
  builtinMap(manifests); // Also validate collisions across the selected files.
  return manifests;
}
