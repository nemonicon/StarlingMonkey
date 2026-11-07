// Source/actual retained DATA and inert callbacks only. No app copy or actor.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {compileFunction} from 'node:vm';
import {join} from 'node:path';
import {relativeMember,sourceDirectoryNames,ownedDirectoryNames,validateFreshInput} from './app-policy.mjs';
const read=async name=>JSON.parse(await readFile(new URL(name,import.meta.url),'utf8'));
const plan=await read('./plan.json');
async function retained(ref){const bytes=await readFile(ref.path);assert.equal(bytes.length,ref.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),ref.sha256);return JSON.parse(bytes);}
const input=await retained(plan.applicationInputs),build=await retained(plan.applicationBuildResult);
let checks=0;
assert(validateFreshInput(input,build,plan));checks++;
assert.equal(sourceDirectoryNames(input).length,426);assert.equal(ownedDirectoryNames(input,plan.applicationSchema).length,427);checks++;
assert.equal(input.directories.some(x=>x.path==='.'||x.path==='.next/cache'),false);checks++;
for(const [name,change]of[
 ['wrong schema',(i,b,p)=>p.applicationSchema.name='historical-root-included'],
 ['missing explicit root identity',(i,b,p)=>delete p.applicationRootIdentity],
 ['root field missing',(i,b,p)=>delete p.applicationRootIdentity.nlink],
 ['wrong source root',(i,b,p)=>p.applicationSource='/old/root'],
 ['old count',(i,b,p)=>p.applicationSchema.files=2218],
 ['old bytes',(i,b,p)=>p.applicationSchema.bytes=48808299],
 ['root included flag',(i,b,p)=>p.applicationSchema.sourceDirectoriesExcludeRoot=false],
 ['root in source dirs',i=>i.directories.push({path:'.'})],
 ['cache in source dirs',i=>i.directories.push({path:'.next/cache'})],
 ['cache source file',i=>i.files[0].path='.next/cache/data'],
 ['wrong owned count',(i,b,p)=>p.applicationSchema.ownedDirectoriesIncludingRoot=426],
 ['additional undeclared directory',(i,b,p)=>p.applicationSchema.additionalDirectories.push('other')],
 ['failed actual build',(i,b)=>b.passed=false],
 ['missing original protection',(i,b)=>b.originalInputsPreserved=false],
 ['build errors',(i,b)=>b.errors.push({message:'failed'})],
 ['mismatched manifest descriptor',(i,b)=>b.applicationInventoryDescriptor.sha256='0'.repeat(64)],
 ['wrong build root',(i,b)=>b.outputRoot='/old/build'],
 ['wrong installed next',(i,b)=>b.installedVersions.next='99.0.0'],
 ['duplicate file',i=>i.files[1].path=i.files[0].path],
 ['duplicate directory',i=>i.directories[1].path=i.directories[0].path],
]){
 const i=structuredClone(input),b={...build,errors:[],installedVersions:{...build.installedVersions},applicationInventoryDescriptor:{...build.applicationInventoryDescriptor},applicationInventory:i},p=structuredClone(plan);
 change(i,b,p);assert.throws(()=>validateFreshInput(i,b,p),undefined,name);checks++;
}
for(const name of ['.','../x','/absolute','a//b','a\\b','a\0b']){assert.throws(()=>relativeMember(name));checks++;}
const code=await readFile(new URL('./deploy.mjs',import.meta.url),'utf8');
const start=code.indexOf('async function prepareReadonlyCopy(){'),end=code.indexOf('\nasync function readonlyBookend(){',start);assert(start>=0&&end>start);
const make=compileFunction('return '+code.slice(start,end),['assert','cp','input','app','fsConstants','mkdir','join','readdir','chmod','ownedDirectoryNames','plan']);
const original=JSON.stringify(input),calls=[],app='/inert-owned-app';
const prepare=make(assert,async(src,dst,options)=>{assert.equal(src,input.root);assert.equal(dst,app);assert.deepEqual(options,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:71});calls.push(['copy']);},input,app,{COPYFILE_FICLONE:71},async(path,options)=>{assert.equal(path,app+'/.next/cache');assert.deepEqual(options,{mode:0o700});calls.push(['mkdir']);},join,async path=>{assert.equal(path,app+'/.next/cache');calls.push(['empty-check']);return[];},async(path,mode)=>calls.push(['chmod',path,mode]),ownedDirectoryNames,plan);
await prepare();
assert.deepEqual(calls.slice(0,3),[['copy'],['mkdir'],['empty-check']]);
assert.equal(calls.filter(x=>x[0]==='chmod'&&x[2]===0o444).length,2181);
assert.equal(calls.filter(x=>x[0]==='chmod'&&x[2]===0o555).length,427);
assert.equal(calls.at(-1)[1],app);assert.equal(calls.at(-1)[2],0o555);
assert.equal(calls.filter(x=>x[0]==='chmod'&&x[1]===app+'/.next/cache').length,1);
assert.equal(JSON.stringify(input),original);checks++;
let chmodCalls=0;const reason=Symbol('inert mkdir callback refusal');
const refused=make(assert,async()=>{},input,app,{COPYFILE_FICLONE:71},async()=>{throw reason;},join,async()=>[],async()=>{chmodCalls++;},ownedDirectoryNames,plan);
let caught,failed=false;try{await refused();}catch(value){caught=value;failed=true;}
assert(failed&&caught===reason);assert.equal(chmodCalls,0);checks++;
console.log(JSON.stringify({sourceOnly:true,inertChecks:checks,freshActualInventoryValidated:true,
 sourceRootExcludedAndOwnedMountpointSeparate:true,actualCopyFunctionTextUsed:true,
 cacheMountpointCreatedBeforeAnyChmod:true,exactSourceInputUnchanged:true,
 noAppCopyOrFilesystemMutationOrActorOrNetworkOrGuestInvoked:true}));
