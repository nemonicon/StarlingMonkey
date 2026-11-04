// ISOLATED continuation of the frozen codec/guard stage. Node22 stream
// algorithms and MIT source attribution are pinned in source-pins.json.
export function installReadableIteration(record){
  const {ReadableStream:Stream,ReadableStreamDefaultReader:Reader,
    ReadableStreamDefaultController:Controller}=record;
  const apply=Reflect.apply,define=Object.defineProperty,descriptor=Object.getOwnPropertyDescriptor;
  const getPrototype=Object.getPrototypeOf,setPrototype=Object.setPrototypeOf;
  const TypeErrorCtor=TypeError,PromiseCtor=Promise;
  const then=PromiseCtor.prototype.then,resolve=PromiseCtor.resolve.bind(PromiseCtor);
  const call=(fn,self,args=[])=>apply(fn,self,args);
  const chain=(promise,fulfilled,rejected)=>call(then,promise,[fulfilled,rejected]);
  const locked=descriptor(Stream.prototype,'locked').get;
  const read=Reader.prototype.read,cancel=Reader.prototype.cancel,release=Reader.prototype.releaseLock;
  const closed=descriptor(Reader.prototype,'closed').get;
  const enqueue=Controller.prototype.enqueue,close=Controller.prototype.close;
  const iteratorSymbol=Symbol.iterator,asyncSymbol=Symbol.asyncIterator;
  function codeOwn(error,code){define(error,'code',{__proto__:null,value:code,writable:true,enumerable:true,configurable:true});return error;}
  function invalid(code,message){throw codeOwn(new TypeErrorCtor(message),code);}
  const asyncPrototype=getPrototype(getPrototype(getPrototype((async function*(){})())));
  const iteratorBase=setPrototype({next:undefined,return:undefined},asyncPrototype);

  function iteratorRecord(iterable){
    // Property access and callable errors deliberately remain ordinary errors.
    let method=iterable[asyncSymbol];
    if(method==null){
      method=iterable[iteratorSymbol];
      if(method===undefined)invalid('ERR_ARG_NOT_ITERABLE','The argument must be iterable');
      const iterator=call(method,iterable);
      // Node22 util.getIterator uses typeof object, excluding callable results.
      if(typeof iterator!=='object'||iterator===null)invalid('ERR_INVALID_STATE','Iterator method must return an object');
      const next=iterator.next;
      // Match the pinned async-generator bridge: yielded promises from sync
      // iterators are awaited and sync return delegation retains its semantics.
      const adapter=(async function*(){return yield*{[iteratorSymbol](){return iterator;}};})();
      // Capture the original next once, as Node's GetIterator does before
      // creating the bridge (the bridge itself reads next again on first use).
      void next;
      return{iterator:adapter,next:adapter.next};
    }
    const iterator=call(method,iterable);
    if(typeof iterator!=='object'||iterator===null)invalid('ERR_INVALID_STATE','Iterator method must return an object');
    return{iterator,next:iterator.next};
  }
  const methods={
    from(iterable){
      const source=iteratorRecord(iterable);
      return new Stream({
        pull(controller){
          const result=call(source.next,source.iterator);
          if(typeof result!=='object'||result===null)invalid('ERR_INVALID_STATE','Iterator.next must return an object');
          return chain(resolve(result),entry=>{
            if(typeof entry!=='object'||entry===null)invalid('ERR_INVALID_STATE','Iterator.next promise must fulfill with an object');
            if(entry.done)call(close,controller);else call(enqueue,controller,[entry.value]);
          });
        },
        cancel(reason){
          const method=source.iterator.return;
          if(method===undefined)return;
          return chain(resolve(call(method,source.iterator,[reason])),entry=>{
            if(typeof entry!=='object'||entry===null)invalid('ERR_INVALID_STATE','Iterator.return promise must fulfill with an object');
          });
        },
      },{highWaterMark:0});
    },
    values(options=undefined){
      // Class prototypes have no initialized stream; never delegate that
      // receiver. Native getter supplies the ordinary receiver brand check.
      if(this===Stream.prototype)invalid('ERR_INVALID_THIS','Invalid ReadableStream receiver');
      try{call(locked,this);}catch{invalid('ERR_INVALID_THIS','Invalid ReadableStream receiver');}
      if(options!==undefined&&options!==null&&typeof options!=='object'&&typeof options!=='function')
        invalid('ERR_INVALID_ARG_TYPE','options must be an object');
      const preventCancel=!!options?.preventCancel;
      let reader;
      try{reader=new Reader(this);}catch(error){
        if(error instanceof TypeErrorCtor&&!descriptor(error,'code'))codeOwn(error,'ERR_INVALID_STATE');throw error;
      }
      // Releasing an ordinary reader can reject its closed promise; handle it
      // privately even if the iterator's caller never inspects that promise.
      chain(call(closed,reader),()=>{},()=>{});
      let done=false,current,started=false;
      const finished=value=>({done:true,value});
      function nextStep(){
        if(done)return resolve(finished(undefined));
        return chain(call(read,reader),entry=>{
          current=undefined;
          if(entry.done){done=true;call(release,reader);return finished(undefined);}
          return{value:entry.value,done:false};
        },error=>{current=undefined;done=true;call(release,reader);throw error;});
      }
      function returnStep(value){
        if(done)return resolve(finished(value));
        done=true;
        if(preventCancel){call(release,reader);return resolve(finished(value));}
        let cancellation;
        try{cancellation=call(cancel,reader,[value]);}finally{call(release,reader);}
        return chain(resolve(cancellation),()=>finished(value));
      }
      return setPrototype({
        next(){
          if(!started){current=resolve();started=true;}
          current=current!==undefined?chain(current,nextStep,nextStep):nextStep();
          return current;
        },
        return(value){
          started=true;
          current=current!==undefined?chain(current,()=>returnStep(value),()=>returnStep(value)):returnStep(value);
          return current;
        },
        [asyncSymbol](){return this;},
      },iteratorBase);
    },
  };
  define(Stream,'from',{value:methods.from,writable:true,enumerable:false,configurable:true});
  define(Stream.prototype,'values',{value:methods.values,writable:true,enumerable:true,configurable:true});
  define(Stream.prototype,asyncSymbol,{value:methods.values,writable:true,enumerable:false,configurable:true});
  return{from:methods.from,values:methods.values};
}
