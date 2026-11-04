import bufferDefault,{Buffer} from 'node:buffer';
import consumerDefault,* as consumers from 'node:stream/consumers';
import {ReadableStream as SelectedReadableStream} from 'node:stream/web';
import {Readable} from 'node:stream';
import required from './consumer.cjs';
import {textChecks} from './differential.mjs';
import {profileChecks} from './profiles.mjs';
import {extraCase,extraNames} from './extras.mjs';
const own=Object.hasOwn;
const backing=new ArrayBuffer(7),view=new Uint8Array(backing,2,3);view.set([65,66,67]);
const snapshotBuffer=Buffer.from(new Uint8Array([17,18]));
const snapshotText=await consumers.text([view,'!']);
const snapshotJson=await consumers.json(['{"snapshot":true}']);
const snapshotFlush=await consumers.text([new Uint8Array([0xe2])]);
let calls=0,gcCalls=0;
function errorFields(error){const fields={};for(const key of['code','module','operation','profile'])fields[key]={own:own(error,key),type:typeof error[key],value:error[key]};return{name:error.name,fields};}
function refusalRecords(){const records=[];for(const name of['arrayBuffer','blob','buffer'])for(const mode of['call','new']){let error;try{if(mode==='new')Reflect.construct(consumers[name],[[]]);else consumers[name]([]);}catch(caught){error=caught;}if(!error)throw new Error('Missing consumer refusal');records.push({name,mode,error:errorFields(error)});}return records;}
const initializationRefusals=refusalRecords();
function snapshot(){return{text:snapshotText,json:snapshotJson,flush:snapshotFlush,bufferByte:snapshotBuffer[0],bufferBrand:Buffer.isBuffer(snapshotBuffer),viewOffset:view.byteOffset,backingBytes:backing.byteLength};}
export async function moduleContract(){
 const canonicalId=String.fromCharCode(110,111,100,101,58,115,116,114,101,97,109,47,99,111,110,115,117,109,101,114,115),aliasId=String.fromCharCode(115,116,114,101,97,109,47,99,111,110,115,117,109,101,114,115);
 const canonical=await import(canonicalId),canonicalAgain=await import(canonicalId),alias=await import(aliasId),aliasAgain=await import(aliasId);
 const names=Object.keys(consumers).sort(),values=['arrayBuffer','blob','buffer','text','json'];
 return JSON.stringify({calls,gcCalls,names,aliasNames:Object.keys(alias).sort(),canonicalCached:canonical===canonicalAgain,aliasCached:alias===aliasAgain,canonicalStatic:canonical===consumers,aliasValues:values.every(name=>alias[name]===consumers[name])&&alias.default===consumerDefault,defaultNamed:values.every(name=>consumerDefault[name]===consumers[name]),defaultKeys:Object.keys(consumerDefault),defaultMutable:!Object.isFrozen(consumerDefault),cjsDefault:required===consumerDefault,thenType:typeof consumers.then,aliasThenType:typeof alias.then,defaultThenType:typeof consumerDefault.then,safeAwaitNamespace:await Promise.resolve(consumers)===consumers,safeAwaitAlias:await Promise.resolve(alias)===alias,safeAwaitDefault:await Promise.resolve(consumerDefault)===consumerDefault,namespaceTag:Object.prototype.toString.call(consumers),namespacePrototypeNull:Object.getPrototypeOf(consumers)===null,namespaceExtensible:Object.isExtensible(consumers),globalBuffer:globalThis.Buffer===Buffer&&bufferDefault.Buffer===Buffer,privateFactoryType:typeof consumers.createConsumersModule,privateDecoderType:typeof consumers.TextDecoder,selectedWeb:{constructor:typeof SelectedReadableStream,asyncIterator:typeof SelectedReadableStream.prototype[Symbol.asyncIterator]},rawGlobalReadableObservation:{constructor:typeof globalThis.ReadableStream,asyncIterator:typeof globalThis.ReadableStream?.prototype[Symbol.asyncIterator],passedToConsumer:false},snapshot:snapshot(),initializationRefusals});
}
export async function run(index){
 if(!Number.isInteger(index)||index<0||index>=38)throw new RangeError('Finite public case index');
 calls++;snapshotBuffer[0]++;
 let group,kind;
 if(index<18){group=(await textChecks(consumers,index))[0];kind='node-differential';}
 else if(index<30){group=(await profileChecks(consumers,index-18))[0];kind='profile';}
 else{group={name:extraNames[index-30],result:await extraCase(consumers,{Buffer,Readable,ReadableStream:SelectedReadableStream},index-30)};kind='public-stream-and-boundary';}
 if(!group)throw new Error('Missing finite consumer case');
 return JSON.stringify({calls,gcCalls,index,kind,...group,snapshot:snapshot(),refusals:refusalRecords(),nativeBlobInvoked:false});
}
export async function ordinaryGc(){
 gcCalls++;const operations=[],owner=Buffer.from(new Uint8Array([65]));
 async function* source(){yield new Uint8Array([0xe2]);for(let i=0;i<8;i++){const input=Buffer.from(new Uint8Array([i]));operations.push(input.toString('hex'));await Promise.resolve();}yield new Uint8Array([0x82,0xac]);}
 const value=await consumers.text(source());
 return JSON.stringify({calls,gcCalls,value,operations,ownerHex:owner.toString('hex'),applicationStrongOwnerRetained:true,decoderSpansAwaitAndNativeHex:true,vmTemporaryRootsIsolated:false,nativeBlobInvoked:false});
}
