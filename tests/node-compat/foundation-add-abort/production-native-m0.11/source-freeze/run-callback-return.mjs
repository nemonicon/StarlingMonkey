import assert from 'node:assert/strict';
import * as nodeEvents from 'node:events';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {harness} from './harness.mjs';
import {hash} from './preflight.mjs';
import {callbackReturnObservation} from './callback-return-cases.mjs';
const h=await harness();assert.equal(h.metadata.entropyPolicy,'off');
const sourceFiles=[];
for(const name of ['callback-return-cases.mjs','callback-return-component.mjs','run-callback-return.mjs']){
 const bytes=await readFile(join(h.here,name)),saved=join(h.output,'observation-source',name);await mkdir(join(h.output,'observation-source'),{recursive:true});await writeFile(saved,bytes);sourceFiles.push({name,sha256:hash(bytes),saved});
}
const node=await callbackReturnObservation(nodeEvents);assert.deepEqual(node,{ordinary:1,protectedSignal:1,alreadyAborted:0});
const bundle=await h.bundle(join(h.here,'callback-return-component.mjs'),['node:events']),fixture=await h.build('callback_return_observation',bundle.code),instance=await h.importFixture(fixture);
const jco=JSON.parse(await instance.run()),fresh=h.freshHost(fixture),nativeExpected={ordinary:0,protectedSignal:0,alreadyAborted:0};
assert.deepEqual(jco,nativeExpected);assert.deepEqual(fresh.observed,nativeExpected);assert.notDeepEqual(node,jco);
await h.finish();for(const entry of sourceFiles)assert.equal(hash(await readFile(join(h.here,entry.name))),entry.sha256);
const report={state:'CONFIRMED_FRESH_CALLBACK_RETURN_THEN_GETTER_COUNTEREXAMPLE',observationCompleted:true,nodeCompatibilityPassed:false,recordedAtUtc:new Date().toISOString(),...h.evidence,
 fixture,node:{observed:node,executable:process.execPath,executableSha256:hash(await readFile(process.execPath))},jco:{freshInstance:true,observed:jco},wasmtime:fresh,observationSources:sourceFiles,
 limitation:'Pinned Node22 reads .then on a fresh ordinary EventTarget or protected AbortSignal callback return. Selected native EventTarget currently ignores rval, so those getter effects are absent. Already-aborted queued callback return is correctly discarded on both.',
 sourceBasis:{node:'lib/internal/event_target.js dispatch addCatch(result)',guest:'EventTarget::inner_invoke JS::Call stores rooted rval and does not process it'},
 scope:'Safe ordinary returned objects only; get then increments a counter and returns undefined. No throwing/rejecting thenable, asynchronous listener Promise, Error poisoning, fault, raw/private memory or old engine path. Native304/manifest/CMake/recipe unchanged; fix belongs to future scheduler/callback-result routing work.'};
await h.save(report);console.log(JSON.stringify({state:report.state,nodeCompatibilityPassed:false,node,guest:jco,emittedImports:fixture.emittedImports,output:h.output},null,2));
