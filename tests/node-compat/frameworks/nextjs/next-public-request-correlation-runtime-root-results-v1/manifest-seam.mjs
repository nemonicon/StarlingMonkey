// Actual host metadata functions only; no browser, app, guest, guard or constructor.
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm,readdir,lstat,realpath} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {validatePublicCorrelation,writePublicCorrelationManifest} from '../next-public-request-correlation-runtime-v1/public-correlation.mjs';
import {validatePublicCorrelationManifest,readPublicCorrelationManifest} from '../next-public-request-correlation-browser-v1/manifest.mjs';
const rows=[],directory=await realpath(await mkdtemp(join(tmpdir(),'next-public-correlation-metadata-')));
const block={headerName:'x-next-public-request-correlation',nonceByTest:{'client-counter':'a'.repeat(64),'server-action':'b'.repeat(64)}};
const valid={schemaVersion:1,runId:'metadata-seam',origin:'http://127.0.0.1:49123',...block};
const clone=x=>JSON.parse(JSON.stringify(x));
async function test(id,body){try{await body();rows.push({id,passed:true});}catch(error){rows.push({id,passed:false,error:{name:error.name,message:error.message}});}}
try{
 await test('valid-pure-schemas',()=>{assert.equal(validatePublicCorrelation(block),true);const v=validatePublicCorrelationManifest(valid);assert(Object.isFrozen(v)&&Object.isFrozen(v.nonceByTest));});
 for(const [id,value] of [['short','a'.repeat(63)],['long','a'.repeat(65)],['LF','a'.repeat(64)+'\n'],['CRLF','a'.repeat(64)+'\r\n'],['uppercase','A'.repeat(64)],['nonhex','z'.repeat(64)]])await test('reject-'+id,()=>{const b=clone(block);b.nonceByTest['client-counter']=value;assert.throws(()=>validatePublicCorrelation(b));assert.throws(()=>validatePublicCorrelationManifest({...valid,...b}));});
 await test('reject-same-values',()=>{const b=clone(block);b.nonceByTest['server-action']=b.nonceByTest['client-counter'];assert.throws(()=>validatePublicCorrelation(b));assert.throws(()=>validatePublicCorrelationManifest({...valid,...b}));});
 await test('reject-final-LF-runId',async()=>{assert.throws(()=>validatePublicCorrelationManifest({...valid,runId:'metadata-seam\n'}));const before=await readdir(directory);await assert.rejects(writePublicCorrelationManifest({block,runId:'metadata-seam\n',origin:valid.origin,output:directory}));assert.deepEqual(await readdir(directory),before);});
 await test('reject-extra-schema-key',()=>assert.throws(()=>validatePublicCorrelationManifest({...valid,extra:true})));
 await test('exclusive-writer-and-bounded-reader',async()=>{const w=await writePublicCorrelationManifest({block,runId:valid.runId,origin:valid.origin,output:directory});const r=await readPublicCorrelationManifest(w.manifest.path);assert.deepEqual(r.manifest,valid);assert.deepEqual(r.source,w.manifest);assert.equal((await lstat(w.manifest.path)).mode&0o777,0o600);await assert.rejects(writePublicCorrelationManifest({block,runId:valid.runId,origin:valid.origin,output:directory}));});
 for(const [id,bytes] of [['oversize',Buffer.alloc(4097,32)],['empty',Buffer.alloc(0)],['invalid-utf8',Buffer.from([255])]])await test('reader-reject-'+id,async()=>{const path=join(directory,id+'.json');await writeFile(path,bytes,{flag:'wx',mode:0o600});await assert.rejects(readPublicCorrelationManifest(path));});
 await test('reader-reject-invalid-nonce-file',async()=>{const path=join(directory,'bad-nonce.json');const v=clone(valid);v.nonceByTest['server-action']+='\n';await writeFile(path,JSON.stringify(v),{flag:'wx',mode:0o600});await assert.rejects(readPublicCorrelationManifest(path));});
}finally{await rm(directory,{recursive:true,force:true});}
const sources=[];for(const relative of ['../next-public-request-correlation-runtime-v1/public-correlation.mjs','../next-public-request-correlation-browser-v1/manifest.mjs']){const path=fileURLToPath(new URL(relative,import.meta.url));const bytes=await readFile(path);sources.push({path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length});}
const passed=rows.every(x=>x.passed);console.log(JSON.stringify({schemaVersion:1,passed,cases:rows.length,rows,sources,actualHostMetadataFunctionsInvoked:true,temporaryOwnedFixturesRemoved:true,browserApplicationGuestGuardConstructorOrTargetInvoked:false,concurrentMutationSafetyProved:false},null,2));process.exitCode=passed?0:1;
