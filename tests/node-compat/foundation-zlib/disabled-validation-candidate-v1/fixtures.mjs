// Finite future guest/bundler source strings; importing this file executes no guest.
export const deniedSources=Object.freeze(['node:zlib','zlib'].flatMap(id=>[
 {id,kind:'default-esm',files:{'entry.mjs':`import z from ${JSON.stringify(id)}; export function run(){return typeof z;}`} },
 {id,kind:'named-esm',files:{'entry.mjs':`import {gzipSync} from ${JSON.stringify(id)}; export function run(){return typeof gzipSync;}`} },
 {id,kind:'namespace-esm',files:{'entry.mjs':`import * as z from ${JSON.stringify(id)}; export function run(){return typeof z;}`} },
 {id,kind:'literal-cjs',files:{'entry.mjs':"import z from './literal.cjs'; export function run(){return typeof z;}",'literal.cjs':`module.exports=require(${JSON.stringify(id)});`} },
]));
export const directNativeSource="import * as z from 'node:zlib'; export function run(){return typeof z;}\n";
export const smokeSource=`import {Buffer} from 'node:buffer';
import child,* as childNamespace from 'node:child_process';
const assert=(value,message)=>{if(!value)throw new Error(message);};
function refusal(mode){try{if(mode==='new')new child.exec('unavailable');else child.exec('unavailable');throw new Error('Expected explicit refusal');}catch(error){const fields={};for(const key of ['code','module','operation','profile'])fields[key]={own:Object.hasOwn(error,key),type:typeof error[key],value:error[key]};return fields;}}
function bytes(){const backing=new ArrayBuffer(8),window=new Uint8Array(backing,2,3);window.set([1,2,3]);const shared=Buffer.from(backing,2,3),copy=Buffer.from(shared);shared[0]=9;const view=shared.subarray(1);assert(copy[0]===1&&shared[0]===9,'copy/view observable bytes');return{sharedHex:shared.toString('hex'),copyHex:copy.toString('hex'),viewHex:view.toString('hex'),sharedBacking:shared.buffer===backing,sharedOffset:shared.byteOffset,viewBacking:view.buffer===backing,viewOffset:view.byteOffset,copyIndependent:copy.buffer!==backing,globalBuffer:globalThis.Buffer===Buffer};}
const snapshot={bytes:bytes(),call:refusal('call'),construction:refusal('new')};let calls=0;
export function run(){calls++;const names=Object.keys(childNamespace).sort();return JSON.stringify({calls,snapshot,bytes:bytes(),call:refusal('call'),construction:refusal('new'),namespace:names,defaultNamed:names.filter(name=>name!=='default').every(name=>childNamespace[name]===child[name]),allCallable:names.filter(name=>name!=='default').every(name=>typeof childNamespace[name]==='function'),thenType:typeof childNamespace.then,defaultThenType:typeof child.then});}
`;
