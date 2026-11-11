import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {lstat,mkdir,open,readFile,realpath} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const here=dirname(fileURLToPath(import.meta.url));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
assert.deepEqual(process.execArgv,[],'Bare pinned Node required');
for(const key of ['NODE_OPTIONS','NODE_PATH'])assert(!Object.hasOwn(process.env,key),key+' forbidden');
const planBytes=await readFile(join(here,'plan.json')),plan=JSON.parse(planBytes);
assert.equal(plan.state,'SOURCE_ONLY_RESPONSE_CLONE_CANCEL_FOLLOWUP_OBSERVATION_V1');
assert.equal(plan.outerDeadlineMs,5000);assert.equal(process.execPath,plan.node.path);
assert.equal(await realpath(process.execPath),process.execPath);
const source=join(here,'cases.mjs'),sourceBytes=await readFile(source);
assert.deepEqual({path:source,sha256:sha(sourceBytes),bytes:sourceBytes.length},plan.sharedCase);
const output=resolve(process.argv[2]);assert.equal(output,process.argv[2]);
const outputPrefix='/private/tmp/starling-node-compat/response-clone-cancel-followup-candidate-v1-node-';
assert(output.startsWith(outputPrefix));
assert(/^[a-z0-9][a-z0-9-]{0,47}$/.test(output.slice(outputPrefix.length)));
assert.equal(await realpath(dirname(output)),dirname(output));
await mkdir(output,{mode:0o700});assert.equal((await lstat(output)).mode&0o777,0o700);
const {runResponseCloneCancelFollowups,describeThrown}=await import(pathToFileURL(source).href);
const report={};const result={schemaVersion:1,suite:'NODE_RESPONSE_CLONE_CANCEL_FOLLOWUP_OBSERVATION_V1',
  executionKind:'bare-node-host',nodeVersion:process.version,nodeExecutable:process.execPath,
  selectedNode:plan.node,toolBinaryHashVerifiedByThisCLI:false,
  sharedCase:plan.sharedCase,plan:{path:join(here,'plan.json'),sha256:sha(planBytes),bytes:planBytes.length},
  captureCompleted:false,semanticAccepted:null,expectedForGuest:null,observation:report,
  outerDeadlineMs:5000,timedOut:false,error:null,secondaryErrors:[],fullNextAccepted:false};
let failed=false,primary,timer;
// Observe the collector immediately, even if the outer deadline wins.
const pending=runResponseCloneCancelFollowups({report}).then(value=>({kind:'fulfilled',value}),error=>({kind:'rejected',error}));
try{
  const observed=await Promise.race([pending,new Promise(resolve=>{timer=setTimeout(()=>resolve({kind:'deadline'}),5000);})]);
  if(observed.kind==='deadline'){result.timedOut=true;throw new Error('Shared case exceeded outer5000ms deadline');}
  if(observed.kind==='rejected')throw observed.error;
  assert.equal(observed.value,report);assert.equal(report.collectionComplete,true);
  assert.equal(sha(await readFile(source)),plan.sharedCase.sha256,'Case Source changed');
  assert((await readFile(join(here,'plan.json'))).equals(planBytes),'Plan changed');
  result.captureCompleted=true;
}catch(error){failed=true;primary=error;result.error=describeThrown(error);}
finally{clearTimeout(timer);}
// Snapshot once: an unresolved case after a deadline cannot mutate the saved bytes.
const bytes=Buffer.from(JSON.stringify(result,null,2)+'\n');assert(bytes.length<=65536,'Report cap');
const path=join(output,'result.json');let handle,publicationFailed=false,publicationPrimary;
try{handle=await open(path,'wx',0o600);await handle.writeFile(bytes);await handle.sync();}
catch(error){publicationFailed=true;publicationPrimary=error;}
finally{if(handle)try{await handle.close();}catch(error){
  if(!publicationFailed){publicationFailed=true;publicationPrimary=error;}
  else result.secondaryErrors.push({stage:'publication-close',error:describeThrown(error)});
}}
if(!publicationFailed)try{assert((await readFile(path)).equals(bytes),'Publication readback');}
catch(error){publicationFailed=true;publicationPrimary=error;}
if(publicationFailed){
  console.error(JSON.stringify({primary:failed?describeThrown(primary):null,
    publication:describeThrown(publicationPrimary),secondaryErrors:result.secondaryErrors}));
  if(failed)throw primary;
  throw publicationPrimary;
}
console.log(JSON.stringify({suite:result.suite,captureCompleted:result.captureCompleted,timedOut:result.timedOut,
  result:{path,sha256:sha(bytes),bytes:bytes.length},semanticAccepted:null,fullNextAccepted:false}));
process.exitCode=failed?1:0;
