// Future bounded owned child: read-only source/authority audit, never guest entry.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parentRoot,parentIndexSha256,verifyTimingSources,auditComposedCorrectness} from './admission.mjs';
import {selectTimingPhase} from './phase.mjs';
const here=parentRoot,admissionHere=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
const[indexSha,phasePath,phaseSha]=process.argv.slice(2);await verifyTimingSources(admissionHere,indexSha);
const {executionPreflight}=await import(pathToFileURL(join(here,'runtime-preflight.mjs')));
const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});await on.recheck();await off.recheck();
if(phasePath){assert(/^[0-9a-f]{64}$/.test(phaseSha??''));const bytes=await readFile(phasePath);assert.equal(hash(bytes),phaseSha);const phase=selectTimingPhase(JSON.parse(bytes));assert.equal(phase.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(phase.timingAdmissionSourceIndexSha256,indexSha);await auditComposedCorrectness(phase,indexSha);assert.equal(phase.pairPinsSha256,on.pairSha256);
 for(const name of['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']){const row=phase[name];assert.equal(hash(await readFile(row.reportPath)),row.reportSha256);assert.equal(hash(await readFile(row.rootReviewPath)),row.rootReviewSha256);}
 for(const row of Object.values(phase.components)){assert.equal(hash(await readFile(row.componentPath)),row.componentSha256);assert.equal(hash(await readFile(row.enginePath)),row.engineSha256);for(const file of row.transpiledFiles)assert.equal(hash(await readFile(join(dirname(row.modulePath),file.name))),file.sha256);}}
console.log(JSON.stringify({state:'READ_ONLY_POST_OPERATION_SOURCE_AUDIT_PASSED',sourceFamilyIndexSha256:parentIndexSha256,timingAdmissionSourceIndexSha256:indexSha,pairPinsSha256:on.pairSha256,phaseSha256:phasePath?phaseSha:null,guestExecuted:false}));
