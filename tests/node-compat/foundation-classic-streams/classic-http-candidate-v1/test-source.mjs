// Pure validator/composer/data tests. Old host bodies are clearly marked test
// data; no new guest/host result is adopted or emitted by this script.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createClassicHTTPPlugin,BASELINE_ENTRY,ORIGINAL_HTTP,COMPOSER_ID,COMPOSER_SOURCE} from './capability/composer-plugin.mjs';
import {projectCombinedHTTPBody,checkCombinedHTTPReport,checkCombinedHTTPSamples} from './capability/validate-combined.mjs';
import {selectCombinedHTTPPin} from './capability/http-contract.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=data=>createHash('sha256').update(data).digest('hex');
const checks=[];const pass=name=>checks.push({name,passed:true});
const reject=(name,fn)=>{assert.throws(fn,undefined,name);pass(name);};
const plugin=createClassicHTTPPlugin();assert.equal(plugin.resolveId(relative(dirname(BASELINE_ENTRY),ORIGINAL_HTTP),BASELINE_ENTRY),COMPOSER_ID);
assert.equal(plugin.resolveId(relative(dirname(BASELINE_ENTRY),ORIGINAL_HTTP),BASELINE_ENTRY+'.other'),undefined);
assert.equal(plugin.resolveId('node:buffer',BASELINE_ENTRY),undefined);assert.equal(plugin.load(COMPOSER_ID),COMPOSER_SOURCE);plugin.buildEnd();pass('composer redirects only sealed baseline handler import exactly once');
reject('composer missing redirect fails',()=>createClassicHTTPPlugin().buildEnd());
const double=createClassicHTTPPlugin();double.resolveId(ORIGINAL_HTTP,BASELINE_ENTRY);double.resolveId(ORIGINAL_HTTP,BASELINE_ENTRY);reject('composer duplicate redirect fails',()=>double.buildEnd());
assert(COMPOSER_SOURCE.includes('return original(async()=>'));assert(COMPOSER_SOURCE.includes('if(baseline.failure)'));assert(COMPOSER_SOURCE.indexOf('if(baseline.failure)')<COMPOSER_SOURCE.indexOf('await runClassic19()'));pass('actual original resource handler and baseline-failure-before-classic path retained in source');
const oldRoot='/tmp/starling-node-compat/production-scheduler-runtime-v1/http';
const fixturePath=join(oldRoot,'http-joint/wasmtime-v1/wasmtime-results.json'),auditPath=join(oldRoot,'http-joint/component-audit.json');
const fixtureBytes=await readFile(fixturePath),auditBytes=await readFile(auditPath);
assert.equal(hash(fixtureBytes),'8856c0389de6bea514245cc8f5600356a341723c78b68cde1bc1b877b9648169');
assert.equal(hash(auditBytes),'e2d8a4732388c4e930877cb7666aa4ff65f19f6ae10dafecc3ffe7d5e3ca01fe');
const old=JSON.parse(fixtureBytes),audit={...JSON.parse(auditBytes),classicCombinedHTTP:{schema:1,ordinaryGroups:19}};
const oracleBytes=await readFile(new URL('../implementation-candidate-v1/node-final-acceptance-results.json',import.meta.url));
assert.equal(hash(oracleBytes),'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');
const expected=JSON.parse(oracleBytes).expected;
// In-memory composite models test validation. They are never presented as
// observed responses from the new component or serialized into a host report.
const models=old.responses.map(row=>({...structuredClone(row),body:{...structuredClone(row.body),native:{combinedSchema:1,
  baseline:structuredClone(row.body.native),classic:{schema:1,calls:row.body.componentInstanceRequestCount,ordinary:structuredClone(expected),identity:{esmAliases:true,rootDefault:true,promises:true,globalBuffer:true}}}}}));
const before=JSON.stringify(models);for(const row of models){const projected=checkCombinedHTTPReport(row.body,audit);assert.equal(projected.native,row.body.native.baseline);assert.equal(projected.requestTag,row.body.requestTag);}
checkCombinedHTTPSamples(models,audit);assert.equal(JSON.stringify(models),before);pass('data-only projection feeds all unchanged baseline validators and leaves raw composite models unchanged');
for(const[name,mutate]of [
 ['outer failure',value=>value.failure={}],['combined failure',value=>value.native.failure={}],
 ['baseline failure',value=>value.native.baseline.failure={}],['classic failure',value=>value.native.classic.failure={}],
 ['classic schema',value=>value.native.classic.schema=2],['ordinary mismatch',value=>value.native.classic.ordinary[0].result.extra=true],
 ['identity mismatch',value=>value.native.classic.identity.globalBuffer=false],['counter mismatch',value=>value.native.classic.calls++],
 ['baseline core mismatch',value=>value.native.baseline.strings=0],['baseline protected count mismatch',value=>value.native.baseline.foundations.protectedAbort.calls++],
]){const value=structuredClone(models[0].body);mutate(value);reject(name,()=>checkCombinedHTTPReport(value,audit));}
const repeat=structuredClone(models);for(const row of repeat)row.body.native.baseline.entropyIntegration.secure.bytes='0'.repeat(64);reject('entropy sample replay still rejected after projection',()=>checkCombinedHTTPSamples(repeat,audit));
const engine={engineSha256:'a'.repeat(64),receiptSha256:'b'.repeat(64)},sourceSha='c'.repeat(64),root='/tmp/NO_COMPONENT_OR_HOST_CREATED';
const pin={state:'reviewed-classic-combined-http-component',root,engineSha256:engine.engineSha256,engineReceiptSha256:engine.receiptSha256,sourceInputSha256:sourceSha,
  componentSha256:'1'.repeat(64),componentBytes:1,auditSha256:'2'.repeat(64),applicationBundleSha256:'3'.repeat(64),inputsSha256:'4'.repeat(64),
  componentPath:join(root,'http-joint/native-profile-http.component.wasm'),auditPath:join(root,'http-joint/component-audit.json'),bundlePath:join(root,'http-joint/http.bundle.mjs'),inputsPath:join(root,'http-inputs.json'),sourceEntryPath:join(here,'capability/http-component.mjs')};
const document={schemaVersion:1,state:'ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1',component:pin};
assert.deepEqual(selectCombinedHTTPPin(document,engine,sourceSha),pin);pass('synthetic phase shape only accepts original entry/path/native/source tuple; no files followed');
for(const[name,mutate]of [['unreviewed',value=>value.state='OBSERVED'],['null pin',value=>value.component=null],
 ['wrong engine',value=>value.component.engineSha256='d'.repeat(64)],['wrong source',value=>value.component.sourceInputSha256='d'.repeat(64)],
 ['moved entry',value=>value.component.sourceEntryPath='/tmp/relabeled.mjs'],['escaped component',value=>value.component.componentPath='/tmp/outside.wasm'],
 ['empty bytes',value=>value.component.componentBytes=0],['zero digest',value=>value.component.auditSha256='0'.repeat(64)]]){const changed=structuredClone(document);mutate(changed);reject('phase '+name,()=>selectCombinedHTTPPin(changed,engine,sourceSha));}
assert.equal(JSON.parse(await readFile(join(here,'capability/component-pins.json'))).component,null);pass('checked-in phase pin remains null');
const output=resolve(process.env.NODE_COMPAT_CLASSIC_HTTP_SOURCE_TEST_OUTPUT);assert(output&&output!==resolve('undefined'));
assert(output.startsWith('/tmp/starling-node-compat/'));try{await lstat(output);assert.fail('Choose fresh source test output');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(dirname(output),{recursive:true});
const result={schemaVersion:1,state:'COMBINED_HTTP_PURE_SOURCE_VALIDATOR_CHECKS_PASSED',checks:checks.length,passed:checks.length,observations:checks,
  syntheticCompositeModelsOnly:true,syntheticPhaseShapeOnly:true,oldBaselineFixture:{path:fixturePath,sha256:hash(fixtureBytes),scope:'Immutable validator test data, never a new runtime pass'},
  actualComponentOrGuestExecuted:false,hostStarted:false,ordinary19Executed:false,sourceOnly:true};
await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,checks:checks.length,output}));
