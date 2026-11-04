const events=require('events');
const canonical=require('node:events');
module.exports=function inspectCommonJS(){
 let call,newCall;
 try{events.once();}catch(error){call=error.code;}
 try{new events.EventEmitterAsyncResource();}catch(error){newCall=error.code;}
 return{same:events===canonical,constructorAlias:events.EventEmitter===events,defaultProperty:typeof events.default,
  addAbortListenerType:typeof events.addAbortListener,errorMonitorType:typeof events.errorMonitor,rejectedCall:call,rejectedConstruction:newCall};
};
