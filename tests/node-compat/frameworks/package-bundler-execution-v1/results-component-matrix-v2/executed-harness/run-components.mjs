import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,readdir,copyFile} from 'node:fs/promises';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runOwnedCommand} from '../../foundation-zlib/cost-jco-correctness-candidate-v2/durable-host.mjs';

assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),suite=resolve(here,'../nextjs');
const argv=process.argv.slice(2),option=(key,defaultValue)=>{const i=argv.indexOf(key);return i<0?defaultValue:argv[i+1];};
const application=resolve(option('--application')),output=resolve(option('--output')),record=option('--record');
const bundler=option('--bundler','packages-v1');assert(['packages-v1','packages-v2'].includes(bundler));
process.env.NODE_ENV='production';
const engine=option('--engine','/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm');
const sourceRoot=option('--source-root','/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source');
process.env.NODE_COMPAT_TOOLCHAIN??='/private/tmp/starling-node-compat/toolchain';
process.env.NODE_COMPAT_COMPONENTIZE_MODULE??='/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js';
process.env.NODE_COMPAT_WASMTIME??='/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime';
const descriptor=async path=>{const bytes=await readFile(path);return{path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};};
await mkdir(output);await mkdir(join(output,'processes'));await mkdir(join(output,'wasm'));await mkdir(join(output,'executed-harness'));
const cases=['native-cjs-interop','native-modules','react-element','react-dom-edge','react-dom-string','next-server','next-headers','next-standalone','next-page','next-route'];
const report={schemaVersion:1,suite:'production-package-components-v1',output,application,node:process.version,bundler,nodeEnvironment:'production',
  selectedInterfaces:[],nativeProfileChanged:false,legacyBundlerChanged:false,frameworkCompatible:false,
  cases:[],commands:[],errors:[],sources:await Promise.all([fileURLToPath(import.meta.url),resolve(here,bundler==='packages-v2'?'../../framework-package-bundler-v2.mjs':'../../framework-package-bundler.mjs'),join(suite,'wasm-worker.mjs'),...(bundler==='packages-v2'?[resolve(here,'../../package-environment-guards.mjs'),resolve(here,'../package-bundler-bindings-v2/bindings.mjs')]:[])].map(descriptor))};
for(const row of report.sources)await copyFile(row.path,join(output,'executed-harness',row.path.split('/').at(-1)));
const save=()=>writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');await save();
async function command(name,args,timeoutMs){
  const r=await runOwnedCommand({output,name,executable:process.execPath,args,timeoutMs,maxOutputBytes:16*1024*1024,write:writeFile,register:()=>{}});
  const terminal=JSON.parse(await readFile(r.terminalPath));report.commands.push(terminal);
  for(const [kind,row] of [['stdout',r.stdoutFile],['stderr',r.stderrFile]])await copyFile(row.path,join(output,name+'.'+kind+'.log'));
  await writeFile(join(output,name+'.terminal.json'),JSON.stringify(terminal,null,2)+'\n');await save();return r;
}
for(const name of cases){
  const observation={id:name,nodeControl:null,worker:null,differential:null};
  try{
    if(!name.startsWith('next-') || ['next-server','next-headers'].includes(name)){
      const original=join(suite,'probes',name+'.mjs');
      const runId=createHash('sha256').update(output).digest('hex').slice(0,16);
      const entry=name==='native-cjs-interop'?original:join(application,'.sm-node-package-'+name+'-'+runId+'.mjs');
      if(entry!==original)await writeFile(entry,await readFile(original),{flag:'wx'});
      const code=`try{const m=await import(${JSON.stringify(entry)});process.stdout.write(JSON.stringify({status:'passed',value:await m.run()})+'\\n');}catch(e){process.stdout.write(JSON.stringify({status:'threw',name:e.name,code:e.code,message:e.message})+'\\n');}`;
      const control=await command('node-'+name,['--input-type=module','--eval',code],30000);
      assert(control.terminalExitZeroObserved&&control.ownedGroupGone,'Node control collector failed');
      observation.nodeControl=JSON.parse(await readFile(control.stdoutFile.path,'utf8'));
    }
    const destination=join(output,'wasm',name);
    const worker=await command('wasm-'+name,[join(suite,'wasm-worker.mjs'),'--case',name,'--application',application,'--output',destination,
      '--engine',engine,'--source-root',sourceRoot,'--bundler',bundler],240000);
    assert(worker.terminalExitZeroObserved&&worker.ownedGroupGone,'Worker collector failed');
    observation.worker=JSON.parse(await readFile(join(destination,'result.json')));
    assert(observation.worker.case===name && observation.worker.finishedAtUtc && observation.worker.status!=='pending');
    if(observation.worker.status==='passed' && observation.nodeControl?.status==='passed'){
      const actual=await readFile(join(destination,'jco-0.string.txt'),'utf8');
      const fresh=await readFile(join(destination,'wasmtime.string.txt'),'utf8');
      observation.differential={fullStringEqual:actual===observation.nodeControl.value && fresh===actual,guestValue:JSON.parse(actual)};
      assert(observation.differential.fullStringEqual,'Complete Node/Jco/Wasmtime return differs');
    }
  }catch(error){observation.collectorError={name:error.name,message:error.message,stack:error.stack};report.errors.push({id:name,...observation.collectorError});}
  report.cases.push(observation);await save();
}
for(const before of report.sources)assert.deepEqual(await descriptor(before.path),before,'Executing source changed');
report.finished=new Date().toISOString();report.observationsComplete=report.cases.length===cases.length && report.errors.length===0;
report.requiredPositivePassed=['native-cjs-interop','native-modules','react-element'].every(id=>report.cases.find(c=>c.id===id)?.differential?.fullStringEqual===true);
await save();
if(record){
  const destination=resolve(record);await mkdir(dirname(destination),{recursive:true});await mkdir(destination);
  async function copyText(source,target){await mkdir(target,{recursive:true});for(const f of await readdir(source,{withFileTypes:true}))if(f.isFile()&&/\.(?:json|wit|txt|log|mjs)$/.test(f.name))await copyFile(join(source,f.name),join(target,f.name));}
  await copyText(output,destination);await copyText(join(output,'executed-harness'),join(destination,'executed-harness'));
  for(const row of report.cases)await copyText(join(output,'wasm',row.id),join(destination,'wasm',row.id));
}
console.log(JSON.stringify({output,observationsComplete:report.observationsComplete,requiredPositivePassed:report.requiredPositivePassed,
  cases:report.cases.map(r=>({id:r.id,stage:r.worker?.stage,status:r.worker?.status,differential:r.differential?.fullStringEqual})),errors:report.errors},null,2));
if(!report.observationsComplete||!report.requiredPositivePassed)process.exitCode=1;
