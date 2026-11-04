import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {verifyReleaseOff,requireFreshOutput,completeReleaseScope,here,repository,modules,moduleOutputVariable,hash} from './preflight.mjs';
import {runSerial,fixedEnvironment,spawnJob,publish} from './serial.mjs';
const admission=await verifyReleaseOff(); // Null pins stop before output/old controls/loaders.
const output=await requireFreshOutput('NODE_COMPAT_OPTIONAL_OUTPUT');await mkdir(output);
const environment=fixedEnvironment(admission,process.env);
const jobs=modules.map(name=>({name,runner:join(here,'run-'+name+'.mjs'),variable:moduleOutputVariable(name),output:join(output,name)}));
const result={schemaVersion:1,state:'running',engineSha256:admission.production.engineSha256,sourceFiles:342,
  admission:admission.report,modules:[],scope:'Fresh complete six-foundation replay only; no prior pass reuse or scheduler/ALS/reset proof'};
const path=join(output,'results.json');await publish(path,result);
try{
  await runSerial(jobs,async job=>{
    await admission.recheck();await requireFreshOutputForJob(job);
    const entry=await spawnJob(job,{output,environment,repository});result.modules.push(entry);
    if(entry.code!==0){result.state='failed';await publish(path,result);return entry;}
    const reportPath=join(job.output,'results.json'),completionPath=join(job.output,'release-module-admission-complete.json');
    const reportBytes=await readFile(reportPath),completionBytes=await readFile(completionPath),completion=JSON.parse(completionBytes);
    assert.equal(completion.production.engineSha256,admission.production.engineSha256);assert.equal(completion.module,job.name);
    assert.equal(completion.reportSha256,hash(reportBytes));assert.equal(completion.consumedInputsRecheckedAfterRun,true);
    entry.reportPath=reportPath;entry.reportSha256=hash(reportBytes);entry.completionPath=completionPath;entry.completionSha256=hash(completionBytes);
    entry.finalComponentAudits=completion.checked.finalComponentAudits;assert(entry.finalComponentAudits>0);
    await admission.recheck();await publish(path,result);return entry;
  });
  if(result.modules.length!==6||result.modules.some(row=>row.code!==0)){process.exitCode=1;}
  else{await admission.recheck();result.state='passed';result.completedAtUtc=new Date().toISOString();await publish(path,result);
    await completeReleaseScope(output,admission,{scope:'All six original module runner bodies completed fresh',modules:6,reportSha256:hash(await readFile(path))});}
}catch(error){result.state='failed';result.error={name:error.name,code:error.code,message:error.message};await publish(path,result);throw error;}
async function requireFreshOutputForJob(job){const prior=process.env[job.variable];try{process.env[job.variable]=job.output;await requireFreshOutput(job.variable);}finally{if(prior===undefined)delete process.env[job.variable];else process.env[job.variable]=prior;}}
