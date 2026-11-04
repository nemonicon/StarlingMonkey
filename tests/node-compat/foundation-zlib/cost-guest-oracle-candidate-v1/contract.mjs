// Pure finite data/transport contract. No codec, Node-zlib or package imports.
import {cases} from './cases.generated.mjs';
import {consumeFNV1a} from './fixtures.mjs';
export {cases};
export const VERSION='bounded-zlib-cost-guest-v1';
export const MAX_INPUT=1048576,MAX_OUTPUT=16777216,MAX_RAW=524288,MAX_WIRE=2097152;
export const EXPORTS=Object.freeze(['identity','setup','observe','batch','checkpoint','stage','validate']);
export const ENCODERS=Object.freeze(['node-22.14.0','native-on','fflate-on','fflate-off']);
export const FORMATS=Object.freeze(['zlib','gzip','raw']);
const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
export function requireValue(value,message){if(!value)throw new Error('ERR_CODEC_COST_CONTRACT: '+message);}
export function u32(value,label='u32'){requireValue(Number.isInteger(value)&&value>=0&&value<=4294967295,label);return value;}
export function exactKeys(value,keys,label){requireValue(value!==null&&typeof value==='object'&&!Array.isArray(value),label);requireValue(Object.keys(value).sort().join('|')===[...keys].sort().join('|'),label+' keys');return value;}
export function primaryCase(index){u32(index,'case id');requireValue(index<30,'primary case0..29');return cases[index];}
export function caseSelection(index){u32(index,'case id');requireValue(index<120,'finite codec/control ID');return{primary:cases[index%30],kind:index<30?'codec':index<60?'consumeInput':index<90?'copyInputAndConsume':'harnessNoCodec'};}
export function operationCount(index,operations){const selected=caseSelection(index);u32(operations,'operation count');requireValue(operations>0,'positive operation count');requireValue(selected.kind==='codec'?operations<=selected.primary.timingNMax:operations===1,'finite N/control N1');return selected;}
export function jsonRecord(source){requireValue(typeof source==='string','record must be a string');requireValue(source.length<=MAX_WIRE,'record UTF16 cap');return JSON.parse(source);}
export function wire(value){const output=JSON.stringify(value);requireValue(output.length<=MAX_WIRE,'serialized response UTF16 cap; never truncate');return output;}
export function bytesEqual(a,b){if(a.length!==b.length)return false;for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;return true;}
export function base64(bytes){let result='';for(let i=0;i<bytes.length;i+=3){const a=bytes[i],hasB=i+1<bytes.length,hasC=i+2<bytes.length,b=hasB?bytes[i+1]:0,c=hasC?bytes[i+2]:0;result+=alphabet[a>>>2]+alphabet[((a&3)<<4)|(b>>>4)]+(hasB?alphabet[((b&15)<<2)|(c>>>6)]:'=')+(hasC?alphabet[c&63]:'=');}return result;}
export function unbase64(source,maxBytes=MAX_INPUT){
 requireValue(Number.isInteger(maxBytes)&&maxBytes>=0&&maxBytes<=MAX_OUTPUT,'finite decoded bound');
 requireValue(typeof source==='string'&&source.length%4===0&&source.length<=Math.ceil(maxBytes/3)*4,'canonical bounded base64 text');
 const padding=source.endsWith('==')?2:source.endsWith('=')?1:0,length=source.length/4*3-padding;
 for(let i=0;i<source.length;i++)requireValue(i>=source.length-padding?source[i]==='=':alphabet.includes(source[i]),'canonical base64 alphabet/padding');
 requireValue(length<=maxBytes,'decoded bytes cap before allocation');const result=new Uint8Array(length);let out=0;
 for(let i=0;i<source.length;i+=4){const a=alphabet.indexOf(source[i]),b=alphabet.indexOf(source[i+1]),c=source[i+2]==='='?0:alphabet.indexOf(source[i+2]),d=source[i+3]==='='?0:alphabet.indexOf(source[i+3]);if(out<length)result[out++]=(a<<2)|(b>>>4);if(out<length)result[out++]=((b&15)<<4)|(c>>>2);if(out<length)result[out++]=((c&3)<<6)|d;}
 requireValue(base64(result)===source,'zero base64 pad bits');return result;
}
export function stageRecord(value){
 exactKeys(value,['schemaVersion','kind','caseId','fixture','format','provider','streamId','encodedBytes','encodedFNV1aU32','encodedSha256','encodedBase64'],'stage');
 requireValue(value.schemaVersion===1&&value.kind==='codec-cost-stage-v1','stage version');const row=primaryCase(value.caseId);
 requireValue(row.direction==='decode'&&row.fixture===value.fixture&&row.format===value.format,'stage matches active trusted decoder case');
 requireValue(ENCODERS.includes(value.provider),'trusted encoder provider ID');
 requireValue(value.streamId===value.provider+'.'+value.fixture+'.'+value.format,'exact stream ID');
 requireValue(Number.isInteger(value.encodedBytes)&&value.encodedBytes>0&&value.encodedBytes<=MAX_INPUT,'compressed input bytes');u32(value.encodedFNV1aU32,'encoded FNV');
 requireValue(typeof value.encodedSha256==='string'&&/^[0-9a-f]{64}$/.test(value.encodedSha256),'parent authenticated SHA descriptor');
 const bytes=unbase64(value.encodedBase64);requireValue(bytes.length===value.encodedBytes&&consumeFNV1a(bytes)===value.encodedFNV1aU32,'decoded length/FNV');
 return{record:value,bytes,row};
}
export function nodeInputs(value){
 exactKeys(value,['schemaVersion','kind','oracleSha256','records'],'Node inputs');
 requireValue(value.schemaVersion===1&&value.kind==='codec-cost-node-inputs-v1','Node input version');
 requireValue(typeof value.oracleSha256==='string'&&/^[0-9a-f]{64}$/.test(value.oracleSha256),'actual oracle binding');
 requireValue(Array.isArray(value.records)&&value.records.length===15,'fifteen Node decoder inputs');
 const expected=cases.filter(row=>row.direction==='decode');
 for(let i=0;i<expected.length;i++){const record=value.records[i];requireValue(record!==null&&typeof record==='object'&&record.caseId===expected[i].index&&record.provider==='node-22.14.0','exact ordered Node input IDs');}
 return value;
}
export function aggregateStep(hash,outputFNV,outputBytes,index){for(const value of[outputFNV,outputBytes,index])hash=Math.imul(hash^(value>>>0),16777619)>>>0;return hash;}
