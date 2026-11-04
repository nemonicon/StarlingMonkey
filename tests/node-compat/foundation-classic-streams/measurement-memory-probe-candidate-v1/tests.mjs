// Pure descriptor and source-data tests only. Never imports either action entry.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateDescriptor,validateAuthority,schedule,artifactRoot,packageFile,tuples,phaseSha,timingSha,timingRootSha,integritySha} from './contracts.mjs';
const here=dirname(fileURLToPath(import.meta.url));let passed=0;const check=(name,fn)=>{fn();passed++;};
const sha='1'.repeat(64),tuple=tuples['native-on'],root=artifactRoot('native-on');
const descriptor={schemaVersion:1,state:'PARENT_AUTHENTICATED_SMALL_MEMORY_WORKER_INPUT_V1',sourceIndexSha256:sha,parentPhaseSha256:phaseSha,arm:'native-on',comparison:'same-engine-binding',repetition:0,runOrder:['native-on','canonical-on'],position:0,
 component:{path:root+'/common-byte.component.wasm',sha256:tuple[0],bytes:tuple[1]},modulePath:root+'/common_byte.js',coreFiles:['common_byte.core.wasm'],criticalFiles:[
 {path:root+'/common-byte.component.wasm',sha256:tuple[0],bytes:tuple[1]},
 {path:root+'/common_byte.core.wasm',sha256:tuple[2],bytes:tuple[3]},
 {path:root+'/common_byte.js',sha256:'747296bc080f83a7a97657224a6aff71cfeaff124a47d4266c5c65124d99a53c',bytes:133860},
 {path:root+'/common_byte.d.ts',sha256:'e6e5d4c3d021092d6a6b662c6235f34987eca59672915aa18ab0e1618f3defe8',bytes:2209},packageFile('native-on')],
 expected:{identityRaw:'{}',probeRaw:'{}',cases:[1,5].map(index=>({index,iterations:1,setupReturn:'setup',batchRaw:JSON.stringify({result:{iterations:1,totalUnits:index===1?8192:4194304,records:[]}}),units:index===1?8192:4194304}))},
 nativeEvidence:{engineSha256:'12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274',metadataSha256:'f2f67947631136647259b7ba40422d6fb89fe943b1b74d2db4c5754bbfcc2c31',notLoadedByWorker:true}};
check('bounded descriptor accepted as data, not artifact proof',()=>assert.deepEqual(validateDescriptor(descriptor),descriptor));
for(const [name,change] of [
 ['old full measure entry',d=>{d.modulePath=root+'/measure.mjs';}],
 ['unknown artifact root',d=>{d.component.path='/tmp/unrelated/component.wasm';}],
 ['foreign core',d=>{d.coreFiles=['other.core.wasm'];}],
 ['engine path smuggled to worker',d=>{d.nativeEvidence.enginePath='/tmp/engine.wasm';}],
 ['full proof field smuggled to worker',d=>{d.compositionReport={records:[]};}],
 ['unhashed extra critical file',d=>{d.criticalFiles.push({path:'/tmp/proof.json',sha256:sha,bytes:1});}],
 ['critical hash mutation',d=>{d.criticalFiles[1].sha256=sha;}],
 ['oversized expected payload',d=>{d.expected.identityRaw=JSON.stringify({proof:'x'.repeat(16384)});}],
 ['non-JSON expected value',d=>{d.expected.probeRaw='not json';}],
 ['N16 forbidden',d=>{d.expected.cases[0].iterations=16;}],
 ['large then small forbidden',d=>{d.expected.cases.reverse();}],
 ['wrong units forbidden',d=>{d.expected.cases[0].units=1;}],
 ['unknown native tuple',d=>{d.nativeEvidence.engineSha256=sha;}],
 ['wrong metadata tuple',d=>{d.nativeEvidence.metadataSha256=sha;}],
 ['wrong order metadata',d=>{d.runOrder.reverse();}],
 ['extra repetition',d=>{d.repetition=3;}],
 ['unreviewed phase',d=>{d.parentPhaseSha256=sha;}]
])check(name,()=>{const d=structuredClone(descriptor);change(d);assert.throws(()=>validateDescriptor(d));});
const authority={schemaVersion:1,state:'ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V1',sourceIndexSha256:sha,memorySupplementAllowed:true,throughputReplacement:false,runtimeAcceptanceClaim:false,
 phase:{path:'/fixture/phase.json',sha256:phaseSha},timingReport:{path:'/fixture/report.json',sha256:timingSha},timingRootReceipt:{path:'/fixture/root.json',sha256:timingRootSha},integrityIndex:{path:'/fixture/index.json',sha256:integritySha}};
check('authority shape accepted, no file/artifact/action claim',()=>assert.deepEqual(validateAuthority(authority,sha),authority));
for(const [name,change] of [
 ['null authority',()=>null],['unknown source',v=>({...v,sourceIndexSha256:'2'.repeat(64)})],['unreviewed state',v=>({...v,state:'UNREVIEWED'})],['implicit old timing permission',v=>({...v,memorySupplementAllowed:false})],['old report mutation',v=>({...v,timingReport:{...v.timingReport,sha256:sha}})],['throughput replacement',v=>({...v,throughputReplacement:true})],['oversized authority path',v=>({...v,phase:{...v.phase,path:'/'+ 'x'.repeat(2048)}})]
])check(name,()=>assert.throws(()=>validateAuthority(change(structuredClone(authority)),sha)));
check('18 fresh workers, six observations per comparison AB/BA/AB',()=>{const s=schedule();assert.equal(s.length,18);for(const id of new Set(s.map(r=>r.comparison))){const rows=s.filter(r=>r.comparison===id);assert.equal(rows.length,6);assert.deepEqual(rows.map(r=>r.position),[0,1,0,1,0,1]);assert.deepEqual(rows[0].runOrder,rows[4].runOrder);assert.deepEqual(rows[0].runOrder,[...rows[2].runOrder].reverse());}});
const worker=await readFile(join(here,'worker.mjs'),'utf8'),parent=await readFile(join(here,'parent.mjs'),'utf8');
check('worker imports no full-proof audit/entry',()=>{for(const forbidden of ['auditComposedCorrectness','executionPreflight','verifyConsumedSeal','selectTimingPhase','measure-body.mjs','audit-inputs.mjs','input-freeze.json'])assert(!worker.includes(forbidden));});
check('worker authenticates self before dynamic helper or binding load',()=>{assert(worker.indexOf('const manifestRaw=')<worker.indexOf("await import('./contracts.mjs')"));assert(worker.indexOf('const raw=await small(descriptorPath')<worker.indexOf('await import(pathToFileURL(expectedPaths[2]))'));});
check('whole raw scalar persistence precedes equality',()=>assert(worker.indexOf("await persist('raw-'+label,observed)")<worker.indexOf('if(serialized!==expectedRaw)')));
check('public-only scope no private probe/forced GC',()=>{for(const forbidden of ['global.gc(','.exports.memory','getHeapStatistics','getHeapSnapshot','v8.writeHeapSnapshot','_malloc','WebAssembly.Memory','NODE_COMPAT_GC_STRESS'])assert(!worker.includes(forbidden));});
check('null authority checked before parent proof/code imports and output',()=>{const gate=parent.indexOf('validateAuthority(JSON.parse(authorityRaw),ownSha)');assert(gate<parent.indexOf("await import(pathToFileURL(join(timing,'admission.mjs')))"));assert(gate<parent.indexOf('await mkdir(output)'));});
check('old timing/corpus not imported as worker',()=>assert(!parent.includes("collectWorker(join(timing,'measure.mjs')")));
check('ancestor package boundary explicit, not a broad filesystem discovery',()=>{assert.equal(packageFile('native-on').path,'/tmp/starling-node-compat/production-common-byte-correctness-v2/package.json');assert.equal(packageFile('stock-on').path,'/tmp/starling-node-compat/production-common-byte-stock-only-v1/package.json');assert.equal(packageFile('native-on').bytes,18);});
const future=JSON.parse(await readFile(join(here,'future-root-authority.json')));
check('checked-in authority remains closed',()=>{assert.equal(future.memorySupplementAllowed,false);assert.equal(future.sourceIndexSha256,null);assert.throws(()=>validateAuthority(future,sha));});
console.log(JSON.stringify({schemaVersion:1,state:'PURE_MEMORY_DESCRIPTOR_AND_SOURCE_TESTS_PASSED',passed,actionEntriesImported:false,artifactOrGuestActionsExecuted:false}));
