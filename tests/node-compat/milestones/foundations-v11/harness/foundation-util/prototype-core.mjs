// Test-only bounded adaptation of Node22 lib/util.js and internal/util.js.
// Copyright Node.js contributors; Node source license notice: LICENSE.node.
const Define=Object.defineProperty,Defines=Object.defineProperties,Descriptors=Object.getOwnPropertyDescriptors;
const GetPrototype=Object.getPrototypeOf,SetPrototype=Object.setPrototypeOf,Values=Object.values;
const Apply=Reflect.apply,PromiseConstructor=Promise,ArrayPush=Array.prototype.push,WellFormed=String.prototype.toWellFormed;
const custom=Symbol.for('nodejs.util.promisify.custom');
function invalid(name){const error=new TypeError(`The "${name}" argument has an invalid type`);error.code='ERR_INVALID_ARG_TYPE';return error;}
export function inherits(ctor,superCtor){
  if(ctor===undefined||ctor===null)throw invalid('ctor');
  if(superCtor===undefined||superCtor===null)throw invalid('superCtor');
  if(superCtor.prototype===undefined)throw invalid('superCtor.prototype');
  Define(ctor,'super_',{__proto__:null,value:superCtor,writable:true,configurable:true});
  SetPrototype(ctor.prototype,superCtor.prototype);
}
export function promisify(original){
  if(typeof original!=='function')throw invalid('original');
  // Node22 observes a truthy custom property twice; do not merge these reads.
  if(original[custom]){
    const fn=original[custom];if(typeof fn!=='function')throw invalid('util.promisify.custom');
    return Define(fn,custom,{__proto__:null,value:fn,enumerable:false,writable:false,configurable:true});
  }
  function fn(...args){
    return new PromiseConstructor((resolve,reject)=>{
      Apply(ArrayPush,args,[(error,...values)=>error?reject(error):resolve(values[0])]);
      Apply(original,this,args);
    });
  }
  SetPrototype(fn,GetPrototype(original));
  Define(fn,custom,{__proto__:null,value:fn,enumerable:false,writable:false,configurable:true});
  const descriptors=Descriptors(original);
  for(const descriptor of Values(descriptors))SetPrototype(descriptor,null);
  return Defines(fn,descriptors);
}
promisify.custom=custom;
export const toUSVString=({toUSVString(input){return Apply(WellFormed,`${input}`,[]);}}).toUSVString;
