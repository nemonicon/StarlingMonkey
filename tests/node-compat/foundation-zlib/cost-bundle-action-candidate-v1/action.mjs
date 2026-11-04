// Untimed source bundling only. No codec, provider, component or guest is run.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const here=dirname(fileURLToPath(import.meta.url));
const TOOLING='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8';
const PUBLICATION='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b';
const NODE='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0';
const OUTPUT='/private/tmp/starling-node-compat/zlib-cost-bundles-v1';
const arms=Object.freeze(['native-on','fflate-on','fflate-off']);
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const exactSha=value=>assert(typeof value==='string'&&/^[0-9a-f]{64}$/.test(value));
function name(value){assert(typeof value==='string'&&!isAbsolute(value)&&!value.includes('\\')&&!value.includes('\0')&&value.split('/').every(p=>p&&p!=='.'&&p!=='..'));return value;}
async function bytes(input,limit=32*1024*1024){
 const row=Object.freeze({path:input.path,sha256:input.sha256,bytes:input.bytes});
 assert(isAbsolute(row.path)&&resolve(row.path)===row.path);exactSha(row.sha256);assert(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=limit);
 assert.equal(await realpath(dirname(row.path)),dirname(row.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp'));
 const before=await lstat(row.path);assert(before.isFile()&&!before.isSymbolicLink()&&before.size===row.bytes);
 const raw=await readFile(row.path),after=await lstat(row.path);
 for(const key of ['dev','ino','size','mtimeMs','ctimeMs'])assert.equal(after[key],before[key]);
 assert.equal(raw.length,row.bytes);assert.equal(hash(raw),row.sha256);return raw;
}
async function nodeExecutable(){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);
 assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
 assert.equal(await realpath(process.execPath),'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');
 const h=createHash('sha256');for await(const block of createReadStream(process.execPath))h.update(block);assert.equal(h.digest('hex'),NODE);
}
async function main(){
 assert.equal(process.argv.length,3,'One exact config descriptor JSON argument');
 const configDescriptor=Object.freeze(JSON.parse(process.argv[2]));
 const config=JSON.parse(await bytes(configDescriptor));exactSha(config.sourceIndexSha256);
 const indexRaw=await readFile(join(here,'index.json'));assert.equal(hash(indexRaw),config.sourceIndexSha256);
 const index=JSON.parse(indexRaw);assert.equal(index.state,'COST_BUNDLE_ACTION_SOURCE_ONLY');
 const ownRows=index.files.map(row=>Object.freeze({...row,path:join(here,name(row.path))}));
 async function own(){assert.equal(hash(await readFile(join(here,'index.json'))),config.sourceIndexSha256);for(const row of ownRows)await bytes(row);await bytes(configDescriptor);}
 await own();await nodeExecutable();
 const authority=JSON.parse(await bytes(config.rootAction));
 assert.equal(authority.bundleActionSourceIndexSha256,config.sourceIndexSha256);
 assert.equal(authority.toolingCandidateIndexSha256,TOOLING);assert.equal(authority.publicationIndexSha256,PUBLICATION);
 assert.equal(authority.action,'bundle-source');assert.equal(authority.actionAllowed,true);
 assert.equal(authority.outputRoot,OUTPUT);assert.deepEqual(authority.permittedArms,arms);
 assert.equal(authority.operationalAdmission,false);assert.equal(authority.sourcePromotionAllowed,false);
 assert.equal(authority.componentGuestNativeBuildPilotOrTimingAllowed,false);
 assert.equal(config.toolingSourceIndexSha256,TOOLING);assert.equal(config.publicationIndex.sha256,PUBLICATION);
 const publication=JSON.parse(await bytes(config.publicationIndex));
 const root=await realpath(dirname(config.publicationIndex.path));assert.equal(root,'/private/tmp/starling-node-compat/zlib-cost-source-v3');
 assert.equal(publication.toolingSourceIndexSha256,TOOLING);
 // Authenticate the complete local guard import closure before loading it.
 for(const file of ['authority.mjs','context.mjs','native.mjs','preflight.mjs','bundle.mjs','environment.mjs','durable.mjs']){
  const relative='control/'+file,row=publication.files.find(r=>r.path===relative);assert(row);await bytes({...row,path:join(root,relative)});
 }
 const {costPreflight}=await import(pathToFileURL(join(root,'control/preflight.mjs')));
 const {bundleCost}=await import(pathToFileURL(join(root,'control/bundle.mjs')));
 const {DurableOutput}=await import(pathToFileURL(join(root,'control/durable.mjs')));
 let output;
 const captured=[];
 try{
  for(const arm of arms){
   const admitted=await costPreflight({...config,arm,action:'bundle-source'});
   assert.equal(admitted.rootActionSha256,config.rootAction.sha256);
   if(!output)output=await DurableOutput.create(OUTPUT);
   await output.write('progress/'+arm+'.json',{schemaVersion:1,state:'BEFORE_SOURCE_BUNDLE',arm,rootActionSha256:admitted.rootActionSha256},{json:true});
   const result=await bundleCost(admitted,{arm,entryPath:join(admitted.guestRoot,'guest.mjs'),providerPath:join(admitted.guestRoot,arm==='native-on'?'native-provider.mjs':'fflate-provider.mjs'),oracleInputsPath:admitted.oracleInputsPath});
   const code=await output.write(arm+'/bundle.mjs',Buffer.from(result.code,'utf8'));
   const graph=await output.write(arm+'/graph.json',result.graph,{json:true});
   captured.push({arm,nativeEngineSha256:admitted.pin.engineSha256,code,graph,virtualModuleIds:result.graph.virtualModuleIds});
   await admitted.recheck();await own();
  }
  await nodeExecutable();await own();await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:'ZLIB_COST_SOURCE_BUNDLES_CAPTURED_UNREVIEWED_V1',toolingSourceIndexSha256:TOOLING,sourcePublicationIndexSha256:PUBLICATION,bundleActionSourceIndexSha256:config.sourceIndexSha256,rootActionSha256:config.rootAction.sha256,arms:captured,libraryBundlerExecuted:true,codecProviderOrComponentOrGuestExecuted:false,operationalAdmission:false,timingAllowed:false,independentSourceAndVirtualHelperReviewRequired:true},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,state:'UNREVIEWED_ZLIB_COST_SOURCE_BUNDLE_FILES',files:[...output.rows.values()]},{json:true});
  const completion=await output.write('completion.json',{schemaVersion:1,state:'SOURCE_BUNDLE_CAPTURE_UNREVIEWED_EXTERNAL_EXIT_ZERO_REQUIRED',index,result,componentizationAllowed:false},{json:true});
  await output.recheck();process.stdout.write(JSON.stringify({root:OUTPUT,index,completion,componentizationAllowed:false})+'\n');
 }catch(error){
  if(output)try{await output.write('failure.json',{state:'FAILED_UNREVIEWED_SOURCE_BUNDLE_ACTION',thrownType:typeof error,propertiesRead:false,partialOutputsRetained:true},{json:true});}catch{}
  throw error;
 }finally{if(output)await output.close();}
}
await main();
