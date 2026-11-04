// Ordinary fixed/attached/unshared Node-host cases only. No guest or fault test.
import assert from 'node:assert/strict';
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import * as consumers from 'node:stream/consumers';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { streamChecks } from '../../foundation-stream/valid-api-checks.mjs';
assert.equal(process.version,'v22.14.0');
const toolchain=resolve(process.env.NODE_COMPAT_TOOLCHAIN??'/tmp/starling-node-compat/native-toolchain-lock');
const require=createRequire(join(toolchain,'package.json'));
const core=require(join(toolchain,'node_modules/readable-stream/lib/stream.js'));
const cases=await streamChecks(stream,promises,consumers,Buffer);
function typedWrite(module) {
  const backing=new Uint8Array([0,65,66,0]); let seen;
  const sink=new module.Writable({write(chunk,encoding,callback) {
    seen={bytes:[...chunk],shared:chunk.buffer===backing.buffer,offset:chunk.byteOffset}; callback();
  }});
  sink.on('error',()=>{});
  let failure; try {sink.write(new DataView(backing.buffer,1,2));} catch(error) {failure={name:error.name,code:error.code};}
  sink.destroy(); return {seen:seen??null,failure:failure??null};
}
function aggregate(module) {
  const source=new module.Readable({read(){}});
  source.push(new Uint8Array([0,1,2]).subarray(1)); source.push(new Uint8Array([3,4])); source.push(null);
  const first=source.read(3),rest=source.read(); source.destroy();
  return {first:[...first],rest:[...rest],firstIsBuffer:Buffer.isBuffer(first),restIsBuffer:Buffer.isBuffer(rest)};
}
function encoding(module) {
  const source=new module.Readable({read(){}}); source.setEncoding('utf8');
  source.push(Buffer.from([0xE2,0x82])); source.push(Buffer.from([0xAC])); source.push(null);
  const result=source.read(); source.destroy(); return result;
}
const supplemental={
  defaults:{node:[stream.getDefaultHighWaterMark(false),stream.getDefaultHighWaterMark(true)],readable:[core.getDefaultHighWaterMark(false),core.getDefaultHighWaterMark(true)]},
  typedViewWrite:{node:typedWrite(stream),readable:typedWrite(core)},
  multiChunkRead:{node:aggregate(stream),readable:aggregate(core)},
  splitUtf8:{node:encoding(stream),readable:encoding(core)},
  constructorAliases:Object.fromEntries([['readable','Readable'],['writable','Writable'],['duplex','Duplex'],['transform','Transform'],['passthrough','PassThrough']].map(([id,name])=>[id,require('node:_stream_'+id)===stream[name]])),
  newOrCall:Object.fromEntries(['Readable','Writable','Duplex','Transform','PassThrough'].map(name=>[name,stream[name]({read(){},write(c,e,cb){cb();},transform(c,e,cb){cb(null,c);}}) instanceof stream[name]])),
};
assert.deepEqual(supplemental.defaults.node,[65536,16]); assert.deepEqual(supplemental.defaults.readable,[16384,16]);
assert.equal(supplemental.typedViewWrite.node.failure,null); assert.equal(supplemental.typedViewWrite.readable.failure.code,'ERR_INVALID_ARG_TYPE');
assert.deepEqual(supplemental.multiChunkRead.node,supplemental.multiChunkRead.readable);
assert.equal(supplemental.splitUtf8.node,'€'); assert.equal(supplemental.splitUtf8.readable,'€');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const report={schemaVersion:1,node:process.version,nodeExecutableSha256:hash(await readFile(process.execPath)),
  oracleCases:cases,supplemental,
  sources:await Promise.all([new URL(import.meta.url),new URL('../../foundation-stream/valid-api-checks.mjs',import.meta.url)].map(async url=>({path:url.pathname,sha256:hash(await readFile(url))}))),
  scope:'Pinned Node host only, including portable readable-stream running with Node host dependencies. No native guest adapter/module, component, runtime scheduler, snapshot, throughput or memory proof.'};
await writeFile(new URL('node-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({nodeGroups:cases.length,supplementalGroups:Object.keys(supplemental).length,typedView:supplemental.typedViewWrite,defaults:supplemental.defaults}));
