// Builds only new PRIVATE source/build namespaces from the accepted v3 freeze.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,copyFile,symlink,access,readdir} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {auditBuild} from './audit-build.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../..'),hash=data=>createHash('sha256').update(data).digest('hex');
const pins=JSON.parse(await readFile(join(here,'pins.json')));
const variant=process.argv.find(value=>['release','gc','oom'].includes(value))??'release';
const planOnly=process.argv.includes('--plan');
const freeze=resolve(process.env.NODE_COMPAT_UTF8_FREEZE??'/tmp/starling-node-compat/foundations-v3/native-freeze');
const root=resolve(process.env.NODE_COMPAT_UTF8_BUILD_ROOT??`/tmp/starling-node-compat/utf8-direct/${variant}-v1`);
assert(root!==repo && relative(repo,root).startsWith('..'),'Private build must be outside the checkout');
if(planOnly){console.log(JSON.stringify({variant,freeze,root,changes:['existing TextEncoder encode implementation only','private GC/failure header and explicit test flags'],normalRecipe:'Exact frozen v3 recipe; no production edits',state:'No configure or build in plan mode'},null,2));process.exit(0);}
assert.equal(process.version,'v22.14.0');
try{await access(join(root,'build-started.json'));throw new Error('Select a fresh NODE_COMPAT_UTF8_BUILD_ROOT; prior experiments stay immutable');}catch(error){if(error.code!=='ENOENT')throw error;}
const baseEngine=join(freeze,'off-path.engine.wasm'),base=JSON.parse(await readFile(baseEngine+'.build.json'));
assert.equal(hash(await readFile(baseEngine)),pins.baseEngineSha256);assert.equal(base.engineSha256,pins.baseEngineSha256);
assert.equal(hash(await readFile(baseEngine+'.build.json')),pins.baseReceiptSha256);
assert.equal(base.sourceManifest.length,pins.baseNativeInputs);
for(const entry of base.sourceManifest)assert.equal(hash(await readFile(join(freeze,'source',entry.path))),entry.sha256,entry.path);
const recipe=await readFile(join(freeze,'build-engine.sh'));assert.equal(hash(recipe),pins.baseRecipeSha256);
const patch=await readFile(join(here,'text-encoder-direct-v1.patch'));assert.equal(hash(patch),pins.patchSha256);
const testing=await readFile(join(here,'text-encoder-direct-testing.h'));assert.equal(hash(testing),pins.testingHeaderSha256);
await mkdir(root,{recursive:true});await writeFile(join(root,'build-started.json'),JSON.stringify({variant,freeze,baseEngineSha256:base.engineSha256,baseReceiptSha256:pins.baseReceiptSha256,recipeSha256:pins.baseRecipeSha256,patchSha256:pins.patchSha256,testingHeaderSha256:pins.testingHeaderSha256},null,2)+'\n');
function command(program,args,options={}){const result=spawnSync(program,args,{stdio:'inherit',...options});assert.equal(result.status,0,`${program} failed (${result.status})`);return result;}
const source=join(root,'source');command('git',['clone','--shared','--no-checkout',repo,source]);command('git',['-C',source,'checkout','--detach',base.starlingMonkeyRevision]);
for(const entry of base.sourceManifest){const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});await copyFile(join(freeze,'source',entry.path),target);}
for(const entry of pins.helpers){
  const frozenAudit=entry.path.endsWith('/openssl-source-audit.py')?join(freeze,'openssl-source-audit.py'):join(repo,entry.path);
  assert.equal(hash(await readFile(frozenAudit)),entry.sha256,entry.path);const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});await copyFile(frozenAudit,target);
}
let privateRecipeBytes=recipe;
let extensionPath;
if(variant!=='release'){
  extensionPath=join(root,'web-codec-testing.cmake');
  const definitions=['STARLING_UTF8_DIRECT_GC_STRESS=1',...(variant==='oom'?['STARLING_UTF8_DIRECT_OOM_TESTING=1','NODE_COMPAT_OOM_TESTING=1']:[])];
  await writeFile(extensionPath,`if(NOT TARGET builtin_web_text_codec)\n  message(FATAL_ERROR "Expected existing text-codec builtin target")\nendif()\ntarget_compile_definitions(builtin_web_text_codec PRIVATE ${definitions.join(' ')})\n`);
  const before='-DWEVAL=OFF -DUSE_WASM_OPT=ON';
  assert.equal(recipe.toString().split(before).length-1,1);
  privateRecipeBytes=Buffer.from(recipe.toString().replace(before,before+' -DCMAKE_CXX_FLAGS= -DCMAKE_PROJECT_ComponentizeJS_INCLUDE="$NODE_COMPAT_UTF8_EXTENSION_CMAKE"'));
}
const privateRecipe=join(source,'tests/node-compat/build-engine.sh');await writeFile(privateRecipe,privateRecipeBytes,{mode:0o755});
command('patch',['-p1','-d',source],{input:patch,stdio:['pipe','inherit','inherit']});
const codec='builtins/web/text-codec/text-encoder.cpp',header='builtins/web/text-codec/text-encoder-direct-testing.h';
assert.equal(hash(await readFile(join(source,codec))),pins.patchedTextEncoderSha256);await writeFile(join(source,header),testing);
const work=join(root,'build'),shared=resolve(process.env.NODE_COMPAT_CACHE_ROOT??'/tmp/starling-node-compat/improved-build');await mkdir(work,{recursive:true});
for(const directory of ['cache','tools'])await symlink(join(shared,directory),join(work,directory),'dir');
const flags='';
const env={...process.env,NODE_COMPAT_NODE:process.execPath,NODE_COMPAT_BUILD_ROOT:work,NODE_COMPAT_BUILD_TYPE:variant==='oom'?'Debug':'Release',NODE_COMPAT_GC_STRESS:variant==='release'?'0':'1',NODE_COMPAT_OOM_TESTING:variant==='oom'?'1':'0',NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_PATH:'1',NODE_COMPAT_ARTIFACT_TAG:`utf8-direct-${variant}-v1`,NODE_COMPAT_UTF8_EXTENSION_CMAKE:extensionPath??'',CXXFLAGS:flags};
command('bash',[privateRecipe],{env});
const sidecars=(await readdir(join(work,'artifacts'))).filter(name=>name.endsWith('.wasm.build.json')&&!name.endsWith('.raw.wasm.build.json'));assert.equal(sidecars.length,1);
const sidecar=join(work,'artifacts',sidecars[0]);
const metadata=await auditBuild({sidecar,variant,source,extensionPath});
console.log(JSON.stringify({engine:metadata.enginePath,engineSha256:metadata.engineSha256,sourceRoot:source,sidecar,variant},null,2));
