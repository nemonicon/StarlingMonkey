// UNAPPLIED second source revision: additive rebase on verified HTTP-v10.
import assert from 'node:assert/strict';
import { readFile, writeFile, readdir, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)), repo=resolve(here,'../../../..');
const first=join(here,'../production-candidate-m0.11'), hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const old=JSON.parse(await readFile(join(first,'source-receipt.json')));
const frozen={
  'index.json':'ef229fb89f768486ccc4cb142bd1defbec79e08aa091bf782d17d1592a6ba29a',
  'source-receipt.json':'740c2ea910055b1435270161c23ee80e305cd61ed806ad7d132021e80edb6d3b',
  'host-results.json':'fef08ee6f551fe999ef14fc6a34c49252ea4330e829389f40065f2d66be84ded',
  'core-m0.11-rebased.patch':'d547c51724aef22b99e0ba3f4c86a1745c62a01525394fdc19f0e0c94565a455',
};
for(const [path,sha]of Object.entries(frozen))assert.equal(hash(await readFile(join(first,path))),sha,path);
const http=JSON.parse(await readFile(join(repo,'tests/node-compat/foundations/http-v10-results.json')));
assert.equal(http.state,'HTTP_V10_BOTH_UNMODIFIED_HOSTS_PASSED');
assert.equal(hash(await readFile(join(repo,'tests/node-compat/foundations/http-v10-index.json'))),'86233ce25675225ca825a3e76ecf2efc140bac70599bf6e9473a9204e34f3619');
assert.equal(http.sourceFilesVerified.length,18);
for(const file of http.sourceFilesVerified)assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,file.path);
for(const file of old.ancestry)assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,file.path);
assert.equal(old.ancestry.length,304);
const dirs=['builtins','runtime','include','cmake','host-apis/wasi-0.2.0','host-apis/wasi-0.2.3','host-apis/wasi-0.2.10','crates','deps/patches'];
const extensions=new Set(['.cpp','.h','.c','.cmake','.mjs','.rs','.toml','.lock','.o','.wasm','.json','.wit','.patch']);
const actual=[];for(const dir of dirs)for(const path of await walk(repo,dir))if(extensions.has(path.slice(path.lastIndexOf('.'))))actual.push(path);
actual.push('CMakeLists.txt','rust-toolchain.toml');assert.deepEqual(actual.sort(),old.ancestry.map(file=>file.path).sort(),'No missing/new native ancestry inputs');

async function walk(root,path=''){let files=[];for(const entry of await readdir(join(root,path),{withFileTypes:true})){const p=join(path,entry.name);if(entry.isDirectory())files.push(...await walk(root,p));else files.push(p);}return files.sort();}
const paths=new Set(await walk(join(first,'base')));
for(const file of http.sourceFilesVerified)paths.add(file.path);
const httpAudit=JSON.parse(await readFile('/tmp/starling-node-compat/foundations-v10/http-joint/component-audit.json'));
for(const id of httpAudit.bundledModules)if(id.startsWith(repo+'/'))paths.add(relative(repo,id.replace(/\.cjs\.native-profile\.mjs$/,'.cjs')));
for(const path of[
  'tests/node-compat/foundation-add-abort/integration-candidate-m0.10/new-policy-pins.json',
  'tests/node-compat/foundation-add-abort/production-native-m0.10/callback-return-results.json',
  'tests/node-compat/foundation-add-abort/production-native-m0.10/callback-return-cases.mjs',
  'tests/node-compat/wasmcloud/profile-runtime-entropy.wit','tests/node-compat/wasmcloud/profile.wit',
  'tests/node-compat/foundation-path/lexical-vectors.json','tests/node-compat/foundation-path/glob-vectors.json','tests/node-compat/foundation-path/glob-results.json',
  'tests/node-compat/foundation-string-decoder/component-corpus.json',
  'tests/node-compat/foundation-events/native-node-results.json',
  'tests/node-compat/foundation-stream-web/production-candidate/native-preflight-contract.json',
  'tests/node-compat/foundation-stream-web/candidate/codec-node-results.json','tests/node-compat/foundation-stream-web/candidate/byob-node-results.json',
  'tests/node-compat/foundation-stream-web/candidate/typed-view-node-results.json','tests/node-compat/foundation-stream-web/candidate/controller-node-results.json',
  'tests/node-compat/foundation-stream-web/iteration/node-results.json','tests/node-compat/foundation-stream-web/dataview/node-results.json',
])paths.add(path);
await writeFile(join(here,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),sourceOnly:true,nativeInputs:304,httpSchema:5,protectedGroups:29})+'\n',{flag:'wx'});
const files=new Map();
for(const path of [...paths].sort()){
  const bytes=await readFile(join(repo,path));files.set(path,hash(bytes));
  for(const variant of['base','source']){const dest=join(here,variant,path);await mkdir(dirname(dest),{recursive:true});await writeFile(dest,bytes);}
}
const reused=old.changes.filter(file=>file.path!=='tests/node-compat/wasmcloud/build-http.mjs'&&!file.path.endsWith('/http-v11.mjs'));
assert.equal(reused.length,9);
for(const file of reused){assert.equal(files.get(file.path),file.before,file.path);const bytes=await readFile(join(first,'source',file.path));assert.equal(hash(bytes),file.after,file.path);await writeFile(join(here,'source',file.path),bytes);}
const source=join(here,'source');
const generator=spawnSync(process.execPath,[join(source,'builtins/node-compat/generate-factories.mjs')],{encoding:'utf8'});assert.equal(generator.status,0,generator.stderr);
const checked=spawnSync(process.execPath,[join(source,'builtins/node-compat/generate-factories.mjs'),'--check'],{encoding:'utf8'});assert.equal(checked.status,0,checked.stderr);
for(const [path,sha256]of Object.entries(old.corePins))assert.equal(hash(await readFile(join(source,path))),sha256,'Exact reviewed core: '+path);
const v10='tests/node-compat/foundations/http-v10.mjs',v11='tests/node-compat/foundations/http-v11.mjs';
await writeFile(join(source,v11),(await readFile(join(source,v10),'utf8')).replace(/^\/\/.*\n/,'// Unapplied core m0.11 proposal; complete HTTP-v10 protected29/schema5 retained.\n'));
files.set(v11,null);
const builder='tests/node-compat/wasmcloud/build-http.mjs';
let text=await readFile(join(source,builder),'utf8');
for(const [before,after]of[
  ["const protectedAbortFoundationsFixture = httpEntry === resolve(here, '../foundations/http-v10.mjs');", "const protectedAbortFoundationsFixture = ['http-v10.mjs', 'http-v11.mjs'].some(name => httpEntry === resolve(here, '../foundations/'+name));"],
  ["['http-v7.mjs', 'http-v8.mjs', 'http-v9.mjs', 'http-v10.mjs']", "['http-v7.mjs', 'http-v8.mjs', 'http-v9.mjs', 'http-v10.mjs', 'http-v11.mjs']"],
]){assert.equal(text.split(before).length,2,before);text=text.replace(before,after);}
await writeFile(join(source,builder),text);
const changes=[];
for(const [path,before]of files){const after=hash(await readFile(join(source,path)));if(before!==after)changes.push({path,before,after});}
assert.equal(changes.length,11);
for(const file of old.ancestry)if(!old.changes.slice(0,4).some(input=>input.path===file.path))assert.equal(hash(await readFile(join(source,file.path))),file.sha256,file.path);
for(const file of [...old.protected10,...old.unchangedCritical])assert.equal(hash(await readFile(join(source,file.path))),file.sha256,file.path);
for(const file of http.sourceFilesVerified)if(!changes.some(change=>change.path===file.path))assert.equal(hash(await readFile(join(source,file.path))),file.sha256,file.path);
let patch='';
for(const change of changes){const diff=spawnSync('diff',['-u','-L',change.before?'a/'+change.path:'/dev/null','-L','b/'+change.path,change.before?join(here,'base',change.path):'/dev/null',join(source,change.path)],{encoding:'utf8'});assert.equal(diff.status,1,diff.stderr);patch+=diff.stdout;}
await writeFile(join(here,'core-m0.11-http-v10-rebased.patch'),patch);
const check=spawnSync('git',['apply','--check',join(here,'core-m0.11-http-v10-rebased.patch')],{cwd:repo,encoding:'utf8'});assert.equal(check.status,0,check.stderr);
for(const [path,sha]of files)if(sha!==null)assert.equal(hash(await readFile(join(repo,path))),sha,'Live source changed: '+path);
for(const [path,sha]of Object.entries(frozen))assert.equal(hash(await readFile(join(first,path))),sha,path);
const result={schema:2,state:'UNAPPLIED_M011_V2_HTTP_V10_REBASE_PREPARED',atUtc:new Date().toISOString(),nativeAncestryInputs:304,ancestry:old.ancestry,
  changes,corePins:old.corePins,protected10:old.protected10,unchangedCritical:old.unchangedCritical,
  originalPacket:{path:first,frozen},httpReference:{schema:5,groups:{public:16,nested:4,receivers:9,total:29},
    resultsSha256:hash(await readFile(join(repo,'tests/node-compat/foundations/http-v10-results.json'))),indexSha256:'86233ce25675225ca825a3e76ecf2efc140bac70599bf6e9473a9204e34f3619',auditedInputs:http.sourceFilesVerified,
    componentSha256:http.component.sha256,scope:'Existing m0.10 host proof only; not proof of prospective m0.11 component'},
  copiedLiveInputs:[...files].filter(([,sha])=>sha!==null).map(([path,sha256])=>({path,sha256})),
  reviewedCandidateFilesReused:reused,generator:{exitCode:generator.status,checkExitCode:checked.status,checkStdout:checked.stdout},
  patchSha256:hash(patch),patchApplyCheck:0,sourcePolicy:'zeroed-no-pool-direct-u8-v1',publicApiExpanded:false,hostImportsAdded:[],
  applied:false,nativeBuilt:false,componentized:false,performanceTransferred:false,
  pending:['Root m0.10 archive acceptance before application','Review/apply coherent11file patch','New combined actual engine/fullcore/GC/strict/HTTP import and both-host gates'],
  knownInheritedGap:'Callback-return getter READ COUNTS: Node ordinary1/protectedSignal1/alreadyAborted0; native Jco+Wasmtime ordinary0/protectedSignal0/alreadyAborted0. Getters return undefined, with no callable-then or rejection test. This core allocation proposal does not close the inherited m0.10 Events gap.'};
await writeFile(join(here,'source-receipt.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:result.state,changedFiles:changes.length,nativeInputs:304,copiedInputs:result.copiedLiveInputs.length,protected10Unchanged:true,exactReviewedCore:true,httpProtectedGroups:29,patchSha256:result.patchSha256,applied:false}));
