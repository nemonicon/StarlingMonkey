// Host-harness declarations only. No entropy, filesystem or request work at import.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {writeFile,lstat,realpath,readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';

export const HEADER='x-next-public-request-correlation';
const TESTS=['client-counter','server-action'];
function keys(value,want){
  assert(value!==null&&typeof value==='object'&&!Array.isArray(value));
  assert.deepEqual(Object.keys(value).sort(),[...want].sort());
}
export function validatePublicCorrelation(block){
  keys(block,['headerName','nonceByTest']);assert.equal(block.headerName,HEADER);
  keys(block.nonceByTest,TESTS);
  for(const id of TESTS)assert(typeof block.nonceByTest[id]==='string'&&block.nonceByTest[id].length===64&&/^[0-9a-f]{64}$/.test(block.nonceByTest[id]));
  assert.notEqual(block.nonceByTest['client-counter'],block.nonceByTest['server-action']);
  return true;
}
export async function writePublicCorrelationManifest({block,runId,origin,output}){
  validatePublicCorrelation(block);
  assert(typeof runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId)?.[0]===runId);
  const url=new URL(origin);assert.equal(url.origin,origin);assert.equal(url.protocol,'http:');
  assert.equal(url.hostname,'127.0.0.1');assert(url.port&&url.username===''&&url.password==='');
  assert.equal(resolve(output),output);
  const value={schemaVersion:1,runId,origin,headerName:HEADER,nonceByTest:{...block.nonceByTest}};
  const bytes=Buffer.from(JSON.stringify(value,null,2)+'\n');assert(bytes.length<=4096);
  const path=join(output,'public-request-correlation.json');
  await writeFile(path,bytes,{flag:'wx',mode:0o600});
  const before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1);
  assert.equal(await realpath(path),path);assert.equal(before.size,bytes.length);
  const actual=await readFile(path);assert.deepEqual(actual,bytes);
  const after=await lstat(path);
  for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(after[key],before[key]);
  return {manifest:{path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length},
    value,hostOnly:true,guestEnvironmentAdded:false,nonceGenerationAtInit:false};
}
