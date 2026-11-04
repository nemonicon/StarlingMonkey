import {pathToFileURL}from'node:url';
const[modulePath,operation]=process.argv.slice(2);const observations=[];
globalThis.__DEBUG_ABI_OBSERVE=observation=>observations.push(observation);
try{const guest=await import(pathToFileURL(modulePath));const value=guest[operation]();console.log(JSON.stringify({ok:true,value:ArrayBuffer.isView(value)?Array.from(value.subarray(0,128)):value,...(ArrayBuffer.isView(value)?{viewLength:value.length,truncated:value.length>128}:{}),observations}));}catch(error){console.log(JSON.stringify({ok:false,error:{name:error.name,message:error.message},observations}));}
