import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { validateManifest } from '../../builtins/node-compat/validate-manifest.mjs';

assert.equal(process.version, 'v22.14.0');
const directory = new URL('../../builtins/node-compat/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('export-manifest.node-v22.14.0.json', directory)));
const schema = JSON.parse(await readFile(new URL('manifest.schema.json', directory)));
assert.equal(validateManifest(manifest, schema), manifest);
for (const [id, module] of Object.entries(manifest.modules)) {
  const namespace = await import(id);
  assert.deepEqual([...module.exports].sort(), Object.getOwnPropertyNames(namespace).sort());
  for (const [name, value] of Object.entries(module.numericExports ?? {})) {
    assert.equal(typeof value, 'number');
    assert.equal(typeof namespace[name], 'number');
  }
}
const rejections = [
  ['unknown root field', x => { x.hostAdapter = 'custom'; }],
  ['unversioned host capability', x => { x.requiredHostInterfaces.push('wasi:io/streams'); }],
  ['custom host capability', x => { x.requiredHostInterfaces.push('jco:node/fs@0.2.10'); }],
  ['wrong interface release', x => { x.requiredHostInterfaces.push('wasi:io/streams@0.2.12'); }],
  ['wrong Node release', x => { x.nodeVersion = 'v22.15.0'; }],
  ['wrong profile identity', x => { x.profileVersion = 'complete-node'; }],
  ['duplicate export', x => { x.modules['node:buffer'].exports.push('Buffer'); }],
  ['invalid identifier', x => { x.modules['node:buffer'].exports.push('bad-name'); }],
  ['missing default', x => { x.modules['node:buffer'].exports = ['Buffer']; }],
  ['accidental thenable', x => { x.modules['node:buffer'].exports.push('then'); }],
  ['alias collision', x => { x.modules['node:child_process'].aliases.push('buffer'); }],
  ['invalid alias', x => { x.modules['node:buffer'].aliases.push('node:buffer'); }],
  ['unregistered numeric member', x => { x.modules['node:buffer'].numericExports.secret = 1; }],
  ['wrong constant type', x => { x.modules['node:buffer'].numericExports.kMaxLength = '16777216'; }],
  ['fractional limit', x => { x.modules['node:buffer'].limits.MAX_LENGTH = 1.5; }],
  ['negative limit', x => { x.modules['node:buffer'].limits.MAX_LENGTH = -1; }],
  ['unknown support status', x => { x.modules['node:buffer'].status = 'complete'; }],
  ['unknown module field', x => { x.modules['node:buffer'].proxy = true; }],
  ['empty module selection', x => { x.modules = {}; }],
];
for (const [name, mutate] of rejections) {
  const candidate = structuredClone(manifest);
  mutate(candidate);
  assert.throws(() => validateManifest(candidate, schema), undefined, name);
}
assert.throws(() => validateManifest(manifest, { ...schema, ignoredSchemaKeyword: true }), /unsupported schema keyword/);
const selectedCapability = structuredClone(manifest);
selectedCapability.requiredHostInterfaces = ['wasi:io/streams@0.2.10'];
validateManifest(selectedCapability, schema);
console.log(JSON.stringify({ node: process.version, schemaValidated: true,
  exactNamespaces: Object.keys(manifest.modules), rejectedMalformedManifests: rejections.length,
  unknownSchemaKeywordRejected: true, versionedStandardCapabilityAccepted: true }));
