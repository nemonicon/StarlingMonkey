// New all-fresh serial OFF batch. No resume, prior report reuse or native build.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {verifyReleaseOff,requireFreshOutput,completeReleaseScope,here,repository,hash} from './preflight.mjs';
import {releaseJobs} from './job-plan.mjs';
import {runSerial,fixedEnvironment,spawnJob,publish,countAudits} from './serial.mjs';
const admission=await verifyReleaseOff(); // Before toolchain, child, old result or output.
const output=await requireFreshOutput('NODE_COMPAT_PRODUCTION_RELEASE_OUTPUT');await mkdir(output);
const jobs=releaseJobs(here,output),environment=fixedEnvironment(admission,process.env);
assert.equal(jobs.length,8);
const result={schemaVersion:1,state:'running',engineSha256:admission.production.engineSha256,sourceFiles:342,admission:admission.report,
  jobs:[],reusedResults:0,resumeSupported:false,scope:'Fresh ordinary Release entropy-OFF private-ticks core/allocator/Web/six-foundation/strict4 replay only; HTTP and GC are separate gates'};
const path=join(output,'results.json');await publish(path,result);
try{
  await runSerial(jobs,async job=>{
    await admission.recheck();
    const entry=await spawnJob(job,{output,environment,repository});result.jobs.push(entry);
    if(entry.code!==0){result.state='failed';await publish(path,result);return entry;}
    const reportPath=join(job.output,job.report),completionPath=join(job.output,job.completion);
    const reportBytes=await readFile(reportPath),report=JSON.parse(reportBytes),sealBytes=await readFile(completionPath),seal=JSON.parse(sealBytes);
    assert.equal(report.engineSha256,admission.production.engineSha256);assert.equal(seal.consumedInputsRecheckedAfterRun,true);
    const sealEngine=seal.production?.engineSha256??seal.engineSha256;
    assert.equal(sealEngine,admission.production.engineSha256);
    if(job.name==='optional'){assert.equal(report.state,'passed');assert.equal(report.modules.length,6);assert(report.modules.every(row=>row.code===0&&row.completionSha256));}
    else assert(countAudits(report)>0,'Complete final-component interface audits required');
    entry.reportPath=reportPath;entry.reportSha256=hash(reportBytes);entry.completionPath=completionPath;entry.completionSha256=hash(sealBytes);
    await admission.recheck();await publish(path,result);return entry;
  });
  if(result.jobs.length!==8||result.jobs.some(row=>row.code!==0)){process.exitCode=1;}
  else{await admission.recheck();result.state='passed';result.completedAtUtc=new Date().toISOString();await publish(path,result);
    await completeReleaseScope(output,admission,{scope:'All eight OFF jobs completed fresh; no prior runtime pass reused',jobs:8,reportSha256:hash(await readFile(path))});}
}catch(error){result.state='failed';result.error={name:error.name,code:error.code,message:error.message};await publish(path,result);throw error;}
