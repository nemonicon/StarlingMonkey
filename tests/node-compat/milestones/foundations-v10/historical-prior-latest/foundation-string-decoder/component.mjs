import {Buffer} from 'node:buffer';
import {createStringDecoderModule} from './prototype.mjs';
import {decoderCases} from './decoder-cases.mjs';
import expected from 'node-compat:string-decoder-oracles';
const {StringDecoder,default:namespace}=createStringDecoderModule(Buffer);
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
    if(namespace.StringDecoder!==StringDecoder)throw Error('default binding identity');
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
