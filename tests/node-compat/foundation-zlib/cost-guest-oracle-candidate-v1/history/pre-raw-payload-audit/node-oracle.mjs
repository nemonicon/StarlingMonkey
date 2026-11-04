// Future untimed host function only. No codec module is imported here.
// Toolchain owns Root action/preflight admission BEFORE API injection/call.
import {createHash} from 'node:crypto';
import {readFile,realpath} from 'node:fs/promises';
import {fixtureSpecs,fixtureBytes,consumeFNV1a} from './fixtures.mjs';
import {cases,MAX_INPUT,MAX_OUTPUT,MAX_RAW,requireValue,base64,bytesEqual,stageRecord} from './contract.mjs';
import {framing} from './framing.mjs';
const NODE_SHA='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0';
const PROPOSAL_SHA='e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8';
const DECISION_SHA='0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6';
const sha=raw=>createHash('sha256').update(raw).digest('hex');
const encoders={zlib:'deflateSync',gzip:'gzipSync',raw:'deflateRawSync'},decoders={zlib:'inflateSync',gzip:'gunzipSync',raw:'inflateRawSync'};
function binding(value){
 requireValue(value&&value.proposalIndexSha256===PROPOSAL_SHA&&value.protocolDecisionSha256===DECISION_SHA&&value.nodeExecutableSha256===NODE_SHA,'exact source/Node binding');
 for(const key of['guestSourceIndexSha256','costToolingIndexSha256','rootActionAuthoritySha256'])requireValue(typeof value[key]==='string'&&/^[0-9a-f]{64}$/.test(value[key]),'future explicit '+key);
 return{...value};
}
async function selectedNode(){requireValue(process.version==='v22.14.0','pinned Node22.14');requireValue(sha(await readFile(await realpath(process.execPath)))===NODE_SHA,'actual Node executable hash');}
function methods(api){for(const name of[...Object.values(encoders),...Object.values(decoders)])requireValue(typeof api[name]==='function','actual injected Node sync method');return api;}
function capture(bytes){return{bytes:bytes.length,sha256:sha(bytes),fnv1aU32:consumeFNV1a(bytes),base64:base64(bytes)};}
export async function createNodeOracle({Buffer,nodeZlib,sourceBinding,retain}){
 const sources=binding(sourceBinding);requireValue(typeof retain==='function','durable raw retention callback');await selectedNode();const api=methods(nodeZlib);
 const rawFixtures=[],encodedStreams=[],repeatedEncoderOutputs=[],decodedOwnStreams=[];
 for(const spec of fixtureSpecs){
  const raw=fixtureBytes(spec);requireValue(raw.length<=MAX_RAW,'trusted raw corpus');const fixture={id:spec.id,...capture(raw)};await retain('raw-'+spec.id,raw);rawFixtures.push(fixture);
  for(const format of['zlib','gzip','raw']){
   const input=Buffer.from(raw.buffer,raw.byteOffset,raw.length),before=new Uint8Array(input),encode=encoders[format];
   // No options: this external Node oracle is not a guest performance arm.
   const first=api[encode](input);await retain('node-'+spec.id+'-'+format+'-first',first);
   requireValue(Buffer.isBuffer(first)&&first.length>0&&first.length<=MAX_INPUT,'actual encoded input cap BEFORE decoder');requireValue(bytesEqual(input,before),'Node encoder input immutability');
   const second=api[encode](input);await retain('node-'+spec.id+'-'+format+'-repeat',second);
   requireValue(second.length<=MAX_INPUT&&bytesEqual(first,second)&&bytesEqual(input,before),'actual Node encoding determinism/input immutability');
   const frame=framing(format,first,raw),decodeCase=cases.find(row=>row.fixture===spec.id&&row.format===format&&row.direction==='decode');
   const stream={schemaVersion:1,kind:'codec-cost-stage-v1',caseId:decodeCase.index,fixture:spec.id,format,provider:'node-22.14.0',streamId:'node-22.14.0.'+spec.id+'.'+format,encodedBytes:first.length,encodedFNV1aU32:consumeFNV1a(first),encodedSha256:sha(first),encodedBase64:base64(first)};
   stageRecord(stream);encodedStreams.push(stream);repeatedEncoderOutputs.push({streamId:stream.streamId,first:capture(first),second:capture(second),fullByteEqual:true,framing:frame});
   // info:true is an EXTERNAL untimed consumption audit, never a native option.
   const decoded=api[decoders[format]](first,{info:true,maxOutputLength:MAX_OUTPUT});await retain('node-'+spec.id+'-'+format+'-decoded',decoded.buffer);
   requireValue(Buffer.isBuffer(decoded.buffer)&&decoded.buffer.length<=MAX_OUTPUT&&decoded.buffer.length<=MAX_RAW&&bytesEqual(decoded.buffer,raw),'whole Node decoded raw bytes');
   requireValue(decoded.engine&&decoded.engine.bytesWritten===first.length,'whole encoded source consumed');
   decodedOwnStreams.push({streamId:stream.streamId,...capture(decoded.buffer),sourceBytesConsumed:decoded.engine.bytesWritten,fullRawEqual:true});
  }
 }
 requireValue(encodedStreams.length===15&&decodedOwnStreams.length===15,'complete Node fixture/format matrix');
 return{schemaVersion:1,state:'NODE_22_CODEC_COST_ORACLE_CAPTURED_UNREVIEWED_V1',sourceBinding:sources,node:'v22.14.0',nodeExecutableSha256:NODE_SHA,rawFixtures,encodedStreams,repeatedEncoderOutputs,decodedOwnStreams,cases:cases.map(row=>({caseId:row.index,caseName:row.id,fixture:row.fixture,format:row.format,direction:row.direction,logicalUncompressedBytes:row.logicalUncompressedBytesPerOperation,rawFixtureSha256:rawFixtures.find(value=>value.id===row.fixture).sha256,providerSpecificGuestEncodingExpected:null})),providerLevel45EncoderOr135CrossDecodeProof:false,ffOffProof:false,guestOrTimingExecuted:false,requiresIndependentReview:true};
}
export async function decodeNodeStream({Buffer,nodeZlib,record,expectedRaw,sourceBinding,retain}){
 binding(sourceBinding);requireValue(typeof retain==='function','durable raw retention callback');await selectedNode();const checked=stageRecord(record),raw=expectedRaw;
 requireValue(raw instanceof Uint8Array&&raw.length<=MAX_RAW,'trusted expected raw');requireValue(sha(checked.bytes)===record.encodedSha256,'full source SHA before Node decode');
 await retain('cross-input-'+record.streamId,checked.bytes);
 const input=Buffer.from(checked.bytes.buffer,checked.bytes.byteOffset,checked.bytes.length),actual=methods(nodeZlib)[decoders[record.format]](input,{info:true,maxOutputLength:MAX_OUTPUT});
 await retain('cross-output-'+record.streamId,actual.buffer);
 requireValue(actual.buffer.length<=MAX_OUTPUT&&actual.buffer.length<=MAX_RAW&&bytesEqual(actual.buffer,raw),'whole Node cross-decoded bytes');requireValue(actual.engine.bytesWritten===input.length,'whole cross-input consumed');
 return{streamId:record.streamId,provider:record.provider,decoder:'node-22.14.0',input:capture(input),output:capture(actual.buffer),fullRawEqual:true,framing:framing(record.format,input,raw),sourceBytesConsumed:actual.engine.bytesWritten};
}
