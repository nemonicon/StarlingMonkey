// Actual v2 native admission plus this separate HTTP source closure.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {classicPreflight} from '../../production-runtime-activated-v2/runtime-preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url));
export const hash=data=>createHash('sha256').update(data).digest('hex');
export async function verifyInputClosure({manifestPath=join(here,'../input-freeze.json'),expectedSha256}={}){
  const bytes=await readFile(manifestPath),sha256=hash(bytes);
  if(expectedSha256!==undefined)assert.equal(sha256,expectedSha256,'HTTP source manifest changed before parsing');
  const rows=JSON.parse(bytes).inputs,seen=new Set();
  for(const row of rows){const path=resolve(dirname(manifestPath),row.path);assert(!seen.has(path));seen.add(path);
    const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);
    const data=await readFile(path);assert.equal(hash(data),row.sha256,path);assert.equal(data.length,row.bytes,path);}
  return{path:resolve(manifestPath),sha256,files:rows.length};
}
export async function verifyProductionTicks({gcStress=false,entropyPolicy='runtime-only'}={}){
  assert.equal(gcStress,false);assert.equal(entropyPolicy,'runtime-only');
  const actual=await classicPreflight({variant:'normal-runtime'});
  assert.equal(actual.metadata.classicStreamsEnabled,true);
  assert.equal(actual.metadata.entropyPolicy,'runtime-only');assert.equal(actual.metadata.gcStress,false);
  const inputClosure=await verifyInputClosure(),manifestPath=inputClosure.path,expectedManifest=inputClosure.sha256;
  for(const[key,value]of Object.entries({NODE_COMPAT_ENGINE:actual.enginePath,NODE_COMPAT_ENGINE_SOURCE_ROOT:actual.sourceRoot,NODE_COMPAT_ENGINE_METADATA:actual.enginePath+'.build.json'})){
    if(process.env[key])assert.equal(resolve(process.env[key]),value);process.env[key]=value;
  }
  const nativeRecheck=actual.recheck;
  async function recheck(){await nativeRecheck();await verifyInputClosure({manifestPath,expectedSha256:expectedManifest});}
  const report={state:'ACTUAL_CLASSIC_COMBINED_HTTP_NATIVE_SOURCE_ADMISSION',engineSha256:actual.pin.engineSha256,
    engineReceiptSha256:actual.pin.receiptSha256,sourceFilesVerified:342,gcStress:false,entropyPolicy,inputClosure,
    scope:'Source/config admission only; not component or host acceptance'};
  await recheck();return{...actual,engine:actual.enginePath,report,recheck};
}
export async function requireFreshOutput(variable){assert(process.env[variable]);const path=resolve(process.env[variable]);
  try{await lstat(path);assert.fail('Output exists: '+path);}catch(error){if(error.code!=='ENOENT')throw error;}return path;}
export async function completeRegression(variable,admission){await admission.recheck();
  await writeFile(join(resolve(process.env[variable]),'production-admission-complete.json'),JSON.stringify({...admission.report,
    sourceInputsRecheckedAfterRun:true,requiresIndependentTerminalExitZero:true,runtimeAcceptanceClaim:false},null,2)+'\n',{flag:'wx'});}
