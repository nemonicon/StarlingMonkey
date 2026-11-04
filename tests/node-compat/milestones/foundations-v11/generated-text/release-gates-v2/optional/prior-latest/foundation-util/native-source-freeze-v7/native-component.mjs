import * as util from 'node:util';
import * as bareUtil from 'util';
import * as types from 'node:util/types';
import * as bareTypes from 'util/types';
import * as sys from 'node:sys';
import * as bareSys from 'sys';
import commonJS from './native-require.cjs';
import {runComponentCases} from './component-cases.mjs';
import scope from './prototype-scope.mjs';
const snapshot={util,types,sys,defaults:util.default,options:util.inspect.defaultOptions,encoder:util.TextEncoder,decoder:util.TextDecoder};
let calls=0;
export async function run(){
  try{
    const features={sharedArrayBuffer:typeof SharedArrayBuffer==='function',transfer:typeof ArrayBuffer.prototype.transfer==='function',resizable:typeof ArrayBuffer.prototype.resize==='function'&&new ArrayBuffer(1,{maxByteLength:2}).resizable===true};
    const cases=await runComponentCases({util,types,sys,predicateNames:scope.typesImplemented,features});
    const deferred=[];
    for(const[module,namespace,names]of [['node:util',util,Object.keys(util).filter(name=>name!=='default'&&name!=='types'&&!scope.utilImplemented.includes(name))],['node:util/types',types,scope.typesDeferred]])for(const name of names)for(const construct of [false,true]){
      let error;try{if(construct)Reflect.construct(namespace[name],[]);else namespace[name]();}catch(caught){error=caught;}
      if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||error.module!==module||error.operation!==(name==='debug'?'debuglog':name)||error.profile!=='sm-node-22.14.0-m0.7')throw new Error('deferred binding '+name);
      deferred.push({module,name,construct,code:error.code,profile:error.profile});
    }
    const dynamic=await import('node:util'),dynamicTypes=await import('node:util/types'),dynamicSys=await import('node:sys');
    const aliases={bareCanonicalNamespaces:bareUtil===util&&bareTypes===types&&bareSys===sys,cachedDynamicNamespaces:dynamic===util&&dynamicTypes===types&&dynamicSys===sys,sysNamespaceDistinct:sys!==util,sharedDefault:sys.default===util.default,sharedTypes:util.types===types.default,thenType:typeof util.then,namespacePrototypeNull:Object.getPrototypeOf(util)===null};
    const common={same:commonJS.util===util.default&&commonJS.sys===util.default&&commonJS.canonical===util.default&&commonJS.types===types.default,textIdentity:commonJS.util.TextEncoder===globalThis.TextEncoder,customSymbol:commonJS.util.promisify.custom===Symbol.for('nodejs.util.promisify.custom'),defaultProperty:typeof commonJS.util.default};
    const identity=snapshot.util===util&&snapshot.types===types&&snapshot.sys===sys&&snapshot.defaults===util.default&&snapshot.options===util.inspect.defaultOptions&&snapshot.encoder===util.TextEncoder&&snapshot.decoder===util.TextDecoder;
    // Valid public global replacements: error paths must use captured helpers.
    const E=globalThis.Error,T=globalThis.TypeError,A=Object.assign,oldCode=Object.getOwnPropertyDescriptor(E.prototype,'code');let unsupported,invalid,setterCalls=0,depth;
    try{
      Object.defineProperty(E.prototype,'code',{set(){setterCalls++;throw new E('inherited setter');},configurable:true});
      globalThis.Error=function(){throw new E('replaced Error');};globalThis.TypeError=function(){throw new E('replaced TypeError');};Object.assign=function(){throw new E('replaced assign');};
      try{util.inspect();}catch(error){unsupported=error;}try{util.inherits(null,function(){});}catch(error){invalid=error;}
      const previous=util.inspect.defaultOptions.depth;util.inspect.defaultOptions={depth:4};depth=util.inspect.defaultOptions.depth;util.inspect.defaultOptions={depth:previous};
    }finally{globalThis.Error=E;globalThis.TypeError=T;Object.assign=A;if(oldCode)Object.defineProperty(E.prototype,'code',oldCode);else delete E.prototype.code;}
    const hardening={unsupportedCode:unsupported?.code,invalidCode:invalid?.code,setterCalls,depth};
    return JSON.stringify({calls:++calls,cases,deferred,aliases,common,snapshotIdentity:identity,hardening,exports:{util:Object.keys(util).sort(),types:Object.keys(types).sort(),sys:Object.keys(sys).sort()},noFacadeBundled:true});
  }catch(error){return JSON.stringify({failure:String(error),stack:error?.stack});}
}
