// Exact synchronous return capture; unexpected values are never awaited/coerced.
import {need} from './models.mjs';
const bigintString=BigInt.prototype.toString;
export function primitive(value){
 const type=typeof value;
 if(value===null||type==='string'||type==='boolean')return{type,value};
 if(type==='undefined')return{type};
 if(type==='number')return Number.isFinite(value)?Object.is(value,-0)?{type,special:'negative-zero'}:{type,value}:{type,special:Number.isNaN(value)?'NaN':value>0?'positive-infinity':'negative-infinity'};
 if(type==='bigint')return{type,decimal:Reflect.apply(bigintString,value,[])};
 return{type,opaque:true,fullOpaqueValueClaim:false};
}
export async function capturedRun(invoke,write,sequence){
 const id=++sequence.attempted;let value,thrown=false;
 try{value=invoke();}catch(error){value=error;thrown=true;}
 const raw={schemaVersion:1,name:'run',args:[],kind:thrown?'throw':'return',observed:primitive(value)};
 try{await write('raw/'+String(id).padStart(3,'0')+'.json',raw);sequence.written++;}
 catch(captureError){sequence.captureFailures.push({id,kind:raw.kind,error:primitive(captureError),rawRecordRetained:false});if(thrown)throw value;throw captureError;}
 if(thrown)throw value;
 need(typeof value==='string'&&value.length<=2097152,'Whole ordinary bounded string AFTER durable raw retention');return value;
}
