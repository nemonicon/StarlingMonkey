// Host evidence only. Never inspect an unexpected opaque value's properties.
import {createHash} from 'node:crypto';
export function need(ok,message){if(!ok)throw new Error('ERR_COST_JCO_CORRECTNESS: '+message);}
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function typed(value){
 const type=typeof value;
 if(value===null)return{type,kind:'null',value:null,fullPrimitiveCaptured:true};
 if(type==='string')return{type,value,codeUnits:value.length,fullPrimitiveCaptured:true};
 if(type==='undefined')return{type,kind:'undefined',fullPrimitiveCaptured:true};
 if(type==='boolean')return{type,value,fullPrimitiveCaptured:true};
 if(type==='number')return{type,kind:Number.isNaN(value)?'NaN':value===Infinity?'Infinity':value===-Infinity?'-Infinity':Object.is(value,-0)?'-0':'finite',...(Number.isFinite(value)&&!Object.is(value,-0)?{value}:{}),fullPrimitiveCaptured:true};
 if(type==='bigint')return{type,decimal:value.toString(),fullPrimitiveCaptured:true};
 return{type,kind:'opaque',propertiesRead:false,fullPrimitiveCaptured:false};
}
export function exactKeys(value,names,label){need(value!==null&&typeof value==='object'&&!Array.isArray(value),label+' object');need(Object.keys(value).sort().join('|')===[...names].sort().join('|'),label+' exact fields');}
export function equalBytes(a,b){if(a.length!==b.length)return false;for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;return true;}
export function fullBytes(record,maximum=1048576){
 need(record&&typeof record.base64==='string'&&Number.isSafeInteger(record.bytes)&&record.bytes>=0&&record.bytes<=maximum,'finite full output');
 need(record.base64.length<=Math.ceil(maximum/3)*4,'bounded base64 before decode');
 const raw=Buffer.from(record.base64,'base64');need(raw.toString('base64')===record.base64&&raw.length===record.bytes,'canonical complete bytes');return raw;
}
export async function exact(write,name,actual,expected){
 // Both are already ordinary data; no assert formatter ever sees giant values.
 if(JSON.stringify(actual)!==JSON.stringify(expected)){
  await write(name+'-counterexample.json',{schemaVersion:1,actual,expected,comparison:'exact JSON data; no byte or trace truncation'});
  throw new Error('ERR_COST_JCO_CORRECTNESS: exact mismatch; full counterexample retained at '+name);
 }
}
export async function observedCall({invoke,write,name,exportName,args}){
 let value;
 await write(name+'-before.json',{schemaVersion:1,exportName,args,partial:true});
 // The reviewed synchronous scalar contract must not assimilate a Promise or thenable.
 try{value=invoke(exportName,args);}
 catch(error){await write(name+'-throw.json',{schemaVersion:1,exportName,thrown:typed(error),partial:true});throw new Error('ERR_COST_JCO_CORRECTNESS: guest call threw; typed evidence retained at '+name);}
 const raw=await write(name+'-raw.json',{schemaVersion:1,exportName,returned:typed(value),partial:true});
 need(typeof value==='string','typed raw return retained before string requirement');
 need(value.length<=2097152,'full scalar string exceeds wire cap; no clipping');
 let parsed;try{parsed=JSON.parse(value);ordinaryReturnedJSON(parsed);}catch{throw new Error('ERR_COST_JCO_CORRECTNESS: invalid/nonfinite returned JSON; complete raw return retained at '+name);}
 return{value:parsed,raw,rawString:value};
}

export function ordinaryReturnedJSON(value){
 const pending=[{value,depth:0}];let nodes=0;
 while(pending.length){const item=pending.pop(),v=item.value;need(++nodes<=1048576&&item.depth<=64,'bounded ordinary returned JSON');
  if(v===null||typeof v==='string'||typeof v==='boolean')continue;
  if(typeof v==='number'){need(Number.isFinite(v)&&!Object.is(v,-0),'finite exact JSON numbers');continue;}
  need(v&&typeof v==='object','ordinary JSON data');
  for(const child of Object.values(v))pending.push({value:child,depth:item.depth+1});
 }return value;
}
