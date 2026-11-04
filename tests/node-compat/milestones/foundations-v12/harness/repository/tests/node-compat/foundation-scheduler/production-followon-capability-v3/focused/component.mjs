import EventEmitter,* as events from 'node:events';
import bare,* as aliases from 'events';
import * as again from 'node:events';
import inspectCommonJS from './require.cjs';
import {publicCases,nestedOnceCases,receiverCases,targetSymbolInfo} from './public-cases.mjs';

let calls=0,snapshotCallbacks=0,snapshotThis=false,snapshotTarget=false;
const snapshotController=new AbortController();
const snapshotResource=events.addAbortListener(snapshotController.signal,function(event){
 snapshotCallbacks++;snapshotThis=this===snapshotController.signal;snapshotTarget=event.currentTarget===snapshotController.signal;
});
function profileErrors(){
 const ErrorCtor=Error,TypeErrorCtor=TypeError,define=Object.defineProperty,keys=['code','module','operation','profile'];
 const old=keys.map(key=>Object.getOwnPropertyDescriptor(ErrorCtor.prototype,key));let hooks=0,ambient=0;const errors=[];
 try{
  for(const key of keys)define(ErrorCtor.prototype,key,{configurable:true,set(){hooks++;throw new ErrorCtor('inherited metadata hook');}});
  globalThis.Error=function(){ambient++;};globalThis.TypeError=function(){ambient++;};
  for(const[name,operation]of [['once-call',()=>events.once()],['once-new',()=>new events.once()],['on-call',()=>events.on()],['on-new',()=>new events.on()],
   ['async-resource-call',()=>events.EventEmitterAsyncResource()],['async-resource-new',()=>new events.EventEmitterAsyncResource()],['invalid-signal',()=>events.addAbortListener(null,()=>{})]]){
   let error;try{operation();}catch(value){error=value;}
   if(!error)throw new ErrorCtor('Expected profile error '+name);
   errors.push({name,type:error.name,code:error.code,module:error.module,operation:error.operation,profile:error.profile,own:keys.every(key=>Object.hasOwn(error,key))});
  }
 }finally{
  globalThis.Error=ErrorCtor;globalThis.TypeError=TypeErrorCtor;
  for(let i=0;i<keys.length;i++)if(old[i])define(ErrorCtor.prototype,keys[i],old[i]);else Reflect.deleteProperty(ErrorCtor.prototype,keys[i]);
 }
 return{errors,hooks,ambient};
}
export async function run(){
 calls++;
 try{
  const publicObserved=await publicCases(events),nested=nestedOnceCases(events),receivers=receiverCases(events);
  const snapshotBefore=snapshotCallbacks;snapshotController.signal.dispatchEvent(new Event('abort'));snapshotResource[Symbol.dispose]();
  return JSON.stringify({calls,publicCases:publicObserved,nestedOnceCases:nested,receiverCases:receivers,
   namespace:{names:Object.getOwnPropertyNames(events).sort(),defaultNamed:EventEmitter===events.EventEmitter,canonicalCached:events===again,
    aliasValues:Object.keys(events).every(key=>events[key]===aliases[key]),defaultAlias:EventEmitter===bare,then:typeof events.then,
    errorMonitorType:typeof events.errorMonitor,captureRejectionSymbol:events.captureRejectionSymbol===Symbol.for('nodejs.rejection'),
    defaultMaxListeners:events.defaultMaxListeners,captureRejections:events.captureRejections,usingDomains:events.usingDomains},
   commonJS:inspectCommonJS(),profileErrors:profileErrors(),symbol:targetSymbolInfo(),
   snapshot:{before:snapshotBefore,after:snapshotCallbacks,signalThis:snapshotThis,currentTarget:snapshotTarget,aborted:snapshotController.signal.aborted}});
 }catch(error){return JSON.stringify({calls,failure:{name:error?.name??null,code:error?.code??null,message:String(error?.message??error)}});}
}
