// Source + retained/synthetic DATA only; no host/CLI/server/filesystem-copy action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {compileFunction} from 'node:vm';
import {join} from 'node:path';
import {permissions,validateAuthority,configuration,validateEffective,validateSelection,evaluate,clean,registrationFromLogs} from './models.mjs';
const read=async name=>JSON.parse(await readFile(new URL(name,import.meta.url),'utf8'));
const plan=await read('./plan.json'),contract=await read('./cold-contract.json'),refs=(await read('./test-data-inputs.json')).inputs;
async function retained(key){const r=refs[key],b=await readFile(r.path);assert.equal(b.length,r.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),r.sha256);return JSON.parse(b);}
const construction=await retained('constructionResult'),audit=await retained('componentAudit'),native=await retained('nativeMetadata'),ctor=await retained('constructorAuthority');
const rows=[],copy=x=>structuredClone(x);
function test(name,body){body();rows.push({name,passed:true});}
// Synthetic authority-shaped DATA for predicates only. No authority file issued.
const a={state:'ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1',runId:'pure-data-test',...permissions,applicationSource:'/pure-data/app',engineBuildEvidence:construction.artifacts.engineBuildEvidence,metadataExpectedFixedValues:ctor.metadataExpectedFixedValues,nativeProtectedInputs:[plan.node],nativeSourceFamilies:[]};
for(const[k,e]of Object.entries(plan.expectedArtifacts))a[k]={path:'/pure-data/'+k,...e};
for(const k of ['component','componentAudit','engine','nativeMetadata','inputEntry','inputSourceIndex','adapter'])a[k]=construction.artifacts[k];a.constructionCallerIndex=construction.callerIndex;
test('actual retained V5 component/native/constructor Source selection',()=>{validateSelection(construction,audit,native,ctor,a,plan);validateAuthority(a,plan);});
for(const[name,change]of[
 ['host mutation',x=>x.hostMutationAllowed=true],['new services',x=>x.newServicesAllowed=true],['browser',x=>x.browserAllowed=true],
 ['retained acceptance',x=>x.retainedContractAcceptanceAllowed=true],['guest permission missing',x=>delete x.coldNextGuestAllowed],
 ['wrong component',x=>x.component.sha256='0'.repeat(64)],['wrong wash',x=>x.wash.sha256='0'.repeat(64)],['unsafe runId',x=>x.runId='../other'],
])test('Root DATA refusal '+name,()=>{const x=copy(a);change(x);assert.throws(()=>validateAuthority(x,plan));});
const configured=configuration(a.component.path,'/pure-data/app','/pure-data/cache','http://127.0.0.1:12345');
test('actual prior CLI effective shape supports exact proposed config',()=>{const e=copy(configured);delete e.dev.components;delete e.dev.plugins;delete e.dev.host_plugins;delete e.workload.config;validateEffective(e,configured);});
const prior=(await retained('priorEffectiveConfig')).data;
test('prior actual CLI supplied exactly app/cache preopens and explicit env',()=>{assert.equal(prior.version,'2.11.0');assert.equal(prior.dev.service,false);assert.deepEqual(prior.dev.volumes.map(v=>v.guest_path),['/app','/cache']);for(const k of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts'])assert.deepEqual(prior.workload[k],[]);});
for(const[name,change]of[
 ['wrong nested cache',x=>x.dev.volumes[1].guest_path='/cache'],['extra mount',x=>x.dev.volumes.push({host_path:'/',guest_path:'/'})],
 ['wrong component',x=>x.dev.component_path='/other'],['service enabled',x=>x.dev.service=true],['plugin',x=>x.dev.plugins=['other']],
 ['outgoing host',x=>x.workload.allowedHosts=['*']],['DNS',x=>x.workload.allowedIpNameLookups=['*']],['loopback egress',x=>x.workload.allowedHostLoopbackPorts=[12345]],
 ['ambient env',x=>x.workload.environment.config.EXTRA='unexpected'],['origin mismatch',x=>x.workload.environment.config.STARLING_NEXT_ORIGIN='http://127.0.0.1:54321'],
 ['fetch WIT',x=>x.wit.skip_fetch=false],['build',x=>x.build.command='other'],
])test('effective configuration refusal '+name,()=>{const x=copy(configured);change(x);assert.throws(()=>validateEffective(x,configured));});
for(const origin of ['http://localhost:12345','http://127.0.0.1:12345/path','https://127.0.0.1:12345'])test('origin refusal '+origin,()=>assert.throws(()=>configuration('/component','/app','/cache',origin)));
for(const[name,change]of[
 ['native frame cast',x=>x.metadataKind='OLD_83'],['wrong native engine',x=>x.engine.sha256='0'.repeat(64)],
])test('native DATA refusal '+name,()=>{const x=copy(native);change(x);assert.throws(()=>validateSelection(construction,audit,x,ctor,a,plan));});
for(const[name,change]of[
 ['unselected import',x=>x.emittedImports.push('custom:host/service@1.0.0')],['old interface version',x=>x.emittedImports[0]=x.emittedImports[0].replace('@0.2.10','@0.2.0')],
 ['missing interface',x=>x.emittedImports.pop()],['extra export',x=>x.exports.push('run')],['custom allowed',x=>x.noExternalPreview1OrCustomImports=false],
])test('component audit refusal '+name,()=>{const x=copy(audit);change(x);assert.throws(()=>validateSelection(construction,x,native,ctor,a,plan));});
const terminal=await retained('priorMonitorTerminal');test('actual prior owned host terminal clean',()=>assert.equal(clean(terminal),true));
for(const[name,change]of[
 ['interrupt',x=>x.interruptedSignals=[2]],['timeout',x=>x.timeout=true],['nonzero',x=>x.rawExitCode=1],['group remains',x=>x.allObservedOwnedGroupsGone=false],['error missing',x=>delete x.errors],
])test('owned cleanup refusal '+name,()=>{const x=copy(terminal);change(x);assert.equal(clean(x),false);});
test('exact eight cold requests distinct from retained contract',()=>{assert.deepEqual(contract.requests.map(x=>x.id),['cold-health-1','cold-health-2','cold-health-3','home','json-post','fs-crypto-probe','public-asset','suspense-complete']);assert.equal(contract.cacheSequenceIncluded,false);assert.equal(contract.browserIncluded,false);assert.equal(contract.retainedStateClaimed,false);});
for(const c of contract.requests){const body=c.json?JSON.stringify(c.json):c.includes.join(' '),record={status:c.status,complete:true,shellChunk:0,readyChunk:1};test('cold contract '+c.id,()=>assert.equal(evaluate(record,body,c).passed,true));test('cold non200 refusal '+c.id,()=>assert.equal(evaluate({...record,status:500},body,c).passed,false));}
test('stream coalesced shell/ready refuses strict streaming',()=>{const c=contract.requests.at(-1);assert.equal(evaluate({status:200,complete:true,shellChunk:0,readyChunk:0},c.includes.join(' '),c).passed,false);});
// Execute ACTUAL capture() function text with only in-memory transport/files.
const code=await readFile(new URL('./deploy.mjs',import.meta.url),'utf8'),start=code.indexOf('async function capture(request,origin){'),end=code.indexOf('\ntry{\n // COPYFILE_FICLONE',start);assert(start>=0&&end>start);
const captureText=code.slice(start,end);assert(captureText.endsWith('\n}'));
const makeCapture=compileFunction('return '+captureText,['result','save','fetch','AbortSignal','plan','join','output','writeFile','row','evaluate','errorData']);
async function captureTest(name,parts,options={}){
 const result={responses:[]},files=new Map(),snapshots=[],c=contract.requests.at(-1);let evaluations=0;
 const write=async(path,bytes)=>{assert(!files.has(path));files.set(path,typeof bytes==='string'?new TextEncoder().encode(bytes):new Uint8Array(bytes));};
 const row=async path=>({path,sha256:createHash('sha256').update(files.get(path)).digest('hex'),bytes:files.get(path).length});
 const expectedPath='/pure-data/responses/'+c.id+'.body';
 const capture=makeCapture(result,async()=>snapshots.push(copy(result)),async url=>{assert.equal(url,'http://pure-data.invalid'+c.path);return{status:200,headers:new Map([['content-type','text/html']]),body:(async function*(){for(const part of parts)yield part;})()};},{timeout(ms){assert.equal(ms,20000);return{inert:true};}},{requestMilliseconds:20000,maxResponseBytes:options.limit??8388608},join,'/pure-data',write,row,(record,body,cc)=>{assert(files.has(expectedPath));assert(snapshots.some(s=>s.responses[0]?.body?.path===expectedPath));evaluations++;return evaluate(record,body,cc);},e=>({message:String(e)}));
 let failed=false;try{await capture(c,'http://pure-data.invalid');}catch{failed=true;}
 assert.equal(failed,options.failure===true);assert.equal(evaluations,1);const record=result.responses[0];assert(files.has(expectedPath));assert.equal(record.complete,options.failure!==true);
 const reassembled=Buffer.concat(record.chunks.map(x=>Buffer.from(x.base64,'base64')));assert.deepEqual(reassembled,Buffer.from(files.get(expectedPath)));
 if(options.failure)assert.equal(record.contract.passed,false);else assert.equal(record.contract.passed,true);
 if(options.limit)assert.equal(record.limitExceeded.limit,options.limit);
 rows.push({name,passed:true});
}
const enc=x=>new TextEncoder().encode(x);
await captureTest('actual capture raw-before-contract/strict chunk semantics',[enc('NEXT_STREAM_SHELL'),enc('NEXT_STREAM_READY')]);
await captureTest('actual capture invalid UTF8 preserves offending raw chunk',[Uint8Array.of(255)],{failure:true});
await captureTest('actual capture byte limit honest partial boundary',[Uint8Array.of(1,2),Uint8Array.of(3,4)],{failure:true,limit:3});
// Actual V1 failure is preserved: TCP was live but the deployed-workload marker
// was absent. These are DATA reads, never an actual retry or log fabrication.
const oldStdout=await readFile(refs.v1DevStdout.path,'utf8'),oldStderr=await readFile(refs.v1DevStderr.path,'utf8'),oldResult=await retained('v1FailedResult');
const oldOrigin=oldResult.portLease.origin;
test('actual V1 TCP positive is not post-registration readiness',()=>{assert.equal(oldResult.readiness.tcpConnect,true);assert.equal(registrationFromLogs({stdout:oldStdout,stderr:oldStderr},oldOrigin).registered,false);assert.equal(oldResult.passed,false);assert(oldResult.responses.every(r=>r.status===404&&r.body.bytes===0));assert.equal(oldResult.server.exit.code,130);});
const line='2026-11-07T00:00:00Z  INFO listening for HTTP requests address='+oldOrigin+'\n';
for(const [name,text]of [
 ['early HTTP listener','INFO HTTP server listening addr='+new URL(oldOrigin).host+' protocol="HTTP"\n'],
 ['build started','INFO development session started, building and deploying component...\n'],
 ['build complete','INFO component build complete\n'],
 ['routing warning','WARN failed to route incoming request err=no workload registered\n'],
 ['missing address','INFO listening for HTTP requests\n'],
 ['debug only',line.replace('INFO','DEBUG')],['partial final line',line.trimEnd()],
])test('readiness refuses '+name,()=>assert.equal(registrationFromLogs({stdout:'',stderr:text},oldOrigin).registered,false));
test('Source-derived exact completion marker and origin accepted as MODEL only',()=>{const x=registrationFromLogs({stdout:'',stderr:oldStderr+line},oldOrigin);assert.equal(x.registered,true);assert.equal(x.events.length,1);assert.equal(x.events[0].address,oldOrigin);assert.equal(x.events[0].stream,'stderr');});
test('quoted and ANSI log formatting keeps exact address',()=>assert.equal(registrationFromLogs({stdout:'\u001b[32m'+line.replace('address='+oldOrigin,'address="'+oldOrigin+'"')+'\u001b[0m\n',stderr:''},oldOrigin).registered,true));
test('different leased origin refuses without fallback',()=>assert.throws(()=>registrationFromLogs({stdout:'',stderr:line.replace(oldOrigin,'http://127.0.0.1:1')},oldOrigin)));
test('pinned official source orders await running before readiness event',()=>{assert.equal(plan.listenerSeconds,60);assert.equal(plan.readinessPolicy.capSeconds,60);assert.equal(plan.readinessPolicy.extraHttpRequests,0);});
const official=await readFile(new URL('./upstream/dev.rs',import.meta.url),'utf8'),provenance=JSON.parse(await readFile(new URL('./source-provenance.json',import.meta.url),'utf8'));
test('exact Git blob Source publication and awaited running predicate',()=>{assert.equal(provenance.pinnedCommit,'bc5acfb8e15f7d6d199ca940354d82e590c2d5ff');assert.equal(createHash('sha256').update(official).digest('hex'),provenance.source.sha256);const reload=official.indexOf('let workload_id = reload_component(host.clone(), &workload, None).await?;'),marker=official.indexOf('"listening for HTTP requests"'),signal=official.indexOf('let shutdown = shutdown.ready();');assert(reload>=0&&reload<marker&&marker<signal);assert(official.includes('response.workload_status.workload_state != WorkloadState::Running'));});
test('capture loop is strictly after combined registration and TCP gate',()=>{const gate=code.indexOf("if(registered.registered&&await tcpReady(address.port))"),refusal=code.indexOf("assert(ready,'Exact post-registration marker AND TCP listener unavailable within60s')"),first=code.indexOf('for(const request of contract.requests)');assert(gate>=0&&gate<refusal&&refusal<first);assert(!code.includes('if(await tcpReady(address.port)){ready=true'));});
console.log(JSON.stringify({passed:true,pureDataCases:rows.length,rows,actualHostOrCliOrGuestOrNetworkInvoked:false,actualFilesystemCopyInvoked:false,inertCaptureOnly:true}));
