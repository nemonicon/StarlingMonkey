// Independent real-Node reference. No candidate helper/provider, HTTP or server.
import assert from 'node:assert/strict';
import {createGzip} from 'node:zlib';
import {Readable, Transform} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {createWriteStream} from 'node:fs';
import {mkdir, lstat, readFile, writeFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {createHash} from 'node:crypto';
assert.equal(process.version, 'v22.14.0'); assert.equal(process.argv.length, 3);
const output = resolve(process.argv[2]);
try { await lstat(output); throw new Error('Reference output must be fresh'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
await mkdir(output, {mode: 0o700});
const descriptor = async path => { const b = await readFile(path); return {path, sha256:createHash('sha256').update(b).digest('hex'), bytes:b.length}; };
const result = {schemaVersion:1,suite:'INDEPENDENT_NODE_GZIP_COMPOSITION_REFERENCE_V1',node:process.version,
  candidateCodeLoaded:false,httpOrServerInvoked:false,cases:[],errors:[],rawCaptureOnly:true};
for (const id of ['small', 'large']) {
  // Independent implementation of the published byte fixture, not a guest import.
  let plain;
  if (id === 'small') plain = Buffer.from('NEXT_GZIP_COMPOSITION_SMALL_V1\nplain finite response\n');
  else {
    plain = Buffer.alloc(2097152); let n = 1831565813;
    for (let at = 0; at !== plain.length; at++) {
      n = (n ^ (n << 13)) >>> 0; n = (n ^ (n >>> 17)) >>> 0; n = (n ^ (n << 5)) >>> 0;
      plain[at] = n >>> 24;
    }
  }
  const plainPath=join(output,id+'.plain'), gzipPath=join(output,id+'.gzip');
  await writeFile(plainPath,plain,{flag:'wx',mode:0o600});
  const record={caseId:id,plain:await descriptor(plainPath),gzip:null,error:null,encodedBytes:0,events:[]};
  const gzip=createGzip({chunkSize:16384,readableHighWaterMark:65536,writableHighWaterMark:65536});
  for (const event of ['finish','end','close']) gzip.on(event,()=>record.events.push(event));
  try {
    const cap=new Transform({transform(chunk,encoding,callback){record.encodedBytes+=chunk.length;
      callback(record.encodedBytes>3145728?new RangeError('Reference gzip cap'):null,chunk);}});
    async function* chunks(){for(let n=0;n<plain.length;n+=32768)yield plain.subarray(n,n+32768);}
    await pipeline(Readable.from(chunks()),gzip,cap,createWriteStream(gzipPath,{flags:'wx',mode:0o600}));
  } catch(error) { record.error={name:error?.name??null,message:error?.message??String(error)};result.errors.push({caseId:id,...record.error}); }
  try {record.gzip=await descriptor(gzipPath);}catch(error){result.errors.push({caseId:id,stage:'gzip-readback',message:String(error)});}
  result.cases.push(record);
  await writeFile(join(output,id+'.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx',mode:0o600});
}
// Raw outputs and errors precede the independent DATA verifier; no comparison here.
await writeFile(join(output,'reference.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});
console.log(JSON.stringify({reference:await descriptor(join(output,'reference.json')),errors:result.errors,rawCaptureOnly:true}));
process.exitCode=result.errors.length?1:0;
