import assert from 'node:assert/strict';
import vm from 'node:vm';
import {Buffer as NodeBuffer} from 'node:buffer';
import {createBufferModule} from './after/builtins/node-compat/buffer-facade.mjs';
import {hostKernel} from '../../../buffer-next-candidate-v1/host-kernel.mjs';
const B=createBufferModule(hostKernel).Buffer;let cases=0;
for(const view of [vm.runInNewContext('new Uint8Array([8,1,2,9]).subarray(1,3)'),(()=>{const x=new Uint8Array([1,2]);Object.setPrototypeOf(x,null);return x;})()]){const b=B.from(view);assert.deepEqual([...b],[1,2]);view[0]=99;assert.deepEqual([...b],[1,2]);cases++;}
for(const s of ['','ASCII','€','é','𐀀','\ud800'])for(const enc of ['utf8','hex','base64','latin1','utf16le']){assert.deepEqual([...B.from(s,enc)],[...NodeBuffer.from(s,enc)]);cases++;}
for(const value of [new Uint16Array(1),new Uint8ClampedArray(1),new DataView(new ArrayBuffer(1)),{[Symbol.toStringTag]:'Uint8Array'},new Proxy(new Uint8Array(1),{})]){assert.throws(()=>B.from(value),{code:'ERR_SM_NODE_UNSUPPORTED'});cases++;}
const poison=new Uint8Array([3]);let invoked=0;Object.defineProperties(poison,{buffer:{get(){invoked++;throw 1;}},byteOffset:{get(){invoked++;throw 2;}},byteLength:{get(){invoked++;throw 3;}},[Symbol.iterator]:{get(){invoked++;throw 4;}}});Object.setPrototypeOf(poison,null);assert.deepEqual([...B.from(poison)],[3]);assert.equal(invoked,0);cases++;
console.log(JSON.stringify({passed:true,cases,testOnlyHostKernel:true,nativeCompiled:false,guestExecuted:false}));
