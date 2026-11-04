// Host-only source/seal/negative-entry checks; no packager or guest executes.
import {selectActualPin} from '../production-regression-candidate-v5/admission.mjs';
import assert from 'node:assert/strict';
import {selectDependencyIndex} from '../production-regression-candidate-v5/dependency-bindings.mjs';
import {createHash} from 'node:crypto';
import {readFile,writeFile,lstat,mkdtemp,rm} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {verifyInputClosure,recheckInputSeal} from '../production-regression-candidate-v5/preflight.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
const hash=value=>createHash('sha256').update(value).digest('hex');
assert(process.env.NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT,'Set a fresh host JSON output path');
const output=resolve(process.env.NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT);
try{await lstat(output);assert.fail('Output already exists');}catch(error){if(error.code!=='ENOENT')throw error;}
const results=[];
function test(name,run){run();results.push({name,passed:true});}
async function asyncTest(name,run){await run();results.push({name,passed:true});}
const ancestry=JSON.parse(await readFile(join(here,'ancestry.json')));
for(const row of ancestry.inputs)assert.equal(hash(await readFile(join(repo,row.path))),row.sha256,row.path);
const transformations=JSON.parse(await readFile(join(here,'runner-transformations.json')));
assert.equal(transformations.runners.length,5);
for(const row of transformations.runners){
 const staged=await readFile(join(here,row.generated),'utf8'),generated=staged.replaceAll('production-regression-candidate-v5','production-regression-candidate-v4'),original=await readFile(join(repo,row.original),'utf8');
 let restored=generated;
 for(const change of [...row.changes].reverse()){assert.equal(restored.split(change.after).length-1,change.count);restored=restored.split(change.after).join(change.before);}
 test('declared edits restore original bytes '+row.name,()=>{assert.equal(hash(restored),row.originalSha256);assert.equal(hash(original),row.originalSha256);assert.equal(hash(generated),row.generatedSha256);});
 const semantic=text=>text.slice(text.indexOf(row.semanticBlockStart),text.indexOf(row.semanticBlockEnd));
 test('whole semantic/control section unchanged '+row.name,()=>{assert.equal(semantic(generated),semantic(original));assert.equal(hash(semantic(generated)),row.semanticBlockSha256);});
 test('actual inner v11 guard replaced '+row.name,()=>{
  assert(!generated.includes('verifyProductionV11'));
  assert(staged.includes("from '../../production-regression-candidate-v5/preflight.mjs'"));
  assert(generated.includes('await verifyProductionTicks({gcStress:false})'));
  if(['sync','runtime','callbacks'].includes(row.name))assert(generated.includes("'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'"));
  assert(!/writeFile\(join\(here,/.test(generated),'No old latest-result mirror writes');
 });
}
const prior=JSON.parse(await readFile(join(repo,'tests/node-compat/foundation-add-abort/runtime-async-observation-results.json')));
test('both original runtime observation sources retained as exact input bytes',()=>{assert.equal(prior.results.length,2);for(const row of prior.results)assert.equal(hash(row.source),row.sourceSha256);});
await asyncTest('actual LIVE adapter source bytes remain pinned; runtime closure pending',async()=>assert.equal(hash(await readFile(join(repo,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'))),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'));
// Reuse the production check on owned scratch data, never packet/engine files.
const scratch=await mkdtemp(join(tmpdir(),'starling-followon-seal-negative-'));
try{
 const manifestPath=join(scratch,'inputs.json'),pinsPath=join(scratch,'pins.json'),dataPath=join(scratch,'data.txt');
 const initial=Buffer.from('initial'),pins=Buffer.from('{"scratchOnly":true}');
 await writeFile(dataPath,initial);await writeFile(pinsPath,pins);
 await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'data.txt',sha256:hash(initial),bytes:initial.length}]}));
 const closure=await verifyInputClosure({manifestPath}),expectedManifestSha256=closure.sha256,expectedPinsSha256=hash(pins);
 const args={manifestPath,pinsPath,expectedManifestSha256,expectedPinsSha256};
 await writeFile(dataPath,'replacement');
 await asyncTest('listed-file tamper rejects in inherited shared checker',async()=>assert.rejects(recheckInputSeal(args),/data.txt/));
 const replacement=Buffer.from('replacement');
 await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'data.txt',sha256:hash(replacement),bytes:replacement.length}]}));
 await asyncTest('manifest plus matching file replacement still rejects',async()=>assert.rejects(recheckInputSeal(args),/Runtime input manifest changed/));
 await writeFile(manifestPath,'NOT JSON');
 await asyncTest('manifest digest rejects before parsing new content',async()=>assert.rejects(recheckInputSeal(args),/Runtime input manifest changed/));
 await writeFile(pinsPath,'replacement pins');
 await asyncTest('pin digest rejects before changed manifest is parsed',async()=>assert.rejects(recheckInputSeal(args),/Production pins changed/));
}finally{await rm(scratch,{recursive:true});}

// OWN scratch selector inputs; these tests never inspect or rewrite current pin files.
for(const document of [null,[],{},
 {schemaVersion:1,state:'UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1',variants:{'normal-off':{state:'unreviewed-production-freeze-pin-candidate'}}},
 {schemaVersion:1,state:'UNCONFIGURED_ACTUAL_PRODUCTION_FREEZES_REQUIRED',variants:{'normal-off':null}}])
 test('scratch malformed/null/unreviewed production selector '+JSON.stringify(document),()=>assert.throws(()=>selectActualPin(document,{gcStress:false})));
for(const document of [null,{},
 {schemaVersion:1,state:'UNCONFIGURED_SEALED_PARENT_INDICES_REQUIRED',commonIndexSha256:null},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:null},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:'not-a-digest'},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:'0'.repeat(64)}])
 test('scratch unresolved/malformed dependency binding '+JSON.stringify(document),()=>assert.throws(()=>selectDependencyIndex(document,'commonIndexSha256')));
const report={schemaVersion:1,state:'HOST_ONLY_ACTIVATION_OFF_SOURCE_CHECKS_PASSED',tests:results.length,passed:results.length,results,
 commonInputState:'v5 staged; no reviewed tuple or index inferred',innerGuardsReplaced:5,wholeSemanticSectionsByteIdentical:5,
 negativeChildren:0,scratchSealChecks:4,liveAdapterReadOnlyChecks:1,finalInputManifestChecked:false,oldAncestryInputsUnchanged:ancestry.inputs.length,
 actualFixedArtifactSuccessExecuted:false,nativeBuild:false,componentizerToolchainOrWasmtimeRun:false,componentOrGuestExecuted:false,oldFixturesOrLatestReportsModified:false};
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
