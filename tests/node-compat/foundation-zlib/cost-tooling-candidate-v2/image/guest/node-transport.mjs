// Host-side evidence carriers only. No codec module or object introspection.
import {requireValue} from './contract.mjs';
export function transportValue(value){
 const type=typeof value;
 if(type==='string')return{type,value,codeUnits:value.length,fullPrimitiveValueCaptured:true};
 if(value===null)return{type:'object',kind:'null',value:null,fullPrimitiveValueCaptured:true};
 if(type==='undefined')return{type,kind:'undefined',fullPrimitiveValueCaptured:true};
 if(type==='boolean')return{type,value,fullPrimitiveValueCaptured:true};
 if(type==='number')return{type,kind:Number.isNaN(value)?'NaN':value===Infinity?'Infinity':value===-Infinity?'-Infinity':Object.is(value,-0)?'-0':'finite',...(Number.isFinite(value)&&!Object.is(value,-0)?{value}:{}),fullPrimitiveValueCaptured:true};
 if(type==='bigint')return{type,decimal:value.toString(),fullPrimitiveValueCaptured:true};
 return{type,kind:'opaque',propertiesRead:false,fullPrimitiveValueCaptured:false};
}
export async function retainedNodeCall({Buffer,api,method,args,retain,name}){
 let value;
 try{value=api[method](...args);}
 catch(error){await retain(name+'-throw',{schemaVersion:1,kind:'node-codec-call-threw',method,thrown:transportValue(error)});throw error;}
 await retain(name+'-return-transport',{schemaVersion:1,kind:'node-codec-call-returned',method,value:transportValue(value)});
 if(Buffer.isBuffer(value))await retain(name+'-return-bytes',value);
 return value;
}
export async function retainedNodeInfo({Buffer,value,retain,name}){
 requireValue(value!==null&&typeof value==='object','Node info wrapper object');
 let buffer,engine;
 try{buffer=value.buffer;engine=value.engine;}
 catch(error){await retain(name+'-info-field-throw',{schemaVersion:1,kind:'node-info-field-read-threw',thrown:transportValue(error)});throw error;}
 await retain(name+'-buffer-transport',transportValue(buffer));
 requireValue(Buffer.isBuffer(buffer),'Node info Buffer');await retain(name+'-decoded',buffer);
 await retain(name+'-engine-transport',transportValue(engine));requireValue(engine!==null&&typeof engine==='object','Node info engine');
 let sourceBytesConsumed;
 try{sourceBytesConsumed=engine.bytesWritten;}
 catch(error){await retain(name+'-bytesWritten-throw',{schemaVersion:1,kind:'node-public-bytesWritten-read-threw',thrown:transportValue(error)});throw error;}
 await retain(name+'-sourceBytesConsumed-transport',transportValue(sourceBytesConsumed));
 requireValue(Number.isSafeInteger(sourceBytesConsumed)&&sourceBytesConsumed>=0,'public Node consumed byte count');
 return{buffer,sourceBytesConsumed};
}
