// Pure manifest and factory DATA validation; no ALS instances or native calls.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateManifest} from '../../../../builtins/node-compat/validate-manifest.mjs';
const json=async p=>JSON.parse(await readFile(new URL(p,import.meta.url),'utf8'));
const manifest=await json('./after/builtins/node-compat/export-manifest.async-hooks.node-v22.14.0.json');
const schema=await json('../../../../builtins/node-compat/manifest.schema.json');
const surface=await json('./node22-surface.json');
assert.equal(validateManifest(manifest,schema),manifest);
assert.deepEqual(manifest.modules['node:async_hooks'].exports,surface.exports);
assert.equal(Object.keys(surface.providers).length,63);
for(const bad of [null,7,{}, {...manifest,profileVersion:'wrong'}])assert.throws(()=>validateManifest(bad,schema));
console.log(JSON.stringify({schemaVersion:1,state:'ALS_MANIFEST_DATA_CHECKS_PASSED',checks:7,
  nativeKernelInvoked:false,alsInstancesCreated:false}));
