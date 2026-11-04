import {Buffer} from 'node:buffer';
import path from 'node:path';
import {EventEmitter} from 'node:events';
import {runBufferCases} from './smoke-cases.mjs';
const snapshot=Buffer.from('snapshot\u00e9'),backing=snapshot.buffer;
const snapshotHex=snapshot.toString('hex');
let calls=0;
export async function run(){
  await Promise.resolve();
  const child=await import('node:child_process');
  let error;try{child.spawn();}catch(caught){error=caught;}
  if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||error.module!=='node:child_process'||error.operation!=='spawn')throw new Error('unsupported callable semantics');
  const emitter=new EventEmitter();let eventCalls=0;emitter.once('x',()=>eventCalls++);emitter.emit('x');emitter.emit('x');
  if(eventCalls!==1||path.posix.normalize('/a/../b//c')!=='/b/c')throw new Error('selected native module behavior');
  if(snapshot.buffer!==backing||snapshot.toString('hex')!==snapshotHex)throw new Error('snapshot output changed');
  return JSON.stringify({calls:++calls,buffer:runBufferCases(Buffer),snapshotHex,backingIdentityPreserved:true,unsupportedCode:error.code,firstDeployedDynamicImport:true,eventCalls,path:'/b/c'});
}
export function directU32(value){return value;}
export function constantMax(){return 0xffffffff;}
export function directS32(value){return value;}
export function directF32(value){return value;}
export function directF64(value){return value;}
export function directU64(value){return value;}
export function directS64(value){return value;}
export function echoString(value){return value;}
export function echoBytes(value){return new Uint8Array(value);}
export function echoRecord(value){return value;}
export function resultU32(ok,value){if(ok)return value;throw value;}
