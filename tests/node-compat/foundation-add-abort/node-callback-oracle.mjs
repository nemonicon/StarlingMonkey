// Stock pinned Node, ordinary public EventTarget/FinalizationRegistry and a
// documented --expose-gc oracle flag. No guest/private memory or fault testing.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const cases=[];
for(const[name,body]of[
 ['registration-getter',"let reads=0,caught=false,registered=false;const t=new EventTarget();try{t.addEventListener('test',{get handleEvent(){reads++;throw new Error('GETTER_REGISTRATION')}});registered=true}catch(error){caught=error.message==='GETTER_REGISTRATION'}await new Promise(resolve=>setImmediate(resolve));result={reads,caught,registered};"],
 ['dispatch-getter',"let reads=0,armed=false,dispatchCaught=false,second=0;const t=new EventTarget();t.addEventListener('test',{get handleEvent(){reads++;if(armed)throw new Error('GETTER_DISPATCH');return()=>{}}});t.addEventListener('test',()=>second++);armed=true;try{t.dispatchEvent(new Event('test'))}catch{dispatchCaught=true}await new Promise(resolve=>setImmediate(resolve));result={reads,dispatchCaught,second};"],
 ['direct-finalizer',"let seen=0;const registry=new FinalizationRegistry(()=>{seen++;throw new Error('DIRECT_FINALIZER')});function register(){registry.register({},0)}register();for(let i=0;i<30&&seen===0;i++){globalThis.gc();await new Promise(resolve=>setImmediate(resolve));}result={seen};"],
]){
 const source="const errors=[];process.on('uncaughtException',error=>{errors.push(error.message)});let result;"+body+"console.log(JSON.stringify({result,errors}));";
 const child=spawnSync(process.execPath,['--expose-gc','--input-type=module','-e',source],{encoding:'utf8',timeout:10000,maxBuffer:1024*1024});assert.equal(child.status,0,child.stderr);const observed=JSON.parse(child.stdout.trim());
 if(name==='registration-getter')assert.deepEqual(observed,{result:{reads:1,caught:true,registered:false},errors:[]});
 if(name==='dispatch-getter')assert.deepEqual(observed,{result:{reads:2,dispatchCaught:false,second:1},errors:['GETTER_DISPATCH']});
 if(name==='direct-finalizer')assert.deepEqual(observed,{result:{seen:1},errors:['DIRECT_FINALIZER']});
 cases.push({name,source,sourceSha256:hash(source),observed,childArguments:['--expose-gc','--input-type=module','-e','<source>'],status:child.status,stderr:child.stderr});
}
const report={schemaVersion:1,state:'public-node22-callback-counterexample-oracle-passed',recordedAtUtc:new Date().toISOString(),nodeVersion:process.version,nodeExecutable:process.execPath,nodeExecutableSha256:hash(await readFile(process.execPath)),runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),nodeOptionsPresent:false,cases,limits:['Node oracle only; public uncaughtException handler captures errors in isolated fresh processes.','--expose-gc triggers ordinary Node collection solely to schedule FinalizationRegistry; no DEBUG/fault/private memory introspection.','Finalizer timing is bounded by explicit attempts; no universal GC scheduling/order guarantee is inferred.']};
await writeFile(join(here,'node-callback-oracle-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,cases:cases.length}));
