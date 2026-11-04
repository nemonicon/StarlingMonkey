import assert from 'node:assert/strict';
import {readFile,open} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const K='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto',STAGE='/private/tmp/starling-node-compat/crypto-owner-source-v2',BASE=join(STAGE,'tests/node-compat/foundation-crypto/native-integration-candidate-v2'),OUT='/tmp/starling-node-compat/crypto-owner-v2-normal-off-bootstrap-root';
const hash=b=>createHash('sha256').update(b).digest('hex'),desc=async path=>{const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};};
async function checked(row){assert.deepEqual(await desc(row.path),row);return JSON.parse(await readFile(row.path,'utf8'));}
async function write(path,value){const h=await open(path,'wx');try{await h.writeFile(JSON.stringify(value,null,2)+'\n');await h.sync();}finally{await h.close();}return desc(path);}
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const pins=await desc(join(K,'reviewed-native-v2-validation-bootstrap-pins-v1.json')),review=await desc(join(K,'native-v2-validation-bootstrap-root-review-v1.json'));assert.equal(pins.sha256,'e6bdb310607ff972133db03ac46c8047cdd2d80fceb4a2d1dcb62d68c8e943a9');assert.equal(review.sha256,'071666bdbac66f21e7c0f4980395f776d49b19274fae8c089fc323df6d83b0bb');
assert.equal((await desc(join(BASE,'index.json'))).sha256,'68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575');
for(const row of JSON.parse(await readFile(join(BASE,'index.json'),'utf8')).files){const d=await desc(join(BASE,row.path));assert.equal(d.sha256,row.sha256);assert.equal(d.bytes,row.bytes);}
for(const row of JSON.parse(await readFile(join(BASE,'artifact-tools/tool-pins.json'),'utf8')).toolDependencies){const d=await desc(join(STAGE,row.path));assert.equal(d.sha256,row.sha256);assert.equal(d.bytes,row.bytes);}
const {cryptoOwnerBootstrapPreflight}=await import(pathToFileURL(join(BASE,'artifact-tools/bootstrap-preflight.mjs')));
const frame=await cryptoOwnerBootstrapPreflight({variant:'normal-off',reviewedPinsPath:pins.path,reviewedPinsSha256:pins.sha256,rootReviewPath:review.path,rootReviewSha256:review.sha256});
const capture=await write(join(OUT,'frame-data.json'),{enginePath:frame.enginePath,sourceRoot:frame.sourceRoot,configuredSourceRoot:frame.configuredSourceRoot,metadata:frame.metadata,pin:frame.pin,variant:frame.variant,selectedManifests:frame.selectedManifests,validationBootstrapOnly:frame.validationBootstrapOnly,operationalAdmission:frame.operationalAdmission});
assert.equal(frame.variant,'normal-off');assert.equal(frame.pin.engineSha256,'36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05');assert.equal(frame.metadata.sourceManifest.length,355);assert.equal(frame.metadata.cryptoKeyOwnershipPolicy.version,'sm-webcrypto-key-owner-and-prototype-guard-source-v1');assert.equal(frame.validationBootstrapOnly,true);assert.equal(frame.operationalAdmission,false);
assert.equal(frame.sourceRoot,'/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source');assert.equal(frame.configuredSourceRoot,STAGE);assert.notEqual(frame.sourceRoot,frame.configuredSourceRoot);
await frame.recheck();await checked(pins);await checked(review);
const result={schemaVersion:1,state:'ROOT_OBSERVED_GENUINE_CRYPTO_OWNER355_NORMAL_OFF_TWO_CONTEXT_JS_BOOTSTRAP_PASSED_V1',variant:'normal-off',reviewedPins:pins,rootReview:review,frameData:capture,enginePath:frame.enginePath,engineSha256:frame.pin.engineSha256,sourceFiles:355,sourceRoot:frame.sourceRoot,configuredSourceRoot:frame.configuredSourceRoot,selectedManifests:frame.selectedManifests.length,recheckPassed:true,readOnlyAdmissionHelpersInvoked:true,intermediatePythonHelperObjectsSeparatelyRetained:false,sourceControlFlowAndCleanFinalOutcomeSupportHelperRechecks:true,engineKeyCryptoGcComponentGuestHostOrTimingExecuted:false,runtimeAcceptanceClaim:false,operationalAdmission:false};
const row=await write(join(OUT,'result.json'),result);console.log(JSON.stringify({result:row,frameData:capture,variant:'normal-off',sourceFiles:355,engineExecuted:false}));
