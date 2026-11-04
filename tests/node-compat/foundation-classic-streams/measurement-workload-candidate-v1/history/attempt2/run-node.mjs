// Node-host checksum/trace oracles only; no componentization or target execution.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as nodeProvider from './node-provider.mjs';
import * as canonicalProvider from './canonical-node-provider.mjs';
import {createWorkload,scenarioIds} from './workload.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const here=dirname(fileURLToPath(import.meta.url)),hash=b=>createHash('sha256').update(b).digest('hex');
assert.equal(hash(await readFile(process.execPath)),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const output=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Choose fresh output');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(output,{recursive:true});
const node=createWorkload(nodeProvider),canonical=createWorkload(canonicalProvider),expected=[],counterexamples=[];
for(const id of scenarioIds)for(const iterations of [1,16]){
 console.log(JSON.stringify({stage:'case-start',id,iterations}));
 const setup=node.setup(id),observedSetup=canonical.setup(id);assert.equal(setup,observedSetup);
 const oracle=await node.run(iterations,{trace:true}),observed=await canonical.run(iterations,{trace:true});
 const record={id,iterations,setup,oracle};expected.push(record);
 try{assert.deepEqual(observed,oracle);}catch(error){counterexamples.push({id,iterations,oracle,observed,message:error.message});}
 assert(oracle.scheduledCallbacks<65536,'Instrumented workload callbacks alone must not exhaust guest budget');
}
const result={schemaVersion:1,state:'NODE22_CLASSIC_WORKLOAD_CHECKSUM_AND_TRACE_ORACLES_CAPTURED',node:process.version,nodeExecutable:process.execPath,nodeExecutableSha256:hash(await readFile(process.execPath)),
 ordinaryScenarios:7,rawControlFamilies:3,iterationBounds:[1,16],providerContract:['stream','promises','dependencies.Buffer','dependencies.EventEmitter','dependencies.StringDecoder','dependencies.nextTick'],
 expected,canonicalHostCompared:20,canonicalHostCounterexamples:counterexamples,
 queueCheckpointBudget:65536,budgetRaised:false,guestBudgetProof:false,
 scope:'Real Node oracle and canonical algorithm using Node dependencies/nextTick; no native queue, component, guest, host service or timing execution',
 sourceHashes:Object.fromEntries(await Promise.all(['workload.mjs','node-provider.mjs','canonical-node-provider.mjs'].map(async name=>[name,hash(await readFile(join(here,name)))])))};
await writeFile(join(output,'node-results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,oracleCases:expected.length,canonicalCounterexamples:counterexamples.length,output}));
