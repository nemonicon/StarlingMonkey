// Raw diagnostic-only fixed artifact gate. No package/component/guest imports.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const hash=data=>createHash('sha256').update(data).digest('hex');
const SHA=/^[0-9a-f]{64}$/;
export function selectPin(document,{variant,recipeSha256}){
 assert(document&&typeof document==='object');assert.equal(document.schemaVersion,1);
 assert.equal(document.state,'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2','Null/unreviewed benchmark pins stop before artifacts/loaders');
 assert(['benchmark-classic-on','benchmark-classic-off'].includes(variant));
 const pin=document.variants?.[variant];assert(pin&&typeof pin==='object');
 assert.equal(pin.state,'reviewed-classic-trace-benchmark-diagnostic-freeze');assert.equal(pin.variant,variant);
 assert.equal(pin.recipeSha256,recipeSha256);assert.equal(pin.sourceFiles,342);assert.equal(pin.addonFiles,2);
 assert.equal(pin.sourceContractVersion,'sm-classic-trace-source-v1');
 for(const name of ['engineSha256','metadataSha256','freezeReceiptSha256','sourceIndexSha256'])assert(SHA.test(pin[name]),name);
 assert(Number.isSafeInteger(pin.engineBytes)&&pin.engineBytes>8);return structuredClone(pin);
}
async function regular(path,expected){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const raw=await readFile(path);assert.equal(hash(raw),expected,path);return raw;}
export async function diagnosticPreflight({variant='benchmark-classic-on',reviewedPinsPath=join(here,'reviewed-pins.json'),reviewedPinsSha256,sourceRoot}={}){
 const pinsPath=resolve(reviewedPinsPath),raw=await readFile(pinsPath);
 if(reviewedPinsSha256!==undefined){assert(SHA.test(reviewedPinsSha256));assert.equal(hash(raw),reviewedPinsSha256);}
 const contract=JSON.parse(await readFile(join(here,'contract.json')));
 const pin=selectPin(JSON.parse(raw),{variant,recipeSha256:contract.recipeSha256});
 assert(SHA.test(reviewedPinsSha256??''),'Explicit exact Root-reviewed authority digest required');
 assert.equal(typeof sourceRoot,'string','Explicit containing corrected sourceRoot required');
 const containingRoot=resolve(here,'../../../..');assert.equal(resolve(sourceRoot),containingRoot);
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 const root='/tmp/starling-node-compat/classic-benchmark-trace-v2-artifacts/native-freeze';assert.equal(pin.freezeRoot,root);
 const indexSha=pin.sourceIndexSha256,pinSha=hash(raw),freezePath=join(root,variant+'-freeze-receipt.json');
 async function verify(){
  await regular(pinsPath,pinSha);await regular(join(here,'index.json'),indexSha);await regular(freezePath,pin.freezeReceiptSha256);
  const child=spawnSync('python3',[join(here,'verify-frozen.py'),variant,pin.freezeReceiptSha256,indexSha,containingRoot],{encoding:'utf8',timeout:55000,maxBuffer:2*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  assert.equal(child.status,0,child.error?.message??child.stderr);const result=JSON.parse(child.stdout);
  for(const key of ['engineSha256','engineBytes','metadataSha256','freezeReceiptSha256','recipeSha256'])assert.equal(result[key],pin[key],key);
  return result;
 }
 const result=await verify();
 const metadata=JSON.parse(await regular(join(root,variant+'.engine.wasm.build.json'),pin.metadataSha256));
 const {rawBuiltinManifests}=await import('./metadata-admission.mjs');
 const builtinManifests=await rawBuiltinManifests(metadata,variant,result.sourceRoot);
 for(const[key,value]of Object.entries({NODE_COMPAT_ENGINE:result.enginePath,NODE_COMPAT_ENGINE_SOURCE_ROOT:result.sourceRoot,NODE_COMPAT_ENGINE_METADATA:join(root,variant+'.engine.wasm.build.json')})){
  if(process.env[key])assert.equal(resolve(process.env[key]),value);}
 const frozenPin=structuredClone(pin),recheck=async()=>{await verify();};
 return Object.freeze({enginePath:result.enginePath,sourceRoot:result.sourceRoot,metadata,builtinManifests,
  diagnosticExternalIds:Object.freeze(['starling:test-classic-benchmark']),pin:frozenPin,variant,recheck,
  scope:'Diagnostic-only real-artifact/source gate; not production admission, guest correctness or measurement.'});
}
