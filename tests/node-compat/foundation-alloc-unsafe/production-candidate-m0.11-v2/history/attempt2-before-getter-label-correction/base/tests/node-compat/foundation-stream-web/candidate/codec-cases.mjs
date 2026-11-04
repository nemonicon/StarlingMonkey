// Bounded public API differential cases; shared with exact Node22 oracle.
export function errorValue(error){
  if(error===null||typeof error!=='object')return{primitive:error};
  const value={name:error.name,sentinel:error.message==='sentinel'};
  if(error.code!==undefined)value.code=error.code;
  return value;
}
function outputValue(value){
  if(typeof value==='string')return value.length>256?{stringLength:value.length,first:value[0],last:value[value.length-1]}:value;
  if(value.byteLength>256){let sum=0;for(let i=0;i<value.length;i++)sum=(Math.imul(sum,33)+value[i])>>>0;return{byteLength:value.byteLength,hash:sum};}
  return[...value];
}
export async function pipeline(codec,chunks){
  const writer=codec.writable.getWriter(),reader=codec.readable.getReader(),outputs=[];
  const closed=writer.closed.then(()=>({fulfilled:true}),error=>({error:errorValue(error)}));
  const readerClosed=reader.closed.then(()=>({fulfilled:true}),error=>({error:errorValue(error)}));
  const draining=(async()=>{try{while(true){const item=await reader.read();if(item.done)return{fulfilled:true};outputs.push(outputValue(item.value));}}
    catch(error){return{error:errorValue(error)};}})();
  const writes=[];let failed=false;
  for(const chunk of chunks){try{await writer.write(chunk);writes.push({fulfilled:true});}
    catch(error){writes.push({error:errorValue(error)});failed=true;break;}}
  let close={skipped:true};if(!failed)try{await writer.close();close={fulfilled:true};}catch(error){close={error:errorValue(error)};}
  const read=await draining,writerClosed=await closed,readClosed=await readerClosed;
  writer.releaseLock();reader.releaseLock();
  return{outputs,writes,close,read,writerClosed,readClosed};
}
export function definitions(){
  const values=[];
  function encoder(name,make){values.push({name:'encoder:'+name,kind:'encoder',make});}
  function decoder(name,chunks,options){values.push({name:'decoder:'+name,kind:'decoder',make:()=>({chunks:chunks.map(bytes=>Uint8Array.from(bytes)),options})});}
  encoder('empty',()=>({chunks:[]}));encoder('empty-writes',()=>({chunks:['','','']}));
  encoder('ascii',()=>({chunks:['a','bc']}));encoder('pair-split',()=>({chunks:['\ud83c','\udf0d']}));
  encoder('pair-whole',()=>({chunks:['🌍']}));encoder('high-empty-low',()=>({chunks:['\ud83c','','\udf0d']}));
  encoder('high-flush',()=>({chunks:['\ud800']}));encoder('low',()=>({chunks:['\udfff']}));
  encoder('high-high-low',()=>({chunks:['\ud800','\ud800','\udc00']}));
  encoder('mixed',()=>({chunks:['a\ud800b\udc00c','\udbff','\udfffz']}));
  encoder('scalars',()=>({chunks:[undefined,null,true,42,2n,Symbol('s')]}));
  encoder('coercion',trace=>({chunks:[{toString(){trace.push('toString');return 'abc';},valueOf(){trace.push('valueOf');return 1;}}]}));
  encoder('throwing-coercion',trace=>({chunks:['\ud800',{toString(){trace.push('toString');throw Error('sentinel');}}]}));
  const seeds=[[],[0x61],[0xc2,0xa2],[0xe2,0x82,0xac],[0xf0,0x9f,0x8c,0x8d],[0xef,0xbb,0xbf,0x61],
    [0xc0,0x80],[0xed,0xa0,0x80],[0xf0,0x8f,0x80,0x80],[0xf4,0x90,0x80,0x80],[0xe2,0x82],[0xff,0x61],
    [0xf0,0x9f,0x8c,0x8d,0xef,0xbb,0xbf]];
  for(let index=0;index<seeds.length;index++){
    const bytes=seeds[index];
    for(let mask=0;mask<2**Math.max(0,bytes.length-1);mask++){
      const chunks=[];let start=0;
      for(let cursor=1;cursor<=bytes.length;cursor++)if(cursor===bytes.length||(mask&2**(cursor-1))){chunks.push(bytes.slice(start,cursor));start=cursor;}
      for(const fatal of [false,true])decoder('split-'+index+'-'+mask+'-'+fatal,chunks,{fatal});
    }
  }
  decoder('bom-preserved',[[0xef],[0xbb,0xbf,0x61]],{ignoreBOM:true});
  decoder('bom-removed',[[0xef],[0xbb,0xbf,0x61]],{ignoreBOM:false});
  values.push({name:'decoder:arraybuffer-offset',kind:'decoder',make:()=>({chunks:[new DataView(Uint8Array.of(0,97,98,0).buffer,1,2),Uint8Array.of(99).buffer]})});
  values.push({name:'decoder:shadowed-fields',kind:'decoder',make:()=>{const input=Uint8Array.of(97);for(const key of ['buffer','byteOffset','byteLength'])Object.defineProperty(input,key,{get(){throw Error('sentinel');}});return{chunks:[input]};}});
  for(const value of [undefined,null,1,'abc',{}])values.push({name:'decoder:invalid-'+String(value),kind:'decoder',make:()=>({chunks:[value]})});
  return values;
}
export async function codecCases(web){
  const cases=[];
  for(const definition of definitions()){
    const trace=[],spec=definition.make(trace),Ctor=definition.kind==='encoder'?web.TextEncoderStream:web.TextDecoderStream;
    try{const instance=definition.kind==='encoder'?new Ctor():new Ctor('utf-8',spec.options);
      cases.push({name:definition.name,trace,result:await pipeline(instance,spec.chunks)});}
    catch(error){cases.push({name:definition.name,trace,error:errorValue(error)});}
  }
  return cases;
}
export async function cancellationCases(web){
  const cases=[];
  for(const name of ['TextEncoderStream','TextDecoderStream'])for(const operation of ['cancel-readable','abort-writable']){
    const instance=new web[name](),reader=instance.readable.getReader(),writer=instance.writable.getWriter(),reason={reason:operation};
    const closed=writer.closed.then(()=>false,error=>error===reason),readClosed=reader.closed.then(()=>true,error=>error===reason);
    if(operation==='cancel-readable'){
      const pending=writer.write(name==='TextEncoderStream'?'a':Uint8Array.of(97)).then(()=>false,error=>error===reason);
      await reader.cancel(reason);cases.push({name:name+':'+operation,pendingRejected:await pending,writerRejected:await closed,readerClosed:await readClosed});
    }else{
      const pending=reader.read().then(()=>false,error=>error===reason);
      await writer.abort(reason);cases.push({name:name+':'+operation,pendingRejected:await pending,writerRejected:await closed,readerClosed:await readClosed});
    }
    writer.releaseLock();reader.releaseLock();
  }
  return cases;
}
export function constructorCases(web){
  const cases=[];
  const probe=(name,callback)=>{const trace=[];try{cases.push({name,trace,value:callback(trace)});}catch(error){cases.push({name,trace,error:errorValue(error)});}};
  for(const name of ['TextEncoderStream','TextDecoderStream']){
    const Ctor=web[name],value=new Ctor();
    cases.push({name:name+':shape',value:{name:Ctor.name,length:Ctor.length,prototypeNames:Object.getOwnPropertyNames(Ctor.prototype),
      enumerable:Object.keys(Ctor.prototype),ownNames:Object.getOwnPropertyNames(value),tag:Object.prototype.toString.call(value),encoding:value.encoding}});
    probe(name+':plain',()=>Ctor());
    for(const key of Object.getOwnPropertyNames(Ctor.prototype))if(key!=='constructor'){
      const getter=Object.getOwnPropertyDescriptor(Ctor.prototype,key).get;
      for(const receiver of [undefined,{},Object.create(Ctor.prototype)])probe(name+':brand:'+key+':'+String(receiver),()=>getter.call(receiver));
    }
  }
  for(const label of ['utf-8','UTF8',' unicode-1-1-utf-8 ','\tutf-8\r',{},Symbol('s'),'rot13'])
    probe('label:'+String(label),()=>new web.TextDecoderStream(label).encoding);
  probe('label-coercion',trace=>new web.TextDecoderStream({toString(){trace.push('label');return 'utf8';}}).encoding);
  probe('options-order',trace=>{const value=new web.TextDecoderStream('utf8',{get fatal(){trace.push('fatal');return false;},get ignoreBOM(){trace.push('ignoreBOM');return true;}});
    return{encoding:value.encoding,fatal:value.fatal,ignoreBOM:value.ignoreBOM};});
  probe('flags-first-vs-public-second',trace=>{let f=0,b=0;const value=new web.TextDecoderStream('utf8',{get fatal(){trace.push('fatal');return ++f===1;},get ignoreBOM(){trace.push('ignoreBOM');return ++b===1;}});
    return{fatal:value.fatal,ignoreBOM:value.ignoreBOM};});
  probe('unknown-label-before-options',trace=>new web.TextDecoderStream('rot13',{get fatal(){trace.push('fatal');throw Error('sentinel');}}));
  probe('invalid-options-before-label',()=>new web.TextDecoderStream('rot13',1));
  probe('throwing-options',trace=>new web.TextDecoderStream('utf8',{get fatal(){trace.push('fatal');throw Error('sentinel');}}));
  return cases;
}
