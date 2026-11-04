import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createClassicStreams as originalFactory} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {createClassicStreams as candidateFactory} from './proposed/classic-streams.mjs';
import * as nodeProvider from './workload/node-provider.mjs';
import * as events from 'node:events';
import {encodingCases} from './encoding-cases.mjs';
assert.equal(process.version,'v22.14.0');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');assert.equal(hash(await readFile(process.execPath)),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
function provider(factory){const graph=factory({...nodeProvider.dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});return{stream:graph.root,promises:graph.promises,dependencies:nodeProvider.dependencies};}
const expected=await encodingCases(nodeProvider),before=await encodingCases(provider(originalFactory)),after=await encodingCases(provider(candidateFactory));
const rows=expected.map((row,index)=>({id:row.id,originalMatches:JSON.stringify(row)===JSON.stringify(before[index]),candidateMatches:JSON.stringify(row)===JSON.stringify(after[index])}));
assert(rows.every(row=>row.candidateMatches));
const output=await mkdtemp('/tmp/starling-node-compat/classic-trace-encoding-v1-'),result={schemaVersion:1,state:'NODE22_ORDINARY_ENCODING_RETURN_BOUNDARIES_PASSED',cases:rows,expected,before,after,
 sameRealNodeDependenciesAndNextTick:true,traceNormalized:false,liveSourceModified:false,nativeOrGuestOrTargetHostExecuted:false,output};
await writeFile(output+'/results.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,output,cases:rows.length,originalGaps:rows.filter(row=>!row.originalMatches).length}));
