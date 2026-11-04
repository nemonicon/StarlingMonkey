// Host-side typed retention before the declared string result assertion.
// It never reads arbitrary object properties/getters or guest/private memory.
export function transportReturnEnvelope(value){
 const type=typeof value;
 if(type==='string')return{type,codeUnits:value.length,valueStoredSeparatelyAsRawString:true};
 if(value===null)return{type:'object',kind:'null',value:null,fullPrimitiveValueCaptured:true};
 if(type==='undefined')return{type,kind:'undefined',fullPrimitiveValueCaptured:true};
 if(type==='number')return{type,kind:Number.isNaN(value)?'NaN':value===Infinity?'Infinity':value===-Infinity?'-Infinity':Object.is(value,-0)?'-0':'finite',...(Number.isFinite(value)&&!Object.is(value,-0)?{value}:{}),fullPrimitiveValueCaptured:true};
 if(type==='boolean')return{type,value,fullPrimitiveValueCaptured:true};
 if(type==='bigint')return{type,decimal:value.toString(),fullPrimitiveValueCaptured:true};
 return{type,kind:'opaque-unexpected-transport-type',fullPrimitiveValueCaptured:false,propertiesRead:false};
}
