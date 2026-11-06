// Host-only ordinary Source tests. No guest/native/compiler/Next app is run.
import assert from 'node:assert/strict';
import Module from 'node:module';
import vm from 'node:vm';
import {mkdtempSync,writeFileSync,rmSync,realpathSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {createBufferModule} from '/private/tmp/starling-node-compat/next-native-intl-build-v1/native-source/builtins/node-compat/buffer-facade.mjs';
import {hostKernel} from '../../../buffer-next-candidate-v1/host-kernel.mjs';
import {installCrossPrototypeBufferFrom,installNonAsciiCompileFallback} from './entry-fixes.mjs';
assert.equal(process.version,'v22.14.0');const originalGlobalBuffer=globalThis.Buffer;
const B=createBufferModule(hostKernel).Buffer;const oldFrom=B.from;
const ordinary=new Uint8Array([1,2,3]),foreign=vm.runInNewContext('new Uint8Array([9,4,5,8]).subarray(1,3)'),custom=new Uint8Array([6,7]);Object.setPrototypeOf(custom,null);
assert.throws(()=>oldFrom(foreign),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.throws(()=>oldFrom(custom),{code:'ERR_SM_NODE_UNSUPPORTED'});
let checks=2;const binding=installCrossPrototypeBufferFrom(B);
for(const [view,expected]of [[ordinary,[1,2,3]],[foreign,[4,5]],[custom,[6,7]]]){const value=B.from(view);assert.deepEqual(Array.from(value),expected);view[0]=99;assert.deepEqual(Array.from(value),expected);checks+=2;}
const weird=new Uint8Array([11]);Object.defineProperty(weird,Symbol.iterator,{get(){throw new Error('iterator must not run');}});Object.setPrototypeOf(weird,null);assert.deepEqual(Array.from(B.from(weird)),[11]);checks++;
for(const value of [new Uint8ClampedArray(1),new Uint16Array(1),new DataView(new ArrayBuffer(1)),{[Symbol.toStringTag]:'Uint8Array',0:1,length:1},new Proxy(new Uint8Array(1),{})]){assert.throws(()=>B.from(value),{code:'ERR_SM_NODE_UNSUPPORTED'});checks++;}
for(const value of [new Uint8Array(new SharedArrayBuffer(1)),new Uint8Array(new ArrayBuffer(1,{maxByteLength:2}))]){Object.setPrototypeOf(value,null);assert.throws(()=>B.from(value),{code:'ERR_SM_NODE_UNSUPPORTED'});checks++;}
const detached=new Uint8Array(1),detachedBacking=detached.buffer;Object.setPrototypeOf(detached,null);structuredClone(detachedBacking,{transfer:[detachedBacking]});assert.throws(()=>B.from(detached),{code:'ERR_SM_NODE_UNSUPPORTED'});checks++;
binding.restore();assert.equal(B.from,oldFrom);assert.equal(globalThis.Buffer,originalGlobalBuffer);checks+=2;
const root=realpathSync(mkdtempSync(join(tmpdir(),'next-cjs-utf16-host-'))),filename=join(root,'module.js'),child=join(root,'child.js');writeFileSync(child,'module.exports={parent:module.parent.id,value:7};');
const originalCompile=Module.prototype._compile;let nativeCalls=0,functionCalls=0;
Module.prototype._compile=function(...args){nativeCalls++;return Reflect.apply(originalCompile,this,args);};
const counted=Module.prototype._compile;
function create(){const mod=new Module(filename);mod.filename=filename;mod.paths=Module._nodeModulePaths(root);return mod;}
function run(mod,source){return mod._compile(source,filename);}
const restore=installNonAsciiCompileFallback(Module,function(...args){functionCalls++;return Reflect.apply(Function,undefined,args);});
try{
 const a=create();run(a,'module.exports={ascii:1};');assert.equal(nativeCalls,1);assert.equal(functionCalls,0);checks++;
 for(const literal of ['€','é','𐀀','\ud800']){const mod=create();run(mod,'module.exports='+JSON.stringify(literal)+';');assert.equal(mod.exports,literal);checks++;}
 const source="module.exports={value:'€',receiver:this===exports,file:__filename,dir:__dirname,cache:require.cache===require('node:module')._cache,extensions:require.extensions===require('node:module')._extensions,resolve:require.resolve('./child.js'),paths:Array.isArray(require.resolve.paths('./child.js')),child:require('./child.js')};";
 delete Module._cache[child];const actual=create();run(actual,source);assert.deepEqual(actual.exports,{value:'€',receiver:true,file:filename,dir:dirname(filename),cache:true,extensions:true,resolve:child,paths:true,child:{parent:actual.id,value:7}});assert.equal(actual.children[0],Module._cache[child]);checks+=2;
 const again=create();run(again,"module.exports={value:require('./child.js'),unicode:'é'};");assert.equal(again.exports.value,actual.exports.child);checks++;
 const reassigned=create();run(reassigned,"exports.a='é';module.exports={old:exports,changed:true};");assert.deepEqual(reassigned.exports,{old:{a:'é'},changed:true});checks++;
 const hashbang=create();run(hashbang,"#!/usr/bin/env node\nmodule.exports='€';");assert.equal(hashbang.exports,'€');checks++;
 const sentinel={tag:'original'};const throwing=create();throwing.sentinel=sentinel;assert.throws(()=>run(throwing,"/*é*/throw module.sentinel"),e=>e===sentinel);checks++;
 for(const bad of ['/app/bad\nname.js','/app/bad\rname.js','/app/bad\0name.js','/app/bad\u2028name.js','relative.js']){assert.throws(()=>create()._compile("module.exports='é';",bad),{code:'ERR_INVALID_ARG_VALUE'});checks++;}
 assert.throws(()=>run(create(),"module.exports='é'; let = ;"),SyntaxError);checks++;
 // ASCII child + ASCII JSON-escaped lone surrogate also delegate natively.
 assert.equal(nativeCalls,3);assert.equal(functionCalls,9);checks++;
}finally{restore.restore();assert.equal(Module.prototype._compile,counted);Module.prototype._compile=originalCompile;delete Module._cache[child];rmSync(root,{recursive:true,force:true});}
console.log(JSON.stringify({passed:true,checks,hostNodeOnly:true,testOnlyHostBufferKernel:true,hostGlobalBufferUnchanged:globalThis.Buffer===originalGlobalBuffer,nativeCompileCalls:nativeCalls,functionFallbackCalls:functionCalls,guestExecuted:false,nativeKernelCompiled:false}));
