import bufferDefault,* as buffer from 'node:buffer';
import childDefault,* as child from 'node:child_process';
import commonJS from './static-require.cjs';
import {allocationChecks} from 'node-compat:installed-allocation-checks';
import contract from 'node-compat:installed-core-contract';
import {allocationProfile,stubPoisonChecks} from './checks.mjs';
import {createDemandList} from 'node-compat:installed-buffer-list-demand';
import {demandChecks} from '../demand-checks.mjs';
const {Buffer}=buffer,allocate=Buffer.allocUnsafe;
const snapshot=allocate(3),view=snapshot.subarray(1,3),backing=snapshot.buffer;
snapshot[0]=17;
let calls=0,bareBuffer,bareChild;
function check(value,message){if(!value)throw new Error('Installed allocator: '+message);}
export async function run(){
  try{
    const b=String.fromCharCode(98,117,102,102,101,114),c=String.fromCharCode(99,104,105,108,100,95,112,114,111,99,101,115,115);
    const nextBuffer=await import(b),nextChild=await import(c);
    if(bareBuffer)check(bareBuffer===nextBuffer&&bareChild===nextChild,'per-specifier module cache');
    bareBuffer=nextBuffer;bareChild=nextChild;
    check((await import('node:buffer'))===buffer&&(await import('node:child_process'))===child,'canonical module cache');
    check(bareBuffer.Buffer===Buffer&&bareBuffer.default===bufferDefault&&bareChild.default===childDefault,'native bare aliases');
    check(commonJS.Buffer===Buffer&&commonJS.buffer===bufferDefault&&commonJS.child===childDefault&&globalThis.Buffer===Buffer,'static CJS/global identity');
    check(Object.getPrototypeOf(buffer)===null&&Object.getPrototypeOf(child)===null,'native namespace prototypes');
    check(Object.prototype.toString.call(buffer)==='[object Module]'&&Object.prototype.toString.call(child)==='[object Module]','native namespace tags');
    check(buffer.then===undefined&&child.then===undefined&&bufferDefault.then===undefined&&childDefault.then===undefined,'safe namespace inspection');
    check(await Promise.resolve(buffer)===buffer&&await Promise.resolve(child)===child,'safe namespace await');
    for(const name of contract.bufferExports.filter(n=>n!=='default'))check(buffer[name]===bufferDefault[name],'Buffer default binding');
    for(const name of contract.childExports)check(child[name]===childDefault[name],'child default binding');
    check(Buffer.allocUnsafe===allocate&&bareBuffer.Buffer.allocUnsafe===allocate&&commonJS.Buffer.allocUnsafe===allocate,'actual allocator unchanged');
    const cases=allocationChecks(Buffer,allocate),profile=allocationProfile(Buffer),refusals=stubPoisonChecks(buffer,child,contract);
    const demand=demandChecks(Buffer,createDemandList(Buffer));
    check(Buffer.allocUnsafe===allocate,'allocator never replaced');
    check(Buffer.isBuffer(snapshot)&&snapshot.buffer===backing&&backing.byteLength===3&&snapshot.byteOffset===0,'snapshot owned brand/backing');
    check(Buffer.isBuffer(view)&&view.buffer===backing&&view.byteOffset===1,'snapshot shared view');
    view[0]=++calls;snapshot[0]++;
    return JSON.stringify({calls,cases,profile,refusals,demand,snapshot:{first:snapshot[0],shared:view[0]===snapshot[1],viewValue:view[0],byteOffset:view.byteOffset,backingBytes:backing.byteLength},
      coreVersion:contract.coreVersion,actualNativeModule:true,allocatorReplaced:false,namespaceAliases:true,staticCommonJS:true,globalIdentity:true});
  }catch(error){return JSON.stringify({failure:{name:error.name,code:error.code,message:error.message,stack:error.stack}});}
}
