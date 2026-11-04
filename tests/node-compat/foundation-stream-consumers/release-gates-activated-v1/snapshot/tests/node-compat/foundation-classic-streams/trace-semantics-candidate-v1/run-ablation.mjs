// Public API host ablations only, same real Node dependencies and nextTick.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import * as nodeProvider from './workload/node-provider.mjs';
import * as events from 'node:events';
import {runCases,makeInput} from './public-repros/cases.mjs';
import {encodingCases} from './encoding-cases.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url));
const expectedRepro=await runCases({stream:nodeProvider.stream,Buffer:nodeProvider.dependencies.Buffer,input:makeInput(nodeProvider.dependencies.Buffer),queueMicrotask});
const expectedEncoding=await encodingCases(nodeProvider),results=[];
for(const group of ['encoding','returns','finish']){
 const {createClassicStreams}=await import(pathToFileURL(join(here,'ablations',group,'classic-streams.mjs')));
 const graph=createClassicStreams({...nodeProvider.dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
 const provider={stream:graph.root,promises:graph.promises,dependencies:nodeProvider.dependencies};
 const repro=await runCases({stream:provider.stream,Buffer:provider.dependencies.Buffer,input:makeInput(provider.dependencies.Buffer),queueMicrotask});
 const encoding=await encodingCases(provider);
 results.push({group,minimal:repro.map((row,index)=>({id:row.id,exactMatches:JSON.stringify(row)===JSON.stringify(expectedRepro[index]),observed:row})),
  encoding:encoding.map((row,index)=>({id:row.id,exactMatches:JSON.stringify(row)===JSON.stringify(expectedEncoding[index]),observed:row}))});
}
const output=await mkdtemp('/tmp/starling-node-compat/classic-trace-ablation-v1-');
const report={schemaVersion:1,state:'INDEPENDENT_WRITABLE_DELTA_NODE_HOST_ABLATIONS_CAPTURED',results,expectedRepro,expectedEncoding,
 schedulerUnchanged:true,traceNormalized:false,liveSourceChanged:false,nativeGuestOrTargetHostExecuted:false,output};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output,groups:results.map(row=>({group:row.group,minimalExact:row.minimal.filter(value=>value.exactMatches).length,encodingExact:row.encoding.filter(value=>value.exactMatches).length}))}));
