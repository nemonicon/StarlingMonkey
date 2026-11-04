// PREPARED ONLY. Never execute with an old or module-ON engine. Exact corrected
// native source pins and observed OFF flag are checked before packaging.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness} from './native-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const harness=await nativeHarness({streamWebEnabled:false,
  output:process.env.NODE_COMPAT_STREAM_GUARD_OFF_OUTPUT??'/tmp/starling-node-compat/stream-web-guard-off-future'});
const bundled=await harness.bundle(join(here,'native-controller-off.mjs'));assert.deepEqual(bundled.imports,[]);
assert(!bundled.moduleIds.some(id=>/node_modules|factory|fixture-record|production-candidate\/(?:codecs|byob|readable-iteration)\.mjs/.test(id)),
  'OFF control must not install or bundle wrappers');
await writeFile(join(harness.output,'application.bundle.mjs'),bundled.code);
const component=await harness.artifact('native-controller-off',bundled.code),calls=[];
function check(report,index){assert(!report.failure,JSON.stringify(report.failure));assert(report.passed);assert.equal(report.calls,index);
  assert.equal(report.cases.length,6);assert.equal(report.additionalInvalidReceivers,16);assert(report.nativeMethodsWithoutWrappers&&report.temporaryStreamsOnlyDeployedAndCleaned);}
for(let index=1;index<=3;index++){const report=JSON.parse(await component.instance.run());calls.push(report);await writeFile(join(harness.output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);}
const wasmtimeReport=await harness.hostRun('native-controller-off',component.path);check(wasmtimeReport,1);assert.deepEqual(wasmtimeReport,calls[0]);
const sources=['native-controller-off.mjs','run-native-controller-off.mjs','native-harness.mjs','native-preflight.mjs','native-preflight-contract.json',
  '../candidate/controller-cases.mjs','../candidate/codec-cases.mjs','../profile.wit'];
const{instance,...componentMetadata}=component;
const result={schema:1,state:'executed-corrected-native-off',atUtc:new Date().toISOString(),
  scope:'Corrected native Transform controller receiver/state gate with stream module explicitly OFF, no JS wrappers or test hooks',
  engine:harness.engine,engineSha256:harness.metadata.engineSha256,sourceRoot:harness.sourceRoot,metadata:harness.metadata,
  componentizer:harness.componentizer,safetyAudit:harness.safetyAudit,bundle:{imports:[],moduleIds:bundled.moduleIds},component:componentMetadata,
  calls,wasmtime:harness.wasmtimeVersion,wasmtimeReport,
  sourceManifest:await Promise.all(sources.map(async path=>({path,sha256:harness.hash(await readFile(join(here,path)))}))),
  limitations:['Native WrongReceiver errors are TypeError without Node ERR_INVALID_THIS; ON Node-facing wrappers retain own Node-style code',
    'Only ordinary invalid receivers and valid closed/errored state cases; no allocation fault, raw memory or old-native hazardous entry']};
await writeFile(join(harness.output,'results.json'),JSON.stringify(result,null,2)+'\n');await writeFile(join(here,'native-controller-off-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output:harness.output,correctedNativeOnly:true,moduleOff:true,zeroImports:true,nativeCases:6,additionalInvalidReceivers:16}));
