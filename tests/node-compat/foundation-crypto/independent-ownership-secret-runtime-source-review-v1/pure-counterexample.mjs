// Extract ONLY two inert functions; no source module/helper/generated import.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile,writeFile} from 'node:fs/promises';
const source='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v1/runtime-body.mjs';
const text=await readFile(source,'utf8'),start=text.indexOf('export function primitive('),end=text.indexOf('async function finalProtection(');
assert(start>=0&&end>start);const block=text.slice(start,end).replace(/^export /gm,'');
const context=vm.createContext({need:(v,m)=>{if(!v)throw new Error(m);}});
vm.runInContext(block+'\nglobalThis.testCall=capturedCall;',context,{timeout:1000});
const rows=[];
for(const original of [new Error('synthetic original guest throw'),Object.freeze({synthetic:'frozen-original'}),null,false,0,'synthetic-original-string']){
 const writer=new Error('synthetic capture writer failure'),sequence={attempted:0,written:0};let caught;
 try{await context.testCall({invoke(){throw original;},name:'run',args:[0],sequence,write:async()=>{throw writer;}});}catch(e){caught=e;}
 assert.equal(caught,writer);assert.notEqual(caught,original);assert.deepEqual(sequence,{attempted:1,written:0});
 rows.push({originalType:typeof original,originalNull:original===null,propagatedWriterIdentity:true,originalIdentityLost:true,attempted:1,written:0});
}
const original=Object.freeze({synthetic:'successfully-retained-throw'}),sequence={attempted:0,written:0};let caught,retained;
try{await context.testCall({invoke(){throw original;},name:'inspect',args:[],sequence,write:async(p,v)=>{retained=v;}});}catch(e){caught=e;}
assert.equal(caught,original);assert.equal(retained.kind,'throw');assert.deepEqual(sequence,{attempted:1,written:1});
const result={schemaVersion:1,sourceFunctionOnlyExtracted:true,sourceModuleImported:false,ownerAPIOrGeneratedOrEngineOrGuestInvoked:false,pureCases:7,combinedCases:rows,successfulCapturePreservesOriginal:true,finding:'M1_COMBINED_THROW_AND_CAPTURE_WRITER_FAILURE_MASKS_ORIGINAL'};
console.log(JSON.stringify(result));
