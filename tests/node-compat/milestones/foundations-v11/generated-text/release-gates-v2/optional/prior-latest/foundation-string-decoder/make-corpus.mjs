import assert from 'node:assert/strict';
import {StringDecoder} from 'node:string_decoder';
import {Buffer} from 'node:buffer';
import {writeFile} from 'node:fs/promises';
import {decoderCases} from './decoder-cases.mjs';
assert.equal(process.version,'v22.14.0');
const sequences=[];
function state(decoder){return {need:decoder.lastNeed,total:decoder.lastTotal,char:[...decoder.lastChar]};}
function add(encoding,chunks){
  const decoder=new StringDecoder(encoding);
  const expected=chunks.map(chunk=>({output:decoder.write(Uint8Array.from(chunk)),state:state(decoder)}));
  sequences.push({encoding,chunks,expected,end:{output:decoder.end(),state:state(decoder)}});
}
for(const hex of ['','24','c2a2','e282ac','f09f8c8d','efbbbf','eda0b5edb08d','c0','c080','f08f8080','f69bd1','f4bde5','e2fbcc01','f0fb00','cce2b8b8','e2b8ccb8','ccb8cdb9']){
  const data=Buffer.from(hex,'hex');
  for(let cuts=0;cuts<2**Math.max(0,data.length-1);cuts++){
    const chunks=[];let start=0;
    for(let i=1;i<=data.length;i++)if(i===data.length||(cuts&2**(i-1))){chunks.push([...data.subarray(start,i)]);start=i;}
    add('utf8',chunks);add('hex',chunks);
  }
}
// Every individual byte in both positions; malformed and valid split tails.
for(let byte=0;byte<256;byte++)for(const chunks of [[[byte]],[[byte],[0x80]],[[0xe2],[byte]]])add('utf8',chunks);
let seed=0x5eed1234;
function random(){return seed=Math.imul(seed,1664525)+1013904223>>>0;}
for(let i=0;i<2000;i++){
  const chunks=[];
  for(let j=0,count=random()%6+1;j<count;j++){
    const bytes=[];for(let k=0,length=random()%17;k<length;k++)bytes.push(random()&255);
    chunks.push(bytes);
  }
  add(i%2?'utf8':'hex',chunks);
}
const nodeCases=decoderCases(),profileCases=structuredClone(nodeCases),deviations=[];
for(const [name,profile,reason] of [
  ['invalid-input-before-stream-getter',{error:{name:'TypeError',sentinel:false},trace:[]},'Existing Starling type-first validation is preserved; Node reads stream before rejecting input.'],
  ['constructor-getter-order',{trace:['fatal','ignoreBOM']},'Existing Starling constructor reads each option once; Node22 reads both twice.']
]){
  const index=nodeCases.findIndex(entry=>entry.name===name);assert(index>=0);
  const node=nodeCases[index];
  if(name==='invalid-input-before-stream-getter')assert.deepEqual(node.trace,['stream']);
  else assert.deepEqual(node.trace,['fatal','ignoreBOM','ignoreBOM','fatal']);
  profileCases[index]={...profileCases[index],...profile};
  deviations.push({name,node,profile:profileCases[index],reason});
}
const corpus={node:process.version,decoderCases:profileCases,nodeDecoderCases:nodeCases,deviations,sequences};
await writeFile(new URL('./component-corpus.json',import.meta.url),JSON.stringify(corpus)+'\n');
console.log(JSON.stringify({sequences:sequences.length,genericCases:corpus.decoderCases.length,writes:sequences.reduce((sum,value)=>sum+value.chunks.length,0)}));
