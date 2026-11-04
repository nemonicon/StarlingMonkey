// Actual finite source admission only. No engine bytes, Wasm or toolchain loads.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateProductionMetadata} from '../production-followon-capability-v2/admission.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
import {selectCoreExpectations} from '../../core-expectations.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const hash=b=>createHash('sha256').update(b).digest('hex');
export const RECIPE='869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173';
export function classify(metadata,label){
 assert(['normal-off','normal-runtime','gc-off'].includes(label));
 assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
 assert(metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false,'Diagnostic receipts forbidden before engine use');
 assert(!Object.hasOwn(metadata,'internalTickDiagnosticPolicy'),'Diagnostic policy forbidden before engine use');
 assert.equal(metadata.buildRecipeSha256,RECIPE,'Production recipe869 required before engine use');
 const options={gcStress:label==='gc-off',entropyPolicy:label==='normal-runtime'?'runtime-only':'off'};
 assert.equal(metadata.gcStress,options.gcStress);assert.equal(metadata.entropyPolicy,options.entropyPolicy);
 return options;
}
export async function admit(metadata,label,sourceRoot){
 const options=classify(metadata,label);
 const policyBytes=await readFile(join(here,'../integration-candidate-v1/policy.json'));
 assert.equal(hash(policyBytes),'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0');
 const policy=JSON.parse(policyBytes);
 assert.equal(hash(await readFile(join(here,'../integration-candidate-v1/layer-policy.py'))),'78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c');
 const external=[{path:'embedding/embedding.cpp',sha256:policy.embedding.afterSha256},{path:'embedding/embedding.h',sha256:'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},{path:'CMakeLists.txt',sha256:'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}];
 validateProductionMetadata(metadata,{...options,expectedSources:policy.expectedNativeSourceManifest,expectedExternal:external});
 const manifests=selectedManifestsForEngine(metadata,{sourceRoot});
 const core=selectCoreExpectations(metadata,{sourceRoot});assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
 return{state:'ACTUAL_FINITE_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION',label,options,sourceRoot,
  sourceFiles:306,externalSources:external,selectedManifestCount:manifests.length,coreExpectations:core,
  policySha256:hash(policyBytes),selectorSourceSha256:hash(await readFile(join(here,'../../module-selection.mjs'))),
  admissionSourceSha256:hash(await readFile(join(here,'../../private-ticks-admission.mjs'))),engineBytesRead:false,guestExecuted:false};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 assert.equal(process.argv.length,5);const metadata=JSON.parse(await readFile(process.argv[2]));
 console.log(JSON.stringify(await admit(metadata,process.argv[3],resolve(process.argv[4]))));
}
