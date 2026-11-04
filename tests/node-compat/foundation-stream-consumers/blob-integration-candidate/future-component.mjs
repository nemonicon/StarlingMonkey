// NEW corrected-engine fixture only. The future host runner MUST verify the
// complete 304-source ancestry and all four v2 replacements before packaging.
// This file has never been componentized/executed; do not use an old engine.
import {Blob as DeferredBlob,File as DeferredFile,Buffer} from 'node:buffer';
import {ordinaryCases,receiverCases} from './cases.mjs';
const classes={Blob:globalThis.Blob,File:globalThis.File};
const snapshotBlob=new classes.Blob([new Uint8Array([65,66])]);
const snapshotFile=new classes.File(['C'],'snapshot.txt',{lastModified:17});
const snapshotText=await snapshotBlob.text();
let calls=0;
export async function run(){
 const ordinary=await ordinaryCases(classes),receivers=await receiverCases(classes),deferred=[];
 for(const [name,C]of [['Blob',DeferredBlob],['File',DeferredFile]]){
  for(const construct of [false,true]){
   let code;try{construct?Reflect.construct(C,[]):C();}catch(error){code=error.code;}
   deferred.push({name,construct,code,distinctFromGlobal:C!==classes[name]});
  }
 }
 const buffer=Buffer.from(await snapshotBlob.arrayBuffer());
 return JSON.stringify({calls:++calls,ordinary,receivers,deferred,snapshot:{text:snapshotText,
  current:await snapshotBlob.text(),fileName:snapshotFile.name,lastModified:snapshotFile.lastModified,
  fileText:await snapshotFile.text(),bufferBrand:Buffer.isBuffer(buffer),bufferBytes:[...buffer]},
  nativeBlobStreamInvoked:false,publicNodeBufferBlobFilePromoted:false});
}
