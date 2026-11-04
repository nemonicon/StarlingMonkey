// Delegate the unchanged API to the separately reviewed actual runtime family.
// This file implements source/authority binding only, not a second native backend.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url)),RUNTIME=resolve(HERE,'../production-runtime-activated-v2');
const AUTHORITY_SHA='7fdf8849f7169a1496f43a6fd60a43c358181224c992564396addb8fd0a7cae2',INPUTS_SHA='ab2e88236065d4f85be2ee6aa28792ea12bd5ee9198346b913f334d294e817a3',RUNTIME_INDEX_SHA='8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a';
const PINS_SHA='c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e';
const REVIEW_SHA='1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const labels=['normal-off','normal-runtime','gc-off','disabled-off'];
async function regular(path,sha,bytes){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const data=await readFile(path);assert.equal(hash(data),sha,path);if(bytes!==undefined)assert.equal(data.length,bytes,path);return data;}
async function indexedRuntime(){
 assert((await lstat(RUNTIME)).isDirectory()&&!(await lstat(RUNTIME)).isSymbolicLink());
 const raw=await regular(join(RUNTIME,'index.json'),RUNTIME_INDEX_SHA),index=JSON.parse(raw); // Hash before rows/import.
 assert.equal(index.schemaVersion,1);assert.equal(index.state,'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED');assert.equal(index.runtimeAcceptanceClaim,false);
 const seen=new Set();for(const row of index.files){assert(typeof row.path==='string'&&!isAbsolute(row.path)&&!row.path.includes('\\')&&!row.path.includes('\0')&&row.path.split('/').every(part=>part&&part!=='.'&&part!=='..'));
  assert(!seen.has(row.path));seen.add(row.path);let path=RUNTIME;for(const part of row.path.split('/')){path=join(path,part);assert(!(await lstat(path)).isSymbolicLink());}await regular(path,row.sha256,row.bytes);}
 for(const name of ['runtime-preflight.mjs','runtime-pins.json','root-review-receipt.json','source-receipt.json','input-freeze.json'])assert(seen.has(name));
 return index;
}
async function authority(index){
 const binding=JSON.parse(await regular(join(HERE,'activation-reference.json'),AUTHORITY_SHA));
 assert.equal(binding.state,'ROOT_REVIEWED_CLASSIC342_REPLAY_AUTHORITY_BOUND_NOT_EXECUTED');assert.equal(binding.runtimeIndexSha256,RUNTIME_INDEX_SHA);
 assert.equal(binding.reviewedPinsSha256,PINS_SHA);assert.equal(binding.rootReviewReceiptSha256,REVIEW_SHA);assert.equal(binding.runtimeRoot,RUNTIME);
 const pinBytes=await regular(join(HERE,'runtime-pins.json'),PINS_SHA),reviewBytes=await regular(join(HERE,'root-review-receipt.json'),REVIEW_SHA);
 assert.deepEqual(await regular(join(RUNTIME,'runtime-pins.json'),PINS_SHA),pinBytes);
 assert.deepEqual(await regular(join(RUNTIME,'root-review-receipt.json'),REVIEW_SHA),reviewBytes);
 const pins=JSON.parse(pinBytes),review=JSON.parse(reviewBytes);
 assert.equal(pins.state,'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1');assert.equal(review.state,'ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1');assert.equal(review.reviewedPinsSha256,PINS_SHA);
 assert.deepEqual(Object.keys(pins.variants).sort(),[...labels].sort());assert.deepEqual(Object.keys(review.variants).sort(),[...labels].sort());
 const sourceRow=index.files.find(row=>row.path==='source-receipt.json');
 const source=JSON.parse(await regular(join(RUNTIME,'source-receipt.json'),sourceRow.sha256,sourceRow.bytes));
 assert.equal(source.state,'ACTUAL_REVIEWED_CLASSIC_RUNTIME_FAMILY_CREATED_NOT_EXECUTED');assert.equal(source.pinsSha256,PINS_SHA);assert.equal(source.rootReviewSha256,REVIEW_SHA);
 assert.equal(source.schemaVersion,1);assert.equal(source.engineMetadataRewritten,false);assert.equal(source.componentOrHostExecuted,false);assert.equal(source.runtimeAcceptanceClaim,false);
 for(const label of labels){for(const name of ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']){
  assert.equal(pins.variants[label][name],review.variants[label][name]);assert.equal(pins.variants[label][name],source.actualArtifacts[label][name]);}}
 return pins;
}
async function ownSeal(){
 const raw=await regular(join(HERE,'input-freeze.json'),INPUTS_SHA),document=JSON.parse(raw); // Hash before following changed rows.
 let template;const seen=new Set();for(const row of document.inputs){assert(typeof row.path==='string'&&!row.path.includes('\0'));const path=resolve(HERE,row.path);assert(!seen.has(path));seen.add(path);const bytes=await regular(path,row.sha256,row.bytes);if(path===join(HERE,'native-preflight.template.mjs'))template=bytes.toString();}
 assert.equal(typeof template,'string');
 const rendered=template.replaceAll('@'+'AUTHORITY_SHA'+'@',AUTHORITY_SHA).replaceAll('@'+'INPUTS_SHA'+'@',INPUTS_SHA).replaceAll('@'+'RUNTIME_INDEX_SHA'+'@',RUNTIME_INDEX_SHA).replaceAll('@'+'RUNTIME_FAMILY'+'@',RUNTIME.split('/').at(-1));
 await regular(fileURLToPath(import.meta.url),hash(Buffer.from(rendered)));
 return document.inputs.length;
}
export async function classicPreflight({variant='normal-off'}={}){
 assert(labels.includes(variant));assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 const index=await indexedRuntime(),pins=await authority(index); // Exact runtime index/data precede the import.
 const {classicPreflight:preflight}=await import(pathToFileURL(join(RUNTIME,'runtime-preflight.mjs')));
 const native=await preflight({variant}); // Existing actual342 gate and whole tool/source closure, no metadata projection.
 assert.deepEqual(native.pin,pins.variants[variant]);
 await ownSeal();
 const nativeRecheck=native.recheck;
 async function recheck(){await nativeRecheck();const index=await indexedRuntime();await authority(index);await ownSeal();}
 await recheck();return Object.freeze({...native,recheck});
}
