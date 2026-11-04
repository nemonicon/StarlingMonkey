// Host-only: run the exact private file verifier on owned scratch data.
// The complete component driver, adapter, producer and freezer are never run.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,rm,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),old=join(here,'../diagnostic-link1-consumers-v1');
const hash=value=>createHash('sha256').update(value).digest('hex');
assert(process.env.NODE_COMPAT_LINK1_ADAPTER_TEST_OUTPUT,'Choose a fresh host-only report');
const output=resolve(process.env.NODE_COMPAT_LINK1_ADAPTER_TEST_OUTPUT);
try{await lstat(output);assert.fail('Output already exists');}catch(error){if(error.code!=='ENOENT')throw error;}
const source=await readFile(join(here,'run-components.UNEXECUTED.mjs'),'utf8');
const start=source.indexOf('async function verifyFrozenInputs(){'),end=source.indexOf('\nawait verifyFrozenInputs();',start);
assert(start>=0&&end>start);
const verifierSource=source.slice(start,end),countSource=source.match(/^assert\.equal\(frozenInputs\.length,32[^\n]+$/m)[0];
const results=[];
function test(name,fn){fn();results.push({name,passed:true});}
async function asyncTest(name,fn){await fn();results.push({name,passed:true});}
function verifier(directory,manifestBytes,rows,calls=[]){
 const context=vm.createContext({assert,hash,join,resolve,here:directory,frozenInputs:rows,frozenInputSha256:hash(manifestBytes),
  readFile:async path=>{calls.push(path);return readFile(path);}});
 return new vm.Script(verifierSource+'\nverifyFrozenInputs;',{filename:'extracted-driver-file-verifier.js'}).runInContext(context);
}
const fixedFiles=['preflight.mjs','link-evidence.mjs','freeze-diagnostic-engine.py','consumer-pins.json','build-one-diagnostic.py','diagnostic.cmake','test-extension.cpp'];
await asyncTest('native consumer acceptance and build inputs byte-identical',async()=>{for(const name of fixedFiles)assert((await readFile(join(here,name))).equals(await readFile(join(old,name))),name);});
const oldSource=await readFile(join(old,'run-components.UNEXECUTED.mjs'),'utf8');
const corpus=value=>value.split('const ordinaryWorld=',2)[1].split('const sourceNames=',1)[0];
test('entire packaging invocation and semantic corpus unchanged',()=>assert.equal(corpus(source),corpus(oldSource)));
test('actual source count assertion refuses31',()=>assert.throws(()=>new vm.Script(countSource).runInNewContext({assert,frozenInputs:Array(31)})));
const actualManifest=await readFile(join(here,'input-freeze.json')),actualRows=JSON.parse(actualManifest).inputs;
test('actual driver source count accepts32',()=>new vm.Script(countSource).runInNewContext({assert,frozenInputs:actualRows}));
await asyncTest('actual32 source files verified without loading driver',async()=>{assert.equal(actualRows.length,32);await verifier(here,actualManifest,actualRows)();});
const scratch=await mkdtemp(join(tmpdir(),'starling-link1-driver-adapter-'));
try{
 const rows=[];
 for(let i=0;i<32;i++){
  const name=i===31?'owned-adapter.wasm':'source-'+i+'.txt',data=Buffer.from('owned-data-'+i);
  await writeFile(join(scratch,name),data);rows.push({path:name,sha256:hash(data),bytes:data.length});
 }
 const manifest=Buffer.from(JSON.stringify({inputs:rows}));await writeFile(join(scratch,'input-freeze.json'),manifest);
 const calls=[],check=verifier(scratch,manifest,rows,calls),adapter=join(scratch,'owned-adapter.wasm');
 await asyncTest('owned32 source seal succeeds',()=>check());
 await rm(adapter);
 await asyncTest('missing owned adapter refuses with real file error',()=>assert.rejects(check(),{code:'ENOENT'}));
 await writeFile(adapter,'tampered-adapter');
 await asyncTest('tampered owned adapter refuses digest mismatch',()=>assert.rejects(check(),/Frozen diagnostic source changed: owned-adapter.wasm/));
 const replacement=rows.map(row=>({...row}));replacement[31].sha256=hash(Buffer.from('tampered-adapter'));
 await writeFile(join(scratch,'input-freeze.json'),JSON.stringify({inputs:replacement}));calls.length=0;
 await asyncTest('replacement manifest plus adapter refuses before rows',async()=>{await assert.rejects(check(),/Input freeze changed/);assert.deepEqual(calls,[join(scratch,'input-freeze.json')]);});
 await writeFile(join(scratch,'input-freeze.json'),'INVALID JSON');calls.length=0;
 await asyncTest('changed manifest refuses before any row read',async()=>{await assert.rejects(check(),/Input freeze changed/);assert.deepEqual(calls,[join(scratch,'input-freeze.json')]);});
}finally{await rm(scratch,{recursive:true});}
const report={schemaVersion:1,state:'HOST_ONLY_DRIVER32_ADAPTER_SEAL_PASSED',tests:results.length,passed:results.length,results,
 extractedVerifierSha256:hash(verifierSource),driverSha256:hash(source),sourceInputs:32,
 nativeConsumerFilesByteIdentical:fixedFiles,fullOriginalCorpusByteIdentical:true,
 nativeMetadataOrFreezeAcceptanceExecuted:false,wholeDriverImportedOrRun:false,
 producerFreezerLauncherOrAdapterExecuted:false,toolchainComponentGuestOrHostExecuted:false,
 scratchScope:'Owned32 tiny datafiles only; no valid Wasm module or real engine is executed'};
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
