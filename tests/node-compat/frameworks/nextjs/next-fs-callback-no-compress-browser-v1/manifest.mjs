// Host-only manifest DATA. Imports allocate no guest/host resource or workload.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {lstat,open,realpath} from 'node:fs/promises';
import {resolve} from 'node:path';

export const publicCorrelationHeader='x-next-public-request-correlation';
export const publicCorrelationTests=Object.freeze(['client-counter','server-action']);
export const publicCorrelationManifestLimit=4096;
const stamp=s=>[s.dev,s.ino,s.mode,s.nlink,s.size,s.mtimeMs,s.ctimeMs];
const evidence=s=>({dev:s.dev,ino:s.ino,mode:s.mode,nlink:s.nlink,size:s.size,mtimeMs:s.mtimeMs,ctimeMs:s.ctimeMs});

export function validatePublicCorrelationManifest(value){
  assert(value&&typeof value==='object'&&!Array.isArray(value));
  assert.deepEqual(Object.keys(value).sort(),['headerName','nonceByTest','origin','runId','schemaVersion']);
  assert.equal(value.schemaVersion,1);
  assert(typeof value.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(value.runId)?.[0]===value.runId);
  assert.equal(typeof value.origin,'string');
  const origin=new URL(value.origin);
  assert.equal(origin.origin,value.origin);assert.equal(origin.protocol,'http:');
  assert.equal(origin.hostname,'127.0.0.1');assert(origin.port&&Number(origin.port)>0);
  assert.equal(origin.username,'');assert.equal(origin.password,'');
  assert.equal(value.headerName,publicCorrelationHeader);
  const nonces=value.nonceByTest;
  assert(nonces&&typeof nonces==='object'&&!Array.isArray(nonces));
  assert.deepEqual(Object.keys(nonces).sort(),[...publicCorrelationTests].sort());
  for(const test of publicCorrelationTests)assert(typeof nonces[test]==='string'&&nonces[test].length===64&&/^[a-f0-9]{64}$/.test(nonces[test]));
  assert.notEqual(nonces['client-counter'],nonces['server-action']);
  return Object.freeze({...value,nonceByTest:Object.freeze({...nonces})});
}

export async function readPublicCorrelationManifest(path){
  assert.equal(typeof path,'string');assert.equal(resolve(path),path);
  const before=await lstat(path);
  assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1);
  assert(before.size>0&&before.size<=publicCorrelationManifestLimit);
  assert.equal(await realpath(path),path);
  let handle,primarySet=false;
  try{
    handle=await open(path,'r');
    const opened=await handle.stat();assert.deepEqual(stamp(opened),stamp(before));
    assert(opened.isFile()&&opened.nlink===1&&opened.size>0&&opened.size<=publicCorrelationManifestLimit);
    // Fixed allocation/read ceiling, even if a concurrent writer enlarges input.
    const buffer=Buffer.alloc(publicCorrelationManifestLimit+1);let total=0;
    while(total<buffer.length){
      const result=await handle.read(buffer,total,buffer.length-total,total);
      assert(Number.isInteger(result.bytesRead)&&result.bytesRead>=0&&result.bytesRead<=buffer.length-total);
      if(result.bytesRead===0)break;total+=result.bytesRead;
    }
    assert(total>0&&total<=publicCorrelationManifestLimit);assert.equal(total,opened.size);
    const after=await handle.stat(),pathAfter=await lstat(path);
    assert.deepEqual(stamp(after),stamp(opened));assert.deepEqual(stamp(pathAfter),stamp(opened));
    assert.equal(await realpath(path),path);
    const bytes=buffer.subarray(0,total);
    const manifest=validatePublicCorrelationManifest(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes)));
    return {manifest,bytes,source:{path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:total},
      evidence:{limitBytes:publicCorrelationManifestLimit,initial:evidence(before),final:evidence(pathAfter),
        timestampUnits:'Node stat milliseconds; atime excluded',canonicalRegularNlinkOne:true,readBookendsStable:true}};
  }catch(error){primarySet=true;throw error;}
  finally{if(handle)try{await handle.close();}catch(error){if(!primarySet)throw error;}}
}
