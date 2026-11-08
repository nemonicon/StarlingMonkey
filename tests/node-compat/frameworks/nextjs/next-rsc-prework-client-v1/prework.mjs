// Fixed nonbrowser workload from the real full client; no code runs at import.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile,open,lstat,readdir,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {collectSupplemental,validateSupplemental} from '../wasmtime-deployment-candidate-v8/supplemental.mjs';
import {collectPortableCache,validatePortableCache} from '../next-portable-cache-http-collector-v1/collector.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const stamp=s=>[s.dev,s.ino,s.mode,s.nlink,s.size,s.mtimeMs,s.ctimeMs];
const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),code:e?.code??null});
async function fileRef(path,limit){
 const before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size<=limit);assert.equal(await realpath(path),path);
 const bytes=await readFile(path);assert.deepEqual(stamp(await lstat(path)),stamp(before));assert.equal(bytes.length,before.size);
 return {path,sha256:hash(bytes),bytes:bytes.length};
}
export async function runPrework({origin,output}){
 const root=output;
 const result={schemaVersion:1,suite:'NEXT_RSC_PREBROWSER_WORKLOAD_V1',executed:true,collectionComplete:false,passed:false,
  origin,node:process.version,http:[],errors:[],transportErrors:[],rawFiles:[],browserExecuted:false,publicManifestUsed:false,
  controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,
  fixedRequestGraphNotDeterministicSchedule:true,actualRuntimeExecutionClaimRequiresParentProof:true};
 assert.equal(process.version,'v22.14.0');
 await mkdir(join(root,'responses'),{mode:0o700});
 const save=()=>writeFile(join(root,'prework-progress.json'),JSON.stringify(result,null,2)+'\n');
 await save();
 try {
  result.portableCache=await collectPortableCache({origin:result.origin,output:join(root,'portable-cache')});
  await save(); // Whole five-request raw capture precedes semantic comparison.
  result.portableCacheValidation=validatePortableCache(result.portableCache);
  await save();
  result.supplemental=await collectSupplemental({origin:result.origin,output:join(root,'supplemental')});
  await save(); // Whole six-case raw capture precedes semantic comparison.
  result.supplementalValidation=validateSupplemental(result.supplemental);
  await save();
  const contract = JSON.parse(await readFile(join(here, '../fixture-contract.json')));
  const bodies = new Map();
  for (const item of contract.requests) {
    const response = await fetch(result.origin + item.path, {method: item.method ?? 'GET',
      headers: item.headers, body: item.body, redirect: 'manual', signal: AbortSignal.timeout(20000)});
    const body = await response.text();
    const failures = [];
    if (response.status !== item.status) failures.push('status ' + response.status + ' != ' + item.status);
    for (const text of item.includes ?? []) if (!body.includes(text)) failures.push('missing ' + JSON.stringify(text));
    if (item.location && response.headers.get('location') !== item.location) failures.push('location mismatch');
    if (item.json) try {
      const actual = JSON.parse(body);
      for (const [key, value] of Object.entries(item.json)) if (JSON.stringify(actual[key]) !== JSON.stringify(value)) failures.push('JSON ' + key + ' mismatch');
    } catch (error) { failures.push(error.message); }
    for (const [key, value] of Object.entries(item.responseHeaders ?? {})) if (response.headers.get(key) !== value) failures.push('header ' + key + ' mismatch');
    for (const [key, values] of Object.entries(item.responseHeaderIncludes ?? {})) for (const value of values) if (!response.headers.get(key)?.includes(value)) failures.push('header ' + key + ' missing ' + value);
    if (item.equalJsonTo && body !== bodies.get(item.equalJsonTo)) failures.push('body differs from ' + item.equalJsonTo);
    bodies.set(item.id, body);
    await writeFile(join(root, 'responses', item.id + '.txt'), body);
    result.http.push({id: item.id, status: response.status, headers: Object.fromEntries(response.headers),
      bodyBytes: Buffer.byteLength(body), bodySha256: hash(body), passed: !failures.length, failures});
    await save();
  }
  const names = [...bodies.get('server-action-form-ssr').matchAll(/name="(\$ACTION_ID_[^"]+)"/g)].map(m => m[1]);
  assert.equal(names.length, 1);
  const form = new FormData();
  form.set(names[0], ''); form.set('value', 'fixture-action');
  const action = await fetch(result.origin + '/actions', {method: 'POST', body: form,
    headers: {origin: result.origin}, redirect: 'manual', signal: AbortSignal.timeout(20000)});
  const actionBody = await action.text();
  await writeFile(join(root, 'responses/server-action-submit.txt'), actionBody);
  result.http.push({id: 'server-action-submit', status: action.status, headers: Object.fromEntries(action.headers),
    bodyBytes: Buffer.byteLength(actionBody), bodySha256: hash(actionBody),
    passed: action.status === 303 && action.headers.get('location') === '/action-result?value=fixture-action'});
  const before = JSON.parse(bodies.get('cache-first')), after = JSON.parse(bodies.get('cache-after-revalidate'));
  result.cacheInvalidation = {before, after, passed: after.generation > before.generation};
  const streamed = await fetch(result.origin + '/stream', {signal: AbortSignal.timeout(20000)});
  const chunks = []; let text = '', shell = -1, ready = -1;
  const decoder = new TextDecoder();
  for await (const chunk of streamed.body) {
    text += decoder.decode(chunk, {stream: true});
    if (shell < 0 && text.includes('NEXT_STREAM_SHELL')) shell = chunks.length;
    if (ready < 0 && text.includes('NEXT_STREAM_READY')) ready = chunks.length;
    chunks.push({base64: Buffer.from(chunk).toString('base64'), bytes: chunk.length});
  }
  text += decoder.decode();
  await writeFile(join(root, 'stream-chunks.json'), JSON.stringify(chunks, null, 2) + '\n');
  result.streaming = {chunks: chunks.length, shellChunk: shell, readyChunk: ready,
    complete: text.includes('NEXT_STREAM_SHELL') && text.includes('NEXT_STREAM_READY'),
    incrementalDeliveryObserved: ready > shell && shell >= 0};
 }catch(error){result.errors.push({stage:'prebrowser-workload',...errorData(error)});}
 // Collection is independent of the unchanged semantic predicates.
 const portable=result.portableCache?.records,supplemental=result.supplemental?.observations;
 let allHttpBodiesPublished=false,streamCapturePublished=false;
 try{
  if(result.http.length===24){
   for(const row of result.http){assert(/^[a-z0-9-]+$/.exec(row.id)?.[0]===row.id);assert.deepEqual(await fileRef(join(root,'responses',row.id+'.txt'),8388608),{path:join(root,'responses',row.id+'.txt'),sha256:row.bodySha256,bytes:row.bodyBytes});}
   allHttpBodiesPublished=true;
  }
  if(result.streaming){
   const stream=JSON.parse(await readFile(join(root,'stream-chunks.json'),'utf8'));
   assert(Array.isArray(stream)&&stream.length===result.streaming.chunks&&stream.length>0);
   for(const row of stream){const bytes=Buffer.from(row.base64,'base64');assert.equal(bytes.toString('base64'),row.base64);assert.equal(bytes.length,row.bytes);}
   streamCapturePublished=true;
  }
  const files=[];
  async function walk(directory){
   for(const name of(await readdir(directory)).sort()){
    const path=join(directory,name),s=await lstat(path);assert(!s.isSymbolicLink());
    if(s.isDirectory())await walk(path);else{assert(s.isFile()&&s.nlink===1&&s.size<=8388608);files.push({path,bytes:s.size});}
   }
  }
  for(const name of ['responses','portable-cache','supplemental'])await walk(join(root,name));
  for(const name of ['stream-chunks.json','prework-progress.json']){const path=join(root,name),s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1&&s.size<=8388608);files.push({path,bytes:s.size});}
  assert(files.length<=128&&files.reduce((n,r)=>n+r.bytes,0)<=33554432);
  for(const file of files)result.rawFiles.push(await fileRef(file.path,8388608));
 }catch(error){result.errors.push({stage:'prework-raw-publication',...errorData(error)});}
 const rawByPath=new Map(result.rawFiles.map(ref=>[ref.path,ref]));
 const validBody=ref=>ref&&typeof ref.path==='string'&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&typeof ref.sha256==='string'&&ref.sha256.length===64&&/^[a-f0-9]+$/.test(ref.sha256)&&JSON.stringify(rawByPath.get(ref.path))===JSON.stringify(ref);
 const allPortableCollected=Array.isArray(portable)&&portable.length===5&&portable.every(r=>r.complete===true&&r.overflow===false&&r.transportError===null&&Array.isArray(r.cleanupErrors)&&r.cleanupErrors.length===0&&Number.isSafeInteger(r.receivedBytes)&&r.receivedBytes===r.retainedBytes&&validBody(r.body)&&r.body.bytes===r.receivedBytes);
 const allSupplementalCollected=Array.isArray(supplemental)&&supplemental.length===6&&supplemental.every(r=>r.bodyEofObserved===true&&r.error===null&&r.readerReleaseError===null&&r.publicationError===null&&r.signalAborted===false&&validBody(r.body));
 result.collectionFrame={httpRecords:result.http.length,portableRecords:portable?.length??0,portableChecks:result.portableCacheValidation?.checks??0,
  supplementalRecords:supplemental?.length??0,supplementalChecks:result.supplementalValidation?.checks??0,streamChunks:result.streaming?.chunks??0,
  allHttpBodiesPublished,allPortableCollected,allSupplementalCollected,streamCapturePublished};
 result.collectionComplete=result.http.length===24&&allHttpBodiesPublished&&allPortableCollected&&allSupplementalCollected
  &&Number.isSafeInteger(result.portableCacheValidation?.checks)&&Number.isSafeInteger(result.supplementalValidation?.checks)&&streamCapturePublished
  &&result.cacheInvalidation!==null&&typeof result.cacheInvalidation==='object'&&result.errors.length===0&&result.transportErrors.length===0;
 result.original24GenerationAndStreamPassed=result.http.length===24&&result.http.every(x=>x.passed)&&result.cacheInvalidation?.passed===true
  &&result.streaming?.complete===true&&result.streaming?.incrementalDeliveryObserved===true&&result.errors.length===0&&result.transportErrors.length===0;
 result.passed=result.collectionComplete&&result.original24GenerationAndStreamPassed&&result.supplementalValidation?.passed===true&&result.portableCacheValidation?.passed===true;
 const path=join(root,'prework-result.json'),bytes=Buffer.from(JSON.stringify(result,null,2)+'\n');assert(bytes.length<=1048576);
 let handle,failed=false,primary;
 try{handle=await open(path,'wx',0o600);await handle.writeFile(bytes);await handle.sync();}catch(error){failed=true;primary=error;}
 finally{if(handle)try{await handle.close();}catch(error){if(!failed){failed=true;primary=error;}}}
 if(failed)throw primary;
 const ref=await fileRef(path,1048576);assert.equal(ref.bytes,bytes.length);assert.equal(ref.sha256,hash(bytes));
 return {executed:result.executed,collectionComplete:result.collectionComplete,passed:result.passed,result:ref,
  publication:{complete:true,fsynced:true,closed:true,fileBytes:bytes.length,sha256:ref.sha256,errors:[]}};
}
