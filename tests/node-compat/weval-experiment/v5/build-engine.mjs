// Untested build template. --plan (default) does no clone/configure/build.
// --build operates only in a new private namespace; the production recipe and
// all existing source/build/artifact directories remain unchanged.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,copyFile,stat,access,symlink} from 'node:fs/promises';
import {constants} from 'node:fs';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {wevalRecipe} from './recipe-transform.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
const pins=JSON.parse(await readFile(join(here,'pins.json'))),hash=value=>createHash('sha256').update(value).digest('hex');
const driverPaths=['build-engine.mjs','recipe-transform.mjs','pins.json','../prepare-assets.mjs','../pins.json'];
const driverSources=await Promise.all(driverPaths.map(async path=>({path:resolve(here,path),sha256:hash(await readFile(resolve(here,path)))})));
const root=resolve(process.env.NODE_COMPAT_WEVAL_ROOT??'/tmp/starling-node-compat/weval-experiment');
const namespace=resolve(process.env.NODE_COMPAT_WEVAL_BUILD_ROOT??join(root,'custom-release-v5-1'));
assert(namespace!==repo && relative(repo,namespace).startsWith('..'),'Use an external private build namespace');
const build=process.argv.includes('--build');
const plan={namespace,mode:build?'build':'plan-only',needs:['NODE_COMPAT_WEVAL_BASE_ENGINE: verified current OFF Release engine including lazy builtin import fix','NODE_COMPAT_WEVAL_SOURCE_FREEZE: root containing its exact sourceManifest paths','NODE_COMPAT_NODE: exact v22.14.0','NODE_COMPAT_WEVAL_CACHE_ROOT: existing pinned SDK/cbindgen/CPM cache (optional)'],requestedCMakeOptions:pins.buildOptions,packagingOptions:pins.packagingOptions,nativeSources:'Copy and hash-check the explicit accepted native engine manifest, with no production code edits',cache:'Generate a new matching generic IC cache from the same custom raw engine; copy and hash-bind it to that engine',status:'Frozen production v5 native inputs; no application AOT/performance claim'};
if(!build){console.log(JSON.stringify(plan,null,2));process.exit(0);}
assert.equal(process.version,'v22.14.0');assert.equal(process.platform,'darwin');assert.equal(process.arch,'arm64');
assert(process.env.NODE_COMPAT_WEVAL_BASE_ENGINE && process.env.NODE_COMPAT_WEVAL_SOURCE_FREEZE,'Select the exact accepted engine and frozen native source inputs');
try{await access(join(namespace,'build-started.json'));throw new Error('Refusing to overwrite a prior experiment namespace; select a new NODE_COMPAT_WEVAL_BUILD_ROOT');}catch(error){if(error.code!=='ENOENT')throw error;}
const baseEngine=resolve(process.env.NODE_COMPAT_WEVAL_BASE_ENGINE),base=JSON.parse(await readFile(baseEngine+'.build.json'));
assert.equal(hash(await readFile(baseEngine)),pins.baseline.engineSha256);assert.equal(base.engineSha256,pins.baseline.engineSha256);assert.equal(hash(await readFile(baseEngine+'.build.json')),pins.baseline.metadataSha256);assert.equal(base.starlingMonkeyRevision,pins.baseline.starlingMonkeyRevision);assert.equal(base.sourceManifest.length,pins.baseline.sourceCount);assert.equal(hash(JSON.stringify(base.sourceManifest)),pins.baseline.sourceManifestSha256);assert.deepEqual(base.componentizeSourceManifest,pins.baseline.componentizeSourceManifest);assert.equal(base.pathEnabled,true);assert.equal(base.eventsEnabled,true);assert.equal(base.entropyPolicy,'off');assert.equal(base.profileEnabled,true);assert.equal(base.gcStress,false);assert.equal(base.oomTesting,false);assert.equal(base.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
const freeze=resolve(process.env.NODE_COMPAT_WEVAL_SOURCE_FREEZE);
for(const entry of base.sourceManifest)assert.equal(hash(await readFile(join(freeze,entry.path))),entry.sha256,entry.path);
// The accepted freeze includes its historical normal recipe. Events or later
// working-tree changes must not silently change this experiment's control.
const frozenRecipe=resolve(process.env.NODE_COMPAT_WEVAL_BASE_RECIPE??join(dirname(baseEngine),'build-engine.sh'));
const baseline=await readFile(frozenRecipe,'utf8');
assert.equal(hash(baseline),pins.baseline.recipeSha256,'Normal recipe changed; review/repin the private transformation');
const normalHelperPaths=pins.helperFiles;
const frozenAudit=resolve(process.env.NODE_COMPAT_WEVAL_BASE_AUDIT??join(dirname(baseEngine),'openssl-source-audit.py'));
const helperSource=entry=>entry.source==='frozen-audit'?frozenAudit:join(repo,entry.path);
for(const entry of normalHelperPaths)assert.equal(hash(await readFile(helperSource(entry))),entry.sha256,entry.path);
await mkdir(namespace,{recursive:true});await writeFile(join(namespace,'build-started.json'),JSON.stringify({...plan,baseEngine,baseEngineSha256:base.engineSha256,baseReceiptSha256:hash(await readFile(baseEngine+'.build.json')),baseSourceManifestSha256:hash(JSON.stringify(base.sourceManifest))},null,2)+'\n');
function command(program,args,options={}){const result=spawnSync(program,args,{stdio:'inherit',...options});assert.equal(result.status,0,`${program} failed (${result.status})`);return result;}
const source=join(namespace,'source');command('git',['clone','--shared','--no-checkout',repo,source]);command('git',['-C',source,'checkout','--detach',base.starlingMonkeyRevision]);
for(const entry of base.sourceManifest){const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});await copyFile(join(freeze,entry.path),target);}
for(const entry of normalHelperPaths){const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});await copyFile(helperSource(entry),target);}
const receiptPath=join(root,'asset-receipt.json');
let assets;try{assets=JSON.parse(await readFile(receiptPath));}catch{}
if(!assets?.extracted){command(process.execPath,[join(here,'../prepare-assets.mjs'),'--extract']);assets=JSON.parse(await readFile(receiptPath));}
for(const tool of assets.tools)assert.equal(hash(await readFile(tool.path)),tool.sha256,tool.name);
for(const tool of assets.tools)assert.equal(tool.sha256,pins.cachedHostTools[tool.name].sha256,tool.name);
const tool=name=>assets.tools.find(entry=>entry.name===name).path;
const recipe=wevalRecipe(baseline);
const privateRecipe=join(source,'tests/node-compat/build-engine.sh');await mkdir(dirname(privateRecipe),{recursive:true});await writeFile(privateRecipe,recipe,{mode:0o755});
await writeFile(join(namespace,'recipe-transformation.json'),JSON.stringify({baseRecipe:frozenRecipe,baseRecipeSha256:hash(baseline),privateRecipeSha256:hash(recipe),privateRecipe,sourceFiles:normalHelperPaths,changes:['Release-only release_weval asset and matching distribution','WEVAL ON, wasm-opt -O0 path and explicit checked tools','Weval engine output filename and artifact namespace','Matching metadata requested flags'],scope:'Only this private copy is changed; repository build-engine.sh and production CMake are unchanged'},null,2)+'\n');
const work=join(namespace,'build');await mkdir(work,{recursive:true});
const shared=resolve(process.env.NODE_COMPAT_WEVAL_CACHE_ROOT??'/tmp/starling-node-compat/improved-build');
for(const dir of ['cache','tools'])await symlink(join(shared,dir),join(work,dir),'dir');
for(const[name,destination]of [['spidermonkey-static-release_weval.tar.gz','spidermonkey-release_weval.tar.gz']])await copyFile(join(root,'downloads',name),join(work,destination),constants.COPYFILE_FICLONE);
const env={...process.env,NODE_COMPAT_NODE:process.execPath,NODE_COMPAT_BUILD_ROOT:work,NODE_COMPAT_BUILD_TYPE:'Release',NODE_COMPAT_GC_STRESS:'0',NODE_COMPAT_OOM_TESTING:'0',NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_PATH:'1',NODE_COMPAT_EVENTS:'1',NODE_COMPAT_JOBS:'4',NODE_COMPAT_ABI_FIX:'1',NODE_COMPAT_BIGINT_FIX:'1',NODE_COMPAT_ARTIFACT_TAG:'weval-experiment-v5-1',NODE_COMPAT_WEVAL_BIN:tool('weval'),NODE_COMPAT_WEVAL_WASM_OPT:tool('wasmOpt'),RUST_MIN_STACK:'67108864',RAYON_NUM_THREADS:'4'};
command('bash',[privateRecipe],{env});
const fs=await import('node:fs/promises'),sidecars=(await fs.readdir(join(work,'artifacts'))).filter(name=>name.endsWith('.wasm.build.json'));assert.equal(sidecars.length,1);
const sidecar=join(work,'artifacts',sidecars[0]),metadata=JSON.parse(await readFile(sidecar)),engine=metadata.enginePath,buildDirectory=dirname(metadata.cmakeCachePath);
assert.equal(metadata.observedCMakeOptions.WEVAL,'ON');assert.equal(metadata.observedCMakeOptions.USE_WASM_OPT,'OFF');
assert.deepEqual(metadata.sourceManifest,base.sourceManifest,'Only backend/archive/optimizer configuration may differ from the accepted native source freeze');
assert.deepEqual(metadata.componentizeSourceManifest,base.componentizeSourceManifest,'Keep all native embedding ABI/entry patches identical');
const raw=join(buildDirectory,'starling-raw.wasm/starling-raw.wasm');assert.equal(hash(await readFile(raw)),metadata.engineSha256,'IC cache and copied embedding must use the same raw engine');
const cache=engine.replace(/\.wasm$/,'.ics.wevalcache');await copyFile(join(buildDirectory,'starling-raw.wasm/starling-ics.wevalcache'),cache);
const commands=spawnSync('ninja',['-C',buildDirectory,'-t','commands'],{encoding:'utf8',maxBuffer:16*1024*1024});assert.equal(commands.status,0);
const actualCommands=commands.stdout.split('\n').filter(line=>line.includes('weval --dir')||line.includes('--strip-debug -O0'));
assert(actualCommands.some(line=>line.includes(tool('weval'))&&line.includes('--cache starling-ics.wevalcache')),'Actual matching IC-cache generation command missing');
assert(actualCommands.some(line=>line.includes(tool('wasmOpt'))&&line.includes('--strip-debug -O0')),'Actual unoptimized Weval engine command missing');
assert.equal(metadata.sourceInputsCapturedBeforeBuild,true);assert.equal(metadata.componentizeSourcesCapturedBeforeBuild,true);assert.equal(metadata.generatedRustProject.cargoBuildLocked,true);assert.equal(metadata.openssl.completeSourceAudit.beforeAndAfterBuild,true);assert.equal(metadata.archivePins.spiderMonkeySha256,pins.downloads.find(item=>item.name==='spidermonkey-static-release_weval.tar.gz').sha256);
for(const entry of driverSources)assert.equal(hash(await readFile(entry.path)),entry.sha256,'Build driver changed during execution');
metadata.wevalExperiment={schemaVersion:2,baseline:'foundations-v5',sourceRoot:source,baseEngineSha256:base.engineSha256,sameNativeAndEmbeddingSourcesAsBase:true,driverSources,driversVerifiedBeforeAndAfter:true,cache:{path:cache,sha256:hash(await readFile(cache)),bytes:(await stat(cache)).size,generatedFromRawEngineSha256:metadata.engineSha256,kind:'generic IC cache from null.js; not workload training'},tools:assets.tools,downloadPins:pins.downloads,sourceReceipt:join(namespace,'build-started.json'),recipeTransformation:{path:join(namespace,'recipe-transformation.json'),baseRecipeSha256:hash(baseline),privateRecipeSha256:hash(recipe)},actualWevalAndOptimizerCommands:actualCommands,cacheGenerationEnvironment:{RAYON_NUM_THREADS:'4',RUST_MIN_STACK:'67108864'},packagingOptions:pins.packagingOptions};
await writeFile(sidecar,JSON.stringify(metadata,null,2)+'\n');console.log(JSON.stringify({engine,engineSha256:metadata.engineSha256,cache:metadata.wevalExperiment.cache,source},null,2));
