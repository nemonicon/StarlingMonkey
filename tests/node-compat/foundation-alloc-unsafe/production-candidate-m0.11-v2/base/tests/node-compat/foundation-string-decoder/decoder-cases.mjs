// Ordinary API cases only. This module is permitted in the FIXED private
// candidate component; never use it to probe the old native decoder.
export function decoderCases() {
  const results=[];
  function probe(name,callback){
    const trace=[];
    try{results.push({name,value:callback(trace),trace});}
    catch(error){results.push({name,error:{name:error.name,sentinel:error.message==='sentinel'},trace});}
  }
  probe('undefined',()=>new TextDecoder().decode());
  probe('zero-u8',()=>new TextDecoder().decode(new Uint8Array(0)));
  probe('zero-ab',()=>new TextDecoder().decode(new ArrayBuffer(0)));
  probe('ascii-ab',()=>new TextDecoder().decode(Uint8Array.of(97,98,99).buffer));
  probe('u8-offset',()=>new TextDecoder().decode(Uint8Array.of(0,97,98,99,0).subarray(1,4)));
  probe('dataview-offset',()=>new TextDecoder().decode(new DataView(Uint8Array.of(0,97,98,99,0).buffer,1,3)));
  for(const Type of [Uint8Array,Uint8ClampedArray,Int8Array,Uint16Array,Int16Array,Uint32Array,Int32Array,Float32Array,Float64Array,BigInt64Array,BigUint64Array]){
    probe('view-'+Type.name,()=>new TextDecoder().decode(new Type(new Uint8Array(32).fill(97).buffer,8,16/Type.BYTES_PER_ELEMENT)));
  }
  probe('shadowed-properties',()=>{
    const input=Uint8Array.of(97,98,99);
    for(const key of ['buffer','byteOffset','byteLength','length'])Object.defineProperty(input,key,{get(){throw Error('sentinel');}});
    return new TextDecoder().decode(input);
  });
  probe('stream-getter-mutate',trace=>{
    const input=Uint8Array.of(97,98,99);
    return new TextDecoder().decode(input,{get stream(){trace.push('stream');input.fill(122);return false;}});
  });
  probe('stream-getter-throw',trace=>new TextDecoder().decode(Uint8Array.of(97),{get stream(){trace.push('stream');throw Error('sentinel');}}));
  probe('invalid-input-before-stream-getter',trace=>new TextDecoder().decode('abc',{get stream(){trace.push('stream');throw Error('sentinel');}}));
  probe('undefined-stream-getter',trace=>new TextDecoder().decode(undefined,{get stream(){trace.push('stream');return false;}}));
  probe('null-options',()=>new TextDecoder().decode(Uint8Array.of(97),null));
  probe('getter-detach-view',trace=>{
    const input=Uint8Array.of(97,98,99);
    return new TextDecoder().decode(input,{get stream(){trace.push('stream');input.buffer.transfer();return false;}});
  });
  probe('getter-detach-arraybuffer',trace=>{
    const input=Uint8Array.of(97,98,99).buffer;
    return new TextDecoder().decode(input,{get stream(){trace.push('stream');input.transfer();return false;}});
  });
  probe('already-detached-view',()=>{
    const input=Uint8Array.of(97,98,99);input.buffer.transfer();return new TextDecoder().decode(input);
  });
  probe('getter-shrink-fixed',trace=>{
    const input=new ArrayBuffer(8,{maxByteLength:16});new Uint8Array(input).fill(97);
    const view=new Uint8Array(input,4,4);
    return new TextDecoder().decode(view,{get stream(){trace.push('stream');input.resize(2);return false;}});
  });
  probe('getter-shrink-tracking',trace=>{
    const input=new ArrayBuffer(8,{maxByteLength:16});new Uint8Array(input).fill(97);
    const view=new Uint8Array(input);
    return new TextDecoder().decode(view,{get stream(){trace.push('stream');input.resize(2);return false;}});
  });
  probe('getter-grow-tracking',trace=>{
    const input=new ArrayBuffer(2,{maxByteLength:16});new Uint8Array(input).fill(97);
    const view=new Uint8Array(input);
    return new TextDecoder().decode(view,{get stream(){trace.push('stream');input.resize(4);return false;}});
  });
  probe('getter-shrink-arraybuffer',trace=>{
    const input=new ArrayBuffer(8,{maxByteLength:16});new Uint8Array(input).fill(97);
    return new TextDecoder().decode(input,{get stream(){trace.push('stream');input.resize(2);return false;}});
  });
  for(const ignoreBOM of [false,true])probe('bom-'+ignoreBOM,()=>{
    const decoder=new TextDecoder('utf-8',{ignoreBOM});
    return [decoder.decode(Uint8Array.of(0xef),{stream:true}),decoder.decode(Uint8Array.of(0xbb,0xbf,97),{stream:true}),decoder.decode(),decoder.decode(Uint8Array.of(0xef,0xbb,0xbf,98))];
  });
  probe('utf8-stream-flush-reuse',()=>{
    const decoder=new TextDecoder();
    return [decoder.decode(Uint8Array.of(0xe2),{stream:true}),decoder.decode(Uint8Array.of(0x82),{stream:true}),decoder.decode(Uint8Array.of(0xac)),decoder.decode(Uint8Array.of(0xf0),{stream:true}),decoder.decode(),decoder.decode(Uint8Array.of(97))];
  });
  probe('fatal-malformed',()=>new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.of(0xff)));
  probe('fatal-incomplete-flush',()=>{
    const decoder=new TextDecoder('utf-8',{fatal:true});decoder.decode(Uint8Array.of(0xe2),{stream:true});return decoder.decode();
  });
  probe('label-coercion',trace=>new TextDecoder({toString(){trace.push('label');return ' UTF-8 ';}}).encoding);
  probe('label-throw-before-options',trace=>new TextDecoder({toString(){trace.push('label');throw Error('sentinel');}},{get fatal(){trace.push('fatal');return false;}}).encoding);
  probe('constructor-getter-order',trace=>{
    const decoder=new TextDecoder('utf-8',{get fatal(){trace.push('fatal');return false;},get ignoreBOM(){trace.push('ignoreBOM');return true;}});
    return {encoding:decoder.encoding,fatal:decoder.fatal,ignoreBOM:decoder.ignoreBOM};
  });
  probe('constructor-throw-fatal',trace=>new TextDecoder('utf-8',{get fatal(){trace.push('fatal');throw Error('sentinel');},get ignoreBOM(){trace.push('ignoreBOM');return false;}}));
  probe('constructor-throw-ignoreBOM',trace=>new TextDecoder('utf-8',{get fatal(){trace.push('fatal');return false;},get ignoreBOM(){trace.push('ignoreBOM');throw Error('sentinel');}}));
  return results;
}
