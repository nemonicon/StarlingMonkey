// Dormant actual WT deployment orchestration, permitted only by late Root authority.
// Builtins only; neither generated guest modules nor packaging APIs are imported.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {createReadStream} from 'node:fs';
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
const authorityPath=resolve(process.argv[2]),authority=await read(authorityPath),plan=await read(join(here,'plan.json'));
assert.equal(authority.state,'ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2');
assert.deepEqual(authority.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(authority.plan,await row(join(here,'plan.json')));
for(const key of ['localhostServeAllowed','actualNextGuestAllowed','browserAllowed'])assert.equal(authority[key],true);
for(const key of ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed'])assert.equal(authority[key],false);
assert(authority.constructionCallerIndex&&typeof authority.constructionCallerIndex.path==='string','Exact late Root constructor index is mandatory');
assert.equal(resolve(authority.constructionCallerIndex.path),authority.constructionCallerIndex.path);assert.equal(await realpath(authority.constructionCallerIndex.path),authority.constructionCallerIndex.path);assert.equal(authority.constructionCallerIndex.path.split('/').at(-1),'index.json');
async function protect(){await family(authority.sourceIndex);await family(authority.constructionCallerIndex);for(const ref of plan.sourceFamilies)await family(ref);for(const r of plan.protectedInputs)await verify(r);}
await protect();await verify(authority.constructionResult);await verify(authority.component);await verify(authority.componentAudit);
const construction=await read(authority.constructionResult.path),audit=await read(authority.componentAudit.path);
assert.equal(construction.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(construction.passed,true);assert.equal(construction.entryMode,'real-next');
assert.deepEqual(construction.artifacts.component,authority.component);assert.deepEqual(construction.artifacts.componentAudit,authority.componentAudit);
assert.deepEqual(construction.callerIndex,authority.constructionCallerIndex);assert.equal(construction.finalProtection.unchanged,true);assert.equal(construction.error,null);
for(const key of ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'])assert.equal(construction[key],false);
assert(Array.isArray(construction.artifacts.engineBuildEvidence)&&construction.artifacts.engineBuildEvidence.length>0);
const artifactRefs=[authority.constructionResult,authority.component,authority.componentAudit,construction.rootAuthority,construction.callerIndex,construction.plan,...construction.artifacts.engineBuildEvidence];
for(const key of ['engine','nativeMetadata','inputSourceIndex','inputEntry','adapter','returnedImports','returnedOwnShape'])artifactRefs.push(construction.artifacts[key]);
async function artifactBookend(){for(const ref of artifactRefs)await verify(ref);}
await artifactBookend();
assert.deepEqual(construction.artifacts.inputEntry,plan.guestEntry);
assert.equal(audit.schemaVersion,1);assert.equal(audit.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(audit.passed,true);assert.deepEqual(audit.component,authority.component);
assert.deepEqual([...audit.selectedInterfaces].sort(),[...plan.selectedInterfaces].sort());assert.equal(new Set(audit.selectedInterfaces).size,13);
assert.equal(new Set(audit.emittedImports).size,audit.emittedImports.length);assert(audit.emittedImports.every(x=>plan.selectedInterfaces.includes(x)&&x.endsWith('@0.2.10')));
assert(Array.isArray(audit.unusedSelectedInterfaces));assert.deepEqual([...audit.unusedSelectedInterfaces].sort(),plan.selectedInterfaces.filter(x=>!audit.emittedImports.includes(x)).sort());
assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);assert.equal(audit.allEmittedVersion,'0.2.10');assert.equal(audit.noExternalPreview1OrCustomImports,true);
for(const key of ['validateTerminal','witTerminal']){await verify(audit[key]);const t=await read(audit[key].path);assert.equal(t.rawExitCode,0);assert.equal(t.timeout,false);assert.equal(t.forcedCleanup,false);assert.equal(t.parentOwnedGroupGone,true);assert.equal(t.allObservedOwnedGroupsGone,true);for(const k of ['signals','errors','interruptedSignals','remainingObservedPids'])assert.deepEqual(t[k],[]);artifactRefs.push(audit[key],t.stdout,t.stderr);}
await verify(plan.applicationInputs);const input=await read(plan.applicationInputs.path);assert.equal(input.root,plan.applicationSource);
async function sourceBookend(){assert.equal(await realpath(input.root),input.root);const tree=await walk(input.root);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),input.directories.map(x=>x.path).sort());for(const r of input.files){const path=join(input.root,r.path),s=await lstat(path);await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);}for(const r of input.directories){const s=await lstat(join(input.root,r.path));assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}}
await sourceBookend();
const output=plan.outputRoot,app=join(output,'app'),cache=join(output,'cache');await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'NEXT_WASMTIME_DEPLOYMENT_IN_PROGRESS_V2',component:authority.component,componentAudit:authority.componentAudit,constructionResult:authority.constructionResult,rootAuthority:await row(authorityPath),sourceIndex:authority.sourceIndex,selectedInterfaces:plan.selectedInterfaces,emittedImports:audit.emittedImports,errors:[],server:null,client:null,originalInputsPreserved:false,readonlyAppPreserved:false,adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function boundedWait(promise,ms){let timer;try{await Promise.race([promise,new Promise(resolve=>{timer=setTimeout(resolve,ms);})]);}finally{clearTimeout(timer);}}
const handles=[];let host,hostExit=null,hostDone,stopping=false,lease;
async function launch(exe,args,id){const stdout=join(output,id+'.stdout.log'),stderr=join(output,id+'.stderr.log'),out=await open(stdout,'wx',0o600),err=await open(stderr,'wx',0o600);handles.push(out,err);const child=spawn(exe,args,{cwd:output,stdio:['ignore',out.fd,err.fd],env:{...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}});let status=null;const done=new Promise(resolve=>{child.once('error',error=>{status={code:null,signal:null,error:errorData(error)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});return{child,done,stdout,stderr,get status(){return status;},command:[exe,...args]};}
async function readonlyBookend(){const tree=await walk(app);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),input.directories.map(x=>x.path).sort());for(const r of input.files){const q=join(app,r.path),s=await lstat(q);await verify({path:q,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,0o444);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}for(const r of input.directories)assert.equal((await lstat(join(app,r.path))).mode&0o777,0o555);}
try{
 await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true});
 for(const r of input.files)await chmod(join(app,r.path),0o444);for(const r of [...input.directories].sort((a,b)=>b.path.length-a.path.length))await chmod(join(app,r.path),0o555);
 await readonlyBookend();await mkdir(cache,{mode:0o700});assert.equal((await lstat(cache)).mode&0o777,0o700);
 assert((await lstat(join(app,'.next/cache'))).isDirectory(),'Readonly parent/cache path must physically exist');
 result.mounts=[{host:app,guest:'/app',physicalDirectoryMode:'0555',physicalFileMode:'0444'},{host:cache,guest:'/app/.next/cache',physicalRootMode:'0700'}];result.applicationCopy={files:input.regularFiles,bytes:input.bytes,byteIdentical:true,independentInodes:true};
 lease=createServer();lease.on('error',()=>{});await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');
 const origin='http://127.0.0.1:'+address.port;result.portLease={address:address.address,port:address.port,origin,heldUntilImmediatelyBeforeSingleLaunch:true,fallbackAllowed:false};await save();
 const args=['serve','--addr',address.address+':'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--env','STARLING_NEXT_ORIGIN='+origin,'--env','NODE_ENV=production','--env','NEXT_TELEMETRY_DISABLED=1','--dir',app+'::/app','--dir',cache+'::/app/.next/cache','--max-instance-reuse-count','128','--idle-instance-timeout','60s',authority.component.path];
 await protect();await artifactBookend();
 await new Promise((resolve,reject)=>lease.close(error=>error?reject(error):resolve()));lease=null;result.portLease.releasedBeforeSpawn=true;
 const server=await launch(plan.wasmtime.path,args,'wasmtime');host=server.child;hostDone=server.done;void hostDone.then(status=>{hostExit=status;if(!stopping)result.errors.push({stage:'server-exited-before-owned-shutdown',status});});result.server={command:server.command,pid:host.pid??null,stdout:server.stdout,stderr:server.stderr,plannedGracefulStop:'SIGINT',forcedCleanup:false};await save();
 const deadline=Date.now()+60000;let ready=false;
 while(Date.now()<deadline){if(hostExit)throw Error('Wasmtime exited before readiness');let logs='';for(const path of [server.stdout,server.stderr]){const s=await lstat(path);assert(s.size<=8388608,'Readiness log exceeds8MiB; full bytes retained');logs+=await readFile(path,'utf8');}const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs)?.[1];if(found){assert.equal(found,origin,'Port lease race/origin mismatch: never fallback');ready=true;break;}await pause(50);}
 assert(ready,'Wasmtime did not report exact listener within60s');result.server.readyOrigin=origin;await save();
 const client=await launch(plan.node.path,[join(here,'run-contracts.mjs'),origin,join(output,'client'),plan.browserTools],'client');result.client={command:client.command,pid:client.child.pid??null,stdout:client.stdout,stderr:client.stderr};await save();const status=await client.done;result.client.exit=status;result.client.result=await row(join(output,'client/result.json'));const observed=await read(result.client.result.path);assert.deepEqual(status,{code:0,signal:null,error:null});assert.equal(observed.passed,true);assert.equal(hostExit,null,'Server must remain live through full contracts');result.contractsPassed=true;
}catch(error){result.errors.push({stage:'deployment-or-contracts',...errorData(error)});}
finally{
 if(lease)await new Promise(resolve=>lease.close(()=>resolve()));
 if(host&&!hostExit){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.kill('SIGINT');await boundedWait(hostDone,5000);if(!hostExit){result.server.forcedCleanup=true;result.server.sigkillSent=host.kill('SIGKILL');await boundedWait(hostDone,5000);}}
 if(result.server){result.server.exit=hostExit;for(const k of ['stdout','stderr'])result.server[k]=await row(result.server[k]);}
 if(result.client)for(const k of ['stdout','stderr'])result.client[k]=await row(result.client[k]);
 for(const handle of handles)try{await handle.close();}catch(error){result.errors.push({stage:'raw-stream-close',...errorData(error)});}
 try{await sourceBookend();await protect();await artifactBookend();result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'source-final-protection',...errorData(error)});}
 try{await readonlyBookend();result.readonlyAppPreserved=true;}catch(error){result.errors.push({stage:'readonly-app-final',...errorData(error)});}
 result.cacheInventory=[];try{const tree=await walk(cache);assert.equal(tree.links.length,0);for(const name of tree.files){const path=join(cache,name);result.cacheInventory.push({...await row(path),relativePath:name,mode:(await lstat(path)).mode&0o777});}}catch(error){result.errors.push({stage:'cache-final-inventory',...errorData(error)});}
 result.passed=result.contractsPassed===true&&result.errors.length===0&&result.originalInputsPreserved&&result.readonlyAppPreserved&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&hostExit?.code===0&&hostExit?.signal===null&&hostExit?.error===null;
 result.state=result.passed?'NEXT_WASMTIME_DEPLOYMENT_CONTRACTS_PASSED_UNREVIEWED_V2':'NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2';await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,errors:result.errors}));process.exitCode=result.passed?0:1;
