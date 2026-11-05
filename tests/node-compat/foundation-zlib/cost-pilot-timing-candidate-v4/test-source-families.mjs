// Source/read-hash and owned scratch DATA only. Never imports a timing body.
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkIndexedFamily,checkFileRows,assertSourceFamilyAudit,ANCESTORS} from './source-families.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));let checks=0;
const check=fn=>{fn();checks++;},reject=async fn=>{await assert.rejects(fn);checks++;};
const hash=b=>createHash('sha256').update(b).digest('hex'),descriptor=async path=>{const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};};
const inherited=[];
for(const row of ANCESTORS){const family=await checkIndexedFamily(row);await family.recheck();inherited.push({index:family.index,indexedMembers:family.rows.length,initialAndRecheckPassed:true});checks+=2;}
check(()=>assert.deepEqual(inherited.map(v=>v.indexedMembers),[85,26,50]));
const scratch=await mkdtemp('/private/tmp/starling-node-compat/zlib-cost-source-families-v4-');
async function fixture(name){
 const root=join(scratch,name);await mkdir(root,{mode:0o700});const member=join(root,'helper.mjs');await writeFile(member,'export const fixture = true;\n',{flag:'wx'});const row=await descriptor(member),index=join(root,'index.json');
 await writeFile(index,JSON.stringify({schemaVersion:1,files:[{...row,path:'helper.mjs'}]})+'\n',{flag:'wx'});return{root,member,index:await descriptor(index)};
}
const normal=await fixture('normal'),captured=await checkIndexedFamily(normal.index);await captured.recheck();checks+=2;
const initial=await fixture('initial-member-tamper');await writeFile(initial.member,'changed before first authentication\n');await reject(()=>checkIndexedFamily(initial.index));
const later=await fixture('recheck-member-tamper'),held=await checkIndexedFamily(later.index);await writeFile(later.member,'changed after authenticated capture\n');await reject(()=>held.recheck());
const manifest=await fixture('initial-index-tamper');await writeFile(manifest.index.path,'{}\n');await reject(()=>checkIndexedFamily(manifest.index));
const manifestLater=await fixture('recheck-index-tamper'),heldManifest=await checkIndexedFamily(manifestLater.index);await writeFile(manifestLater.index.path,'{}\n');await reject(()=>heldManifest.recheck());
const extra=await fixture('unlisted-source');await writeFile(join(extra.root,'unlisted.mjs'),'not indexed\n',{flag:'wx'});await reject(()=>checkIndexedFamily(extra.index));
const extraLater=await fixture('unlisted-at-recheck'),heldExtra=await checkIndexedFamily(extraLater.index);await writeFile(join(extraLater.root,'unlisted.mjs'),'not indexed\n',{flag:'wx'});await reject(()=>heldExtra.recheck());
const dependency=await fixture('runtime-dependency-tamper'),depRow=await descriptor(dependency.member),deps=await checkFileRows([depRow]);await writeFile(dependency.member,'changed imported source\n');await reject(()=>deps.recheck());
const mutation=await fixture('caller-primitive-mutation'),mutable=[await descriptor(mutation.member)],pending=checkFileRows(mutable);mutable[0].path=join(scratch,'redirect');mutable.pop();const privateRows=await pending;await privateRows.recheck();checks+=2;
check(()=>assert.throws(()=>assertSourceFamilyAudit({sourceAuthenticationOnly:true,recheck:async()=>{}},normal.index)));
const guard=await readFile(join(HERE,'parent-guard.template.mjs'),'utf8'),worker=await readFile(join(HERE,'worker-body.mjs'),'utf8');
check(()=>assert(guard.includes('const inheritedFamilies=await captureSourceFamilies(ownRow)')));
check(()=>assert(guard.includes('await inheritedFamilies.recheck();await own.recheck()')));
check(()=>assert(worker.includes('await sourceFamilyAudit.recheck();await regular(inputRow)')));
for(const name of['run.mjs','worker.mjs','prepare-plan.mjs']){const source=await readFile(join(HERE,name),'utf8');check(()=>assert(source.indexOf('await captureSourceFamilies(')<source.indexOf('await import(')));}
console.log(JSON.stringify({schemaVersion:1,state:'COMPLETE_SOURCE_FAMILY_READ_HASH_AND_SCRATCH_NEGATIVES_PASSED_V4',checks,scratch,
 inherited,memberAndIndexTamperInitialAndRecheckRefused:true,unlistedMembershipInitialAndRecheckRefused:true,
 runtimeImportedFileRecheckRefused:true,callerMutationCapturedPrivately:true,fakeSourceCapsuleRefused:true,
 publicBootstrapsAuthenticateBeforeCustomBodyImports:true,parentAndWorkerFinalCapturedSourceRechecksPresent:true,
 sourceHelperScratchFilesNeverImportedOrExecuted:true,providerGuestPreflightWorkerNativeJcoWasmtimePilotTimingExecuted:false,operationalAdmission:false}));
