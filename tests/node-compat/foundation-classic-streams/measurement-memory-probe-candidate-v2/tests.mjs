// Pure descriptor and source-data tests only. Never imports either action entry.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateDescriptor,validateAuthority,buildDescriptor,buildExpectedCases,requirePublicReturn,requireS32,schedule,packageFile,phaseSha,timingSha,timingRootSha,integritySha} from './contracts.mjs';
import {compactExpected} from '../measurement-execution-activated-v2/compact-oracle.mjs';
const here=dirname(fileURLToPath(import.meta.url));let passed=0;const check=(name,fn)=>{fn();passed++;};
const sha='1'.repeat(64),hash=raw=>createHash('sha256').update(raw).digest('hex'),base=dirname(here),old=join(base,'measurement-execution-activated-v2');
async function pinned(path,digest){const raw=await readFile(path);assert.equal(hash(raw),digest);return raw;}
const oldIndex=JSON.parse(await pinned(join(old,'index.json'),'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'));
const oracles=[];for(const name of ['node-common-oracle.json','node-control-oracle.json']){const row=oldIndex.files.find(r=>r.path===name);assert(row);oracles.push(...JSON.parse(await pinned(join(old,name),row.sha256)).cases);}
const phase=JSON.parse(await pinned(join(base,'production-adoption-v1/reviewed-composed-timing-phase-v1.json'),phaseSha));
const wit=(await pinned('/tmp/starling-node-compat/production-common-byte-correctness-v2/native-on/emitted.wit','53336fc899248b72ca00055a55af04acbdd06e9f03270173b67e9a633407b77d')).toString();
const declarations=(await pinned('/tmp/starling-node-compat/production-common-byte-correctness-v2/native-on/common_byte.d.ts','e6e5d4c3d021092d6a6b662c6235f34987eca59672915aa18ab0e1618f3defe8')).toString();
check('actual signed32 ABI from pinned emittedWIT and declarations',()=>{assert(wit.includes('export setup: func(index: u32) -> s32;'));assert(declarations.includes('setup(index: number): number'));for(const name of ['batch','identity','checkpoint-probe'])assert(wit.split('\n').some(line=>line.includes('export '+name+':')&&line.includes('-> string;')));});
const expectedCases=buildExpectedCases(oracles,compactExpected);check('genuine two Node setup values retained as numbers',()=>assert.deepEqual(expectedCases.map(r=>r.setupReturn),[151852933,-1502831163]));
const descriptors=schedule().map(row=>{const record=phase.components[row.arm];return buildDescriptor({sourceIndexSha256:sha,row,record,expectedCases,native:{engineSha256:record.engineSha256,metadataSha256:record.engineMetadataSha256}});});
check('actual parent builder validates all18 genuine phase/oracle descriptors',()=>{assert.equal(descriptors.length,18);for(const d of descriptors){assert.deepEqual(validateDescriptor(d),d);assert.deepEqual(d.expected.cases.map(r=>r.setupReturn),[151852933,-1502831163]);}});
const descriptor=descriptors[0],root=dirname(descriptor.modulePath);
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
for(const [name,value] of [['string','151852933'],['NaN',NaN],['fraction',1.25],['high',2147483648],['low',-2147483649],['infinity',Infinity],['null',null]]){
 check('typed setup '+name+' refused by descriptor and shared public guard',()=>{const d=structuredClone(descriptor);d.expected.cases[0].setupReturn=value;assert.throws(()=>validateDescriptor(d));assert.throws(()=>requirePublicReturn('setup',value,151852933));});
}
check('signed32 limits accepted without string coercion',()=>{assert.equal(requireS32(-2147483648),-2147483648);assert.equal(requireS32(2147483647),2147483647);});
check('shared typed return guard accepts both genuine setup returns',()=>{for(const row of expectedCases)requirePublicReturn('setup',row.setupReturn,row.setupReturn);});
check('incorrect integer setup result rejected strictly',()=>assert.throws(()=>requirePublicReturn('setup',151852934,151852933)));
check('incorrect numeric expected result rejected in actual descriptor construction',()=>{const bad=structuredClone(expectedCases);bad[0].setupReturn++;const row=schedule()[0],record=phase.components[row.arm];assert.throws(()=>buildDescriptor({sourceIndexSha256:sha,row,record,expectedCases:bad,native:{engineSha256:record.engineSha256,metadataSha256:record.engineMetadataSha256}}));});
check('number expected cannot be string-coerced',()=>assert.throws(()=>requirePublicReturn('setup',151852933,'151852933')));
check('five other public returns remain JSON strings',()=>{for(const d of descriptors){requirePublicReturn('identity',d.expected.identityRaw,d.expected.identityRaw);requirePublicReturn('checkpointProbe',d.expected.probeRaw,d.expected.probeRaw);for(const row of d.expected.cases){requirePublicReturn('batch',row.batchRaw,row.batchRaw);assert.throws(()=>requirePublicReturn('batch',JSON.parse(row.batchRaw),row.batchRaw));}}});
check('actual construction fails on string oracle setup before output',()=>{const bad=structuredClone(oracles);bad[1].setup=String(bad[1].setup);assert.throws(()=>buildExpectedCases(bad,compactExpected));});
const authority={schemaVersion:1,state:'ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V2',sourceIndexSha256:sha,memorySupplementAllowed:true,throughputReplacement:false,runtimeAcceptanceClaim:false,
 phase:{path:'/fixture/phase.json',sha256:phaseSha},timingReport:{path:'/fixture/report.json',sha256:timingSha},timingRootReceipt:{path:'/fixture/root.json',sha256:timingRootSha},integrityIndex:{path:'/fixture/index.json',sha256:integritySha}};
check('authority shape accepted, no file/artifact/action claim',()=>assert.deepEqual(validateAuthority(authority,sha),authority));
check('old v1 Root permission cannot activate v2',()=>assert.throws(()=>validateAuthority({...authority,state:'ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V1'},sha)));
for(const [name,change] of [
 ['null authority',()=>null],['unknown source',v=>({...v,sourceIndexSha256:'2'.repeat(64)})],['unreviewed state',v=>({...v,state:'UNREVIEWED'})],['implicit old timing permission',v=>({...v,memorySupplementAllowed:false})],['old report mutation',v=>({...v,timingReport:{...v.timingReport,sha256:sha}})],['throughput replacement',v=>({...v,throughputReplacement:true})],['oversized authority path',v=>({...v,phase:{...v.phase,path:'/'+ 'x'.repeat(2048)}})]
])check(name,()=>assert.throws(()=>validateAuthority(change(structuredClone(authority)),sha)));
check('18 fresh workers, six observations per comparison AB/BA/AB',()=>{const s=schedule();assert.equal(s.length,18);for(const id of new Set(s.map(r=>r.comparison))){const rows=s.filter(r=>r.comparison===id);assert.equal(rows.length,6);assert.deepEqual(rows.map(r=>r.position),[0,1,0,1,0,1]);assert.deepEqual(rows[0].runOrder,rows[4].runOrder);assert.deepEqual(rows[0].runOrder,[...rows[2].runOrder].reverse());}});
const worker=await readFile(join(here,'worker.mjs'),'utf8'),parent=await readFile(join(here,'parent.mjs'),'utf8');
check('worker imports no full-proof audit/entry',()=>{for(const forbidden of ['auditComposedCorrectness','executionPreflight','verifyConsumedSeal','selectTimingPhase','measure-body.mjs','audit-inputs.mjs','input-freeze.json'])assert(!worker.includes(forbidden));});
check('worker authenticates self before dynamic helper or binding load',()=>{assert(worker.indexOf('const manifestRaw=')<worker.indexOf("await import('./contracts.mjs')"));assert(worker.indexOf('const raw=await small(descriptorPath')<worker.indexOf('await import(pathToFileURL(expectedPaths[2]))'));});
check('whole typed raw scalar persistence precedes shared guard',()=>{assert(worker.includes('rawReturn:actual,rawReturnType:typeof actual'));assert(worker.indexOf("await persist('raw-'+label,observed)")<worker.indexOf('requirePublicReturn(name,actual,expectedRaw)'));});
check('public-only scope no private probe/forced GC',()=>{for(const forbidden of ['global.gc(','.exports.memory','getHeapStatistics','getHeapSnapshot','v8.writeHeapSnapshot','_malloc','WebAssembly.Memory','NODE_COMPAT_GC_STRESS'])assert(!worker.includes(forbidden));});
check('null authority checked before parent proof/code imports and output',()=>{const gate=parent.indexOf('validateAuthority(JSON.parse(authorityRaw),ownSha)');assert(gate<parent.indexOf("await import(pathToFileURL(join(timing,'admission.mjs')))"));assert(gate<parent.indexOf('await mkdir(output)'));});
check('old timing/corpus not imported as worker',()=>assert(!parent.includes("collectWorker(join(timing,'measure.mjs')")));
check('ancestor package boundary explicit, not a broad filesystem discovery',()=>{assert.equal(packageFile('native-on').path,'/tmp/starling-node-compat/production-common-byte-correctness-v2/package.json');assert.equal(packageFile('stock-on').path,'/tmp/starling-node-compat/production-common-byte-stock-only-v1/package.json');assert.equal(packageFile('native-on').bytes,18);});
const future=JSON.parse(await readFile(join(here,'future-root-authority.json')));
check('checked-in authority remains closed',()=>{assert.equal(future.memorySupplementAllowed,false);assert.equal(future.sourceIndexSha256,null);assert.throws(()=>validateAuthority(future,sha));});
console.log(JSON.stringify({schemaVersion:1,state:'PURE_MEMORY_DESCRIPTOR_AND_SOURCE_TESTS_PASSED',passed,actionEntriesImported:false,artifactOrGuestActionsExecuted:false}));
