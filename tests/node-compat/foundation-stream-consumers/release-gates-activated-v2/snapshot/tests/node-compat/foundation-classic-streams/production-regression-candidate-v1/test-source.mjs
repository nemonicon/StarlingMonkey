// Pure source/path/contract checks only. Never imports a runner or toolchain.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectClassicPin,variants} from './runtime-contract.mjs';
import {verifyProductionTicks,verifyInputClosure} from './common/preflight.mjs';
import {releaseJobs} from './release/job-plan.mjs';
import {variantOptions,scalarImports,HTTP_IMPORTS,validateHTTPInterfaces} from './capability/capabilities.mjs';
import {validatePinBoundary} from './capability/admission.mjs';
import {selectHTTPPin} from './capability/http-contract.mjs';
import {requireComputedRows,LIVE_COMPUTED_INPUTS} from './capability/computed-inputs.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..'),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const checks=[];function pass(name){checks.push({name,passed:true});}function rejects(name,action){assert.throws(action);pass(name);}
const pins=JSON.parse(await readFile(join(here,'runtime-pins.json')));
for(const variant of variants)rejects('null actual pin '+variant,()=>selectClassicPin(pins,{variant,recipeSha256:'not-used-before-unconfigured'}));
for(const options of[{gcStress:false},{gcStress:true},{entropyPolicy:'runtime-only'}]){await assert.rejects(verifyProductionTicks(options),/unconfigured/);pass('actual fixed native null gate '+JSON.stringify(options));}
await assert.rejects(verifyProductionTicks({gcStress:true,entropyPolicy:'runtime-only'}));pass('RuntimeGC unavailable');
rejects('unknown capability variant',()=>variantOptions('gc-runtime'));
assert.deepEqual(scalarImports('off'),[]);assert.deepEqual(scalarImports('runtime-only'),['wasi:random/random@0.2.10']);pass('finite scalar interface lists');
rejects('unsupported scalar mode',()=>scalarImports('all'));
const synthetic={entropyPolicy:'runtime-only',emittedImports:HTTP_IMPORTS,emittedExports:['wasi:http/incoming-handler@0.2.10'],selectedInterfaces:HTTP_IMPORTS,allowedImports:HTTP_IMPORTS,clockDependency:{typeOnly:true,callableImports:[],coreClockImports:[]}};
validateHTTPInterfaces(synthetic);pass('synthetic HTTP type-only-clock contract shape; not measured imports');
for(const change of[model=>model.emittedImports=[],model=>model.clockDependency.callableImports=['now'],model=>model.clockDependency.coreClockImports=['clock_time_get']]){const changed=structuredClone(synthetic);change(changed);rejects('malformed HTTP capability shape',()=>validateHTTPInterfaces(changed));}
for(const root of['relative','/tmp/a/../b','/tmp/a\0b'])rejects('invalid HTTP pin boundary '+JSON.stringify(root),()=>validatePinBoundary(root));
const httpPins=JSON.parse(await readFile(join(here,'capability/http-component-pins.json')));assert.equal(httpPins.component,null);rejects('unconfigured HTTP pin',()=>selectHTTPPin(httpPins,{}));
const jobs=releaseJobs(join(here,'release'),'/tmp/NEVER-EXECUTED-source-test');assert.deepEqual(jobs.map(row=>row.name),['core','allocator','stream-web','optional','strict-sync','strict-runtime','strict-late','strict-callbacks']);pass('complete eight-stage plan, no jobs started');
assert(jobs.every(row=>row.runner.startsWith(here+'/')));pass('every stage uses new guarded source entry');
const source=JSON.parse(await readFile(join(here,'derivations.json')));assert.equal(source.records.length,64);
for(const row of source.records){const original=await readFile(join(repo,row.sourcePath),'utf8');let after=await readFile(join(here,row.destinationPath),'utf8');assert.equal(hash(original),row.beforeSha256);assert.equal(hash(after),row.afterSha256);
 for(const edit of [...row.edits].reverse()){
  if(edit.new===''){const anchor='export {requireFreshOutput,hash};';assert.equal(after.split(anchor).length,2);after=after.replace(anchor,edit.old+anchor);}
  else{const count=edit.count??1;assert(after.split(edit.new).length-1>=count);for(let i=0;i<count;i++)after=after.replace(edit.new,edit.old);}
 }assert.equal(hash(after),row.beforeSha256,row.destinationPath);}
pass('all64 exact text reverse proofs');
const manifest=JSON.parse(await readFile(join(here,'capability/input-freeze.json'))),computed=requireComputedRows(manifest.inputs,{manifestPath:join(here,'capability/input-freeze.json'),repository:repo});assert.equal(computed.length,8);assert.deepEqual(computed.map(row=>row.name),LIVE_COMPUTED_INPUTS);pass('all8 actual LIVE computed HTTP paths sealed');
const observation=await readFile(join(here,'capability/focused/run-callback-return.mjs'),'utf8');assert(observation.includes('nodeCompatibilityPassed:false'));pass('known getter false parity remains explicit');
const audit=await readFile(join(here,'capability/audit-http.mjs'),'utf8');assert(audit.includes('instanceReuseClaim:false'));pass('HTTP no-reuse claim preserved');
const scratch=resolve(process.env.NODE_COMPAT_CLASSIC_REPLAY_TEST_SCRATCH??'/tmp/starling-node-compat/classic-replay-source-test-v1');await mkdir(scratch);
const path=join(scratch,'manifest.json'),bytes=Buffer.from('{"schemaVersion":1,"inputs":[]}\n');await writeFile(path,bytes,{flag:'wx'});
await verifyInputClosure({manifestPath:path,expectedSha256:hash(bytes)});await writeFile(path,'{"schemaVersion":1,"inputs":[{"path":"MUST_NOT_FOLLOW"}]}');await assert.rejects(verifyInputClosure({manifestPath:path,expectedSha256:hash(bytes)}),/seal changed/);pass('manifest hash checked before following changed rows');
const result={schemaVersion:1,state:'CLASSIC342_REPLAY_PURE_SOURCE_CHECKS_PASSED',checks:checks.length,passed:checks.length,failures:0,sourceDerivations:64,syntheticHTTPShapeOnly:true,allActualPinsNull:true,runnerImported:false,nativeBuild:false,componentizer:false,guest:false,targetHost:false,observations:checks};
const output=resolve(process.env.NODE_COMPAT_CLASSIC_REPLAY_SOURCE_TEST_OUTPUT??join(here,'host-test-results.json'));await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({checks:checks.length,output}));
