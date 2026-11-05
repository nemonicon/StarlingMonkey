// Exploratory framework regression: real Next build/HTTP oracle and isolated
// Wasm attempts. A failed framework attempt is evidence, not API support.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawn, execFileSync } from 'node:child_process';
import { createWriteStream } from 'node:fs';
import { mkdir, cp, readFile, writeFile, readdir, stat, copyFile } from 'node:fs/promises';
import { dirname, join, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';
import { createServer } from 'node:net';
import { isDeepStrictEqual } from 'node:util';

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../../..');
const args = process.argv.slice(2);
function option(name, fallback) { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; }
assert.equal(process.version, 'v22.14.0');
const output = resolve(option('--output', `/private/tmp/starling-node-compat/nextjs-${Date.now()}`));
assert(!output.startsWith(repository + '/'), 'Generated dependencies/components must stay outside the checkout');
const record = option('--record');
const application = join(output, 'application');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const descriptor = async path => { const b = await readFile(path); return {path, sha256: hash(b), bytes: b.length}; };
const engine = resolve(option('--engine', '/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm'));
const sourceRoot = resolve(option('--source-root', '/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source'));
const env = {...process.env, PATH: dirname(process.execPath) + ':' + process.env.PATH,
  NEXT_TELEMETRY_DISABLED: '1', CI: '1', NODE_ENV: 'production',
  NODE_COMPAT_TOOLCHAIN: process.env.NODE_COMPAT_TOOLCHAIN ?? '/private/tmp/starling-node-compat/toolchain',
  NODE_COMPAT_COMPONENTIZE_MODULE: process.env.NODE_COMPAT_COMPONENTIZE_MODULE ?? '/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',
  NODE_COMPAT_WASMTIME: process.env.NODE_COMPAT_WASMTIME ?? '/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime'};
const result = {schemaVersion: 1, suite: 'nextjs-component-compatibility-v1', started: new Date().toISOString(),
  repositoryRevision: execFileSync('git', ['rev-parse', 'HEAD'], {cwd: repository, encoding:'utf8'}).trim(),
  node: process.version, next: '16.4.5', react: '19.3.1', acceptedRuntime: 'foundations-v13',
  output, engine: await descriptor(engine), metadata: await descriptor(engine + '.build.json'),
  selectedInterfaces: [], fullNextServerInWasm: false, browserRequested:args.includes('--browser'), commands: [], http: [], wasm: [], errors: []};
await mkdir(output); // Exclusive run directory: never overwrite an earlier experiment.
await mkdir(join(output, 'logs'));
result.harnessFiles=await Promise.all(['run.mjs','wasm-worker.mjs','fixture-contract.json',
  ...(result.browserRequested?['browser-check.mjs','browser-toolchain/package.json']:[])].map(n=>descriptor(join(here,n))));
const save = () => writeFile(join(output, 'results.json'), JSON.stringify(result, null, 2) + '\n');
await save();

function launch(id, argv, cwd, timeoutMs, environment = {}) {
  const stdoutPath = join(output, 'logs', id + '.stdout.log');
  const stderrPath = join(output, 'logs', id + '.stderr.log');
  const stdout = createWriteStream(stdoutPath, {flags:'wx'});
  const stderr = createWriteStream(stderrPath, {flags:'wx'});
  const started = Date.now();
  const child = spawn(argv[0], argv.slice(1), {cwd, env:{...env,...environment}, detached:true, stdio:['ignore','pipe','pipe']});
  child.stdout.pipe(stdout); child.stderr.pipe(stderr);
  let timedOut = false, spawnError = null, killTimer;
  const signals=[];
  const signal = value => { try { process.kill(-child.pid, value); signals.push(value); } catch (e) { if(e.code !== 'ESRCH') throw e; } };
  const groupAlive=()=> { if(!child.pid)return false;try{process.kill(-child.pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;} };
  const timer = setTimeout(() => { timedOut=true; signal('SIGTERM'); killTimer=setTimeout(() => signal('SIGKILL'), 1500); }, timeoutMs);
  const completion = new Promise(resolveDone => {
    child.on('error', error => {spawnError=error.message;});
    child.on('close', async (code, exitSignal) => {
      clearTimeout(timer); clearTimeout(killTimer);
      await Promise.all([new Promise(r => stdout.writableFinished ? r() : stdout.on('finish', r)),
        new Promise(r => stderr.writableFinished ? r() : stderr.on('finish', r))]);
      let ownedGroupGone=false,groupObservationError=null;
      try {
        if(groupAlive()) { signal('SIGTERM');for(let n=0;n<40 && groupAlive();n++)await delay(50); }
        if(groupAlive()) { signal('SIGKILL');for(let n=0;n<40 && groupAlive();n++)await delay(50); }
        ownedGroupGone=!groupAlive();
      }catch(e){groupObservationError=e.message;}
      const terminal = {id, argv, cwd, pid:child.pid ?? null, code, signal:exitSignal, timedOut, spawnError,ownedGroupGone,groupObservationError,signals,
        elapsedMs:Date.now()-started, stdout:await descriptor(stdoutPath), stderr:await descriptor(stderrPath)};
      await writeFile(join(output, 'logs', id + '.terminal.json'), JSON.stringify(terminal,null,2)+'\n');
      result.commands.push(terminal); await save(); resolveDone(terminal);
    });
  });
  return {child, completion, signal};
}
async function command(id, argv, cwd, timeoutMs) { return launch(id, argv, cwd, timeoutMs).completion; }
async function inventory(directory) {
  const rows=[];
  async function visit(path) {
    for(const entry of await readdir(path,{withFileTypes:true})) {
      if(entry.name === 'node_modules' || entry.name === '.next' || entry.name === '.git') continue;
      const p=join(path,entry.name);
      if(entry.isDirectory()) await visit(p);
      else if(entry.isFile()) rows.push({...await descriptor(p),path:relative(directory,p)});
    }
  }
  await visit(directory); return rows.sort((a,b)=>a.path.localeCompare(b.path));
}
async function port() { const s=createServer(); await new Promise(r=>s.listen(0,'127.0.0.1',r)); const p=s.address().port; await new Promise(r=>s.close(r)); return p; }

try {
  await cp(join(here, 'app-fixture'), application, {recursive:true});
  result.fixture = await inventory(application);
  const npm = join(dirname(process.execPath), '../lib/node_modules/npm/bin/npm-cli.js');
  const locked = await stat(join(application,'package-lock.json')).then(()=>true, e=>{if(e.code==='ENOENT')return false;throw e;});
  const install = await command('npm-install', [process.execPath,npm,locked?'ci':'install','--ignore-scripts','--no-audit','--no-fund'], application, 600000);
  assert.equal(install.code,0,'Fixture dependency installation failed');
  result.packageLock = await descriptor(join(application,'package-lock.json'));
  result.installedVersions = Object.fromEntries(await Promise.all(['next','react','react-dom'].map(async n=>[n,JSON.parse(await readFile(join(application,'node_modules',n,'package.json'))).version])));
  assert.deepEqual(result.installedVersions,{next:'16.4.5',react:'19.3.1','react-dom':'19.3.1'});
  const build = await command('next-build', [process.execPath,join(application,'node_modules/next/dist/bin/next'),'build','--webpack'], application, 900000);
  await copyFile(join(application,'package-lock.json'),join(output,'package-lock.json'));
  if(result.browserRequested) {
    await cp(join(here,'browser-toolchain'),join(output,'browser-tools'),{recursive:true});
    const installBrowser=await command('browser-tools-install',[process.execPath,npm,'install','--ignore-scripts','--no-audit','--no-fund'],join(output,'browser-tools'),180000);
    assert.equal(installBrowser.code,0,'Browser tooling installation failed');
  }
  result.nextBuildPassed = build.code===0;
  if(result.nextBuildPassed) {
    const standalone=join(application,'.next/standalone');
    await cp(join(application,'.next/static'),join(standalone,'.next/static'),{recursive:true});
    await cp(join(application,'public'),join(standalone,'public'),{recursive:true});
    result.generatedArtifacts = await Promise.all(['.next/standalone/server.js','.next/server/app/page.js','.next/server/app/api/compat/route.js',
      '.next/routes-manifest.json','.next/prerender-manifest.json','.next/server/server-reference-manifest.json'].map(p=>descriptor(join(application,p))));
    const p=await port();
    const origin=`http://127.0.0.1:${p}`;
    const server=launch('next-server',[process.execPath,join(standalone,'server.js')],standalone,180000,{PORT:String(p),HOSTNAME:'127.0.0.1'});
    try {
      let ready=false;
      for(let attempt=0;attempt<150;attempt++) {
        if(server.child.exitCode!==null)break;
        try { const r=await fetch(`http://127.0.0.1:${p}/api/health`,{signal:AbortSignal.timeout(1000)}); if(r.ok){ready=true;break;} } catch {}
        await delay(200);
      }
      assert(ready,'Next HTTP oracle did not become ready');
      const contract=JSON.parse(await readFile(join(here,'fixture-contract.json')));
      const bodies=new Map();
      for(const c of contract.requests) {
        const response=await fetch(`http://127.0.0.1:${p}${c.path}`,{method:c.method??'GET',headers:c.headers,body:c.body,redirect:'manual',signal:AbortSignal.timeout(15000)});
        const body=await response.text();
        const failures=[];
        if(response.status!==c.status)failures.push(`status ${response.status} != ${c.status}`);
        for(const text of c.includes??[])if(!body.includes(text))failures.push(`missing ${JSON.stringify(text)}`);
        if(c.location && response.headers.get('location')!==c.location)failures.push('location mismatch');
        if(c.json) { try {const actual=JSON.parse(body);for(const [key,value] of Object.entries(c.json))if(JSON.stringify(actual[key])!==JSON.stringify(value))failures.push(`JSON ${key} mismatch`);}catch(e){failures.push(e.message);} }
        for(const [key,value] of Object.entries(c.responseHeaders??{}))if(response.headers.get(key)!==value)failures.push(`header ${key} mismatch`);
        for(const [key,values] of Object.entries(c.responseHeaderIncludes??{}))for(const value of values)if(!response.headers.get(key)?.includes(value))failures.push(`header ${key} missing ${value}`);
        if(c.equalJsonTo && body!==bodies.get(c.equalJsonTo))failures.push(`body differs from ${c.equalJsonTo}`);
        bodies.set(c.id,body);
        await writeFile(join(output,'logs',`http-${c.id}.body.txt`),body);
        result.http.push({id:c.id,path:c.path,method:c.method??'GET',status:response.status,headers:Object.fromEntries(response.headers),
          bodyBytes:Buffer.byteLength(body),bodySha256:hash(body),passed:failures.length===0,failures}); await save();
      }
      // Exercise the real action ID emitted by this build, never a fabricated ID.
      const form=new FormData();
      const actionHtml=bodies.get('server-action-form-ssr');
      const actionNames=[...actionHtml.matchAll(/name="(\$ACTION_ID_[^"]+)"/g)].map(m=>m[1]);
      assert.equal(actionNames.length,1,'Expected one genuine Next server action ID');
      form.set(actionNames[0],''); form.set('value','fixture-action');
      const actionResponse=await fetch(origin+'/actions',{method:'POST',body:form,headers:{origin},redirect:'manual',signal:AbortSignal.timeout(15000)});
      const actionBody=await actionResponse.text();
      await writeFile(join(output,'logs','http-server-action-submit.body.txt'),actionBody);
      result.http.push({id:'server-action-submit',method:'POST',path:'/actions',status:actionResponse.status,headers:Object.fromEntries(actionResponse.headers),
        bodySha256:hash(actionBody),bodyBytes:Buffer.byteLength(actionBody),passed:actionResponse.status===303 && actionResponse.headers.get('location')==='/action-result?value=fixture-action'});
      const before=JSON.parse(bodies.get('cache-first')), after=JSON.parse(bodies.get('cache-after-revalidate'));
      result.cacheInvalidation={before,after,passed:after.generation>before.generation};
      // Record transport chunk boundaries; coalesced delivery is not a failure
      // of server rendering and does not prove incremental delivery either.
      const streamResponse=await fetch(origin+'/stream',{signal:AbortSignal.timeout(15000)});
      const streamChunks=[]; const streamStart=performance.now(); let position=0,streamText='',shell=-1,readyChunk=-1;
      const decoder=new TextDecoder('utf-8',{fatal:true});
      for await(const chunk of streamResponse.body) {
        assert(position+chunk.length<=8*1024*1024,'Complete streaming response exceeds test bound');
        const utf8=decoder.decode(chunk,{stream:true}); streamText+=utf8;
        if(shell<0 && streamText.includes('NEXT_STREAM_SHELL'))shell=streamChunks.length;
        if(readyChunk<0 && streamText.includes('NEXT_STREAM_READY'))readyChunk=streamChunks.length;
        streamChunks.push({bytes:chunk.length,atMs:performance.now()-streamStart,position,base64:Buffer.from(chunk).toString('base64'),utf8});position+=chunk.length;
      }
      streamText+=decoder.decode();
      await writeFile(join(output,'stream-chunks.json'),JSON.stringify(streamChunks,null,2)+'\n');
      result.streaming={status:streamResponse.status,chunks:streamChunks.length,shellChunk:shell,readyChunk,
        completeBodySha256:hash(streamText),incrementalDeliveryObserved:shell>=0 && readyChunk>shell};
      result.sameSourceNodeValue=JSON.parse(bodies.get('bounded-node-compat'));
      if(result.browserRequested) {
        const browser=await command('browser-check',[process.execPath,join(here,'browser-check.mjs'),'--origin',origin,
          '--tools',join(output,'browser-tools'),'--output',join(output,'browser')],repository,120000);
        result.browser=JSON.parse(await readFile(join(output,'browser','result.json')));
        result.browserWorkerExit=browser.code;
      }
    } finally { server.signal('SIGTERM'); await server.completion; }
  }
  const cases=['compat','react-element','react-dom-edge','react-dom-string','next-server','next-headers','next-standalone','next-page','next-route',
    'import-fs-promises','import-crypto','import-async-hooks','import-http','import-net','import-url','import-process','import-timers','child-process-call','buffer-unsupported'];
  for(const name of cases) {
    const workerOutput=join(output,'wasm',name); await mkdir(dirname(workerOutput),{recursive:true});
    const terminal=await command('wasm-'+name,[process.execPath,join(here,'wasm-worker.mjs'),'--case',name,'--application',application,
      '--output',workerOutput,'--engine',engine,'--source-root',sourceRoot],repository,240000);
    const report=await readFile(join(workerOutput,'result.json'),'utf8').then(JSON.parse,()=>null);
    result.wasm.push({id:name,workerExit:terminal.code,workerSignal:terminal.signal,workerTimedOut:terminal.timedOut,workerOwnedGroupGone:terminal.ownedGroupGone,
      workerSpawnError:terminal.spawnError,report,missingReport:report===null}); await save();
  }
  const compat=result.wasm.find(x=>x.id==='compat');
  if(compat?.report?.status==='passed') {
    const guest=JSON.parse(await readFile(join(output,'wasm/compat/jco-0.parsed.json')));
    result.sameSourceDifferential={performed:true,passed:isDeepStrictEqual(guest,result.sameSourceNodeValue),node:result.sameSourceNodeValue,guest};
  } else result.sameSourceDifferential={performed:false,passed:false,reason:'Shared compat fixture did not pass component/runtime stages',actualStage:compat?.report?.stage};
} catch(error) { result.errors.push({name:error.name,message:error.message,stack:error.stack}); }
result.finished=new Date().toISOString();
result.oraclePassed=result.nextBuildPassed===true && result.http.length>0 && result.http.every(r=>r.passed) && result.cacheInvalidation?.passed===true
  && (!result.browserRequested || (result.browserWorkerExit===0 && result.browser?.passed===true));
result.observationsComplete=result.errors.length===0 && result.wasm.length===19 && result.wasm.every(r=>
  r.workerExit===0 && !r.workerSignal && !r.workerTimedOut && !r.workerSpawnError && r.workerOwnedGroupGone===true && r.report?.case===r.id &&
  ['passed','refused','failed','missing-fixture'].includes(r.report?.status) && typeof r.report?.finishedAtUtc==='string');
result.requiredDifferentialPassed=result.sameSourceDifferential?.performed===true && result.sameSourceDifferential?.passed===true;
await save();
if(record) {
  const destination=resolve(record); await mkdir(dirname(destination),{recursive:true}); await mkdir(destination);
  await copyFile(join(output,'results.json'),join(destination,'results.json'));
  await copyFile(join(output,'package-lock.json'),join(destination,'package-lock.json'));
  await copyFile(join(output,'stream-chunks.json'),join(destination,'stream-chunks.json')).catch(e=>{if(e.code!=='ENOENT')throw e;});
  await cp(join(output,'logs'),join(destination,'logs'),{recursive:true});
  if(result.browserRequested) {
    await cp(join(output,'browser'),join(destination,'browser'),{recursive:true}).catch(e=>{if(e.code!=='ENOENT')throw e;});
    await copyFile(join(output,'browser-tools','package-lock.json'),join(destination,'browser-toolchain-lock.json'));
  }
  for(const row of result.wasm) {
    const src=join(output,'wasm',row.id); const dst=join(destination,'wasm',row.id); await mkdir(dst,{recursive:true});
    for(const name of await readdir(src).catch(()=>[]))if(/\.(?:json|wit|log|txt)$/.test(name))await copyFile(join(src,name),join(dst,name));
  }
}
process.stdout.write(JSON.stringify({output,oraclePassed:result.oraclePassed,observationsComplete:result.observationsComplete,http:result.http.length,
  wasm:result.wasm.map(x=>({id:x.id,stage:x.report?.stage,status:x.report?.status})),errors:result.errors},null,2)+'\n');
if(!result.oraclePassed || !result.observationsComplete || !result.requiredDifferentialPassed)process.exitCode=1;
