// Host ownership/capture helpers derived from held direct-control/single-probe Sources.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {readFile,readdir,lstat,realpath,open} from 'node:fs/promises';
import {dirname,relative,resolve,join} from 'node:path';
import {spawn} from 'node:child_process';
import {createConnection} from 'node:net';

export const read=async path=>JSON.parse(await readFile(path,'utf8'));
export const errorData=e=>({type:typeof e,isNull:e===null,name:e?.name??null,message:e?.message??String(e),stack:e?.stack??null,code:e?.code??null});
export async function row(path){const hash=createHash('sha256');let bytes=0;for await(const block of createReadStream(path)){hash.update(block);bytes+=block.length;}return{path,sha256:hash.digest('hex'),bytes};}
export async function verify(ref){assert.equal(resolve(ref.path),ref.path);assert.equal(await realpath(ref.path),ref.path);const s=await lstat(ref.path);assert(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1);assert.deepEqual(await row(ref.path),ref);}
export async function walk(root){const files=[],dirs=['.'];async function visit(path){for(const name of(await readdir(path)).sort()){const q=join(path,name),s=await lstat(q);assert(!s.isSymbolicLink());if(s.isDirectory()){dirs.push(relative(root,q));await visit(q);}else{assert(s.isFile()&&s.nlink===1);files.push(relative(root,q));}}}await visit(root);return{files:files.sort(),dirs:dirs.sort()};}
export async function family(ref){await verify(ref);const root=dirname(ref.path),index=await read(ref.path),names=index.files.map(r=>r.path);assert.equal(new Set(names).size,names.length);const dirs=new Set(['.']);for(const name of names){assert(!name.startsWith('/')&&name.split('/').every(x=>x&&x!=='.'&&x!=='..'));for(let p=dirname(name);p!=='.';p=dirname(p))dirs.add(p);}const actual=await walk(root);assert.deepEqual(actual.files,[...names,'index.json'].sort());assert.deepEqual(actual.dirs,[...dirs].sort());for(const r of index.files)await verify({...r,path:join(root,r.path)});}
export async function durable(path,value,fresh=false){const h=await open(path,fresh?'wx':'w',0o600);try{await h.writeFile(value);await h.sync();}finally{await h.close();}}
export const jsonBytes=value=>JSON.stringify(value,null,2)+'\n';
export const pause=ms=>new Promise(r=>setTimeout(r,ms));
export async function waitBounded(promise,ms){let timer;try{return await Promise.race([promise,new Promise(r=>{timer=setTimeout(()=>r(null),ms);})]);}finally{clearTimeout(timer);}}
export function originPort(value){assert(typeof value==='string'&&/^http:\/\/127\.0\.0\.1:([1-9][0-9]{0,4})$/.exec(value)?.[0]===value);const url=new URL(value),port=Number(url.port);assert.equal(url.origin,value);assert(port>=1&&port<=65535&&port!==80);return port;}
export function layout(plan,id){assert(typeof id==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(id)?.[0]===id);assert.equal(plan.outputPrefix,'/private/tmp/starling-node-compat/next-response-gzip-composition');return plan.outputPrefix+'-'+id;}
export const ownershipClean=t=>t&&Number.isInteger(t.rawExitCode)&&t.timeout===false&&t.forcedCleanup===false&&t.parentOwnedGroupGone===true&&t.allObservedOwnedGroupsGone===true&&['errors','signals','interruptedSignals','remainingObservedPids'].every(k=>Array.isArray(t[k])&&t[k].length===0)&&t.finalGroups.length>0&&t.finalGroups.every(g=>g.alive===false&&g.signalAllowed===false);
export const clean=t=>ownershipClean(t)&&t.rawExitCode===0;
export async function tcpOnce(port,ms){return new Promise(resolve=>{const socket=createConnection({host:'127.0.0.1',port});let done=false;const finish=ok=>{if(done)return;done=true;socket.destroy();resolve(ok);};socket.once('connect',()=>finish(true));socket.once('error',()=>finish(false));socket.setTimeout(ms,()=>finish(false));});}
export async function launch(invocation,label,output,handles,children){
 const out=await open(join(output,label+'.stdout.log'),'wx',0o600);handles.push(out);
 const err=await open(join(output,label+'.stderr.log'),'wx',0o600);handles.push(err);
 const child=spawn(invocation.exe,invocation.args,{cwd:invocation.cwd,env:invocation.env,stdio:['ignore',out.fd,err.fd]});let status=null;
 const done=new Promise(resolve=>{const finish=value=>{if(status!==null)return;status=value;resolve(value);};child.once('error',error=>finish({code:null,signal:null,error:errorData(error)}));child.once('exit',(code,signal)=>finish({code,signal,error:null}));});
 const item={child,done,get status(){return status;},record:{label,argv:[invocation.exe,...invocation.args],cwd:invocation.cwd,environment:invocation.env,pid:child.pid??null,stdout:join(output,label+'.stdout.log'),stderr:join(output,label+'.stderr.log'),exit:null}};children.push(item);return item;
}
export async function context(here,path){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert.equal(process.env.NODE_OPTIONS,undefined);
 const plan=await read(join(here,'plan.json'));assert.equal(plan.prospectiveActualBindingsPending,false,'Actual gzip INIT/build bindings pending');
 const authorityRef=await row(path),a=await read(path);assert.equal(a.state,'ROOT_GZIP_COMPOSITION_RUNTIME_AUTHORIZED_V1');
 assert.deepEqual(a.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(a.plan,await row(join(here,'plan.json')));
 for(const k of ['controllerAllowed','nodeReferenceAllowed','guestAllowed','hostProbeRequestAllowed','rawWireCaptureAllowed','dataValidationAllowed'])assert.equal(a[k],true);
 for(const k of ['nodeControlAllowed','componentConstructionAllowed','nativeBuildAllowed','compilerAllowed','cargoAllowed','browserAllowed','applicationSourceMutationAllowed','appMountAllowed','fixtureStagingAllowed','networkBeyondLoopbackAllowed','fullNextAcceptanceAllowed','adoptionAllowed'])assert.equal(a[k],false);
 originPort(a.origin);assert(!['argv','environment','outputRoot','monitorOutputRoot'].some(k=>Object.hasOwn(a,k)));
 assert.equal(Object.keys(plan.expectedBindings).length,15);
 for(const[k,v]of Object.entries(plan.expectedBindings)){assert(v&&typeof v==='object');assert.deepEqual(a[k],v);}
 for(const[phase,key]of [['reference','nodeReferenceAuthority'],['wire','wireAuthority']]){
  const grant=await read(a[key].path);assert.equal(grant.state,'ROOT_GZIP_COMPOSITION_PHASE_AUTHORIZED_V1');assert.equal(grant.phase,phase);assert.equal(grant.operationAllowed,true);
  for(const k of ['sourceIndex','plan','runId','origin'])assert.deepEqual(grant[k],a[k]);
  assert.equal(grant.nodeReferenceAllowed,phase==='reference');assert.equal(grant.rawWireCaptureAllowed,phase==='wire');
  for(const k of ['guestAllowed','buildAllowed','constructorAllowed','browserAllowed','appMountAllowed','networkBeyondLoopbackAllowed'])assert.equal(grant[k],false);
  assert(!['parentAuthority','argv','environment','outputRoot'].some(k=>Object.hasOwn(grant,k)));
 }
 async function protect(){await verify(authorityRef);await family(a.sourceIndex);for(const ref of [...plan.sourceFamilies,...a.nativeSourceFamilies])await family(ref);for(const ref of [...plan.protectedInputs,...Object.values(plan.expectedBindings),a.nodeReferenceAuthority,a.wireAuthority,...a.engineBuildEvidence,...a.nativeProtectedInputs,...a.worldInputs])await verify(ref);}
 await protect();return{a,plan,authorityRef,protect};
}
