// Pure context mapping only. No filesystem, child, artifact or crypto access.
import assert from 'node:assert/strict';
import {isAbsolute,resolve} from 'node:path';
function canonical(value){
 assert.equal(typeof value,'string');assert(value&&!value.includes('\0')&&!value.includes('\\'));
 assert(isAbsolute(value)&&resolve(value)===value,'Normalized absolute context path');
 return value.replace(/^\/tmp(?=\/|$)/,'/private/tmp');
}
export function captureBootstrapContexts(actual,contract,authority){
 assert(actual&&typeof actual==='object'&&contract&&authority);
 assert.equal(actual.schemaVersion,1);assert.equal(actual.state,'ROOT_REVIEWED_CRYPTO_OWNER355_BUILD_VALIDATION_BOOTSTRAP_PASSED');
 assert.equal(actual.validationBootstrapOnly,true);assert.equal(actual.operationalAdmission,false);assert.equal(actual.guestExecuted,false);
 for(const field of['proposalIndexSha256','reviewedPinsSha256','rootReviewSha256'])assert.equal(actual[field],authority[field],'Actual authenticated Python proof '+field);
 // Keep the actual authenticated primitive spellings; normalization is used
 // only for the declared system /tmp alias comparison, never to invent roots.
 const configuredSourceRoot=actual.configuredSourceRoot,sourceRoot=actual.sourceRoot;
 assert.equal(canonical(configuredSourceRoot),canonical(contract.nativeConfiguredSourceRoot),'Configured admission/tool context');
 assert.equal(canonical(sourceRoot),canonical(contract.frozenSourceRoot),'Frozen native/runtime context');
 assert.equal(canonical(sourceRoot),canonical(actual.pin?.sourceRoot),'Actual reviewed frozen pin context');
 assert.notEqual(canonical(configuredSourceRoot),canonical(sourceRoot),'Configured and frozen contexts remain distinct');
 return Object.freeze({configuredSourceRoot,sourceRoot});
}
