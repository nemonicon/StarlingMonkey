// TEST ONLY real stock Node scheduling/liveness adapter. Not installed in guest.
import * as timers from 'node:timers';
export function createHostBackend(){
 let next=1,deployed=true;const tasks=new Map(),events=[];
 function check(){if(!deployed)throw Object.assign(Error('INIT'),{code:'ERR_SM_NODE_TIMERS_INITIALIZATION'});}
 function entry(id){return tasks.get(id);}
 const kernel={
  create(kind,callback,delay,args){check();if(tasks.size>=4096)throw Object.assign(RangeError('budget'),{code:'ERR_SM_NODE_SCHEDULER_LIMIT'});const id=next++,record={id,kind,handle:null,generation:0};
   const run=()=>{const generation=record.generation;events.push(['run',id,kind]);try{return callback(...args);}finally{if(kind!==1&&record.generation===generation)tasks.delete(id);}};
   record.handle=kind===2?timers.setImmediate(run):kind===1?timers.setInterval(run,delay):timers.setTimeout(run,delay);tasks.set(id,record);events.push(['create',id,kind]);return id;},
  state(id){check();const e=entry(id);return e?(e.handle.hasRef()?1:0):-1;},
  setRef(id,ref){check();const e=entry(id);if(e){ref?e.handle.ref():e.handle.unref();events.push(['ref',id,ref]);}},
  clear(id){check();const e=entry(id);if(e){e.kind===2?timers.clearImmediate(e.handle):timers.clearTimeout(e.handle);tasks.delete(id);events.push(['clear',id]);}},
  refresh(id){check();const e=entry(id);if(!e||e.kind===2)throw Object.assign(Error('inactive'),{code:'ERR_SM_NODE_TIMER_INACTIVE'});e.handle.refresh();e.generation++;events.push(['refresh',id]);}
 };
 return{kernel,events,active(){return tasks.size;},referenced(){return[...tasks.values()].filter(x=>x.handle.hasRef()).length;},phase(value){deployed=value;},close(){for(const id of [...tasks.keys()])kernel.clear(id);}};
}
