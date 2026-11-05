// Root harness: authenticates the retained API before importing it. No guest runs.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {readFile,lstat,readdir,realpath,open,mkdir} from 'node:fs/promises';
import {dirname,join,isAbsolute,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const ENTRY=fileURLToPath(import.meta.url);
const SOURCE='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-retained-bootstrap-candidate-v1';
const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-secret-retained-preflight-v1';
const SOURCE_SHA='c47ac2f9b3c89a5b4ed3f91acfa96ea30443d8d459adae4a21739d3102048d7c';
const PEER_SHA='0372effb76f052f0021865606e3d21c0abb0e92feb3a9bb71c38c2ae3837217c';
const API_SHA='e99896b1dad126df83ebe17046c92e39a943c319af4d5767e4267dd046517c35';
const hash=b=>createHash('sha256').update(b).digest('hex');
const initial=new Map(),families=[];
const identity=s=>[s.dev,s.ino,s.size,s.mtimeMs,s.ctimeMs];
async function pinned(row){
  assert(row&&typeof row.path==='string'&&isAbsolute(row.path)&&resolve(row.path)===row.path);
  const a=await lstat(row.path),physical=await realpath(row.path);assert(a.isFile()&&!a.isSymbolicLink());
  const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(row.path)){h.update(b);bytes+=b.length;}
  const z=await lstat(row.path);assert.deepEqual(identity(a),identity(z));assert.equal(await realpath(row.path),physical);
  assert.equal(bytes,row.bytes);assert.equal(h.digest('hex'),row.sha256);
  const value={row,identity:identity(z),physical};if(initial.has(row.path))assert.deepEqual(value,initial.get(row.path));initial.set(row.path,value);return row;
}
async function json(row){await pinned(row);assert(row.bytes<=32*1024*1024);const b=await readFile(row.path);assert.equal(hash(b),row.sha256);return JSON.parse(b);}
async function tree(root,names){
  const s=await lstat(root);assert(s.isDirectory()&&!s.isSymbolicLink());const actual=[];
  async function walk(path,prefix=''){for(const n of await readdir(path)){const p=join(path,n),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p,prefix+n+'/');else{assert(s.isFile());actual.push(prefix+n);}}}
  await walk(root);assert.deepEqual(actual.sort(),[...names].sort());
}
async function family(index){
  const d=await json(index),root=dirname(index.path),names=new Set(['index.json']);assert.equal(d.schemaVersion,1);
  for(const r of d.files){assert(typeof r.path==='string'&&!isAbsolute(r.path)&&r.path.split('/').every(p=>p&&p!=='.'&&p!=='..'));assert(!names.has(r.path));names.add(r.path);await pinned({...r,path:join(root,r.path)});}
  await tree(root,names);families.push({root,names});return d;
}
async function recheckInputs(){for(const {row}of [...initial.values()])await pinned(row);for(const {root,names}of families)await tree(root,names);}
async function write(name,data){
  const path=join(OUTPUT,name),raw=Buffer.from(typeof data==='string'?data:JSON.stringify(data,null,2)+'\n');
  const f=await open(path,'wx',0o600);try{await f.writeFile(raw);await f.sync();}finally{await f.close();}
  return {path,sha256:hash(raw),bytes:raw.length};
}
assert.equal(process.version,'v22.14.0');assert.equal(process.execArgv.length,0);assert.equal(process.argv.length,3);
for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])assert(!process.env[k]);
const configDescriptor=JSON.parse(process.argv[2]),cfg=await json(configDescriptor);
assert.equal(cfg.state,'SECRET355_RETAINED_BOOTSTRAP_CONFIG_V1');assert.equal(cfg.sourceIndex.sha256,SOURCE_SHA);assert.equal(cfg.sourceIndex.path,join(SOURCE,'index.json'));
await family(cfg.sourceIndex);
const ownIndex=JSON.parse(await readFile(cfg.sourceIndex.path));
const own=name=>{const r=ownIndex.files.find(r=>r.path===name);assert(r);return {...r,path:join(SOURCE,name)};};
const inputs=await json(own('source-inputs.json'));assert.equal(inputs.files.length,28208);
for(const row of inputs.files)await pinned(row);for(const index of inputs.families)await family(index);
const refs=await json(own('references.json')),authority=await json(cfg.rootAuthority);
assert.equal(authority.state,'ROOT_REVIEWED_SECRET355_RETAINED_BOOTSTRAP_PREFLIGHT_V1');assert.equal(authority.readOnlyVerificationAllowed,true);
assert.equal(authority.sourceIndependentReview.index.sha256,PEER_SHA);await family(authority.sourceIndependentReview.index);
const peer=await json(authority.sourceIndependentReview.result);assert.equal(peer.state,'INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_BOOTSTRAP_SOURCE_REVIEW_PASSED_V1');assert.equal(peer.sourceIndexSha256,SOURCE_SHA);
await pinned(authority.rootVerifierEntry);assert.equal(authority.rootVerifierEntry.path,ENTRY);await pinned(refs.node);assert.equal(await realpath(process.execPath),refs.node.path);
const api=own('retained-bootstrap.mjs');assert.equal(api.sha256,API_SHA);await recheckInputs();
await mkdir(OUTPUT,{mode:0o700});
let record=null,primary=null,finalError=null,apiCalls=0,freshRecheckCalls=0;
const outputs={};
try{
  const loaded=await import(pathToFileURL(api.path));assert.equal(typeof loaded.retainedSecretBootstrapPreflight,'function');
  apiCalls++;record=await loaded.retainedSecretBootstrapPreflight({configDescriptor});
  // Retain all six DATA properties, with the live closure described separately.
  const data=Object.fromEntries(Object.entries(record).filter(([key])=>key!=='recheck'));
  outputs.recordData=await write('record-data.json',data);
  outputs.historical=await write('historical-bootstrap.json',JSON.stringify(record.historicalBootstrap,null,2)+'\n');
  outputs.shape=await write('record-shape.json',Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(record)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}])));
  assert.deepEqual(Object.keys(record),['schemaVersion','kind','sourceIndex','actualReview','historicalBootstrap','currentVerification','recheck']);
  assert.equal(record.schemaVersion,1);assert.equal(record.kind,'retained-secret355-bootstrap-v1');assert.equal(Object.isFrozen(record),true);
  assert.deepEqual(record.sourceIndex,cfg.sourceIndex);assert.deepEqual(record.actualReview,refs.actualBootstrapReview);
  assert.equal(outputs.historical.sha256,refs.historicalBootstrap.sha256);assert.equal(outputs.historical.bytes,refs.historicalBootstrap.bytes);
  assert.equal(Object.keys(record.historicalBootstrap).length,41);assert.equal(record.historicalBootstrap.nativeSourceFiles,355);assert.equal(record.historicalBootstrap.selectedManifests.length,11);
  assert.equal(record.historicalBootstrap.currentCompleteVerifierCalls,1);
  for(const k of ['helperInvocations','originalApiInvocations','historicalRecheckInvocations','processesSpawned','filesCreated'])assert.equal(record.currentVerification[k],0);
  assert.equal(record.currentVerification.sourceAndProtectionChecked,true);assert.equal(record.currentVerification.engineExecuted,false);assert.equal(record.currentVerification.componentOrGuestExecuted,false);
  assert.equal(typeof record.recheck,'function');
}catch(error){primary={name:error.name,message:error.message,stack:error.stack};}
finally{
  const errors=[];
  try{if(record){freshRecheckCalls++;assert.equal(await record.recheck(),undefined);}}
  catch(error){errors.push({scope:'fresh-own-recheck',name:error.name,message:error.message,stack:error.stack});}
  try{await recheckInputs();}
  catch(error){errors.push({scope:'root-input-protection',name:error.name,message:error.message,stack:error.stack});}
  if(errors.length)finalError=errors;
}
const result={schemaVersion:1,state:primary===null&&finalError===null?'ROOT_SECRET355_RETAINED_PREFLIGHT_PASSED_UNREVIEWED_V1':'ROOT_SECRET355_RETAINED_PREFLIGHT_FAILED_V1',sourceIndex:cfg.sourceIndex,sourceIndependentReview:authority.sourceIndependentReview,rootAuthority:cfg.rootAuthority,config:configDescriptor,entry:authority.rootVerifierEntry,apiCalls,freshOwnRecheckCalls:freshRecheckCalls,originalOneShotApiCalls:0,historicalCallableCalls:0,helperCalls:0,originalProtectedRows:initial.size,outputs,primaryError:primary,finalProtectionError:finalError,engineOrGuestExecuted:false,operationalAdmission:false,runtimeAcceptanceClaim:false,requiresIndependentActualReview:true};
const resultRow=await write('result.json',result);process.stdout.write(JSON.stringify({result:resultRow,state:result.state})+'\n');
if(primary!==null||finalError!==null)process.exitCode=1;
