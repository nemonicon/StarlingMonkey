// Pure null-pin and tiny scratch source-seal checks, never native preflight.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,resolve} from 'node:path';
import {selectClassicPin} from './runtime-contract.mjs';
import {verifyConsumedSeal} from './consumed.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);
assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const output=resolve(process.env.NODE_COMPAT_TRACE_ACTIVATION_TEST_OUTPUT??'');
assert(process.env.NODE_COMPAT_TRACE_ACTIVATION_TEST_OUTPUT&&output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Fresh owned output required');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(output,{recursive:false});
const hash=data=>createHash('sha256').update(data).digest('hex'),checks=[];
const pass=name=>checks.push(name);
const nullPins=JSON.parse(await readFile(new URL('./runtime-pins.json',import.meta.url)));
const recipe='3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3';
for(const variant of ['normal-off','normal-runtime','gc-off','disabled-off']){
 assert.throws(()=>selectClassicPin(nullPins,{variant,recipeSha256:recipe}));pass('null future pin refuses '+variant);
}
assert.throws(()=>selectClassicPin(nullPins,{variant:'unknown',recipeSha256:recipe}));pass('unknown variant refuses');
const before=await readFile(new URL('../production-runtime-activated-v3/runtime-pins.json',import.meta.url));
assert.throws(()=>selectClassicPin(JSON.parse(before),{recipeSha256:recipe}));pass('old reviewed document refuses');
const template=await readFile(new URL('./runtime-preflight.template.mjs',import.meta.url));
const replacements=Object.fromEntries(['PINS_SHA','INPUTS_SHA','RECIPE_SHA','SELECTOR_SHA','ADMISSION_SHA','ROOT_REVIEW_SHA'].map((key,i)=>[key,String(i+1).repeat(64)]));
let compiled=template.toString();for(const[key,value]of Object.entries(replacements))compiled=compiled.replaceAll('@'+key+'@',value);
assert.doesNotMatch(compiled,/@[A-Z_]+@/);pass('six placeholders bind completely without evaluating compiled preflight');
const files={'runtime-preflight.template.mjs':template,'data.txt':Buffer.from('owned small data\n'),'root-review-receipt.json':Buffer.from('{"scratchOnly":true}\n')};
for(const[name,data]of Object.entries(files))await writeFile(join(output,name),data,{flag:'wx'});
await writeFile(join(output,'runtime-preflight.mjs'),compiled,{flag:'wx'});
const document={schemaVersion:1,inputs:Object.entries(files).map(([path,data])=>({path,sha256:hash(data),bytes:data.length,boundary:'.'})),toolTrees:[],toolLinks:[]};
const raw=Buffer.from(JSON.stringify(document));await writeFile(join(output,'input-freeze.json'),raw,{flag:'wx'});
assert.equal(await verifyConsumedSeal(output,hash(raw),replacements,{invocation:false}),3);pass('unchanged consumed helper accepts tiny scratch source seal');
const poisoned=Buffer.from(JSON.stringify({...document,inputs:[{path:'must-not-be-read',sha256:'0'.repeat(64),bytes:1}]}));
await writeFile(join(output,'input-freeze.json'),poisoned);
await assert.rejects(()=>verifyConsumedSeal(output,hash(raw),replacements,{invocation:false}),/Consumed-input manifest changed/);pass('manifest hash checked before following changed rows');
await writeFile(join(output,'input-freeze.json'),raw);
await writeFile(join(output,'runtime-preflight.mjs'),compiled+'\n');
await assert.rejects(()=>verifyConsumedSeal(output,hash(raw),replacements,{invocation:false}),/Compiled preflight differs/);pass('compiled template mismatch refuses');
await writeFile(join(output,'runtime-preflight.mjs'),compiled);
await writeFile(join(output,'root-review-receipt.json'),'changed');
await assert.rejects(()=>verifyConsumedSeal(output,hash(raw),replacements,{invocation:false}));pass('changed review bytes refuse through captured source seal');
await writeFile(join(output,'root-review-receipt.json'),files['root-review-receipt.json']);
assert.equal(await verifyConsumedSeal(output,hash(raw),replacements,{invocation:false}),3);pass('restored scratch bytes pass');
const result={schemaVersion:1,state:'PURE_TRACE_ACTIVATION_NULL_PIN_AND_SCRATCH_SOURCE_SEAL_CHECKS_PASSED',passed:checks.length,checks,output,
 actualOrSyntheticNewEnginePinsCreated:false,compiledPreflightEvaluated:false,actualNativePreflightOrActivationMainExecuted:false,
 componentizerGuestNativeHostOrTimingExecuted:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
