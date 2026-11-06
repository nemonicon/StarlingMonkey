// Host client/observer for the real C component; no JS engine or Next application.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir,chmod,open,readdir,stat} from 'node:fs/promises';
import {join,resolve} from 'node:path';

const output=resolve(process.argv[2]),build=resolve(process.argv[3]);
assert.equal(output,'/private/tmp/starling-node-compat/next-adapter-probe-v1-wasmtime');
assert.equal(build,'/private/tmp/starling-node-compat/next-adapter-probe-v1-build');
assert.equal(process.version,'v22.14.0');
const source=resolve(import.meta.dirname),plan=JSON.parse(await readFile(join(source,'plan.json'),'utf8'));
const audit=JSON.parse(await readFile(join(build,'component-audit.json'),'utf8'));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(audit.passed,true);assert(audit.imports.every(name=>plan.selectedInterfaces.includes(name)&&name.endsWith('@0.2.10')));
assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);
assert.equal(hash(await readFile(audit.component.path)),audit.component.sha256);
const executable=plan.pins.wasmtime.path;
assert.equal(hash(await readFile(executable)),plan.pins.wasmtime.sha256);
const app=join(output,'app'),cache=join(output,'cache');
await mkdir(app,{mode:0o700});await mkdir(cache,{mode:0o700});
await writeFile(join(app,'message.txt'),'app-readable\n',{flag:'wx',mode:0o444});await chmod(app,0o555);
const args=['serve','--addr','127.0.0.1:0','-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n',
  '--env','STARLING_NEXT_PROBE=capabilities-v1','--dir',app+'::/app','--dir',cache+'::/cache',
  '--max-instance-reuse-count','32','--idle-instance-timeout','60s',audit.component.path];
const result={schemaVersion:1,state:'ACTUAL_NEXT_ADAPTER_C_WASMTIME_UNREVIEWED_V1',component:audit.component,
  adapter:audit.adapter,imports:audit.imports,unusedSelectedInterfaces:audit.unusedSelectedInterfaces,
  argv:[executable,...args],requests:[],errors:[],forcedCleanup:false,passed:false,
  realCComponentExecuted:false,engineJSNextExecuted:false,wasmCloudExecuted:false,
  deploymentPermissions:'Wasmtime preopens use default rights; /app host directory/file physical modes are 0555/0444. No wasmCloud read_only policy claim.'};
const save=()=>writeFile(join(output,'host-result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
await save();
let host,exited=false,exitStatus=null,exitPromise,stdout,stderr;
try {
  stdout=await open(join(output,'wasmtime.stdout.log'),'wx',0o600);stderr=await open(join(output,'wasmtime.stderr.log'),'wx',0o600);
  host=spawn(executable,args,{stdio:['ignore',stdout.fd,stderr.fd],env:{...process.env,
    XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}});
  result.pid=host.pid;
  exitPromise=new Promise(resolve=>{host.once('exit',(code,signal)=>{exited=true;exitStatus={code,signal};resolve();});
    host.once('error',error=>{exited=true;exitStatus={spawnError:{name:error.name,message:error.message}};resolve();});});
  await save();
  let origin;const deadline=Date.now()+30000;
  while(Date.now()<deadline){
    const text=await readFile(join(output,'wasmtime.stderr.log'),'utf8');
    if(exited)throw new Error('Wasmtime exited before readiness: '+text);
    origin=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];
    if(origin)break;await pause(50);
  }
  assert(origin,'No stock Wasmtime readiness');result.origin=origin;await save();
  for(let ordinal=1;ordinal<=3;ordinal++){
    const before=Date.now();
    const response=await fetch(origin+'/probe?request='+ordinal,{headers:{connection:'close'},signal:AbortSignal.timeout(10000)});
    const text=await response.text(),after=Date.now();
    const file=join(output,'response-'+ordinal+'.json');
    await writeFile(file,text,{flag:'wx',mode:0o600});
    const record={ordinal,status:response.status,beforeWallMs:before,afterWallMs:after,rawFile:file,rawSha256:hash(Buffer.from(text)),bytes:Buffer.byteLength(text)};
    result.requests.push(record);result.realCComponentExecuted=true;await save();
    const body=JSON.parse(text);record.body=body;await save(); // whole bytes retained before every semantic check
    assert.equal(response.status,200);assert.equal(body.probe,'next-selective-adapter-probe-v1');
    assert.equal(body.counter,ordinal);assert.equal(body.environmentMarker,'capabilities-v1');
    assert(BigInt(body.monotonicAfter)>BigInt(body.monotonicBefore));
    assert(Number.isInteger(body.wallSeconds)&&Number.isInteger(body.wallNanoseconds)&&body.wallNanoseconds>=0&&body.wallNanoseconds<1e9);
    const wallMs=body.wallSeconds*1000+body.wallNanoseconds/1e6;
    assert(wallMs>=before-1&&wallMs<=after+1,'P2 wall time outside full host-call bracket plus 1ms');
    assert.match(body.randomHex,/^[0-9a-f]{16}$/);
    const appRecord=body.preopens.find(row=>row.name==='/app'),cacheRecord=body.preopens.find(row=>row.name==='/cache');
    assert(appRecord&&cacheRecord);assert.equal(body.preopens.length,2);
    assert.equal(appRecord.readFixture,true);assert.equal(appRecord.createAllowed,false);assert([0,31,33].includes(appRecord.createError));
    for(const key of ['create','write','read','link','rename','unlink'])assert.equal(cacheRecord[key],true,key);
    assert.equal(cacheRecord.secondLink,false);assert.equal(cacheRecord.secondLinkError,7);
    const p=body.p1;
    for(const key of ['stdoutError','stderrError','fileOpenError','fileReadError','fileCloseError','monotonicError','wallError','monotonicResolutionError','wallResolutionError','randomError'])assert.equal(p[key],0,key);
    assert.equal(p.stdoutBytes,13);assert.equal(p.stderrBytes,13);assert.equal(p.fdstat0Error,8);assert.equal(p.read0Error,8);
    assert.equal(p.appPreopenFound,true);assert.equal(p.fileReadEqual,true);assert.equal(p.fileReadBytes,13);
    assert(BigInt(p.monotonicNs)>0n);assert(Number.isSafeInteger(p.monotonicResolution)&&p.monotonicResolution>0);
    assert(Number.isSafeInteger(p.wallResolution)&&p.wallResolution>0);
    const p1WallMs=Number(BigInt(p.wallNs))/1e6;assert(p1WallMs>=before-1&&p1WallMs<=after+1);
    assert.match(p.randomHex,/^[0-9a-f]{16}$/);record.passed=true;await save();
  }
  assert.equal(new Set(result.requests.map(row=>row.body.randomHex)).size,3);
  assert.equal(new Set(result.requests.map(row=>row.body.p1.randomHex)).size,3);
  assert.deepEqual(await readdir(cache),[]);assert.equal(await readFile(join(app,'message.txt'),'utf8'),'app-readable\n');
  assert.equal((await stat(app)).mode&0o777,0o555);
  result.semanticChecksPassed=true;
} catch(error){result.errors.push({name:error.name,message:error.message,stack:error.stack});}
finally {
  if(host&&!exited){result.intentionalShutdownSignal='SIGINT';host.kill('SIGINT');}
  if(exitPromise)await Promise.race([exitPromise,pause(5000)]);
  if(host&&!exited){result.forcedCleanup=true;host.kill('SIGKILL');await exitPromise;}
  result.process=exitStatus;
  if(stdout)await stdout.close();if(stderr)await stderr.close();
  try {
    assert.equal(result.forcedCleanup,false);assert.deepEqual(exitStatus,{code:0,signal:null});
    const out=await readFile(join(output,'wasmtime.stdout.log'),'utf8'),err=await readFile(join(output,'wasmtime.stderr.log'),'utf8');
    assert.equal(out.split('\n').filter(line=>line==='P1_STDOUT_OK').length,3);
    assert.equal(err.split('\n').filter(line=>line==='P1_STDERR_OK').length,3);
    result.stdioMarkers={stdout:3,stderr:3};
  }catch(error){result.errors.push({name:error.name,message:error.message,stack:error.stack});}
  result.passed=result.semanticChecksPassed===true&&result.errors.length===0;
  await save();
}
console.log(JSON.stringify({passed:result.passed,requests:result.requests.length,counters:result.requests.map(row=>row.body?.counter),errors:result.errors}));
if(!result.passed)process.exitCode=1;
