import bufferDefault,* as nativeBuffer from 'node:buffer';
import * as consumers from './prototype.mjs';
import {textChecks} from 'node-compat:consumers-text-checks';
import {profileChecks} from './component-checks.mjs';
const {Buffer}=nativeBuffer;
const backing=new ArrayBuffer(7),view=new Uint8Array(backing,2,3);view.set([65,66,67]);
const snapshotBuffer=Buffer.from(new Uint8Array([17,18]));
const snapshotText=await consumers.text([view,'!']);
const snapshotFlushed=await consumers.text([new Uint8Array([0xe2])]);
let calls=0;
function check(value,message){if(!value)throw new Error('Consumer component: '+message);}
export async function run(){
  try{
    const cases=await textChecks(consumers),profile=await profileChecks(consumers);
    const fresh=await consumers.text([new Uint8Array([0x82,0xac])]);
    check(fresh==='\ufffd\ufffd'&&snapshotFlushed==='\ufffd','decoder state not retained between calls');
    let rejected=false;try{await consumers.json(['{']);}catch(error){rejected=error.name==='SyntaxError';}
    const afterJsonError=await consumers.json(['{"ok":true}']);
    check(rejected&&afterJsonError.ok===true,'fresh JSON error state');
    const id=String.fromCharCode(98,117,102,102,101,114),bare=await import(id);
    check(bare.Buffer===Buffer&&bare.default===bufferDefault&&globalThis.Buffer===Buffer,'actual native Buffer aliases');
    check(Buffer.isBuffer(snapshotBuffer)&&snapshotBuffer.buffer.byteLength===2&&snapshotBuffer.byteOffset===0,'snapshot native Buffer ownership');
    check(view.buffer===backing&&view.byteOffset===2&&snapshotText==='ABC!','snapshot views/text');
    snapshotBuffer[0]++;
    return JSON.stringify({calls:++calls,cases,profile,snapshot:{text:snapshotText,flushed:snapshotFlushed,
      byte:snapshotBuffer[0],bufferBrand:Buffer.isBuffer(snapshotBuffer),viewOffset:view.byteOffset,backingBytes:backing.byteLength},
      state:{freshDecoderAfterSnapshot:true,freshJsonAfterError:afterJsonError.ok},
      nativeBuffer:true,nativeBlobInvoked:false,
      nativeReadableStream:{constructor:typeof ReadableStream,asyncIterator:typeof ReadableStream.prototype[Symbol.asyncIterator],values:typeof ReadableStream.prototype.values,from:typeof ReadableStream.from},
      scope:'Isolated bundled text/json facade over actual native decoder. Plain iterator fixtures only; no native/classic Stream acceptance or installed consumer namespace.'});
  }catch(error){return JSON.stringify({failure:{name:error.name,code:error.code,message:error.message,stack:error.stack}});}
}
