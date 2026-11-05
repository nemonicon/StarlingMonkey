// Explicitly authorized standalone DATA utilities only: never call a preflight/guest.
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const HERE=dirname(fileURLToPath(import.meta.url)),pins=JSON.parse(await readFile(join(HERE,'data-utility-pins.json'),'utf8'));
async function auth(row){const raw=await readFile(row.path);assert.equal(raw.length,row.bytes);assert.equal(createHash('sha256').update(raw).digest('hex'),row.sha256);}
assert.equal(process.version,'v22.14.0');assert.equal(await realpath(process.execPath),pins.node.path);
let nh=createHash('sha256'),nb=0;for await(const b of createReadStream(pins.node.path)){nh.update(b);nb+=b.length;}assert.equal(nb,pins.node.bytes);assert.equal(nh.digest('hex'),pins.node.sha256);
for(const row of pins.files)await auth(row);
const authorityRow=pins.files.find(r=>r.path.endsWith('/authority.mjs')),packagingRow=pins.files.find(r=>r.path.endsWith('/packaging.mjs'));
const {descriptor,regular}=await import(pathToFileURL(authorityRow.path)),{streamHash}=await import(pathToFileURL(packagingRow.path));
const proof=JSON.parse(await readFile(join(HERE,'successor-derivations.json'),'utf8')),manifestBytes=await readFile(join(HERE,'input-freeze.json')),manifest=JSON.parse(manifestBytes),beforeBytes=await readFile(dirname(proof.donorSourceIndex.path)+'/input-freeze.json'),before=JSON.parse(beforeBytes);
const bad=before.files.filter(r=>!r.path.startsWith('/'));assert.equal(bad.length,17);
for(const row of bad)assert.throws(()=>descriptor(row),/Canonical absolute path required/);
let regularRows=0,streamRows=0,actualBytes=0;const fixed=[];
for(const row of manifest.files){
 const captured=descriptor(row);assert.deepEqual(captured,row);let mode;
 if(row.bytes>32*1024*1024){await streamHash(row);streamRows++;mode='genuine-streamHash';}
 else{const raw=await regular(row,{maxBytes:64*1024*1024});assert.equal(raw.length,row.bytes);regularRows++;mode='genuine-regular-max64MiB';}
 const observed=await lstat(row.path);assert.equal(observed.size,row.bytes);actualBytes+=observed.size;
 const correction=proof.relativeRowsCorrected.find(r=>r.after.path===row.path);if(correction)fixed.push({before:correction.before,after:row,readMode:mode,descriptorPassed:true,fullBytesReadAndDigestVerified:true,observedBytes:observed.size});
}
assert.equal(fixed.length,17);assert.equal(regularRows+streamRows,manifest.files.length);
for(const row of pins.files)await auth(row);
process.stdout.write(JSON.stringify({schemaVersion:1,state:'GENUINE_DATA_DESCRIPTOR_AND_FULL_READ_BOUNDARY_PASSED_V1',node:pins.node,dataUtilities:pins.files,manifestSha256:createHash('sha256').update(manifestBytes).digest('hex'),declaredRows:manifest.files.length,actualRowsRead:regularRows+streamRows,regularRows,streamRows,declaredBytes:manifest.files.reduce((n,r)=>n+r.bytes,0),actualBytes,all17BeforeRowsRejected:true,allCorrectedAndOtherRowsDescriptorAndByteBoundaryPassed:true,correctedRows:fixed,sourceOnly:true,genuineDataUtilitiesImported:true,bootstrapPreflightOrOracleInvoked:false,generatedJsImported:false,guestKeyGcOrNativeActionsInvoked:false,rootActivationCreated:false})+'\n');
