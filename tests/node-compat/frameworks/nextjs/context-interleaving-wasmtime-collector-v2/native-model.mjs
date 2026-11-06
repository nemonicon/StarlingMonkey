// Genuine whole metadata is retained; exact late Root selection, no frame casts.
import assert from 'node:assert/strict';
export function validateNative(native,authority,constructorAuthority){
 assert(native&&typeof native==='object'&&!Array.isArray(native));
 const fixed=authority.metadataExpectedFixedValues;
 assert(fixed&&typeof fixed==='object'&&!Array.isArray(fixed));
 assert(Object.hasOwn(fixed,'schemaVersion')&&Object.hasOwn(fixed,'metadataKind')&&Object.hasOwn(fixed,'engine'));
 assert.equal(fixed.schemaVersion,1);assert.equal(typeof fixed.metadataKind,'string');assert(fixed.metadataKind.length>0);
 assert.deepEqual(fixed.engine,authority.engine);assert.deepEqual(native.engine,authority.engine);
 assert.deepEqual(constructorAuthority.engine,authority.engine);assert.deepEqual(constructorAuthority.nativeMetadata,authority.nativeMetadata);
 assert.deepEqual(constructorAuthority.metadataExpectedFixedValues,fixed);
 assert.deepEqual(constructorAuthority.engineBuildEvidence,authority.engineBuildEvidence);
 for(const[k,v]of Object.entries(fixed))assert.deepEqual(native[k],v,k);
 return true;
}
