import assert from 'node:assert/strict';
import * as consumers from 'node:stream/consumers';
import { Buffer, Blob as BufferBlob } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { textChecks, blobChecks } from './node-checks.mjs';
assert.equal(process.version,'v22.14.0');
const hash=value=>createHash('sha256').update(value).digest('hex');
const names=Object.keys(consumers).sort();assert.deepEqual(names,['arrayBuffer','blob','buffer','default','json','text']);
const inventory={module:'node:stream/consumers',aliases:['stream/consumers'],exports:names,
  defaultType:typeof consumers.default,defaultKeys:Object.keys(consumers.default),defaultFrozen:Object.isFrozen(consumers.default),
  defaultPrototype:Object.getPrototypeOf(consumers.default)===Object.prototype?'Object.prototype':'other',
  functions:Object.fromEntries(names.filter(name=>name!=='default').map(name=>[name,{name:consumers[name].name,length:consumers[name].length,
    constructorName:consumers[name].constructor.name,defaultIdentity:consumers[name]===consumers.default[name],ownKeys:Reflect.ownKeys(consumers[name]).map(String)}])),
  namespace:{prototype:Object.getPrototypeOf(consumers)===null?'null':'other',toString:Object.prototype.toString.call(consumers),then:typeof consumers.then},
  globalBlobEqualsBufferBlob:globalThis.Blob===BufferBlob,globalBufferIdentity:globalThis.Buffer===Buffer};
const text=await textChecks(consumers),blob=await blobChecks(consumers);
const report={schema:1,proposalVersion:'stream-consumers-source-v1',node:process.version,nodeOnly:true,installed:false,inventory,text,blob,
  sources:{'node-checks.mjs':hash(await readFile(new URL('./node-checks.mjs',import.meta.url))),'run-node.mjs':hash(await readFile(fileURLToPath(import.meta.url)))},
  nodeEmbeddedSources:Object.fromEntries(['stream/consumers','internal/blob','internal/encoding'].map(name=>[name,{sha256:hash(process.binding('natives')[name]),bytes:Buffer.byteLength(process.binding('natives')[name])}])),
  scope:'Small ordinary bounded Node22 oracle cases. No guest/native Blob probe; no getter/detach/shared/OOM lifetime test; no classic stream or production support claim.'};
await writeFile(new URL('./node-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({exports:names,textGroups:text.length,blobGroups:blob.length,nodeOnly:true,installed:false}));
