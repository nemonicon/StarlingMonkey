// Source/phase binding only. No host or component import/execution here.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const INPUTS_SHA='879d8c24241380fe8391e66056579f941cc3bb587f130c296b83d8c4f7062158';
const PHASE_SHA='eb1caa1168f57f135c1b38c924ef1ce99305aa34688419edd5847e242a5f9c29';
const phasePath=resolve(here,'../production-adoption-v1/http-component-phase-root-review-v1.json');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function requireSupportedFixtureOptions(environment){
  assert.notEqual(environment.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1',
    'This fixed combined HTTP fixture has no optional intrinsics report; remove NODE_COMPAT_HTTP_REQUIRE_INTRINSICS=1 before host startup');
}
export async function verifyRetrySource(){
  requireSupportedFixtureOptions(process.env);
  assert.equal(resolve(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS??''),phasePath,'Use the original reviewed external phase document');
  assert.equal(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256,PHASE_SHA);
  async function recheck(){
    requireSupportedFixtureOptions(process.env);
    const raw=await readFile(join(here,'input-freeze.json'));assert.equal(hash(raw),INPUTS_SHA,'Retry source seal changed before parsing');
    const document=JSON.parse(raw);assert.equal(document.schemaVersion,1);
    const seen=new Set();let template;
    for(const row of document.inputs){const path=resolve(here,row.path);assert(!seen.has(path));seen.add(path);
      const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const bytes=await readFile(path);
      assert.equal(hash(bytes),row.sha256,path);assert.equal(bytes.length,row.bytes,path);
      if(path===join(here,'verify-retry.template.mjs'))template=bytes.toString();}
    assert.equal(typeof template,'string');assert.equal(await readFile(fileURLToPath(import.meta.url),'utf8'),template.replaceAll('@'+'INPUTS_SHA'+'@',INPUTS_SHA));
    const phase=await readFile(phasePath);assert.equal(hash(phase),PHASE_SHA);
    assert.equal(JSON.parse(phase).state,'ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1');
    return{state:'EXACT_RETRY_SOURCE_AND_UNCHANGED_REVIEWED_PHASE_VERIFIED',sourceSha256:INPUTS_SHA,phaseSha256:PHASE_SHA,files:seen.size};
  }
  const report=await recheck();return{report,recheck};
}
