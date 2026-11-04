// Pure finite contracts. No filesystem, package, native or guest imports.
import assert from 'node:assert/strict';
export const labels=Object.freeze(['normal-off','normal-runtime','gc-off','disabled-off']);
export const scopes=Object.freeze(['release-off','allocator-gc','focused-off','focused-runtime','focused-gc','getter']);
export const consumerValidationSha256='36964b2dff52497ed43ce89ec34dbec1610d03d180a477510189150907ded65b';
export function assertConsumerPrerequisite(document){
 assert.equal(document.state,'ROOT_REVIEWED_CONSUMERS355_BOUNDED_COMPONENT_VALIDATION_V1');assert.equal(document.nativeSourceFiles,355);
 assert.equal(document.totalReturnedStrings,207);assert.equal(document.scope.operationalAdmission,false);assert.equal(document.scope.productionAcceptanceIssued,false);
 assert.equal(document.scope.fullNodeOrFullBufferOrFullConsumersSupportClaim,false);
}
export function variantForScope(scope){assert(scopes.includes(scope));return scope==='focused-runtime'?'normal-runtime':['allocator-gc','focused-gc'].includes(scope)?'gc-off':'normal-off';}
export function assertRuntimeAuthority(document,{familyIndexSha256,scope,output}){
 assert(/^[0-9a-f]{64}$/.test(familyIndexSha256??''));assert(typeof output==='string'&&output.startsWith('/'));
 assert(document&&document.state==='ROOT_AUTHORIZED_FRESH_CONSUMERS355_RELEASE_GATES_V1');
 assert.equal(document.familyIndexSha256,familyIndexSha256);assert.equal(document.operationalAdmission,false);
 assert.equal(document.consumerValidationSha256,consumerValidationSha256,'Separate bounded consumer validation prerequisite required; no transfer to new release results');
 assert.equal(document.allowTiming,false);assert.equal(document.allowNativeBuild,false);
 assert.equal(document.noResume,true);assert.equal(document.noPriorPassReuse,true);
 assert(scopes.includes(scope));const item=document.scopes?.[scope];assert(item&&item.approved===true,'Scope authority remains NULL/held');
 assert.equal(item.variant,variantForScope(scope));assert.equal(item.output,output);
 assert(Number.isSafeInteger(item.deadlineMs)&&item.deadlineMs>=1000&&item.deadlineMs<=7200000);
 return Object.freeze({...item});
}
export function assertFourPins(pins,review,pinsSha256){
 assert.equal(pins.state,'ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1');
 assert.equal(review.reviewedPinsSha256,pinsSha256);assert.equal(review.proposalIndexSha256,'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378');
 assert.equal(review.operationalAdmission,false);assert.equal(pins.operationalAdmission,false);
 assert.equal(pins.sourceFiles,355);assert.equal(pins.externalSources,3);
 for(const label of labels){const pin=pins.variants?.[label],actual=review.variants?.[label];assert(pin&&actual,'Four independently reviewed native tuples required');
  assert.equal(pin.reviewRequired,false);assert.equal(pin.variant,label);assert.equal(pin.state,'reviewed-consumers355-native-build-for-validation');
  assert.equal(pin.gcStress,label==='gc-off');assert.equal(pin.entropyPolicy,label==='normal-runtime'?'runtime-only':'off');
  assert.equal(pin.runtimeAcceptanceClaim,false);assert.equal(pin.runtimeBackendProof.verified,false);
  for(const key of ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256'])assert.equal(pin[key],actual[key],label+':'+key);
 }
 return true;
}
export function assertFrame(metadata,sourceRoot,frame){
 assert(frame&&frame.validationBootstrapOnly===true&&frame.operationalAdmission===false,'No captured genuine355 validation frame');
 assert.equal(sourceRoot,frame.sourceRoot);assert.deepEqual(metadata,frame.metadata,'Caller cannot project/subset/relable genuine metadata');
 assert.equal(metadata.sourceManifest.length,355);assert.equal(new Set(metadata.sourceManifest.map(row=>row.path)).size,355);
 assert.equal(metadata.syntheticMetadataOnly===true,false);assert.equal(metadata.diagnosticOnly===true,false);
 return true;
}
export function assertSourceTransition(before,after,changes,added){
 const old=new Map(before.map(row=>[row.path,row.sha256])),next=new Map(after.map(row=>[row.path,row.sha256]));
 assert.equal(old.size,before.length);assert.equal(next.size,after.length);
 assert.equal(next.size,old.size+added.length);const changeMap=new Map(changes.map(row=>[row.path,row]));
 assert.equal(changeMap.size,changes.length);assert.equal(new Set(added).size,added.length);
 for(const [path,digest]of old){const delta=changeMap.get(path);assert.equal(next.get(path),delta?delta.afterSha256:digest,path);if(delta)assert.equal(delta.beforeSha256,digest,path);}
 for(const path of added){assert(!old.has(path)&&next.has(path),path);}
 for(const path of next.keys())assert(old.has(path)||added.includes(path),'Undeclared source addition: '+path);
}
