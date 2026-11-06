// Dormant host observer. Guest execution requires late authenticated Root grant.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {createReadStream} from 'node:fs';
import {readFile,mkdir,cp,chmod,lstat,readdir,realpath,open} from 'node:fs/promises';
import {join,dirname,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url)),pause=ms=>new Promise(r=>setTimeout(r,ms));
const read=async path=>JSON.parse(await readFile(path,'utf8'));
async function row(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
async function verify(r){assert.deepEqual(await row(r.path),r,r.path);}
async function write(path,bytes,exclusive=false){const f=await open(path,exclusive?'wx':'w',0o600);try{await f.writeFile(bytes);await f.sync();}finally{await f.close();}}
const errorData=e=>({name:e?.name??typeof e,message:e?.message??String(e),stack:e?.stack??null});
async function tree(root){const result={files:[],dirs:['.']};async function visit(folder){for(const name of(await readdir(folder)).sort()){const path=join(folder,name),s=await lstat(path);assert(!s.isSymbolicLink(),'No symlinks');if(s.isDirectory()){result.dirs.push(relative(root,path));await visit(path);}else{assert(s.isFile());result.files.push(relative(root,path));}}}await visit(root);return result;}
async function family(ref){await verify(ref);const root=dirname(ref.path),index=await read(ref.path),names=index.files.map(x=>x.path);assert.equal(new Set(names).size,names.length);assert.deepEqual((await tree(root)).files.filter(x=>x!=='index.json').sort(),[...names].sort());for(const r of index.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));await verify({...r,path:join(root,r.path)});}}
export function validateResponse(body,{ids,method,bodyBytes}){
 assert.equal(body.marker,'NEXT_NATIVE_DEPENDENCIES_OK');assert(Array.isArray(body.records));assert.equal(body.records.length,16);
 assert.deepEqual(body.records.map(x=>x.id),ids);for(const r of body.records)assert.equal(r.passed,true,r.id);
 const http=body.records.find(x=>x.id==='http-adapter');assert.deepEqual(http.value,{method,pathname:'/dependencies',bodyBytes});
 const barriers=body.snapshotBarriers;assert.equal(barriers.deployedResetAttempted,false);assert.equal(barriers.deployedResnapshotAttempted,false);assert.equal(barriers.nativeSnapshotGuardRuntimeProof,false);
 assert.equal(body.records.find(x=>x.id==='rng-deployed-shapes').value.secretValuesRetained,false);
}
async function main(authorityPath){
 assert.equal(process.version,'v22.14.0');const a=await read(authorityPath),p=await read(join(HERE,'plan.json'));
 assert.equal(a.schemaVersion,1);assert.equal(a.state,'ROOT_NEXT_INTL_DEPENDENCIES_WASMTIME_AUTHORIZED_V1');assert.match(a.runId,/^[a-z0-9][a-z0-9-]{0,48}$/);
 for(const k of ['localhostServeAllowed','dependencyGuestAllowed'])assert.equal(a[k],true);
 for(const k of ['fullNextApplicationAllowed','compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed'])assert.equal(a[k],false);
 assert.deepEqual(a.engine,p.engine);assert.deepEqual(a.nativeMetadata,p.nativeMetadata);assert.deepEqual(a.constructorSourceIndex,p.expectedConstructorSourceIndex);assert.deepEqual(a.inputSourceIndex,p.expectedInputSourceIndex);assert.deepEqual(a.inputEntry,p.expectedInputEntry);
 assert.deepEqual(a.sourceIndex,await row(join(HERE,'index.json')));assert.deepEqual(a.plan,await row(join(HERE,'plan.json')));
 const authorityRow=await row(authorityPath),fixed=[p.node,p.wasmtime,p.monitor,p.applicationInputs,a.engine,a.nativeMetadata];
 async function protect(){await verify(authorityRow);await family(a.sourceIndex);await family(a.constructorSourceIndex);await family(a.inputSourceIndex);await verify(a.inputEntry);const index=await read(a.inputSourceIndex.path);assert(index.files.some(r=>join(dirname(a.inputSourceIndex.path),r.path)===a.inputEntry.path&&r.sha256===a.inputEntry.sha256&&r.bytes===a.inputEntry.bytes),'Exact late entry must be an indexed family member');for(const r of fixed)await verify(r);for(const k of ['constructionResult','component','componentAudit'])await verify(a[k]);for(const ref of p.nativeProtectedInputs)await verify(ref);}
 await protect();const construction=await read(a.constructionResult.path),audit=await read(a.componentAudit.path);
 assert.equal(construction.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(construction.passed,true);assert.equal(construction.entryMode,'dependencies');assert.equal(construction.error,null);assert.equal(construction.finalProtection.unchanged,true);
 assert.deepEqual(construction.callerIndex,a.constructorSourceIndex);for(const [key,ref]of Object.entries({component:a.component,componentAudit:a.componentAudit,inputEntry:a.inputEntry,inputSourceIndex:a.inputSourceIndex,engine:a.engine,nativeMetadata:a.nativeMetadata}))assert.deepEqual(construction.artifacts[key],ref);
 for(const k of ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'])assert.equal(construction[k],false);
 const artifactRefs=[construction.rootAuthority,construction.callerIndex,construction.plan,...construction.artifacts.engineBuildEvidence];
 for(const k of ['inputEntry','inputSourceIndex','engine','nativeMetadata','adapter','returnedImports','returnedOwnShape'])artifactRefs.push(construction.artifacts[k]);
 async function artifacts(){for(const r of artifactRefs)await verify(r);}await artifacts();
 const {validateNative}=await import('./native-model.mjs');validateNative(await read(a.nativeMetadata.path),p);
 assert.equal(audit.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(audit.passed,true);assert.deepEqual(audit.component,a.component);assert.deepEqual([...audit.selectedInterfaces].sort(),[...p.selectedInterfaces].sort());assert.equal(p.selectedInterfaces.length,13);assert.equal(new Set(audit.emittedImports).size,audit.emittedImports.length);assert(audit.emittedImports.every(x=>p.selectedInterfaces.includes(x)&&x.endsWith('@0.2.10')));assert.deepEqual(audit.exports,[p.expectedExport]);assert.equal(audit.noExternalPreview1OrCustomImports,true);assert.equal(audit.allEmittedVersion,'0.2.10');
 assert.deepEqual([...audit.unusedSelectedInterfaces].sort(),p.selectedInterfaces.filter(x=>!audit.emittedImports.includes(x)).sort());
 for(const key of ['validateTerminal','witTerminal']){await verify(audit[key]);const t=await read(audit[key].path);assert.equal(t.rawExitCode,0);assert.equal(t.timeout,false);assert.equal(t.forcedCleanup,false);assert.equal(t.parentOwnedGroupGone,true);assert.equal(t.allObservedOwnedGroupsGone,true);for(const k of ['signals','errors','interruptedSignals','remainingObservedPids'])assert.deepEqual(t[k],[]);artifactRefs.push(audit[key],t.stdout,t.stderr);}
 const input=await read(p.applicationInputs.path);assert.equal(input.root,p.applicationSource);assert.equal(input.regularFiles,2218);
 async function appCheck(root,copy){assert.equal(await realpath(root),root);const actual=await tree(root);assert.deepEqual(actual.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(actual.dirs.sort(),input.directories.map(x=>x.path).sort());for(const r of input.files){const path=join(root,r.path),s=await lstat(path);await verify({path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,copy?0o444:r.mode);if(copy){assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}else{assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);}}for(const r of input.directories){const s=await lstat(join(root,r.path));assert.equal(s.mode&0o777,copy?0o555:r.mode);if(!copy){assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}}}
 await appCheck(input.root,false);const output=p.outputPrefix+'-'+a.runId,app=join(output,'app');await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,state:'NEXT_INTL_DEPENDENCIES_WASMTIME_RUNNING_V1',authority:authorityRow,plan:a.plan,component:a.component,componentAudit:a.componentAudit,constructionResult:a.constructionResult,inputEntry:a.inputEntry,inputSourceIndex:a.inputSourceIndex,requests:[],errors:[],passed:false,hostLaunchAttempted:false,ordinaryRequestAttempts:0,fullNextApplicationServed:false,adoption:false,sameInstanceIdentityProved:false};
 const save=()=>write(join(output,'result.json'),JSON.stringify(result,null,2)+'\n');await save();let lease,host,hostDone,hostExit=null,stopping=false;const handles=[];
 try{
  await cp(input.root,app,{recursive:true,force:false,errorOnExist:true,verbatimSymlinks:true});for(const r of input.files)await chmod(join(app,r.path),0o444);for(const r of [...input.directories].sort((a,b)=>b.path.length-a.path.length))await chmod(join(app,r.path),0o555);await appCheck(app,true);result.appCopy={files:2218,bytes:input.bytes,readonlyFiles:0o444,readonlyDirectories:0o555,independentFileInodes:true};
  lease=createServer();await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;
  const args=['serve','--addr','127.0.0.1:'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--env','STARLING_NEXT_ORIGIN='+origin,'--env','NODE_ENV=production','--env','NEXT_TELEMETRY_DISABLED=1','--dir',app+'::/app','--max-instance-reuse-count','32','--idle-instance-timeout','60s',a.component.path];
  result.origin=origin;result.server={argv:[p.wasmtime.path,...args],stdout:join(output,'wasmtime.stdout.log'),stderr:join(output,'wasmtime.stderr.log'),forcedCleanup:false};await save();await protect();await artifacts();
  const stdout=await open(result.server.stdout,'wx',0o600);handles.push(stdout);const stderr=await open(result.server.stderr,'wx',0o600);handles.push(stderr);await new Promise((resolve,reject)=>lease.close(e=>e?reject(e):resolve()));lease=null;
  result.hostLaunchAttempted=true;await save();host=spawn(p.wasmtime.path,args,{stdio:['ignore',stdout.fd,stderr.fd],env:{...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}});result.server.pid=host.pid??null;
  hostDone=new Promise(resolve=>{host.once('error',e=>{hostExit={code:null,signal:null,error:errorData(e)};resolve();});host.once('exit',(code,signal)=>{hostExit={code,signal,error:null};if(!stopping)result.errors.push({stage:'host-exited-before-owned-stop',status:hostExit});resolve();});});await save();
  const deadline=Date.now()+30000;let ready=false;while(Date.now()<deadline){assert.equal(hostExit,null,'Wasmtime exited before readiness');const text=await readFile(result.server.stderr,'utf8');const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];if(found){assert.equal(found,origin,'Lease race: no fallback port');ready=true;break;}await pause(50);}assert(ready,'No exact stock Wasmtime readiness');result.server.ready=true;await save();
  for(let ordinal=1;ordinal<=3;ordinal++){
   const method=ordinal===3?'POST':'GET',body=method==='POST'?p.postBody:undefined;result.ordinaryRequestAttempts++;await save();const before=Date.now();const response=await fetch(origin+'/dependencies?request='+ordinal,{method,body,redirect:'error',headers:{connection:'close',...(body?{'content-type':'text/plain; charset=utf-8'}:{})},signal:AbortSignal.timeout(p.requestTimeoutMs)});const bytes=Buffer.from(await response.arrayBuffer()),path=join(output,'response-'+ordinal+'.body');await write(path,bytes,true);
   const record={ordinal,method,status:response.status,headers:[...response.headers],beforeWallMs:before,afterWallMs:Date.now(),rawBody:await row(path)};result.requests.push(record);await save();record.body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));await save();assert.equal(response.status,200);validateResponse(record.body,{ids:p.recordIds,method,bodyBytes:body?Buffer.byteLength(body):0});record.passed=true;await save();
  }
  assert.equal(hostExit,null);result.semanticChecksPassed=true;
 }catch(e){result.errors.push({stage:'host-or-dependency-control',...errorData(e)});}
 finally{
  if(lease)await new Promise(resolve=>lease.close(()=>resolve()));
  if(host&&!hostExit){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.kill('SIGINT');await Promise.race([hostDone,pause(5000)]);if(!hostExit){result.server.forcedCleanup=true;host.kill('SIGKILL');await Promise.race([hostDone,pause(5000)]);}}
  if(result.server)result.server.exit=hostExit;for(const handle of handles)try{await handle.sync();await handle.close();}catch(e){result.errors.push({stage:'stdio-sync-close',...errorData(e)});}
  for(const key of ['stdout','stderr'])if(result.server&&typeof result.server[key]==='string')try{result.server[key]=await row(result.server[key]);}catch(e){result.errors.push({stage:'raw-stdio-retention',...errorData(e)});}
  try{await protect();await artifacts();await appCheck(input.root,false);result.originalInputsPreserved=true;}catch(e){result.errors.push({stage:'original-final-protection',...errorData(e)});}
  try{await appCheck(app,true);result.readonlyCopyPreserved=true;}catch(e){result.errors.push({stage:'app-copy-final-protection',...errorData(e)});}
  result.passed=result.semanticChecksPassed===true&&result.requests.length===3&&result.requests.every(x=>x.passed===true)&&result.errors.length===0&&result.originalInputsPreserved===true&&result.readonlyCopyPreserved===true&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&hostExit?.code===0&&hostExit?.signal===null&&hostExit?.error===null;
  result.state=result.passed?'NEXT_INTL_DEPENDENCIES_WASMTIME_PASSED_UNREVIEWED_V1':'NEXT_INTL_DEPENDENCIES_WASMTIME_FAILED_UNACCEPTED_V1';await save();
 }
 console.log(JSON.stringify({state:result.state,passed:result.passed,requests:result.requests.length,errors:result.errors}));return result.passed?0:1;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))main(resolve(process.argv[2])).then(code=>{process.exitCode=code;},e=>{console.error(JSON.stringify(errorData(e)));process.exitCode=1;});
