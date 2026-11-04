// Source routing/data tests with an ECHO kernel. No codec/native/guest execution.
import assert from 'node:assert/strict';
import {Buffer} from 'node:buffer';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createZlibModule} from './source/builtins/node-compat/zlib/facade.mjs';
import {createZlibData} from './source/builtins/node-compat/zlib/constant-data.generated.mjs';
import {validateZlibSourceAdmission} from './source/tests/node-compat/zlib-admission.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),contract=JSON.parse(await readFile(join(here,'contract.json'))),checks=[];
const pass=name=>checks.push(name),calls=[];
// Intentionally fictitious source-test data proves no Node/header number is
// substituted. This is not an observed backend or artifact declaration.
const backend={headerVersion:'SOURCE-MODEL',runtimeVersion:'SOURCE-MODEL',vernum:0x2222};
const kernel={backendInfo:()=>backend,run(input,format,encode,limit){calls.push({format,encode,limit});return Uint8Array.from(input);}};
const module=createZlibModule(kernel,Buffer),exports=contract.deferredCallables;
assert.equal(Object.keys(module).length,40);assert(!('then'in module));pass('finite40 namespace with safe assimilation');
const manifest=JSON.parse(await readFile(join(here,'source/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json')));
assert.deepEqual(Object.keys(module).sort(),manifest.modules['node:zlib'].exports.slice().sort());assert.deepEqual(manifest.modules['node:zlib'].aliases,['zlib']);pass('pinned named inventory and finite alias declaration');
for(const name of exports){assert.throws(()=>module[name](),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.throws(()=>new module[name](),{code:'ERR_SM_NODE_UNSUPPORTED'});pass('explicit deferred call/new '+name);}
for(const [i,name]of contract.syncOperations.entries()){
 assert.throws(()=>new module[name](),{code:'ERR_SM_NODE_UNSUPPORTED'});pass('sync construct refusal '+name);
 const output=module[name](new Uint8Array([1,2,3]));assert(Buffer.isBuffer(output));assert.deepEqual([...output],[1,2,3]);assert.equal(output.buffer instanceof ArrayBuffer,true);pass('ECHO routing only '+name);
}
assert.deepEqual(calls.map(row=>[row.format,row.encode]),[[0,true],[0,false],[1,true],[1,false],[2,true],[2,false]]);pass('six format/direction mappings');
assert.equal(module.constants.ZLIB_VERNUM,0x2222);assert.equal(module.default.ZLIB_VERNUM,0x2222);pass('native-input constant overlay and legacy identity; synthetic sentinel only');
assert.equal(typeof module.constants.Z_MAX_CHUNK,'number');assert.equal(module.constants.Z_MAX_CHUNK,Infinity);assert.equal(module.default.Z_MAX_CHUNK,Infinity);pass('numeric Infinity retained in both data views');
assert.equal(Object.getPrototypeOf(module.constants),null);assert.equal(Object.getPrototypeOf(module.codes),null);assert(Object.isFrozen(module.default)&&Object.isFrozen(module.constants)&&Object.isFrozen(module.codes));pass('declared immutable data/default deviation');
assert.equal(Object.getOwnPropertyDescriptor(module.default,'ZLIB_VERNUM').enumerable,false);pass('legacy version nonenumerable');
for(const name of Object.keys(module))if(name!=='default')assert.equal(module[name],module.default[name]);pass('named/default identities');
for(const value of [null,{}, {...backend,vernum:undefined},{...backend,vernum:NaN},{...backend,vernum:0},{...backend,vernum:1.5},{...backend,runtimeVersion:'different'}]){
 assert.throws(()=>createZlibData(value),{code:'ERR_SM_ZLIB_BACKEND_MISMATCH'});pass('invalid private backend data refused '+checks.length);
}
assert.throws(()=>module.gzipSync('string'),{code:'ERR_SM_NODE_UNSUPPORTED'});pass('byte-only input contract retained');
assert.throws(()=>module.gzipSync(new Uint8Array(),{level:1}),{code:'ERR_SM_NODE_UNSUPPORTED'});pass('unknown options refused');
assert.throws(()=>module.gzipSync(new Uint8Array(),{maxOutputLength:0}),{code:'ERR_OUT_OF_RANGE'});pass('bounded output option');
assert.equal(validateZlibSourceAdmission({}),null);pass('old unhinted metadata guard remains neutral');
for(const metadata of [{zlibEnabled:true},{zlibEnabled:false},{zlibPolicy:{}},{observedCMakeOptions:{NODE_COMPAT_ZLIB:'OFF'}},{sourceManifest:[{path:'builtins/node-compat/zlib/kernel.cpp'}]}]){
 assert.throws(()=>validateZlibSourceAdmission(metadata),{code:'ERR_SM_NODE_ZLIB_ACTIVATION_PENDING'});pass('future ON/OFF source lineage remains blocked '+checks.length);
}
const baseline=JSON.parse(await readFile(join(here,'backend-profile.proposal.json')));assert.equal(baseline.actualGuest.ZLIB_VERNUM,null);assert.equal(baseline.actualGuest.verified,false);pass('actual guest version authority remains NULL');
const result={schemaVersion:1,state:'ZLIB_SOURCE_ECHO_ROUTING_AND_DATA_ONLY_PASSED',passed:checks.length,checks,sourceModelVernum:'0x2222-fictitious-not-guest',kernelIsEcho:true,compressionTested:false,codecGuestOrHostTargetExecuted:false};
await writeFile(join(here,'evidence/source-model-results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,passed:checks.length}));
