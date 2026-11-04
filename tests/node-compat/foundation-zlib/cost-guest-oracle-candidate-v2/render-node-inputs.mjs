// Data-only renderer. Toolchain owns Root action/source publication approval.
import {createHash} from 'node:crypto';
import {cases,requireValue,stageRecord,unbase64,bytesEqual,MAX_RAW} from './contract.mjs';
import {fixtureSpecs,fixtureBytes} from './fixtures.mjs';
const sha=raw=>createHash('sha256').update(raw).digest('hex');
export function renderNodeInputs(raw,expectedOracleSha256){
 requireValue(raw instanceof Uint8Array&&raw.length<=32*1024*1024,'bounded exact oracle bytes');requireValue(typeof expectedOracleSha256==='string'&&/^[0-9a-f]{64}$/.test(expectedOracleSha256),'explicit oracle digest');
 requireValue(sha(raw)===expectedOracleSha256,'oracle digest BEFORE JSON parse/rows');const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
 requireValue(value.schemaVersion===1&&value.state==='NODE_22_CODEC_COST_ORACLE_CAPTURED_UNREVIEWED_V1'&&value.node==='v22.14.0','actual future Node oracle schema');
 requireValue(value.nodeExecutableSha256==='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','pinned Node');
 requireValue(value.sourceBinding?.proposalIndexSha256==='e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8'&&value.sourceBinding?.protocolDecisionSha256==='0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','exact parent/source protocol binding');
 requireValue(Array.isArray(value.rawFixtures)&&value.rawFixtures.length===5&&Array.isArray(value.encodedStreams)&&value.encodedStreams.length===15&&Array.isArray(value.cases)&&value.cases.length===30&&Array.isArray(value.decodedOwnStreams)&&value.decodedOwnStreams.length===15&&Array.isArray(value.repeatedEncoderOutputs)&&value.repeatedEncoderOutputs.length===15,'complete oracle finite matrix');
 for(let i=0;i<fixtureSpecs.length;i++){const spec=fixtureSpecs[i],row=value.rawFixtures[i],bytes=unbase64(row.base64,MAX_RAW),expected=fixtureBytes(spec);requireValue(row.id===spec.id&&row.bytes===bytes.length&&sha(bytes)===row.sha256&&bytesEqual(bytes,expected),'whole deterministic raw fixture');}
 const expected=cases.filter(row=>row.direction==='decode');
 for(let i=0;i<expected.length;i++){
  const stream=value.encodedStreams[i],checked=stageRecord(stream),decoded=value.decodedOwnStreams[i],repeat=value.repeatedEncoderOutputs[i],rawFixture=fixtureBytes(fixtureSpecs.find(row=>row.id===stream.fixture));
  requireValue(stream.caseId===expected[i].index&&stream.provider==='node-22.14.0'&&sha(checked.bytes)===stream.encodedSha256,'all exact Node streams');
  requireValue(decoded.streamId===stream.streamId&&decoded.fullRawEqual===true&&decoded.sourceBytesConsumed===stream.encodedBytes&&decoded.rawPayload?.fullRawEqual===true&&decoded.rawPayload.sourceBytesConsumed===decoded.rawPayload.bytes,'recorded full wrapper/raw payload consumption proofs');
  const rawDecoded=unbase64(decoded.output.base64,MAX_RAW);requireValue(decoded.output.bytes===rawFixture.length&&sha(rawDecoded)===decoded.output.sha256&&bytesEqual(rawDecoded,rawFixture),'recorded whole decoded fixture');
  requireValue(repeat.streamId===stream.streamId&&repeat.fullByteEqual===true&&repeat.first.base64===stream.encodedBase64&&repeat.second.base64===stream.encodedBase64,'recorded actual Node determinism');
 }
 for(let i=0;i<cases.length;i++)requireValue(value.cases[i].caseId===i&&value.cases[i].caseName===cases[i].id&&value.cases[i].fixture===cases[i].fixture&&value.cases[i].format===cases[i].format,'all30 case associations');
 const inputs={schemaVersion:1,kind:'codec-cost-node-inputs-v1',oracleSha256:expectedOracleSha256,records:value.encodedStreams};
 return{moduleSource:'// Exact future Node input data; capture is UNREVIEWED until separate Root proof. No codec executes here.\nexport const oracleInputs='+JSON.stringify(inputs)+';\n',oracleSha256:expectedOracleSha256,nodeInputRecords:15,renderInvokesCodec:false,requiresSeparateRootReview:true};
}
