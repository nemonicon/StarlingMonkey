// Host-only independent schema/alias checks; no guest/module initializer call.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const base='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-integration-candidate-v1';
const sha=b=>createHash('sha256').update(b).digest('hex');
const ix=readFileSync(base+'/index.json');
assert.equal(sha(ix),'7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429');
const members=JSON.parse(ix).files;
for(const row of members){const b=readFileSync(base+'/'+row.path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);}
const inputs=JSON.parse(readFileSync(base+'/input-hashes.json')).files;
for(const path of ['/Users/dan/dev/StarlingMonkey/builtins/node-compat/validate-manifest.mjs','/Users/dan/dev/StarlingMonkey/builtins/node-compat/manifest.schema.json',process.execPath]){
 const row=inputs.find(r=>r.path===path);assert(row);const b=readFileSync(path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);
}
const policy=JSON.parse(readFileSync(base+'/policy.json'));
const schema=JSON.parse(readFileSync('/Users/dan/dev/StarlingMonkey/builtins/node-compat/manifest.schema.json'));
const {validateHashHmacSelectedManifests}=await import(pathToFileURL(base+'/manifest-model.mjs'));
assert.equal(validateHashHmacSelectedManifests(policy.selectedManifestValues,policy,schema).grantsNativeOrRuntimeAuthority,false);
const rejected=[];
for(const [name,change] of [
 ['old eleven',r=>r.pop()],
 ['then export',r=>r.at(-1).modules['node:crypto'].exports.push('then')],
 ['alias collision',r=>r.at(-1).modules['node:crypto'].aliases.push('buffer')],
 ['unexpected module',r=>r.at(-1).modules['node:fs']={aliases:['fs'],status:'partial',exports:['default']}],
]){const rows=structuredClone(policy.selectedManifestValues);change(rows);assert.throws(()=>validateHashHmacSelectedManifests(rows,policy,schema));rejected.push(name);}
for(const row of members){const b=readFileSync(base+'/'+row.path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);}
assert(isDeepStrictEqual(policy.selectedManifestValues,JSON.parse(readFileSync(base+'/policy.json')).selectedManifestValues));
console.log(JSON.stringify({schemaVersion:1,positive:true,rejected,checks:5,manifestCount:12,nativeBuildOrGuestOrCryptoWorkloadInvoked:false}));
