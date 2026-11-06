// Pure whole-current-metadata validation; no imports of engine/generated code.
import assert from 'node:assert/strict';
export function validateNative(native,plan){
 assert.equal(native.schemaVersion,1);assert.equal(native.metadataKind,'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1');assert.deepEqual(native.engine,plan.engine);
 assert.equal(native.nativePolicyInputCount,435);assert.equal(native.buildSupportInputCount,387);assert.equal(native.embeddingInputCount,3);assert.equal(native.actualCompileRows.length,80);assert.equal(native.actualSeparateEmbeddingCompileRows.length,1);
 assert.equal(native.selectedModuleManifests.public.length,22);assert.equal(native.selectedModuleManifests.private.length,2);assert.equal(native.requestedCMake.SPIDERMONKEY_INTL,'ON');assert.equal(native.observedCMake.SPIDERMONKEY_INTL.value,'ON');
 for(const k of ['old83MetadataProjected','engineExecuted','guestExecuted','adoption'])assert.equal(native[k],false);
 for(const [k,v]of Object.entries(plan.nativeDescriptorBindings))assert.deepEqual(native[k],v,k);
 assert.equal(native.actualRustConfiguration.lock.sha256,native.actualAggregateLock.sha256);
}
