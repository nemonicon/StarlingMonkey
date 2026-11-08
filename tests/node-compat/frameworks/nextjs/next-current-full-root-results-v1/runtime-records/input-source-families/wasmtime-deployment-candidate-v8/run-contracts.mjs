// Reuses unchanged real24 HTTP/action/cache/strict-stream assertions.
// Standalone client only; server is the separately owned actual Wasmtime process.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {once} from 'node:events';
import {spawn} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {collectSupplemental,validateSupplemental} from './supplemental.mjs';
const here=dirname(fileURLToPath(import.meta.url)),origin=new URL(process.argv[2]),root=resolve(process.argv[3]),browserTools=process.argv[4];
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,6);const runId=process.argv[5];assert(/^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId)?.[0]===runId);assert.equal(origin.origin,process.argv[2]);assert.equal(origin.hostname,'127.0.0.1');assert.equal(origin.protocol,'http:');assert(browserTools);assert.equal(root,'/private/tmp/starling-node-compat/next-wasmtime-deployment-'+runId+'/client');
await mkdir(root,{mode:0o700});await mkdir(join(root,'responses'));
const hash=b=>createHash('sha256').update(b).digest('hex');
const result={schemaVersion:1,suite:'ACTUAL_NEXT_WASMTIME_FULL_CONTRACT_CLIENT_V2',origin:origin.origin,node:process.version,http:[],errors:[],transportErrors:[],actualComponentExecutionClaimRequiresParentProof:true};
const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),stack:e?.stack??null});
const save=()=>writeFile(join(root,'result.json'),JSON.stringify(result,null,2)+'\n');await save();
try {
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
  if (browserTools) {
    const args = [join(here, '../browser-hydration-candidate-v3/browser-check.mjs'), '--origin', result.origin,
      '--tools', browserTools, '--output', join(root, 'browser')];
    result.browserArgv = [process.execPath, ...args];
    const child = spawn(process.execPath, args, {stdio: ['ignore', 'inherit', 'inherit']});
    const [code, signal] = await once(child, 'exit');
    result.browserExit = {code, signal};
    result.browser = JSON.parse(await readFile(join(root, 'browser/result.json')));
  }
} catch(error){result.errors.push(errorData(error));}
finally {
 result.passed=result.http.length===24&&result.http.every(x=>x.passed)&&result.cacheInvalidation?.passed===true&&result.streaming?.complete===true&&result.streaming?.incrementalDeliveryObserved===true&&result.browserExit?.code===0&&result.browser?.passed===true&&result.errors.length===0&&result.transportErrors.length===0;
 result.originalContractPassed=result.passed;
 result.passed=result.originalContractPassed&&result.supplementalValidation?.passed===true;
 await save();
}
console.log(JSON.stringify({state:result.passed?'ACTUAL_NEXT_WASMTIME_CONTRACT_CLIENT_PASSED_V2':'ACTUAL_NEXT_WASMTIME_CONTRACT_CLIENT_FAILED_V2',http:result.http.length,passedHttp:result.http.filter(x=>x.passed).length,errors:result.errors}));process.exitCode=result.passed?0:1;
