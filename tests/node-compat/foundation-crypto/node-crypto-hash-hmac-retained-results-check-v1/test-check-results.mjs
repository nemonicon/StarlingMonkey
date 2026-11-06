// Retained DATA and benign temporary text copies only. No workload/process API.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,cp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve,relative as relativePath} from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadRetainedInput,checkResults,compareRetainedRecords} from './check-results.mjs';
const dataset=resolve(process.argv[2]||new URL('../node-crypto-hash-hmac357-runtime-validation-v1/',import.meta.url).pathname);
const prepared=await loadRetainedInput(dataset),comparator=await import(pathToFileURL(prepared.modulePath).href),base=prepared.records;
const names=[];
function good(name,fn){const value=fn();assert(value);names.push(name);}
function bad(name,mutate){const r=structuredClone(base);mutate(r);assert.throws(()=>compareRetainedRecords(r,comparator,prepared.fixtureManifest),undefined,name);names.push(name);}
const positive=compareRetainedRecords(base,comparator,prepared.fixtureManifest);
good('actual14 records/280 positive/112 separate policy',()=>positive.guestReturnRecords===14&&positive.acceptedRecordComparisons===280&&positive.separateNativePolicyChecks===112);
good('actual raw native namespace difference remains separate',()=>positive.arms['raw-fixture'].calls.every(x=>x.namespaceObjectsSame===false)&&positive.arms['raw-fixture'].knownNativeNamespaceAliasDifferenceObserved&&positive.arms.bundled.calls.every(x=>x.namespaceObjectsSame===true)&&positive.providerIdentityProved===false);
bad('missing arm',r=>delete r.arms['raw-fixture']);
bad('missing retained call',r=>r.arms.bundled.jcoRetained.pop());
bad('missing WT call',r=>r.arms['raw-fixture'].wasmtimeDecoded.pop());
bad('wrong retained ordinal',r=>r.arms.bundled.jcoRetained.reverse());
bad('wrong WT typed return',r=>r.arms.bundled.wasmtimeDecoded[0].type='number');
bad('wrong WT decoded ordinal',r=>r.arms.bundled.wasmtimeDecoded[0].expectedCallOrdinal=2);
bad('clipped guest string',r=>r.arms.bundled.jcoFresh=r.arms.bundled.jcoFresh.slice(0,-1));
bad('changed accepted value',r=>{const v=JSON.parse(r.arms.bundled.jcoRetained[0]);v.nodeComparable[0].value.actual.outcome.observed.value='0'.repeat(64);r.arms.bundled.jcoRetained[0]=JSON.stringify(v);});
bad('changed native constant',r=>{const v=JSON.parse(r.arms.bundled.jcoFresh);v.providerAndConstants.opensslVersionNumber.value=0;r.arms.bundled.jcoFresh=JSON.stringify(v);});
bad('changed alias structure',r=>{const v=JSON.parse(r.arms['raw-fixture'].jcoFresh);v.aliases.unexpected=true;r.arms['raw-fixture'].jcoFresh=JSON.stringify(v);});
function nodeFrames(r,fn){const frames=r.nodeOracleText.trimEnd().split('\n').map(JSON.parse);fn(frames);r.nodeOracleText=frames.map(x=>JSON.stringify(x)).join('\n')+'\n';}
bad('Node observed type mismatch',r=>nodeFrames(r,rows=>rows[1].observed.type='number'));
bad('Node wrong sequence',r=>nodeFrames(r,rows=>rows[2].sequence=1));
bad('Node identity version mismatch',r=>nodeFrames(r,rows=>rows[0].version='v0.0.0'));
bad('Node extra JSONL frame',r=>r.nodeOracleText+='{}\n');
bad('Node guest provider claim refused',r=>nodeFrames(r,rows=>rows[0].guestProviderProof=true));
const temporary=await mkdtemp(join(tmpdir(),'hash-hmac-retained-data-test-'));
try{
 const relocated=join(temporary,'relocated');await cp(dataset,relocated,{recursive:true,errorOnExist:true});
 const replay=await checkResults(relocated);assert.deepEqual(replay,await checkResults(dataset));names.push('whole indexed dataset relocation without external original paths');
 await writeFile(join(relocated,'unexpected.txt'),'extra retained DATA\n');await assert.rejects(()=>checkResults(relocated),/membership/);names.push('extra unindexed file refused');await rm(join(relocated,'unexpected.txt'));
 const victim=join(relocated,'jco-bundled/retained/raw-1.json'),original=await readFile(victim);await writeFile(victim,Buffer.concat([original,Buffer.from(' ')]));await assert.rejects(()=>checkResults(relocated),/length|SHA256/);names.push('tampered indexed file refused');await writeFile(victim,original);
 await rm(victim);await assert.rejects(()=>checkResults(relocated));names.push('missing indexed file refused');
 const index=JSON.parse(await readFile(join(dataset,'index.json'),'utf8'));
 const row=name=>({...index.files.find(r=>r.path===name),path:join(dataset,name)});
 const manifest={schemaVersion:1,comparator:{module:row('inputs/comparator.mjs'),contract:row('inputs/contract.mjs')},fixtureManifest:row('inputs/fixture-manifest.json'),nodeOracleStdout:row('inputs/node-oracle.stdout.jsonl'),arms:['bundled','raw-fixture'].map(id=>{const tag=id==='bundled'?'bundled':'raw';return{id,jcoRetained:[1,2,3].map(n=>row('jco-'+tag+'/retained/raw-'+n+'.json')),jcoFresh:row('jco-'+tag+'/fresh/raw-1.json'),wasmtimeDecoded:[1,2,3].map(n=>row('wasmtime-'+tag+'/call-'+n+'-decoded.json'))};})};
 const manifestPath=join(temporary,'manifest.json');await writeFile(manifestPath,JSON.stringify(manifest));assert.equal((await checkResults(manifestPath)).guestReturnRecords,14);names.push('explicit absolute descriptor manifest');
 const relative=structuredClone(manifest);
 // An actual relative path can leave the manifest directory; descriptors still
 // authenticate only the explicitly chosen data. Avoid filesystem-root guesses.
 for(const row of [relative.comparator.module,relative.comparator.contract,relative.fixtureManifest,relative.nodeOracleStdout,...relative.arms.flatMap(a=>[...a.jcoRetained,a.jcoFresh,...a.wasmtimeDecoded])])row.path=relativePath(temporary,row.path);
 await writeFile(manifestPath,JSON.stringify(relative));assert.equal((await checkResults(manifestPath)).guestReturnRecords,14);names.push('explicit relative descriptor manifest');
 for(const [name,mutate]of [
  ['duplicate guest file role',m=>m.arms[0].jcoRetained[1]=m.arms[0].jcoRetained[0]],
  ['duplicate arm',m=>m.arms[1].id='bundled'],
  ['descriptor hash mismatch',m=>m.fixtureManifest.sha256='0'.repeat(64)],
  ['trusted comparator version mismatch',m=>m.comparator.module={...m.comparator.contract}],
  ['trusted contract relative dependency mismatch',m=>m.comparator.contract={...m.comparator.contract,path:resolve(dataset,'../node-crypto-hash-hmac-data-comparator-candidate-v1/contract.mjs')}]
 ]){const changed=structuredClone(manifest);mutate(changed);await writeFile(manifestPath,JSON.stringify(changed));await assert.rejects(()=>checkResults(manifestPath),undefined,name);names.push(name);}
}finally{await rm(temporary,{recursive:true,force:true});}
await prepared.recheck();
console.log(JSON.stringify({schemaVersion:1,state:'RETAINED_RECORD_CHECKER_DATA_TESTS_PASSED',checks:names.length,names,allWorkloadExecutions:false,guestOrOracleOrProcessInvoked:false}));
