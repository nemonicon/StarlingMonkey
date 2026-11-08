// Reusable control-only client. The separately owned parent selects Node or Wasm host.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,lstat,realpath} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readPublicCorrelationManifest} from './manifest.mjs';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,6);
const here=dirname(fileURLToPath(import.meta.url)),origin=new URL(process.argv[2]),output=resolve(process.argv[3]),tools=resolve(process.argv[4]),runId=process.argv[5];
assert.equal(origin.origin,process.argv[2]);assert.equal(origin.protocol,'http:');assert.equal(origin.hostname,'127.0.0.1');assert(origin.port&&origin.username===''&&origin.password==='');
assert(typeof runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId)?.[0]===runId);assert.equal(await realpath(dirname(output)),dirname(output));
const policy=JSON.parse(await readFile(join(here,'plan.json'),'utf8'));assert.equal(policy.actualAssetBindingsPending,false,'Source assets pending before control output/browser');
const manifestPath=join(dirname(output),'public-request-correlation.json'),correlation=await readPublicCorrelationManifest(manifestPath);
assert.equal(correlation.manifest.origin,origin.origin);assert.equal(correlation.manifest.runId,runId);
await mkdir(output,{mode:0o700});
const result={schemaVersion:1,suite:'NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_CLIENT_V1',controlOnly:true,fullOriginalContractExecuted:false,origin:origin.origin,runId,node:process.version,publicRequestCorrelation:{manifest:correlation.manifest,manifestSource:correlation.source,readEvidence:correlation.evidence},browserArgv:null,browserExit:null,browserResult:null,browser:null,errors:[],passed:false,fullNextAccepted:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});
await save();
try{
 const args=[join(here,'browser-check.mjs'),'--origin',origin.origin,'--tools',tools,'--output',join(output,'browser'),'--correlation-manifest',manifestPath];result.browserArgv=[process.execPath,...args];await save();
 const child=spawn(process.execPath,args,{stdio:['ignore','inherit','inherit']});
 result.browserExit=await new Promise(resolveExit=>{let error=null;child.once('error',e=>{error={name:e.name,message:e.message};});child.once('close',(code,signal)=>resolveExit({code,signal,error}));});
 const path=join(output,'browser/result.json'),before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size<=16*1024*1024);assert.equal(await realpath(path),path);
 const bytes=await readFile(path),after=await lstat(path);for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(before[key],after[key]);
 result.browserResult={path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};result.browser=JSON.parse(bytes);
 assert.deepEqual(result.browser.publicRequestCorrelation.manifestSource,correlation.source);
 result.passed=result.browserExit.code===0&&result.browserExit.signal===null&&result.browserExit.error===null&&result.browser.passed===true;
}catch(error){result.errors.push({name:error?.name??'Error',message:error?.message??String(error)});}
finally{await save();}
console.log(JSON.stringify({controlOnly:true,passed:result.passed,browserExit:result.browserExit,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
