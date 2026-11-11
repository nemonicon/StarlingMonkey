// Dormant stock wasmCloud full-contract actor; late Root authority is mandatory.
// Builtins only; neither generated guest modules nor packaging APIs are imported.
import assert from 'node:assert/strict';
import {admitNextRuntime} from './admit-next.mjs';
import {captureRawStdout} from './capture-stdout.mjs';
import {configuration,validateEffective,registrationFromLogs} from './models.mjs';
import {validatePublicCorrelation,writePublicCorrelationManifest} from './public-correlation.mjs';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer,createConnection} from 'node:net';
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
const plan=await read(join(here,'plan.json'));
assert.equal(plan.bindingState,'READY_DISCONNECT_RECOVERY_PROBE','Unbound Source: no authority input, output or actor');
for(const key of ['clientSource','browserSource','clientSourceIndex','browserSourceIndex','expectedComponent'])assert(plan[key]!==null,'Missing reviewed binding:'+key);
assert.equal(plan.newComponentBindingsPending,false,'Actual new construction/composition bindings pending');
assert.equal(plan.hostToolRevalidationPending,false,'Current browser/runtime tool revalidation pending');
assert(Array.isArray(plan.protectedInputs)&&plan.protectedInputs.length>0,'Fresh Root protection graph required');
assert.equal(plan.controlOnly,true);assert.equal(plan.prospectiveProbeBindingsPending,false,'New app/client DATA pending');
assert.equal(plan.disconnectRecoveryClient.clientSourcePending,false,'New full client Source pending');
assert(plan.disconnectRecoveryClient.requiredClientIndex&&plan.disconnectRecoveryClient.requiredClient);
assert.deepEqual(plan.clientSourceIndex,plan.disconnectRecoveryClient.requiredClientIndex);
assert.deepEqual(plan.clientSource,plan.disconnectRecoveryClient.requiredClient);
for(const key of ['outputPrefix','applicationSource','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','applicationSchema','clientSource','clientSourceIndex','browserSource','browserSourceIndex'])assert(plan[key]!==null,'New control binding:'+key);
const authorityPath=resolve(process.argv[2]),authority=await read(authorityPath),authorityRef=await row(authorityPath);
assert.equal(authority.state,'ROOT_NEXT_DISCONNECT_RECOVERY_CLOUD_AUTHORIZED_V1');
assert.equal(authority.publicRequestCorrelationAllowed,true);
assert.equal(authority.standardHandlerObserverAllowed,true);
assert.equal(authority.disconnectRecoveryProbeAllowed,true);assert.equal(authority.rscStreamObserverAllowed,false);assert.equal(authority.controlOnly,true);
for(const key of ['stockHostAllowed','configInspectAllowed','guestEnvironmentAllowed','outgoingHttpWorkloadSelected'])assert.equal(authority[key],true);
for(const key of ['hostMutationAllowed','automaticRetryAllowed','newServicesAllowed'])assert.equal(authority[key],false);
const selectedOrigin=new URL(authority.selfOrigin);assert.equal(authority.selfOrigin,selectedOrigin.origin);assert.equal(selectedOrigin.protocol,'http:');assert.equal(selectedOrigin.hostname,'127.0.0.1');assert.equal(selectedOrigin.username,'');assert.equal(selectedOrigin.password,'');assert(Number.isInteger(Number(selectedOrigin.port))&&Number(selectedOrigin.port)>0&&Number(selectedOrigin.port)<=65535);
assert.equal(authority.runId,plan.namespacePolicy.plannedRunId);assert.equal(plan.outputPrefix,plan.namespacePolicy.plannedOutputPrefix);
for(const key of ['node','monitor','wash'])await verify(plan[key]);
assert.deepEqual(await row(process.execPath),plan.node);
validatePublicCorrelation(authority.publicRequestCorrelation);
assert.deepEqual(authority.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(authority.plan,await row(join(here,'plan.json')));
for(const key of ['localhostServeAllowed','actualNextGuestAllowed'])assert.equal(authority[key],true);assert.equal(authority.browserAllowed,false);
for(const key of ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed'])assert.equal(authority[key],false);
assert(typeof authority.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(authority.runId)?.[0]===authority.runId,'Mandatory safe fresh runId');
for(const key of ['constructionCallerIndex','inputSourceIndex','inputEntry']){const ref=authority[key];assert(ref&&typeof ref.path==='string'&&/^[a-f0-9]{64}$/.test(ref.sha256)&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0,'Exact late Root descriptor required:'+key);assert.equal(resolve(ref.path),ref.path);assert.equal(await realpath(ref.path),ref.path);if(key!=='inputEntry')assert.equal(ref.path.split('/').at(-1),'index.json');}
async function entrySelection(){await family(authority.inputSourceIndex);await verify(authority.inputEntry);const base=dirname(authority.inputSourceIndex.path),rel=relative(base,authority.inputEntry.path);assert(rel&&!rel.startsWith('../')&&!rel.startsWith('/'));const members=(await read(authority.inputSourceIndex.path)).files,member=members.find(r=>r.path===rel);assert(member,'Selected real-next entry must be indexed in selected Source family');assert.deepEqual({...member,path:join(base,member.path)},authority.inputEntry);}
async function protect(){await verify(authorityRef);for(const key of ['node','monitor','wash'])await verify(plan[key]);await family(authority.sourceIndex);await family(authority.constructionCallerIndex);await entrySelection();for(const ref of plan.sourceFamilies)await family(ref);await family(plan.clientSourceIndex);await family(plan.browserSourceIndex);for(const r of [...plan.protectedInputs,plan.clientSource,plan.browserSource])await verify(r);}
await protect();
const runtimeAdmission=await admitNextRuntime({plan,authority,kind:'cloud'});
const {constructionReview,artifactRefs,artifactBookend,witBookend}=runtimeAdmission;
await artifactBookend();await witBookend();

await verify(plan.applicationInputs);await verify(plan.applicationBuildResult);
const input=await read(plan.applicationInputs.path),appBuild=await read(plan.applicationBuildResult.path);
await verify(plan.applicationBuildReview);await verify(plan.applicationRootIdentityEvidence);
const newAppReview=await read(plan.applicationBuildReview.path);
assert.equal(newAppReview.state,'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1');assert.equal(newAppReview.verifiedPassed,true);
assert.equal(newAppReview.buildVersion,1);for(const key of ['sourceCacheAbsent','runtimeCacheMountPolicyCompatible','configuredCompressFalseVerified','effectiveStandaloneConfigCompressFalseVerified'])assert.equal(newAppReview[key],true);
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
const output=resolve(plan.outputPrefix+'-'+authority.runId);assert.equal(output,plan.outputPrefix+'-'+authority.runId);const app=join(output,'app'),cache=join(output,'cache'),project=join(output,'project');await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'NEXT_DISCONNECT_RECOVERY_CLOUD_PROFILE_IN_PROGRESS_V1',controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,probeExecuted:false,probeCollectionComplete:false,probeCleanupComplete:false,browserInvoked:false,runId:authority.runId,outputRoot:output,inputEntry:authority.inputEntry,inputSourceIndex:authority.inputSourceIndex,component:authority.component,constructionReview:authority.constructionReview,engineAdmission:authority.engineAdmission,constructionRequest:authority.constructionRequest,constructionResult:authority.constructionResult,servedEnvelope:authority.envelope,servedEnvelopeCompositionReview:authority.compositionReview,standardHandlerObserverMarkersInterpreted:false,rootAuthority:authorityRef,sourceIndex:authority.sourceIndex,selectedInterfaces:plan.selectedInterfaces,emittedImports:constructionReview.emittedImports,errors:[],server:null,client:null,originalInputsPreserved:false,readonlyAppPreserved:false,applicationBuildResult:plan.applicationBuildResult,applicationInputs:plan.applicationInputs,applicationSchema:plan.applicationSchema,sourceRootIdentity:plan.applicationRootIdentity,ownedAdditionalDirectories:[],adoption:false,actualHost:'stock-wasmCloud-2.11.0',wash:plan.wash,commands:[],configVerifiedBeforeDev:false,readiness:null};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const pause=ms=>new Promise(yes=>setTimeout(yes,ms));const children=[];let host=null,status=null,clientProcess=null,lease=null,stopping=false;
async function prepareReadonlyCopy(){
 await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:fsConstants.COPYFILE_FICLONE});
 // Independent direct-P2 app/cache preopens require no extra directory in the app copy.
 for(const r of input.files)await chmod(join(app,r.path),0o444);
 for(const name of ownedDirectoryNames(input,plan.applicationSchema).sort((a,b)=>b.length-a.length))await chmod(join(app,name),0o555);
}
async function readonlyBookend(){
 const tree=await walk(app);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),ownedDirectoryNames(input,plan.applicationSchema));
 for(const r of input.files){const path=join(app,r.path),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,0o444);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
 for(const name of ownedDirectoryNames(input,plan.applicationSchema)){const path=join(app,name),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(s.mode&0o777,0o555);}
}
 async function stopItem(item,reason){
  if(!item)return;if(item.stopPromise)return item.stopPromise;
  item.stopPromise=(async()=>{item.record.shutdownReason=reason;item.record.shutdownRequested=true;
   if(item.status===null){item.record.sigintSent=item.child.kill('SIGINT');try{await bounded(item.done,plan.normalStopSeconds*1000,'Normal stock child stop deadline');}catch{item.record.forcedCleanup=true;item.child.kill('SIGKILL');await bounded(item.done,plan.forcedStopSeconds*1000,'Forced stock child stop deadline');}}
  })();return item.stopPromise;
 }
 async function stopHost(reason){return stopItem(host,reason);}
 async function launchWash(args,label){
  const stdout=join(output,label+'.stdout.log'),stderr=join(output,label+'.stderr.log');
  const out=await open(stdout,'wx',0o600);let err;try{err=await open(stderr,'wx',0o600);}catch(error){await out.close();throw error;}
  const env={PATH:'/usr/bin:/bin',LANG:'C',LC_ALL:'C',XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')};
  for(const key of ['HOME','USER','LOGNAME'])if(typeof process.env[key]==='string')env[key]=process.env[key];
  const child=spawn(plan.wash.path,args,{cwd:project,env,stdio:['ignore','pipe',err.fd],detached:false});
  const item={child,status:null,done:null,capture:null,stderrHandle:err,streamsFinalized:false,stopPromise:null,record:{label,argv:[plan.wash.path,...args],pid:child.pid??null,stdoutPath:stdout,stderrPath:stderr,spawnAttempts:1,timeout:false,shutdownRequested:false,sigintSent:false,forcedCleanup:false,shutdownReason:null,exit:null}};
  children.push(item);result.commands.push(item.record);let spawnError=null;
  item.done=new Promise(yes=>{child.once('error',e=>{spawnError=errorData(e);});child.once('close',(code,signal)=>{item.status={code,signal,error:spawnError};item.record.exit=item.status;if(label==='wash-dev')status=item.status;yes(item.status);});});
  item.capture=captureRawStdout({readable:child.stdout,handle:out,path:stdout,limitBytes:plan.stdoutLimitBytes});
  void item.capture.failure.then(error=>{result.errors.push({stage:label+'-stdout-capture-live',error});void stopItem(item,'capture-failure').catch(e=>result.errors.push({stage:label+'-capture-failure-stop',...errorData(e)}));});
  return item;
 }
 async function finalizeItem(item){
  if(item.streamsFinalized)return;item.streamsFinalized=true;
  try{item.record.stdoutCapture=await bounded(item.capture.done,plan.captureFinalizeSeconds*1000,'Stdout EOF/finalization deadline');}
  catch(error){result.errors.push({stage:item.record.label+'-stdout-finalization',...errorData(error)});item.capture.abort('owned-finalization-deadline');try{item.record.stdoutCapture=await bounded(item.capture.done,1000,'Aborted capture deadline');}catch(e){result.errors.push({stage:item.record.label+'-stdout-abort-finalization',...errorData(e)});}}
  try{await item.stderrHandle.sync();}catch(error){result.errors.push({stage:item.record.label+'-stderr-sync',...errorData(error)});}
  try{await item.stderrHandle.close();}catch(error){result.errors.push({stage:item.record.label+'-stderr-close',...errorData(error)});}
  if(item.record.stdoutCapture?.complete)item.record.stdout=await row(item.record.stdoutPath);
  item.record.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 }

async function launchClient(args){
 const stdout=join(output,'full-contract-client.stdout.log'),stderr=join(output,'full-contract-client.stderr.log');
 const out=await open(stdout,'wx',0o600);let err;try{err=await open(stderr,'wx',0o600);}catch(error){await out.close();throw error;}
 const env={...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')};
 const child=spawn(plan.node.path,args,{cwd:output,env,stdio:['ignore',out.fd,err.fd]});let status=null,spawnError=null;
 const record={label:'full-contract-client',argv:[plan.node.path,...args],pid:child.pid??null,stdoutPath:stdout,stderrPath:stderr,stdout,stderr,timeout:false,forcedCleanup:false,exit:null};
 const done=new Promise(yes=>{child.once('error',error=>{spawnError=errorData(error);});child.once('close',(code,signal)=>{status={code,signal,error:spawnError};record.exit=status;yes(status);});});
 const item={child,done,out,err,record,get status(){return status;}};result.commands.push(record);return item;
}
async function finalizeClient(item){
 if(!item)return;
 if(item.status===null){item.record.shutdownRequested=true;item.record.sigtermSent=item.child.kill('SIGTERM');try{await bounded(item.done,5000,'Client stop deadline');}catch{item.record.forcedCleanup=true;item.record.sigkillSent=item.child.kill('SIGKILL');await bounded(item.done,5000,'Forced client stop deadline');}}
 item.record.exit=item.status;
 for(const handle of [item.out,item.err]){try{await handle.sync();}catch(error){result.errors.push({stage:'client-stream-sync',...errorData(error)});}try{await handle.close();}catch(error){result.errors.push({stage:'client-stream-close',...errorData(error)});}}
 if(item.record.shutdownRequested===true||item.status===null||![0,1].includes(item.status.code)||item.status.signal!==null||item.status.error!==null){
  item.record.rawStreamDigestsUnavailable=true;item.record.rawStreamFinalization='Interrupted client: descendant quiescence delegated to the unchanged original600-second monitor; raw paths retained without final digests';
 }else{item.record.stdout=await row(item.record.stdoutPath);item.record.stderr=await row(item.record.stderrPath);}
}
async function bounded(promise,ms,label){let timer;try{return await Promise.race([promise,new Promise((_,no)=>{timer=setTimeout(()=>no(new Error(label)),ms);})]);}finally{clearTimeout(timer);}}
async function tcpReady(port){return new Promise(yes=>{const socket=createConnection({host:'127.0.0.1',port});let settled=false;function finish(ok){if(settled)return;settled=true;socket.destroy();yes(ok);}socket.once('connect',()=>finish(true));socket.once('error',()=>finish(false));socket.setTimeout(150,()=>finish(false));});}
async function readinessLogs(item){
 const logs={},sizes={};for(const [stream,path]of [['stdout',item.record.stdoutPath],['stderr',item.record.stderrPath]]){const s=await lstat(path);assert(s.size<=plan.readinessPrefixBytes,'Readiness log cap; no truncated readiness fallback');logs[stream]=await readFile(path,'utf8');sizes[stream]=s.size;}return{logs,sizes};
}

try{
 await prepareReadonlyCopy();await readonlyBookend();await mkdir(cache,{mode:0o700});const cacheStat=await lstat(cache);assert(cacheStat.isDirectory()&&!cacheStat.isSymbolicLink());assert.equal(cacheStat.mode&0o777,0o700);assert.equal(await realpath(cache),cache);assert.deepEqual(await readdir(cache),[]);
 await mkdir(join(project,'.wash'),{recursive:true,mode:0o700});
 result.mounts=[{host:app,guest:'/app',physicalDirectoryMode:'0555',physicalFileMode:'0444'},{host:cache,guest:'/app/.next/cache',physicalRootMode:'0700'}];result.applicationCopy={files:input.regularFiles,bytes:input.bytes,sourceDirectoriesExcludingRoot:input.directories.length,ownedDirectoriesIncludingRoot:plan.applicationSchema.ownedDirectoriesIncludingRoot,byteIdentical:true,independentInodes:true,ownedAdditionalDirectories:[]};result.readonlyWasiDescriptorRightsProved=false;await save();
 lease=createServer();lease.on('error',()=>{});await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port:Number(selectedOrigin.port),exclusive:true},yes);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;assert.equal(origin,authority.selfOrigin,'Exact Root-literal origin; no fallback');result.portLease={origin,port:address.port,heldThroughConfigInspection:true,singleAttempt:true,fallbackAllowed:false};
 const configured=configuration(authority.envelope.path,app,cache,origin),configPath=join(project,'.wash/config.json'),empty=join(output,'empty-user-config.json');
 await writeFile(configPath,JSON.stringify(configured,null,2)+'\n',{flag:'wx',mode:0o600});await writeFile(empty,'{}\n',{flag:'wx',mode:0o600});result.configFiles=[await row(configPath),await row(empty)];artifactRefs.push(...result.configFiles);result.configured=configured;await save();
 await protect();await sourceBookend();await readonlyBookend();await artifactBookend();await witBookend();
 const show=await launchWash(['--user-config',empty,'-C',project,'--output','json','config','show'],'config-show');
 try{await bounded(show.done,plan.configSeconds*1000,'Stock config-show deadline');}catch(error){show.record.timeout=true;await stopItem(show,'config-deadline');throw error;}
 await finalizeItem(show);assert.deepEqual(show.status,{code:0,signal:null,error:null});assert.equal(show.record.stdoutCapture?.complete,true);await verify(show.record.stdout);const shown=await read(show.record.stdout.path);assert.equal(shown.success,true);validateEffective(shown.data,configured);result.effectiveConfiguration=shown.data;result.configVerifiedBeforeDev=true;await save();
 await protect();await sourceBookend();await readonlyBookend();await artifactBookend();await witBookend();
 await new Promise((yes,no)=>lease.close(error=>error?no(error):yes()));lease=null;result.portLease.releasedImmediatelyBeforeSingleDevLaunch=true;
 host=await launchWash(['--user-config',empty,'-C',project,'--log-level','info','--meters','duration','dev'],'wash-dev');result.server=host.record;result.server.freshProcess=true;
 void host.done.then(exit=>{if(!stopping)result.errors.push({stage:'server-exited-before-owned-shutdown',status:exit});});await save();
 const deadline=Date.now()+plan.listenerSeconds*1000;let ready=false;result.readiness={tcpConnect:false,workloadRegistered:false,extraHttpRequests:0,origin,polls:0,source:plan.readinessPolicy.sourceFile,completionEvents:[]};
 while(Date.now()<deadline){assert.equal(host.status,null,'Stock host exited before registration');assert.equal(host.capture.failed,false);const {logs,sizes}=await readinessLogs(host),registered=registrationFromLogs(logs,origin);result.readiness.polls++;result.readiness.lastLogSizes=sizes;result.readiness.workloadRegistered=registered.registered;result.readiness.completionEvents=registered.events;result.readiness.matchingMessageLines=registered.messageLines;
  if(registered.registered&&await tcpReady(address.port)){assert.equal(host.status,null);result.readiness.tcpConnect=true;ready=true;await save();break;}await save();await pause(50);}
 assert(ready,'Exact post-registration event AND TCP listener deadline');assert.equal(host.status,null,'Stock host exited before full contracts');
 result.publicRequestCorrelation=await writePublicCorrelationManifest({block:authority.publicRequestCorrelation,runId:authority.runId,origin,output});artifactRefs.push(result.publicRequestCorrelation.manifest);await artifactBookend();await save();
 clientProcess=await launchClient([plan.clientSource.path,origin,join(output,'client'),plan.browserTools,authority.runId]);result.client=clientProcess.record;result.fullContractClientInvoked=false;result.probeClientInvoked=true;await save();
 const clientStatus=await Promise.race([clientProcess.done,host.capture.failure.then(failure=>{throw Error('Stock lifetime stdout capture failed: '+failure.stage);})]);
 result.client.exit=clientStatus;result.client.result=await row(join(output,'client/result.json'));const observed=await read(result.client.result.path);assert.equal(typeof observed.probeExecuted,'boolean');result.probeExecuted=observed.probeExecuted;assert.equal(typeof observed.collectionComplete,'boolean');result.probeCollectionComplete=observed.collectionComplete;assert.equal(typeof observed.cleanupComplete,'boolean');result.probeCleanupComplete=observed.cleanupComplete;assert.equal(observed.fullOriginalContractExecuted,false);await save();
 assert.equal(observed.suite,'NEXT_DISCONNECT_RECOVERY_CLIENT_V1');assert.equal(observed.controlOnly,true);assert.equal(observed.probeExecuted,true);assert.equal(observed.collectionComplete,true);assert.equal(observed.cleanupComplete,true);assert.equal(observed.calls.length,114);assert.equal(observed.cycles.length,19);assert.equal(observed.fullOriginalContractExecuted,false);assert.equal(observed.fullNextAccepted,false);assert.deepEqual(clientStatus,{code:0,signal:null,error:null});assert.equal(observed.passed,true);assert.equal(host.status,null,'Stock host must remain live through bounded probe');result.controlPassed=true;
}catch(error){result.errors.push({stage:'wasmcloud-full-deployment-or-control',...errorData(error)});}
finally{
 if(lease?.listening)try{await new Promise(yes=>lease.close(()=>yes()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
 try{await finalizeClient(clientProcess);}catch(error){result.errors.push({stage:'client-finalize',...errorData(error)});}
 stopping=true;try{await stopHost('full-contracts-collected');}catch(error){result.errors.push({stage:'host-stop',...errorData(error)});}
 for(const item of children){try{if(item.status===null)await stopItem(item,'final-cleanup');await finalizeItem(item);}catch(error){result.errors.push({stage:item.record.label+'-finalize',...errorData(error)});}}
 result.stdoutCapture=host?.record.stdoutCapture??null;result.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 if(host){result.server.exit=host.status;result.server.stderrPath=host.record.stderrPath;result.server.stdoutPath=host.record.stdoutPath;result.server.plannedGracefulStop='SIGINT';}
 try{await sourceBookend();await protect();await artifactBookend();await witBookend();result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'source-final-protection',...errorData(error)});}
 try{await readonlyBookend();result.readonlyAppPreserved=true;}catch(error){result.errors.push({stage:'readonly-app-final',...errorData(error)});}
 result.cacheInventory=[];try{assert.equal((await lstat(cache)).mode&0o777,0o700);const tree=await walk(cache);assert.equal(tree.links.length,0);for(const name of tree.files){const path=join(cache,name);result.cacheInventory.push({...await row(path),relativePath:name,mode:(await lstat(path)).mode&0o777});}}catch(error){result.errors.push({stage:'cache-final-inventory',...errorData(error)});}
 result.allDirectCliExitsZero=JSON.stringify(result.commands.map(x=>x.label))===JSON.stringify(['config-show','wash-dev','full-contract-client'])&&result.commands.every(x=>x.timeout===false&&x.forcedCleanup===false&&x.exit?.code===0&&x.exit?.signal===null&&x.exit?.error===null);
 result.passed=result.controlPassed===true&&result.configVerifiedBeforeDev===true&&result.errors.length===0&&result.originalInputsPreserved&&result.readonlyAppPreserved&&result.allDirectCliExitsZero&&children.length===2&&children.every(x=>x.record.stdoutCapture?.complete===true)&&result.server?.shutdownReason==='full-contracts-collected'&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&host?.status?.code===0&&host?.status?.signal===null&&host?.status?.error===null;
 result.state=result.passed?'NEXT_DISCONNECT_RECOVERY_CLOUD_PROFILE_PASSED_UNREVIEWED_V1':'NEXT_DISCONNECT_RECOVERY_CLOUD_PROFILE_FAILED_RAW_PRESERVED_V1';await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,fullOriginalContractExecuted:result.fullOriginalContractExecuted,fullNextAccepted:false,errors:result.errors}));process.exitCode=result.passed?0:1;
