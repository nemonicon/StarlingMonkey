// Dormant actual both-host action. Only the source-authenticated bootstrap calls it.
import {mkdir,readFile,lstat,readdir,copyFile,statfs} from 'node:fs/promises';
import {constants,createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {createServer} from 'node:net';
import {join,relative,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {assertHostSources} from './source-auth.mjs';
import {need,descriptor,hash} from '../http-host-candidate-v1/authority.mjs';
import {DurableOutput} from '../http-host-candidate-v1/durable.mjs';
import {streamHash} from '../http-host-candidate-v1/physical.mjs';
import {hostPreflight} from './guard.mjs';
import {runOwnedCommand} from '../http-host-candidate-v1/commands.mjs';
import {ownedServer} from '../http-host-candidate-v1/server.mjs';
import {ENV,inheritedHomePaths,readinessRetryAllowed,loopback,washConfig,effectiveWash,gracefulServer,SIX,EXPORTS,same} from './models.mjs';
import {validateResponse,validateBoth} from '../http-host-candidate-v1/validate.mjs';
import {captureResponse,captureSetSummary} from './response-capture.mjs';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
function child(root,path){const name=relative(root,path);need(name&&!isAbsolute(name)&&!name.startsWith('../')&&!name.includes('\\')&&name.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Owned relative evidence path');return name;}
async function disk(root,minimum){const s=await statfs(root);need(s.bavail*s.bsize>=minimum,'Operational disk headroom, no capacity guarantee');}
async function adopt(output,path=output.root){for(const item of await readdir(path,{withFileTypes:true})){const full=join(path,item.name),s=await lstat(full);need(!s.isSymbolicLink(),'No unaccounted output symlink');if(s.isDirectory())await adopt(output,full);else{need(s.isFile()&&s.nlink===1&&s.size<=1024**3,'Ordinary independently owned bounded evidence file');const digest=createHash('sha256');let bytes=0;for await(const raw of createReadStream(full)){digest.update(raw);bytes+=raw.length;}const after=await lstat(full);need(s.dev===after.dev&&s.ino===after.ino&&s.size===after.size&&s.mtimeMs===after.mtimeMs&&s.ctimeMs===after.ctimeMs&&bytes===s.size,'Stable complete output read');const name=child(output.root,full);output.rows.set(name,{path:name,sha256:digest.digest('hex'),bytes});need(output.rows.size<=10000,'Finite full host/caches output inventory');}}}
export async function runHosts(options,source){
 assertHostSources(source,options.sourceIndex);const a=await hostPreflight(options);await disk('/private/tmp/starling-node-compat',2*1024**3);await source.recheck();await a.recheck();
 const output=await DurableOutput.create(a.root.outputRoot),reports={},responseCaptures=[],write=(name,v)=>output.write(name,v,{json:true});
 try{
  await mkdir(join(output.root,'processes'),{mode:0o700});
  const inheritedPaths=inheritedHomePaths(process.env),processEnv={...ENV,...inheritedPaths,TMPDIR:join(output.root,'private-env/tmp'),XDG_CACHE_HOME:join(output.root,'private-env/cache'),XDG_CONFIG_HOME:join(output.root,'private-env/config'),XDG_DATA_HOME:join(output.root,'private-env/data')};await mkdir(join(output.root,'private-env'),{mode:0o700});for(const path of [processEnv.TMPDIR,processEnv.XDG_CACHE_HOME,processEnv.XDG_CONFIG_HOME,processEnv.XDG_DATA_HOME])await mkdir(path,{mode:0o700});
  const validators={combined:await import(pathToFileURL(a.p.validators.combined.path)),hosts:await import(pathToFileURL(a.p.validators.hosts.path))};
  async function command(name,executable,args,{env=processEnv,cwd=output.root,timeoutMs=30000,expectedCode=0}={}){
   await write('commands/'+name+'.context.json',{schemaVersion:1,executable,args,env,cwd,timeoutMs,expectedCode,partial:true});const registered=new Set();
   const status=await runOwnedCommand({output:output.root,name,executable,args,env,cwd,timeoutMs,maxOutputBytes:16*1024*1024,
    write:(path,data)=>output.write(child(output.root,path),data),register:path=>registered.add(path)});
   for(const path of registered){const raw=await readFile(path),name=child(output.root,path);output.rows.set(name,{path:name,sha256:hash(raw),bytes:raw.length});}
   // Full stdout/stderr/terminal are durable before status or parsed-data checks.
   need(status.status===expectedCode&&status.closed&&status.ownedGroupGone&&!status.timedOut&&!status.outputLimitExceeded&&status.signal===null&&status.spawnError===null&&status.externalSignal===null&&status.errors.length===0&&status.signals.length===0,'Exact owned command terminal, no partial reuse');
   return status;
  }
  async function request(host,url,tag,sequence,{timeoutMs=30000}={}){
   loopback(url);const name='requests/'+host+'-'+String(sequence).padStart(4,'0');
   try{const captured=await captureResponse({name,url,tag,
    fetchResponse:()=>fetch(url+tag,{signal:AbortSignal.timeout(timeoutMs),redirect:'error'}),
    writeJson:write,writeBytes:(path,bytes)=>output.write(path,bytes)});
    responseCaptures.push(captured.capture);return captured.response;
   }catch(error){responseCaptures.push(error?.rawCapture??{schemaVersion:1,availableRawRetained:false,completeResponseRetained:false,captureProtocolFailure:true,failureRecordRetained:false});throw error;}
  }
  async function stopProbe(name,url){const result=await command(name+'-stopped-refusal',a.p.curl.path,['--disable','--noproxy','*','--connect-timeout','2','--max-time','3','--silent','--show-error','--include',url+'/node-compat?stopped=1'],{timeoutMs:10000,expectedCode:7});need(result.stdoutFile.bytes===0,'Stopped listener refused before any HTTP response');return{rawExitCode:7,stdout:result.stdoutFile,stderr:result.stderrFile,ownedGroupGone:result.ownedGroupGone};}
  const wtVersion=await command('wasmtime-version',a.p.wasmtime.path,['--version']);need(/^wasmtime 42\.0\.1\b/.test(wtVersion.stdout),'Pinned stock Wasmtime42.0.1');await disk(output.root,800*1024**2);
  let wtUrl=null,wtSequence=0;
  const wt=await ownedServer({output,name:'wasmtime',executable:a.p.wasmtime.path,args:['serve','--addr','127.0.0.1:0',a.rows.component.path],env:processEnv,cwd:output.root,
   visit:async host=>{const deadline=Date.now()+60000;while(Date.now()<deadline){host.check();const logs=await host.readLogs(),m=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs.stdout+'\n'+logs.stderr);if(m){wtUrl=loopback(m[1]);break;}await pause(100);}need(wtUrl,'Accepted Wasmtime serve readiness line');const responses=[];
    for(let i=1;i<=3;i++){const r=await request('wasmtime',wtUrl,'/node-compat?request='+i,++wtSequence);r.body=JSON.parse(r.text);validateResponse(r,a.audit,validators.combined);responses.push(r);}return responses;}});
  gracefulServer(wt.terminal);need(wt.value?.length===3,'Three complete stock WT responses');const wtStopped=await stopProbe('wasmtime',wtUrl);
  reports.wasmtime={schema:1,wasmtime:wtVersion.stdout.trim(),componentSha256:a.rows.component.sha256,componentBytes:a.rows.component.bytes,responses:wt.value,process:{stopped:wt.terminal.closed,exitStatus:{code:wt.terminal.status,signal:wt.terminal.signal}},ownedTerminal:wt.terminal,stoppedServerRefusal:wtStopped};await write('wasmtime-results.json',reports.wasmtime);
  await source.recheck();await a.recheck();await disk(output.root,800*1024**2);
  await output.write('wash/empty-user-config.json','{}\n');const userConfig=join(output.root,'wash/empty-user-config.json');
  const washVersion=await command('wash-version',a.p.wash.path,['--version']);need(washVersion.stdout.trim()==='wash 2.11.0','Unmodified official wash2.11.0');
  const inspected=await command('wash-inspect',a.p.wash.path,['--user-config',userConfig,'--output','json','inspect',a.rows.component.path]),inspection=JSON.parse(inspected.stdout);need(inspection.success===true&&typeof inspection.data?.wit==='string','Actual released host inspection');
  const names=kind=>[...inspection.data.wit.matchAll(new RegExp('^\\s*'+kind+'\\s+([^;\\s]+);','gm'))].map(m=>m[1]).sort();need(same(names('import'),[...SIX])&&same(names('export'),EXPORTS),'Released host sees same six/handler');
  const project=join(output.root,'wash/project'),deployed=join(project,'native-profile-http.component.wasm');await write('wash/project/.wash/owned-project.json',{schemaVersion:1,component:a.rows.component});await copyFile(a.rows.component.path,deployed,constants.COPYFILE_EXCL);await streamHash({...a.rows.component,path:deployed});const sourceStat=await lstat(a.rows.component.path),copyStat=await lstat(deployed);need(sourceStat.dev!==copyStat.dev||sourceStat.ino!==copyStat.ino,'Independent deployed component inode');
  const probe=createServer();let port;try{await new Promise((resolve,reject)=>probe.once('error',reject).listen(0,'127.0.0.1',resolve));port=probe.address().port;}finally{if(probe.listening)await new Promise((resolve,reject)=>probe.close(e=>e?reject(e):resolve()));}
  const address='127.0.0.1:'+port,url=loopback('http://'+address),config=washConfig(deployed,address);await write('wash/project/.wash/config.json',config);
  const env={...ENV,...inheritedPaths,TMPDIR:join(output.root,'wash/tmp'),XDG_CACHE_HOME:join(output.root,'wash/cache'),XDG_CONFIG_HOME:join(output.root,'wash/config'),XDG_DATA_HOME:join(output.root,'wash/data')};for(const path of [env.TMPDIR,env.XDG_CACHE_HOME,env.XDG_CONFIG_HOME,env.XDG_DATA_HOME])await mkdir(path,{mode:0o700});
  const base=['--user-config',userConfig,'-C',project],effective=await command('wash-config',a.p.wash.path,[...base,'--output','json','config','show'],{env,cwd:project});const configuration=JSON.parse(effective.stdout).data;effectiveWash(configuration,address);
  let washSequence=0;const wash=await ownedServer({output,name:'wash',executable:a.p.wash.path,args:[...base,'--log-level','info','--meters','duration','dev'],env,cwd:project,
   visit:async host=>{const deadline=Date.now()+120000;let first;while(Date.now()<deadline){host.check();try{const r=await request('wash',url,'/node-compat?request=1',++washSequence,{timeoutMs:5000});if(r.status===200){first=r;break;}need([404,503].includes(r.status),'Only accepted transient deployment statuses');}catch(e){if(e.readinessRetryAllowed!==true)throw e;}await pause(150);}need(first,'wash readiness HTTP200 within accepted bound');const responses=[];
    for(let i=1;i<=3;i++){const r=i===1?first:await request('wash',url,'/node-compat?request='+i,++washSequence);r.body=JSON.parse(r.text);validateResponse(r,a.audit,validators.combined);responses.push(r);}return responses;}});
  gracefulServer(wash.terminal);need(wash.value?.length===3,'Three complete wash responses');await streamHash({...a.rows.component,path:deployed});const washStopped=await stopProbe('wash',url);
  reports.wash={schema:1,host:{version:'2.11.0',unmodifiedOfficialBinary:true,binaryPath:a.p.wash.path,binarySha256:a.p.wash.sha256},component:{sha256:a.rows.component.sha256,bytes:a.rows.component.bytes,deployedPath:deployed},effectiveConfiguration:configuration,responses:wash.value,process:{stopped:wash.terminal.closed,exitStatus:{code:wash.terminal.status,signal:wash.terminal.signal}},ownedTerminal:wash.terminal,stoppedServerRefusal:washStopped};await write('wash-results.json',reports.wash);
  const validation=validateBoth({audit:a.audit,selection:a.selectedInterfaces,...reports},validators);await source.recheck();await a.recheck();await adopt(output);await output.recheck();
  const result=await write('results.json',{schemaVersion:1,state:'CONSUMERS355_HTTP_BOTH_HOSTS_COMPLETE_UNREVIEWED_EXTERNAL_ZERO_REQUIRED_V2',sourceIndex:a.sourceIndex,rootAction:a.rootAction,component:a.rows.component,componentAudit:a.rows.componentAudit,actualComponentReview:a.root.actualComponentReview,validation,...reports,responseCaptures,fullActualComponentAudit:a.audit,requestsPerHost:3,configuredSourceRoot:a.frame.admissionSourceRoot,frozenSourceRoot:a.frame.runtimeSourceRoot,sourceRecheckPassed:true,wireBodyAdapter:false,instanceReuseClaim:false,requestIsolationClaim:false,gcOrBackendProofClaim:false,operationalAdmission:false,runtimeAcceptanceClaim:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]}),completion=await write('completion.json',{schemaVersion:1,state:'HTTP_HOSTS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V2',sourceIndex:a.sourceIndex,result,index,component:a.rows.component});await source.recheck();await a.recheck();await output.recheck();return{result,index,completion};
 }catch(error){let audited=false;try{await source.recheck();await a.recheck();audited=true;}catch{}let partialInventoryCaptured=false;try{await adopt(output);partialInventoryCaptured=true;}catch{}try{await write('failure.json',{schemaVersion:1,state:'FAILED_HTTP_HOSTS_UNACCEPTED_V2',name:error?.name??null,message:String(error?.message??'host failure').slice(0,2048),partialRawArtifactInventoryCaptured:partialInventoryCaptured,...captureSetSummary(responseCaptures),
    rawCaptureScope:'Per-attempt complete/partial/write-failure records only; no blanket full capture claim',completedHosts:Object.keys(reports),postFailureSourceAuditPassed:audited,runtimeAcceptanceClaim:false});}catch{}throw error;}
 finally{await output.close();}
}
