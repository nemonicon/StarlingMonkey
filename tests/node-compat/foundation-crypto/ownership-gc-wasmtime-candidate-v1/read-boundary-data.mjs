// Genuine standalone read/hash utilities only; no WT CLI/helper/preflight action.
import {readFile,realpath,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const HERE=dirname(fileURLToPath(import.meta.url)),pins=JSON.parse(await readFile(join(HERE,'data-utility-pins.json'),'utf8'));
async function auth(row){const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),row.sha256);}
assert.equal(process.version,'v22.14.0');assert.equal(await realpath(process.execPath),pins.node.path);let h=createHash('sha256'),bytes=0;for await(const b of createReadStream(pins.node.path)){h.update(b);bytes+=b.length;}assert.equal(bytes,pins.node.bytes);assert.equal(h.digest('hex'),pins.node.sha256);
for(const row of pins.files)await auth(row);
const {descriptor,regular}=await import(pathToFileURL(pins.files.find(r=>r.path.endsWith('/authority.mjs')).path)),{streamHash}=await import(pathToFileURL(pins.files.find(r=>r.path.endsWith('/packaging.mjs')).path));
const raw=await readFile(join(HERE,'input-freeze.json')),data=JSON.parse(raw),seen=new Set();let small=0,large=0,total=0;
for(const row of data.files){descriptor(row);assert(!seen.has(row.path));seen.add(row.path);if(row.bytes>32*1024*1024){await streamHash(row);large++;}else{await regular(row,{maxBytes:64*1024*1024});small++;}assert.equal((await lstat(row.path)).size,row.bytes);total+=row.bytes;}
for(const row of pins.files)await auth(row);
process.stdout.write(JSON.stringify({schemaVersion:1,state:'GENUINE_CANONICAL_FULL_READ_SOURCE_BOUNDARY_PASSED_V1',manifestSha256:createHash('sha256').update(raw).digest('hex'),declaredRows:data.files.length,actualRowsRead:small+large,regularRows:small,streamRows:large,actualDeclaredBytes:total,node:pins.node,sourceOnly:true,genuineReadUtilitiesImported:true,wasmtimeCliInvoked:false,preflightOrBootstrapOrOracleInvoked:false,generatedJsImported:false,guestKeyPressureGcNativeActionsInvoked:false})+'\n');
