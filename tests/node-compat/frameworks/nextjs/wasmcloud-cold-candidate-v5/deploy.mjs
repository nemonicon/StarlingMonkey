// Dormant: standard builtins only until whole Source/Root/artifact authentication.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer,createConnection} from 'node:net';
import {createReadStream,constants as fsConstants} from 'node:fs';
import {readFile,writeFile,mkdir,cp,chmod,lstat,readdir,realpath,open} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const errorData=e=>({name:e?.name??typeof e,message:e?.message??String(e),stack:e?.stack??null});
// Pure fresh-app DATA policy, inlined into the authenticated actor.
function relativeMember(name){
 assert.equal(typeof name,'string');assert(name&&!name.includes('\\')&&!name.includes('\0'));
 assert(name.split('/').every(x=>x!==''&&x!=='.'&&x!=='..'));return name;
}
function sourceDirectoryNames(input){
 const names=input.directories.map(x=>relativeMember(x.path));assert.equal(new Set(names).size,names.length);
 return ['.',...names].sort();
}
function ownedDirectoryNames(input,policy){
 assert.deepEqual(policy.additionalDirectories,[]);
 const names=sourceDirectoryNames(input);assert(names.includes('.next'));assert(!names.includes('.next/cache'));
 assert(!input.files.some(x=>x.path==='.next/cache'||x.path.startsWith('.next/cache/')));
 return names;
}
function validateFreshInput(input,build,plan){
 const policy=plan.applicationSchema;
 assert.equal(policy.name,'fresh-next-standalone-root-excluded-v1');assert.equal(input.schemaVersion,1);
 assert.equal(policy.sourceDirectoriesExcludeRoot,true);assert.equal(input.root,plan.applicationSource);
 assert.equal(input.regularFiles,input.files.length);assert.equal(input.regularFiles,policy.files);
 assert.equal(input.bytes,input.files.reduce((sum,x)=>sum+x.bytes,0));assert.equal(input.bytes,policy.bytes);
 assert.equal(input.directories.length,policy.directoriesExcludingRoot);assert.deepEqual(input.symlinks,[]);
 assert.equal(new Set(input.files.map(x=>relativeMember(x.path))).size,input.files.length);
 const dirs=sourceDirectoryNames(input);assert(!input.directories.some(x=>x.path==='.'));
 assert(input.files.every(x=>!dirs.includes(x.path)));
 const owned=ownedDirectoryNames(input,policy);assert.equal(owned.length,policy.ownedDirectoriesIncludingRoot);
 assert.equal(build.schemaVersion,1);assert.equal(build.state,'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1');
 assert.equal(build.passed,true);assert.deepEqual(build.errors,[]);assert.equal(build.originalInputsPreserved,true);
 assert.equal(build.outputRoot,plan.applicationBuildOutputRoot);assert.equal(build.sourceOnlyPreparation,false);
 assert.deepEqual(build.applicationInventoryDescriptor,plan.applicationInputs);assert.deepEqual(build.applicationInventory,input);
 const versions={next:'16.4.5',react:'19.3.1','react-dom':'19.3.1'};
 assert.deepEqual(build.installedVersions,versions);assert.deepEqual(build.installedVersionsBeforeNextBuild,versions);
 const root=plan.applicationRootIdentity;
 assert.deepEqual(Object.keys(root).sort(),['dev','ino','mode','nlink']);
 for(const value of Object.values(root))assert(Number.isSafeInteger(value)&&value>=0);
 assert(root.ino>0&&root.nlink>0&&root.mode<=0o777);return true;
}
async function row(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
async function verify(r){assert(r&&typeof r.path==='string'&&resolve(r.path)===r.path);const s=await lstat(r.path);assert(s.isFile()&&!s.isSymbolicLink());assert.equal(await realpath(r.path),r.path);assert.deepEqual(await row(r.path),r);}
async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),rel=relative(root,path);if(s.isSymbolicLink())out.links.push(rel);else if(s.isDirectory()){out.dirs.push(rel);await visit(path);}else{assert(s.isFile());out.files.push(rel);}}}await visit(root);return out;}
async function family(ref){await verify(ref);const root=dirname(ref.path),j=await read(ref.path),names=j.files.map(x=>x.path),tree=await walk(root);assert.equal(new Set(names).size,names.length);assert.deepEqual(tree.files.filter(x=>x!=='index.json').sort(),[...names].sort());assert.deepEqual(tree.links,[]);for(const r of j.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));await verify({...r,path:join(root,r.path)});}}
const authpath=resolve(process.argv[2]),a=await read(authpath),authorityRef=await row(authpath),plan=await read(join(here,'plan.json'));
assert.equal(a.state,'ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1');assert.deepEqual(a.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(a.plan,await row(join(here,'plan.json')));
const extraRefs=[];
async function entrySelection(){await family(a.inputSourceIndex);await verify(a.inputEntry);const base=dirname(a.inputSourceIndex.path),rel=relative(base,a.inputEntry.path);assert(rel&&!rel.startsWith('../')&&!rel.startsWith('/'));const member=(await read(a.inputSourceIndex.path)).files.find(x=>x.path===rel);assert(member);assert.deepEqual({...member,path:join(base,rel)},a.inputEntry);}
async function protect(){await verify(authorityRef);await family(a.sourceIndex);await family(a.constructionCallerIndex);await entrySelection();for(const ref of plan.protectedSourceReferences)await verify(ref);for(const k of ['node','monitor'])await verify(plan[k]);for(const k of Object.keys(plan.expectedArtifacts))await verify(a[k]);for(const ref of [...a.engineBuildEvidence,...a.nativeProtectedInputs,...extraRefs])await verify(ref);for(const ref of a.nativeSourceFamilies)await family(ref);}
await protect();
const {validateAuthority,validateSelection,configuration,validateEffective,clean,evaluate,registrationFromLogs}=await import('./models.mjs');validateAuthority(a,plan);
const construction=await read(a.constructionResult.path),audit=await read(a.componentAudit.path);
extraRefs.push(construction.rootAuthority,construction.plan,...construction.artifacts.engineBuildEvidence);
for(const k of ['returnedImports','returnedOwnShape'])extraRefs.push(construction.artifacts[k]);
await protect();const ctor=await read(construction.rootAuthority.path),ctorPlan=await read(construction.plan.path);
validateSelection(construction,audit,await read(a.nativeMetadata.path),ctor,a,plan);
assert.equal(ctorPlan.worldName,'next-http');assert.deepEqual([...ctorPlan.selectedInterfaces].sort(),[...plan.selectedInterfaces].sort());
let worldIdentityBefore;
async function witBookend(){
 const ref=plan.worldFamily.sourceIndex,root=dirname(ref.path);assert.equal(ctorPlan.witDirectory,root);assert.deepEqual(ref,ctorPlan.worldSourceIndex);assert.equal(await realpath(root),root);await family(ref);
 const tree=await walk(root);assert.deepEqual(tree.links,[]);assert.deepEqual([...tree.dirs].sort(),plan.worldFamily.directories);
 assert.deepEqual(tree.files.filter(x=>x.endsWith('.wit')).sort(),plan.fixedWit.files.map(x=>x.path).sort());for(const r of plan.fixedWit.files)await verify({...r,path:join(root,r.path)});
 const identities=[];for(const name of [...tree.files,...tree.dirs].sort()){const path=join(root,name),s=await lstat(path);assert(!s.isSymbolicLink());assert.equal(await realpath(path),path);if(s.isFile())assert.equal(s.nlink,1);else assert(s.isDirectory());identities.push({relativePath:name,kind:s.isFile()?'file':'directory',mode:s.mode&0o777,dev:s.dev,ino:s.ino,nlink:s.nlink});}
 if(worldIdentityBefore===undefined)worldIdentityBefore=identities;else assert.deepEqual(identities,worldIdentityBefore);
}
await witBookend();
assert.deepEqual(construction.commands.map(x=>x.label),['componentize-init','component-validate','component-wit']);
for(const command of construction.commands){await verify(command.terminal);const t=await read(command.terminal.path);assert(clean(t));assert.deepEqual(t.authority,construction.rootAuthority);assert.equal(command.rawExitCode,0);assert.equal(command.clean,true);assert.deepEqual(t.stdout,command.stdout);assert.deepEqual(t.stderr,command.stderr);extraRefs.push(command.terminal,t.stdout,t.stderr);}
for(const k of ['validateTerminal','witTerminal']){await verify(audit[k]);const t=await read(audit[k].path);assert(clean(t));extraRefs.push(audit[k],t.stdout,t.stderr);}
assert.deepEqual(a.applicationInputs,plan.applicationInputs);assert.equal(a.applicationSource,plan.applicationSource);
const input=await read(a.applicationInputs.path),appBuild=await read(plan.applicationBuildResult.path);validateFreshInput(input,appBuild,plan);
async function sourceBookend(){
 assert.equal(await realpath(input.root),input.root);const rootStat=await lstat(input.root);assert(rootStat.isDirectory()&&!rootStat.isSymbolicLink());
 assert.deepEqual({dev:rootStat.dev,ino:rootStat.ino,mode:rootStat.mode&0o777,nlink:rootStat.nlink},plan.applicationRootIdentity);
 const tree=await walk(input.root);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),sourceDirectoryNames(input));
 for(const r of input.files){const path=join(input.root,r.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);assert.equal(s.nlink,1);}
 for(const r of input.directories){const path=join(input.root,r.path),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}
}
await sourceBookend();await protect();
process.umask(0o077);const output=resolve(plan.outputPrefix+'-'+a.runId);assert.equal(output,plan.outputPrefix+'-'+a.runId);await mkdir(output,{mode:0o700});
const app=join(output,'app'),cache=join(output,'cache'),project=join(output,'project');
const result={schemaVersion:1,state:'NEXT_WASMCLOUD_COLD_IN_PROGRESS_V1',runId:a.runId,rootAuthority:authorityRef,sourceIndex:a.sourceIndex,component:a.component,componentAudit:a.componentAudit,engine:a.engine,nativeMetadata:a.nativeMetadata,engineBuildEvidence:a.engineBuildEvidence,constructionResult:a.constructionResult,inputEntry:a.inputEntry,inputSourceIndex:a.inputSourceIndex,worldFamily:plan.worldFamily.sourceIndex,worldBefore:worldIdentityBefore,wash:a.wash,applicationInputs:a.applicationInputs,outputRoot:output,commands:[],responses:[],errors:[],server:null,originalInputsPreserved:false,readonlyAppPreserved:false,applicationBuildResult:plan.applicationBuildResult,applicationSchema:plan.applicationSchema,sourceRootIdentity:plan.applicationRootIdentity,ownedAdditionalDirectories:[],coldPolicySourceOnly:plan.coldPolicy,physicalInstanceIdentityObserved:false,cacheSequenceExecuted:false,browserExecuted:false,retainedContractAcceptance:false,fullNextAcceptance:false,adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const handles=[],children=[];let lease,host,stopping=false;
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function boundedWait(promise,ms){let timer;try{return await Promise.race([promise,new Promise(resolve=>{timer=setTimeout(()=>resolve(null),ms);})]);}finally{clearTimeout(timer);}}
async function launch(args,label){
 const stdout=join(output,label+'.stdout.log'),stderr=join(output,label+'.stderr.log'),out=await open(stdout,'wx',0o600),err=await open(stderr,'wx',0o600);handles.push(out,err);
 const env={...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')};
 const child=spawn(a.wash.path,args,{cwd:project,env,stdio:['ignore',out.fd,err.fd]});let status=null;
 const done=new Promise(resolve=>{child.once('error',e=>{status={code:null,signal:null,error:errorData(e)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});
 const item={child,done,get status(){return status;},record:{label,argv:[a.wash.path,...args],pid:child.pid??null,stdout,stderr,timeout:false,forcedCleanup:false,exit:null}};children.push(item);result.commands.push(item.record);await save();return item;
}
async function prepareReadonlyCopy(){
 await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:fsConstants.COPYFILE_FICLONE});
 // Independent direct-P2 preopens do not require a path in the copied app.
 // No additional directory is created in this owned copy.
 for(const r of input.files)await chmod(join(app,r.path),0o444);
 for(const name of ownedDirectoryNames(input,plan.applicationSchema).sort((a,b)=>b.length-a.length))await chmod(join(app,name),0o555);
}
async function readonlyBookend(){
 const tree=await walk(app);assert.deepEqual(tree.links,[]);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),ownedDirectoryNames(input,plan.applicationSchema));
 for(const r of input.files){const path=join(app,r.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,0o444);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
 for(const name of ownedDirectoryNames(input,plan.applicationSchema)){const path=join(app,name),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(s.mode&0o777,0o555);}
}
async function tcpReady(port){return new Promise(resolve=>{const socket=createConnection({host:'127.0.0.1',port});let settled=false;function finish(ok){if(settled)return;settled=true;socket.destroy();resolve(ok);}socket.once('connect',()=>finish(true));socket.once('error',()=>finish(false));socket.setTimeout(150,()=>finish(false));});}
async function capture(request,origin){
 const record={id:request.id,sourceFixtureId:request.sourceFixtureId,method:request.method??'GET',path:request.path,complete:false,chunks:[],shellChunk:-1,readyChunk:-1};result.responses.push(record);await save();
 const chunks=[],decoder=new TextDecoder('utf-8',{fatal:true});let text='',total=0,transportError=null;
 try{
  const response=await fetch(origin+request.path,{method:record.method,headers:request.headers,body:request.body,redirect:'manual',signal:AbortSignal.timeout(plan.requestMilliseconds)});record.status=response.status;record.headers=Object.fromEntries(response.headers);await save();
  for await(const part of response.body){const bytes=new Uint8Array(part);if(total+bytes.length>plan.maxResponseBytes){record.limitExceeded={capturedBytes:total,nextChunkBytes:bytes.length,limit:plan.maxResponseBytes};throw Error('Bounded response exceeds8MiB; subsequent bytes not retained');}const chunkIndex=record.chunks.length;chunks.push(bytes);total+=bytes.length;record.chunks.push({base64:Buffer.from(bytes).toString('base64'),bytes:bytes.length});await save();text+=decoder.decode(bytes,{stream:true});if(record.shellChunk<0&&text.includes('NEXT_STREAM_SHELL'))record.shellChunk=chunkIndex;if(record.readyChunk<0&&text.includes('NEXT_STREAM_READY'))record.readyChunk=chunkIndex;await save();}
  text+=decoder.decode();record.complete=true;
 }catch(error){transportError=errorData(error);record.transportError=transportError;}
 finally{
  const bytes=Buffer.concat(chunks,total),body=join(output,'responses',request.id+'.body'),chunkPath=join(output,'responses',request.id+'.chunks.json');await writeFile(body,bytes,{flag:'wx',mode:0o600});await writeFile(chunkPath,JSON.stringify(record.chunks,null,2)+'\n',{flag:'wx',mode:0o600});record.body=await row(body);record.chunkRecord=await row(chunkPath);record.bodyEncoding='fetch-decoded HTTP bytes; wire SHA unavailable';record.wireSha256=null;await save();
 }
 // Full/partial captured bytes precede all contract assertions.
 record.contract=evaluate(record,text,request);await save();if(transportError)throw Error('Captured transport failure at '+request.id+': '+transportError.message);return record;
}
try{
 // COPYFILE_FICLONE (not FORCE) uses Node's ordinary copy fallback. Verify every byte/inode.
 await prepareReadonlyCopy();
 await readonlyBookend();await mkdir(cache,{mode:0o700});assert.equal((await lstat(cache)).mode&0o777,0o700);const cacheStat=await lstat(cache);assert(cacheStat.isDirectory()&&!cacheStat.isSymbolicLink());assert.equal(await realpath(cache),cache);
 await mkdir(join(project,'.wash'),{recursive:true,mode:0o700});await mkdir(join(output,'responses'),{mode:0o700});
 result.applicationCopy={files:input.regularFiles,bytes:input.bytes,sourceDirectoriesExcludingRoot:input.directories.length,ownedDirectoriesIncludingRoot:plan.applicationSchema.ownedDirectoriesIncludingRoot,ownedAdditionalDirectories:[],byteIdentical:true,independentInodes:true,filesMode:'0444',directoryMode:'0555'};result.mounts=[{host:app,guest:'/app'},{host:cache,guest:'/app/.next/cache',physicalRootMode:'0700'}];result.readonlyWasiDescriptorRightsProved=false;await save();
 lease=createServer();lease.on('error',()=>{});await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;result.portLease={origin,port:address.port,heldThroughConfigInspection:true,singleAttempt:true,fallbackAllowed:false};
 const configured=configuration(a.component.path,app,cache,origin),configPath=join(project,'.wash/config.json'),empty=join(output,'empty-user-config.json');await writeFile(configPath,JSON.stringify(configured,null,2)+'\n',{flag:'wx',mode:0o600});await writeFile(empty,'{}\n',{flag:'wx',mode:0o600});const configRefs=[await row(configPath),await row(empty)];extraRefs.push(...configRefs);result.configured=configured;result.configFiles=configRefs;await save();
 await protect();await sourceBookend();await witBookend();
 const show=await launch(['--user-config',empty,'-C',project,'--output','json','config','show'],'config-show');if(await boundedWait(show.done,plan.configSeconds*1000)===null){show.record.timeout=true;show.child.kill('SIGTERM');if(await boundedWait(show.done,1000)===null){show.record.forcedCleanup=true;show.child.kill('SIGKILL');await boundedWait(show.done,1000);}}show.record.exit=show.status;show.record.stdout=await row(show.record.stdout);show.record.stderr=await row(show.record.stderr);await save();assert.equal(show.record.timeout,false);assert.deepEqual(show.status,{code:0,signal:null,error:null});const shown=await read(show.record.stdout.path);assert.equal(shown.success,true);validateEffective(shown.data,configured);result.effectiveConfiguration=shown.data;result.configVerifiedBeforeDev=true;await save();
 await protect();await sourceBookend();await witBookend();await new Promise((resolve,reject)=>lease.close(error=>error?reject(error):resolve()));lease=null;result.portLease.releasedImmediatelyBeforeSingleDevLaunch=true;await save();
 host=await launch(['--user-config',empty,'-C',project,'--log-level','info','--meters','duration','dev'],'wash-dev');result.server=host.record;void host.done.then(status=>{if(!stopping)result.errors.push({stage:'server-exited-before-owned-shutdown',status});});await save();
 const deadline=Date.now()+plan.listenerSeconds*1000;let ready=false;result.readiness={tcpConnect:false,workloadRegistered:false,extraHttpRequests:0,origin,polls:0,source:plan.readinessPolicy.sourceFile,completionEvents:[]};await save();
 while(Date.now()<deadline){
  assert.equal(host.status,null,'wash exited before workload-registration readiness');const logs={},sizes={};
  for(const stream of ['stdout','stderr']){const path=host.record[stream],s=await lstat(path);assert(s.size<=8388608,'Readiness log exceeds8MiB; raw file retained');logs[stream]=await readFile(path,'utf8');sizes[stream]=s.size;}
  const registered=registrationFromLogs(logs,origin);result.readiness.polls++;result.readiness.lastLogSizes=sizes;result.readiness.workloadRegistered=registered.registered;result.readiness.completionEvents=registered.events;result.readiness.matchingMessageLines=registered.messageLines;
  if(registered.registered&&await tcpReady(address.port)){result.readiness.tcpConnect=true;ready=true;await save();break;}await save();await pause(50);
 }
 assert(ready,'Exact post-registration marker AND TCP listener unavailable within60s');
 const contract=await read(join(here,'cold-contract.json'));assert.equal(contract.requests.length,8);for(const request of contract.requests){assert.equal(host.status,null,'wash exited during cold controls');await capture(request,origin);}
 result.eightCaptured=result.responses.length===8&&result.responses.every(x=>x.complete===true);result.contractsPassed=result.eightCaptured&&result.responses.every(x=>x.contract.passed===true);result.selected13InstantiationDemonstrated=result.contractsPassed===true;await save();
}catch(error){result.errors.push({stage:'cold-deployment-or-contracts',...errorData(error)});}
finally{
 if(lease?.listening)await new Promise(resolve=>lease.close(()=>resolve()));
 if(host&&!host.status){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.child.kill('SIGINT');if(await boundedWait(host.done,plan.gracefulStopMilliseconds)===null){result.server.forcedCleanup=true;host.child.kill('SIGKILL');await boundedWait(host.done,plan.gracefulStopMilliseconds);}}
 for(const child of children){if(!child.status){child.record.forcedCleanup=true;child.child.kill('SIGKILL');await boundedWait(child.done,1000);}child.record.exit=child.status;for(const k of ['stdout','stderr'])if(typeof child.record[k]==='string')child.record[k]=await row(child.record[k]);}
 for(const handle of handles)try{await handle.close();}catch(error){result.errors.push({stage:'raw-stream-close',...errorData(error)});}
 try{await sourceBookend();await protect();await witBookend();result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...errorData(error)});}
 try{await readonlyBookend();result.readonlyAppPreserved=true;}catch(error){result.errors.push({stage:'final-readonly-app',...errorData(error)});}
 result.cacheInventory=[];try{assert.equal((await lstat(cache)).mode&0o777,0o700);const tree=await walk(cache);assert.deepEqual(tree.links,[]);for(const name of tree.files){const path=join(cache,name);result.cacheInventory.push({...await row(path),relativePath:name,mode:(await lstat(path)).mode&0o777});}}catch(error){result.errors.push({stage:'final-cache-inventory',...errorData(error)});}
 result.allDirectCliExitsZero=children.length===2&&children.every(c=>c.record.timeout===false&&c.record.forcedCleanup===false&&c.status?.code===0&&c.status?.signal===null&&c.status?.error===null);
 result.passed=result.contractsPassed===true&&result.configVerifiedBeforeDev===true&&result.errors.length===0&&result.originalInputsPreserved&&result.readonlyAppPreserved&&result.allDirectCliExitsZero&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true;
 result.state=result.passed?'NEXT_WASMCLOUD_EIGHT_COLD_REQUESTS_PASSED_UNREVIEWED_V1':'NEXT_WASMCLOUD_COLD_FAILED_UNACCEPTED_V1';await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,responses:result.responses.length,passedRequests:result.responses.filter(x=>x.contract?.passed===true).length,errors:result.errors,retainedContractAcceptance:false,fullNextAcceptance:false,adoption:false}));process.exitCode=result.passed?0:1;
