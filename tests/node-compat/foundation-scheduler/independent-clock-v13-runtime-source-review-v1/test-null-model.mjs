// Pure extracted capture + exact catch/guard model; never calls an action/worker.
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=await readFile(new URL('../clock-v13-runtime-candidate-v1/body.mjs',import.meta.url),'utf8');
const text=source.slice(source.indexOf('export function observed('),source.indexOf('async function retainNative(')).replaceAll('export ','');
const context=vm.createContext({need(v,m){assert.ok(v,m);}});
const {capturedRun}=new vm.Script(text+';({capturedRun})').runInContext(context);
const records=[],sequence={attempted:0,written:0};let caught=false,thrown;
try{await capturedRun(()=>{throw null;},async(name,row)=>records.push({name,row}),sequence);}catch(e){caught=true;thrown=e;}
assert.ok(caught&&thrown===null&&sequence.attempted===1&&sequence.written===1&&records[0].row.kind==='throw'&&records[0].row.observed.value===null);
assert.equal((source.match(/catch\(error\)\{primary=error;\}/g)||[]).length,3);
assert.equal((source.match(/if\(primary!==null\|\|finalErrors.length\)/g)||[]).length,3);
const condition='primary!==null||finalErrors.length';
const classify=vm.runInNewContext('(value)=>{let primary=null, finalErrors=[];try{throw value;}catch(error){primary=error;}return Boolean('+condition+');}');
assert.equal(classify(null),false);
for(const value of [undefined,false,0,'',NaN,{}])assert.equal(classify(value),true);
// The parent full-raw predicate independently rejects the retained throw.
const r=records[0].row;assert.equal(r.name==='run'&&JSON.stringify(r.args)==='[]'&&r.kind==='return'&&r.observed.type==='string',false);
console.log(JSON.stringify({schemaVersion:1,pureModelPassed:true,checks:11,actualSourceCaptureRetainsNullThrow:true,threeBodyPrimarySentinelsMissNull:true,parentWholeRawGuardRejectsThrow:true,actualGeneratedWasmCallableInvoked:false,observedRuntimeFailure:false,ownerOrMonitorOrShimOrGuestInvoked:false}));
