// UNWIRED SOURCE TEMPLATE. Bindings come from future reviewed static imports.
// This is a private valid-fixture comparand, never a public node:zlib fallback.
const operations=Object.freeze(['deflateSync','inflateSync','gzipSync','gunzipSync','deflateRawSync','inflateRawSync']);
const maxInput=1048576,maxOutput=16777216;
function requireValue(value,message){if(!value)throw new Error(message);}
function selectedInput(Buffer,input){
 requireValue(Buffer.isBuffer(input),'Only internally constructed ordinary Buffer fixtures');
 requireValue(input.byteLength<=maxInput,'Input cap');
 // Actual setup/correctness must separately prove fixed/attached/unshared windows.
 return input;
}
export function createNativeComparand({Buffer,api}){
 const selected=Object.fromEntries(operations.map(name=>{requireValue(typeof api[name]==='function','Missing native binding');return[name,api[name]];}));
 return Object.freeze(Object.fromEntries(operations.map(name=>[name,input=>{
  selectedInput(Buffer,input);
  const output=Reflect.apply(selected[name],undefined,[input]); // NO level/mtime/options argument.
  requireValue(Buffer.isBuffer(output)&&output.byteLength<=maxOutput,'Native bounded Buffer output');
  requireValue(output.byteLength===0||output.buffer!==input.buffer,'Nonempty native output must not alias input');return output;
 }])));
}
export function createFFlateComparand({Buffer,fflate}){
 const fixed=Object.freeze({level:6}),gzip=Object.freeze({level:6,mtime:0});
 const selected={deflateSync:fflate.zlibSync,inflateSync:fflate.unzlibSync,gzipSync:fflate.gzipSync,
  gunzipSync:fflate.gunzipSync,deflateRawSync:fflate.deflateSync,inflateRawSync:fflate.inflateSync};
 for(const name of operations)requireValue(typeof selected[name]==='function','Missing selected fflate sync binding');
 return Object.freeze(Object.fromEntries(operations.map(name=>[name,input=>{
  selectedInput(Buffer,input);const encoder=name==='deflateSync'||name==='gzipSync'||name==='deflateRawSync';
  const output=encoder?selected[name](input,name==='gzipSync'?gzip:fixed):selected[name](input);
  requireValue(output instanceof Uint8Array&&output.byteLength<=maxOutput,'fflate valid-domain output cap');
  requireValue(output.byteLength===0||output.buffer!==input.buffer,'Nonempty fflate output must not alias input');
  // Share a fresh JS-owned output window, like the native facade. No extra
  // Buffer.from(Uint8Array) copy is inserted to disguise bridge differences.
  // This POST-allocation check is not native allocation-limit/error parity.
  return Buffer.from(output.buffer,output.byteOffset,output.byteLength);
 }])));
}
