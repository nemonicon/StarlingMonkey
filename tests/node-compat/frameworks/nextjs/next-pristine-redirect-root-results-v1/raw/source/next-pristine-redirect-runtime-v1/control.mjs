// Dormant direct Node control. Imports only standard Node modules and pure models.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer,createConnection} from 'node:net';
import {createReadStream,constants} from 'node:fs';
import {readFile,writeFile,mkdir,cp,lstat,readdir,realpath,open} from 'node:fs/promises';
import {dirname,join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {outputFor,directoryNames,validateInput,listenerFromLogs,serverInvocation,accepted} from './models.mjs';
import {validatePublicCorrelation,writePublicCorrelationManifest} from './public-correlation.mjs';
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const diagnostic=e=>({name:e?.name??typeof e,message:e?.message??String(e),stack:e?.stack??null});
async function row(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){bytes+=b.length;h.update(b);}return{path,sha256:h.digest('hex'),bytes};}
async function verify(ref){const s=await lstat(ref.path);assert(s.isFile()&&!s.isSymbolicLink());assert.equal(s.nlink,1);assert.equal(await realpath(ref.path),ref.path);assert.deepEqual(await row(ref.path),ref);}
async function walk(root){const value={files:[],dirs:['.'],links:[]};async function visit(p){for(const name of(await readdir(p)).sort()){const q=join(p,name),s=await lstat(q),r=relative(root,q);if(s.isSymbolicLink())value.links.push(r);else if(s.isDirectory()){value.dirs.push(r);await visit(q);}else{assert(s.isFile(),'Regular files/directories only');value.files.push(r);}}}await visit(root);return value;}
async function family(ref){await verify(ref);const root=dirname(ref.path),index=await read(ref.path),names=index.files.map(r=>r.path),tree=await walk(root);assert.equal(new Set(names).size,names.length);assert.deepEqual(tree.links,[]);assert.deepEqual(tree.files.filter(x=>x!=='index.json').sort(),[...names].sort());const dirs=new Set(['.']);for(const r of index.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));let p=dirname(r.path);while(p!=='.'){dirs.add(p);p=dirname(p);}await verify({...r,path:join(root,r.path)});}assert.deepEqual(tree.dirs.sort(),[...dirs].sort());}
const plan=await read(join(here,'plan.json'));
assert.equal(plan.prospectiveBindingsPending,false,'Root actual app/client/asset/protection bindings pending before authority/output');
for(const key of ['applicationSource','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','expectedApplication','clientSource','clientSourceIndex','browserWorker','browserIndex','assetSelection','assetPins','sourceFamilies','protectedInputs','outputPrefix','runId'])assert(plan[key]!==null,'Missing Root binding:'+key);
assert(Array.isArray(plan.sourceFamilies)&&plan.sourceFamilies.length>0&&Array.isArray(plan.protectedInputs)&&plan.protectedInputs.length>0);
const authorityPath=resolve(process.argv[2]),authorityRef=await row(authorityPath),a=await read(authorityPath);
assert.equal(a.schemaVersion,1);assert.equal(a.state,'ROOT_NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_AUTHORIZED_V1');
assert.deepEqual(a.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(a.plan,await row(join(here,'plan.json')));
for(const k of ['hostOnlyDirectStandaloneAllowed','localhostServeAllowed','browserAllowed','publicRequestCorrelationAllowed'])assert.equal(a[k],true);
for(const k of ['compilerAllowed','nativeBuildAllowed','engineAllowed','guestAllowed','componentConstructionAllowed','packageInstallAllowed','applicationSourceMutationAllowed','externalDeploymentAllowed','adoptionAllowed'])assert.equal(a[k],false);
assert(!['argv','outputRoot','monitorOutputRoot','environment'].some(k=>Object.hasOwn(a,k)));assert.equal(a.runId,plan.runId);validatePublicCorrelation(a.publicRequestCorrelation);
async function protect(){await verify(authorityRef);await family(a.sourceIndex);for(const ref of plan.sourceFamilies)await family(ref);for(const ref of plan.protectedInputs)await verify(ref);}
await protect();
for(const key of ['applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentityEvidence'])assert.deepEqual(plan[key],plan.requiredApplicationData[key]);
assert.equal(plan.applicationSource,plan.requiredApplicationData.applicationRoot);
for(const key of ['applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentityEvidence','clientSource','browserWorker','assetSelection'])await verify(plan[key]);
await family(plan.clientSourceIndex);await family(plan.browserIndex);
assert.deepEqual(plan.clientSourceIndex,plan.browserIndex,'One genuine browser/client Source family');
assert.equal(dirname(plan.clientSource.path),dirname(plan.clientSourceIndex.path));assert.equal(dirname(plan.browserWorker.path),dirname(plan.browserIndex.path));
assert.equal(plan.clientSource.path,join(dirname(plan.clientSourceIndex.path),'run-browser.mjs'));assert.equal(plan.browserWorker.path,join(dirname(plan.browserIndex.path),'browser-check.mjs'));
assert.deepEqual(plan.assetSelection,plan.requiredAssetSelection);
const review=await read(plan.applicationBuildReview.path),identity=await read(plan.applicationRootIdentityEvidence.path),assets=await read(plan.assetSelection.path);
assert.equal(review.state,plan.expectedApplicationBuildReviewState);assert.equal(review.verifiedPassed,true);
assert.deepEqual(review.actualResult,plan.applicationBuildResult);assert.deepEqual(review.applicationInputs,plan.applicationInputs);assert.deepEqual(review.applicationRootIdentityEvidence,plan.applicationRootIdentityEvidence);assert.equal(review.applicationRoot,plan.applicationSource);
assert.deepEqual(Object.fromEntries(['path','mode','dev','ino','nlink'].map(k=>[k,identity.rootIdentity[k]])),plan.applicationRootIdentity);assert.deepEqual(identity.inventory,plan.applicationInputs);
assert.equal(assets.verifiedPassed,true);assert.deepEqual(assets.applicationBuildReview,plan.applicationBuildReview);assert.deepEqual(assets.actualBuildResult,plan.applicationBuildResult);assert.deepEqual(assets.applicationInputs,plan.applicationInputs);assert.deepEqual(assets.applicationRootIdentityEvidence,plan.applicationRootIdentityEvidence);assert.equal(assets.applicationRoot,plan.applicationSource);assert.deepEqual(assets.assetPins,plan.assetPins);
const browserPolicy=await read(join(dirname(plan.browserIndex.path),'plan.json'));assert.equal(browserPolicy.actualAssetBindingsPending,false);assert.deepEqual(browserPolicy.applicationInputs,plan.applicationInputs);assert.deepEqual(browserPolicy.assetPins,plan.assetPins);
assert.deepEqual(browserPolicy.actualAssetSelectionReview,plan.assetSelection);assert.deepEqual(browserPolicy.assetSelectionHtml,assets.clientHtml);assert.deepEqual(browserPolicy.actionsAssetSelectionHtml,assets.actionsHtml);assert.deepEqual(browserPolicy.actionsAssetPins,assets.actionsAssetPins);
const input=await read(plan.applicationInputs.path),build=await read(plan.applicationBuildResult.path);validateInput(input,build,plan);
async function sourceBookend(){
 assert.equal(await realpath(input.root),input.root);const s=await lstat(input.root);assert(s.isDirectory()&&!s.isSymbolicLink());
 for(const[k,v]of Object.entries(plan.applicationRootIdentity))if(k!=='path')assert.equal(k==='mode'?s.mode&0o777:s[k],v,'Original root '+k);
 const tree=await walk(input.root);assert.deepEqual(tree.links,[]);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),directoryNames(input));
 for(const r of input.files){const q=join(input.root,r.path),st=await lstat(q);await verify({path:q,sha256:r.sha256,bytes:r.bytes});assert.deepEqual([st.mode&0o777,st.dev,st.ino,st.nlink],[r.mode,r.dev,r.ino,r.nlink]);}
 for(const r of input.directories){const st=await lstat(join(input.root,r.path));assert.deepEqual([st.mode&0o777,st.dev,st.ino],[r.mode,r.dev,r.ino]);}
}
await sourceBookend();const output=outputFor(plan.outputPrefix,a.runId),app=join(output,'app');assert.equal(resolve(output),output);await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_IN_PROGRESS_V1',runId:a.runId,rootAuthority:authorityRef,sourceIndex:a.sourceIndex,plan:a.plan,applicationInputs:plan.applicationInputs,applicationBuildResult:plan.applicationBuildResult,sourceRootIdentity:plan.applicationRootIdentity,outputRoot:output,errors:[],server:null,client:null,browserControlPassed:false,copyInitiallyVerified:false,originalInputsPreserved:false,ownedFinalInventoryRecorded:false,controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,guestExecuted:false,engineExecuted:false,moduleProviderOrHttpBridgeUsed:false,applicationSourceModified:false,adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const handles=[],children=[];let host=null,hostDone=null,hostExit=null,lease=null,stopping=false;
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function boundedWait(promise,ms){let t;try{return await Promise.race([promise,new Promise(r=>{t=setTimeout(()=>r(null),ms);})]);}finally{clearTimeout(t);}}
async function launch(invocation,label){
 const stdout=join(output,label+'.stdout.log'),stderr=join(output,label+'.stderr.log');const out=await open(stdout,'wx',0o600);handles.push(out);const err=await open(stderr,'wx',0o600);handles.push(err);
 const child=spawn(invocation.exe,invocation.args,{cwd:invocation.cwd,env:invocation.env,stdio:['ignore',out.fd,err.fd]});let status=null;
 const done=new Promise(resolve=>{child.once('error',e=>{status={code:null,signal:null,error:diagnostic(e)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});
 const item={child,done,get status(){return status;},record:{label,argv:[invocation.exe,...invocation.args],cwd:invocation.cwd,environment:invocation.env,pid:child.pid??null,stdout,stderr,exit:null}};children.push(item);return item;
}
async function verifyInitialCopy(){
 const s=await lstat(app);assert(s.isDirectory()&&!s.isSymbolicLink());assert.equal(await realpath(app),app);assert.equal(s.mode&0o777,plan.applicationRootIdentity.mode);assert(s.dev!==plan.applicationRootIdentity.dev||s.ino!==plan.applicationRootIdentity.ino);
 const tree=await walk(app);assert.deepEqual(tree.links,[]);assert.deepEqual(tree.files.sort(),input.files.map(r=>r.path).sort());assert.deepEqual(tree.dirs.sort(),directoryNames(input));
 for(const r of input.files){const q=join(app,r.path),s=await lstat(q);await verify({path:q,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert(s.dev!==r.dev||s.ino!==r.ino);}
 for(const r of input.directories)assert.equal((await lstat(join(app,r.path))).mode&0o777,r.mode);
}
async function tcpOnce(port){return new Promise(resolve=>{const s=createConnection({host:'127.0.0.1',port});let settled=false;function end(ok){if(settled)return;settled=true;s.destroy();resolve(ok);}s.once('connect',()=>end(true));s.once('error',()=>end(false));s.setTimeout(plan.tcpConnectMilliseconds,()=>end(false));});}
async function stopServer(){
 if(host&&!hostExit){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.kill('SIGINT');await boundedWait(hostDone,plan.gracefulStopMilliseconds);
  if(!hostExit){result.server.forcedCleanup=true;result.server.sigkillSent=host.kill('SIGKILL');await boundedWait(hostDone,plan.forcedStopWaitMilliseconds);}}
 if(result.server)result.server.exit=hostExit;
}
try{
 await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:constants.COPYFILE_FICLONE});await verifyInitialCopy();result.copyInitiallyVerified=true;
 result.applicationCopy={files:input.regularFiles,bytes:input.bytes,directoriesIncludingRoot:input.directories.length+1,independentRootAndFileInodes:true,modesEqual:true,copyFlag:'COPYFILE_FICLONE',reflinkActuallyUsed:null,initialMembershipExact:true,finalWholeCopyImmutabilityClaimed:false};
 // Fresh build has no cache. Only this owned copy may gain runtime caches.
 assert(!(await walk(app)).dirs.includes('.next/cache'));await mkdir(join(output,'tmp'),{mode:0o700});
 lease=createServer();await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;
 result.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};const invocation=serverInvocation(plan.node.path,app,origin,process.env,join(output,'tmp'));
 assert.deepEqual(invocation.args,[join(app,'server.js')]);assert(!['NODE_OPTIONS','NODE_PATH','NEXT_MANUAL_SIG_HANDLE','NODE_CHANNEL_FD'].some(k=>Object.hasOwn(invocation.env,k)));await protect();await sourceBookend();
 await new Promise((resolve,reject)=>lease.close(e=>e?reject(e):resolve()));lease=null;result.portLease.releasedBeforeSingleSpawn=true;
 const server=await launch(invocation,'server');host=server.child;hostDone=server.done;result.server={...server.record,shutdownRequested:false,sigintSent:false,forcedCleanup:false,expectedSignalExit:130};
 void hostDone.then(status=>{hostExit=status;if(!stopping)result.errors.push({stage:'server-exited-before-owned-stop',status});});await save();
 const deadline=Date.now()+plan.listenerSeconds*1000;let events=[];
 while(Date.now()<deadline){assert.equal(hostExit,null,'Server exited before listener');const logs={};for(const k of ['stdout','stderr']){assert((await lstat(server.record[k])).size<=plan.logLimitBytes);logs[k]=await readFile(server.record[k],'utf8');}events=listenerFromLogs(logs,origin);if(events.length)break;await pause(50);}
 assert(events.length>0,'Exact leased Next Local URL not observed');assert(await tcpOnce(address.port),'Single TCP readiness failed');assert.equal(hostExit,null);
 result.readiness={exactListenerEvents:events,tcpConnect:true,extraHttpRequests:0,applicationHandlersInitializedObserved:false,sourceRequestWaitsForHandlersPromise:true,readyLogIsNotHandlerCompletion:true};await save();
 result.publicRequestCorrelation=await writePublicCorrelationManifest({block:a.publicRequestCorrelation,runId:a.runId,origin,output});await save();
 const client=await launch({exe:plan.node.path,args:[plan.clientSource.path,origin,join(output,'client'),plan.browserTools,a.runId],cwd:output,env:invocation.env},'client');result.client=client.record;await save();const status=await client.done;result.client.exit=status;result.client.result=await row(join(output,'client/result.json'));const observed=await read(result.client.result.path);
 assert.deepEqual(status,{code:0,signal:null,error:null});assert.equal(observed.passed,true);assert.equal(observed.controlOnly,true);assert.equal(observed.fullOriginalContractExecuted,false);assert.equal(observed.fullNextAccepted,false);assert.equal(observed.browser.passed,true);assert.equal(observed.browser.functionalPassed,true);assert.equal(observed.browser.browserErrorFree,true);assert.deepEqual(observed.browser.tests.map(t=>t.id),['client-counter','server-action']);assert.equal(hostExit,null,'Server must stay live through contracts');result.browserControlPassed=true;
}catch(e){result.errors.push({stage:'direct-control',...diagnostic(e)});}
finally{
 if(lease?.listening)try{await new Promise(r=>lease.close(()=>r()));}catch(e){result.errors.push({stage:'lease-close',...diagnostic(e)});}
 try{await stopServer();}catch(e){result.errors.push({stage:'server-stop',...diagnostic(e)});}
 for(const child of children)if(!child.status&&child.child!==host){child.record.shutdownRequested=true;child.record.forcedCleanup=true;result.errors.push({stage:'unfinished-client-cleanup'});child.child.kill('SIGTERM');if(await boundedWait(child.done,plan.forcedStopWaitMilliseconds)===null){child.child.kill('SIGKILL');await boundedWait(child.done,plan.forcedStopWaitMilliseconds);}}
 for(const child of children){child.record.exit=child.status;if(child.record.label==='client'&&(child.record.shutdownRequested===true||child.status?.code!==0||child.status?.signal!==null||child.status?.error!==null)){child.record.streamDigestPublication='unavailable-until-original-owner-quiescence';child.record.rawStreamPathsRetained=true;child.record.browserDescendantQuiescenceProvedByClientReaping=false;continue;}for(const k of ['stdout','stderr'])try{const ref=await row(child.record[k]);child.record[k]=ref;if(child.record.label==='server')result.server[k]=ref;}catch(e){result.errors.push({stage:'stream-descriptor',...diagnostic(e)});}}
 for(const h of handles)try{await h.close();}catch(e){result.errors.push({stage:'stream-close',...diagnostic(e)});}
 try{await sourceBookend();await protect();result.originalInputsPreserved=true;}catch(e){result.errors.push({stage:'final-original-protection',...diagnostic(e)});}
 try{const tree=await walk(app);assert.deepEqual(tree.links,[]);const files=[];for(const name of tree.files){const q=join(app,name),s=await lstat(q);files.push({...await row(q),relativePath:name,mode:s.mode&0o777,dev:s.dev,ino:s.ino,nlink:s.nlink});}const path=join(output,'owned-app-final-inventory.json');await writeFile(path,JSON.stringify({files,directories:tree.dirs,sourceModesRetainedInitially:true,wholeCopyImmutable:false},null,2)+'\n',{flag:'wx',mode:0o600});result.ownedFinalInventory=await row(path);result.ownedFinalInventoryRecorded=true;}catch(e){result.errors.push({stage:'owned-final-observation',...diagnostic(e)});}
 result.passed=accepted(result);result.state=result.passed?'NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_PASSED_UNREVIEWED_V1':'NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_FAILED_UNACCEPTED_V1';await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,serverExit:result.server?.exit,errors:result.errors}));process.exitCode=result.passed?0:1;
