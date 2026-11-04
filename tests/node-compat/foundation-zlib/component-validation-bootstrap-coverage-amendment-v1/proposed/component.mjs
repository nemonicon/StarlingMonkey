import zlib,* as namespace from 'node:zlib';
import {Buffer} from 'node:buffer';
import cjs from './canonical-require.cjs';
import {cases,formats,inputFor,plainBytes,byteView,MAX_INPUT} from './corpus.mjs';
import {fixtures} from './node-fixtures.mjs';
import {contract} from './profile-contract.mjs';
const requireValue=(value,message)=>{if(!value)throw new Error(message);};
let calls=0;
function typed(value){return typeof value==='number'&&!Number.isFinite(value)?{type:'number',valueEncoding:value===Infinity?'positive-infinity':value===-Infinity?'negative-infinity':'NaN'}:{type:typeof value,value:value===undefined?null:value};}
function errorRecord(error){const fields={};for(const key of['code','module','operation','profile','errno'])fields[key]={own:Object.hasOwn(error,key),...typed(error[key])};return{name:error.name,fields};}
function allRefusals(){const records=[];for(const name of contract.deferred)for(const mode of['call','new']){try{if(mode==='new')new namespace[name]();else namespace[name]();throw new Error('Expected finite deferred error');}catch(error){records.push({name,mode,error:errorRecord(error)});}}
 for(const name of contract.sync){try{new namespace[name](Buffer.from([1]));throw new Error('Expected finite construction refusal');}catch(error){records.push({name,mode:'new-sync',error:errorRecord(error)});}}return records;}
const initializationRefusals=allRefusals();
const snapshotInput=Buffer.from([0,1,2,3,254,255]),snapshotCompressed=zlib.gzipSync(snapshotInput),snapshotPlain=zlib.gunzipSync(snapshotCompressed);
requireValue(snapshotPlain.length===snapshotInput.length&&snapshotPlain.every((value,index)=>value===snapshotInput[index]),'Pure initialization roundtrip');
const snapshot={inputHex:snapshotInput.toString('hex'),compressedHex:snapshotCompressed.toString('hex'),plainHex:snapshotPlain.toString('hex')};
export async function moduleContract(){
 const aliasId='z'+'lib',canonicalId='node:'+'zlib',alias=await import(aliasId),aliasAgain=await import(aliasId),canonical=await import(canonicalId),canonicalAgain=await import(canonicalId);const names=Object.keys(namespace).sort();
 const result={calls,aliasNamespaceCached:alias===aliasAgain,canonicalNamespaceCached:canonical===canonicalAgain,canonicalStaticNamespace:canonical===namespace,namespace:names,aliasNamespace:Object.keys(alias).sort(),sameAliases:names.every(name=>alias[name]===namespace[name]),defaultNamed:names.filter(name=>name!=='default').every(name=>namespace[name]===zlib[name]),cjsDefault:cjs===zlib,
  globalBuffer:globalThis.Buffer===Buffer,thenType:typeof namespace.then,defaultThenType:typeof zlib.then,
  constants:Object.fromEntries(Object.entries(zlib.constants).map(([name,value])=>[name,typed(value)])),codes:Object.fromEntries(Object.entries(zlib.codes).map(([name,value])=>[name,typed(value)])),
  publicVernum:typed(zlib.constants.ZLIB_VERNUM),legacyVernum:typed(zlib.ZLIB_VERNUM),sameConstantObjects:namespace.constants===zlib.constants&&namespace.codes===zlib.codes,
  frozenDefault:Object.isFrozen(zlib),frozenConstants:Object.isFrozen(zlib.constants),frozenCodes:Object.isFrozen(zlib.codes),constantPrototypeNull:Object.getPrototypeOf(zlib.constants)===null,codePrototypeNull:Object.getPrototypeOf(zlib.codes)===null,
  publicBackendInfoType:typeof namespace.backendInfo,publicKernelType:typeof namespace.kernel,initializationRefusals,snapshot};
 requireValue(names.length===40&&names.every((name,index)=>name===[...contract.exports].sort()[index]),'Exactly40 finite public bindings');return JSON.stringify(result);
}
export function refusals(){return JSON.stringify({records:allRefusals(),initializationRefusals});}
export function run(index){
 calls++;requireValue(Number.isInteger(index)&&index>=0&&index<cases.length,'Finite codec case');const row=cases[index],input=inputFor(row,fixtures,Buffer),source=typeof input==='string'?null:byteView(input),before=source?new Uint8Array(source):null,backingBefore=source?new Uint8Array(new Uint8Array(source.buffer)):null;
 let output,error=null,returned=false;try{output=namespace[row.operation](input,row.options);returned=true;}catch(value){error=errorRecord(value);}
 const immutable=source===null||source.length===before.length&&source.every((value,i)=>value===before[i])&&new Uint8Array(source.buffer).every((value,i)=>value===backingBefore[i]);requireValue(immutable,'Full input and backing-window sentinel immutability');
 if(error){const recovery=zlib.gunzipSync(inputFor(cases.find(row=>row.id==='gzip-decode-binary'),fixtures,Buffer));requireValue(recovery.length===256,'Ordinary post-error recovery');return JSON.stringify({calls,index,id:row.id,outcome:'error',error,partialOutputPublished:returned,inputImmutable:immutable,recoveryHex:recovery.toString('hex')});}
 requireValue(Buffer.isBuffer(output)&&output instanceof Uint8Array&&Object.getPrototypeOf(output)===Buffer.prototype,'Actual global Buffer result');
 requireValue(output.buffer!==source?.buffer,'Fresh output storage');
 let roundtrip=null;
 if(row.kind==='encode'){
  const decoder=formats.find(format=>format.encode===row.operation).decode;
  if(output.length>MAX_INPUT){try{namespace[decoder](output);throw new Error('Expected compressed-input cap');}catch(value){roundtrip={kind:'input-cap',error:errorRecord(value)};}}
  else{const decoded=namespace[decoder](output),expected=plainBytes(row.expectedPlain);requireValue(decoded.length===expected.length&&decoded.every((value,i)=>value===expected[i]),'Full guest roundtrip bytes');roundtrip={kind:'decoded',bytes:decoded.length};}
 }
 return JSON.stringify({calls,index,id:row.id,outcome:'ok',outputHex:output.toString('hex'),outputLength:output.length,inputImmutable:immutable,isBuffer:Buffer.isBuffer(output),globalBuffer:Buffer===globalThis.Buffer,byteOffset:output.byteOffset,backingLength:output.buffer.byteLength,roundtrip});
}
export function ownership(){
 const backing=new ArrayBuffer(280),input=new Uint8Array(backing,8,256);for(let i=0;i<input.length;i++)input[i]=(i*17+3)&255;
 const first=zlib.deflateSync(input),original=first.toString('hex'),second=zlib.deflateSync(input);input.fill(0);
 requireValue(first.toString('hex')===original,'Output stable after input mutation');second[0]^=255;requireValue(first.toString('hex')===original,'Independent successful outputs');
 return JSON.stringify({firstHex:original,independentBacking:first.buffer!==second.buffer,inputSharedWithOutput:first.buffer===backing,inputByteOffset:8,inputByteLength:256,globalBuffer:Buffer===globalThis.Buffer});
}
export function ordinaryGc(){
 const out=zlib.gunzipSync(inputFor(cases.find(row=>row.id==='gzip-decode-repeat'),fixtures,Buffer)),before=out.toString('hex');
 const operations=[];for(let i=0;i<8;i++){const value=Buffer.from([i]);operations.push(value.toString('hex'));}
 requireValue(out.toString('hex')===before&&out.length===4096,'Retained codec output across ordinary Buffer operations');
 return JSON.stringify({bytes:out.length,outputHex:before,operations,applicationStrongOwnerRetained:true,vmTemporaryRootsIsolated:false,privateGcHookUsed:false});
}
