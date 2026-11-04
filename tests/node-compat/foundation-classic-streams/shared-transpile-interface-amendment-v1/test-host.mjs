// Owned output tests and host-side Jco transpilation only; no guest invocation.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp,mkdir,readFile,writeFile,lstat,symlink,unlink,readdir} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {trackedWriter,publishCompletion} from './proposed/harness/completion.mjs';
import {loadToolchain} from '../../toolchain.mjs';
assert.equal(process.version,'v22.14.0');
const hash=data=>createHash('sha256').update(data).digest('hex');
const root=await mkdtemp('/tmp/starling-node-compat/classic-shared-interface-v1-');
const cases=[];
async function check(name,fn){await fn();cases.push(name);}
async function area(name){const output=join(root,name);await mkdir(join(output,'interfaces'),{recursive:true});return{output,tracked:trackedWriter(output)};}
const {output,tracked}=await area('owned');
const declaration=join(output,'interfaces/wasi-random-random.d.ts');
await check('new generated declaration exclusively created',async()=>{await tracked.writeGenerated(declaration,'export interface Random {}\n',{flag:'wx'});assert.equal(tracked.paths.size,1);});
const firstStat=await lstat(declaration,{bigint:true});
await check('same-run byte-identical declaration reused without rewrite',async()=>{await tracked.writeGenerated(declaration,Buffer.from('export interface Random {}\n'),{flag:'wx'});const stat=await lstat(declaration,{bigint:true});assert.equal(stat.ino,firstStat.ino);assert.equal(stat.mtimeNs,firstStat.mtimeNs);assert.equal(tracked.paths.size,1);});
await check('same-length different declaration refused',async()=>assert.rejects(tracked.writeGenerated(declaration,'export interface Danger {}\n',{flag:'wx'})));
await check('different-length declaration refused',async()=>assert.rejects(tracked.writeGenerated(declaration,'changed',{flag:'wx'})));
await check('ordinary duplicate writer remains exclusive',async()=>assert.rejects(tracked.write(declaration,'export interface Random {}\n',{flag:'wx'}),{code:'EEXIST'}));
await check('untracked existing declaration refused',async()=>{const path=join(output,'interfaces/old.d.ts');await writeFile(path,'old');await assert.rejects(tracked.writeGenerated(path,'old',{flag:'wx'}),{code:'EEXIST'});});
await check('generated JavaScript cannot be reused',async()=>{const path=join(output,'classic.js');await tracked.writeGenerated(path,'export {};',{flag:'wx'});await assert.rejects(tracked.writeGenerated(path,'export {};',{flag:'wx'}));});
await check('generated core Wasm cannot be reused',async()=>{const path=join(output,'classic.core.wasm');await tracked.writeGenerated(path,new Uint8Array([0,97,115,109]),{flag:'wx'});await assert.rejects(tracked.writeGenerated(path,new Uint8Array([0,97,115,109]),{flag:'wx'}));});
await check('nested declaration cannot be reused',async()=>{const path=join(output,'interfaces/nested/file.d.ts');await mkdir(dirname(path),{recursive:true});await tracked.writeGenerated(path,'nested',{flag:'wx'});await assert.rejects(tracked.writeGenerated(path,'nested',{flag:'wx'}));});
await check('nonexclusive generated mode refused',async()=>assert.rejects(tracked.writeGenerated(declaration,'export interface Random {}\n',{flag:'w'})));
await check('outside output refused',async()=>assert.rejects(tracked.writeGenerated(join(root,'escape.d.ts'),'escape',{flag:'wx'})));
await check('tracked leaf replaced by symlink refused',async()=>{const a=await area('leaf-link'),path=join(a.output,'interfaces/one.d.ts'),target=join(root,'leaf-target');await a.tracked.writeGenerated(path,'same',{flag:'wx'});await writeFile(target,'same');await unlink(path);await symlink(target,path);await assert.rejects(a.tracked.writeGenerated(path,'same',{flag:'wx'}));});
await check('symlinked output parent refused',async()=>{const a=await area('parent-link'),target=join(root,'external');await mkdir(target);await symlink(target,join(a.output,'alias'));await assert.rejects(a.tracked.writeGenerated(join(a.output,'alias/new.d.ts'),'same',{flag:'wx'}));});
await check('tracked declaration tamper cannot become new expected bytes',async()=>{const a=await area('tampered'),path=join(a.output,'interfaces/one.d.ts');await a.tracked.writeGenerated(path,'original',{flag:'wx'});await writeFile(path,'replacement');await assert.rejects(a.tracked.writeGenerated(path,'replacement',{flag:'wx'}));});
await check('completion inventories shared declaration once',async()=>{const done=await publishCompletion({output,paths:tracked.paths,report:{variant:'owned',status:'HOST_ONLY',engineSha256:null}});assert.equal(done.files.filter(row=>row.path==='interfaces/wasi-random-random.d.ts').length,1);assert.equal(done.requiresIndependentTerminalExitCodeZero,true);});

const toolchain=await loadToolchain();
const jcoPath=toolchain.require.resolve('@bytecodealliance/jco');
const {transpile}=await import(pathToFileURL(jcoPath));
const original='/tmp/starling-node-compat/production-classic-runtime-v2/normal-runtime';
const generated=await area('actual-two-components');
const artifacts=[],filesByComponent=[];
for(const name of ['classic','deployed_fatal']){
  const componentPath=join(original,name+'.component.wasm'),component=await readFile(componentPath);
  const result=await transpile(component,{name,wasiShim:true});
  const names=Object.keys(result.files).sort();
  for(const filename of names){const path=join(generated.output,filename);await mkdir(dirname(path),{recursive:true});await generated.tracked.writeGenerated(path,result.files[filename],{flag:'wx'});}
  assert.equal(hash(await readFile(componentPath)),hash(component));
  artifacts.push({componentPath,componentSha256:hash(component),componentBytes:component.length,transpileName:name,generatedFiles:names.map(path=>({path,sha256:hash(result.files[path]),bytes:Buffer.byteLength(result.files[path])}))});
  filesByComponent.push(new Set(names));
}
const shared=[...filesByComponent[0]].filter(path=>filesByComponent[1].has(path));
assert.deepEqual(shared,['interfaces/wasi-random-random.d.ts']);
for(const filename of shared)assert.equal(artifacts[0].generatedFiles.find(x=>x.path===filename).sha256,artifacts[1].generatedFiles.find(x=>x.path===filename).sha256);
const report={schemaVersion:1,state:'SHARED_DECLARATION_HOST_TESTS_AND_ACTUAL_TRANSPILE_PASSED',passed:cases.length,failures:0,cases,output:root,
  actualComponents:artifacts,sharedGeneratedFiles:shared,trackedActualGeneratedFiles:generated.tracked.paths.size,
  jcoVersion:JSON.parse(await readFile(join(toolchain.directory,'node_modules/@bytecodealliance/jco/package.json'))).version,
  jcoEntrySha256:hash(await readFile(jcoPath)),guestModuleImported:false,guestExportCalled:false,componentizerInvoked:false,targetHostInvoked:false,
  scope:'Transpiles two existing Runtime components and writes generated files to a fresh owned directory. No generated JavaScript is imported.'};
await writeFile(join(root,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(report));
