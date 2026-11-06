// Retained DATA only. No application/probe/oracle/generated module is imported.
import assert from 'node:assert/strict';
import {readFile,readdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const read=async p=>JSON.parse(await readFile(join(here,p),'utf8'));
const hash=b=>createHash('sha256').update(b).digest('hex');
const idx=await read('index.json'),names=idx.files.map(r=>r.path);
assert.equal(new Set(names).size,names.length);
const actual=[];
async function walk(dir){for(const n of await readdir(dir)){const p=join(dir,n),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p);else{assert(s.isFile());actual.push(relative(here,p));}}}
await walk(here);assert.deepEqual(actual.filter(n=>n!=='index.json').sort(),[...names].sort());
for(const r of idx.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));const b=await readFile(join(here,r.path));assert.equal(b.length,r.bytes);assert.equal(hash(b),r.sha256);}
const copies=(await read('copies.json')).copies,map=new Map();
for(const r of copies){assert(!map.has(r.original.path));const b=await readFile(join(here,r.copy.path));assert.equal(hash(b),r.original.sha256);assert.equal(b.length,r.original.bytes);assert.equal(r.copy.sha256,r.original.sha256);assert.equal(r.copy.bytes,r.original.bytes);map.set(r.original.path,r);}
async function ref(r){const x=map.get(r.path);assert(x,'Missing retained descriptor '+r.path);assert.deepEqual(x.original,r);return read(x.copy.path);}
async function bytesRef(r){const x=map.get(r.path);assert(x,'Missing retained bytes '+r.path);assert.deepEqual(x.original,r);return readFile(join(here,x.copy.path));}
function clean(t,code){assert.equal(t.rawExitCode,code);for(const k of ['timeout','forcedCleanup'])assert.equal(t[k],false);for(const k of ['parentOwnedGroupGone','allObservedOwnedGroupsGone'])assert.equal(t[k],true);for(const k of ['signals','interruptedSignals','errors','remainingObservedPids'])assert.deepEqual(t[k],[]);}
async function terminal(p,code){const t=await read(p);clean(t,code);await bytesRef(t.stdout);await bytesRef(t.stderr);return t;}
const r=await read('evidence/http/result.json'),ob=await read('evidence/http-outer/observation.json'),auth=await read('evidence/root/http-authority.json');
assert.equal(r.state,'ISOLATED_STACKTRACE_SELECTED_DIFFERENCES_OBSERVED_V1');assert.equal(ob.state,'ROOT_ISOLATED_STACKTRACE_PROBE_OBSERVATION_V1');
assert.equal(r.observationsValid,true);assert.equal(r.nodeSelectedParity,false);assert.equal(r.inputsPreserved,true);assert.deepEqual(r.errors,[]);assert.equal(r.comparisonComplete,true);assert.equal(r.allThreeCaptureAttemptsComplete,true);
for(const k of ['applicationMounted','applicationImported','fullNextAcceptance','adoption'])assert.equal(r[k],false);
assert.deepEqual(await ref(r.rootAuthority),auth);assert.deepEqual(r.sourceIndex,auth.sourceIndex);assert.deepEqual(r.component,auth.component);assert.deepEqual(r.componentAudit,auth.componentAudit);
assert.deepEqual(await ref(auth.sourceIndex),await read('source/stacktrace-wasmtime-collector-v1/index.json'));
const plan=await ref(auth.plan);assert.deepEqual(auth.constructionCallerIndex,plan.constructionCallerIndex);assert.equal(auth.state,'ROOT_STACKTRACE_HTTP_PROBE_AUTHORIZED_V1');
for(const k of ['ordinaryProbeAllowed','loopbackServeAllowed'])assert.equal(auth[k],true);for(const k of ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed'])assert.equal(auth[k],false);
assert.deepEqual(await ref(ob.result),r);assert.deepEqual(await ref(ob.terminal),await terminal('evidence/http-outer/terminal.json',1));
assert.equal(ob.rawExitCode,1);assert.equal(ob.ownedGroupsClean,true);assert.equal(ob.protectedInputsPreserved,true);assert.equal(ob.observationsValid,true);assert.equal(ob.nodeSelectedParity,false);
const nt=await terminal('evidence/node-owned/terminal.json',0);assert.deepEqual(nt.stdout,auth.nodeOracleStdout);assert.deepEqual(await ref(auth.nodeOracleTerminal),nt);
const na=await read('evidence/root/node-authority.json'),ns=await read('evidence/node-owned/started.json');assert.equal(na.state,'ROOT_STACKTRACE_NODE_ORACLE_V1');assert.deepEqual(na.node,plan.node);assert.deepEqual(na.sourceIndex,plan.probeSourceIndex);assert.deepEqual(na.entry,plan.nodeOracleSource);assert.equal(na.calls,3);assert.equal(na.capSeconds,60);assert.deepEqual(ns.argv,[plan.node.path,plan.nodeOracleSource.path]);assert.equal(ns.timeoutSeconds,60);assert.deepEqual(await ref(ns.authority),na);await bytesRef(na.cases);
const oracleBytes=await bytesRef(auth.nodeOracleStdout);assert.deepEqual(await readFile(join(here,'evidence/http/node-oracle.stdout.jsonl')),oracleBytes);
const nodeFrames=oracleBytes.toString('utf8').trim().split('\n').map(JSON.parse);assert.equal(nodeFrames.length,4);assert.equal(nodeFrames[0].kind,'node-oracle-identity');assert.equal(nodeFrames[0].node,'v22.14.0');assert.equal(nodeFrames[0].guestExecuted,false);
// The copied comparator is authenticated above; importing it performs no IO.
const {validate,compare,ids}=await import('./comparison.mjs');
assert.equal(r.responses.length,3);const comparisons=[],semantic=[];
for(let i=0;i<3;i++){
 const call=i+1,q=r.responses[i],nf=nodeFrames[call];assert.equal(q.call,call);assert.equal(q.status,200);assert.equal(q.transportError,undefined);assert.equal(q.ordinalValidated,true);assert.equal(q.rawValueType,'Uint8Array');
 const b=await bytesRef(q.body);assert.equal(Number(q.headers['content-length']),b.length);assert.match(q.headers['content-type'],/^application\/json/);const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(b));assert.deepEqual(q.typedPayload,value);
 assert.equal(nf.call,call);assert.equal(nf.kind,'string');assert.equal(typeof nf.value,'string');const node=JSON.parse(nf.value);validate(value,call);validate(node,call);assert.equal(value.errorGlobalsRestored,true);assert.equal(node.errorGlobalsRestored,true);
 const c=compare(value,node,call);assert.equal(c.nodeSelectedParity,false);assert.deepEqual(c.differences,ids);comparisons.push(c);
 const [plain,structured,throwing,depd]=value.records;assert(value.records.every(v=>v.completed));assert.equal(plain.value.stackOwnDescriptor.data,true);assert.equal(plain.value.stackOwnDescriptor.valueType,'string');assert.equal(structured.value.callbackInvocations,0);assert.equal(structured.value.callbackFrames,null);assert.equal(structured.value.stack.valueType,'string');assert.equal(throwing.value.callbackInvocations,0);assert.equal(throwing.value.captureReturned,true);assert.equal(throwing.value.stackReadReturned,true);assert.equal(throwing.value.captureThrown,null);assert.equal(throwing.value.stackReadThrown,null);assert.equal(depd.value.depdLocationSucceeded,false);assert.deepEqual(depd.value.locationError.name,{type:'string',value:'TypeError'});assert.deepEqual(depd.value.locationError.message,{type:'string',value:'e.getFileName is not a function'});
 assert.equal(node.records[1].value.callbackInvocations,1);assert.equal(node.records[1].value.callbackTargetIdentity,true);assert.equal(node.records[2].value.stackReadThrown.identity,true);assert.equal(node.records[3].value.depdLocationSucceeded,true);
 semantic.push({call,eagerStringStack:true,prepareStackTraceCallbacks:0,throwingCallbackInvoked:false,depdLocationSucceeded:false,depdError:'TypeError: e.getFileName is not a function'});
}
assert.deepEqual(comparisons,r.comparisons);assert.deepEqual(r.selectedDifferences,comparisons.flatMap(c=>c.differences.map(id=>({call:c.call,id}))));
const stdout=(await readFile(join(here,'evidence/http-outer/stdout.log'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(stdout.length,1);assert.equal(stdout[0].observationsValid,true);assert.equal(stdout[0].nodeSelectedParity,false);assert.deepEqual(stdout[0].selectedDifferences,r.selectedDifferences);
assert.equal(r.server.shutdownRequested,true);assert.equal(r.server.sigintSent,true);assert.equal(r.server.forcedCleanup,false);assert.deepEqual(r.server.exit,{code:0,signal:null,error:null});await bytesRef(r.server.stdout);await bytesRef(r.server.stderr);
assert.equal(r.server.command[0],plan.wasmtime.path);assert.equal(r.server.command.at(-1),r.component.path);assert(r.server.command.includes('cli=y,tcp=n,udp=n,allow-ip-name-lookup=n'));assert(!r.server.command.some(s=>s.startsWith('--dir')));assert.equal(r.server.command[r.server.command.indexOf('--max-instance-reuse-count')+1],'32');assert.equal(r.server.command[r.server.command.indexOf('--idle-instance-timeout')+1],'60s');
const c=await read('evidence/construction/result.json');assert.deepEqual(await ref(auth.constructionResult),c);assert.equal(c.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(c.passed,true);assert.equal(c.entryMode,'stacktrace-probe');assert.equal(c.finalProtection.unchanged,true);assert.equal(c.error,null);assert.deepEqual(c.callerIndex,auth.constructionCallerIndex);
assert.deepEqual(await ref(c.rootAuthority),await read('evidence/root/construction-authority.json'));
for(const [k,v]of Object.entries({component:r.component,componentAudit:r.componentAudit,inputEntry:plan.probeEntry,inputSourceIndex:plan.probeSourceIndex,engine:plan.engine,nativeMetadata:plan.nativeMetadata,adapter:plan.adapter}))assert.deepEqual(c.artifacts[k],v);
assert.equal(c.commands.length,3);assert.deepEqual(c.commands.map(x=>x.label),['componentize-init','component-validate','component-wit']);
for(const q of c.commands){assert.equal(q.rawExitCode,0);assert.equal(q.clean,true);const t=await ref(q.terminal);clean(t,0);assert.deepEqual(t.stdout,q.stdout);assert.deepEqual(t.stderr,q.stderr);await bytesRef(q.stdout);await bytesRef(q.stderr);}
await terminal('evidence/construction-outer/terminal.json',0);
const outerFrames=(await readFile(join(here,'evidence/construction-outer/stdout.log'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(outerFrames.length,4);assert.equal(outerFrames[3].passed,true);assert.deepEqual(await ref(outerFrames[3].result),c);
const a=await ref(c.artifacts.componentAudit);assert.equal(a.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(a.passed,true);assert.deepEqual(a.component,r.component);assert.equal(a.entryMode,'stacktrace-probe');assert.equal(a.noExternalPreview1OrCustomImports,true);assert.equal(a.allEmittedVersion,'0.2.10');assert.deepEqual(a.exports,['wasi:http/incoming-handler@0.2.10']);assert.deepEqual([...a.selectedInterfaces].sort(),[...plan.selectedInterfaces].sort());assert.equal(a.emittedImports.length,13);assert.equal(new Set(a.emittedImports).size,13);assert(a.emittedImports.every(x=>a.selectedInterfaces.includes(x)&&x.endsWith('@0.2.10')));
assert.deepEqual(a.validateTerminal,c.commands[1].terminal);assert.deepEqual(a.witTerminal,c.commands[2].terminal);
const imports=await ref(c.artifacts.returnedImports);assert(imports.every(x=>Array.isArray(x)&&x.length===2&&x.every(s=>typeof s==='string')));assert.deepEqual([...new Set(imports.map(x=>x[0]))].sort(),[...a.emittedImports].sort());
const shape=await ref(c.artifacts.returnedOwnShape);assert.equal(shape.type,'object');const componentShape=shape.properties.find(p=>p.key.string==='component');assert.equal(componentShape.kind,'data');assert.equal(componentShape.value.type,'Uint8Array');assert.equal(componentShape.value.byteLength,r.component.bytes);assert.equal(componentShape.value.sha256,r.component.sha256);assert.deepEqual(componentShape.value.file,r.component);assert(shape.properties.some(p=>p.key.string==='imports'&&p.kind==='data'&&p.value.type==='Array'));
const nr=await read('evidence/construction/api-return/node-result.json');assert.equal(nr.state,'NEXT_NATIVE_COMPONENT_API_RETURN_CAPTURED_UNREVIEWED_V1');assert.equal(nr.entryMode,'stacktrace-probe');assert.deepEqual(nr.inputEntry,c.artifacts.inputEntry);assert.deepEqual(nr.inputSourceIndex,c.artifacts.inputSourceIndex);for(const k of ['component','returnedImports','returnedOwnShape'])assert.deepEqual(nr.artifacts[k],c.artifacts[k]);assert.equal(nr.ordinaryExportsInvoked,false);
console.log(JSON.stringify({schemaVersion:1,state:'STACKTRACE_FAILED_EXPERIMENT_RETAINED_DATA_CHECK_PASSED_V1',curationChecksPassed:true,underlyingExperimentExitCode:1,observationsValid:true,nodeSelectedParity:false,http200Calls:3,retainedCaseRecords:12,differentCaseRecords:12,constructorRawZeroCommands:3,nodeOracleRawExitCode:0,ownedCleanupVerified:true,sourceCoupledProtectionReported:true,portableNativeInputsReexecuted:false,semantic,fullNextAcceptance:false,adoption:false}));
