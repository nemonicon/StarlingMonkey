import {Buffer} from 'node:buffer';
import defaultExport, {StringDecoder} from 'node:string_decoder';
import * as namespace from 'node:string_decoder';
import bareDefault, * as bareNamespace from 'string_decoder';
import cjs from './native-require.cjs';
import {decoderCases} from './decoder-cases.mjs';
import expected from 'node-compat:string-decoder-oracles';

const snapshotDecoder=new StringDecoder();
const snapshotCarry=snapshotDecoder.write(Uint8Array.of(0xe2));
const snapshotTextDecoder=new TextDecoder();
const snapshotTextCarry=snapshotTextDecoder.decode(Uint8Array.of(0xe2),{stream:true});
let calls=0;
function state(decoder){return {need:decoder.lastNeed,total:decoder.lastTotal,char:[...decoder.lastChar]};}
function same(actual,wanted,label){if(JSON.stringify(actual)!==JSON.stringify(wanted))throw Error(label+': '+JSON.stringify({actual,wanted}));}
export function run(){
  const report={calls:++calls,genericCases:0,sequences:0,writes:0,mutationChecks:0};
  try{
    same(decoderCases(),expected.decoderCases,'generic decoder oracle');report.genericCases=expected.decoderCases.length;
    report.preservedOrderingDeviations=expected.deviations.length;
    for(const vector of expected.sequences){
      const decoder=new StringDecoder(vector.encoding);
      for(let i=0;i<vector.chunks.length;i++){
        const bytes=Uint8Array.from(vector.chunks[i]);
        const input=i%2?new DataView(bytes.buffer):bytes;
        same({output:decoder.write(input),state:state(decoder)},vector.expected[i],'sequence '+report.sequences+' chunk '+i);
        report.writes++;
      }
      same({output:decoder.end(),state:state(decoder)},vector.end,'sequence '+report.sequences+' end');
      same(decoder.end(Uint8Array.of(97)),vector.encoding==='hex'?'61':'a','reuse');report.sequences++;
    }
    same(Object.keys(namespace).sort(),['StringDecoder','default'],'exact native exports');
    if(namespace.default!==defaultExport||bareNamespace.default!==defaultExport||bareDefault!==defaultExport||
       namespace.StringDecoder!==StringDecoder||bareNamespace.StringDecoder!==StringDecoder||
       defaultExport.StringDecoder!==StringDecoder||cjs.canonical!==defaultExport||cjs.bare!==defaultExport)throw Error('ESM/default/alias/CJS identity');
    if(namespace.then!==undefined||namespace.missing!==undefined)throw Error('safe namespace inspection');
    if(Object.isFrozen(defaultExport))throw Error('default object should be ordinary mutable');
    const saved=defaultExport.StringDecoder;
    try{defaultExport.StringDecoder=null;if(namespace.StringDecoder!==saved)throw Error('named binding must be snapshot');}
    finally{defaultExport.StringDecoder=saved;}
    const encodingBefore=Object.getOwnPropertyDescriptor(globalThis,'encoding');
    const symbolsBefore=Object.getOwnPropertySymbols(globalThis);
    let plain;
    try{StringDecoder();}catch(error){plain=error;}
    if(!(plain instanceof TypeError))throw Error('plain invocation must reject');
    same(Object.getOwnPropertyDescriptor(globalThis,'encoding'),encodingBefore,'plain call global encoding pollution');
    same(Object.getOwnPropertySymbols(globalThis),symbolsBefore,'plain call global state-symbol pollution');
    const receiver={};
    if(StringDecoder.call(receiver,'utf8')!==undefined||receiver.encoding!=='utf8')throw Error('ordinary call receiver');
    const detachedState=new StringDecoder();detachedState.lastChar.buffer.transfer();
    for(const action of [()=>detachedState.lastChar,()=>detachedState.lastNeed,()=>detachedState.lastTotal,
      ()=>detachedState.write(Uint8Array.of(97)),()=>detachedState.end()]){
      let error;try{action();}catch(caught){error=caught;}
      if(!(error instanceof TypeError)||error.code!=='ERR_SM_NODE_DECODER_STATE')throw Error('detached private state rejection');
    }
    report.detachedInternalStateChecks=5;report.nativeAliases=2;report.commonJS=true;report.noGlobalPollution=true;
    const typed=Object.getPrototypeOf(Uint8Array.prototype),length=Object.getOwnPropertyDescriptor(typed,'length');
    const originals={Error,TypeError,RangeError,weakGet:WeakMap.prototype.get,weakSet:WeakMap.prototype.set,
      alloc:Buffer.alloc,from:Buffer.from,toString:Buffer.prototype.toString,subarray:Buffer.prototype.subarray};
    let replacedCalls=0;
    function replaced(){replacedCalls++;throw new originals.Error('replaced intrinsic');}
    try{
      Object.defineProperty(typed,'length',{get:replaced,configurable:true});
      globalThis.Error=globalThis.TypeError=globalThis.RangeError=replaced;
      WeakMap.prototype.get=WeakMap.prototype.set=replaced;
      Buffer.alloc=Buffer.from=Buffer.prototype.toString=Buffer.prototype.subarray=replaced;
      const isolated=new StringDecoder();
      same(isolated.write(Uint8Array.of(0xe2)),'','captured producer prefix');
      same(isolated.end(Uint8Array.of(0x82,0xac)),'€','captured producer suffix');
      if(isolated.lastChar.byteLength!==4||isolated.lastNeed!==0)throw new originals.Error('captured byte getters');
      let unsupported;
      try{new StringDecoder('ascii');}catch(error){unsupported=error;}
      if(!(unsupported instanceof originals.Error)||unsupported.code!=='ERR_SM_NODE_UNSUPPORTED')throw new originals.Error('captured error constructor');
    }finally{
      Object.defineProperty(typed,'length',length);
      globalThis.Error=originals.Error;globalThis.TypeError=originals.TypeError;globalThis.RangeError=originals.RangeError;
      WeakMap.prototype.get=originals.weakGet;WeakMap.prototype.set=originals.weakSet;
      Buffer.alloc=originals.alloc;Buffer.from=originals.from;
      Buffer.prototype.toString=originals.toString;Buffer.prototype.subarray=originals.subarray;
    }
    if(replacedCalls!==0)throw Error('mutable public intrinsic invoked');
    report.primordialReplacementCalls=replacedCalls;
    const decoder=new StringDecoder();
    decoder.write(Uint8Array.of(0xe2));decoder.encoding='hex';
    same(decoder.write('literal'),'literal','string passthrough');
    same(decoder.lastNeed,2,'string passthrough preserves state');
    decoder.lastChar[0]=0x61;
    same(decoder.end(),'a','legacy live byte mutation');report.mutationChecks++;
    const text=new StringDecoder();text.write(Uint8Array.of(0xe2));
    let trace=[];
    same(text.text({slice(offset){trace.push(offset);same(text.lastNeed,0,'text clears before slice');return Uint8Array.of(97);}},3),'a','observable text slice');
    same(trace,[3],'slice offset');report.mutationChecks++;
    for(const label of ['ascii','latin1','binary','base64','base64url','utf16le','utf-16le','ucs2','ucs-2']){
      let error;try{new StringDecoder(label);}catch(caught){error=caught;}
      if(error?.code!=='ERR_SM_NODE_UNSUPPORTED')throw Error('unsupported encoding '+label);
    }
    for(const label of ['rot13',' utf8 ',{},0]){
      let error;try{new StringDecoder(label);}catch(caught){error=caught;}
      if(error?.code!=='ERR_UNKNOWN_ENCODING')throw Error('unknown encoding');
    }
    if(calls===1){
      same(snapshotCarry,'','snapshot StringDecoder carry');same(snapshotDecoder.end(Uint8Array.of(0x82,0xac)),'€','resumed StringDecoder');
      same(snapshotTextCarry,'','snapshot TextDecoder carry');same(snapshotTextDecoder.decode(Uint8Array.of(0x82,0xac)),'€','resumed TextDecoder');
    }
    const previous=new TextDecoder();
    previous.decode(Uint8Array.of(0xe2),{stream:true});
    let seen=false;
    try{previous.decode(Uint8Array.of(0x82,0xac),{get stream(){throw Error('sentinel');}});}catch(error){seen=error.message==='sentinel';}
    if(!seen)throw Error('stream getter exception');same(previous.decode(Uint8Array.of(0x82,0xac)),'€','getter throw leaves decoder state');
    report.shared=typeof SharedArrayBuffer==='undefined'?'unavailable in guest':'explicitly rejected by private candidate';
    if(typeof SharedArrayBuffer!=='undefined'){
      let rejected=false;try{new TextDecoder().decode(new Uint8Array(new SharedArrayBuffer(1)));}catch(error){rejected=error instanceof TypeError;}
      if(!rejected)throw Error('private shared policy');
    }
    report.snapshotResumption=true;report.identities=true;report.passed=true;
  }catch(error){report.failure={name:error.name,message:error.message};}
  return JSON.stringify(report);
}
