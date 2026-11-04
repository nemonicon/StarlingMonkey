// Concrete call order over a future reviewed synchronous Jco session.
// This module imports no loader/provider/guest and performs no calls at import.
import {observedCall,need,equalBytes,hash} from './transport.mjs';
import {consumeFNV1a} from './fixtures.mjs';
export async function call(session,collector,write,prefix,name,args){
 const record=await observedCall({invoke:session.invoke,write,name:prefix,exportName:name,args});
 const value=record.value;
 if(name==='identity')await collector.identity(value,prefix);
 else if(name==='setup')await collector.setup(value,args[0],prefix);
 else if(name==='stage')await collector.stage(value,JSON.parse(args[0]),prefix);
 else if(name==='observe')record.bytes=await collector.observe(value,args[0],prefix);
 else if(name==='checkpoint')await collector.checkpoint(value,prefix);
 else if(name==='validate')record.pair=await collector.validate(value,JSON.parse(args[0]),prefix);
 return record;
}
export async function primaryCase({session,collector,write,caseId,prefix}){
 await call(session,collector,write,prefix+'-setup','setup',[caseId]);
 const first=await call(session,collector,write,prefix+'-observe1','observe',[caseId]),second=await call(session,collector,write,prefix+'-observe2','observe',[caseId]);
 const batch=await observedCall({invoke:session.invoke,write,name:prefix+'-untimed-batchN1',exportName:'batch',args:[caseId,1]});await collector.batch(batch.value,caseId,prefix+'-untimed-batchN1',first.bytes);
 await call(session,collector,write,prefix+'-checkpoint1','checkpoint',[]);
 const request={schemaVersion:1,kind:'primary',caseId};const wrapped=await call(session,collector,write,prefix+'-validate','validate',[JSON.stringify(request)]);
 if(!equalBytes(first.bytes,wrapped.pair.first)||!equalBytes(second.bytes,wrapped.pair.second)){await write(prefix+'-pair-counterexample.json',{firstBase64:Buffer.from(first.bytes).toString('base64'),secondBase64:Buffer.from(second.bytes).toString('base64'),validateFirstBase64:Buffer.from(wrapped.pair.first).toString('base64'),validateSecondBase64:Buffer.from(wrapped.pair.second).toString('base64'),rawRows:[first.raw,second.raw,wrapped.raw]});throw new Error('ERR_COST_JCO_CORRECTNESS: separate/within-export output equality; full counterexample retained');}
 await call(session,collector,write,prefix+'-checkpoint2','checkpoint',[]);
 return {caseId,first:new Uint8Array(first.bytes),second:new Uint8Array(second.bytes),rawRows:[first.raw,second.raw,batch.raw,wrapped.raw],untimedBatchN1:true,withinExportPairCompared:true};
}
export async function crossdecode({session,collector,write,record,prefix}){
 const caseId=record.caseId;
 await call(session,collector,write,prefix+'-setup','setup',[caseId]);
 // Setup MUST precede stage, because setup clears old staging.
 await call(session,collector,write,prefix+'-stage','stage',[JSON.stringify(record)]);
 const first=await call(session,collector,write,prefix+'-observe1','observe',[caseId]),second=await call(session,collector,write,prefix+'-observe2','observe',[caseId]);
 const batch=await observedCall({invoke:session.invoke,write,name:prefix+'-untimed-batchN1',exportName:'batch',args:[caseId,1]});await collector.batch(batch.value,caseId,prefix+'-untimed-batchN1',first.bytes);
 await call(session,collector,write,prefix+'-checkpoint1','checkpoint',[]);
 const request={schemaVersion:1,kind:'crossdecode',caseId,stageRecord:record};const wrapped=await call(session,collector,write,prefix+'-validate','validate',[JSON.stringify(request)]);
 if(!equalBytes(first.bytes,wrapped.pair.first)||!equalBytes(second.bytes,wrapped.pair.second)){await write(prefix+'-pair-counterexample.json',{firstBase64:Buffer.from(first.bytes).toString('base64'),secondBase64:Buffer.from(second.bytes).toString('base64'),validateFirstBase64:Buffer.from(wrapped.pair.first).toString('base64'),validateSecondBase64:Buffer.from(wrapped.pair.second).toString('base64'),rawRows:[first.raw,second.raw,wrapped.raw]});throw new Error('ERR_COST_JCO_CORRECTNESS: separate/validate crossdecode equality; full counterexample retained');}
 await call(session,collector,write,prefix+'-checkpoint2','checkpoint',[]);
 return{streamId:record.streamId,provider:record.provider,caseId,fullRawOutputsMatched:true,rawRows:[first.raw,second.raw,batch.raw,wrapped.raw],ordinaryPublicSequence:true,withinExportSequenceSeparate:true};
}
export function makeStream({provider,row,bytes}){
 need(['native-on','fflate-on','fflate-off'].includes(provider)&&row.direction==='encode','actual guest encoder stream only');
 need(bytes instanceof Uint8Array&&bytes.length>0&&bytes.length<=1048576,'compressed cap before any decoder');
 return{schemaVersion:1,kind:'codec-cost-stage-v1',caseId:row.index+1,fixture:row.fixture,format:row.format,provider,streamId:provider+'.'+row.fixture+'.'+row.format,encodedBytes:bytes.length,encodedFNV1aU32:consumeFNV1a(bytes),encodedSha256:hash(bytes),encodedBase64:Buffer.from(bytes).toString('base64')};
}
export async function assertSameStream(write,name,actual,expected){
 const a=Buffer.from(actual.encodedBase64,'base64'),b=Buffer.from(expected.encodedBase64,'base64');
 if(!equalBytes(a,b)){await write(name+'-stream-counterexample.json',{actual,expected,comparison:'whole encoded bytes within same provider; or separately required FF-OFF vsFF-ON'});throw new Error('ERR_COST_JCO_CORRECTNESS: full stream bytes differ; counterexample retained');}
}
