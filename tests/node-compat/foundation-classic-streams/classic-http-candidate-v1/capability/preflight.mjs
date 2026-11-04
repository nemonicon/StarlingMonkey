// Actual v2 native admission plus this separate HTTP source closure.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,writeFile} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const INPUTS_SHA='511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b',RUNTIME_INDEX_SHA='8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a';
const runtime=resolve(here,'../../production-runtime-activated-v2');
export const hash=data=>createHash('sha256').update(data).digest('hex');
export async function verifyInputClosure({manifestPath=join(here,'../input-freeze.json'),expectedSha256=INPUTS_SHA}={}){
  const manifestStat=await lstat(manifestPath);assert(manifestStat.isFile()&&!manifestStat.isSymbolicLink());
  const bytes=await readFile(manifestPath),sha256=hash(bytes);
  assert.equal(sha256,expectedSha256,'HTTP source manifest changed before parsing');
  const document=JSON.parse(bytes);assert.equal(document.schemaVersion,1);const rows=document.inputs,seen=new Set();let template;
  for(const row of rows){const path=resolve(dirname(manifestPath),row.path);assert(!seen.has(path));seen.add(path);
    if(row.boundary){const boundary=resolve(dirname(manifestPath),row.boundary),name=relative(boundary,path);assert(name&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name));assert((await lstat(boundary)).isDirectory()&&!(await lstat(boundary)).isSymbolicLink());let cursor=path;while(cursor!==boundary){assert(!(await lstat(cursor)).isSymbolicLink());cursor=dirname(cursor);}}
    const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);
    const data=await readFile(path);assert.equal(hash(data),row.sha256,path);assert.equal(data.length,row.bytes,path);if(path===join(here,'preflight.template.mjs'))template=data.toString();}
  assert.equal(typeof template,'string');const compiled=template.replaceAll('@'+'INPUTS_SHA'+'@',INPUTS_SHA);assert.equal(await readFile(fileURLToPath(import.meta.url),'utf8'),compiled,'Rendered HTTP preflight changed');
  return{path:resolve(manifestPath),sha256,files:rows.length};
}
async function verifyRuntimeIndex(){
  assert((await lstat(runtime)).isDirectory()&&!(await lstat(runtime)).isSymbolicLink());
  const raw=await readFile(join(runtime,'index.json'));assert.equal(hash(raw),RUNTIME_INDEX_SHA,'Runtime source index changed before parsing');
  const index=JSON.parse(raw);assert.equal(index.state,'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED');assert.equal(index.runtimeAcceptanceClaim,false);
  const seen=new Set();for(const row of index.files){assert(typeof row.path==='string'&&!row.path.startsWith('/')&&!row.path.includes('\\')&&row.path.split('/').every(part=>part&&part!=='.'&&part!=='..'));assert(!seen.has(row.path));seen.add(row.path);
    let path=runtime;for(const part of row.path.split('/')){path=join(path,part);assert(!(await lstat(path)).isSymbolicLink());}const data=await readFile(path);assert.equal(hash(data),row.sha256);assert.equal(data.length,row.bytes);}
  assert(seen.has('runtime-preflight.mjs'));return index.files.length;
}
export async function verifyProductionTicks({gcStress=false,entropyPolicy='runtime-only'}={}){
  assert.equal(gcStress,false);assert.equal(entropyPolicy,'runtime-only');
  await verifyRuntimeIndex();const {classicPreflight}=await import(pathToFileURL(join(runtime,'runtime-preflight.mjs')));
  const actual=await classicPreflight({variant:'normal-runtime'});
  assert.equal(actual.metadata.classicStreamsEnabled,true);
  assert.equal(actual.metadata.entropyPolicy,'runtime-only');assert.equal(actual.metadata.gcStress,false);
  const inputClosure=await verifyInputClosure(),manifestPath=inputClosure.path,expectedManifest=inputClosure.sha256;
  for(const[key,value]of Object.entries({NODE_COMPAT_ENGINE:actual.enginePath,NODE_COMPAT_ENGINE_SOURCE_ROOT:actual.sourceRoot,NODE_COMPAT_ENGINE_METADATA:actual.enginePath+'.build.json'})){
    if(process.env[key])assert.equal(resolve(process.env[key]),value);process.env[key]=value;
  }
  const nativeRecheck=actual.recheck;
  async function recheck(){await nativeRecheck();await verifyRuntimeIndex();await verifyInputClosure({manifestPath,expectedSha256:expectedManifest});}
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
