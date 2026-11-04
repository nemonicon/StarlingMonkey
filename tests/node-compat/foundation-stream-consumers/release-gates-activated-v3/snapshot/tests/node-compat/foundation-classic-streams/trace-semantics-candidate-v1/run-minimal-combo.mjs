// Real Node22 dependency/scheduler differential only; no native engine/guest.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createClassicStreams as originalFactory} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {createClassicStreams as candidateFactory} from './ablations/returns-encoding/classic-streams.mjs';
import * as nodeProvider from './workload/node-provider.mjs';
import * as events from 'node:events';
import {createWorkload,scenarioIds} from './workload/workload.mjs';
import {runCases,makeInput} from './public-repros/cases.mjs';
import {checks} from './inherited-checks.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
assert.equal(hash(await readFile(process.execPath)),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const output=await mkdtemp('/tmp/starling-node-compat/classic-trace-semantics-v1-');
function provider(factory){const graph=factory({...nodeProvider.dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});return{stream:graph.root,promises:graph.promises,dependencies:nodeProvider.dependencies};}
const original=provider(originalFactory),candidate=provider(candidateFactory);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function firstDifference(a,b,path='$'){
 if(Object.is(a,b))return null;
 if(!a||!b||typeof a!=='object'||typeof b!=='object')return{path,node:a,candidate:b};
 const keys=[...new Set([...Object.keys(a),...Object.keys(b)])];
 for(const key of keys){if(!Object.hasOwn(a,key)||!Object.hasOwn(b,key))return{path:path+'.'+key,nodeOwn:Object.hasOwn(a,key),candidateOwn:Object.hasOwn(b,key)};const diff=firstDifference(a[key],b[key],path+(Array.isArray(a)?'['+key+']':'.'+key));if(diff)return diff;}
 return null;
}
const reproNode=await runCases({stream:nodeProvider.stream,Buffer:nodeProvider.dependencies.Buffer,input:makeInput(nodeProvider.dependencies.Buffer),queueMicrotask});
const reproOriginal=await runCases({stream:original.stream,Buffer:original.dependencies.Buffer,input:makeInput(original.dependencies.Buffer),queueMicrotask});
const reproCandidate=await runCases({stream:candidate.stream,Buffer:candidate.dependencies.Buffer,input:makeInput(candidate.dependencies.Buffer),queueMicrotask});
const minimal=reproNode.map((node,index)=>({id:node.id,originalMatches:same(node,reproOriginal[index]),candidateMatches:same(node,reproCandidate[index]),
 originalFirstDifference:firstDifference(node,reproOriginal[index]),candidateFirstDifference:firstDifference(node,reproCandidate[index])}));
const expectedPath='/tmp/starling-node-compat/classic-measurement-workload-node-v4/node-results.json',expectedBytes=await readFile(expectedPath),reference=JSON.parse(expectedBytes);
const expected=reference.expected;assert.equal(expected.length,20);assert.equal(reference.canonicalHostCounterexamples.length,14);
const sourcePins=JSON.parse(await readFile(join(here,'workload/source-pins.json')));
for(const row of sourcePins.files)assert.equal(hash(await readFile(join(here,'workload',row.path))),row.sha256);
assert.equal(hash(await readFile(join(here,'workload/workload.mjs'))),reference.sourceHashes['workload.mjs']);
const workload=createWorkload(candidate),comparison=[],observed=[];
for(const row of expected){
 console.log(JSON.stringify({stage:'candidate-case',id:row.id,iterations:row.iterations}));
 assert.equal(workload.setup(row.id),row.setup);const value=await workload.run(row.iterations,{trace:true});observed.push(value);
 comparison.push({id:row.id,iterations:row.iterations,checksumsMatch:value.unsignedChecksum===row.oracle.unsignedChecksum,
  exactTraceMatches:same(value,row.oracle),firstDifference:firstDifference(row.oracle,value)});
}
assert.equal(hash(await readFile(expectedPath)),hash(expectedBytes));
const legacyObserved=await checks(candidate.stream,candidate.promises,candidate.dependencies.Buffer);
const legacyPath=join(here,'../implementation-candidate-v1/node-final-acceptance-results.json'),legacyBytes=await readFile(legacyPath);
assert.equal(hash(legacyBytes),'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');
const legacyExpected=JSON.parse(legacyBytes).expected;assert.equal(legacyObserved.length,19);
const result={schemaVersion:1,state:'NODE22_ISOLATED_WRITABLE_CANDIDATE_COMPARISON_COMPLETED',node:process.version,output,
 sameRealNodeDependencies:true,sameRealProcessNextTick:true,schedulerPatched:false,traceNormalized:false,
 originalWorkloadCounterexamplesPreserved:{path:expectedPath,sha256:hash(expectedBytes),count:14},
 minimalCases:minimal,minimalNode:reproNode,minimalOriginal:reproOriginal,minimalCandidate:reproCandidate,
 workloadCases:comparison,workloadObserved:observed,legacyCases:19,legacyExactMatches:same(legacyObserved,legacyExpected),legacyFirstDifference:firstDifference(legacyExpected,legacyObserved),
 candidateMinimalFailures:minimal.filter(row=>!row.candidateMatches).length,candidateWorkloadTraceFailures:comparison.filter(row=>!row.exactTraceMatches).length,
 candidateWorkloadChecksumFailures:comparison.filter(row=>!row.checksumsMatch).length,
 sourceHashes:Object.fromEntries(await Promise.all(['ablations/returns-encoding/classic-core.generated.mjs','ablations/returns-encoding/classic-streams.mjs','workload/workload.mjs','inherited-checks.mjs','public-repros/cases.mjs'].map(async name=>[name,hash(await readFile(join(here,name)))]))),
 liveFactoryChanged:false,compiledNativeEngineUsed:false,componentizerOrGuestOrTargetHostExecuted:false,runtimeAcceptanceClaim:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,output,minimalFailures:result.candidateMinimalFailures,workloadTraceFailures:result.candidateWorkloadTraceFailures,checksumFailures:result.candidateWorkloadChecksumFailures,legacyExactMatches:result.legacyExactMatches}));
