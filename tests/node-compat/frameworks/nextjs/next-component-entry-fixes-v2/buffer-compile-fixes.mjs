// Experimental guest entry corrections, not embedding APIs or host adapters.
// Installation is pure INIT metadata work. Compilation/copying is ordinary only.
export function installCrossPrototypeBufferFrom(Buffer, world=globalThis) {
  const U8=world.Uint8Array,AB=world.ArrayBuffer,prototype=Object.getPrototypeOf(U8.prototype);
  const tag=Object.getOwnPropertyDescriptor(prototype,Symbol.toStringTag).get;
  const buffer=Object.getOwnPropertyDescriptor(prototype,'buffer').get;
  const offset=Object.getOwnPropertyDescriptor(prototype,'byteOffset').get;
  const length=Object.getOwnPropertyDescriptor(prototype,'byteLength').get;
  const abLength=Object.getOwnPropertyDescriptor(AB.prototype,'byteLength').get;
  const resizable=Object.getOwnPropertyDescriptor(AB.prototype,'resizable')?.get;
  const detached=Object.getOwnPropertyDescriptor(AB.prototype,'detached')?.get;
  const hasInstance=Function.prototype[Symbol.hasInstance],apply=Reflect.apply;
  const original=Buffer.from;
  function refused(){const e=new TypeError('node:buffer.from requires fixed unshared Uint8Array backing');e.code='ERR_SM_NODE_UNSUPPORTED';e.module='node:buffer';e.operation='Buffer.from';throw e;}
  function from(...args) {
    const value=args[0];let branded=false;
    try{branded=apply(tag,value,[])==='Uint8Array';}catch{}
    if(branded&&!apply(hasInstance,U8,[value])) {
      let backing,start,count;
      try{
        backing=apply(buffer,value,[]);apply(abLength,backing,[]);
        if(resizable&&apply(resizable,backing,[]))refused();
        if(detached&&apply(detached,backing,[]))refused();
        start=apply(offset,value,[]);count=apply(length,value,[]);
        if(!detached)new U8(backing,0,0); // Refuse detached backing, including zero-length views.
      }catch{refused();}
      // A temporary ordinary-prototype view shares only during this call.
      // The genuine old factory performs its existing bounded owned COPY.
      args[0]=new U8(backing,start,count);
    }
    return apply(original,this,args);
  }
  Buffer.from=from;
  return {restore(){if(Buffer.from===from)Buffer.from=original;}};
}

export function installNonAsciiCompileFallback(Module, FunctionConstructor=Function) {
  const original=Module.prototype._compile,apply=Reflect.apply;
  const char=Function.prototype.call.bind(String.prototype.charCodeAt);
  const replace=Function.prototype.call.bind(String.prototype.replace);
  const encode=encodeURI,MaxSource=16*1024*1024,MaxPath=4096;
  function failure(code,message){const e=new TypeError(message);e.code=code;throw e;}
  function bytes(text,limit){let n=0;for(let i=0;i<text.length;i++){const c=char(text,i);if(c<128)n++;else if(c<2048)n+=2;else if(c>=0xd800&&c<=0xdbff&&i+1<text.length&&char(text,i+1)>=0xdc00&&char(text,i+1)<=0xdfff){n+=4;i++;}else n+=3;if(n>limit)failure('ERR_SM_NODE_LIMIT','CommonJS source/filename exceeds existing byte limit');}return n;}
  function makeRequire(mod) {
    // Same public-Module links and parent object as the genuine private helper.
    function require(request){return mod.require(request);}
    require.resolve=(request,options)=>Module._resolveFilename(request,mod,false,options);
    require.resolve.paths=request=>{if(typeof request!=='string')failure('ERR_INVALID_ARG_TYPE','request must be a string');return Module._resolveLookupPaths(request,mod);};
    require.cache=Module._cache;require.extensions=Module._extensions;require.main=Module._main;
    return require;
  }
  function compile(...args) {
    const [content,filename]=args;let nonAscii=false;
    if(typeof content==='string')for(let i=0;i<content.length;i++)if(char(content,i)>127){nonAscii=true;break;}
    if(!nonAscii)return apply(original,this,args); // ASCII/errors keep original native behavior.
    if(typeof filename!=='string'||filename[0]!=='/'||/[\0\r\n\u2028\u2029]/.test(filename))
      failure('ERR_INVALID_ARG_VALUE','CommonJS fallback requires a bounded absolute single-line POSIX filename');
    bytes(content,MaxSource);bytes(filename,MaxPath);
    let sourceURL;try{sourceURL='file://'+encode(filename);}catch{failure('ERR_INVALID_ARG_VALUE','Invalid CommonJS fallback filename');}
    const source=replace(content,/^#![^\n]*(?:\n|$)/,'\n');
    const fn=FunctionConstructor('exports','require','module','__filename','__dirname',source+'\n//# sourceURL='+sourceURL+'\n');
    const slash=filename.lastIndexOf('/'),directory=slash===0?'/':filename.slice(0,slash);
    return apply(fn,this.exports,[this.exports,makeRequire(this),this,filename,directory]);
  }
  Module.prototype._compile=compile;
  return {restore(){if(Module.prototype._compile===compile)Module.prototype._compile=original;}};
}
