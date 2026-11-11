// Dormant actual WT deployment orchestration, permitted only by late Root authority.
// Builtins only; neither generated guest modules nor packaging APIs are imported.
import assert from 'node:assert/strict';
import {admitNextRuntime} from './admit-next.mjs';
import {captureRawStdout} from './capture-stdout.mjs';
import {validatePublicCorrelation,writePublicCorrelationManifest} from './public-correlation.mjs';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {createReadStream,constants as fsConstants} from 'node:fs';
import {readFile,writeFile,mkdir,cp,chmod,lstat,readdir,realpath,open} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const read=async p=>JSON.parse(await readFile(p,'utf8'));
async function row(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
async function verify(r){assert.deepEqual(await row(r.path),r);}
async function family(ref){await verify(ref);const root=dirname(ref.path),j=await read(ref.path),names=j.files.map(x=>x.path);assert.equal(new Set(names).size,names.length);const actual=await walk(root);assert.deepEqual(actual.files.filter(x=>x!=='index.json').sort(),[...names].sort());assert.equal(actual.links.length,0);for(const r of j.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));await verify({...r,path:join(root,r.path)});}}
async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),r=relative(root,path);if(s.isSymbolicLink())out.links.push(r);else if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile(),'Only regular files/directories');out.files.push(r);}}}await visit(root);return out;}
const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),stack:e?.stack??null});
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
 assert.deepEqual(policy.additionalDirectories,['.next/cache']);
 const names=sourceDirectoryNames(input);assert(names.includes('.next'));assert(!names.includes('.next/cache'));
 assert(!input.files.some(x=>x.path==='.next/cache'||x.path.startsWith('.next/cache/')));
 return [...names,'.next/cache'].sort();
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
const plan=await read(join(here,'wasmtime-plan.json'));
assert.equal(plan.bindingState,'READY_CLONE_CANCEL_NEXT_FULL','Unbound Source: no authority input, output or actor');
for(const key of ['clientSource','browserSource','clientSourceIndex','browserSourceIndex','expectedComponent'])assert(plan[key]!==null,'Missing reviewed binding:'+key);
assert.equal(plan.newComponentBindingsPending,false,'Actual new construction/composition bindings pending');
assert.equal(plan.hostToolRevalidationPending,false,'Current browser/runtime tool revalidation pending');
assert(Array.isArray(plan.protectedInputs)&&plan.protectedInputs.length>0,'Fresh Root protection graph required');
assert.equal(plan.controlOnly,false);assert.equal(plan.prospectiveFullClientBindingsPending,false,'New app/client DATA pending');
assert.equal(plan.fullClientFullContract.clientSourcePending,false,'New full client Source pending');
assert(plan.fullClientFullContract.requiredClientIndex&&plan.fullClientFullContract.requiredClient);
assert.deepEqual(plan.clientSourceIndex,plan.fullClientFullContract.requiredClientIndex);
assert.deepEqual(plan.clientSource,plan.fullClientFullContract.requiredClient);
for(const key of ['outputPrefix','applicationSource','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','applicationSchema','clientSource','clientSourceIndex','browserSource','browserSourceIndex'])assert(plan[key]!==null,'New control binding:'+key);
const authorityPath=resolve(process.argv[2]),authority=await read(authorityPath);
assert.equal(authority.state,'ROOT_CLONE_CANCEL_NEXT_FULL_WASMTIME_AUTHORIZED_V1');
assert.equal(authority.publicRequestCorrelationAllowed,true);
assert.equal(authority.standardHandlerObserverAllowed,true);
assert.equal(authority.fullClientFullContractAllowed,true);assert.equal(authority.rscStreamObserverAllowed,true);assert.equal(authority.controlOnly,false);
validatePublicCorrelation(authority.publicRequestCorrelation);
assert.deepEqual(authority.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(authority.plan,await row(join(here,'wasmtime-plan.json')));
for(const key of ['localhostServeAllowed','actualNextGuestAllowed','browserAllowed'])assert.equal(authority[key],true);
for(const key of ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed'])assert.equal(authority[key],false);
assert(typeof authority.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(authority.runId)?.[0]===authority.runId,'Mandatory safe fresh runId');
for(const key of ['constructionCallerIndex','inputSourceIndex','inputEntry']){const ref=authority[key];assert(ref&&typeof ref.path==='string'&&/^[a-f0-9]{64}$/.test(ref.sha256)&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0,'Exact late Root descriptor required:'+key);assert.equal(resolve(ref.path),ref.path);assert.equal(await realpath(ref.path),ref.path);if(key!=='inputEntry')assert.equal(ref.path.split('/').at(-1),'index.json');}
async function entrySelection(){await family(authority.inputSourceIndex);await verify(authority.inputEntry);const base=dirname(authority.inputSourceIndex.path),rel=relative(base,authority.inputEntry.path);assert(rel&&!rel.startsWith('../')&&!rel.startsWith('/'));const members=(await read(authority.inputSourceIndex.path)).files,member=members.find(r=>r.path===rel);assert(member,'Selected real-next entry must be indexed in selected Source family');assert.deepEqual({...member,path:join(base,member.path)},authority.inputEntry);}
async function protect(){await family(authority.sourceIndex);await family(authority.constructionCallerIndex);await entrySelection();for(const ref of plan.sourceFamilies)await family(ref);await family(plan.clientSourceIndex);await family(plan.browserSourceIndex);for(const r of [...plan.protectedInputs,plan.clientSource,plan.browserSource])await verify(r);}
await protect();
const runtimeAdmission=await admitNextRuntime({plan,authority,kind:'wasmtime'});
const {constructionReview,artifactRefs,artifactBookend,witBookend}=runtimeAdmission;
await artifactBookend();await witBookend();

await verify(plan.applicationInputs);await verify(plan.applicationBuildResult);
const input=await read(plan.applicationInputs.path),appBuild=await read(plan.applicationBuildResult.path);
await verify(plan.applicationBuildReview);await verify(plan.applicationRootIdentityEvidence);
const newAppReview=await read(plan.applicationBuildReview.path);
assert.equal(newAppReview.state,'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1');assert.equal(newAppReview.verifiedPassed,true);
assert.deepEqual(newAppReview.actualResult,plan.applicationBuildResult);assert.deepEqual(newAppReview.applicationInputs,plan.applicationInputs);
assert.deepEqual(newAppReview.applicationRootIdentityEvidence,plan.applicationRootIdentityEvidence);assert.equal(newAppReview.applicationRoot,plan.applicationSource);
artifactRefs.push(plan.applicationBuildReview,plan.applicationRootIdentityEvidence);
validateFreshInput(input,appBuild,plan);
async function sourceBookend(){
 assert.equal(await realpath(input.root),input.root);const rootStat=await lstat(input.root);assert(rootStat.isDirectory()&&!rootStat.isSymbolicLink());
 assert.deepEqual({dev:rootStat.dev,ino:rootStat.ino,mode:rootStat.mode&0o777,nlink:rootStat.nlink},plan.applicationRootIdentity);
 const tree=await walk(input.root);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),sourceDirectoryNames(input));
 for(const r of input.files){const path=join(input.root,r.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);assert.equal(s.nlink,1);}
 for(const r of input.directories){const path=join(input.root,r.path),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}
}
await sourceBookend();
const output=resolve(plan.outputPrefix+'-'+authority.runId);assert.equal(output,plan.outputPrefix+'-'+authority.runId);const app=join(output,'app'),cache=join(output,'cache');await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'CLONE_CANCEL_NEXT_FULL_WASMTIME_PROFILE_IN_PROGRESS_V1',controlOnly:false,fullOriginalContractExecuted:false,fullNextAccepted:false,runId:authority.runId,outputRoot:output,inputEntry:authority.inputEntry,inputSourceIndex:authority.inputSourceIndex,component:authority.component,constructionReview:authority.constructionReview,engineAdmission:authority.engineAdmission,constructionRequest:authority.constructionRequest,constructionResult:authority.constructionResult,servedEnvelope:authority.envelope,servedEnvelopeCompositionReview:authority.compositionReview,standardHandlerObserverMarkersInterpreted:false,rootAuthority:await row(authorityPath),sourceIndex:authority.sourceIndex,selectedInterfaces:plan.selectedInterfaces,emittedImports:constructionReview.emittedImports,errors:[],server:null,client:null,originalInputsPreserved:false,readonlyAppPreserved:false,applicationBuildResult:plan.applicationBuildResult,applicationInputs:plan.applicationInputs,applicationSchema:plan.applicationSchema,sourceRootIdentity:plan.applicationRootIdentity,ownedAdditionalDirectories:[],adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function boundedWait(promise,ms){let timer;try{await Promise.race([promise,new Promise(resolve=>{timer=setTimeout(resolve,ms);})]);}finally{clearTimeout(timer);}}
const handles=[];let host,hostExit=null,hostDone,stopping=false,lease,hostCapture,hostCaptureOutcome,clientProcess;
async function launch(exe,args,id){
 const stdout=join(output,id+'.stdout.log'),stderr=join(output,id+'.stderr.log');
 const out=await open(stdout,'wx',0o600);handles.push(out);
 const err=await open(stderr,'wx',0o600),pipeStdout=id==='wasmtime';handles.push(err);
 const child=spawn(exe,args,{cwd:output,stdio:['ignore',pipeStdout?'pipe':out.fd,err.fd],env:{...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}});
 let status=null;const done=new Promise(resolve=>{child.once('error',error=>{status={code:null,signal:null,error:errorData(error)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});
 const capture=pipeStdout?captureRawStdout({readable:child.stdout,handle:out,path:stdout,limitBytes:8388608}):null;
 if(pipeStdout)handles.splice(handles.indexOf(out),1); // Only the pipe writer now owns this file handle.
 return{child,done,stdout,stderr,capture,get status(){return status;},command:[exe,...args]};
}
async function prepareReadonlyCopy(){
 await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:fsConstants.COPYFILE_FICLONE});
 // This empty mountpoint belongs ONLY to the owned copy, never the Source inventory.
 await mkdir(join(app,'.next/cache'),{mode:0o700});assert.deepEqual(await readdir(join(app,'.next/cache')),[]);
 for(const r of input.files)await chmod(join(app,r.path),0o444);
 for(const name of ownedDirectoryNames(input,plan.applicationSchema).sort((a,b)=>b.length-a.length))await chmod(join(app,name),0o555);
}
async function readonlyBookend(){
 const tree=await walk(app);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),ownedDirectoryNames(input,plan.applicationSchema));
 for(const r of input.files){const path=join(app,r.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,0o444);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
 for(const name of ownedDirectoryNames(input,plan.applicationSchema)){const path=join(app,name),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(s.mode&0o777,0o555);}
 assert.deepEqual(await readdir(join(app,'.next/cache')),[]);
}
try{
 await prepareReadonlyCopy();
 await readonlyBookend();await mkdir(cache,{mode:0o700});assert.equal((await lstat(cache)).mode&0o777,0o700);
 assert((await lstat(join(app,'.next/cache'))).isDirectory(),'Readonly parent/cache path must physically exist');
 result.mounts=[{host:app,guest:'/app',physicalDirectoryMode:'0555',physicalFileMode:'0444'},{host:cache,guest:'/app/.next/cache',physicalRootMode:'0700'}];result.applicationCopy={files:input.regularFiles,bytes:input.bytes,sourceDirectoriesExcludingRoot:input.directories.length,ownedDirectoriesIncludingRoot:plan.applicationSchema.ownedDirectoriesIncludingRoot,byteIdentical:true,independentInodes:true};result.ownedAdditionalDirectories=[{path:'.next/cache',sourceInventoryMember:false,empty:true,mode:0o555,purpose:'underlying mountpoint for separately writable cache preopen'}];
 lease=createServer();lease.on('error',()=>{});await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');
 const origin='http://127.0.0.1:'+address.port;result.portLease={address:address.address,port:address.port,origin,heldUntilImmediatelyBeforeSingleLaunch:true,fallbackAllowed:false};await save();
 const args=['serve','--no-logging-prefix','--addr',address.address+':'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--env','STARLING_NEXT_ORIGIN='+origin,'--env','NODE_ENV=production','--env','NEXT_TELEMETRY_DISABLED=1','--dir',app+'::/app','--dir',cache+'::/app/.next/cache','--max-instance-reuse-count','128','--idle-instance-timeout','60s',authority.envelope.path];
 await protect();await artifactBookend();await witBookend();
 await new Promise((resolve,reject)=>lease.close(error=>error?reject(error):resolve()));lease=null;result.portLease.releasedBeforeSpawn=true;
 const server=await launch(plan.wasmtime.path,args,'wasmtime');host=server.child;hostDone=server.done;hostCapture=server.capture;
 void hostCapture.done.then(value=>{hostCaptureOutcome=value;},error=>{result.errors.push({stage:'stdout-capture-unexpected-rejection',...errorData(error)});});void hostDone.then(status=>{hostExit=status;if(!stopping)result.errors.push({stage:'server-exited-before-owned-shutdown',status});});result.server={command:server.command,pid:host.pid??null,stdout:server.stdout,stderr:server.stderr,plannedGracefulStop:'SIGINT',forcedCleanup:false};await save();
 const deadline=Date.now()+60000;let ready=false;
 while(Date.now()<deadline){if(hostCapture.failed)throw Error('Wasmtime stdout capture failed during readiness');if(hostExit)throw Error('Wasmtime exited before readiness');let logs='';for(const path of [server.stdout,server.stderr]){const s=await lstat(path);assert(s.size<=8388608,'Readiness log exceeds8MiB; raw file retained');const text=await readFile(path,'utf8');logs+=text.slice(0,text.lastIndexOf('\n')+1);}const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs)?.[1];if(found){assert.equal(found,origin,'Port lease race/origin mismatch: never fallback');ready=true;break;}await pause(50);}
 assert(ready,'Wasmtime did not report exact listener within60s');result.server.readyOrigin=origin;await save();
 result.publicRequestCorrelation=await writePublicCorrelationManifest({block:authority.publicRequestCorrelation,runId:authority.runId,origin,output});
 artifactRefs.push(result.publicRequestCorrelation.manifest);await artifactBookend();await save();
 const client=await launch(plan.node.path,[plan.clientSource.path,origin,join(output,'client'),plan.browserTools,authority.runId],'client');clientProcess=client;result.client={command:client.command,pid:client.child.pid??null,stdout:client.stdout,stderr:client.stderr};await save();const status=await Promise.race([client.done,hostCapture.failure.then(failure=>{throw Error('Wasmtime raw stdout capture failed: '+failure.stage);})]);result.client.exit=status;result.client.result=await row(join(output,'client/result.json'));const observed=await read(result.client.result.path);assert.equal(typeof observed.fullOriginalContractExecuted,'boolean');result.fullOriginalContractExecuted=observed.fullOriginalContractExecuted;assert.equal(observed.suite,'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1');assert.equal(observed.controlOnly,false);assert.equal(observed.fullOriginalContractExecuted,true);assert.equal(observed.fullNextAccepted,false);assert.deepEqual(status,{code:0,signal:null,error:null});assert.equal(observed.passed,true);assert.equal(hostExit,null,'Server must remain live through full contracts');result.controlPassed=true;
}catch(error){result.errors.push({stage:'deployment-or-control',...errorData(error)});}
finally{
 if(lease)await new Promise(resolve=>lease.close(()=>resolve()));
 if(host&&!hostExit){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.kill('SIGINT');await boundedWait(hostDone,5000);if(!hostExit){result.server.forcedCleanup=true;result.server.sigkillSent=host.kill('SIGKILL');await boundedWait(hostDone,5000);}}
 // A capture failure can leave the original client pending. Stop only its actual child handle;
 // the unchanged external600-second monitor retains original session/group authority.
 if(clientProcess&&clientProcess.status===null){
  result.client.shutdownRequested=true;result.client.sigtermSent=clientProcess.child.kill('SIGTERM');
  await boundedWait(clientProcess.done,5000);
  if(clientProcess.status===null){result.client.forcedCleanup=true;result.client.sigkillSent=clientProcess.child.kill('SIGKILL');await boundedWait(clientProcess.done,5000);}
 }
 if(result.client&&clientProcess)result.client.exit=clientProcess.status;
 if(hostCapture){
  try{
   await boundedWait(hostCapture.done,5000);
   if(hostCaptureOutcome===undefined){hostCapture.abort('stdout-join-timeout');await boundedWait(hostCapture.done,5000);}
  }catch(error){result.errors.push({stage:'stdout-join',...errorData(error)});}
  if(hostCaptureOutcome===undefined)result.errors.push({stage:'stdout-finalization',message:'Capture writer/pipe did not finalize; no stdout digest or marker interpretation permitted'});
  else{
   result.server.stdoutCapture=hostCaptureOutcome;
   if(!hostCaptureOutcome.complete)result.errors.push({stage:'stdout-capture-incomplete',capture:hostCaptureOutcome});
  }
 }
 if(result.server){
  result.server.exit=hostExit;result.server.stderr=await row(result.server.stderr);
  if(hostExit!==null&&hostCaptureOutcome?.finalized){
   try{
    const raw=await row(result.server.stdout);assert.equal(raw.bytes,hostCaptureOutcome.fileBytes);assert(raw.bytes<=8388608);
    result.server.stdout=raw;result.server.stdoutCaptureScope=hostCaptureOutcome.complete?'complete raw stream':'failed incomplete accepted prefix; unretained tail unknown';
   }catch(error){result.server.stdoutDigestUnavailable=true;result.errors.push({stage:'stdout-publication',...errorData(error)});}
  }else result.server.stdoutDigestUnavailable=true;
 }
 if(result.client){
  if(result.client.shutdownRequested===true||clientProcess.status===null||![0,1].includes(clientProcess.status.code)||clientProcess.status.signal!==null||clientProcess.status.error!==null){
   // Reaping this child does not prove its inherited browser-descendant file descriptors closed.
   result.client.rawStreamDigestsUnavailable=true;
   result.client.rawStreamFinalization='Interrupted client: descendant quiescence delegated to the unchanged original600-second monitor; raw paths retained without final digests';
  }else if(clientProcess.status!==null)for(const k of ['stdout','stderr'])result.client[k]=await row(result.client[k]);
  else{result.client.rawStreamDigestsUnavailable=true;result.errors.push({stage:'client-reap',message:'Client still live; no final raw stream digest claim'});}
 }
 for(const handle of handles)try{await handle.close();}catch(error){result.errors.push({stage:'raw-stream-close',...errorData(error)});}
 try{await sourceBookend();await protect();await artifactBookend();await witBookend();result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'source-final-protection',...errorData(error)});}
 try{await readonlyBookend();result.readonlyAppPreserved=true;}catch(error){result.errors.push({stage:'readonly-app-final',...errorData(error)});}
 result.cacheInventory=[];try{const tree=await walk(cache);assert.equal(tree.links.length,0);for(const name of tree.files){const path=join(cache,name);result.cacheInventory.push({...await row(path),relativePath:name,mode:(await lstat(path)).mode&0o777});}}catch(error){result.errors.push({stage:'cache-final-inventory',...errorData(error)});}
 result.passed=hostCaptureOutcome?.complete===true&&result.controlPassed===true&&result.errors.length===0&&result.originalInputsPreserved&&result.readonlyAppPreserved&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&hostExit?.code===0&&hostExit?.signal===null&&hostExit?.error===null;
 result.state=result.passed?'CLONE_CANCEL_NEXT_FULL_WASMTIME_PROFILE_PASSED_UNREVIEWED_V1':'CLONE_CANCEL_NEXT_FULL_WASMTIME_PROFILE_FAILED_RAW_PRESERVED_V1';await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,errors:result.errors}));process.exitCode=result.passed?0:1;
