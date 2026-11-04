// Future fixed authority before backend/toolchain/packager or output access.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {selectActivation,PRODUCER_INDEX,RECIPE} from './activation-contract.mjs';
import {verifyConsumedSeal} from './consumed.mjs';
const here=dirname(fileURLToPath(import.meta.url)),CONFIG_SHA='3f1c24218c592f160b92a24c96539d3913888efd1302f66950df352013222e92',INPUTS_SHA='406946e8b609c7ff91c05fc80e499a4e48e936a0cb10f506944d21d221309639';
const hash=data=>createHash('sha256').update(data).digest('hex');
async function regular(path,expected,bytes){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const raw=await readFile(path);assert.equal(hash(raw),expected,path);if(bytes!==undefined)assert.equal(raw.length,bytes);return raw;}
export async function correctnessPreflight(){
 const configPath=join(here,'activation-template.json'),raw=await regular(configPath,CONFIG_SHA);
 const config=selectActivation(JSON.parse(raw)); // Current NULL authority fails here, before any external loader/output.
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
 const root=config.sourceRoot,producer=config.producerRoot;assert.equal(resolve(producer,'../../../..'),root);assert.equal(producer,join(root,'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3'));
 async function seal(){return verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});}
 await seal();
 const index=JSON.parse(await regular(join(producer,'index.json'),PRODUCER_INDEX));
 const frozenRows=index.files.map(row=>({...row}));for(const row of frozenRows)await regular(join(producer,row.path),row.sha256,row.bytes);
 const pinsPath=config.reviewedPinsPath,pinsSha=config.reviewedPinsSha256;
 const authority=JSON.parse(await regular(pinsPath,pinsSha));assert.equal(authority.state,'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3');
 const {diagnosticPreflight}=await import(pathToFileURL(join(producer,'runtime-preflight.mjs')));
 const native=await diagnosticPreflight({variant:'benchmark-classic-on',reviewedPinsPath:pinsPath,reviewedPinsSha256:pinsSha,sourceRoot:root});
 assert.equal(native.pin.recipeSha256,RECIPE);assert.equal(native.metadata.diagnosticOnly,true);assert.equal(native.metadata.classicStreamsEnabled,true);assert.equal(native.metadata.gcStress,false);
 assert.deepEqual(native.diagnosticExternalIds,['starling:test-classic-benchmark']);
 for(const key of ['engineSha256','metadataSha256','freezeReceiptSha256','engineBytes','sourceFiles','addonFiles'])assert.equal(native.pin[key],config.reviewedActualEngine[key],key);
 const nativeRecheck=native.recheck;
 async function recheck(){await regular(configPath,CONFIG_SHA);await seal();await regular(pinsPath,pinsSha);await regular(join(producer,'index.json'),PRODUCER_INDEX);for(const row of frozenRows)await regular(join(producer,row.path),row.sha256,row.bytes);await nativeRecheck();}
 await recheck();return Object.freeze({...native,recheck,toolSourceRoot:root,
  correctnessScope:'20 original full-trace workloads and14 original valid boundaries; no timing or queue-counter observability.'});
}
