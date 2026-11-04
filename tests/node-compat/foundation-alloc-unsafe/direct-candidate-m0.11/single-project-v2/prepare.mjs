// Source/configuration preparation ONLY. No CMake configure/build, compiler,
// Rust command, componentizer or performance workload runs in this helper.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,readdir,copyFile,symlink,chmod} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),previous=dirname(here),repository=resolve(here,'../../../../..');
const milestone=join(repository,'tests/node-compat/milestones/foundations-v8');
const frozen='/tmp/starling-node-compat/foundations-v8/native-freeze',experiment='/tmp/starling-node-compat/allocunsafe-direct-m0.11-one-project';
const project=join(experiment,'project'),work=join(experiment,'build');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const receipt=JSON.parse(await readFile(join(previous,'source-receipt.json')));
assert.equal(hash(await readFile(join(previous,'source-receipt.json'))),'97bd998c559f853a14c37e439dad5179866f397b2a796323d65f33f576cf667c');
const metadata=JSON.parse(await readFile(join(frozen,'off-foundations.engine.wasm.build.json')));
assert.equal(metadata.engineSha256,receipt.ancestryEngineSha256);
assert.equal(hash(await readFile(join(frozen,'off-foundations.engine.wasm'))),metadata.engineSha256);
for(const file of metadata.sourceManifest)assert.equal(hash(await readFile(join(frozen,'source',file.path))),file.sha256,file.path);
for(const file of receipt.files)for(const arm of['ancestry','baseline','candidate'])assert.equal(hash(await readFile(join(previous,arm,file.path))),file[arm]);
const nativeBases=['builtins','runtime','include','cmake','host-apis/wasi-0.2.0','host-apis/wasi-0.2.3','host-apis/wasi-0.2.10','crates','deps/patches'];
const suffixes=new Set(['.cpp','.h','.c','.cmake','.mjs','.rs','.toml','.lock','.o','.wasm','.json','.wit','.patch']);
async function walk(root,prefix){let result=[];for(const entry of await readdir(join(root,prefix),{withFileTypes:true})){const path=join(prefix,entry.name);if(entry.isDirectory())result.push(...await walk(root,path));else result.push(path);}return result.sort();}
async function nativeMap(){const files=[];for(const base of nativeBases)for(const path of await walk(project,base))if(suffixes.has(path.slice(path.lastIndexOf('.'))))files.push({path,sha256:hash(await readFile(join(project,path)))});for(const path of['CMakeLists.txt','rust-toolchain.toml'])files.push({path,sha256:hash(await readFile(join(project,path)))});return files;}
function expectedMap(arm){return metadata.sourceManifest.map(file=>({path:file.path,sha256:receipt.files.find(item=>item.path===file.path)?.[arm]??file.sha256}));}
function difference(before,after){assert.deepEqual(before.map(item=>item.path),after.map(item=>item.path));return before.filter((item,index)=>item.sha256!==after[index].sha256).map(item=>item.path);}
function command(args,cwd=repository){const result=spawnSync(args[0],args.slice(1),{cwd,encoding:'utf8',maxBuffer:32*1024*1024});assert.equal(result.status,0,result.stderr||result.stdout);return result.stdout;}
await mkdir(here,{recursive:true});
await writeFile(join(here,'preparation-started.json'),JSON.stringify({atUtc:new Date().toISOString(),experiment,project,work})+'\n',{flag:'wx'});
await mkdir(experiment,{recursive:true});
command(['git','clone','--shared','--no-checkout',repository,project]);command(['git','checkout','--detach',metadata.auditedBaseRevision],project);
assert.equal(command(['git','rev-parse','HEAD'],project).trim(),metadata.auditedBaseRevision);
// Clone supplies immutable tracked configuration/support files missing from the
// historical293-path inventory. Overlay reviewed native bytes, never live files.
for(const file of metadata.sourceManifest){const target=join(project,file.path);await mkdir(dirname(target),{recursive:true});await copyFile(join(frozen,'source',file.path),target);}
for(const file of receipt.files){const target=join(project,file.path);await mkdir(dirname(target),{recursive:true});await copyFile(join(previous,'baseline',file.path),target);}
const inputs=[];
async function pinCopy(source,path,expected,origin){const bytes=await readFile(source);if(expected)assert.equal(hash(bytes),expected,path);const target=join(project,path);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);inputs.push({path,sha256:hash(bytes),source,origin});}
const recipe=join(frozen,'build-engine.sh');
await pinCopy(recipe,'tests/node-compat/build-engine.sh','af5b0e8cd34aae6923dacf32bfaf80f8c05c8f12edf014a3ae3c77d58ed2226f','frozen-v8-native-recipe');
for(const name of['module-selection.mjs','profile-bundler.mjs','componentizer.mjs','capability-policy.mjs','toolchain.mjs','foundations/native-scalar-harness.mjs'])
  await pinCopy(join(milestone,'harness',name),'tests/node-compat/'+name,null,'archived-v8-harness-byte-copy');
await pinCopy(join(frozen,'openssl-source-audit.py'),'tests/node-compat/provenance/openssl-source-audit.py',null,'frozen-v8-full-OpenSSL-auditor');
const patches=[
 ['abi-fix/componentize-u32-result.patch','c70c1b76ae9ddeba7cbaad2861f1ecc03710da7241ca6365d00c9ece8243324b'],
 ['abi-fix/componentize-i64-bigint-v1.patch','c75bd3062ac03fce743901db2cab502b6ac60979679f23ef9f6a869488574cf4'],
 ['entropy/componentize-entry-policy-v1.patch','a12c00a0913a2a03e4cea3ab0e525c5cec56d4e0101d33076d6a3687df824f99'],
 ['foundation-add-abort/strict-event-v3.patch','9b2e54c9527a5c078221ad49f67f7354c9fb1df00eb99f0720b3d7874402603a'],
 ['foundation-add-abort/componentize-strict-event-boundary-v2.patch','84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2'],
 ['abi-fix/componentize-import-i32-v1.patch','d300e345cb56a5bb1560f1f993c2cc763bca273e6bcf51e38aadc8e27d84782c'],
 ['abi-fix/splicer-Cargo.v1.lock','6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd'],
 ['oom/componentize-clock-errno-v2.patch','57ace551f7d723cbf9faa41c42eda08feace9370f571175284e36c67d4c24da3'],
];
for(const[path,digest]of patches)await pinCopy(join(repository,'tests/node-compat',path),'tests/node-compat/'+path,digest,'hash-pinned-v8-recipe-or-packager-input');
// This compares each extra tracked support file with its audited Git blob.
const support=['componentize.sh.in',...(await walk(project,'deps/include')),...(await walk(project,'scripts')),
  'tests/wpt-harness/wpt.cmake','tests/wpt-harness/wpt_builtins.cpp','tests/wpt-harness/build-wpt-runtime.sh','tests/wpt-harness/pre-harness.js','tests/wpt-harness/post-harness.js'];
const supportInputs=[];
for(const path of support){const blob=spawnSync('git',['show',metadata.auditedBaseRevision+':'+path],{cwd:project,maxBuffer:8*1024*1024});assert.equal(blob.status,0);assert.equal(hash(await readFile(join(project,path))),hash(blob.stdout));supportInputs.push({path,sha256:hash(blob.stdout),origin:metadata.auditedBaseRevision+':'+path});}
await chmod(join(project,'scripts/wasm-opt'),0o755);
await mkdir(work,{recursive:true});
const shared='/tmp/starling-node-compat/improved-build';
const links=[['cache',join(shared,'cache')],['tools',join(shared,'tools')],
 ['componentize-source.tar.gz',join(shared,'componentize-source.tar.gz')],
 ['spidermonkey-release.tar.gz',join(shared,'spidermonkey-release.tar.gz')],
 ['spidermonkey-dist-release',join(shared,'spidermonkey-dist-release')],['openssl-source.tar.gz',join(shared,'openssl-source.tar.gz')]];
for(const[name,target]of links)await symlink(target,join(work,name));
const archives=[];for(const[name,expected]of[['componentize-source.tar.gz','8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10'],['spidermonkey-release.tar.gz','c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'],['openssl-source.tar.gz','dfdd77e4ea1b57ff3a6dbde6b0bdc3f31db5ac99e7fdd4eaf9e1fbb6ec2db8ce']]){const path=join(work,name);assert.equal(hash(await readFile(path)),expected);archives.push({path,sha256:expected});}
const baseline=await nativeMap();assert.deepEqual(baseline,expectedMap('baseline'));
const supportBefore=await Promise.all([...inputs,...supportInputs].map(async file=>({path:file.path,sha256:hash(await readFile(join(project,file.path)))})));
// Source-only rehearsal at the SAME absolute paths. Restore baseline before any
// real build. Actual switch after a build is separately baseline-freeze gated.
for(const path of receipt.pairChanged)await copyFile(join(previous,'candidate',path),join(project,path));
const candidate=await nativeMap();assert.deepEqual(candidate,expectedMap('candidate'));
assert.deepEqual(difference(baseline,candidate),receipt.pairChanged);
const supportAfter=await Promise.all(supportBefore.map(async file=>({path:file.path,sha256:hash(await readFile(join(project,file.path)))})));assert.deepEqual(supportAfter,supportBefore);
for(const path of receipt.pairChanged)await copyFile(join(previous,'baseline',path),join(project,path));
assert.deepEqual(await nativeMap(),baseline);
const suffix='entropy-entry-v1-strict-callback-v3.OFF.path-1.events-1.string-decoder-1.assert-1.querystring-1.util-1';
const plan={schema:1,state:'single-private-project-baseline-prepared-no-build',atUtc:new Date().toISOString(),
  supersedes:'Original195-file source checkpoint remains immutable; only two-project build-plan wording is superseded',
  experiment,project,work,sourceDir:join(work,'componentize-abi-fixed-bigint-v1-'+suffix),buildDir:join(work,'engine-abi-fixed-bigint-v1-'+suffix),
  recipe:{path:join(project,'tests/node-compat/build-engine.sh'),sha256:hash(await readFile(recipe)),unchangedFromFrozenV8:true},
  oldSelector:{path:join(project,'tests/node-compat/module-selection.mjs'),sha256:inputs.find(file=>file.path.endsWith('/module-selection.mjs')).sha256,liveSelectorChanged:false},
  inputs,supportInputs,archives,links:links.map(([name,target])=>({path:join(work,name),target})),
  ancestryEngineSha256:metadata.engineSha256,ancestryMetadataSha256:hash(await readFile(join(frozen,'off-foundations.engine.wasm.build.json'))),
  profileVersion:'sm-node-22.14.0-m0.11',sameAbsolutePathsAcrossArms:true,
  sourceMapProof:{baseline,candidate,difference:receipt.pairChanged,supportMapBefore:supportBefore,supportMapAfter:supportAfter,baselineRestored:true},
  requestedCMakeOptions:metadata.requestedCMakeOptions,
  buildEnvironment:{NODE_COMPAT_NODE:'/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',NODE_COMPAT_BUILD_ROOT:work,NODE_COMPAT_JOBS:'4',
    NODE_COMPAT_BUILD_TYPE:'Release',NODE_COMPAT_GC_STRESS:'0',NODE_COMPAT_OOM_TESTING:'0',NODE_COMPAT_ENTROPY_MODE:'OFF',
    NODE_COMPAT_PATH:'1',NODE_COMPAT_EVENTS:'1',NODE_COMPAT_STRING_DECODER:'1',NODE_COMPAT_ASSERT:'1',NODE_COMPAT_QUERYSTRING:'1',NODE_COMPAT_UTIL:'1',
    NODE_COMPAT_ABI_FIX:'1',NODE_COMPAT_BIGINT_FIX:'1',NODE_COMPAT_COMPONENTIZE_MODULE:'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js'},
  artifactTagPolicy:'m011-baseline then m011-candidate; tags change artifact/log/receipt filenames only, not source/build dirs or CMake options',
  buildAuthorized:false,nativeBuilt:false,
  next:'Root reviews helper/recipe and source-map proof; then explicitly authorizes sequential4job baseline/freeze/switch/candidate builds'};
await writeFile(join(here,'preparation-results.json'),JSON.stringify(plan,null,2)+'\n');
await writeFile(join(here,'recipe-diff.patch'),'');
await copyFile(recipe,join(here,'build-engine.v8.sh'));
await writeFile(join(experiment,'state.json'),JSON.stringify({schema:1,phase:'baseline-prepared',preparationSha256:hash(JSON.stringify(plan,null,2)+'\n')},null,2)+'\n');
console.log(JSON.stringify({state:plan.state,project,buildDir:plan.buildDir,nativeInputs:baseline.length,onlyChangedPaths:receipt.pairChanged,supportInputs:supportInputs.length,helperInputs:inputs.length,baselineRestored:true,buildExecuted:false}));
