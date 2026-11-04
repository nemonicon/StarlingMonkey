const external={buffer:{Buffer},events,'string_decoder/':{StringDecoder},'abort-controller':{AbortSignal,AbortController}};
const cache=Object.create(null),HasOwn=Object.hasOwn;
function require(id){
 if(HasOwn(external,id))return external[id];
 if(HasOwn(cache,id))return cache[id].exports;
 if(!HasOwn(modules,id))throw new ErrorCtor('Unknown private classic dependency: '+id);
 const module={exports:{}};cache[id]=module;
 modules[id](module,module.exports,require);
 return module.exports;
}
// Cache-before-call preserves the audited CJS cycles. This loader is a closure,
// accepts only literal generated IDs and is never exported to application JS.
const root=require('lib/stream.js');
return {Stream:root,promises:require('lib/stream/promises.js')};
}
