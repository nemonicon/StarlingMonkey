// Read-only actual Source bookends plus inert copy/schema DATA; no actor/copy.
import assert from 'node:assert/strict';
import {readFile,readdir,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,relative} from 'node:path';
import {compileFunction} from 'node:vm';
const plan=JSON.parse(await readFile(new URL('./plans.json',import.meta.url),'utf8'));
const descriptor=async path=>{const bytes=await readFile(path);return {path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};};
assert.deepEqual(await descriptor(plan.applicationInputs.path),plan.applicationInputs);
const input=JSON.parse(await readFile(plan.applicationInputs.path));
assert.deepEqual(await descriptor(plan.applicationBuildResult.path),plan.applicationBuildResult);
const build=JSON.parse(await readFile(plan.applicationBuildResult.path));assert.deepEqual(build.applicationInventory,input);assert.deepEqual(build.applicationInventoryDescriptor,plan.applicationInputs);
const code=await readFile(new URL('./run-stock.mjs',import.meta.url),'utf8');let checks=0;
const schema=code.slice(code.indexOf('function expectedDirectoryPaths(value){'),code.indexOf('validateInventoryFrame(input,plan.expectedApplication);'));
const validators=compileFunction(schema+'return {expectedDirectoryPaths,validateInventoryFrame};',['assert'])(assert);
validators.validateInventoryFrame(input,plan.expectedApplication);checks++;
assert.equal(validators.expectedDirectoryPaths(input).length,426);assert.equal(input.directories.length,425);checks++;
for(const change of [
 x=>x.directories.push({path:'.'}),x=>x.directories.pop(),x=>x.files.pop(),
 x=>x.directories[0].path='../escape',x=>x.files[0].path=x.files[1].path,x=>x.bytes++,
]){const x=structuredClone(input);change(x);assert.throws(()=>validators.validateInventoryFrame(x,plan.expectedApplication));checks++;}
const walkSource=code.slice(code.indexOf('async function walk(root){'),code.indexOf('async function sourceBookend(){'));
const sourceBody=code.slice(code.indexOf('async function sourceBookend(){'),code.indexOf('\nasync function copiedApplicationBookend'));
function sourceGuard(value,p){return compileFunction(walkSource+sourceBody+'return sourceBookend;',
 ['assert','readFile','readdir','lstat','realpath','join','relative','descriptor','input','plan','expectedDirectoryPaths'])(
 assert,readFile,readdir,lstat,realpath,join,relative,descriptor,value,p,validators.expectedDirectoryPaths);}
const guard=sourceGuard(input,plan);await guard();await guard();checks+=2;
for(const key of ['mode','dev','ino','nlink']){const p=structuredClone(plan);p.applicationRootIdentity[key]++;await assert.rejects(sourceGuard(input,p));checks++;}
const copyBody=code.slice(code.indexOf('async function copiedApplicationBookend(application){'),code.indexOf('\nconst result ='));
const copyRoot='/inert-copy';
async function copyModel(delta={}){
 const dirs=validators.expectedDirectoryPaths(input),rows=new Map(input.files.concat(input.directories).map(r=>[r.path,r]));
 const stat=async path=>{
  const rel=relative(copyRoot,path);if(rel==='')return {mode:delta.rootMode??plan.applicationRootIdentity.mode,dev:plan.applicationRootIdentity.dev,ino:plan.applicationRootIdentity.ino+1,isDirectory:()=>true,isSymbolicLink:()=>false};
  const r=rows.get(rel);assert(r);return {mode:delta.directoryMode&&input.directories.includes(r)?0:r.mode,nlink:delta.nlink??1,dev:r.dev,ino:delta.sameInode?r.ino:r.ino+1000000};
 };
 const describe=async path=>{const r=rows.get(relative(copyRoot,path));return {path,sha256:r.sha256,bytes:r.bytes};};
 const fn=compileFunction(copyBody+'return copiedApplicationBookend;',
  ['assert','walk','input','plan','expectedDirectoryPaths','lstat','realpath','join','descriptor'])(
  assert,async()=>({files:input.files.map(r=>r.path),dirs,links:[]}),input,plan,validators.expectedDirectoryPaths,stat,async p=>p,join,describe);
 await fn(copyRoot);
}
await copyModel();checks++;
for(const delta of [{rootMode:0},{nlink:2},{sameInode:true},{directoryMode:true}]){await assert.rejects(copyModel(delta));checks++;}
assert(code.includes("await rm(join(application, '.next/cache'), {recursive: true, force: true});"));checks++;
console.log(JSON.stringify({sourceOnly:true,checks,actualOriginalApplicationReadOnlyBeforeFinal:true,
 schemaDirectories425RootSeparate:true,actualCopyMade:false,copyBookendCasesAreInertData:true,
 originalSourceModesRetained:true,actorOrServerOrBrowserOrNetworkOrGuestInvoked:false}));
