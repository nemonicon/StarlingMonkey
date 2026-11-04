// UNEXECUTED. Only package after exact corrected native guard pins AND observed
// NODE_COMPAT_STREAM_WEB=OFF pass preflight. No old prototype entry is allowed.
import {controllerCases} from '../candidate/controller-cases.mjs';
let calls=0;
function ensure(value,message){if(!value)throw Error(message);}
async function deployedConstructor(){
  let controller;const stream=new TransformStream({start(value){controller=value;}});
  const writer=stream.writable.getWriter(),reader=stream.readable.getReader(),closing=writer.close();
  await reader.read();await closing;await writer.closed;await reader.closed;writer.releaseLock();reader.releaseLock();
  return controller.constructor;
}
export async function run(){
  const report={calls:++calls,passed:false};
  try{
    ensure(typeof TransformStream==='function','Native web streams must be installed');
    const Controller=await deployedConstructor(),prototype=Controller.prototype;
    ensure(typeof Controller==='function'&&prototype.constructor===Controller,'Real retained native controller');
    const methods={};
    for(const name of ['desiredSize','enqueue','error','terminate']){
      const descriptor=Object.getOwnPropertyDescriptor(prototype,name),method=descriptor.get??descriptor.value;
      ensure(/\[native code\]/.test(Function.prototype.toString.call(method)),'Module OFF must expose native method, no JS wrapper: '+name);
      methods[name]=method;
    }
    // From this point only the newly corrected native CPP is ever entered.
    const cases=await controllerCases({TransformStream,TransformStreamDefaultController:Controller});
    for(const entry of cases.slice(0,4))ensure(entry.error?.name==='TypeError'&&entry.error.code===undefined,'Native prototype receiver TypeError (Node code absent)');
    ensure(cases[4].desiredSize===0&&cases[5].desiredSize===null&&cases[5].writerReason&&cases[5].readerReason,'Valid closed/error states preserved');
    let additionalInvalidReceivers=0;
    for(const receiver of [null,undefined,{},Object.create(prototype)])for(const[name,method]of Object.entries(methods)){
      let caught;try{Reflect.apply(method,receiver,[]);}catch(error){caught=error;}
      ensure(caught instanceof TypeError,'Native invalid receiver '+name);additionalInvalidReceivers++;
    }
    report.cases=cases;report.additionalInvalidReceivers=additionalInvalidReceivers;report.nativeMethodsWithoutWrappers=true;
    report.temporaryStreamsOnlyDeployedAndCleaned=true;report.passed=true;
  }catch(error){report.failure={name:error?.name,message:error?.message,stack:error?.stack};}
  return JSON.stringify(report);
}
