// Host-Node execution of a source-only portable JS bundle, not a Wasm guest.
import assert from 'node:assert/strict';
import {readFile,writeFile,lstat,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const hash=b=>createHash('sha256').update(b).digest('hex');
const graphRoot=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_GRAPH??'');
const oraclePath=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_ORACLE??'');
const output=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_STOCK_OUTPUT??'');
for(const value of [graphRoot,oraclePath,output])assert(value.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Choose fresh host output');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(output,{recursive:true});
const graph=JSON.parse(await readFile(join(graphRoot,'bundle-results.json'))),oracleBytes=await readFile(oraclePath),oracle=JSON.parse(oracleBytes);
const stock=graph.reports.find(row=>row.arm==='stock');assert(stock&&stock.scheduler.override===false);assert.deepEqual(stock.imports,[]);
const bundle=await readFile(stock.bundlePath);assert.equal(hash(bundle),stock.bundleSha256);
const selected=await import(pathToFileURL(stock.bundlePath));
const comparisons=[];
for(const row of oracle.expected){
 const setup=selected.setup(row.id);assert.equal(setup,row.setup);
 try{const observed=JSON.parse(await selected.inspect(row.iterations));comparisons.push({id:row.id,iterations:row.iterations,
   checksumEqual:observed.unsignedChecksum===row.oracle.unsignedChecksum,exactTraceEqual:JSON.stringify(observed)===JSON.stringify(row.oracle),observed});}
 catch(error){comparisons.push({id:row.id,iterations:row.iterations,failed:true,error:{name:error.name,code:error.code??null,message:error.message}});break;}
}
const result={schemaVersion:1,state:'STOCK_JCO_HOST_SOURCE_COMMON_DOMAIN_OBSERVATIONS',node:process.version,graphRoot,
 bundleSha256:stock.bundleSha256,oraclePath,oracleSha256:hash(oracleBytes),comparisons,
 traceCounterexamples:comparisons.filter(row=>!row.exactTraceEqual).map(({id,iterations,failed})=>({id,iterations,failed:failed??false})),
 timingAllowed:false,stockSchedulerModified:false,
 scope:'Real locked stock Jco source bundle executed by Node only; different provider/dependencies and queueMicrotask scheduler. No component/guest/native/target host or timing.'};
await writeFile(join(output,'stock-results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,cases:comparisons.length,counterexamples:result.traceCounterexamples.length,output}));
