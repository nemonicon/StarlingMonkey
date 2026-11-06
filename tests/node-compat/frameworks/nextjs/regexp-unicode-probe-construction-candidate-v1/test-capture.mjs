// Benign host DATA tests only. Does not import entry.mjs or componentize.
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {captureComponentReturn,typedOwnGraph} from './capture.mjs';
const root=await mkdtemp(join(tmpdir(),'next-construction-capture-'));
let checks=0;
async function directory(name){const p=join(root,name);await mkdir(p);return p;}
const bytes=new Uint8Array([0,97,115,109,1,0,0,0]);
const returned={component:bytes,imports:[['wasi:http/types@0.2.10','incoming-request']],debug:undefined};
const good=await directory('good'),artifacts=await captureComponentReturn(returned,good);
assert.deepEqual(await readFile(artifacts.component.path),Buffer.from(bytes));checks++;
assert.deepEqual(JSON.parse(await readFile(artifacts.returnedImports.path,'utf8')),returned.imports);checks++;
const shape=JSON.parse(await readFile(artifacts.returnedOwnShape.path,'utf8'));
assert.deepEqual(shape.properties.map(p=>p.key.string),['component','imports','debug']);checks++;
assert.equal(shape.properties.find(p=>p.key.string==='debug').value.type,'undefined');checks++;
assert.equal(shape.properties.find(p=>p.key.string==='component').value.file.sha256,artifacts.component.sha256);checks++;
await assert.rejects(captureComponentReturn(returned,good),/EEXIST/);checks++;
let getterCalls=0;
const accessor={component:bytes,debug:undefined};Object.defineProperty(accessor,'imports',{get(){getterCalls++;throw new Error('must not execute');},enumerable:true});
const access=await directory('accessor');await assert.rejects(captureComponentReturn(accessor,access),/not own DATA/);checks++;
assert.equal(getterCalls,0);assert((await readdir(access)).includes('returned-component.wasm'));checks++;
assert.equal(JSON.parse(await readFile(join(access,'returned-own-shape.json'),'utf8')).properties.find(p=>p.key.string==='imports').kind,'accessor');checks++;
for(const [id,imports]of [['undefined',undefined],['malformed',[[1,'x']]],['sparse',new Array(2)]]){
  const p=await directory(id);await assert.rejects(captureComponentReturn({component:bytes,imports,debug:undefined},p));
  assert.deepEqual(await readFile(join(p,'returned-component.wasm')),Buffer.from(bytes));
  assert((await readdir(p)).includes('returned-own-shape.json'));checks++;
}
for(const value of [undefined,null,0,false]){const p=await directory('primitive-'+String(value));await assert.rejects(captureComponentReturn(value,p),/own Uint8Array/);assert((await readdir(p)).includes('returned-own-shape.json'));checks++;}
const odd={x:undefined,negativeZero:-0,nan:NaN,infinity:Infinity};odd.self=odd;
const own=typedOwnGraph(odd);assert.equal(own.properties.find(p=>p.key.string==='self').value.type,'reference');checks++;
assert.equal(own.properties.find(p=>p.key.string==='negativeZero').value.value,'-0');checks++;
console.log(JSON.stringify({passed:true,checks,scratch:root,componentizeOrEngineInvoked:false}));
