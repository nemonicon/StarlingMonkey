// Correctness replay only; native builds and performance runs are separate.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,open} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {verifyProductionV11} from '../foundation-add-abort/production-v11-preflight.mjs';
const hash=value=>createHash('sha256').update(value).digest('hex');
const repository=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const preflight=await verifyProductionV11(),base='/tmp/starling-node-compat/foundations-v11';
const output=resolve(process.env.NODE_COMPAT_V11_RELEASE_OUTPUT??join(base,'release-gates-v1'));
await mkdir(output); // A run cannot overwrite an earlier failure or result.
const common={...process.env,NODE_COMPAT_ENGINE:preflight.engine,NODE_COMPAT_ENGINE_SOURCE_ROOT:preflight.sourceRoot,
  NODE_COMPAT_TOOLCHAIN:'/tmp/starling-node-compat/native-toolchain-lock',
  NODE_COMPAT_COMPONENTIZE_MODULE:'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',
  NODE_COMPAT_WASMTIME:'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime'};
const jobs=[
  {name:'core',runner:'run.mjs',variable:'NODE_COMPAT_OUTPUT',report:'results.json'},
  {name:'allocator',runner:'foundation-alloc-unsafe/installed/run-component-v11.mjs',variable:'NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT',report:'results.json'},
  {name:'stream-web',runner:'foundation-stream-web/production-candidate/run-native-component-v11.mjs',variable:'NODE_COMPAT_STREAM_WEB_OUTPUT',report:'results.json'},
  {name:'optional',runner:'foundations/run-v11-optional-regressions.mjs',variable:'NODE_COMPAT_OPTIONAL_OUTPUT',report:'results.json'},
  ...['sync','runtime','late','callbacks'].map(name=>({name:'strict-'+name,
    runner:'foundation-add-abort/run-production-v11-'+name+'.mjs',variable:'NODE_COMPAT_STRICT_EVENT_OUTPUT',
    report:'production-v11-'+(name==='callbacks'?'callback':name)+'-results.json'})),
];
const result={schema:1,state:'running',startedAtUtc:new Date().toISOString(),preflight,jobs:[],
  scope:'New ordinary m0.11 core ON/entropy-OFF source-pinned engine; prior modules, allocator and layered strict-v3/protected-abort callback gates. Installed stream/web and HTTP have separate reports.'};
async function save(){await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');}
await save();
for(const job of jobs){
  const destination=join(output,job.name);
  // Existing runners create their own output; optional orchestrator requires it
  // absent and creates it itself.
  const logPath=join(output,job.name+'.log'),log=await open(logPath,'wx');
  console.log(JSON.stringify({event:'start',name:job.name,output:destination}));
  const runner=join(repository,'tests/node-compat',job.runner),runnerSha256=hash(await readFile(runner));
  const child=spawn(process.execPath,[runner],{cwd:repository,env:{...common,[job.variable]:destination},stdio:['ignore',log.fd,log.fd]});
  const terminal=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',(code,signal)=>resolve({code,signal}));});
  await log.close();
  const entry={...job,runner,runnerSha256,output:destination,logPath,logSha256:hash(await readFile(logPath)),...terminal};
  result.jobs.push(entry);
  if(terminal.code!==0){result.state='failed';await save();process.exitCode=1;break;}
  const reportPath=join(destination,job.report),bytes=await readFile(reportPath),report=JSON.parse(bytes);
  entry.reportPath=reportPath;entry.reportSha256=hash(bytes);
  assert.equal(report.engineSha256??report.preflight?.engineSha256,preflight.engineSha256,job.name);
  const audits=[];
  function inspect(value){if(!value||typeof value!=='object')return;
    if(value.interfaceAudit){assert.deepEqual(value.interfaceAudit.emittedImports,[]);audits.push(value.interfaceAudit);}
    for(const nested of Object.values(value))if(nested&&typeof nested==='object')inspect(nested);
  }
  inspect(report);
  if(job.name==='optional')assert.equal(report.state,'passed');else assert(audits.length>0,job.name+' final component audit required');
  entry.finalComponentAudits=audits.length;entry.emittedImports=[];
  assert.equal(hash(await readFile(runner)),runnerSha256);await verifyProductionV11();await save();
  console.log(JSON.stringify({event:'passed',name:job.name,finalComponentAudits:audits.length}));
}
if(result.jobs.length===jobs.length&&result.jobs.every(job=>job.code===0)){
  result.state='passed';result.completedAtUtc=new Date().toISOString();result.runnerSha256=hash(await readFile(fileURLToPath(import.meta.url)));
  await save();console.log(JSON.stringify({event:'complete',state:'passed',jobs:jobs.length,output}));
}
