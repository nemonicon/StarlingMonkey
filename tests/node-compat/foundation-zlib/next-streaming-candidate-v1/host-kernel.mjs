// TEST-ONLY Node contract adapter. No guest/native candidate code executes.
// writeSync/_writeState are the ACTUAL pinned lib/zlib.js internal seam,
// inspected in upstream/node22-zlib.js processChunkSync. Not a guest API.
import zlib from 'node:zlib';
export function hostKernel(){
 let deployed=true;const live=new Set(),counts={open:0,close:0,feed:0,pull:0};
 const error=(code)=>Object.assign(new Error(code),{code});
 const phase=()=>{if(!deployed)throw error('ERR_SM_NODE_ZLIB_INITIALIZATION');};
 const k={
 checkPhase:phase,
 open(format,level,windowBits,memLevel,strategy,chunkSize){phase();if(live.size===16)throw error('ERR_SM_ZLIB_STREAM_LIMIT');const codec=(format?zlib.createGzip:zlib.createDeflate)({level,windowBits,memLevel,strategy,chunkSize});const h={codec,chunkSize,input:null,offset:0,flush:0,pending:false,ended:false,closed:false,totalIn:0,totalOut:0,steps:0,error:null};codec.on('error',e=>{h.error=e;});live.add(h);counts.open++;return h;},
 feed(h,input,flush){phase();if(h.closed||h.pending||h.ended)throw error('ERR_SM_ZLIB_STREAM_STATE');if(input.length>65536||h.totalIn+input.length>67108864)throw error('ERR_SM_ZLIB_STREAM_LIMIT');h.input=new Uint8Array(input);h.offset=0;h.flush=flush;h.pending=true;h.totalIn+=input.length;counts.feed++;},
 pull(h){phase();if(h.closed||!h.pending)throw error('ERR_SM_ZLIB_STREAM_STATE');if(h.steps++===65536)throw error('ERR_SM_ZLIB_STREAM_LIMIT');counts.pull++;const output=new Uint8Array(h.chunkSize),remaining=h.input.length-h.offset;h.codec._handle.writeSync(h.flush,h.input,h.offset,remaining,output,0,output.length);if(h.error)throw h.error;const [outLeft,inLeft]=h.codec._writeState;const have=output.length-outLeft;h.offset+=remaining-inLeft;h.totalOut+=have;if(h.totalOut>83886080)throw error('ERR_SM_ZLIB_STREAM_LIMIT');const done=inLeft===0&&outLeft!==0;h.pending=!done;h.ended=done&&h.flush===4;return {bytes:output.subarray(0,have),actionDone:done,ended:h.ended};},
 close(h){if(h.closed)return;h.closed=true;h.codec.close();live.delete(h);counts.close++;}
 };
 const sync={backendInfo(){return {headerVersion:process.versions.zlib,runtimeVersion:process.versions.zlib,vernum:zlib.constants.ZLIB_VERNUM};},run(input,format,encode,limit){const fn=(encode?[zlib.deflateSync,zlib.gzipSync,zlib.deflateRawSync]:[zlib.inflateSync,zlib.gunzipSync,zlib.inflateRawSync])[format];return new Uint8Array(fn(input,{maxOutputLength:limit}));}};
 return {kernel:k,sync,counts,setDeployed(v){deployed=v;},get active(){return live.size;},cleanup(){for(const h of [...live])k.close(h);}};
}
