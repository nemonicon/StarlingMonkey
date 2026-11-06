// Derived host typed-capture protocol; no guest/provider/embedding API here.
import {need} from './models.mjs';
const hostNow=Date.now;
export function observed(value){const type=typeof value;if(type==='string'||type==='boolean'||value===null)return{type,value};if(type==='undefined')return{type};if(type==='number')return{type,...(Number.isFinite(value)?Object.is(value,-0)?{special:'negative-zero'}:{value}:{special:Number.isNaN(value)?'NaN':value===Infinity?'positive-infinity':'negative-infinity'})};if(type==='bigint')return{type,decimal:BigInt.prototype.toString.call(value)};return{type,opaque:true,fullOpaqueValueClaim:false};}
export async function captureSync({invoke,name,args,write,sequence,now=hostNow}){
 const id=++sequence.attempted,before=now();let value,thrown=false;try{value=invoke(name,args);}catch(error){value=error;thrown=true;}const after=now();
 const row={schemaVersion:1,sequence:id,name,args,kind:thrown?'throw':'return',observed:observed(value),hostWallBeforeMs:before,hostWallAfterMs:after};
 try{await write('raw/'+String(id).padStart(3,'0')+'.json',row);sequence.written++;}catch(captureError){(sequence.captureFailures??=[]).push({sequence:id,name,kind:row.kind,captureError});if(thrown)throw value;throw captureError;}
 if(thrown)throw value;need(typeof value==='string'&&value.length<=2*1024*1024,'Whole actual scalar string; never await/coerce unexpected return');return{raw:value,before,after};
}
export function captureDiagnostics(s){return{attempted:s.attempted,written:s.written,captureFailures:(s.captureFailures??[]).map(x=>({sequence:x.sequence,name:x.name,kind:x.kind,observed:observed(x.captureError)}))};}
