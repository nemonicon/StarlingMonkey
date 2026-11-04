// Exact existing actual runtime admission; no duplicate native backend.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),runtime=resolve(here,'../production-runtime-activated-v3');
const INPUTS_SHA='b6b4e79f4c13f2e844a8361618e2038d4aa176ad62dd1566a5c44b2f32ee6a3b',RUNTIME_SHA='7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function regular(path,expected,bytes){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const data=await readFile(path);assert.equal(hash(data),expected,path);if(bytes!==undefined)assert.equal(data.length,bytes);return data;}
async function sourceSeal(){const raw=await regular(join(here,'input-freeze.json'),INPUTS_SHA);const document=JSON.parse(raw);assert.equal(document.schemaVersion,1);let template;const seen=new Set();
 for(const row of document.inputs){const path=resolve(here,row.path);assert(!seen.has(path));seen.add(path);const data=await regular(path,row.sha256,row.bytes);if(path===join(here,'preflight.template.mjs'))template=data.toString();}
 assert.equal(typeof template,'string');assert.equal(await readFile(fileURLToPath(import.meta.url),'utf8'),template.replaceAll('@'+'INPUTS_SHA'+'@',INPUTS_SHA));return{path:join(here,'input-freeze.json'),sha256:INPUTS_SHA,files:seen.size};}
async function runtimeIndex(){const raw=await regular(join(runtime,'index.json'),RUNTIME_SHA);const document=JSON.parse(raw);assert.equal(document.state,'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED');assert.equal(document.runtimeAcceptanceClaim,false);
 for(const row of document.files){assert(!row.path.startsWith('/')&&row.path.split('/').every(value=>value&&value!=='.'&&value!=='..'));await regular(join(runtime,row.path),row.sha256,row.bytes);}return document;}
export async function tracePreflight(){
 const inputClosure=await sourceSeal();await runtimeIndex(); // Hash fixed index/data before importing any backend/tool/driver.
 const {classicPreflight}=await import(pathToFileURL(join(runtime,'runtime-preflight.mjs')));const native=await classicPreflight({variant:'normal-off'});
 assert.equal(native.pin.engineSha256,'b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4');assert.equal(native.pin.receiptSha256,'873c47f7d75776d836f642a971164b8751c6a53d56430c3a84f0cf3c161b8f58');
 assert.equal(native.metadata.entropyPolicy,'off');assert.equal(native.metadata.gcStress,false);assert.equal(native.metadata.debuggerEnabled,false);assert.equal(native.metadata.oomTesting,false);assert.equal(native.metadata.classicStreamsEnabled,true);
 const nativeRecheck=native.recheck;async function recheck(){await nativeRecheck();await runtimeIndex();await sourceSeal();}
 await recheck();return{...native,recheck,traceSourceAdmission:{state:'EXACT_SOURCE_AND_ACTUAL_CLASSIC342_NORMAL_OFF_ADMITTED_NOT_EXECUTED',inputClosure,runtimeIndexSha256:RUNTIME_SHA,sourceFilesVerified:342}};
}
