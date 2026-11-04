// Synthetic mapping fixtures only. No classifier/bootstrap/artifact IO or crypto.
import assert from 'node:assert/strict';
import {captureBootstrapContexts} from './artifact-tools/bootstrap-contexts.mjs';
const contract={nativeConfiguredSourceRoot:'/tmp/starling-node-compat/crypto-owner-source-v2',frozenSourceRoot:'/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source'};
const authority={proposalIndexSha256:'a'.repeat(64),reviewedPinsSha256:'b'.repeat(64),rootReviewSha256:'c'.repeat(64)};
const actual={schemaVersion:1,state:'ROOT_REVIEWED_CRYPTO_OWNER355_BUILD_VALIDATION_BOOTSTRAP_PASSED',validationBootstrapOnly:true,operationalAdmission:false,guestExecuted:false,...authority,configuredSourceRoot:'/private/tmp/starling-node-compat/crypto-owner-source-v2',sourceRoot:contract.frozenSourceRoot,pin:{sourceRoot:contract.frozenSourceRoot}};
let checks=0;const yes=f=>{f();checks++;},no=f=>{assert.throws(f);checks++;};
let captured;yes(()=>{captured=captureBootstrapContexts(actual,contract,authority);assert.equal(captured.configuredSourceRoot,actual.configuredSourceRoot);assert.equal(captured.sourceRoot,actual.sourceRoot);assert(Object.isFrozen(captured));});
yes(()=>assert.deepEqual(captureBootstrapContexts({...actual,configuredSourceRoot:contract.nativeConfiguredSourceRoot},contract,authority),{configuredSourceRoot:contract.nativeConfiguredSourceRoot,sourceRoot:actual.sourceRoot}));
for(const changed of[
 {configuredSourceRoot:undefined},{configuredSourceRoot:actual.sourceRoot},{configuredSourceRoot:'/tmp/other'},
 {configuredSourceRoot:'/tmp/a/../crypto-owner-source-v2'},{configuredSourceRoot:'relative'},{configuredSourceRoot:'/tmp/x\0y'},{configuredSourceRoot:'/tmp/x\\y'},
 {sourceRoot:actual.configuredSourceRoot},{sourceRoot:'/tmp/other'},{pin:{sourceRoot:'/tmp/other'}},
 {proposalIndexSha256:'d'.repeat(64)},{reviewedPinsSha256:'d'.repeat(64)},{rootReviewSha256:'d'.repeat(64)},
 {validationBootstrapOnly:false},{operationalAdmission:true},{guestExecuted:true},{state:'UNREVIEWED'},
])no(()=>captureBootstrapContexts({...actual,...changed},contract,authority));
yes(()=>{const caller=structuredClone(actual),privateValue=captureBootstrapContexts(caller,contract,authority);caller.configuredSourceRoot='/tmp/changed';caller.sourceRoot='/tmp/changed-frozen';caller.pin.sourceRoot='/tmp/changed-frozen';assert.equal(privateValue.configuredSourceRoot,captured.configuredSourceRoot);assert.equal(privateValue.sourceRoot,captured.sourceRoot);});
no(()=>captureBootstrapContexts({...actual,configuredSourceRoot:'/tmp/changed-after-initial'},contract,authority));
process.stdout.write(JSON.stringify({schemaVersion:1,state:'PURE_CRYPTO_BOOTSTRAP_CONTEXT_MAPPING_FIXTURES_PASSED',checks,syntheticFixturesOnly:true,pureMappingFunctionExecuted:true,configuredPathTakenFromActualProofField:true,classifierOrBootstrapOrArtifactHelperExecuted:false,SDKGitNativeCryptoGCGuestOrStageExecuted:false,operationalAdmission:false})+'\n');
