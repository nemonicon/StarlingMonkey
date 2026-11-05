// Extract only the actual synchronous descriptor function; never import/bootstrap action.
import {readFile} from 'node:fs/promises';
import {resolve,isAbsolute} from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=await readFile(new URL('./bootstrap.mjs',import.meta.url),'utf8'),start=source.indexOf('export function captureDescriptor('),end=source.indexOf('\nasync function regular(',start);assert(start>0&&end>start);
const code=source.slice(start,end).replace('export function','function'),context=vm.createContext({resolve,isAbsolute,need:(v,m)=>assert(v,m)});vm.runInContext(code+';this.capture=captureDescriptor;',context,{timeout:1000});const capture=context.capture,checks=[];
function pass(name,fn){fn();checks.push({name,passed:true});}
const row={path:'/Users/dan/dev/StarlingMonkey/source.json',sha256:'a'.repeat(64),bytes:4};
pass('genuine synchronous descriptor capture',()=>{const got=capture(row);assert.equal(got.path,row.path);assert.equal(got.sha256,row.sha256);assert.equal(got.bytes,4);assert(Object.isFrozen(got));});
pass('caller mutation cannot change private primitives',()=>{const input={...row},captured=capture(input);input.path='/changed';input.sha256='b'.repeat(64);input.bytes=99;assert.equal(captured.path,row.path);assert.equal(captured.sha256,row.sha256);assert.equal(captured.bytes,4);});
for(const path of ['relative','/a/../b','/a//b','/a\\b','/a\0b'])pass('reject canonical path '+JSON.stringify(path),()=>assert.throws(()=>capture({...row,path})));
for(const value of [null,undefined])pass('NULL refuses before file/helper access '+String(value),()=>assert.throws(()=>capture(value)));
for(const bytes of [-1,NaN,Infinity,1.5,'4'])pass('reject nonfinite/inexact bytes '+String(bytes),()=>assert.throws(()=>capture({...row,bytes})));
pass('bad hash refuses',()=>assert.throws(()=>capture({...row,sha256:'latest'})));
process.stdout.write(JSON.stringify({schemaVersion:1,state:'EXTRACTED_ACTUAL_NODE_DESCRIPTOR_PURE_CHECKS_PASSED_V1',checks,count:checks.length,ownerModuleImported:false,bootstrapInvoked:false,exportInvoked:false,helperOrEngineOrGuestInvoked:false})+'\n');
