// Genuine355 raw validation only. No operational admission or metadata projection.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {verifyConsumedSeal} from './consumed.mjs';
import {verifyComponentToolClosure,componentToolRoot} from './component-tools.mjs';
const here=dirname(fileURLToPath(import.meta.url)),CONFIG_SHA='@CONFIG_SHA@',INPUTS_SHA='@INPUTS_SHA@',hash=raw=>createHash('sha256').update(raw).digest('hex');
async function regular(path,digest){const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink());const bytes=await readFile(path);assert.equal(hash(bytes),digest,path);return bytes;}
const freeze=value=>{if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}return value;};
export async function validationPreflight({variant='normal-off'}={}){
 const config=freeze(JSON.parse(await regular(join(here,'activation.json'),CONFIG_SHA)));
 assert.equal(config.state,'ROOT_REVIEWED_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_V1');assert.equal(config.operationalAdmission,false);
 assert(['normal-off','gc-off','disabled-off'].includes(variant));assert(config.actual[variant],'Variant authority remains unconfigured');
 assert.equal(config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot,'../../../..'));assert.equal(config.nativeConfiguredSourceRoot,'/private/tmp/starling-node-compat/consumers-source-v2');
 assert.equal(config.componentToolRoot,componentToolRoot);assert.notEqual(componentToolRoot,config.nativeConfiguredSourceRoot);
 await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});
 const closure=freeze(JSON.parse(await regular(join(here,'component-tool-closure.json'),config.componentToolClosureSha256)));await verifyComponentToolClosure(closure);
 const nativeIndex=await regular(join(config.bootstrapRoot,'index.json'),config.bootstrapIndexSha256),rows=JSON.parse(nativeIndex).files.map(row=>Object.freeze({...row}));
 for(const row of rows)await regular(join(config.bootstrapRoot,row.path),row.sha256);
 const {consumersBootstrapPreflight}=await import(pathToFileURL(join(config.bootstrapRoot,'artifact-tools/bootstrap-preflight.mjs')));
 const native=await consumersBootstrapPreflight({variant,reviewedPinsPath:join(here,'reviewed-pins.json'),reviewedPinsSha256:config.pinsSha256,rootReviewPath:join(here,'root-review.json'),rootReviewSha256:config.rootReviewSha256});
 assert.equal(native.validationBootstrapOnly,true);assert.equal(native.operationalAdmission,false);assert.equal(native.metadata.sourceManifest.length,355);
 assert.equal(native.metadata.streamConsumersEnabled,variant!=='disabled-off');assert.equal(native.metadata.zlibEnabled,true);assert.equal(native.metadata.gcStress,variant==='gc-off');assert.equal(native.metadata.entropyPolicy,'off');
 assert.equal(native.metadata.sourceManifest.find(row=>row.path==='builtins/web/text-codec/text-decoder.cpp')?.sha256,'4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c');
 for(const key of['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256'])assert.equal(native.pin[key],config.actual[variant][key]);
 const nativeRecheck=native.recheck,selected=freeze(structuredClone(native.selectedManifests)),enginePath=native.enginePath;
 const sourceRoot=native.sourceRoot;assert.equal(sourceRoot,'/tmp/starling-node-compat/production-consumers-v1/native-freeze/source');
 async function recheck(){await regular(join(here,'activation.json'),CONFIG_SHA);await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});await verifyComponentToolClosure(closure);await regular(join(config.bootstrapRoot,'index.json'),config.bootstrapIndexSha256);for(const row of rows)await regular(join(config.bootstrapRoot,row.path),row.sha256);await nativeRecheck();}
 await recheck();return Object.freeze({...native,enginePath,sourceRoot,selectedManifests:selected,recheck,nativeConfiguredSourceRoot:config.nativeConfiguredSourceRoot,componentToolRoot,toolSourceRoot:componentToolRoot,normalEngineSha256:config.actual['normal-off'].engineSha256,liveAdapter:freeze({...config.liveAdapter}),liveWit:freeze(structuredClone(config.liveWit)),sourceFamilyConfigSha256:CONFIG_SHA});
}
