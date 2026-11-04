// Read-only source/data admission. No native verifier, provider or action imports.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
export const parentRoot=resolve(dirname(fileURLToPath(import.meta.url)),'../measurement-execution-activated-v2');
export const parentIndexSha256='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612';
export const collectorRoot=resolve(parentRoot,'../measurement-stock-composition-candidate-v1');
export const collectorIndexSha256='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da';
export const pairSha256='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e';
export const failureSha256='9037865a47939c8f2ff30976f5346ce5848113ea55c87c7c5753aed26e6a099f';
const arms=['native-on','canonical-on','canonical-off','stock-on'];
const SHA=/^[0-9a-f]{64}$/;
export const hash=raw=>createHash('sha256').update(raw).digest('hex');
const exact=(actual,expected,label)=>{if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('Composition admission mismatch: '+label);};
function descriptor(row){assert(row&&isAbsolute(row.path??'')&&SHA.test(row.sha256??''));assert(Number.isSafeInteger(row.bytes)&&row.bytes>=0);}
async function pinned(path,digest,bytes){assert(isAbsolute(path)&&SHA.test(digest));const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink(),path);const raw=await readFile(path);assert.equal(hash(raw),digest,path);if(bytes!==undefined)assert.equal(raw.length,bytes,path);return raw;}
async function readDescriptor(row){descriptor(row);return pinned(row.path,row.sha256,row.bytes);}
async function indexed(root,digest){const index=JSON.parse(await pinned(join(root,'index.json'),digest));assert.equal(index.schemaVersion,1);const seen=new Set();for(const row of index.files){const path=resolve(root,row.path),name=relative(root,path);assert(name!==''&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name)&&!seen.has(name));seen.add(name);await pinned(path,row.sha256,row.bytes);}return index;}

export async function verifyTimingSources(here,ownSha){
 assert(SHA.test(ownSha));await indexed(here,ownSha);
 await indexed(parentRoot,parentIndexSha256);await indexed(collectorRoot,collectorIndexSha256);
 // All executable helpers are indexed. Native/tool closure remains the original
 // genuine executionPreflight in the parent main and bounded post-operation audit.
 return {sourceFamilyIndexSha256:parentIndexSha256,timingAdmissionSourceIndexSha256:ownSha,collectorSourceIndexSha256:collectorIndexSha256};
}

export function validateComposedShape(report,review,phase,ownSha){
 assert(SHA.test(ownSha));assert.equal(phase.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(phase.timingAdmissionSourceIndexSha256,ownSha);assert.equal(phase.pairPinsSha256,pairSha256);
 assert.equal(report.schemaVersion,1);assert.equal(report.state,'COMPOSED_COMMON_BYTE_FOUR_ARM_CORRECTNESS_EVIDENCE');assert.equal(report.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(report.pairPinsSha256,pairSha256);
 assert.equal(report.records.length,4);exact(report.records.map(row=>row.record.arm),arms,'four ordered origin arms');
 exact(report.failedParent,{receiptPath:join(parentRoot,'../production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json'),receiptSha256:failureSha256,rawOuterExit:1,sourceFamilyIndexSha256:parentIndexSha256,wholeParentGatePassed:false},'original failed parent stays failed');
 for(const key of ['timingAllowed','runtimeAcceptanceClaim','performanceClaim','queueEmptyProof','rootIsolationProof','cppStateMachineClaim','unaffectedThreeArmsRerun','controlsSubtracted'])assert.equal(report[key],false,key);
 assert.equal(report.original28CounterexamplesPreserved,true);assert.equal(report.commonCases,8);assert.equal(report.controlCases,6);
 assert.equal(review.state,'ROOT_REVIEWED_COMMON_BYTE_PREREQUISITE_V1');assert.equal(review.prerequisite,'actualCorrectness');assert.equal(review.reviewedPassed,true);assert.equal(review.performanceClaim,false);assert.equal(review.reportSha256,phase.actualCorrectness.reportSha256);assert.equal(review.pairPinsSha256,pairSha256);assert.equal(review.sourceContractVersion,'sm-classic-trace-source-v1');
 assert.equal(review.evidenceKind,report.state);assert.equal(review.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(review.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(review.timingAdmissionSourceIndexSha256,ownSha);
 exact(review.origins,report.records.map(row=>({arm:row.record.arm,...row.origin})),'explicit Root origin review');
 assert.equal(review.compositionProof.rawOuterExit,0);for(const name of ['terminal','completion','stdout','stderr','independentProofIndex','independentProofResult','stockIndependentProofIndex','stockIndependentProofResult'])descriptor(review.compositionProof[name]);
 for(let i=0;i<4;i++){
  const row=report.records[i],origin=row.origin;assert.equal(origin.guestSourceFamilyIndexSha256,parentIndexSha256);assert(isAbsolute(origin.recordPath)&&SHA.test(origin.recordSha256));
  if(i<3){assert.equal(origin.originalParentRawOuterExit,1);assert.equal(origin.wholeOriginalParentGatePassed,false);assert(Number.isSafeInteger(origin.recordBytes)&&origin.recordBytes>0);assert.equal(origin.collectorSourceIndexSha256,undefined);}
  else{assert.equal(origin.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(origin.rawOuterExit,0);exact(origin.stockRootReceipt,report.newStockRootReceipt,'stock Root receipt origin');}
  for(const name of ['correctnessPassed','identityPassed','checkpointProbePassed'])assert.equal(row.record[name],true);
  exact(row.record.emittedImports,[],'zero imports');exact(row.record.interfaceAudit.emittedImports,[],'interface imports');
 }
 return report;
}

export function componentTuple(record){return Object.fromEntries(['arm','componentPath','componentSha256','componentBytes','enginePath','engineSha256','engineMetadataSha256','modulePath','bundleSha256','transpiledFiles','coreFiles'].map(key=>[key,record[key]]));}
export function validateCompositionProof(value,report,reportSha){
 assert.equal(value.schemaVersion,1);assert.equal(value.state,'INDEPENDENT_COMPOSED_COMMON_BYTE_CORRECTNESS_VERIFIED_V1');assert.equal(value.compositionReportSha256,reportSha);assert.equal(value.guestSourceFamilyIndexSha256,parentIndexSha256);assert.equal(value.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(value.pairPinsSha256,pairSha256);assert.equal(value.rawCompositionOuterExit,0);assert.equal(value.verifiedPassed,true);assert.equal(value.timingAllowed,false);assert.equal(value.performanceClaim,false);
 exact(value.origins,report.records.map(row=>({arm:row.record.arm,...row.origin})),'independent composition origins');exact(value.componentTuples,report.records.map(row=>componentTuple(row.record)),'independent four component tuples');
}
export function validateStockProof(value,report){
 const row=report.records[3];assert.equal(row.record.arm,'stock-on');assert.equal(value.schemaVersion,1);assert.equal(value.state,'INDEPENDENT_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_VERIFIED_V1');assert.equal(value.stockReportSha256,row.origin.recordSha256);assert.equal(value.stockRootReceiptSha256,report.newStockRootReceipt.sha256);assert.equal(value.guestSourceFamilyIndexSha256,parentIndexSha256);assert.equal(value.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(value.pairPinsSha256,pairSha256);assert.equal(value.rawStockOuterExit,0);assert.equal(value.verifiedPassed,true);assert.equal(value.timingAllowed,false);assert.equal(value.performanceClaim,false);exact(value.componentTuple,componentTuple(row.record),'independent stock tuple');
}
export function validateProofIndexResult(index,indexPath,resultRow){
 assert.equal(index.schemaVersion,1);assert(Array.isArray(index.files));descriptor(resultRow);const rows=index.files.filter(row=>resolve(dirname(indexPath),row.path)===resultRow.path);assert.equal(rows.length,1,'Proof result must be indexed exactly once');assert.equal(rows[0].sha256,resultRow.sha256);assert.equal(rows[0].bytes,resultRow.bytes);
}
async function proofResult(indexRow,resultRow){
 descriptor(indexRow);descriptor(resultRow);assert.equal(indexRow.path,join(dirname(indexRow.path),'index.json'));
 const index=await indexed(dirname(indexRow.path),indexRow.sha256);assert.equal((await readDescriptor(indexRow)).length,indexRow.bytes);
 validateProofIndexResult(index,indexRow.path,resultRow);return JSON.parse(await readDescriptor(resultRow));
}

export async function auditComposedCorrectness(phase,ownSha){
 const report=JSON.parse(await pinned(phase.actualCorrectness.reportPath,phase.actualCorrectness.reportSha256));
 const review=JSON.parse(await pinned(phase.actualCorrectness.rootReviewPath,phase.actualCorrectness.rootReviewSha256));
 validateComposedShape(report,review,phase,ownSha);
 const proof=review.compositionProof;
 for(const name of ['stdout','stderr'])await readDescriptor(proof[name]);
 validateCompositionProof(await proofResult(proof.independentProofIndex,proof.independentProofResult),report,phase.actualCorrectness.reportSha256);
 validateStockProof(await proofResult(proof.stockIndependentProofIndex,proof.stockIndependentProofResult),report);
 const completion=JSON.parse(await readDescriptor(proof.completion));assert.equal(completion.state,'COMPOSITION_REPORT_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED');assert.equal(completion.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(completion.requiresIndependentRawOuterExitZero,true);assert.equal(completion.oldParentRawExit,1);assert.equal(completion.timingAllowed,false);assert.equal(completion.runtimeAcceptanceClaim,false);exact(completion.result,{path:phase.actualCorrectness.reportPath,sha256:phase.actualCorrectness.reportSha256,bytes:(await pinned(phase.actualCorrectness.reportPath,phase.actualCorrectness.reportSha256)).length},'composition completion result');
 const terminal=JSON.parse(await readDescriptor(proof.terminal));assert.equal(terminal.returncode,0);
 const selectedNode='/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node';assert.equal(await realpath(terminal.command[0]),await realpath(selectedNode));await pinned(terminal.command[0],'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
 exact(terminal.command.slice(1),[join(collectorRoot,'compose.mjs'),collectorIndexSha256,report.threeArmAuthority.path,report.threeArmAuthority.sha256,report.newStockRootReceipt.path,report.newStockRootReceipt.sha256,dirname(phase.actualCorrectness.reportPath)],'composition launcher command');
 const failure=JSON.parse(await pinned(report.failedParent.receiptPath,failureSha256));assert.equal(failure.rawOuterExit,1);assert.equal(failure.wholeFourArmGatePassed,false);
 const three=JSON.parse(await pinned(report.threeArmAuthority.path,report.threeArmAuthority.sha256));assert.equal(three.state,'ROOT_REVIEWED_COMMON_BYTE_THREE_ARMS_FOR_STOCK_ONLY_COMPOSITION_V1');assert.equal(three.failedParentRootReceiptSha256,failureSha256);assert.equal(three.failedParentRawOuterExit,1);assert.equal(three.wholeFailedParentPassed,false);assert.equal(three.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(three.pairPinsSha256,pairSha256);assert.equal(three.timingAllowed,false);
 const stockRoot=JSON.parse(await pinned(report.newStockRootReceipt.path,report.newStockRootReceipt.sha256));assert.equal(stockRoot.state,'ROOT_STOCK_ONLY_COMMON_BYTE_CORRECTNESS_TERMINAL_ZERO_V1');assert.equal(stockRoot.rawOuterExit,0);assert.equal(stockRoot.collectorSourceIndexSha256,collectorIndexSha256);assert.equal(stockRoot.guestSourceFamilyIndexSha256,parentIndexSha256);assert.equal(stockRoot.pairPinsSha256,pairSha256);assert.equal(stockRoot.timingAllowed,false);assert.equal(stockRoot.runtimeAcceptanceClaim,false);
 assert.equal(stockRoot.result.path,report.records[3].origin.recordPath);assert.equal(stockRoot.result.sha256,report.records[3].origin.recordSha256);await readDescriptor(stockRoot.result);
 for(const row of report.records){const origin=row.origin,raw=await pinned(origin.recordPath,origin.recordSha256,origin.recordBytes),value=JSON.parse(raw);if(row.record.arm==='stock-on'){assert.equal(value.state,'ACTUAL_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_PASSED');assert.equal(value.records.length,1);exact(value.records[0],row.record,'stock origin record');}else{exact(value,row.record,'original origin record');const original=failure.completedArmRecords[row.record.arm];assert.equal(original.record.path,origin.recordPath);assert.equal(original.record.sha256,origin.recordSha256);assert.equal(original.record.bytes,origin.recordBytes);}}
 // Hashes are primitives captured by the phase; repeat source/data audits before
 // each old timing boundary and in the bounded post-operation audit.
 await pinned(phase.actualCorrectness.reportPath,phase.actualCorrectness.reportSha256);await pinned(phase.actualCorrectness.rootReviewPath,phase.actualCorrectness.rootReviewSha256);
 return report;
}
