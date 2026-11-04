// Raw350 validation bootstrap, never operational codec admission.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {verifyConsumedSeal} from './consumed.mjs';
const here=dirname(fileURLToPath(import.meta.url)),CONFIG_SHA='@CONFIG_SHA@',INPUTS_SHA='@INPUTS_SHA@',hash=raw=>createHash('sha256').update(raw).digest('hex');
async function regular(path,digest){const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink());const raw=await readFile(path);assert.equal(hash(raw),digest,path);return raw;}
const freeze=value=>{if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}return value;};
export async function validationPreflight({variant='normal-off'}={}){
 const config=JSON.parse(await regular(join(here,'activation.json'),CONFIG_SHA));assert.equal(config.state,'ROOT_REVIEWED_ZLIB350_COMPONENT_VALIDATION_SOURCE_V1');assert.equal(config.operationalAdmission,false);
 assert(['normal-off','gc-off','disabled-off'].includes(variant));assert(config.actual[variant],'Requested validation variant remains unconfigured');
 await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});
 const rows=JSON.parse(await regular(join(config.bootstrapRoot,'index.json'),config.bootstrapIndexSha256)).files.map(row=>Object.freeze({...row}));
 for(const row of rows)await regular(join(config.bootstrapRoot,row.path),row.sha256);
 const {zlibBootstrapPreflight}=await import(pathToFileURL(join(config.bootstrapRoot,'artifact-tools/bootstrap-preflight.mjs')));
 const native=await zlibBootstrapPreflight({variant,reviewedPinsPath:join(here,'reviewed-pins.json'),reviewedPinsSha256:config.pinsSha256,rootReviewPath:join(here,'root-review.json'),rootReviewSha256:config.rootReviewSha256});
 assert.equal(native.validationBootstrapOnly,true);assert.equal(native.operationalAdmission,false);assert.equal(native.metadata.zlibEnabled,variant!=='disabled-off');assert.equal(native.metadata.gcStress,variant==='gc-off');
 for(const key of['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256'])assert.equal(native.pin[key],config.actual[variant][key]);
 const nativeRecheck=native.recheck,selected=freeze(structuredClone(native.selectedManifests));
 async function recheck(){await regular(join(here,'activation.json'),CONFIG_SHA);await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});await regular(join(config.bootstrapRoot,'index.json'),config.bootstrapIndexSha256);for(const row of rows)await regular(join(config.bootstrapRoot,row.path),row.sha256);await nativeRecheck();}
 await recheck();return Object.freeze({...native,selectedManifests:selected,recheck,toolSourceRoot:config.toolSourceRoot,expectedHeader:config.headers[variant],sourceCoupledInferenceOnly:true});
}
