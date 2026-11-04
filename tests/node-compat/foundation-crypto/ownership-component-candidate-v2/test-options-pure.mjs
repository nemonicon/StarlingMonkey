// Pure actual options-caller seam. No loader/bootstrap/component/key/provider action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {workerOptions} from './build-worker.mjs';
import {componentOptions} from '../ownership-component-candidate-v1/abi.mjs';
import {authorityModel} from './guard.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),OLD=join(HERE,'../ownership-component-candidate-v1');let checks=0;const ck=(v,m)=>{assert(v,m);checks++;};
const indexRaw=await readFile(join(OLD,'index.json'));ck(createHash('sha256').update(indexRaw).digest('hex')==='eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30','authentic immutable donor index');const ix=JSON.parse(indexRaw);
async function source(name){const row=ix.files.find(v=>v.path===name);assert(row);const raw=await readFile(join(OLD,name));ck(raw.length===row.bytes&&createHash('sha256').update(raw).digest('hex')===row.sha256,'actual indexed source '+name);return raw;}
const p=JSON.parse(await source('prerequisites.json')),map=JSON.parse(await source('packaging-context.json')),oldWorker=new TextDecoder().decode(await source('build-worker.mjs')),oldParent=new TextDecoder().decode(await source('build.mjs')),wit=await readFile(p.wit.path,'utf8');
const pinsRaw=await readFile(p.reviewedNativePins.path);ck(createHash('sha256').update(pinsRaw).digest('hex')===p.reviewedNativePins.sha256,'actual reviewed normal-only pin DATA');const pin=JSON.parse(pinsRaw).variants['normal-off'];
const member=map.files.find(v=>v.path==='packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),adapter={path:join(map.publicationRoot,member.path),sha256:member.sha256,bytes:member.bytes};const adapterRaw=await readFile(adapter.path);ck(adapter.bytes===53512&&adapterRaw.length===53512&&createHash('sha256').update(adapterRaw).digest('hex')===adapter.sha256,'actual authenticated53512 adapter DATA');
const d={engine:{path:pin.enginePath,sha256:pin.engineSha256,bytes:pin.engineBytes}};ck(!Object.hasOwn(d,'adapter')&&oldParent.includes('const d={')&&!/const d=\{[^;]*\badapter:/.test(oldParent),'real parent source shape omitted adapter; test contains no forged private worker/auth state');
const oldCall=/const options=(componentOptions\(d,wit\));/.exec(oldWorker);ck(!!oldCall,'extract exact old actual worker call');const oldCaller=Function('componentOptions','d','wit','return '+oldCall[1]);assert.throws(()=>oldCaller(componentOptions,d,wit),TypeError);checks++;
const next=workerOptions(d,{adapter},wit);ck(next.engine===pin.enginePath&&next.preview2Adapter===adapter.path,'genuine new options caller uses authenticated packaging.adapter');ck(next.worldName==='validation'&&next.witWorld===wit&&next.selectedInterfaces.length===0&&next.disableFeatures.length===5&&next.enableAot===false&&Object.keys(next.env).length===0,'all inspected options preserved');
// Original caller record may lack adapter; the authoritative packaging tuple wins.
const poison=workerOptions({...d,adapter:{path:'/tmp/untrusted-adapter'}},{adapter},wit);ck(poison.preview2Adapter===adapter.path,'caller adapter cannot substitute authenticated packaging tuple');
const template=JSON.parse(await readFile(join(HERE,'future-component-authority.template.json')));assert.throws(()=>authorityModel(template,'a'.repeat(64)));checks++;ck(template.componentBuildAllowed===false&&template.componentSourceIndexSha256===null&&template.sourceIndependentReview===null,'new authority stays NULL/closed');
console.log(JSON.stringify({schemaVersion:1,state:'PURE_ACTUAL_ADAPTER_OPTIONS_CALLER_REGRESSION_PASSED',checks,oldExactCallerTypeError:true,newGenuineCallerOptionsPassed:true,actualAdapterSha256:adapter.sha256,actualAdapterBytes:adapter.bytes,oldWorkerOrComponentizerInvoked:false,bootstrapInvoked:false,keyOrCryptoInvoked:false,ownerActionsInvoked:false}));
