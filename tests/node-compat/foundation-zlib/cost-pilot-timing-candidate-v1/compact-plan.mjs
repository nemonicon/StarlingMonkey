// Pure parent DATA projection from exact accepted finite proofs. No codec work.
import {need,ARMS} from './planner.mjs';
import {compactCase} from './collector.mjs';
export function compactExpectations({cases,inputFacts,rawFixtures,streams,oracleSha256}){
 need(Array.isArray(cases)&&cases.length===30&&Array.isArray(inputFacts)&&inputFacts.length===30,'complete finite case/input facts');
 need(Array.isArray(rawFixtures)&&rawFixtures.length===5&&Array.isArray(streams)&&streams.length===60,'five raw fixtures and all60 accepted streams');
 const result=[];
 for(const arm of ARMS)for(let index=0;index<30;index++){
  const row=cases[index],input=inputFacts[index];need(row.index===index&&input.index===index&&row.id===input.caseName,'exact ordered case identities');
  const raw=rawFixtures.find(v=>v.id===row.fixture);need(raw&&raw.bytes===row.logicalUncompressedBytesPerOperation,'actual raw logical domain');
  const encoder=streams.filter(v=>v.provider===arm&&v.fixture===row.fixture&&v.format===row.format);need(encoder.length===1,'one accepted actual encoder stream per arm/fixture/format');
  need(input.fixture===row.fixture&&input.direction===row.direction&&input.format===row.format&&input.logicalUncompressedBytes===raw.bytes,'accepted control input facts bind same primary');
  if(row.direction==='encode')need(input.inputBytes===raw.bytes&&input.inputFNV1aU32===raw.rawFNV1aU32&&input.inputSha256===raw.rawSha256,'full accepted raw input fingerprint');
  else{const node=streams.filter(v=>v.provider==='node-22.14.0'&&v.fixture===row.fixture&&v.format===row.format);need(node.length===1&&input.inputBytes===node[0].encodedBytes&&input.inputFNV1aU32===node[0].encodedFNV1aU32&&input.inputSha256===node[0].encodedSha256,'same actual Node decoder input across arms');}
  const encoded=encoder[0];result.push(compactCase({schemaVersion:1,caseId:index,caseName:row.id,arm,direction:row.direction,
   logicalBytes:raw.bytes,inputBytes:input.inputBytes,inputFNV:input.inputFNV1aU32,
   outputBytes:row.direction==='encode'?encoded.encodedBytes:raw.bytes,
   outputFNV:row.direction==='encode'?encoded.encodedFNV1aU32:raw.rawFNV1aU32,
   oracleSha256,inputSource:input.inputSource,parentDeclaredInputSha256:input.parentDeclaredInputSha256,timingNMax:row.timingNMax}));
 }
 need(result.length===90,'complete three-arm30-case compact plan');return Object.freeze(result);
}
