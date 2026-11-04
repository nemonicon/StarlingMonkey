// Internal untimed host decoder schedule. The future action must authenticate
// the reviewed Node executable, exact guest decodeNodeStream source, sourceBinding
// and all source/native/tool proofs BEFORE injecting these actual APIs.
// This module imports no Node-zlib/fflate/guest module and calls nothing at import.
import {need,fullBytes,equalBytes,hash} from './transport.mjs';
import {consumeFNV1a} from './fixtures.mjs';
export async function executeFreshNodeEdges({streams,decodeNodeStream,Buffer,nodeZlib,sourceBinding,rawFixtures,write,writeBytes,prefix}){
 need(typeof decodeNodeStream==='function'&&typeof write==='function'&&typeof writeBytes==='function','Actual authenticated Node decoder and durable JSON/binary retention required');
 need(Array.isArray(streams)&&[15,45].includes(streams.length)&&new Set(streams.map(row=>row.streamId)).size===streams.length,'Finite separate 45-main or15-off stream set');
 const rows=[];
 for(let index=0;index<streams.length;index++){
  const record=streams[index],raw=rawFixtures.get(record.fixture),name=prefix+'-'+String(index).padStart(2,'0');
  need(raw instanceof Uint8Array&&raw.length<=524288,'Trusted full expected fixture');
  const encoded=Buffer.from(record.encodedBase64,'base64');need(encoded.length>0&&encoded.length<=1048576&&encoded.toString('base64')===record.encodedBase64&&encoded.length===record.encodedBytes&&hash(encoded)===record.encodedSha256&&consumeFNV1a(encoded)===record.encodedFNV1aU32,'Whole actual compressed input cap/hash before decoder');
  await write(name+'-started.json',{schemaVersion:1,record,partial:true,freshDecodeRequired:true,earlierNodeOwnDecodeIsNotReused:true});
  // Genuine existing API in guest-v2/node-oracle.mjs; this source only arranges
  // new calls. Its retain callback records Node typed returns/errors BEFORE its
  // assertions; no previous decodedOwnStreams row supplies a fresh matrix edge.
  const retained=[];const retain=async(label,value)=>{need(/^[A-Za-z0-9._-]+$/.test(label),'Finite exact Node retention label');const binary=Buffer.isBuffer(value),path=name+'-'+label+(binary?'.bin':'.json');const row=await(binary?writeBytes(path,value):write(path,value));retained.push(row);return row;};
  const observed=await decodeNodeStream({Buffer,nodeZlib,record,expectedRaw:raw,sourceBinding,retain});
  const whole=await write(name+'-observed.json',{schemaVersion:1,observed,retained,partial:true});
  need(observed.streamId===record.streamId&&observed.provider===record.provider&&observed.decoder==='node-22.14.0'&&observed.fullRawEqual===true,'Actual fresh Node edge identity');
  const output=fullBytes(observed.output,524288);
  if(!equalBytes(output,raw)){await write(name+'-counterexample.json',{observed,expectedBase64:Buffer.from(raw).toString('base64')});throw new Error('ERR_COST_JCO_CORRECTNESS: Node full decoder bytes differ; complete evidence retained');}
  need(observed.sourceBytesConsumed===encoded.length&&observed.rawPayload.fullRawEqual===true&&observed.rawPayload.bytes===observed.rawPayload.sourceBytesConsumed,'Exact actual wrapper/payload consumption');
  const row={schemaVersion:1,streamId:record.streamId,provider:record.provider,fixture:record.fixture,format:record.format,decoder:'node-22.14.0',freshActualDecode:true,earlierNodeOwnDecodeReused:false,whole,retained,timing:false};await write(name+'-complete.json',row);rows.push(row);
 }return rows;
}
