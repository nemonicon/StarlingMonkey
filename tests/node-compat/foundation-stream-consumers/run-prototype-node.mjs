import assert from 'node:assert/strict';
import * as node from 'node:stream/consumers';
import * as prototype from './prototype.mjs';
import { createConsumersModule, CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './create-module.mjs';
import { textChecks } from './node-checks.mjs';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
assert.equal(process.version,'v22.14.0');
const hash=value=>createHash('sha256').update(value).digest('hex');
const oracle=JSON.parse(await readFile(new URL('./node-results.json',import.meta.url)));
assert.equal(hash(await readFile(new URL('./node-checks.mjs',import.meta.url))),oracle.sources['node-checks.mjs']);
const cases=await textChecks(prototype);assert.deepEqual(cases,oracle.text);
const contract=JSON.parse(await readFile(new URL('./export-contract.node-v22.14.0.json',import.meta.url)));
assert.deepEqual(Object.keys(prototype).sort(),contract.exports);assert.equal(contract.contractVersion,CONTRACT_VERSION);
const profiles=[];
async function check(name,run){profiles.push({name,result:await run()});}
function checkError(run, code, operation) {
  let failure;try{run();}catch(error){failure=error;}
  assert(failure instanceof Error);assert.equal(failure.code,code);assert.equal(failure.operation,operation);
  assert.equal(failure.module,'node:stream/consumers');assert.equal(failure.profile,CONTRACT_VERSION);
  return {name:failure.name,code:failure.code,operation:failure.operation};
}
async function expectLimit(chunks) {
  const log=[];async function* source(){try{for(const chunk of chunks)yield chunk;}finally{log.push('finally');}}
  let failure;try{await prototype.text(source());}catch(error){failure=error;}
  assert.equal(failure?.code,'ERR_SM_NODE_LIMIT');assert.equal(failure.name,'RangeError');
  assert.deepEqual(log,['finally']);return {code:failure.code,closed:true};
}
await check('all Blob-dependent operations refuse call and construction',()=>{
  const result=[];
  for(const name of ['arrayBuffer','blob','buffer']) {
    assert.equal(prototype[name].name,name);assert.equal(prototype[name].length,1);
    result.push(checkError(()=>prototype[name]([]),'ERR_SM_NODE_UNSUPPORTED',name));
    result.push(checkError(()=>new prototype[name]([]),'ERR_SM_NODE_UNSUPPORTED',name));
  }
  return result;
});
await check('real ESM inspection and default graph',async()=>{
  assert.equal(Object.getPrototypeOf(prototype),null);assert.equal(Object.prototype.toString.call(prototype),'[object Module]');
  assert.equal(prototype.then,undefined);assert.equal(prototype.default.then,undefined);
  assert.equal(await Promise.resolve(prototype),prototype);assert.equal(await Promise.resolve(prototype.default),prototype.default);
  assert.deepEqual(Object.keys(prototype.default),oracle.inventory.defaultKeys);assert.equal(Object.isFrozen(prototype.default),false);
  for(const name of contract.exports.filter(n=>n!=='default'))assert.equal(prototype[name],prototype.default[name]);
  return {namespace:'[object Module]',keys:Object.keys(prototype).sort(),defaultKeys:Object.keys(prototype.default),then:'undefined'};
});
await check('supported function async shape matches pinned Node',()=>{
  for(const name of ['text','json']) {
    assert.equal(prototype[name].name,node[name].name);assert.equal(prototype[name].length,node[name].length);
    assert.deepEqual(Reflect.ownKeys(prototype[name]),Reflect.ownKeys(node[name]));
    assert.equal(prototype[name].constructor.name,'AsyncFunction');
  }
  return {text:'AsyncFunction',json:'AsyncFunction'};
});
await check('default mutation does not rewrite named bindings or lexical json text',async()=>{
  const saved=prototype.default.text;const replacement=()=>{throw new Error('Mutated default must not run');};
  try {prototype.default.text=replacement;assert.equal(prototype.text,saved);assert.deepEqual(await prototype.json(['{"x":1}']),{x:1});}
  finally{prototype.default.text=saved;}
  return {namedRetained:true,jsonUsesLexicalText:true};
});
await check('captured decoder JSON parser and brand helpers',async()=>{
  const saved={ctor:globalThis.TextDecoder,decode:TextDecoder.prototype.decode,parse:JSON.parse,isView:ArrayBuffer.isView,apply:Reflect.apply};
  let called=0;const poison=()=>{called++;throw new Error('Public replacement called');};let output;
  try {
    globalThis.TextDecoder=poison;saved.ctor.prototype.decode=poison;JSON.parse=poison;ArrayBuffer.isView=poison;Reflect.apply=poison;
    output=await prototype.json([new Uint8Array([123,34,120,34,58]),'1}']);
  }finally{globalThis.TextDecoder=saved.ctor;saved.ctor.prototype.decode=saved.decode;JSON.parse=saved.parse;ArrayBuffer.isView=saved.isView;Reflect.apply=saved.apply;}
  assert.equal(called,0);assert.deepEqual(output,{x:1});return {replacementCalls:called,output};
});
await check('string input cap closes ordinary iterator',()=>expectLimit(['a'.repeat(MAX_STRING_INPUT_CODE_UNITS+1)]));
await check('byte input cap rejects before native decode and closes iterator',()=>expectLimit([new Uint8Array(MAX_BYTE_INPUT+1)]));
await check('output cap spans mixed byte and string inputs',()=>expectLimit(['a'.repeat(MAX_OUTPUT_CODE_UNITS),new Uint8Array([66])]));
await check('final decoder flush output cap occurs after source completion',async()=>{
  const log=[];async function* source(){try{yield 'a'.repeat(MAX_OUTPUT_CODE_UNITS);yield new Uint8Array([0xe2]);}finally{log.push('complete');}}
  await assert.rejects(()=>prototype.text(source()),{code:'ERR_SM_NODE_LIMIT',name:'RangeError'});assert.deepEqual(log,['complete']);return {code:'ERR_SM_NODE_LIMIT',log};
});
await check('chunk cap also bounds empty chunks and closes exactly once',async()=>{
  let calls=0,returns=0;const source={[Symbol.asyncIterator](){return this;},async next(){calls++;return {value:'',done:false};},async return(){returns++;return {done:true};}};
  await assert.rejects(()=>prototype.text(source),{code:'ERR_SM_NODE_LIMIT'});assert.equal(calls,MAX_CHUNKS+1);assert.equal(returns,1);
  return {nextCalls:calls,returnCalls:returns};
});
await check('profile cap error wins over iterator-return rejection',async()=>{
  let returns=0;const source={[Symbol.asyncIterator](){return this;},async next(){return {value:new Uint8Array(MAX_BYTE_INPUT+1),done:false};},async return(){returns++;throw new Error('Return failed');}};
  await assert.rejects(()=>prototype.text(source),{code:'ERR_SM_NODE_LIMIT'});assert.equal(returns,1);return {code:'ERR_SM_NODE_LIMIT',returns};
});
await check('factory does not install globals or expose dependencies',()=>{
  const old={Blob:globalThis.Blob,Buffer:globalThis.Buffer,TextDecoder:globalThis.TextDecoder};const created=createConsumersModule();
  assert.deepEqual(Object.keys(created).sort(),contract.exports);assert.equal(Object.isFrozen(created),true);
  assert.equal(globalThis.Blob,old.Blob);assert.equal(globalThis.Buffer,old.Buffer);assert.equal(globalThis.TextDecoder,old.TextDecoder);
  return {frozenRecord:true,globalMutation:false};
});
const sources={};for(const name of ['create-module.mjs','prototype.mjs','node-checks.mjs','run-prototype-node.mjs','export-contract.node-v22.14.0.json','LICENSE.node'])
  sources[name]=hash(await readFile(new URL(name,import.meta.url)));
const report={schema:1,contractVersion:CONTRACT_VERSION,node:process.version,installed:false,nodeOnly:true,
  differentialGroups:cases.length,cases,profileGroups:profiles.length,profiles,sources,
  oracleSha256:hash(await readFile(new URL('./node-results.json',import.meta.url))),
  scope:'Isolated factory and real finite ESM host tests use Node22 native TextDecoder. No StarlingMonkey guest/component run, Blob implementation or production registration is exercised.',
  limits:{MAX_BYTE_INPUT,MAX_CHUNKS,MAX_OUTPUT_CODE_UNITS,MAX_STRING_INPUT_CODE_UNITS},
  limitations:['Native Blob-dependent exports are explicit refusals, not JS copies or blank objects','No getter/detach/shared lifetime or OOM probe','No byte-copy timing, native scheduling, guest iterator cancellation, snapshot or host-import support claim from host tests']};
await writeFile(new URL('./prototype-node-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({differentialGroups:cases.length,profileGroups:profiles.length,nodeOnly:true,installed:false}));
