// Pure DATA validators. No Wasm/library/process is loaded or invoked here.
import {need,hash} from './authority.mjs';
export const ABI=Object.freeze({identity:'() -> string',setup:'(u32) -> string',observe:'(u32) -> string',batch:'(u32,u32) -> string',checkpoint:'() -> string',stage:'(string) -> string',validate:'(string) -> string'});
export function exactABI(exports,imports){
 need(imports.length===0,'Actual final component imports must be empty');
 need(exports&&Object.keys(exports).length===7&&Object.keys(ABI).every(key=>exports[key]===ABI[key]),'Actual emitted seven-function scalar ABI required');return true;
}
export function retainedString(envelope){
 need(envelope?.rawDurablyRetained===true&&envelope.typeofValue==='string'&&typeof envelope.value==='string','Retain raw typed return BEFORE validation');
 need(envelope.value.length<=2097152,'Full response exceeds2MiB UTF16 cap');return JSON.parse(envelope.value);
}
function count(value){need(Number.isSafeInteger(value)&&value>=0,'Safe nonnegative exact count');return value;}
export function counterDelta(before,after,expected){
 const names=Object.keys(ABI);for(const item of[before,after]){
  need(item&&Object.keys(item).length===4,'Exact counter schema');count(item.publicFunctionEntries);count(item.codecCalls);count(item.controlOperations);
  need(item.perExportEntries&&Object.keys(item.perExportEntries).length===7&&names.every(name=>Number.isSafeInteger(item.perExportEntries[name])&&item.perExportEntries[name]>=0),'Seven per-export counters');
  need(names.reduce((sum,name)=>sum+item.perExportEntries[name],0)===item.publicFunctionEntries,'Named-entry sum is not outer invocation count');
 }
 for(const name of names)need(after.perExportEntries[name]-before.perExportEntries[name]===(expected.entries[name]??0),'Unexpected named-entry delta: '+name);
 need(after.codecCalls-before.codecCalls===expected.codecCalls&&after.controlOperations-before.controlOperations===expected.controlOperations,'Unexpected codec/control delta');return true;
}
export function wasmArgumentFeasibility({argv,environment,argMax,perArgumentLimit=null,transportProof}){
 need(Array.isArray(argv)&&argv.length>0&&argv.every(v=>typeof v==='string'&&!v.includes('\0')),'Exact final argv strings');
 need(environment&&Object.values(environment).every(v=>typeof v==='string'&&!v.includes('\0')),'Exact final child environment');
 count(argMax);need(argMax>0,'Measured host ARG_MAX required; wire cap is not argv allowance');
 need(transportProof?.actualStringParserABIProved===true&&transportProof.actualMaximumStagedRecordProved===true,'Actual stockCLI string parser AND largest real record proof required');
 const argumentBytes=argv.map(v=>Buffer.byteLength(v,'utf8')+1),environmentBytes=Object.entries(environment).reduce((sum,[key,value])=>sum+Buffer.byteLength(key+'='+value,'utf8')+1,0);
 // Pointer accounting is explicitly conservative for this selected64-bit host.
 const pointerBytes=8*(argv.length+Object.keys(environment).length+2),totalBytes=argumentBytes.reduce((a,b)=>a+b,0)+environmentBytes+pointerBytes;
 need(totalBytes<argMax,'Encoded argument+environment+pointer bytes exceed measured ARG_MAX');
 if(perArgumentLimit!==null){count(perArgumentLimit);need(argumentBytes.every(v=>v<perArgumentLimit),'Per-argument transport limit exceeded');}
 return{argumentBytes,environmentBytes,pointerBytes,totalBytes,argMax,perArgumentLimit,wireCapSubstitutedForArgvBudget:false};
}
export function fullBytes(record,expected,{maximum=1048576}={}){
 need(record&&typeof record.base64==='string'&&Number.isSafeInteger(record.bytes)&&record.bytes>=0&&record.bytes<=maximum,'Bounded full-byte response');
 const bytes=Buffer.from(record.base64,'base64');need(bytes.toString('base64')===record.base64&&bytes.length===record.bytes,'Canonical full base64/length');
 need(expected instanceof Uint8Array&&bytes.length===expected.length,'Exact expected byte length');
 for(let i=0;i<bytes.length;i++)if(bytes[i]!==expected[i])throw new Error('Full-byte mismatch at bounded first index '+i+' (complete raw data must already be retained)');
 if(record.sha256!==undefined)need(record.sha256===hash(bytes),'Full-byte SHA');return bytes;
}
export function adjacentOwnership(first,second){
 need(first?.ownership?.previousComparable===false&&first.ownership.previousFullBytesUnchanged===null,'First observation is not a prior-stability proof');
 need(second?.ownership?.previousComparable===true&&second.ownership.previousFullBytesUnchanged===true,'Full prior-output stability must be observed after the next codec call');
 if(second.output.bytes>0&&first.output.bytes>0){const own=second.ownership;
  need(own.successiveIndependentBacking===true&&own.mutationProbe?.performed===true&&own.mutationProbe.currentFullBytesUnchanged===true&&own.mutationProbe.inputFullBytesUnchanged===true&&own.mutationProbe.previousRestored===true,'Complete nonempty mutation/restoration ownership proof');}
 return true;
}
export function workerBudget({pilotOperationMs,pilotWholeProcessMs,operations,large}){
 need(Number.isFinite(pilotOperationMs)&&pilotOperationMs>0&&Number.isFinite(pilotWholeProcessMs)&&pilotWholeProcessMs>=0,'Actual positive pilot observations');
 need(Number.isSafeInteger(operations)&&operations>0&&operations<=(large?128:32768),'Declared sharedN cap; no clipping');
 const milliseconds=Math.ceil(2*pilotOperationMs*operations*10+pilotOperationMs*operations+120000+2*Math.max(0,pilotWholeProcessMs-pilotOperationMs));
 need(milliseconds<=7200000,'Whole worker budget exceeds2h; refuse phase rather than omit samples');return milliseconds;
}
