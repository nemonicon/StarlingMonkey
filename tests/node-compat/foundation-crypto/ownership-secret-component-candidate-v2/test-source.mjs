// Host-only pure checks. The construction API is never invoked.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {requiredPackagingEnvironment,constructionAuthority,captureDescriptor} from './build.mjs';
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url)));
let checks=0;
const good=refs.requiredPackagingEnvironment;
assert.deepEqual(requiredPackagingEnvironment({...good},refs.physicalRoles),good);checks++;
assert(Object.isFrozen(requiredPackagingEnvironment(good,refs.physicalRoles)));checks++;
for(const name of Object.keys(good)){
 for(const value of [undefined,'',good[name]+'-different']){
  assert.throws(()=>requiredPackagingEnvironment({...good,[name]:value},refs.physicalRoles),{message:'Required packaging environment: '+name});checks++;
 }
}
assert.throws(()=>requiredPackagingEnvironment(null,refs.physicalRoles),/NODE_COMPAT_TOOLCHAIN/);checks++;
const own={path:new URL('./index.json',import.meta.url).pathname,sha256:'a'.repeat(64),bytes:1};
const root={...JSON.parse(await readFile(new URL('./future-root-authority.template.json',import.meta.url))),state:'ROOT_REVIEWED_SECRET355_COMPONENT_CONSTRUCTION_V2',phase:'component-build',sourceIndex:own,entry:{path:new URL('./build.mjs',import.meta.url).pathname},componentBuildAllowed:true,componentInitializationAllowed:true,retainedReadOnlyApiAllowed:true,retainedConfig:refs.priorReadOnlyConfigData};
assert.equal(constructionAuthority(root,own,refs),true);checks++;
for(const name of ['outputRoot','externalRoot','engineSha256']){
 assert.throws(()=>constructionAuthority({...root,[name]:root[name]+'-wrong'},own,refs));checks++;
}
for(const name of ['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','generatedModuleImportAllowed','operationalAdmission']){
 assert.throws(()=>constructionAuthority({...root,[name]:true},own,refs));checks++;
}
assert.throws(()=>constructionAuthority({...root,state:'ROOT_REVIEWED_SECRET355_COMPONENT_CONSTRUCTION_V1'},own,refs));checks++;
assert.throws(()=>constructionAuthority({...root,requiredPackagingEnvironment:{...good,NODE_COMPAT_TOOLCHAIN:'/wrong'}},own,refs));checks++;
assert.throws(()=>captureDescriptor({...own,path:own.path+'/../index.json'}));checks++;
process.stdout.write(JSON.stringify({schemaVersion:1,checks,passed:true,inertModuleImported:true,constructionApiInvoked:false,retainedApiInvoked:false,packagerImported:false,engineOrGuestExecuted:false})+'\n');
