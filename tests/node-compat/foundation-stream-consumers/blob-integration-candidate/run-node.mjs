// Ordinary Node host oracle only; no guest/engine/fault execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import * as buffer from 'node:buffer';
import {ordinaryCases,receiverCases,nodeOnlyCases} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const classes={Blob,File};
assert.equal(Blob,buffer.Blob);assert.equal(File,buffer.File);
const ordinary=await ordinaryCases(classes),receivers=await receiverCases(classes),nodeOnly=await nodeOnlyCases(classes);
assert.equal(ordinary.length,11);assert.equal(receivers.length,23);assert.equal(nodeOnly.length,11);
assert.deepEqual(ordinary[0].result,{emptyText:'',emptySize:0,independent:true,emptyBytes:[],oneByte:'A'});
assert.deepEqual(ordinary[3].result,{bytes:[65,66,66],size:3,text:'ABB'});
assert.deepEqual(ordinary[4].result,[0,1,2,3,4,5,2,3,4,5]);
assert.equal(ordinary[10].result.sum,2016);
for(const row of receivers){assert.equal(row.result.name,'TypeError');assert.equal(row.result.phase,/\.(arrayBuffer|bytes|text)$/.test(row.api)?'reject':'throw');}
assert.equal(nodeOnly[6].result.withinWindow,true);
const inventory={};
for(const [name,C]of Object.entries(classes)){
 const rows=[];
 for(const key of Reflect.ownKeys(C.prototype)){
  const descriptor=Object.getOwnPropertyDescriptor(C.prototype,key);
  const symbol=typeof key==='symbol';
  rows.push({key:symbol?String(key):key,keyKind:!symbol?'string':key===Symbol.toStringTag?'well-known-symbol':Symbol.keyFor(key)!==undefined?'registered-symbol':'nonregistry-reflection-only',
    ...(symbol&&Symbol.keyFor(key)!==undefined?{registryKey:Symbol.keyFor(key)}:{}),
    getter:typeof descriptor.get==='function',callable:typeof descriptor.value==='function',enumerable:descriptor.enumerable,configurable:descriptor.configurable,
    ...(typeof descriptor.value==='function'?{length:descriptor.value.length}:{}),...(key===Symbol.toStringTag?{value:descriptor.value}:{})});
 }
 inventory[name]={constructorName:C.name,constructorLength:C.length,prototypeMembers:rows,
   inheritedPrototype:name==='File'?'Blob.prototype':'Object.prototype',globalEqualsNodeBuffer:true};
}
await mkdir(new URL('node-source/',import.meta.url),{recursive:true});
const sourcePins=[];
for(const name of ['internal/blob','internal/file']){
 const text=process.binding('natives')[name];assert.equal(typeof text,'string');const path=name.replace('/','-')+'.node-v22.14.0.js';
 await writeFile(new URL('node-source/'+path,import.meta.url),text);sourcePins.push({module:name,path:'node-source/'+path,sha256:hash(text)});
}
const sources={};for(const path of ['cases.mjs','run-node.mjs'])sources[path]=hash(await readFile(new URL(path,import.meta.url)));
const result={schemaVersion:1,node:process.version,nodeBinary:process.execPath,nodeBinarySha256:hash(await readFile(process.execPath)),
 ordinary,receivers,nodeOnly,inventory,sources,nodeSources:sourcePins,
  guestSelection:{ordinary:11,receivers:23,nodeOnlyExcluded:11,reason:'No genuine Blob stream, default guest clock, broad WebIDL/coercion or known unsafe legacy path enters the future v2 gate.'},
 productionChanged:false,guestExecuted:false,scope:'Pinned Node host evidence only; corrected native candidate remains unlinked/unexecuted.'};
await writeFile(new URL('node-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({ordinary:11,receivers:23,nodeOnly:11,guestExecuted:false}));
