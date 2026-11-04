// Source activation supplies literals only after separate actual pair review.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {verifyConsumedSeal} from './consumed.mjs';
const here=dirname(fileURLToPath(import.meta.url)),CONFIG_SHA='aa4ef27e904435c4ee8ab0ea6ee7e9af3dd3a4b8604c4c257f8725fae893472f',INPUTS_SHA='e8912582589188583c218ceab5f6e94ad603ca16e78b1c094db64e4266fdb8dd';
const hash=raw=>createHash('sha256').update(raw).digest('hex');
async function regular(path,digest){const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink());const raw=await readFile(path);assert.equal(hash(raw),digest,path);return raw;}
export async function executionPreflight({variant}={}){
 const raw=await regular(join(here,'activation.json'),CONFIG_SHA),config=JSON.parse(raw);
 assert.equal(config.state,'ROOT_REVIEWED_COMMON_BYTE_SOURCE_ACTIVATION_V1');assert.equal(config.timingAllowed,false);
 assert(['benchmark-classic-on','benchmark-classic-off'].includes(variant));
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
 const producer=config.producerRoot,pairPath=join(here,'reviewed-pair.json'),pairSha=config.pairSha256;
 await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});
 const index=JSON.parse(await regular(join(producer,'index.json'),config.producerIndexSha256));
 const rows=index.files.map(row=>({...row}));assert.equal(rows.length,40);
 for(const row of rows)await regular(join(producer,row.path),row.sha256);
 await regular(pairPath,pairSha);await regular(join(here,'root-pair-review.json'),config.rootReviewSha256);
 const {diagnosticPreflight}=await import(pathToFileURL(join(producer,'runtime-preflight.mjs')));
 const native=await diagnosticPreflight({variant,reviewedPinsPath:pairPath,reviewedPinsSha256:pairSha,sourceRoot:config.sourceRoot});
 for(const key of ['engineSha256','engineBytes','metadataSha256','freezeReceiptSha256'])assert.equal(native.pin[key],config.actual[variant][key]);
 assert.equal(native.metadata.diagnosticOnly,true);assert.equal(native.metadata.gcStress,false);assert.equal(native.metadata.classicStreamsEnabled,variant==='benchmark-classic-on');
 const nativeRecheck=native.recheck;
 async function recheck(){await regular(join(here,'activation.json'),CONFIG_SHA);await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});await regular(pairPath,pairSha);await regular(join(producer,'index.json'),config.producerIndexSha256);for(const row of rows)await regular(join(producer,row.path),row.sha256);await nativeRecheck();}
 await recheck();return Object.freeze({...native,recheck,toolSourceRoot:config.sourceRoot,pairSha256:pairSha});
}
