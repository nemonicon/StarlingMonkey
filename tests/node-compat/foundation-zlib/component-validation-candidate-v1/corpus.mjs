// Ordinary public byte APIs only. Shared/detached/getter/Proxy probes excluded.
export const encoders=Object.freeze(['gzipSync','deflateSync','deflateRawSync']);
export const decoders=Object.freeze(['gunzipSync','inflateSync','inflateRawSync']);
export const formats=Object.freeze([{encode:'gzipSync',decode:'gunzipSync',id:'gzip'},{encode:'deflateSync',decode:'inflateSync',id:'zlib'},{encode:'deflateRawSync',decode:'inflateRawSync',id:'raw'}]);
export const MAX_INPUT=1048576,MAX_OUTPUT=16777216;
const rows=[];
for(const format of formats){
 for(const[id,input,view]of[['empty',{kind:'zero',length:0},'u8'],['binary',{kind:'seed',length:256,seed:0x12345678},'buffer'],['offset',{kind:'repeat',length:1024,byte:65},'offset-u8']])
  rows.push({id:format.id+'-encode-'+id,operation:format.encode,input,view,expectedPlain:input,kind:'encode',phase:'ordinary'});
 for(const[id,plain,view]of[['empty',{kind:'zero',length:0},'arraybuffer'],['binary',{kind:'seed',length:256,seed:0x12345678},'offset-dataview'],['repeat',{kind:'repeat',length:4096,byte:65},'offset-buffer']])
  rows.push({id:format.id+'-decode-'+id,operation:format.decode,input:{kind:'fixture',id:format.id+'-'+id},view,expectedPlain:plain,kind:'decode',phase:'ordinary'});
 rows.push({id:format.id+'-encode-input-limit',operation:format.encode,input:{kind:'seed',length:MAX_INPUT,seed:0xDEADBEEF},view:'offset-u8',expectedPlain:{kind:'seed',length:MAX_INPUT,seed:0xDEADBEEF},kind:'encode',phase:'boundary',guestRoundtrip:'compressed-result-may-exceed-input-cap; Node-crossdecode-required'});
 rows.push({id:format.id+'-encode-limit-small',operation:format.encode,input:{kind:'repeat',length:256,byte:65},view:'u8',options:{maxOutputLength:1},kind:'error',profileCode:'ERR_BUFFER_TOO_LARGE',phase:'ordinary'});
 rows.push({id:format.id+'-encode-limit-valid',operation:format.encode,input:{kind:'seed',length:256,seed:17},view:'u8',options:{maxOutputLength:1024},expectedPlain:{kind:'seed',length:256,seed:17},kind:'encode',phase:'ordinary'});
 rows.push({id:format.id+'-decode-limit-exact',operation:format.decode,input:{kind:'fixture',id:format.id+'-repeat'},view:'u8',options:{maxOutputLength:4096},expectedPlain:{kind:'repeat',length:4096,byte:65},kind:'decode',phase:'ordinary'});
 rows.push({id:format.id+'-decode-limit-under',operation:format.decode,input:{kind:'fixture',id:format.id+'-repeat'},view:'u8',options:{maxOutputLength:4095},kind:'error',profileCode:'ERR_BUFFER_TOO_LARGE',phase:'ordinary'});
 rows.push({id:format.id+'-decode-output-cap',operation:format.decode,input:{kind:'fixture',id:format.id+'-output-cap'},view:'offset-u8',expectedPlain:{kind:'repeat',length:MAX_OUTPUT,byte:7},kind:'decode',phase:'large-output'});
 rows.push({id:format.id+'-decode-output-over-cap',operation:format.decode,input:{kind:'fixture',id:format.id+'-output-over-cap'},view:'u8',kind:'error',profileCode:'ERR_BUFFER_TOO_LARGE',phase:'large-output'});
 for(const[variant,code]of[['invalid','Z_DATA_ERROR'],['truncated','Z_BUF_ERROR'],['multi','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED'],['trailing','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED']])
  rows.push({id:format.id+'-'+variant,operation:format.decode,input:{kind:'fixture',id:format.id+'-'+variant},view:'u8',kind:'error',profileCode:code,phase:'ordinary',deviation:['multi','trailing'].includes(variant)?'strict-one-member-no-trailing':'compare-actual-Node-code'});
}
rows.push({id:'dictionary-refusal',operation:'inflateSync',input:{kind:'fixture',id:'zlib-dictionary'},view:'u8',kind:'error',profileCode:'ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED',phase:'ordinary',deviation:'Node reports dictionary need; profile explicitly unavailable'});
for(const operation of['gzipSync','inflateSync'])rows.push({id:operation+'-input-over-cap',operation,input:{kind:'zero',length:MAX_INPUT+1},view:'u8',kind:'error',profileCode:'ERR_OUT_OF_RANGE',phase:'boundary',deviation:'profile1MiB input cap precedes codec'});
for(const[value,label,code]of[[0,'zero','ERR_OUT_OF_RANGE'],[-1,'negative','ERR_OUT_OF_RANGE'],[1.5,'fractional','ERR_OUT_OF_RANGE'],['1','string','ERR_INVALID_ARG_TYPE'],[MAX_OUTPUT+1,'over-profile-cap','ERR_OUT_OF_RANGE']])
 rows.push({id:'option-'+label,operation:'gzipSync',input:{kind:'repeat',length:16,byte:1},view:'u8',options:{maxOutputLength:value},kind:'error',profileCode:code,phase:'ordinary'});
rows.push({id:'unknown-option-level',operation:'gzipSync',input:{kind:'repeat',length:16,byte:1},view:'u8',options:{level:1},kind:'error',profileCode:'ERR_SM_NODE_UNSUPPORTED',phase:'ordinary',deviation:'only maxOutputLength admitted'});
rows.push({id:'ordinary-string-input-refusal',operation:'gzipSync',input:{kind:'string',value:'ordinary text'},view:'direct',kind:'error',profileCode:'ERR_SM_NODE_UNSUPPORTED',phase:'ordinary',deviation:'Node accepts strings; profile byte-only'});
export const cases=Object.freeze(rows.map(row=>Object.freeze(row)));
export function plainBytes(descriptor){
 if(descriptor.kind==='string')return descriptor.value;
 const out=new Uint8Array(descriptor.length);let state=descriptor.seed>>>0;
 for(let i=0;i<out.length;i++){if(descriptor.kind==='seed'){state^=state<<13;state^=state>>>17;state^=state<<5;out[i]=state>>>24;}else out[i]=descriptor.kind==='repeat'?descriptor.byte:0;}
 return out;
}
export function fixtureBytes(hex){const out=new Uint8Array(hex.length/2);for(let i=0;i<out.length;i++)out[i]=parseInt(hex.slice(i*2,i*2+2),16);return out;}
export function inputFor(row,fixtures,BufferCtor){
 const source=row.input.kind==='fixture'?fixtureBytes(fixtures[row.input.id]):plainBytes(row.input);
 if(typeof source==='string'||row.view==='direct')return source;
 if(row.view==='arraybuffer')return source.buffer;
 if(row.view==='buffer')return BufferCtor.from(source);
 if(row.view?.startsWith('offset-')){const backing=new ArrayBuffer(source.length+24),window=new Uint8Array(backing,8,source.length);new Uint8Array(backing).fill(0xA5);window.set(source);if(row.view==='offset-dataview')return new DataView(backing,8,source.length);if(row.view==='offset-buffer')return BufferCtor.from(backing,8,source.length);return window;}
 return source;
}
export function byteView(value){if(value instanceof ArrayBuffer)return new Uint8Array(value);return new Uint8Array(value.buffer,value.byteOffset,value.byteLength);}
