// Sequential correctness replay of existing optional foundations. No native
// changes, source-gate bypass, benchmark or new stream/web execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir,cp,open} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const repository=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const engine='/tmp/starling-node-compat/foundations-v8/native-freeze/off-foundations.engine.wasm';
const sourceRoot='/tmp/starling-node-compat/foundations-v8/native-freeze/source';
const output=resolve(process.env.NODE_COMPAT_OPTIONAL_OUTPUT??'/tmp/starling-node-compat/foundations-v8/prior-foundations-v1');
const resume=process.env.NODE_COMPAT_OPTIONAL_RESUME==='1';
const priorIndex=resume?JSON.parse(await readFile(join(output,'results.json'))):null;
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
assert.equal(metadata.engineSha256,'e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9');
assert.equal(metadata.sourceManifest.length,293);assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
async function verifyNative(){assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(hash(await readFile(engine+'.build.json')),hash(metadataBytes));
  for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);}
await verifyNative();
if(!resume)await mkdir(output);const previous=join(output,'prior-latest');if(!resume)await mkdir(previous);
await writeFile(join(output,'engine.build.json'),metadataBytes);
const modules=[['path','run.mjs','results.json'],['events','run-native-component.mjs','native-component-results.json'],
  ['string-decoder','run-native-component.mjs','native-component-results.json'],['assert','run-native-component.mjs','native-component-results.json'],
  ['querystring','run-native-component.mjs','native-component-results.json'],['util','run-native-component.mjs','native-component-results.json']];
const prior=resume?priorIndex.prior:[];
for(const[name,runner,report]of modules){
  if(resume)continue;
  const directory=join(repository,'tests/node-compat/foundation-'+name),destination=join(previous,'foundation-'+name);
  await cp(directory,destination,{recursive:true,errorOnExist:true,force:false});
  const bytes=await readFile(join(destination,report)),old=JSON.parse(bytes);
  prior.push({name,sourceArchive:destination,report:join(destination,report),sha256:hash(bytes),engineSha256:old.engineSha256,
    runnerSha256:hash(await readFile(join(destination,runner)))});
}
await writeFile(join(output,'prior-latest-index.json'),JSON.stringify(prior,null,2)+'\n');
const common={...process.env,NODE_COMPAT_ENGINE:engine,NODE_COMPAT_ENGINE_SOURCE_ROOT:sourceRoot,
  NODE_COMPAT_TOOLCHAIN:'/tmp/starling-node-compat/native-toolchain-lock',
  NODE_COMPAT_COMPONENTIZE_MODULE:'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',
  NODE_COMPAT_WASMTIME:'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime',
  NODE_COMPAT_ASSERT_OFF_ENGINE:'/tmp/starling-node-compat/foundations-v5/native-freeze/off-path-events.engine.wasm',
  NODE_COMPAT_ASSERT_OFF_SOURCE_ROOT:'/tmp/starling-node-compat/foundations-v5/native-freeze/source',
  NODE_COMPAT_QUERYSTRING_OFF_ENGINE:'/tmp/starling-node-compat/foundations-v5/native-freeze/off-path-events.engine.wasm',
  NODE_COMPAT_QUERYSTRING_OFF_SOURCE_ROOT:'/tmp/starling-node-compat/foundations-v5/native-freeze/source',
  NODE_COMPAT_UTIL_OFF_ENGINE:'/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm',
  NODE_COMPAT_UTIL_OFF_SOURCE_ROOT:'/tmp/starling-node-compat/foundations-v6/native-freeze/source'};
// Validate historical controls before starting any expensive guest packaging.
for(const[control,expected]of [[common.NODE_COMPAT_ASSERT_OFF_ENGINE,'165b59a1fac4f3bab14547a28063908193c2b98767bd5fa835ca00b9b6d8adfc'],
  [common.NODE_COMPAT_UTIL_OFF_ENGINE,'33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516']]){
  const receipt=JSON.parse(await readFile(control+'.build.json'));assert.equal(receipt.engineSha256,expected);assert.equal(hash(await readFile(control)),expected);
}
const results=resume?priorIndex.modules.filter(entry=>entry.code===0):[];
const index={schemaVersion:1,state:'running',atUtc:new Date().toISOString(),scope:'Existing six optional bounded module correctness gates on new core m0.8/v8; no stream/web candidate execution',
  engine,engineSha256:metadata.engineSha256,engineReceiptSha256:hash(metadataBytes),sourceRoot,nativeInputs:293,node:process.version,
  nodeExecutable:process.execPath,nodeSha256:hash(await readFile(process.execPath)),prior,modules:results,
  failedAttempts:resume?[...(priorIndex.failedAttempts??[]),...priorIndex.modules.filter(entry=>entry.code!==0)]:[]};
const indexPath=join(output,'results.json'),localIndex=join(repository,'tests/node-compat/foundations/v8-optional-results.json');
async function save(){await writeFile(indexPath,JSON.stringify(index,null,2)+'\n');await writeFile(localIndex,JSON.stringify(index,null,2)+'\n');}
await save();
for(const[name,runner,reportName]of modules){
  const existing=results.find(entry=>entry.name===name);
  if(existing){assert.equal(hash(await readFile(existing.reportPath)),existing.reportSha256);console.log(JSON.stringify({event:'reused-verified-pass',module:name}));continue;}
  const retry=index.failedAttempts.filter(entry=>entry.name===name).length;
  const directory=join(repository,'tests/node-compat/foundation-'+name),destination=join(output,name+(retry?'-retry-'+retry:''));await mkdir(destination);
  const logPath=join(destination,'runner.log'),log=await open(logPath,'wx');
  console.log(JSON.stringify({event:'start',module:name,output:destination}));
  const started=Date.now(),env={...common,['NODE_COMPAT_'+name.replaceAll('-','_').toUpperCase()+'_OUTPUT']:destination};
  // Historical OFF controls are preserved only where existing runners selected
  // them; do not accidentally inherit unrelated optional-control env values.
  delete env.NODE_COMPAT_EVENTS_OFF_ENGINE;delete env.NODE_COMPAT_EVENTS_OFF_SOURCE_ROOT;
  const child=spawn(process.execPath,[join(directory,runner)],{cwd:repository,env,stdio:['ignore',log.fd,log.fd]});
  const terminal=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',(code,signal)=>resolve({code,signal}));});await log.close();
  const entry={name,runner:join(directory,runner),runnerSha256:hash(await readFile(join(directory,runner))),output:destination,logPath,
    logSha256:hash(await readFile(logPath)),elapsedMs:Date.now()-started,...terminal};results.push(entry);
  if(terminal.code!==0){index.state='failed';entry.failure='Existing module runner failed; source/semantic gates were not relaxed';await save();console.log(JSON.stringify({event:'failed',...entry}));process.exitCode=1;break;}
  const reportPath=join(destination,'results.json'),bytes=await readFile(reportPath),report=JSON.parse(bytes);
  assert.equal(report.engineSha256,metadata.engineSha256,name+' must use exact v8 engine');
  const audits=[];
  function inspect(value){if(!value||typeof value!=='object')return;
    if(Object.hasOwn(value,'interfaceAudit')){const audit=value.interfaceAudit;assert.deepEqual(audit.emittedImports,[]);assert.deepEqual(audit.selectedInterfaces,[]);audits.push(audit);}
    for(const nested of Object.values(value))if(nested&&typeof nested==='object')inspect(nested);}
  inspect(report);assert(audits.length>0,name+' must retain actual final-component audits');
  entry.reportPath=reportPath;entry.reportSha256=hash(bytes);entry.finalComponentAudits=audits.length;entry.emittedImports=[];
  entry.latestReportPath=join(directory,reportName);assert.equal(hash(await readFile(entry.latestReportPath)),entry.reportSha256);
  await verifyNative();await save();console.log(JSON.stringify({event:'passed',module:name,elapsedMs:entry.elapsedMs,finalComponentAudits:audits.length}));
}
if(results.length===modules.length&&results.every(entry=>entry.code===0)){
  await verifyNative();index.state='passed';index.completedAtUtc=new Date().toISOString();index.nativeInputsVerifiedBeforeAfter=true;
  index.orchestratorSha256=hash(await readFile(fileURLToPath(import.meta.url)));await save();console.log(JSON.stringify({event:'complete',state:index.state,modules:results.length,output}));
}
