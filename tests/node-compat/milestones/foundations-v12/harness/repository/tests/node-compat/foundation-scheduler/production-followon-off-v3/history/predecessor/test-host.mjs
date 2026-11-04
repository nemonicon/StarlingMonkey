// Host-only source/seal/negative-entry checks; no packager or guest executes.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,lstat,mkdtemp,rm} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {verifyInputClosure,recheckInputSeal} from '../production-regression-candidate-v4/preflight.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
const hash=value=>createHash('sha256').update(value).digest('hex');
assert(process.env.NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT,'Set a fresh host JSON output path');
const output=resolve(process.env.NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT);
try{await lstat(output);assert.fail('Output already exists');}catch(error){if(error.code!=='ENOENT')throw error;}
const results=[];
function test(name,run){run();results.push({name,passed:true});}
async function asyncTest(name,run){await run();results.push({name,passed:true});}
const common=join(here,'../production-regression-candidate-v4'),commonBytes=await readFile(join(common,'index.json'));
await asyncTest('common v4 source index and runtime closure unchanged',async()=>{
 assert.equal(hash(commonBytes),'d0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9');
 const index=JSON.parse(commonBytes);assert.equal(index.files.length,23);
 for(const row of index.files)assert.equal(hash(await readFile(join(common,row.path))),row.sha256,row.path);
 assert.equal((await verifyInputClosure({manifestPath:join(common,'input-freeze.json')})).files,666);
});
const ancestry=JSON.parse(await readFile(join(here,'ancestry.json')));
for(const row of ancestry.inputs)assert.equal(hash(await readFile(join(repo,row.path))),row.sha256,row.path);
const transformations=JSON.parse(await readFile(join(here,'runner-transformations.json')));
assert.equal(transformations.runners.length,5);
for(const row of transformations.runners){
 const generated=await readFile(join(here,row.generated),'utf8'),original=await readFile(join(repo,row.original),'utf8');
 let restored=generated;
 for(const change of [...row.changes].reverse()){assert.equal(restored.split(change.after).length-1,change.count);restored=restored.split(change.after).join(change.before);}
 test('declared edits restore original bytes '+row.name,()=>{assert.equal(hash(restored),row.originalSha256);assert.equal(hash(original),row.originalSha256);assert.equal(hash(generated),row.generatedSha256);});
 const semantic=text=>text.slice(text.indexOf(row.semanticBlockStart),text.indexOf(row.semanticBlockEnd));
 test('whole semantic/control section unchanged '+row.name,()=>{assert.equal(semantic(generated),semantic(original));assert.equal(hash(semantic(generated)),row.semanticBlockSha256);});
 test('actual inner v11 guard replaced '+row.name,()=>{
  assert(!generated.includes('verifyProductionV11'));
  assert(generated.includes("from '../../production-regression-candidate-v4/preflight.mjs'"));
  assert(generated.includes('await verifyProductionTicks({gcStress:false})'));
  if(['sync','runtime','callbacks'].includes(row.name))assert(generated.includes("'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'"));
  assert(!/writeFile\(join\(here,/.test(generated),'No old latest-result mirror writes');
 });
}
const temp=await mkdtemp(join(tmpdir(),'starling-followon-entry-negative-'));
try{
 for(const name of ['sync','runtime','late','callbacks','stream-web']){
  const variable=name==='stream-web'?'NODE_COMPAT_STREAM_WEB_OUTPUT':'NODE_COMPAT_STRICT_EVENT_OUTPUT',destination=join(temp,name);
  const env={...process.env,NODE_COMPAT_ENGINE:'/NO_ENGINE_MUST_BE_READ',NODE_COMPAT_ENGINE_SOURCE_ROOT:'/NO_SOURCE_MUST_BE_READ',NODE_COMPAT_WASMTIME:'/NO_HOST_MUST_BE_RUN',[variable]:destination};delete env.NODE_OPTIONS;
  const child=spawnSync(process.execPath,[join(here,'run-'+name+'.mjs')],{env,encoding:'utf8',timeout:10000,maxBuffer:1024*1024});
  test('entry null pins stop before loaders/output '+name,()=>{assert.notEqual(child.status,0);assert.match(child.stderr,/Actual production pins are unconfigured/);assert(!/ENOENT|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND/.test(child.stderr));});
  try{await lstat(destination);assert.fail('Negative entry created output');}catch(error){assert.equal(error.code,'ENOENT');}
 }
}finally{await rm(temp,{recursive:true});}
const prior=JSON.parse(await readFile(join(repo,'tests/node-compat/foundation-add-abort/runtime-async-observation-results.json')));
test('both original runtime observation sources retained as exact input bytes',()=>{assert.equal(prior.results.length,2);for(const row of prior.results)assert.equal(hash(row.source),row.sourceSha256);});
await asyncTest('new local runtime closure reads exact sealed bytes',async()=>{assert.equal((await verifyInputClosure({manifestPath:join(here,'input-freeze.json')})).files,733);});
const activeRows=JSON.parse(await readFile(join(here,'input-freeze.json'))).inputs;
test('LIVE adapter physical path is in the descendant seal',()=>{const matches=activeRows.filter(row=>resolve(here,row.path)===join(repo,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'));assert.equal(matches.length,1);assert.equal(matches[0].sha256,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');});
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
const report={schemaVersion:1,state:'HOST_ONLY_NORMAL_OFF_FOLLOWON_PREPARATION_PASSED',tests:results.length,passed:results.length,results,
 commonInputState:'v3 null actual production pins preserved',innerGuardsReplaced:5,wholeSemanticSectionsByteIdentical:5,
 negativeChildren:5,scratchSealChecks:4,liveAdapterInputs:1,localInputs:733,commonRuntimeInputs:666,oldAncestryInputsUnchanged:ancestry.inputs.length,
 actualFixedArtifactSuccessExecuted:false,nativeBuild:false,componentizerToolchainOrWasmtimeRun:false,componentOrGuestExecuted:false,oldFixturesOrLatestReportsModified:false};
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
