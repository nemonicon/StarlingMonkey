// Build-time native module admission. A manifest declares bindings; an engine
// receipt selects which optional manifests were actually compiled/installed.
import assert from 'node:assert/strict';
import {validatePrivateTickSourceAdmission} from './private-ticks-admission.mjs';
import {validateClassicSourceAdmission} from './classic-streams-admission.mjs';
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
export const CLASSIC_STREAMS_MANIFEST = 'builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json';
assert.equal(process.version, 'v22.14.0', 'Native module admission uses the pinned Node release inventory');
const repository = fileURLToPath(new URL('../../', import.meta.url));
const schema = JSON.parse(readFileSync(new URL('../../builtins/node-compat/manifest.schema.json', import.meta.url)));
const knownCanonical = new Set([...builtinModules.map(id => `node:${id.replace(/^node:/, '')}`),
  'node:test', 'node:test/reporters', 'node:sea', 'node:sqlite']);
const bareAliases = new Set(builtinModules.filter(id => !id.startsWith('node:')));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
export const coreManifest = validateManifest(JSON.parse(readFileSync(resolve(repository, CORE_MANIFEST))), schema);
const protectedAbortV1Sources = Object.freeze({"builtins/web/event/event-target.h":"516f9c609d78576cf72897c4c5bbe1106a3d04ab4a197c50cedee3fa0c8fb96d","builtins/web/event/event-target.cpp":"1c0263f958d0f6221accf04ffa2ac12c6406e11914e1b2fab3c41c66c3038a1e","builtins/node-compat/register.cpp":"19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b","builtins/node-compat/events.mjs":"b58b0e0891145748e71139b8d08abb4187fe52e1aa12f9705beee3f6380b68f6","builtins/node-compat/events-add-abort-listener.mjs":"106be45fe33b0e35d97aad6ece3fb368210cb954bb652ea7bcdfa478b9c7083e","builtins/node-compat/events-factories.generated.h":"41b4c286e24089e0c223d0e80d4d0f587322afee8816811f2e754217f8103437","builtins/node-compat/generate-events-factory.mjs":"90a7ae6b887fce3bf92dc167090ea44c0bb8755400be2ff577658539f4a84354","builtins/node-compat/generate-factories.mjs":"46b0e0a40d3a50dae58e0d833c4861d1344df045eaf490f74060bbccc1a4561e","builtins/node-compat/export-manifest.events.node-v22.14.0.json":"90f7dc152b990dc8955c0801eab11b9410a10dc96a8019c1b7a81b69981eb561","cmake/builtins.cmake":"0155eae9e45f2d059663f1bcc54315e58e4f2cb0d8e5a9dfcb76cfa9a7f5f9ea"});
const protectedAbortV1Patch = '0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1';

// Missing new-feature fields are accepted solely for exact immutable historical
// engine + compiled-input + recipe identities. This is not a future default.
const streamWebLegacy = JSON.parse(readFileSync(new URL('./legacy-stream-web-receipts.json', import.meta.url)));
assert.equal(streamWebLegacy.schemaVersion, 1);
function validatedSourceManifest(entries) {
  assert(Array.isArray(entries), 'Engine must record its compiled inputs');
  const seen = new Set();
  return entries.map(entry => {
    assert(entry && typeof entry === 'object' && !Array.isArray(entry) &&
      Object.keys(entry).sort().join(',') === 'path,sha256' &&
      typeof entry.path === 'string' && entry.path.length > 0 &&
      !entry.path.includes('\0') && !entry.path.includes('\\') && !/^[A-Za-z]:/.test(entry.path) &&
      entry.path.split('/').every(part => part !== '' && part !== '.' && part !== '..') &&
      typeof entry.sha256 === 'string' && /^[0-9a-f]{64}$/.test(entry.sha256), 'Invalid compiled source entry');
    assert(!seen.has(entry.path), 'Duplicate compiled source path'); seen.add(entry.path);
    return { path: entry.path, sha256: entry.sha256 };
  });
}
function canonicalSourceManifestDigest(entries) {
  const canonical = validatedSourceManifest(entries).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
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
  const classic = validateClassicSourceAdmission(metadata, {sourceRoot,
    parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});
  const privateTicks = classic ?? validatePrivateTickSourceAdmission(metadata, {sourceRoot,
    parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});

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
    ['classicStreamsEnabled', 'NODE_COMPAT_CLASSIC_STREAMS', CLASSIC_STREAMS_MANIFEST],
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
  const sources = new Map(validatedSourceManifest(metadata.sourceManifest).map(entry => [entry.path, entry.sha256]));
  const manifests = selected.map(entry => {
    const expected = sources.get(entry.path);
    assert(expected, `Engine input receipt omits selected manifest: ${entry.path}`);
    if (entry.sha256 !== undefined) assert.equal(entry.sha256, expected, 'Manifest receipt conflicts with engine inputs');
    const bytes = readFileSync(resolve(sourceRoot, entry.path));
    assert.equal(digest(bytes), expected, `Selected manifest differs from built engine: ${entry.path}`);
    const manifest = validateManifest(JSON.parse(bytes), schema);
    if (!privateTicks && entry.path === EVENTS_MANIFEST && manifest.profileVersion === 'sm-node-22.14.0-m0.10') {
      assert.equal(metadata.eventsEnabled, true);
      assert.equal(metadata.protectedAbortListenerEnabled, true, 'm0.10 requires selected protected listener compilation');
      const policy = metadata.protectedAbortListenerPolicy;
      assert.equal(policy?.version, 'sm-protected-abort-listener-v2');
      assert.equal(policy.enabled, true);
      assert.equal(policy.strictPolicyVersion, 'sm-uncaught-event-v3-protected-abort-v2');
      assert.equal(metadata.strictEventExceptionPolicy?.version, policy.strictPolicyVersion);
      assert.equal(policy.patchSha256, protectedAbortV1Patch);
      assert.deepEqual(policy.sourceSha256, protectedAbortV1Sources, 'Unreviewed protected listener source selection');
      for (const [path, expected] of Object.entries(protectedAbortV1Sources)) assert.equal(sources.get(path), expected, 'Protected listener compiled source differs: ' + path);
      assert.deepEqual(policy.prerequisiteCMakeOptions, {ENABLE_BUILTIN_WEB_EVENT:'ON', ENABLE_BUILTIN_WEB_ABORT:'ON', ENABLE_BUILTIN_WEB_QUEUE_MICROTASK:'ON'});
      assert(Array.isArray(policy.actualLayoutCompileCommands) && policy.actualLayoutCompileCommands.length > 0, 'Need actual selected layout compilation');
      assert(Array.isArray(policy.actualEmbeddingCompileCommands) && policy.actualEmbeddingCompileCommands.length > 0, 'Need actual selected embedding compilation');
      for (const command of [...policy.actualLayoutCompileCommands, ...policy.actualEmbeddingCompileCommands]) assert(command.split(/\s+/).includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'), 'Protected EventListener layout flag absent');
      for (const suffix of ['/builtins/web/event/event-target.cpp', '/builtins/web/abort/abort-signal.cpp', '/builtins/node-compat/register.cpp']) assert(policy.actualLayoutCompileCommands.some(command => command.includes(suffix)), 'Missing actual layout translation unit: ' + suffix);
    }
    if (entry.profileVersion !== undefined) assert.equal(entry.profileVersion, manifest.profileVersion);
    return manifest;
  });
  builtinMap(manifests); // Also validate collisions across the selected files.
  return manifests;
}
