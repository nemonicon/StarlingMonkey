import {errorValue} from './codec-cases.mjs';
// On Starling this is permitted ONLY after the new isolated JS wrappers install.
// It must never invoke the known unguarded old-native prototype entry points.
export async function controllerCases(web){
  const prototype=web.TransformStreamDefaultController.prototype,cases=[];
  for(const name of ['desiredSize','enqueue','error','terminate']){
    const entry=Object.getOwnPropertyDescriptor(prototype,name),method=entry.get??entry.value;
    try{method.call(prototype);cases.push({name,returned:true});}
    catch(error){cases.push({name,error:errorValue(error)});}
  }
  let closedController;
  const closed=new web.TransformStream({start(controller){closedController=controller;}});
  const cw=closed.writable.getWriter(),cr=closed.readable.getReader(),closing=cw.close();
  await cr.read();await closing;await cw.closed;await cr.closed;
  cases.push({name:'closed-controller',desiredSize:closedController.desiredSize});cw.releaseLock();cr.releaseLock();
  let erroredController;
  const errored=new web.TransformStream({start(controller){erroredController=controller;}});
  const ew=errored.writable.getWriter(),er=errored.readable.getReader(),reason={reason:'error'};
  const wc=ew.closed.then(()=>false,error=>error===reason),rc=er.closed.then(()=>false,error=>error===reason);
  erroredController.error(reason);
  cases.push({name:'errored-controller',desiredSize:erroredController.desiredSize,writerReason:await wc,readerReason:await rc});
  ew.releaseLock();er.releaseLock();return cases;
}
