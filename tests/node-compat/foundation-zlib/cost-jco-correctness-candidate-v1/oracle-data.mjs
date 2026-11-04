// Data authentication/byte checks only. This does NOT decode a codec stream.
import {need,hash,fullBytes,equalBytes} from './transport.mjs';
import {fixtureSpecs,fixtureBytes,consumeFNV1a} from './fixtures.mjs';
function freeze(value){if(value&&typeof value==='object'){for(const child of Object.values(value))freeze(child);Object.freeze(value);}return value;}
export function parseOracleBytes(bytes,expectedSha,cases){
 need(bytes instanceof Uint8Array&&bytes.length<=32*1024*1024&&/^[0-9a-f]{64}$/.test(expectedSha)&&hash(bytes)===expectedSha,'Exact caller-pinned oracle bytes BEFORE parse');
 const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
 need(value.schemaVersion===1&&value.state==='NODE_22_CODEC_COST_ORACLE_CAPTURED_UNREVIEWED_V1'&&value.node==='v22.14.0'&&value.nodeExecutableSha256==='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','Actual bounded original Node capture; independent review required separately');
 need(value.providerLevel45EncoderOr135CrossDecodeProof===false&&value.ffOffProof===false&&value.guestOrTimingExecuted===false,'Never transfer15 Node-own streams into fullmatrix/FF-OFF claims');
 need(Array.isArray(cases)&&cases.length===30&&Array.isArray(value.cases)&&value.cases.length===30,'Complete30 case association source');
 for(let index=0;index<30;index++){const actual=value.cases[index],row=cases[index];need(row.index===index&&actual.caseId===index&&actual.caseName===row.id&&actual.fixture===row.fixture&&actual.format===row.format&&actual.direction===row.direction&&actual.logicalUncompressedBytes===row.logicalUncompressedBytesPerOperation,'Exact original case association');}
 need(Array.isArray(value.rawFixtures)&&value.rawFixtures.length===5&&new Set(value.rawFixtures.map(row=>row.id)).size===5,'Five complete raw fixtures');
 const rawFixtures=new Map();for(const spec of fixtureSpecs){const row=value.rawFixtures.find(v=>v.id===spec.id);need(row,'Every named trusted fixture');const raw=fullBytes(row,524288),pure=fixtureBytes(spec);need(equalBytes(raw,pure)&&hash(raw)===row.sha256&&consumeFNV1a(raw)===row.fnv1aU32,'Full actual raw bytes match pure deterministic fixture');rawFixtures.set(spec.id,new Uint8Array(raw));}
 need(Array.isArray(value.encodedStreams)&&value.encodedStreams.length===15&&new Set(value.encodedStreams.map(row=>row.streamId)).size===15,'Complete15 unique Node encoder streams');
 const names=new Set();for(const row of cases.filter(row=>row.direction==='decode')){const stream=value.encodedStreams.find(v=>v.caseId===row.index);need(stream?.schemaVersion===1&&stream.kind==='codec-cost-stage-v1'&&stream.provider==='node-22.14.0'&&stream.fixture===row.fixture&&stream.format===row.format&&stream.streamId==='node-22.14.0.'+row.fixture+'.'+row.format,'Strict Node stream/case/provider identity');need(Number.isSafeInteger(stream.encodedBytes)&&stream.encodedBytes>0&&stream.encodedBytes<=1048576,'Compressed input cap BEFORE any future decoder');
  const raw=fullBytes({base64:stream.encodedBase64,bytes:stream.encodedBytes},1048576);need(hash(raw)===stream.encodedSha256&&consumeFNV1a(raw)===stream.encodedFNV1aU32,'Whole actual encoded bytes/hash/FNV');names.add(stream.streamId);
 }need(names.size===15,'Every required Node fixture/format stream');
 return{oracleSha256:expectedSha,nodeInputs:freeze(structuredClone(value.encodedStreams)),rawFixtures,cases:freeze(structuredClone(cases)),originalOracle:freeze(value),nodeOwnStreamCount:15,fullMatrixClaim:false};
}
