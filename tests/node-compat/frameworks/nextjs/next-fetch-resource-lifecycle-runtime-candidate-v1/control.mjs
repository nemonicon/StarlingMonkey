// Thin owned coordinator: unchanged standalone server, independent reference, one guest GET.
import assert from 'node:assert/strict';
import {constants} from 'node:fs';
import {cp,mkdir,lstat,readFile,realpath,statfs} from 'node:fs/promises';
import {createServer} from 'node:net';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {context,layout,originPort,launch,read,row,verify,walk,durable,jsonBytes,errorData,pause,waitBounded,tcpOnce,clean} from './io.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));

async function main(){
 assert.equal(process.argv.length,3);const authpath=resolve(process.argv[2]);const{a,plan,authorityRef,protect}=await context(HERE,authpath);
 await verify(plan.directModels);const models=await import(pathToFileURL(plan.directModels.path).href);
 const input=await read(plan.applicationInputs.path),build=await read(plan.applicationBuildResult.path);models.validateInput(input,build,plan);
 async function sourceBookend(){
  assert.equal(await realpath(input.root),input.root);const root=await lstat(input.root);assert(root.isDirectory()&&!root.isSymbolicLink());
  for(const[k,v]of Object.entries(plan.applicationRootIdentity))if(k!=='path')assert.equal(k==='mode'?root.mode&0o777:root[k],v);
  const tree=await walk(input.root);assert.deepEqual(tree.files,input.files.map(r=>r.path).sort());assert.deepEqual(tree.dirs,models.directoryNames(input));
  for(const r of input.files){const p=join(input.root,r.path),s=await lstat(p);await verify({path:p,sha256:r.sha256,bytes:r.bytes});assert.deepEqual([s.mode&0o777,s.dev,s.ino,s.nlink],[r.mode,r.dev,r.ino,r.nlink]);}
  for(const r of input.directories){const s=await lstat(join(input.root,r.path));assert.deepEqual([s.mode&0o777,s.dev,s.ino],[r.mode,r.dev,r.ino]);}
 }
 await sourceBookend();const output=layout(plan,a.runId),app=join(output,'app');const disk=await statfs(dirname(output));assert(Number(disk.bavail)*Number(disk.bsize)>=1073741824);await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,state:'PUBLIC_FETCH_LIFECYCLE_CONTROLLER_IN_PROGRESS_V1',runId:a.runId,rootAuthority:authorityRef,sourceIndex:a.sourceIndex,plan:a.plan,controlOrigin:a.controlOrigin,guestOrigin:a.guestOrigin,control:null,reference:null,guest:null,validation:null,errors:[],copyInitiallyVerified:false,ownedCopyProtected:false,originalInputsPreserved:false,publicObservableProfilePassed:false,fullNextAccepted:false,nativeResourcesProved:false,adoption:false};
 const save=()=>durable(join(output,'result.json'),jsonBytes(result));await save();
 const handles=[],children=[];let host=null,lease=null,stopping=false,initialCopyRoot=null;const alive=[];
 const controlAlive=label=>{assert(host&&host.status===null,'Control must remain alive: '+label);alive.push({label,observedAtNs:process.hrtime.bigint().toString(),pid:host.child.pid,status:null});};
 async function copyBookend(initial=false){
  const root=await lstat(app);assert(root.isDirectory()&&!root.isSymbolicLink());assert.equal(await realpath(app),app);assert.equal(root.mode&0o777,plan.applicationRootIdentity.mode);assert(root.dev!==plan.applicationRootIdentity.dev||root.ino!==plan.applicationRootIdentity.ino);
  if(initial)initialCopyRoot={dev:root.dev,ino:root.ino,mode:root.mode&0o777};else assert.deepEqual({dev:root.dev,ino:root.ino,mode:root.mode&0o777},initialCopyRoot);
  const tree=await walk(app),knownFiles=new Set(input.files.map(r=>r.path)),knownDirs=new Set(models.directoryNames(input));
  if(initial){assert.deepEqual(tree.files,[...knownFiles].sort());assert.deepEqual(tree.dirs,[...knownDirs].sort());}
  else{for(const name of tree.files)assert(knownFiles.has(name)||name.startsWith('.next/cache/'),'Only owned cache additions');for(const name of tree.dirs)assert(knownDirs.has(name)||name==='.next/cache'||name.startsWith('.next/cache/'),'Only owned cache directories');}
  for(const r of input.files){const p=join(app,r.path),s=await lstat(p);await verify({path:p,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert(s.dev!==r.dev||s.ino!==r.ino);}
  for(const r of input.directories)assert.equal((await lstat(join(app,r.path))).mode&0o777,r.mode);
  return tree;
 }
 async function runPhase(phase){
  const invocation={exe:plan.python.path,args:['-I','-B',join(HERE,'phase-owner.py'),authpath,phase],cwd:output,env:{...process.env}};
  const child=await launch(invocation,phase+'-owner-cli',output,handles,children);const record=child.record;result[phase==='reference'?'reference':'guest']={...record,observation:null,rawCapture:null};await save();
  const status=await child.done;const ownerRoot=join(output,phase==='reference'?'node-reference-owner':'guest-owner'),observationRef=await row(join(ownerRoot,'observation.json')),observation=await read(observationRef.path);
  const observed=result[phase==='reference'?'reference':'guest'];observed.exit=status;observed.observation=observationRef;await save();
  assert.deepEqual(status,{code:0,signal:null,error:null});assert.equal(observation.captureCompletedCleanly,true);assert.equal(observation.controlOrigin,a.controlOrigin);assert.deepEqual(observation.rootAuthority,authorityRef);
  assert.deepEqual(observation.phaseAuthority,phase==='reference'?a.nodeReferenceAuthority:a.guestAuthority);await verify(observation.terminal);const terminal=await read(observation.terminal.path);assert(clean(terminal));assert.deepEqual(terminal.authority,observation.phaseAuthority);
  if(phase==='reference')observed.rawCapture=await row(join(output,'node-reference/observations.json'));
  else{const guestRef=await row(join(output,'guest/result.json')),guest=await read(guestRef.path);observed.result=guestRef;observed.rawCapture=guest.response?.body??null;assert.equal(guest.observationsValid,true);assert.equal(guest.controlOrigin,a.controlOrigin);}
  await save();return observed;
 }
 try{
  await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true,mode:constants.COPYFILE_FICLONE});await copyBookend(true);result.copyInitiallyVerified=true;
  await mkdir(join(output,'tmp'),{mode:0o700});const port=originPort(a.controlOrigin);lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port,exclusive:true},yes);});assert.equal(lease.address().port,port);
  result.controlLease={origin:a.controlOrigin,port,singleAttempt:true,fallbackAllowed:false};await save();const invocation=models.serverInvocation(plan.node.path,app,a.controlOrigin,process.env,join(output,'tmp'));
  assert.deepEqual(invocation.args,[join(app,'server.js')]);for(const k of ['NODE_OPTIONS','NODE_PATH','NEXT_MANUAL_SIG_HANDLE','NODE_CHANNEL_FD'])assert.equal(Object.hasOwn(invocation.env,k),false);
  await protect();await sourceBookend();await new Promise((yes,no)=>lease.close(e=>e?no(e):yes()));lease=null;
  host=await launch(invocation,'control-server',output,handles,children);result.control={...host.record,phaseAuthority:a.controlAuthority,shutdownRequested:false,sigintSent:false,forcedCleanup:false,expectedExitCode:130};
  void host.done.then(status=>{if(!stopping)result.errors.push({stage:'control-exited-before-owned-stop',status});});await save();
  const deadline=Date.now()+30000;let events=[];
  while(Date.now()<deadline){assert.equal(host.status,null);const logs={};for(const k of ['stdout','stderr']){assert((await lstat(host.record[k])).size<=plan.listenerLogByteCap);logs[k]=await readFile(host.record[k],'utf8');}events=models.listenerFromLogs(logs,a.controlOrigin);if(events.length)break;await pause(plan.readinessPollMilliseconds);}
  assert(events.length>0);assert(await tcpOnce(port,plan.tcpConnectMilliseconds));controlAlive('ready-before-reference');
  result.readiness={exactListenerEvents:events,tcpConnect:true,httpWarmupRequests:0,applicationHandlersInitializedObserved:false,readyLogIsNotHandlerCompletion:true};await save();
  await runPhase('reference');controlAlive('after-reference-before-guest');await save();
  await runPhase('guest');controlAlive('after-guest-before-stop');
  await durable(join(output,'raw-publication.json'),jsonBytes({nodeReference:result.reference.rawCapture,guestCapture:result.guest.rawCapture,controlOrigin:a.controlOrigin,semanticValidationInvoked:false}),true);await save();
 }catch(error){result.errors.push({stage:'control-or-owned-phase',...errorData(error)});}
 finally{
  if(lease?.listening)try{await new Promise(r=>lease.close(()=>r()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
  try{if(host&&host.status===null){stopping=true;result.control.shutdownRequested=true;result.control.sigintSent=host.child.kill('SIGINT');await waitBounded(host.done,5000);if(host.status===null){result.control.forcedCleanup=true;host.child.kill('SIGKILL');await waitBounded(host.done,5000);}}if(result.control)result.control.exit=host?.status??null;}catch(error){result.errors.push({stage:'control-shutdown',...errorData(error)});}
  for(const child of children)if(child!==host&&child.status===null){result.errors.push({stage:'unfinished-owned-phase',label:child.record.label});child.child.kill('SIGTERM');if(await waitBounded(child.done,5000)===null){child.child.kill('SIGKILL');await waitBounded(child.done,5000);}}
  result.controlLifetimeBookends=alive;
  try{await copyBookend();const tree=await walk(app),files=[];for(const name of tree.files){const p=join(app,name),s=await lstat(p);files.push({...await row(p),relativePath:name,mode:s.mode&0o777,dev:s.dev,ino:s.ino,nlink:s.nlink});}const path=join(output,'owned-app-final-inventory.json');await durable(path,jsonBytes({files,directories:tree.dirs,knownSourceFilesPreserved:true,onlyCacheAdditions:true}),true);result.ownedFinalInventory=await row(path);result.ownedCopyProtected=true;}catch(error){result.errors.push({stage:'owned-copy-final-protection',...errorData(error)});}
  try{await sourceBookend();await protect();result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'final-original-protection',...errorData(error)});}
  await save();
 }
 // Both raw captures and normal server shutdown precede the sealed DATA CLI.
 if(result.reference?.rawCapture&&result.guest?.rawCapture){
  try{await verify(result.reference.rawCapture);await verify(result.guest.rawCapture);const validation=await launch({exe:plan.python.path,args:['-I','-B',plan.dataVerifier.path,'--capture',result.guest.rawCapture.path,'--node-reference',result.reference.rawCapture.path],cwd:output,env:{...process.env}},'data-verifier',output,handles,children);result.validation={...validation.record,exit:await validation.done};await save();if(result.validation.exit.code===0&&result.validation.exit.signal===null&&result.validation.exit.error===null)result.publicObservableProfilePassed=true;}
  catch(error){result.errors.push({stage:'retained-data-validation',...errorData(error)});}
 }
 for(const child of children){child.record.exit=child.status;const target=child===host?result.control:child.record.label==='reference-owner-cli'?result.reference:child.record.label==='guest-owner-cli'?result.guest:child.record.label==='data-verifier'?result.validation:null;for(const key of ['stdout','stderr'])try{child.record[key]=await row(child.record[key]);if(target)target[key]=child.record[key];}catch(error){result.errors.push({stage:'stream-descriptor',...errorData(error)});}}
 for(const handle of handles)try{await handle.sync();await handle.close();}catch(error){result.errors.push({stage:'stream-close',...errorData(error)});}
 result.passed=result.errors.length===0&&result.copyInitiallyVerified&&result.ownedCopyProtected&&result.originalInputsPreserved&&models.serverStopAccepted(result.control)&&result.reference?.exit?.code===0&&result.guest?.exit?.code===0&&result.publicObservableProfilePassed;
 result.state=result.passed?'PUBLIC_FETCH_LIFECYCLE_PROFILE_CAPTURED_UNREVIEWED_V1':'PUBLIC_FETCH_LIFECYCLE_RUNTIME_FAILED_RAW_PRESERVED_V1';await save();
 console.log(JSON.stringify({state:result.state,passed:result.passed,publicObservableProfilePassed:result.publicObservableProfilePassed,errors:result.errors,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
