// Read-only check of the experimental selected-clock ReactDOM evidence.
// node check-clock-render.mjs RUNTIME_DIRECTORY ROOT_REPORT.json [--self-test]
// This does not execute a component or re-audit its emitted type graph.
import assert from 'node:assert/strict';
import {readFile,readdir,lstat} from 'node:fs/promises';
import {resolve,join,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {parseScalarStringOutput} from '../../foundation-scheduler/clock-v13-runtime-candidate-v2/wave.mjs';

const SOURCE='135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384';
const COMPONENT='5c002f8da675016fd7061d245074965413d6914e4f40eb2a32a8141c1f3b7460';
const ENGINE='d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92';
const CAPS=['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10'];
const hash=b=>createHash('sha256').update(b).digest('hex');
const local=n=>typeof n==='string'&&n&&!isAbsolute(n)&&!n.includes('\\')&&n.split('/').every(v=>v&&v!=='.'&&v!=='..');
function descriptor(bytes,row){assert.equal(bytes.length,row.bytes);assert.equal(hash(bytes),row.sha256);}
function cleanInner(t){
  assert.equal(t.closed,true);assert.equal(t.status,0);assert.equal(t.signal,null);
  assert.equal(t.ownedGroupGone,true);assert.equal(t.terminalExitZeroObserved,true);
  for(const k of ['timedOut','outputLimitExceeded'])assert.equal(t[k],false);
  assert.equal(t.spawnError,null);assert.equal(t.externalSignal,null);
  assert.equal(t.signalCount,0);assert.deepEqual(t.signals,[]);assert.deepEqual(t.errors,[]);
}
export function auditValues({root,result,native,oracle,jco,wasmtime,terminals}){
  assert.equal(root.state,'ROOT_OBSERVED_CLOCK_V13_REACTDOM_DIFFERENTIAL_ZERO_UNREVIEWED_V2');
  assert.equal(root.toolObservation.rawExitCode,0);assert.deepEqual(root.selectedInterfaces,CAPS);
  assert.equal(result.state,'CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V2');
  assert.equal(result.sourceIndex.sha256,SOURCE);assert.equal(result.component.sha256,COMPONENT);
  for(const row of [root,result]){
    assert.equal(row.jcoRetainedWholeStrings,3);assert.equal(row.jcoFreshWholeStrings,1);
    assert.equal(row.stockWasmtimeFreshWholeStrings,3);assert.equal(row.allWholeStringsEqualRetainedNode,true);
    for(const k of ['hostCallCountsObserved','resourceDateSnapshotTimerTeardownSevenCaseGateComplete','fullClockProfileAcceptance','operationalAdmission','runtimeAcceptanceClaim'])assert.equal(row[k],false);
  }
  assert.equal(result.sessions.length,5);assert.equal(terminals.length,5);
  assert.deepEqual(result.sessions.map(s=>s.host),['jco-standard-wasi-shim','jco-standard-wasi-shim','stock-wasmtime42','stock-wasmtime42','stock-wasmtime42']);
  assert.equal(result.sessions[0].scenario,'retained');assert.equal(result.sessions[1].scenario,'fresh');
  const metadata=native.metadata;assert.equal(Object.keys(metadata).length,64);
  assert.equal(metadata.engineSha256,ENGINE);assert.equal(metadata.sourceManifest.length,342);
  assert.equal(metadata.componentizeSourceManifest.length,3);assert.equal(metadata.selectedModuleManifests.length,9);
  assert.equal(native.variant,'normal-off');assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
  assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);
  assert.equal(typeof oracle,'string');assert.deepEqual(JSON.parse(oracle),{library:'react-dom/server.edge',html:'<p id="wasm-ssr">Hello from real ReactDOM</p>',bytes:45});
  assert.equal(jco.length,4);assert.equal(wasmtime.length,3);
  for(const row of jco){assert.equal(row.name,'run');assert.deepEqual(row.args,[]);assert.equal(row.kind,'return');assert.equal(row.observed.type,'string');assert.equal(row.observed.value,oracle);}
  for(const value of wasmtime)assert.equal(value,oracle);
  for(const terminal of terminals)cleanInner(terminal);
  assert.equal(new Set(terminals.map(t=>t.pid)).size,5);
  return {passed:true,wholeNodeEqualStrings:7,jcoRetained:3,jcoFresh:1,wasmtimeFresh:3,recordedSelectedInterfaces:CAPS,fullClockProfileAcceptance:false,fullNextServerClaim:false};
}
export async function checkClockRender(directory,rootReport,{selfTest=false}={}){
  directory=resolve(directory);assert.equal((await lstat(directory)).isSymbolicLink(),false);
  const root=JSON.parse(await readFile(rootReport,'utf8')),indexBytes=await readFile(join(directory,'index.json'));
  descriptor(indexBytes,root.actualIndex);const index=JSON.parse(indexBytes),files=new Map();
  for(const row of index.files){assert(local(row.path));assert(!files.has(row.path));const path=join(directory,row.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());const b=await readFile(path);descriptor(b,row);files.set(row.path,b);}
  const names=[];async function walk(path,prefix=''){for(const name of await readdir(path)){const p=join(path,name),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p,prefix+name+'/');else{assert(s.isFile());names.push(prefix+name);}}}await walk(directory);
  assert.deepEqual(names.sort(),[...files.keys(),'index.json','completion.json'].sort());
  const json=n=>{assert(files.has(n),n);return JSON.parse(files.get(n));};
  const result=json('result.json');descriptor(files.get('result.json'),root.actualResult);
  const completionBytes=await readFile(join(directory,'completion.json'));descriptor(completionBytes,root.actualCompletion);const completion=JSON.parse(completionBytes);
  assert.equal(completion.externalRawZeroAndReviewRequired,true);assert.equal(completion.index.path,'index.json');descriptor(indexBytes,completion.index);assert.equal(completion.result.path,'result.json');descriptor(files.get('result.json'),completion.result);
  const native=json('native-frame-data.json');
  for(const scenario of ['retained','fresh'])assert.deepEqual(json(scenario+'/native-frame-data.json'),native);
  const oracle=json('retained-node-oracle.json');assert.equal(oracle.rerun,false);
  const jco=[...['001','002','003'].map(n=>json('retained/raw/'+n+'.json')),json('fresh/raw/001.json')];
  const terminals=['jco-retained','jco-fresh','wasmtime-0','wasmtime-1','wasmtime-2'].map(n=>json('processes/'+n+'.terminal.json'));
  const wasmtime=[];
  for(let n=0;n<3;n++){
    const t=terminals[n+2],b=files.get('processes/wasmtime-'+n+'.stdout.txt');assert(b);descriptor(b,t.stdout);
    const value=parseScalarStringOutput({stdoutBytes:b,rawDurablyRetained:true});assert.equal(json('wasmtime-'+n+'.decoded.json').value,value);wasmtime.push(value);
  }
  const processNames=['jco-retained','jco-fresh','wasmtime-0','wasmtime-1','wasmtime-2'];
  for(let n=0;n<terminals.length;n++){
    const name=processNames[n],t=terminals[n];assert.equal(t.name,name);
    descriptor(files.get('processes/'+name+'.terminal.json'),result.sessions[n].terminal);
    for(const stream of ['stdout','stderr']){
      assert(t[stream].path.endsWith('/processes/'+name+'.'+stream+'.txt'));
      descriptor(files.get('processes/'+name+'.'+stream+'.txt'),t[stream]);
    }
    if(n>=2)assert.deepEqual(t.args,['run','--invoke','run()',result.component.path]);
  }
  const data={root,result,native,oracle:oracle.value,jco,wasmtime,terminals},report=auditValues(data);
  if(selfTest){
    const negatives=[
      d=>d.jco.pop(),d=>{d.jco[0].kind='throw';},d=>{d.jco[0].observed.value+=' ';},
      d=>d.wasmtime.pop(),d=>{d.wasmtime[0]+=' ';},d=>{d.root.jcoRetainedWholeStrings=2;},
      d=>d.root.selectedInterfaces.push('wasi:random/random@0.2.10'),d=>{d.result.fullClockProfileAcceptance=true;},
      d=>{d.result.component.sha256='0'.repeat(64);},d=>{d.result.sourceIndex.sha256='0'.repeat(64);},
      d=>d.native.metadata.sourceManifest.pop(),d=>{d.terminals[0].timedOut=true;},
      d=>{d.terminals[1].pid=d.terminals[0].pid;},d=>{d.result.sessions[0].scenario='fresh';},
      d=>{d.result.allWholeStringsEqualRetainedNode=false;},d=>{d.native.metadata.entropyPolicy='on';},
      d=>{d.terminals[0].ownedGroupGone=false;},d=>{d.jco[0].observed.type='object';},
    ];
    for(const change of negatives){const copy=structuredClone(data);change(copy);assert.throws(()=>auditValues(copy));}
    report.rejectedInjectedCases=negatives.length;
  }
  return report;
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){
  try{assert([4,5].includes(process.argv.length),'Expected RUNTIME_DIRECTORY ROOT_REPORT.json [--self-test]');if(process.argv.length===5)assert.equal(process.argv[4],'--self-test');console.log(JSON.stringify(await checkClockRender(process.argv[2],process.argv[3],{selfTest:process.argv.length===5}),null,2));}
  catch(error){console.error('Clock render evidence check failed: '+error.message);process.exitCode=1;}
}
