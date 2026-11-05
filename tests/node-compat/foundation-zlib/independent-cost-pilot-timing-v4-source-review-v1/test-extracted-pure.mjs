// Independent actual-source excerpts only. No module/helper/entrypoint imports.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const D=new URL('../cost-pilot-timing-candidate-v4/',import.meta.url),V1=new URL('../cost-pilot-timing-candidate-v1/',import.meta.url);
const text=name=>readFile(new URL(name,D),'utf8');let checks=0;const notes=[];function check(name,fn){fn();checks++;notes.push(name);}
const policy=await readFile(new URL('lifecycle-policy.mjs',V1),'utf8'),literal=policy.match(/export const MEASUREMENT_ENV=Object\.freeze\((\{[\s\S]*?\})\);/)[1],base=new Function('return '+literal)();
const proof=await readFile(new URL('proof-model.mjs',V1),'utf8'),equality=proof.slice(proof.indexOf('export function stable('),proof.indexOf('export function providerComparisons(')).replaceAll('export ',''),same=new Function(equality+';return same;')();
const envSource=await text('environment.mjs'),envCode=envSource.slice(envSource.indexOf('export function measurementEnvironmentModel(')).replace('export function','function'),model=new Function('MEASUREMENT_ENV','same',envCode+';return measurementEnvironmentModel;')(Object.freeze(base),same);
check('actual eight-value requested map',()=>assert.equal(Object.keys(base).length,8));
const facts={platform:'darwin',uid:501},cf='0x1F5:0x0:0x0';
for(const [name,input,platform]of[['exact Darwin',{...base},facts],['exact other OS',{...base},{platform:'linux',uid:501}],['sole current Darwin CF',{...base,__CF_USER_TEXT_ENCODING:cf},facts]])check(name,()=>{const before=JSON.stringify(input);assert.equal(model(input,platform),true);assert.equal(JSON.stringify(input),before);});
for(const name of Object.keys(base)){
 const absent={...base};delete absent[name];check('reject missing '+name,()=>assert.throws(()=>model(absent,facts)));
 check('reject changed '+name,()=>assert.throws(()=>model({...base,[name]:'foreign'},facts)));
}
for(const key of['NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','LD_PRELOAD','UNKNOWN'])check('reject extra '+key,()=>assert.throws(()=>model({...base,[key]:'1'},facts)));
for(const [name,value,platform]of[['wrong uid','0x1F4:0x0:0x0',facts],['lowercase uid','0x1f5:0x0:0x0',facts],['wrong zeros','0x1F5:0x1:0x0',facts],['non-Darwin',cf,{platform:'linux',uid:501}],['uid out of range',cf,{platform:'darwin',uid:0x100000000}]])check('reject CF '+name,()=>assert.throws(()=>model({...base,__CF_USER_TEXT_ENCODING:value},platform)));
let reads=0;const accessor={...base};Object.defineProperty(accessor,'PATH',{get(){reads++;throw Error('not read');},enumerable:true});check('accessor refused before getter',()=>assert.throws(()=>model(accessor,facts)));check('zero environment getter reads',()=>assert.equal(reads,0));
check('symbol extra refuses',()=>assert.throws(()=>model({...base,[Symbol()]:'1'},facts)));
const nonEnumerable={...base};Object.defineProperty(nonEnumerable,'UNKNOWN',{value:'not a snapshot field',enumerable:false});check('record unreachable arbitrary-object limitation',()=>assert.equal(model(nonEnumerable,facts),true));
const entry=await text('worker.mjs'),stages=entry.match(/export const BOOTSTRAP_STAGES=Object\.freeze\((\[[\s\S]*?\])\);/)[1],names=new Function('return '+stages)(),start=entry.indexOf('export function bootstrapFailureLine('),end=entry.indexOf('\nexport async function runWorker(',start),formatter=new Function('BOOTSTRAP_STAGES','Buffer',entry.slice(start,end).replace('export function','function')+';return bootstrapFailureLine;')(Object.freeze(names),Buffer);
let errorReads=0;const hostile=new Proxy({}, {get(){errorReads++;throw 1;},ownKeys(){errorReads++;throw 2;},getPrototypeOf(){errorReads++;throw 3;}});
for(const error of[hostile,undefined,null,NaN,Infinity,-0,1n,Symbol(),()=>{},'large '.repeat(100000)])check('actual formatter no properties '+typeof error,()=>{const raw=formatter('execution-environment',true,error),r=JSON.parse(raw);assert(Buffer.byteLength(raw)<=2048);assert.equal(r.thrownType,typeof error);assert.equal(r.exceptionPropertiesRead,false);assert.equal(r.fullExceptionValueCaptured,false);assert.equal(r.uniqueFailureCauseProven,false);});
check('hostile caught value never read',()=>assert.equal(errorReads,0));for(const stage of names)check('all finite labels '+stage,()=>assert.equal(JSON.parse(formatter(stage,false,hostile)).stage,stage));
check('arbitrary label denied',()=>assert.throws(()=>formatter('guest-controlled',true,hostile)));check('nonboolean source flag denied',()=>assert.throws(()=>formatter('body-entry',{},hostile)));
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_EXTRACTED_V4_ENVIRONMENT_DIAGNOSTIC_PURE_CHECKS_PASSED',checks,notes,actualAuthorModuleImported:false,sourceEntriesOrHelpersInvoked:false,providerCodecOrGuestInvoked:false,caughtValuePropertyReads:errorReads,environmentGetterReads:reads,nonEnumerableArbitraryObjectAcceptedButNotRealCallerDomain:true,actualCallerDomain:'fresh enumerable own-string {...process.env} snapshots only'}));
