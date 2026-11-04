// All three replay modes use the real342 fixed-artifact gate first.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {classicPreflight} from '../native-preflight.mjs';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export async function verifyInputClosure({manifestPath=join(root,'input-freeze.json'),expectedSha256}={}){
 const stat=await lstat(manifestPath);assert(stat.isFile()&&!stat.isSymbolicLink());const bytes=await readFile(manifestPath),sha256=hash(bytes);
 if(expectedSha256!==undefined)assert.equal(sha256,expectedSha256,'Replay source seal changed');
 const document=JSON.parse(bytes);assert.equal(document.schemaVersion,1);const seen=new Set();
 for(const row of document.inputs){assert(typeof row.path==='string'&&!row.path.includes('\0')&&!seen.has(row.path));seen.add(row.path);const path=resolve(dirname(manifestPath),row.path),stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink());const data=await readFile(path);assert.equal(data.length,row.bytes);assert.equal(hash(data),row.sha256,path);}
 return{path:manifestPath,sha256,files:seen.size};
}
export async function verifyProductionTicks({gcStress=false,entropyPolicy='off'}={}){
 assert.equal(typeof gcStress,'boolean');assert(['off','runtime-only'].includes(entropyPolicy));assert(!(gcStress&&entropyPolicy==='runtime-only'),'RuntimeGC is unavailable');
 const variant=entropyPolicy==='runtime-only'?'normal-runtime':gcStress?'gc-off':'normal-off';
 const production=await classicPreflight({variant}); // Null stops before a loader/output/historical-control read.
 assert.equal(production.metadata.classicStreamsEnabled,true);
 process.env.NODE_COMPAT_ENGINE=production.enginePath;process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT=production.sourceRoot;
 assert(process.env.NODE_COMPAT_WASMTIME,'Explicit stock Wasmtime42 executable required');
 const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME),wasmtimeStat=await lstat(wasmtime);assert(wasmtimeStat.isFile()&&!wasmtimeStat.isSymbolicLink());
 assert.equal(hash(await readFile(wasmtime)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
 for(const[key,value]of Object.entries({NODE_COMPAT_TOOLCHAIN:'/tmp/starling-node-compat/native-toolchain-lock',NODE_COMPAT_COMPONENTIZE_MODULE:'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js'})){
  if(process.env[key])assert.equal(resolve(process.env[key]),value,key);process.env[key]=value;
 }
 const inputClosure=await verifyInputClosure();
 const expectedManifest=inputClosure.sha256,path=inputClosure.path,privateRecheck=production.recheck;
 async function recheck(){await privateRecheck();await verifyInputClosure({manifestPath:path,expectedSha256:expectedManifest});
  assert.equal(hash(await readFile(wasmtime)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');}
 const report={state:'fixed-classic342-regression-admission-passed',variant,engineSha256:production.pin.engineSha256,
  sourceFilesVerified:342,recipeSha256:production.pin.recipeSha256,freezeReceiptSha256:production.pin.freezeReceiptSha256,
  entropyPolicy,gcStress,inputClosure,scope:'Read-only actual artifact/source/config admission; no runtime result or historical-source projection'};
 return{...production,engine:production.enginePath,engineSha256:production.pin.engineSha256,sourceFilesVerified:342,report,recheck};
}
export async function requireFreshOutput(variable){assert(process.env[variable],'Choose a fresh output: '+variable);const output=resolve(process.env[variable]);try{await lstat(output);assert.fail('Output exists: '+output);}catch(error){if(error.code!=='ENOENT')throw error;}return output;}
export async function completeRegression(variable,admission){await admission.recheck();await writeFile(join(resolve(process.env[variable]),'production-admission-complete.json'),JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});}
