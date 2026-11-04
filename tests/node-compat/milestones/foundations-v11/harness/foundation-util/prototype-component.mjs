import * as util from './util-prototype.mjs';
import * as types from './types-prototype.mjs';
import * as sys from './sys-prototype.mjs';
import {runComponentCases} from './component-cases.mjs';
import scope from './prototype-scope.mjs';
const snapshot={encoder:util.TextEncoder,decoder:util.TextDecoder,types:util.types,defaultObject:util.default};
let calls=0;
export async function run(){
  try{
    const features={sharedArrayBuffer:typeof SharedArrayBuffer==='function',transfer:typeof ArrayBuffer.prototype.transfer==='function',resizable:typeof ArrayBuffer.prototype.resize==='function'&&new ArrayBuffer(1,{maxByteLength:2}).resizable===true};
    const result=await runComponentCases({util,types,sys,predicateNames:scope.typesImplemented,features});
    const deferred=[];
    for(const[module,namespace,names]of [['node:util',util,Object.keys(util).filter(name=>name!=='default'&&name!=='types'&&!scope.utilImplemented.includes(name))],['node:util/types',types,scope.typesDeferred]])for(const name of names)for(const construct of [false,true]){
      let error;try{if(construct)Reflect.construct(namespace[name],[]);else namespace[name]();}catch(caught){error=caught;}
      if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||error.module!==module||error.operation!==(name==='debug'?'debuglog':name))throw new Error('deferred binding '+name);
      deferred.push({module,name,construct,code:error.code});
    }
    if(snapshot.encoder!==util.TextEncoder||snapshot.decoder!==util.TextDecoder||snapshot.types!==util.types||snapshot.defaultObject!==util.default)throw new Error('snapshot identity');
    return JSON.stringify({calls:++calls,...result,deferred,snapshotIdentityPreserved:true,utilExports:Object.keys(util).sort(),typeExports:Object.keys(types).sort(),sysExports:Object.keys(sys).sort(),nodeOnlyNativeHelperDelegation:false});
  }catch(error){return JSON.stringify({failure:String(error),stack:error?.stack});}
}
