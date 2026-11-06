// Host-only pure manifest/schema checks. No engine, componentizer or crypto API.
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validateHashHmacSelectedManifests } from './manifest-model.mjs';
assert.equal(existsSync(new URL('./index.json',import.meta.url)),false,'Sealed family is immutable');
const read = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const policy = read('./policy.json');
const schema = read('../../../../builtins/node-compat/manifest.schema.json');
const inventory = read('../node-crypto-hash-hmac-candidate-v1/node-export-manifest.json');
assert.deepEqual(policy.selectedManifestValues.at(-1).modules['node:crypto'].exports, inventory.esmNamedIncludingDefault);
const result = validateHashHmacSelectedManifests(policy.selectedManifestValues, policy, schema);
assert.equal(result.grantsNativeOrRuntimeAuthority, false);
const rejected = [];
for (const [label, change] of [
  ['old eleven', rows => rows.pop()],
  ['then export', rows => rows.at(-1).modules['node:crypto'].exports.push('then')],
  ['missing default', rows => rows.at(-1).modules['node:crypto'].exports.pop()],
  ['wrong aliases', rows => rows.at(-1).modules['node:crypto'].aliases.push('buffer')],
  ['unsupported importOnly name', rows => rows.at(-1).modules['node:crypto'].importOnlyExports.push('newUnknown')],
  ['extra module', rows => rows.at(-1).modules['node:fs'] = { aliases:['fs'],status:'partial',exports:['default'] }],
]) {
  const rows = structuredClone(policy.selectedManifestValues);change(rows);
  assert.throws(() => validateHashHmacSelectedManifests(rows,policy,schema));rejected.push(label);
}
writeFileSync(new URL('./manifest-check-results.json',import.meta.url),JSON.stringify({schemaVersion:1,state:'PURE_HOST_MANIFEST_SCHEMA_CHECKS_PASSED',checks:9,positive:result,rejected,engineExecuted:false,cryptoOperationsInvoked:false})+'\n');
console.log(JSON.stringify({passed:true,checks:9,manifestCount:12,cryptoNames:68}));
