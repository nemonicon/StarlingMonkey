// Future read-only data verification. No toolchain, provider or guest imports.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyConsumedSeal} from '../measurement-execution-activated-v2/consumed.mjs';
export const parentRoot=resolve(dirname(fileURLToPath(import.meta.url)),'../measurement-execution-activated-v2');
export const parentIndexSha256='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612';
export const pairSha256='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e';
const parentInputsSha256='e8912582589188583c218ceab5f6e94ad603ca16e78b1c094db64e4266fdb8dd';
export const failureRoot=resolve(parentRoot,'../production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json');
export const failureSha256='9037865a47939c8f2ff30976f5346ce5848113ea55c87c7c5753aed26e6a099f';
export const threeArmProofIndexSha256='bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef';
export const threeArmProofResultSha256='dbcc5fe7b6fe87595499c423119477567ab8fd794f38d04f3aeb203b88e95d19';
export const completedArms=Object.freeze(['native-on','canonical-on','canonical-off']);
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const SHA=/^[0-9a-f]{64}$/;
const within=(root,path)=>{const rel=relative(root,path);return rel!==''&&rel!=='..'&&!rel.startsWith('..'+sep)&&!isAbsolute(rel);};
export async function readPinned(path,digest,bytes){
 assert(typeof path==='string'&&isAbsolute(path)&&SHA.test(digest));
 const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink(),path);
 const raw=await readFile(path);assert.equal(hash(raw),digest,path);if(bytes!==undefined)assert.equal(raw.length,bytes,path);return raw;
}
export function exact(actual,expected,label){if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('Recorded data mismatch: '+label);}
export function validateAuthorityShape(authority){
 assert(authority&&authority.schemaVersion===1);
 assert.equal(authority.state,'ROOT_REVIEWED_COMMON_BYTE_THREE_ARMS_FOR_STOCK_ONLY_COMPOSITION_V1');
 assert.equal(authority.failedParentRootReceiptSha256,failureSha256);
 assert.equal(authority.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(authority.pairPinsSha256,pairSha256);
 assert.equal(authority.failedParentRawOuterExit,1);assert.equal(authority.wholeFailedParentPassed,false);
 exact(authority.arms,completedArms,'exact three completed arms');
 for(const key of ['independentProofIndexSha256','independentProofResultSha256'])assert(SHA.test(authority[key]??''));
 assert.equal(authority.independentProofIndexSha256,threeArmProofIndexSha256);
 assert.equal(authority.independentProofResultSha256,threeArmProofResultSha256);
 for(const key of ['independentProofIndexPath','independentProofResultPath'])assert(isAbsolute(authority[key]??''));
 assert.equal(authority.runtimeAcceptanceClaim,false);assert.equal(authority.timingAllowed,false);
 return authority;
}
export async function verifyCollector(here,indexSha256){
 const indexBytes=await readPinned(join(here,'index.json'),indexSha256),index=JSON.parse(indexBytes);
 assert.equal(index.schemaVersion,1);const frozen=index.files.find(row=>row.path==='input-freeze.json');assert(frozen);
 const raw=await readPinned(join(here,'input-freeze.json'),frozen.sha256,frozen.bytes);
 const seal=JSON.parse(raw);assert.equal(seal.schemaVersion,1);const seen=new Set();
 for(const row of index.files){assert(typeof row.path==='string'&&within(here,resolve(here,row.path)));await readPinned(resolve(here,row.path),row.sha256,row.bytes);}
 for(const row of seal.inputs){const path=resolve(here,row.path);assert(!seen.has(path),'duplicate input');seen.add(path);await readPinned(path,row.sha256,row.bytes);}
 return Object.freeze({inputManifestSha256:frozen.sha256,inputs:seen.size});
}
export async function verifyThreeArmAuthority(path,digest){
 // Check caller-supplied Root authority bytes before parsing any supplied path.
 const authority=validateAuthorityShape(JSON.parse(await readPinned(path,digest)));
 // The old pure source checker also preserves exact tool-tree membership/links.
 await verifyConsumedSeal(parentRoot,parentInputsSha256,null,{invocation:false});
 const failure=JSON.parse(await readPinned(failureRoot,failureSha256));
 assert.equal(failure.rawOuterExit,1);assert.equal(failure.wholeFourArmGatePassed,false);
 assert.equal(failure.stockFailure.stockComponentProduced,false);assert.equal(failure.postFailureSourceAudit.passed,true);
 await readPinned(authority.independentProofIndexPath,authority.independentProofIndexSha256);
 await readPinned(authority.independentProofResultPath,authority.independentProofResultSha256);
 const failureRows=new Map(failure.evidence.map(row=>[row.path,row]));assert.equal(failureRows.size,failure.evidence.length);
 // Rehash every original Root witness, including raw calls, components and glue.
 for(const row of failure.evidence)await readPinned(row.path,row.sha256,row.bytes);
 const common=JSON.parse(await readFile(join(parentRoot,'node-common-oracle.json'))),controls=JSON.parse(await readFile(join(parentRoot,'node-control-oracle.json')));
 const oracle=[...common.cases,...controls.cases];assert.equal(oracle.length,14);
 const records=[];
 for(const arm of completedArms){
  const expected=failure.completedArmRecords[arm],pinned=authority.completedArmRecords[arm];
  exact(pinned,expected,'Root-reviewed record '+arm);
  const record=JSON.parse(await readPinned(expected.record.path,expected.record.sha256,expected.record.bytes));
  validateArmRecord(record,arm,oracle);
  assert.equal(record.componentSha256,expected.componentSha256);assert.equal(record.componentBytes,expected.componentBytes);
  await verifyRecordFiles(record,failureRows);
  records.push({record,origin:{recordPath:expected.record.path,recordSha256:expected.record.sha256,recordBytes:expected.record.bytes,guestSourceFamilyIndexSha256:parentIndexSha256,originalParentRawOuterExit:1,wholeOriginalParentGatePassed:false}});
 }
 assert.equal(records[1].record.bundleSha256,records[2].record.bundleSha256);
 return Object.freeze({authorityPath:path,authoritySha256:digest,failure,records,oracle});
}
export function validateArmRecord(record,arm,oracle){
 assert.equal(record.arm,arm);for(const key of ['correctnessPassed','identityPassed','checkpointProbePassed'])assert.equal(record[key],true);
 exact(record.emittedImports,[],'imports');exact(record.interfaceAudit.emittedImports,[],'interface audit imports');
 assert.equal(record.graph.bundleSha256,record.bundleSha256);assert.equal(record.graph.arm,arm);
 assert.equal(record.correctness.retainedRotations,3);assert.equal(record.correctness.rounds.length,3);assert.equal(record.correctness.freshRows.length,14);assert.equal(record.correctness.wasmtime.length,16);
 assert.equal(oracle.length,14);
 for(let round=0;round<3;round++){assert.equal(record.correctness.rounds[round].length,14);for(let i=0;i<14;i++)exact(record.correctness.rounds[round][i],{calls:round*14+i+1,setup:oracle[i].setup,result:oracle[i].expected},arm+' retained '+round+'/'+i);}
 for(let i=0;i<14;i++)exact(record.correctness.freshRows[i],{calls:i+1,setup:oracle[i].setup,result:oracle[i].expected},arm+' fresh '+i);
 const identity={defaultGraph:true,promisesGraph:true,eventEmitterPrototype:true,selectedTickType:'function',decoderA:'A',bufferView:true,bufferSameAsBefore:arm!=='stock-on',globalSameAsProvider:true,beforeBufferType:'function',globalChangedDuringProvider:arm==='stock-on'};
 exact(record.identity,identity,arm+' identity');
 const probe=record.checkpointProbe;assert.equal(probe.callbacks,1);exact([...probe.trace].sort(),['microtask','selected-tick'],'probe');assert.equal(probe.queueDepthObserved,false);assert.equal(probe.terminalQueueEmptyObserved,false);
 for(let i=-2;i<14;i++){
  const row=record.correctness.wasmtime[i+2],expression=i===-2?'identity()':i===-1?'checkpoint-probe()':'inspect('+i+')';
  assert.equal(row.expression,expression);assert.equal(row.status,0);assert.equal(row.signal,null);
  exact(row.observed,i===-2?identity:i===-1?probe:{calls:1,setup:oracle[i].setup,result:oracle[i].expected},arm+' WT '+i);
 }
}
export async function verifyRecordFiles(record,witnessRows){
 const component=witnessRows.get(record.componentPath);assert(component);assert.equal(component.sha256,record.componentSha256);assert.equal(component.bytes,record.componentBytes);
 await readPinned(record.componentPath,record.componentSha256,record.componentBytes);await readPinned(record.enginePath,record.engineSha256);
 const directory=dirname(record.modulePath);
 for(const row of record.transpiledFiles){const path=resolve(directory,row.name);assert(within(directory,path));const witness=witnessRows.get(path);assert(witness);assert.equal(witness.sha256,row.sha256);await readPinned(path,row.sha256,row.bytes);}
 for(const row of record.graph.physicalSources)await readPinned(row.path,row.sha256,row.bytes);
 for(const row of record.correctness.wasmtime){const terminal=witnessRows.get(row.terminalPath);assert(terminal);const value=JSON.parse(await readPinned(terminal.path,terminal.sha256,terminal.bytes));assert.equal(value.terminalExitZeroObserved,true);assert.equal(value.ownedGroupGone,true);assert.equal(value.status,0);assert.equal(value.timedOut,false);}
}
