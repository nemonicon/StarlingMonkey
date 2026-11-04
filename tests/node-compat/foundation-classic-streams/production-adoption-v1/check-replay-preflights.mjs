// Read-only replay-source admission. No runner, componentizer or guest call.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const family=process.argv[2]??'production-regression-activated-v1';
assert(['production-regression-activated-v1','production-regression-activated-v2','production-regression-activated-v3'].includes(family));
const root=resolve(here,'..',family);
const expected=process.argv[3]??'cc4ceb27efb442d1ec5aeb38880f86ddef12776ed97aa8d9862433fa080930be';
assert(/^[0-9a-f]{64}$/.test(expected));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function source(){
  const raw=await readFile(join(root,'index.json'));assert.equal(hash(raw),expected);
  const index=JSON.parse(raw);
  for(const row of index.files){
    assert(!row.path.startsWith('/')&&!row.path.split('/').includes('..'));
    const data=await readFile(join(root,row.path));assert.equal(hash(data),row.sha256);assert.equal(data.length,row.bytes);
  }
  return index.files.length;
}
const files=await source();
const {verifyProductionTicks}=await import(pathToFileURL(join(root,'common/preflight.mjs')));
const reports=[];
function clearSelectedEngine(){
  for(const key of ['NODE_COMPAT_ENGINE','NODE_COMPAT_ENGINE_SOURCE_ROOT','NODE_COMPAT_ENGINE_METADATA'])delete process.env[key];
}
for(const options of [{gcStress:false},{gcStress:true},{gcStress:false,entropyPolicy:'runtime-only'}]){
  clearSelectedEngine();
  const admission=await verifyProductionTicks(options);await admission.recheck();
  reports.push(admission.report);
}
clearSelectedEngine();
const {verifyReleaseOff}=await import(pathToFileURL(join(root,'release/preflight.mjs')));
const release=await verifyReleaseOff();await release.recheck();await source();
const result={schemaVersion:1,state:'ROOT_ACTUAL_REPLAY_PREFLIGHTS_PASSED',
  indexSha256:expected,sourceFiles:files,nativeReports:reports,releaseReport:release.report,
  componentizerInvoked:false,guestInvoked:false,runtimeSupportAccepted:false};
const suffix=family.endsWith('-v3')?'-v3':family.endsWith('-v2')?'-v2':'';
await writeFile(join(here,'replay-preflight'+suffix+'-results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,nativeModes:reports.length,releaseAdmission:true,sourceFiles:files,guestInvoked:false}));
