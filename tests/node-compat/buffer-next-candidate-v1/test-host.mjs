import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {createBufferModule} from './native/builtins/node-compat/buffer-facade.mjs';
import {hostKernel} from './host-kernel.mjs';
assert.equal(process.version,'v22.14.0');
const module=createBufferModule(hostKernel),B=module.Buffer,cases=[];
const bytes=x=>Array.from(x),from=(C,s)=>C.from(s);
const obs=(C,f)=>{try{return{value:f(C)}}catch(e){return{threw:e.name,code:e.code??null}}};
function test(name,fn){fn();cases.push({name,passed:true});}
function diff(name,f){const n=obs(NodeBuffer,f),b=obs(B,f);assert.deepEqual(b,n,name);cases.push({name,passed:true,node:n});}
for(const enc of ['base64','base64url','latin1','ascii','utf16le','ucs2','hex','utf8'])for(const text of ['','f','fo','foo','hello€𐀀','\0\xff\u0100\ud800'])diff('roundtrip '+enc+' '+JSON.stringify(text),C=>{const a=C.from(text,enc);return{bytes:bytes(a),out:a.toString(enc),length:C.byteLength(text,enc)};});
for(const s of ['Zg==','Zg','Zm8','Z m\nf!v','Zm9v=invalid','-___','+///','Z','A===','\u0141A','a\0GVsbG8='])diff('permissive base64 '+JSON.stringify(s),C=>bytes(C.from(s,'base64')));
for(const name of ['utf8Slice','latin1Slice','asciiSlice','ucs2Slice','hexSlice','base64Slice','base64urlSlice'])diff(name+' visible window',C=>C.from(new Uint8Array([255,128,65,0,66,0])).subarray(1,5)[name](1,3));
for(const [name,args]of [['full',[]],['offset',[1,1,4]],['truncate',[2,1,5]],['negative',[-1]],['source out',[0,9]],['end large',[0,0,999]],['zero',[0,2,1]],['fractional',[1.9,0.9,3.9]],['NaN',[NaN,NaN,NaN]]])diff('copy '+name,C=>{const a=C.from('abcdef'),b=C.alloc(5);const n=a.copy(b,...args);return{n,bytes:bytes(b)};});
diff('overlap forward',C=>{const a=C.from('abcdef');return{n:a.copy(a,2,0,4),value:a.toString()};});
diff('overlap backward windows',C=>{const a=C.from('abcdef');return{n:a.subarray(2).copy(a.subarray(1),0,0,4),value:a.toString()};});
for(const needle of ['ab','',97,new Uint8Array([98,97])])for(const offset of [undefined,0,-3,99,-99,Infinity,-Infinity,NaN])diff('search '+String(needle)+' '+String(offset),C=>{const a=C.from('ababa');return[a.indexOf(needle,offset),a.includes(needle,offset)];});
for(const args of [['hi'],['€',0,2],['€',0,3],['ab',2],['Zg==',0,5,'base64'],['abc',0,5,'hex'],['AB',0,3,'utf16le'],['x',-1],['a',9],['a',0,0]])diff('write '+JSON.stringify(args),C=>{const b=C.alloc(6);return{n:b.write(...args),bytes:bytes(b)};});
for(const args of [[7],['ab'],['',1,4],[true],[null],['ff',0,4,'hex'],['Zg==',1,5,'base64'],[new Uint8Array([8,9]),1,5]])diff('fill '+String(args),C=>{const b=C.alloc(6);const r=b.fill(...args);return{same:r===b,bytes:bytes(b)};});
diff('fill overlapping pattern',C=>{const b=C.from('abcde');b.fill(b.subarray(1,3),0,5);return b.toString();});
diff('equals exact view',C=>[C.from('abc').equals(new Uint8Array([97,98,99])),C.from('abc').equals(C.from('ab'))]);
diff('compare full/ranges',C=>[C.compare(C.from('ab'),C.from('abc')),C.from('xabc').compare(C.from('aby'),0,2,1,3)]);
test('owned copy and visible aliases',()=>{const b=B.from('YWI=','base64'),view=b.slice(1);view[0]=99;assert.equal(b.toString(),'ac');const c=B.from(b);c[0]=120;assert.equal(b[0],97);});
test('fixed backing rejected',()=>{const sab=new Uint8Array(new SharedArrayBuffer(2));assert.throws(()=>B.from('a').copy(sab),{code:'ERR_SM_NODE_UNSUPPORTED'});const r=new Uint8Array(new ArrayBuffer(2,{maxByteLength:4}));assert.throws(()=>B.from('a').equals(r),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('caller metadata getters not invoked',()=>{const v=new Uint8Array([1]);let n=0;Object.defineProperty(v,'byteLength',{get(){n++;return 1;}});assert.throws(()=>B.from('a').copy(v),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.equal(n,0);});
test('native validation facade',()=>{for(const v of [new Uint8Array(),new Uint8Array([0,127]),new Uint8Array([0xc0,0xaf]),new Uint8Array([0xed,0xa0,0x80]),new Uint8Array([0xf4,0x90,0x80,0x80]),new Uint8Array([0xe2,0x82,0xac])]){assert.equal(module.isUtf8(v),hostKernel.validate(v,false));assert.equal(module.isAscii(v),hostKernel.validate(v,true));}assert(module.isUtf8(new ArrayBuffer(0)));});
console.log(JSON.stringify({schemaVersion:1,checks:cases.length,cases,nativeCompiled:false,nativeKernelExecuted:false,guestExecuted:false,testOnlyHostBackend:true}));
