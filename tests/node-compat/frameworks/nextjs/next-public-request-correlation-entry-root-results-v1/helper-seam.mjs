// Root-only actual helper seam, not a guest/module/logger/HTTP invocation.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const path=fileURLToPath(new URL('../next-public-request-correlation-entry-v1/guest-entry.mjs',import.meta.url));
const before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size<=131072);
assert.equal(await realpath(path),path);
const bytes=await readFile(path),sha256=createHash('sha256').update(bytes).digest('hex');
assert.equal(sha256,'a1d66a6e3427204f5fc0a8e2207836e71eea7b095926ce5b38e4e2ecef65c8d3');
const source=bytes.toString('utf8');
function span(start,end){assert.equal(source.split(start).length,2);assert.equal(source.split(end).length,2);const a=source.indexOf(start),b=source.indexOf(end,a);assert(b>a);return source.slice(a,b);}
const own=span('function ownData(value,key){','function streamError(value){');
const helpers=span('function guestCorrelationCount(count,name){','function guestCompletionBegin(');
const compiled=vm.runInNewContext('(function(){let faults=0;function guestCompletionFault(){faults++;}\n'+own+'\n'+helpers+'\nreturn {count:guestCorrelationCount,snapshot:guestCorrelationSnapshot,request:guestCorrelationRequest,classic:guestCorrelationClassic,faults:()=>faults};})()',{}, {timeout:1000});
const HEADER='x-next-public-request-correlation',value='a'.repeat(64),rows=[];
const snapshot=(state,corr,count)=>({corrState:state,corr,corrCount:count});
function check(id,action,expected){const beforeFaults=compiled.faults();let got,thrown=null;try{got=action();}catch(e){thrown={name:e.name,message:e.message};}const observed=got===undefined?{kind:'undefined'}:JSON.parse(JSON.stringify(got));const passed=thrown===null&&JSON.stringify(observed)===JSON.stringify(expected);rows.push({id,observed,expected,thrown,observerFaults:compiled.faults()-beforeFaults,passed});}
check('valid-adapter-real-Request',()=>compiled.request(new Request('http://127.0.0.1/actions',{headers:{[HEADER]:value}}),1),snapshot('valid',value,1));
check('missing-adapter-real-Request',()=>compiled.request(new Request('http://127.0.0.1/actions'),0),snapshot('missing',null,0));
check('case-insensitive-name',()=>compiled.count(0,HEADER.toUpperCase()),1);
check('saturated-name-count',()=>compiled.count(2,HEADER),2);
check('unrelated-name',()=>compiled.count(0,'x-unrelated'),0);
for(const [id,input] of [['short','a'.repeat(63)],['long','a'.repeat(65)],['final-LF',value+'\n'],['uppercase','A'.repeat(64)],['comma-coalesced',value+', '+value],['nonhex','g'.repeat(64)],['object',{toString(){throw Error('must not coerce');}}]])check('invalid-'+id,()=>compiled.snapshot(input,1),snapshot('invalid',null,1));
check('duplicate',()=>compiled.snapshot(value,2),snapshot('duplicate',null,2));
check('shape-invalid',()=>compiled.snapshot(value,1,false),snapshot('invalid',null,1));
check('classic-own-data',()=>compiled.classic({headers:{[HEADER]:value},rawHeaders:[HEADER,value]}),snapshot('valid',value,1));
check('classic-normalized-comma',()=>compiled.classic({headers:{[HEADER]:value+', '+value},rawHeaders:[HEADER,value+', '+value]}),snapshot('invalid',null,1));
check('classic-two-available-names',()=>compiled.classic({headers:{[HEADER]:value},rawHeaders:[HEADER,value,HEADER.toUpperCase(),value]}),snapshot('duplicate',null,2));
check('classic-odd-array',()=>compiled.classic({headers:{[HEADER]:value},rawHeaders:[HEADER]}),snapshot('invalid',null,1));
check('classic-missing-array',()=>compiled.classic({headers:{[HEADER]:value}}),snapshot('invalid',null,0));
let getters=0;const getterRequest={rawHeaders:[HEADER,value]};Object.defineProperty(getterRequest,'headers',{get(){getters++;throw Error('must not run');}});
check('classic-accessor-not-invoked',()=>compiled.classic(getterRequest),snapshot('invalid',null,1));
check('adapter-observer-throw-contained',()=>compiled.request({get headers(){throw Error('observer input');}},1),{kind:'undefined'});
const after=await lstat(path);for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(after[key],before[key]);
const passed=rows.every(r=>r.passed)&&getters===0&&rows.at(-1).observerFaults===1;
console.log(JSON.stringify({schemaVersion:1,passed,cases:rows.length,rows,source:{path,sha256,bytes:bytes.length},selectedHelperFunctionsEvaluated:true,wholeGuestModuleEvaluated:false,loggerInvoked:false,applicationOrNativeHelperInvoked:false,httpOrGuestOrTargetInvoked:false,getterCalls:getters},null,2));
process.exitCode=passed?0:1;
