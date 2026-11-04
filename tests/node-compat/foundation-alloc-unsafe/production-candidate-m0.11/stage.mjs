// UNAPPLIED rebase on live m0.10 source. Copies/patches only; no engine build.
import assert from 'node:assert/strict';
import {readFile,writeFile,readdir,mkdir,copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..'),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const previous=join(here,'../direct-candidate-m0.11'),privateReceipt=JSON.parse(await readFile(join(previous,'source-receipt.json')));
const adoption=JSON.parse(await readFile(join(repo,'tests/node-compat/foundation-add-abort/production-adoption-m0.10/source-receipt.json')));
const nativeDirs=['builtins','runtime','include','cmake','host-apis/wasi-0.2.0','host-apis/wasi-0.2.3','host-apis/wasi-0.2.10','crates','deps/patches'];
const ext=new Set(['.cpp','.h','.c','.cmake','.mjs','.rs','.toml','.lock','.o','.wasm','.json','.wit','.patch']);
async function walk(root,path){let result=[];for(const entry of await readdir(join(root,path),{withFileTypes:true})){const file=join(path,entry.name);if(entry.isDirectory())result.push(...await walk(root,file));else result.push(file);}return result.sort();}
const native=[];for(const dir of nativeDirs)for(const path of await walk(repo,dir))if(ext.has(path.slice(path.lastIndexOf('.'))))native.push({path,sha256:hash(await readFile(join(repo,path)))});
for(const path of['CMakeLists.txt','rust-toolchain.toml'])native.push({path,sha256:hash(await readFile(join(repo,path)))});
assert.equal(native.length,304,'Expected exact current m0.10 native-source ancestry');
for(const file of adoption.changes)assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,'Live m0.10 adoption differs: '+file.path);
const protectedPaths=['builtins/web/event/event-target.h','builtins/web/event/event-target.cpp','builtins/node-compat/register.cpp',
 'builtins/node-compat/events.mjs','builtins/node-compat/events-add-abort-listener.mjs','builtins/node-compat/events-factories.generated.h',
 'builtins/node-compat/generate-events-factory.mjs','builtins/node-compat/generate-factories.mjs','builtins/node-compat/export-manifest.events.node-v22.14.0.json','cmake/builtins.cmake'];
const extras=['tests/node-compat/core-expectations.mjs','tests/node-compat/module-selection.mjs','tests/node-compat/legacy-stream-web-receipts.json',
 'tests/node-compat/legacy-stream-web-test-receipt.json','tests/node-compat/profile-bundler.mjs','tests/node-compat/toolchain.mjs','tests/node-compat/oracle.mjs',
 'tests/node-compat/componentizer.mjs','tests/node-compat/capability-policy.mjs','tests/node-compat/wasi-0.2.10-interfaces.json','tests/node-compat/profile.wit',
 'tests/node-compat/run.mjs','tests/node-compat/fixtures/component.mjs','tests/node-compat/fixtures/static-require.cjs','tests/node-compat/fixtures/raw-aliases.mjs',
 'tests/node-compat/fixtures/top-level-failure.mjs','tests/node-compat/fixtures/top-level-constructor-failure.mjs','tests/node-compat/fixtures/top-level-await-failure.mjs','tests/node-compat/fixtures/unknown-export.mjs',
 'tests/node-compat/optimization/intrinsics-checks.mjs','tests/node-compat/optimized-profile-tests.mjs','tests/node-compat/build-engine.sh',
 'tests/node-compat/wasmcloud/build-http.mjs','tests/node-compat/wasmcloud/test-wasmtime-http.mjs','tests/node-compat/wasmcloud/run-host.mjs',
 'tests/node-compat/wasmcloud/http.mjs','tests/node-compat/foundations/http-v9.mjs','tests/node-compat/foundations/assert-http-report.mjs',
 'docs/node-compat/templates/reference-kernel.mjs'];
const files=new Map(native.map(file=>[file.path,file.sha256]));for(const path of extras)files.set(path,hash(await readFile(join(repo,path))));
await writeFile(join(here,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),nativeInputs:304,baseCore:'sm-node-22.14.0-m0.8',events:'sm-node-22.14.0-m0.10'})+'\n',{flag:'wx'});
for(const[path,digest]of files)for(const variant of['base','source']){const dest=join(here,variant,path);await mkdir(dirname(dest),{recursive:true});const bytes=await readFile(join(repo,path));assert.equal(hash(bytes),digest);await writeFile(dest,bytes);}
const coreFiles=['buffer-facade.mjs','unsupported.mjs','export-manifest.node-v22.14.0.json','factories.generated.h'];
for(const name of coreFiles){const path='builtins/node-compat/'+name,entry=privateReceipt.files.find(file=>file.path===path);assert.equal(files.get(path),entry.ancestry);await copyFile(join(previous,'candidate',path),join(here,'source',path));}
const source=join(here,'source'),generator=spawnSync(process.execPath,[join(source,'builtins/node-compat/generate-factories.mjs')],{encoding:'utf8'});
assert.equal(generator.status,0,generator.stderr||generator.stdout);
for(const name of coreFiles){const path='builtins/node-compat/'+name;assert.equal(hash(await readFile(join(source,path))),privateReceipt.files.find(file=>file.path===path).candidate,'Current generator must reproduce reviewed core file: '+path);}
const check=spawnSync(process.execPath,[join(source,'builtins/node-compat/generate-factories.mjs'),'--check'],{encoding:'utf8'});assert.equal(check.status,0,check.stderr||check.stdout);
const pins=Object.fromEntries([...coreFiles,'buffer.cpp'].map(name=>{const path='builtins/node-compat/'+name;return[path,privateReceipt.files.find(file=>file.path===path).candidate];}));
async function replace(path,before,after){const file=join(source,path),text=await readFile(file,'utf8');assert.equal(text.split(before).length,2,path+' exact source form');await writeFile(file,text.replace(before,after));}
const expectationPath='tests/node-compat/core-expectations.mjs';
await replace(expectationPath,'\n};\nconst hash',',\n  "sm-node-22.14.0-m0.11": '+JSON.stringify({allocUnsafePolicy:'zeroed-no-pool-direct-u8-v1',unsupportedStatic:['copyBytesFrom','of','allocUnsafeSlow','compare','concat'],hashes:pins},null,2).replace(/\n/g,'\n  ')+'\n};\nconst hash');
const hostHelpers=`
// Host-only checks: source-selected core semantics, never a runtime API toggle.
export function unsupportedMessagePattern(value, module, operation) {
  validateCoreExpectations(value);
  const escape = text => [...text].map(character => ${JSON.stringify('\\^$.*+?()[]{}|')}.includes(character) ? ${JSON.stringify('\\')}+character : character).join('');
  return new RegExp(escape(module+'.'+operation+' is unavailable in '+value.coreVersion)+'(?![A-Za-z0-9.-])');
}
export function validateCoreRuntimeReport(report, value) {
  validateCoreExpectations(value);
  assert.equal(report.coreVersion, value.coreVersion);
  assert.equal(report.allocUnsafePolicy, value.allocUnsafePolicy);
  if (value.allocUnsafePolicy === 'zeroed-no-pool-direct-u8-v1')
    assert.deepEqual(report.allocUnsafePrimordialCalls, {integerCalls:0, finiteCalls:0, truncatedLength:3});
  return report;
}
`;
await writeFile(join(source,expectationPath),(await readFile(join(source,expectationPath),'utf8'))+hostHelpers);
await replace('tests/node-compat/fixtures/component.mjs',"if (coreExpectations.allocUnsafePolicy === 'zeroed-no-pool-v1') {","let allocUnsafePrimordialCalls = null;\n  if (['zeroed-no-pool-v1', 'zeroed-no-pool-direct-u8-v1'].includes(coreExpectations.allocUnsafePolicy)) {");
await replace('tests/node-compat/fixtures/component.mjs',"  } else if (coreExpectations.allocUnsafePolicy !== 'deferred') {",`    const savedInteger=Number.isInteger, savedFinite=Number.isFinite; let integerCalls=0, finiteCalls=0, value;
    try { Number.isInteger=()=>{integerCalls++;return true;}; Number.isFinite=()=>{finiteCalls++;return true;}; value=Buffer.allocUnsafe(3.75); }
    finally { Number.isInteger=savedInteger; Number.isFinite=savedFinite; }
    const expectedCalls=coreExpectations.allocUnsafePolicy==='zeroed-no-pool-direct-u8-v1'?0:1;
    equal(integerCalls,expectedCalls,'source-selected integer-hook policy'); equal(finiteCalls,expectedCalls,'source-selected secondary finite-hook policy');
    equal(value.length,3,'captured truncation'); check(Buffer.isBuffer(value),'actual allocator brand');
    allocUnsafePrimordialCalls={integerCalls,finiteCalls,truncatedLength:value.length};
  } else if (coreExpectations.allocUnsafePolicy !== 'deferred') {`);
await replace('tests/node-compat/fixtures/component.mjs','allocUnsafePolicy: coreExpectations.allocUnsafePolicy, calls:','allocUnsafePolicy: coreExpectations.allocUnsafePolicy, allocUnsafePrimordialCalls, calls:');
await replace('tests/node-compat/run.mjs','selectCoreExpectations, coreExpectationsForGuest }','selectCoreExpectations, coreExpectationsForGuest, unsupportedMessagePattern, validateCoreRuntimeReport }');
await replace('tests/node-compat/run.mjs','const first = JSON.parse(await instance.run());','const first = validateCoreRuntimeReport(JSON.parse(await instance.run()), coreExpectations);');
for(const[fixture,operation]of[['top-level-failure.mjs','spawn'],['top-level-constructor-failure.mjs','ChildProcess'],['top-level-await-failure.mjs','exec']])
 await replace('tests/node-compat/run.mjs',`['${fixture}', /node:child_process\\.${operation} is unavailable/]`,`['${fixture}', unsupportedMessagePattern(coreExpectations, 'node:child_process', '${operation}')]`);
for(const path of['tests/node-compat/wasmcloud/test-wasmtime-http.mjs','tests/node-compat/wasmcloud/run-host.mjs']){
 await replace(path,'{ validateCoreExpectations }','{ validateCoreExpectations, validateCoreRuntimeReport }');
 await replace(path,'assert.equal(body.native.coreVersion, coreExpectations.coreVersion);','validateCoreRuntimeReport(body.native, coreExpectations);');
}
const httpPath='tests/node-compat/foundations/http-v11.mjs';
await writeFile(join(source,httpPath),(await readFile(join(source,'tests/node-compat/foundations/http-v9.mjs'),'utf8')).replace(/^\/\/.*\n/,'// Proposed core m0.11; Events m0.10 and stream/web m0.9 retained; new native/hosts pending.\n'));
files.set(httpPath,null);
await replace('tests/node-compat/wasmcloud/build-http.mjs',"const streamWebFoundationsFixture = httpEntry === resolve(here, '../foundations/http-v9.mjs');","const streamWebFoundationsFixture = ['http-v9.mjs', 'http-v11.mjs'].some(name => httpEntry === resolve(here, '../foundations/'+name));");
await replace('tests/node-compat/wasmcloud/build-http.mjs',"['http-v7.mjs', 'http-v8.mjs', 'http-v9.mjs']","['http-v7.mjs', 'http-v8.mjs', 'http-v9.mjs', 'http-v11.mjs']");
const changes=[];for(const[path,before]of files){const after=hash(await readFile(join(source,path)));if(before!==after)changes.push({path,before,after});}
assert.deepEqual(changes.filter(file=>native.some(input=>input.path===file.path)).map(file=>file.path).sort(),coreFiles.map(name=>'builtins/node-compat/'+name).sort());
for(const file of native)if(!coreFiles.some(name=>file.path==='builtins/node-compat/'+name))assert.equal(hash(await readFile(join(source,file.path))),file.sha256,'Protected native input changed: '+file.path);
for(const path of[...protectedPaths,'tests/node-compat/build-engine.sh','tests/node-compat/module-selection.mjs','builtins/node-compat/buffer.cpp'])assert.equal(hash(await readFile(join(source,path))),files.get(path),path);
let patch='';for(const change of changes){const before=change.before?join(here,'base',change.path):'/dev/null';const diff=spawnSync('diff',['-u','-L',change.before?'a/'+change.path:'/dev/null','-L','b/'+change.path,before,join(source,change.path)],{encoding:'utf8'});assert.equal(diff.status,1,diff.stderr);patch+=diff.stdout;}
await writeFile(join(here,'core-m0.11-rebased.patch'),patch);
const patchCheck=spawnSync('git',['apply','--check',join(here,'core-m0.11-rebased.patch')],{cwd:repo,encoding:'utf8'});assert.equal(patchCheck.status,0,patchCheck.stderr);
for(const[path,digest]of files)if(digest!==null)assert.equal(hash(await readFile(join(repo,path))),digest,'Live source mutated during proposal: '+path);
const result={schema:1,state:'unapplied-m011-rebased-on-live-m010-source',atUtc:new Date().toISOString(),nativeAncestryInputs:304,ancestry:native,
  changes,corePins:pins,protected10:protectedPaths.map(path=>({path,sha256:files.get(path)})),unchangedCritical:['tests/node-compat/module-selection.mjs','tests/node-compat/build-engine.sh','builtins/node-compat/buffer.cpp'].map(path=>({path,sha256:files.get(path)})),
  currentAdoptionReceiptSha256:hash(await readFile(join(repo,'tests/node-compat/foundation-add-abort/production-adoption-m0.10/source-receipt.json'))),
  generator:{exitCode:generator.status,stdout:generator.stdout,checkExitCode:check.status,checkStdout:check.stdout},patchSha256:hash(patch),patchApplyCheck:patchCheck.status,
  sourcePolicy:'zeroed-no-pool-direct-u8-v1',publicApiExpanded:false,hostImportsAdded:[],applied:false,nativeBuilt:false,currentM010RuntimeVerified:false,performanceTransferred:false};
await writeFile(join(here,'source-receipt.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:result.state,nativeInputs:304,changedFiles:changes.length,protected10Unchanged:true,exactReviewedCoreFiles:true,patchSha256:result.patchSha256,applied:false}));
