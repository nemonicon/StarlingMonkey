function errorValue(error){return{name:error?.name,...(error?.code!==undefined?{code:error.code}:{})};}
async function outcome(invoke){try{return{value:await invoke()};}catch(error){return{error:errorValue(error)};}}
async function consume(stream){const reader=stream.getReader(),values=[];try{for(;;){const entry=await reader.read();if(entry.done)break;values.push(entry.value);}}finally{reader.releaseLock();}return values;}
export async function iterationCases(web){
  const S=web.ReadableStream,cases=[];
  async function test(name,run){cases.push({name,...await outcome(run)});}
  await test('from-array',()=>consume(S.from([1,2,3])));
  await test('from-string-unicode',()=>consume(S.from('A🌍é')));
  await test('from-sync-generator',()=>consume(S.from((function*(){yield 1;yield 2;return 99;})())));
  await test('from-async-generator',()=>consume(S.from((async function*(){yield 1;await 0;yield 2;})())));
  await test('from-sync-promised-value',()=>consume(S.from([Promise.resolve(7)])));
  await test('from-async-promised-value',async()=>{
    const stream=S.from({[Symbol.asyncIterator](){return{next(){return Promise.resolve({done:false,value:Promise.resolve(8)});}};}});
    const reader=stream.getReader(),entry=await reader.read();const promised=typeof entry.value?.then==='function';
    const value=await entry.value;await reader.cancel();reader.releaseLock();return{promised,value};
  });
  for(const[name,value]of [['null',null],['undefined',undefined],['plain',{}],['number',1],['sync-null',{[Symbol.iterator]:null}],
    ['async-number',{[Symbol.asyncIterator]:1}],['iterator-number',{[Symbol.iterator](){return 1;}}],
    ['iterator-function',{[Symbol.asyncIterator](){return function f(){};}}]])
    await test('from-invalid-'+name,()=>S.from(value));
  await test('from-async-next-number',()=>consume(S.from({[Symbol.asyncIterator](){return{next(){return 1;}};}})));
  await test('from-async-next-promised-number',()=>consume(S.from({[Symbol.asyncIterator](){return{next(){return Promise.resolve(1);}};}})));
  await test('from-sync-next-number',()=>consume(S.from({[Symbol.iterator](){return{next(){return 1;}};}})));
  await test('from-throwing-next',async()=>{
    const reason={tag:'next'},source=S.from({[Symbol.asyncIterator](){return{next(){throw reason;}};}}),reader=source.getReader();
    const handled=reader.closed.catch(error=>error===reason);let same=false;try{await reader.read();}catch(error){same=error===reason;}
    await handled;reader.releaseLock();return{same,locked:source.locked};
  });
  await test('from-no-eager-pull',async()=>{
    const trace=[];let index=0;const stream=S.from({[Symbol.asyncIterator](){trace.push('iterator');return{
      next(){trace.push('next');return Promise.resolve(index++?{done:true}:{value:3,done:false});},
      return(reason){trace.push('return:'+reason);return{done:true};}};}});
    await Promise.resolve();await Promise.resolve();const before=trace.slice(),reader=stream.getReader();
    const first=await reader.read();await Promise.resolve();const after=trace.slice();await reader.cancel('stop');reader.releaseLock();
    return{before,first,after,trace};
  });
  await test('from-next-captured',async()=>{
    let gets=0,index=0;const iterator={get next(){gets++;return function(){return index++?{done:true}:{value:9,done:false};};}};
    const stream=S.from({[Symbol.asyncIterator](){return iterator;}});Object.defineProperty(iterator,'next',{value(){throw Error('changed');}});
    return{values:await consume(stream),gets};
  });
  await test('from-sync-next-get-order',async()=>{
    let gets=0,index=0;const trace=[];const stream=S.from({[Symbol.iterator](){trace.push('iterator');return{
      get next(){trace.push('next-get');gets++;return function(){return index++?{done:true}:{value:9,done:false};};}};}});
    const before=trace.slice(),values=await consume(stream);return{before,trace,gets,values};
  });
  for(const[name,result]of [['number',1],['null',null],['undefined',undefined],['object',{done:true}],['promise-object',Promise.resolve({done:true})]])
    await test('from-cancel-return-'+name,async()=>{
      const reason={why:1};let same=false;const stream=S.from({[Symbol.asyncIterator](){return{next(){return{value:1,done:false};},return(value){same=value===reason;return result;}};}});
      const reader=stream.getReader();await reader.read();const cancelled=await outcome(()=>reader.cancel(reason));reader.releaseLock();return{same,cancelled,locked:stream.locked};
    });
  await test('from-cancel-return-rejection',async()=>{
    const reason={why:2},stream=S.from({[Symbol.asyncIterator](){return{next(){return{value:1,done:false};},return(){return Promise.reject(reason);}};}});
    const reader=stream.getReader();await reader.read();let same=false;try{await reader.cancel();}catch(error){same=error===reason;}reader.releaseLock();return{same,locked:stream.locked};
  });
  await test('from-static-this-ignored',()=>consume(S.from.call(null,[4])));
  await test('from-async-method-precedence',async()=>{
    const trace=[];let done=false;const values=await consume(S.from({
      get [Symbol.iterator](){trace.push('sync');throw Error('wrong');},
      [Symbol.asyncIterator](){trace.push('async');return{next(){if(done)return{done:true};done=true;return{value:5,done:false};}};},
    }));return{trace,values};
  });
  await test('from-null-async-fallback',()=>consume(S.from({[Symbol.asyncIterator]:null,*[Symbol.iterator](){yield 6;}})));
  await test('from-sync-generator-cancel-finally',async()=>{
    const trace=[];const stream=S.from((function*(){try{yield 1;yield 2;}finally{trace.push('finally');}})());
    const reader=stream.getReader(),first=await reader.read();await reader.cancel('done');reader.releaseLock();return{first,trace};
  });
  await test('from-serial-pulls',async()=>{
    let finish,index=0,active=0,maxActive=0;const trace=[];
    const stream=S.from({[Symbol.asyncIterator](){return{next(){
      active++;maxActive=Math.max(maxActive,active);trace.push('next:'+index);
      if(index++===0)return new Promise(resolve=>{finish=()=>{active--;resolve({value:1,done:false});};});
      active--;return{done:true};
    }};}}),reader=stream.getReader();
    const first=reader.read(),second=reader.read();
    await Promise.resolve();await Promise.resolve();const before=trace.slice();finish();
    const results=await Promise.all([first,second]);reader.releaseLock();return{before,trace,results,maxActive};
  });
  for(const field of ['done','value'])await test('from-throwing-result-'+field,async()=>{
    const reason={},entry={done:false,value:1};Object.defineProperty(entry,field,{get(){throw reason;}});
    const stream=S.from({[Symbol.asyncIterator](){return{next(){return entry;}};}}),reader=stream.getReader();
    let same=false;try{await reader.read();}catch(error){same=error===reason;}reader.releaseLock();return{same,locked:stream.locked};
  });
  await test('from-throwing-return-getter',async()=>{
    const reason={},stream=S.from({[Symbol.asyncIterator](){return{next(){return{value:1};},get return(){throw reason;}};}}),reader=stream.getReader();
    await reader.read();let same=false;try{await reader.cancel();}catch(error){same=error===reason;}reader.releaseLock();return{same};
  });
  await test('from-new-rejected',()=>new S.from([]));

  for(const[name,options]of [['undefined',undefined],['null',null],['false',false],['zero',0],['string','x'],['array',[]],['function',()=>{}]])
    await test('values-options-'+name,async()=>{
      const stream=new S({start(c){c.close();}}),iterator=stream.values(options),first=await iterator.next();return{first,locked:stream.locked};
    });
  await test('values-invalid-receiver-before-options',()=>{
    let reads=0;try{S.prototype.values.call({}, {get preventCancel(){reads++;throw Error();}});}catch(error){return{error:errorValue(error),reads};}
  });
  await test('values-prototype-rejected',()=>S.prototype.values.call(S.prototype));
  await test('values-locked-after-getter',async()=>{
    const stream=new S(),reader=stream.getReader(),trace=[];
    const result=await outcome(()=>stream.values({get preventCancel(){trace.push('get');return false;}}));
    reader.releaseLock();await stream.cancel();return{result,trace};
  });
  await test('values-throwing-options-unlocked',async()=>{
    const reason={},stream=new S();let same=false;
    try{stream.values({get preventCancel(){throw reason;}});}catch(error){same=error===reason;}
    const locked=stream.locked;await stream.cancel();return{same,locked};
  });
  await test('values-close-and-next',async()=>{
    const stream=new S({start(c){c.enqueue(1);c.close();}}),iterator=stream.values();
    const lockedBefore=stream.locked,one=await iterator.next(),two=await iterator.next(),three=await iterator.next();
    return{lockedBefore,one,two,three,closedKeys:Object.keys(two),lockedAfter:stream.locked,returned:await iterator.return('after')};
  });
  await test('values-three-concurrent-next',async()=>{
    const stream=new S({start(c){c.enqueue(1);c.enqueue(2);c.close();}}),iterator=stream.values();
    const results=await Promise.all([iterator.next(),iterator.next(),iterator.next()]);return{results,locked:stream.locked};
  });
  await test('values-pending-next-return-serialized',async()=>{
    let control;const trace=[],stream=new S({start(c){control=c;},cancel(reason){trace.push('cancel:'+reason);}}),iterator=stream.values();
    const first=iterator.next().then(value=>{trace.push('next');return value;}),last=iterator.return('stop').then(value=>{trace.push('return');return value;});
    await Promise.resolve();await Promise.resolve();const before=trace.slice();control.enqueue(7);
    const results=await Promise.all([first,last]);return{before,results,trace,locked:stream.locked};
  });
  for(const preventCancel of [false,true,'yes',0])await test('values-return-prevent-'+String(preventCancel),async()=>{
    const reasons=[],stream=new S({start(c){c.enqueue(1);c.enqueue(2);},cancel(reason){reasons.push(reason);}}),iterator=stream.values({preventCancel});
    const first=await iterator.next(),returned=await iterator.return('stop'),again=await iterator.next();
    const locked=stream.locked,reader=stream.getReader(),remaining=preventCancel?(await reader.read()).value:null;
    await reader.cancel();reader.releaseLock();return{first,returned,again,reasons:reasons.slice(0,preventCancel?0:1),locked,remaining};
  });
  await test('values-return-cancel-reject-unlocks',async()=>{
    const reason={},stream=new S({cancel(){return Promise.reject(reason);}}),iterator=stream.values();let same=false;
    try{await iterator.return('stop');}catch(error){same=error===reason;}return{same,locked:stream.locked,next:await iterator.next(),again:await iterator.return('again')};
  });
  await test('values-error-unlocks-and-recovers-queue',async()=>{
    const reason={},stream=new S({start(c){c.error(reason);}}),iterator=stream.values();let same=false;
    try{await iterator.next();}catch(error){same=error===reason;}return{same,locked:stream.locked,next:await iterator.next(),returned:await iterator.return('after')};
  });
  await test('values-concurrent-rejection-next',async()=>{
    const reason={},stream=new S({start(c){c.error(reason);}}),iterator=stream.values();
    const first=iterator.next().then(()=>false,error=>error===reason),second=iterator.next();return{first:await first,second:await second,locked:stream.locked};
  });
  await test('values-return-before-read',async()=>{
    const trace=[],stream=new S({cancel(reason){trace.push(reason);}}),iterator=stream.values();
    return{returned:await iterator.return('early'),next:await iterator.next(),trace,locked:stream.locked};
  });
  await test('values-concurrent-returns',async()=>{
    const reasons=[],stream=new S({cancel(reason){reasons.push(reason);}}),iterator=stream.values();
    const returned=await Promise.all([iterator.return('first'),iterator.return('second'),iterator.next()]);return{returned,reasons,locked:stream.locked};
  });
  await test('values-return-unlocks-before-cancel-fulfilled',async()=>{
    let finish;const stream=new S({cancel(){return new Promise(resolve=>{finish=resolve;});}}),iterator=stream.values();
    let fulfilled=false;const returned=iterator.return('stop').then(value=>{fulfilled=true;return value;});
    await Promise.resolve();await Promise.resolve();const before={locked:stream.locked,fulfilled};finish();
    return{before,returned:await returned,after:fulfilled};
  });
  await test('values-option-read-once',async()=>{
    let gets=0;const stream=new S({start(c){c.close();}}),iterator=stream.values({get preventCancel(){gets++;return true;}});
    await iterator.next();await iterator.return();return{gets,locked:stream.locked};
  });
  await test('values-for-await-break',async()=>{
    const trace=[],stream=new S({start(c){c.enqueue(1);c.enqueue(2);},cancel(reason){trace.push(reason===undefined?'undefined':reason);}});
    const values=[];for await(const value of stream){values.push(value);break;}return{values,trace,locked:stream.locked};
  });
  await test('values-for-await-prevent-cancel',async()=>{
    let cancels=0;const stream=new S({start(c){c.enqueue(1);c.enqueue(2);c.close();},cancel(){cancels++;}}),values=[];
    for await(const value of stream.values({preventCancel:true})){values.push(value);break;}
    const rest=await consume(stream);return{values,rest,cancels,locked:stream.locked};
  });
  await test('values-borrowed-next-return',async()=>{
    const stream=new S({start(c){c.enqueue(3);c.close();}}),iterator=stream.values(),next=iterator.next,stop=iterator.return;
    return{first:await next.call(null),last:await stop.call({x:1},'stop'),locked:stream.locked};
  });
  await test('values-descriptors-and-protocol',async()=>{
    const stream=new S({start(c){c.close();}}),iterator=stream.values(),proto=Object.getPrototypeOf(iterator);
    const result={same:S.prototype.values===S.prototype[Symbol.asyncIterator],valuesLength:S.prototype.values.length,
      fromLength:S.from.length,nextLength:iterator.next.length,returnLength:iterator.return.length,
      self:iterator[Symbol.asyncIterator]()===iterator,throwType:typeof iterator.throw,protoNext:proto.next===undefined,protoReturn:proto.return===undefined,
      ownKeys:Object.keys(iterator),tag:Object.prototype.toString.call(iterator)};
    await iterator.return();return result;
  });
  await test('values-new-rejected',()=>new S.prototype.values());
  await test('own-error-codes-ignore-inherited-setter',async()=>{
    const define=Object.defineProperty,previous=Object.getOwnPropertyDescriptor(Error.prototype,'code');
    let gets=0,sets=0;const codes=[];let stream,reader;
    try{
      define(Error.prototype,'code',{configurable:true,get(){gets++;throw Error('inherited code getter');},set(){sets++;throw Error('inherited code setter');}});
      for(const invoke of [()=>S.from({}),()=>S.prototype.values.call({})]){
        try{invoke();}catch(error){codes.push(Object.getOwnPropertyDescriptor(error,'code')?.value);}
      }
      stream=new S();reader=stream.getReader();try{stream.values();}catch(error){codes.push(Object.getOwnPropertyDescriptor(error,'code')?.value);}
    }finally{
      if(previous)define(Error.prototype,'code',previous);else delete Error.prototype.code;
      if(reader)reader.releaseLock();if(stream)await stream.cancel();
    }
    return{gets,sets,codes};
  });
  return cases;
}
