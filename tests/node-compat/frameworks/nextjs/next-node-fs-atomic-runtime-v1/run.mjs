// Unissued one-GET cache-suite host actor. No retained Source is evaluated as a guard.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createServer,createConnection} from 'node:net';
import http from 'node:http';
import {constants as fsConstants} from 'node:fs';
import {open,readFile,lstat,realpath,mkdir,readdir,statfs,chmod,copyFile} from 'node:fs/promises';
import {join,dirname,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const sleep=ms=>new Promise(yes=>setTimeout(yes,ms));
const hash=b=>createHash('sha256').update(b).digest('hex');
const errorData=e=>({type:e===null?'null':typeof e,name:typeof e?.name==='string'?e.name.slice(0,128):null,message:typeof e?.message==='string'?e.message.slice(0,2048):null});
const stamps=new Map();
function physical(s){return{dev:s.dev,ino:s.ino,mode:s.mode,nlink:s.nlink,size:s.size,mtimeMs:s.mtimeMs,ctimeMs:s.ctimeMs};}
async function row(path){
 assert.equal(await realpath(path),path);const a=await lstat(path);assert(a.isFile()&&!a.isSymbolicLink()&&a.nlink===1);
 const b=await readFile(path),z=await lstat(path);assert.deepEqual(physical(a),physical(z));
 return{path,sha256:hash(b),bytes:b.length};
}
async function verify(ref){assert(ref&&typeof ref.path==='string');assert.deepEqual(await row(ref.path),ref);}
async function document(ref){assert(ref&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=16777216);await verify(ref);const v=JSON.parse(await readFile(ref.path,'utf8'));await verify(ref);return v;}
async function save(path,value){const f=await open(path,'wx',0o600);try{await f.writeFile(JSON.stringify(value,null,2)+'\n');await f.sync();}finally{await f.close();}return row(path);}
async function walk(root){
 const out={files:[],dirs:['.']};
 async function visit(dir){for(const name of(await readdir(dir)).sort()){
  const path=join(dir,name),s=await lstat(path),r=relative(root,path);assert(!s.isSymbolicLink());
  if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile()&&s.nlink===1);out.files.push(r);}
 }}await visit(root);return out;
}
function member(name){assert.equal(typeof name,'string');assert(name&&!name.includes('\\')&&!name.includes('\0'));assert(name.split('/').every(x=>x&&x!=='.'&&x!=='..'));return name;}
async function family(ref){
 const index=await document(ref),root=dirname(ref.path),names=index.files.map(r=>member(r.path));assert.equal(new Set(names).size,names.length);
 const dirs=new Set(['.']);for(const name of names){let p=dirname(name);while(p!=='.'){dirs.add(p);p=dirname(p);}}
 const tree=await walk(root);assert.deepEqual(tree.files.sort(),[...names,'index.json'].sort());assert.deepEqual(tree.dirs.sort(),[...dirs].sort());
 for(const r of index.files)await verify({...r,path:join(root,r.path)});return index;
}
async function inputStamp(path){const s=await lstat(path),value=physical(s);assert.equal(await realpath(path),path);assert(!s.isSymbolicLink());if(stamps.has(path))assert.deepEqual(value,stamps.get(path));else stamps.set(path,value);return s;}
async function allInputBookends(){for(const[path,value]of stamps)assert.deepEqual(physical(await lstat(path)),value);}
async function prefix(path,limit){let f;try{f=await open(path,'r');const b=Buffer.alloc(limit+1),{bytesRead}=await f.read(b,0,b.length,0);assert(bytesRead<=limit,'Readiness prefix exceeded');const t=b.subarray(0,bytesRead).toString('utf8'),last=t.lastIndexOf('\n');return last<0?'':t.slice(0,last+1);}catch(e){if(e.code==='ENOENT')return'';throw e;}finally{await f?.close();}}
async function bounded(promise,ms,label){let timer;try{return await Promise.race([promise,new Promise((_,no)=>{timer=setTimeout(()=>no(new Error(label)),ms);})]);}finally{clearTimeout(timer);}}
async function tcp(port){return new Promise((yes,no)=>{const s=createConnection({host:'127.0.0.1',port});s.setTimeout(1000);s.once('connect',()=>{s.destroy();yes();});s.once('timeout',()=>{s.destroy();no(new Error('TCP readiness deadline'));});s.once('error',no);});}
async function request(port,seconds,limit){return new Promise(yes=>{
 const chunks=[];let bytes=0,settled=false,headers=[],status=null,overflow=false;
 const finish=(error,complete)=>{if(settled)return;settled=true;clearTimeout(timer);yes({body:Buffer.concat(chunks),status,headers,bodyBytes:bytes,overflow,unretainedTailUnknown:overflow,error:error?errorData(error):null,complete});};
 const req=http.request({host:'127.0.0.1',port,method:'GET',path:'/cache-suite',agent:false},res=>{
  status=res.statusCode;headers=res.rawHeaders;res.on('data',b=>{if(bytes+b.length>limit){overflow=true;req.destroy(new Error('HTTP body cap'));return;}chunks.push(b);bytes+=b.length;});
  res.once('end',()=>finish(null,res.complete===true));res.once('error',e=>finish(e,false));res.once('aborted',()=>finish(new Error('HTTP response aborted'),false));
 });const timer=setTimeout(()=>req.destroy(new Error('HTTP request deadline')),seconds*1000);req.once('error',e=>finish(e,false));req.end();
});}

async function main(){
 assert.equal(process.argv.length,4);assert.equal(process.argv[2],'--authority');assert.equal(process.env.NODE_OPTIONS,undefined);assert.equal(process.env.NODE_PATH,undefined);
 const plan=JSON.parse(await readFile(join(HERE,'plan.json'),'utf8'));
 assert.equal(plan.prospectiveArtifactBindingsPending,false,'New actual INIT bindings pending');
 assert.equal(typeof plan.expectedConstructorReviewState,'string');assert(Object.values(plan.expectedBindings).every(x=>x&&typeof x.path==='string'));
 const authpath=resolve(process.argv[3]),ar=await row(authpath),a=await document(ar);
 assert.equal(a.state,'ROOT_NEXT_NODE_FS_ATOMIC_RUNTIME_AUTHORIZED_V1');assert.equal(a.schemaVersion,1);assert.equal(a.unissued,false);
 for(const k of ['localhostServeAllowed','nodeFsAtomicSuiteAllowed','applicationCopyAllowed','fixtureCopyAllowed','writableTestRootAllowed'])assert.equal(a[k],true);
 for(const k of ['browserAllowed','guestEnvironmentAllowed','outgoingHttpWorkloadSelected','automaticRetryAllowed','nativeBuildAllowed','constructorAllowed'])assert.equal(a[k],false);
 assert.equal(typeof a.runId,'string');const match=/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId);assert(match&&match[0]===a.runId);
 assert.deepEqual(a.sourceIndex,await row(join(HERE,'index.json')));assert.deepEqual(a.plan,await row(join(HERE,'plan.json')));
 for(const[k,v]of Object.entries(plan.expectedBindings))assert.deepEqual(a[k],v);
 for(const[k,v]of Object.entries(plan.knownInputs))assert.deepEqual(a[k],v);
 await family(a.sourceIndex);await family(plan.guestSourceIndex);const suiteIndex=await family(plan.suiteSourceIndex);
 await verify(plan.guestEntry);await verify(plan.suiteEntry);assert.equal(suiteIndex.files.filter(r=>r.path==='atomic-cases.cjs'&&r.sha256===plan.suiteEntry.sha256&&r.bytes===plan.suiteEntry.bytes).length,1);
 assert.deepEqual(await row(process.execPath),plan.node);await verify(plan.wasmtime);await verify(a.component);
 const review=await document(a.constructionDataReview);assert.equal(review.state,plan.expectedConstructorReviewState);assert.equal(review.verifiedPassed,true);assert.equal(review.completeReturnedImportAuditVerified,true);
 for(const k of ['component','componentAudit','engine','nativeMetadata'])assert.deepEqual(review[k],a[k]);assert.deepEqual(review.actualResult,a.constructionResult);assert.deepEqual(review.fullBuildReview,a.fullNativeBuildReview);
 const constructor=await document(a.constructionResult);assert.equal(constructor.passed,true);assert.deepEqual(constructor.callerIndex,a.constructionCallerIndex);assert.deepEqual(constructor.plan,a.constructionPlan);assert.deepEqual(constructor.rootAuthority,a.constructionRootAuthority);assert.deepEqual(constructor.artifacts.component,a.component);assert.deepEqual(constructor.artifacts.inputEntry,plan.guestEntry);assert.deepEqual(constructor.artifacts.inputSourceIndex,plan.guestSourceIndex);
 const audit=await document(a.componentAudit);assert.equal(audit.passed,true);assert.deepEqual(audit.component,a.component);assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);assert(audit.emittedImports.every(x=>plan.selectedInterfaces.includes(x)));assert.equal(plan.selectedInterfaces.length,13);
 const input=await document(plan.applicationInventory),rootIdentity=await document(plan.applicationRootIdentity);
 assert.deepEqual(rootIdentity.inventory,plan.applicationInventory);assert.equal(input.root,plan.applicationSource);assert.equal(rootIdentity.rootIdentity.path,input.root);
 assert.equal(input.schemaVersion,1);assert.deepEqual(input.symlinks,[]);assert.equal(input.regularFiles,input.files.length);assert.equal(input.regularFiles,plan.expectedApplication.files);assert.equal(input.directories.length,plan.expectedApplication.directories);assert.equal(input.bytes,plan.expectedApplication.bytes);assert.equal(input.files.reduce((n,x)=>n+x.bytes,0),input.bytes);
 const fileNames=input.files.map(r=>member(r.path)),dirNames=['.',...input.directories.map(r=>member(r.path))].sort();assert.equal(new Set(fileNames).size,fileNames.length);assert.equal(new Set(dirNames).size,dirNames.length);assert(fileNames.every(x=>!dirNames.includes(x)));
 const output=plan.outputPrefix+'-'+a.runId,ownerRoot=output+'-external-root';
 const started=JSON.parse(await readFile(join(ownerRoot,'started.json'),'utf8'));assert.deepEqual(started.authority,ar);assert.equal(started.pid,process.pid);assert.equal(started.timeoutSeconds,180);assert.deepEqual(started.argv,[plan.node.path,join(HERE,'run.mjs'),'--authority',authpath]);
 const disk=await statfs(dirname(output));assert(Number(disk.bavail)*Number(disk.bsize)>=plan.minimumFreeBytes);await mkdir(output,{mode:0o700});
 const app=join(output,'app'),suite=join(output,'suite'),testRoot=join(output,'cache-tests');
 const paths={stdout:join(output,'wasmtime.stdout.log'),stderr:join(output,'wasmtime.stderr.log'),body:join(output,'http.body'),response:join(output,'response.json'),result:join(output,'result.json')};
 const result={schemaVersion:1,state:'NEXT_NODE_FS_ATOMIC_RUNTIME_COLLECTING_V1',rootAuthority:ar,sourceIndex:a.sourceIndex,component:a.component,constructionDataReview:a.constructionDataReview,server:null,http:null,stdoutCapture:null,errors:[],applicationCopy:null,suiteCopy:null,testInventory:null,collectionCompletedCleanly:false,suiteAccepted:false,passed:false,fullNextAccepted:false};
 let host=null,closed=null,status=null,capture=null,captureDone=null,lease=null,stderrHandle=null,stdoutHandle=null,stopPromise=null,origin=null;
 async function sourceApp(){
  const tree=await walk(input.root);assert.deepEqual(tree.files.sort(),[...fileNames].sort());assert.deepEqual(tree.dirs.sort(),dirNames);
  const root=await inputStamp(input.root);for(const k of ['dev','ino','nlink'])assert.equal(root[k],rootIdentity.rootIdentity[k]);assert.equal(root.mode&0o777,rootIdentity.rootIdentity.mode);
  for(const r of input.directories){const s=await inputStamp(join(input.root,r.path));assert(s.isDirectory());assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}
  for(const r of input.files){const path=join(input.root,r.path),s=await inputStamp(path);assert(s.isFile()&&s.nlink===1);assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);await verify({path,sha256:r.sha256,bytes:r.bytes});}
 }
 async function copyTree(source,destination,rows,dirs){
  await mkdir(destination,{mode:0o700});for(const name of dirs.filter(x=>x!=='.').sort((a,b)=>a.split('/').length-b.split('/').length||a.localeCompare(b)))await mkdir(join(destination,name),{mode:0o700});
  for(const r of rows){const src=join(source,r.path),dst=join(destination,r.path);await copyFile(src,dst,fsConstants.COPYFILE_EXCL|fsConstants.COPYFILE_FICLONE);await chmod(dst,0o444);const s=await lstat(src),d=await lstat(dst);assert(d.nlink===1&&(s.dev!==d.dev||s.ino!==d.ino));await verify({path:dst,sha256:r.sha256,bytes:r.bytes});}
  for(const name of [...dirs].sort((a,b)=>b.length-a.length))await chmod(join(destination,name),0o555);
 }
 async function copyBookend(root,rows,dirs){
  const tree=await walk(root);assert.deepEqual(tree.files.sort(),rows.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),[...dirs].sort());
  for(const r of rows){const path=join(root,r.path),s=await lstat(path);assert(s.isFile()&&s.nlink===1&&(s.mode&0o777)===0o444);await verify({path,sha256:r.sha256,bytes:r.bytes});}
  for(const name of dirs){const path=join(root,name),s=await lstat(path);assert(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o555);assert.equal(await realpath(path),path);}
 }
 const suiteRows=[...suiteIndex.files,{path:'index.json',sha256:plan.suiteSourceIndex.sha256,bytes:plan.suiteSourceIndex.bytes}],suiteDirs=new Set(['.']);
 for(const r of suiteRows){let dir=dirname(r.path);while(dir!=='.'){suiteDirs.add(dir);dir=dirname(dir);}}
 function stopHost(reason){if(stopPromise)return stopPromise;stopPromise=(async()=>{if(!host)return;result.server.shutdownReason=reason;result.server.shutdownRequested=true;if(status===null){result.server.sigintSent=host.kill('SIGINT');try{await bounded(closed,plan.normalStopSeconds*1000,'Normal host stop deadline');}catch{result.server.forcedCleanup=true;host.kill('SIGKILL');await bounded(closed,plan.forcedStopSeconds*1000,'Forced host stop deadline');}}})();return stopPromise;}
 try{
  await sourceApp();await copyTree(input.root,app,input.files,dirNames);await copyBookend(app,input.files,dirNames);
  await copyTree(dirname(plan.suiteSourceIndex.path),suite,suiteRows,[...suiteDirs]);await copyBookend(suite,suiteRows,[...suiteDirs]);
  await mkdir(testRoot,{mode:0o700});assert.deepEqual(await readdir(testRoot),[]);assert.equal((await lstat(testRoot)).mode&0o777,0o700);
  result.applicationCopy={files:input.regularFiles,bytes:input.bytes,directoriesIncludingRoot:dirNames.length,independentInodes:true,byteIdentical:true,physicalFilesMode:'0444',physicalDirectoriesMode:'0555'};result.suiteCopy={files:suiteRows.length,bytes:suiteRows.reduce((n,x)=>n+x.bytes,0),byteIdentical:true,independentInodes:true};
  result.mounts=[{host:app,guest:'/app'},{host:suite,guest:'/cache-test-source'},{host:testRoot,guest:'/cache-tests'}];
  lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port:0,exclusive:true},yes);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');origin='http://127.0.0.1:'+address.port;
  result.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};await new Promise((yes,no)=>lease.close(e=>e?no(e):yes()));lease=null;
  stdoutHandle=await open(paths.stdout,'wx',0o600);stderrHandle=await open(paths.stderr,'wx',0o600);
  const args=['serve','--no-logging-prefix','--addr','127.0.0.1:'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s','--dir',app+'::/app','--dir',suite+'::/cache-test-source','--dir',testRoot+'::/cache-tests',a.component.path];assert(!args.includes('--env'));
  host=spawn(plan.wasmtime.path,args,{cwd:output,env:{PATH:'/usr/bin:/bin',LANG:'C',LC_ALL:'C'},stdio:['ignore','pipe',stderrHandle.fd],detached:false});result.server={argv:[plan.wasmtime.path,...args],pid:host.pid??null,freshProcess:true,spawnAttempts:1,shutdownRequested:false,sigintSent:false,forcedCleanup:false,shutdownReason:null,exit:null};
  let spawnError=null;closed=new Promise(yes=>{host.once('error',e=>{spawnError=errorData(e);});host.once('close',(code,signal)=>{status={code,signal,error:spawnError};result.server.exit=status;yes(status);});});
  const{captureRawStdout}=await import('./capture-stdout.mjs');capture=captureRawStdout({readable:host.stdout,handle:stdoutHandle,path:paths.stdout,limitBytes:plan.stdoutLimitBytes});stdoutHandle=null;
  void capture.failure.then(error=>{result.errors.push({stage:'stdout-capture-live',error});void stopHost('capture-failure').catch(e=>result.errors.push({stage:'capture-failure-stop',...errorData(e)}));});
  const until=Date.now()+plan.readinessSeconds*1000;let ready=false;
  while(Date.now()<until){assert.equal(status,null,'Host exited before listener');assert.equal(capture.failed,false);const text=await prefix(paths.stderr,plan.readinessPrefixBytes)+await prefix(paths.stdout,plan.readinessPrefixBytes);const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];if(found){assert.equal(found,origin);ready=true;break;}await sleep(plan.pollMilliseconds);}
  assert(ready,'Exact listener deadline');await tcp(address.port);assert.equal(status,null);result.readiness={exactListener:true,tcpConnectOnly:true,httpWarmupRequests:0};
  const response=await request(address.port,plan.httpSeconds,plan.httpBodyBytes),f=await open(paths.body,'wx',0o600);try{await f.writeFile(response.body);await f.sync();}finally{await f.close();}
  const{body,...fields}=response;result.http={...fields,method:'GET',path:'/cache-suite',body:await row(paths.body)};
 }catch(error){result.errors.push({stage:'collection',...errorData(error)});}
 finally{
  if(lease?.listening)try{await new Promise(yes=>lease.close(()=>yes()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
  try{await stopHost('request-collected');}catch(error){result.errors.push({stage:'host-stop',...errorData(error)});}
  if(capture){try{captureDone=await bounded(capture.done,plan.captureFinalizeSeconds*1000,'Stdout EOF/finalization deadline');}catch(error){result.errors.push({stage:'stdout-finalization',...errorData(error)});capture.abort('owned-finalization-deadline');try{captureDone=await bounded(capture.done,1000,'Aborted capture deadline');}catch(e){result.errors.push({stage:'stdout-abort-finalization',...errorData(e)});}}result.stdoutCapture=captureDone;}
  if(stdoutHandle){try{await stdoutHandle.sync();}catch(error){result.errors.push({stage:'unused-stdout-sync',...errorData(error)});}try{await stdoutHandle.close();}catch(error){result.errors.push({stage:'unused-stdout-close',...errorData(error)});}}
  if(stderrHandle){try{await stderrHandle.sync();}catch(error){result.errors.push({stage:'stderr-sync',...errorData(error)});}try{await stderrHandle.close();}catch(error){result.errors.push({stage:'stderr-close',...errorData(error)});}}
 }
 if(result.stdoutCapture?.complete){result.stdout=await row(paths.stdout);}
 result.stderrPath=paths.stderr;result.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 try{await sourceApp();await family(plan.suiteSourceIndex);await copyBookend(app,input.files,dirNames);await copyBookend(suite,suiteRows,[...suiteDirs]);await allInputBookends();for(const ref of [ar,a.sourceIndex,a.plan,plan.guestSourceIndex,plan.guestEntry,plan.applicationInventory,plan.applicationRootIdentity,...Object.values(plan.expectedBindings),...Object.values(plan.knownInputs)])await verify(ref);result.originalAndOwnedInputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...errorData(error)});result.originalAndOwnedInputsPreserved=false;}
 try{
  const tree=await walk(testRoot);assert(tree.files.length<=plan.testTreeFiles&&tree.dirs.length<=plan.testTreeDirectories);const rows=[];let bytes=0;
  for(const name of tree.files){const path=join(testRoot,name),s=await lstat(path);assert(s.size<=plan.testTreeFileBytes);bytes+=s.size;assert(bytes<=plan.testTreeBytes);rows.push({...await row(path),relativePath:name,mode:s.mode&0o777});}
  result.testInventory={files:rows,directories:tree.dirs,bytes,modeOrWasiRightsInferred:false};
 }catch(error){result.errors.push({stage:'owned-test-inventory',...errorData(error)});}
 const stopped=result.server?.shutdownReason==='request-collected'&&result.server.shutdownRequested&&result.server.sigintSent&&!result.server.forcedCleanup&&status?.code===0&&status.signal===null&&status.error===null;
 result.collectionCompletedCleanly=result.errors.length===0&&result.http?.complete===true&&result.http.error===null&&!result.http.overflow&&result.stdoutCapture?.complete===true&&stopped&&result.originalAndOwnedInputsPreserved===true;
 // Interpretation follows original child shutdown + complete stdout finalization, never live output.
 if(result.http?.complete&&!result.http.overflow){try{
  const value=JSON.parse(await readFile(paths.body,'utf8'));result.parsedResponse=await save(paths.response,value);
  const report=value.report;result.suiteAccepted=result.collectionCompletedCleanly&&result.http.status===200&&value.marker==='NEXT_NODE_FS_ATOMIC_COMPONENT_V1'&&value.suiteFulfilled===true&&value.originalRejection===null&&value.passed===true&&report?.passed===true&&report.executionKind==='wasm-guest'&&report.guestExecuted===true&&report.guestExecutedRequiresExternalParentProof===true&&Array.isArray(report.unattemptedCaseIds)&&report.unattemptedCaseIds.length===0&&Array.isArray(report.cases)&&report.cases.length===plan.expectedCaseIds.length&&report.assertions===11&&report.actualNextHelperUsed===true&&report.fakeDependencies===false&&report.helperImplementationModified===false&&report.cases.every((x,i)=>x.id===plan.expectedCaseIds[i]&&x.passed===true&&Array.isArray(x.assertions)&&x.assertions.length===[4,4,3][i]&&x.assertions.every(a=>a.passed===true));
 }catch(error){result.errors.push({stage:'final-response-json',...errorData(error)});}}
 result.passed=result.collectionCompletedCleanly&&result.suiteAccepted&&result.errors.length===0;result.state=result.passed?'NEXT_NODE_FS_ATOMIC_RUNTIME_PASSED_UNREVIEWED_V1':'NEXT_NODE_FS_ATOMIC_RUNTIME_FAILED_RAW_PRESERVED_V1';
 await save(paths.result,result);console.log(JSON.stringify({collectionCompletedCleanly:result.collectionCompletedCleanly,suiteAccepted:result.suiteAccepted,passed:result.passed,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
