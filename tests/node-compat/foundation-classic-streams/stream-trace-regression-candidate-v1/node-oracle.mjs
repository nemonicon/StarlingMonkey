// Node-host oracle/model only. This file is never a guest or native proof.
import assert from 'node:assert/strict';
import * as stream from 'node:stream';
import {Buffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createClassicStreams} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {makeInput,runCases} from './cases.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const here=dirname(fileURLToPath(import.meta.url)),hash=b=>createHash('sha256').update(b).digest('hex');
const output=resolve(process.env.NODE_COMPAT_STREAM_TRACE_ORACLE_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Choose fresh oracle output');}catch(error){if(error.code!=='ENOENT')throw error;}await mkdir(dirname(output),{recursive:true});
const native=await runCases({stream,Buffer,input:makeInput(Buffer),queueMicrotask});
const graph=createClassicStreams({Buffer,events,EventEmitter:events.EventEmitter,StringDecoder,nextTick:process.nextTick,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
const model=await runCases({stream:graph.root,Buffer,input:makeInput(Buffer),queueMicrotask});
assert.equal(native.length,8);assert.equal(model.length,8);
const differences=[];for(let i=0;i<native.length;i++){assert.equal(native[i].id,model[i].id);assert.equal(native[i].checksum,model[i].checksum);assert.equal(native[i].bytes,model[i].bytes);
 if(JSON.stringify(native[i])!==JSON.stringify(model[i]))differences.push({id:native[i].id,node:native[i],hostModel:model[i]});}
const sourcePins=Object.fromEntries(await Promise.all(['cases.mjs','guest.mjs','node-oracle.mjs','../../../../builtins/node-compat/classic-streams/classic-streams.mjs','../../../../builtins/node-compat/classic-streams/classic-core.generated.mjs'].map(async name=>[name,hash(await readFile(resolve(here,name)))])));
const result={schemaVersion:1,state:'NODE22_PUBLIC_STREAM_TRACE_ORACLE_AND_LABELLED_HOST_MODEL_OBSERVED',node:process.version,groups:8,nodeObserved:native,hostModelObserved:model,differences,
 nodeExecutable:{path:process.execPath,sha256:hash(await readFile(process.execPath))},sourcePins,hostModel:{algorithm:'Current actual installed guest factory source evaluated by Node',dependencies:'Real Node Buffer/events/StringDecoder/Abort globals and process.nextTick; standard queueMicrotask callback control',nativeGuestOrPrivateSchedulerProof:false},
 componentizerInvoked:false,guestExecuted:false,componentBuilt:false,hostTargetExecuted:false,scope:'Bounded64byte writable HWM65/64/63 plus PassThrough pipeline sync/microtask callback traces; public state only.'};
await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,output,groups:8,differingGroups:differences.map(row=>row.id)}));
