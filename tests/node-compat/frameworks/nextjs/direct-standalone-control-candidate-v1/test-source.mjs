// Read-only inputs + real pure/actual-controller text with inert callbacks only.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
import {join} from 'node:path';
import {outputFor,validateInput,listenerFromLogs,serverInvocation,serverStopAccepted,accepted} from './models.mjs';
const read=async name=>JSON.parse(await readFile(new URL(name,import.meta.url),'utf8'));
const plan=await read('./plan.json'),input=JSON.parse(await readFile(plan.applicationInputs.path)),build=JSON.parse(await readFile(plan.applicationBuildResult.path));let checks=0;
assert(validateInput(input,build,plan));checks++;
for(const id of ['a','0','a'.repeat(48)]){assert.equal(outputFor(plan.outputPrefix,id),plan.outputPrefix+'-'+id);checks++;}
for(const id of [undefined,null,false,0,'','a'.repeat(49),'../x','x/y','x\\y','x\n','A','é']){assert.throws(()=>outputFor(plan.outputPrefix,id));checks++;}
for(const change of [x=>x.files.pop(),x=>x.directories.push({path:'.'}),x=>x.files[1].path=x.files[0].path,x=>x.files[0].path='../escape',x=>x.bytes++]){const x=structuredClone(input);assert.throws(()=>{change(x);validateInput(x,build,plan);});checks++;}
for(const change of [x=>x.passed=false,x=>x.errors.push({message:'failure'}),x=>x.originalInputsPreserved=false,x=>x.applicationInventoryDescriptor.sha256='0'.repeat(64),x=>x.installedVersions.next='other']){const x=structuredClone(build);change(x);assert.throws(()=>validateInput(input,x,plan));checks++;}
const origin='http://127.0.0.1:12345';assert.deepEqual(listenerFromLogs({stdout:'Ready in0ms\n'},origin),[]);checks++;
assert.equal(listenerFromLogs({stdout:'\u001b[32m- Local:         '+origin+'\u001b[0m\n'},origin).length,1);checks++;
assert.throws(()=>listenerFromLogs({stderr:'- Local: http://127.0.0.1:12346\n'},origin));checks++;
assert.deepEqual(listenerFromLogs({stdout:'- Local: '+origin},origin),[]);checks++;
const spec=serverInvocation('/actual-node','/owned-app',origin,{HOME:'/home',USER:'user',PATH:'/bin',NODE_OPTIONS:'--require forbidden',NODE_PATH:'/elsewhere',NEXT_MANUAL_SIG_HANDLE:'1',NODE_CHANNEL_FD:'3'},'/owned-tmp');
assert.deepEqual(spec.args,['/owned-app/server.js']);assert.equal(spec.cwd,'/owned-app');assert.equal(spec.env.PORT,'12345');assert.equal(spec.env.HOSTNAME,'127.0.0.1');assert.equal(spec.env.HOME,'/home');assert.equal(spec.env.NODE_ENV,'production');assert.equal(spec.env.NEXT_TELEMETRY_DISABLED,'1');assert.equal(spec.env.TMPDIR,'/owned-tmp');
for(const k of ['NODE_OPTIONS','NODE_PATH','NEXT_MANUAL_SIG_HANDLE','NODE_CHANNEL_FD'])assert(!Object.hasOwn(spec.env,k));checks++;
for(const bad of ['http://localhost:1234','https://127.0.0.1:1234','http://127.0.0.1:1234/path']){assert.throws(()=>serverInvocation('node','app',bad,{},'tmp'));checks++;}
const goodServer={shutdownRequested:true,sigintSent:true,forcedCleanup:false,exit:{code:130,signal:null,error:null}};
const good={contractsPassed:true,errors:[],originalInputsPreserved:true,copyInitiallyVerified:true,ownedFinalInventoryRecorded:true,server:goodServer};assert(accepted(good));checks++;
for(const change of [x=>x.server.exit.code=0,x=>x.server.exit.code=143,x=>x.server.exit.signal='SIGINT',x=>x.server.exit.error={},x=>x.server.shutdownRequested=false,x=>x.server.sigintSent=false,x=>x.server.forcedCleanup=true,x=>x.contractsPassed=false,x=>x.originalInputsPreserved=false,x=>x.copyInitiallyVerified=false,x=>x.ownedFinalInventoryRecorded=false,x=>x.errors.push({message:'strict failure'})]){const x=structuredClone(good);change(x);assert.equal(accepted(x),false);checks++;}
const source=await readFile(new URL('./control.mjs',import.meta.url),'utf8');
const begin=source.indexOf('async function launch(invocation,label){'),end=source.indexOf('\nasync function verifyInitialCopy()',begin);assert(begin>=0&&end>begin);
const opens=[],spawns=[],children=[],handles=[];
const launch=compileFunction(source.slice(begin,end)+'return launch;',['join','output','open','handles','spawn','diagnostic','children'])(join,'/inert-output',async(path,flags,mode)=>{opens.push({path,flags,mode});return {fd:opens.length};},handles,(exe,args,options)=>{spawns.push({exe,args,options});return {pid:17,once(){}};},e=>({message:String(e)}),children);
const child=await launch(spec,'server');assert.equal(child.record.pid,17);assert.equal(children.length,1);assert.deepEqual(spawns,[{exe:'/actual-node',args:['/owned-app/server.js'],options:{cwd:'/owned-app',env:spec.env,stdio:['ignore',1,2]}}]);assert(opens.every(x=>x.flags==='wx'&&x.mode===0o600));assert.equal(handles.length,2);checks++;
const stopBegin=source.indexOf('async function stopServer(){'),stopEnd=source.indexOf('\ntry{',stopBegin);assert(stopBegin>=0&&stopEnd>stopBegin);
for(const variant of ['normal130','wrong0','timeoutThenKilled','alreadyExited']){
 const signals=[],result={server:{shutdownRequested:false,sigintSent:false,forcedCleanup:false}};let calls=0,api;
 const make=compileFunction('let hostExit=initial,stopping=false;'+source.slice(stopBegin,stopEnd)+'return {stopServer,setExit:x=>hostExit=x};',['host','hostDone','result','plan','boundedWait','initial']);
 api=make({kill:signal=>{signals.push(signal);return true;}},Promise.resolve(),result,plan,async()=>{calls++;if(variant==='timeoutThenKilled'&&calls===1)return null;const status={code:variant==='wrong0'?0:variant==='timeoutThenKilled'?null:130,signal:variant==='timeoutThenKilled'?'SIGKILL':null,error:null};api.setExit(status);return status;},variant==='alreadyExited'?{code:130,signal:null,error:null}:null);
 await api.stopServer();assert.equal(serverStopAccepted(result.server),variant==='normal130');assert.deepEqual(signals,variant==='alreadyExited'?[]:variant==='timeoutThenKilled'?['SIGINT','SIGKILL']:['SIGINT']);checks++;
}
const donor=await readFile(new URL('../wasmtime-deployment-candidate-v7/run-contracts.mjs',import.meta.url),'utf8'),client=await readFile(new URL('./run-contracts.mjs',import.meta.url),'utf8');
assert.equal(client,donor.replace('// Standalone client only; server is the separately owned actual Wasmtime process.','// Client only; server is separately owned unmodified Next standalone on host Node.').replaceAll('next-wasmtime-deployment-','next-direct-standalone-control-').replaceAll('ACTUAL_NEXT_WASMTIME_FULL_CONTRACT_CLIENT_V2','ACTUAL_NEXT_DIRECT_STANDALONE_FULL_CONTRACT_CLIENT_V1').replaceAll('actualComponentExecutionClaimRequiresParentProof','actualDirectHostExecutionClaimRequiresParentProof').replaceAll('ACTUAL_NEXT_WASMTIME_CONTRACT_CLIENT_PASSED_V2','ACTUAL_NEXT_DIRECT_STANDALONE_CONTRACT_CLIENT_PASSED_V1').replaceAll('ACTUAL_NEXT_WASMTIME_CONTRACT_CLIENT_FAILED_V2','ACTUAL_NEXT_DIRECT_STANDALONE_CONTRACT_CLIENT_FAILED_V1'));checks++;
console.log(JSON.stringify({sourceOnly:true,checks,actualControllerLaunchAndStopTextExercised:true,strictClientOnlyProvenanceAndNamespaceChanged:true,expectedServer130NeverRelabeledRaw0:true,noActorNetworkTimerFilesystemMutationOrAppCopy:true}));
