// Ordinary corrected module-OFF control: bundler denial AND actual guest denial.
import assert from 'node:assert/strict';
import {writeFile,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness} from './native-harness.mjs';
const h=await nativeHarness({streamWebEnabled:false,
  output:process.env.NODE_COMPAT_STREAM_WEB_OFF_ADMISSION_OUTPUT??'/tmp/starling-node-compat/foundations-v9/off-module-admission'});
const results=[];
for(const[alias,id]of [['canonical','node:stream/web'],['bare','stream/web']]){
  const source=`import * as web from ${JSON.stringify(id)}; export function run(){return typeof web.ReadableStream;}`;
  const input=join(h.output,alias+'.input.mjs');await writeFile(input,source);
  let bundlerError,guestError;
  try{await h.bundle(input);}catch(error){bundlerError=error.message;}
  assert.match(bundlerError??'',/not admitted/,'OFF imports must not fall back to a JavaScript adapter');
  // Bypass only the bundler here to test the deployed engine's actual resolver,
  // never the native source/feature/receiver safety admission.
  try{await h.artifact(alias,source);}catch(error){guestError=error.message;}
  assert(guestError,'OFF engine unexpectedly defines '+id);assert.match(guestError,/stream\/web/);
  results.push({id,input,source,sourceSha256:h.hash(source),bundlerError,guestError,
    bundlerDenied:true,actualGuestInitializationDenied:true});
}
const report={schema:1,state:'corrected-stream-web-off-admission-passed',engine:h.engine,
  engineSha256:h.metadata.engineSha256,metadata:h.metadata,safetyAudit:h.safetyAudit,
  componentizer:h.componentizer,results,runnerSha256:h.hash(await readFile(fileURLToPath(import.meta.url))),
  scope:'Two actual module-OFF import failures, independent of source-only manifest denial; no successful component claimed.'};
await writeFile(join(h.output,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,engineSha256:report.engineSha256,bundlerDenials:2,actualGuestInitializationDenials:2,output:h.output}));
