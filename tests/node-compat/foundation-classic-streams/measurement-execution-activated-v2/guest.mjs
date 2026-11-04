import {bufferBeforeProvider} from './capture-before.mjs';
import * as provider from 'benchmark:provider';
import {createWorkload as common} from './workload.mjs';
import {createWorkload as rawControls} from './control-workload.mjs';
import {selectedCase} from './protocol.mjs';
const commonWork=common(provider),controlWork=rawControls(provider);
let active=-1,calls=0;
const requireValue=(value,message)=>{if(!value)throw new Error(message);};
function choose(index){const row=selectedCase(index);return{row,work:row.control?controlWork:commonWork};}
export function setup(index){const{row,work}=choose(index);active=index;return work.setup(row.id);}
export async function inspect(index){calls++;const{row,work}=choose(index);const setupValue=setup(index);return JSON.stringify({calls,setup:setupValue,result:await work.run(row.iterations,{trace:true})});}
export async function batch(index,iterations){calls++;requireValue(active===index,'Call setup for this exact finite case');const{row,work}=choose(index);requireValue(Number.isInteger(iterations)&&iterations>=1&&iterations<=row.iterations,'Finite calibrated1..requested bound≤16');return JSON.stringify({result:await work.run(iterations,{trace:false})});}
export function identity(){
 const{Buffer,EventEmitter,StringDecoder,nextTick}=provider.dependencies;
 const backing=new ArrayBuffer(20),window=Buffer.from(backing,8,4);window[0]=65;
 return JSON.stringify({defaultGraph:provider.default===provider.stream.default&&provider.stream.default===provider.stream.Stream,
  promisesGraph:provider.stream.promises.pipeline===provider.promises.pipeline,
  eventEmitterPrototype:provider.stream.Writable.prototype instanceof EventEmitter,
  selectedTickType:typeof nextTick,decoderA:new StringDecoder('utf8').write(window.subarray(0,1)),
  bufferView:window.buffer===backing&&window.byteOffset===8&&window.length===4,
  bufferSameAsBefore:Buffer===bufferBeforeProvider,globalSameAsProvider:globalThis.Buffer===Buffer,
  beforeBufferType:typeof bufferBeforeProvider,globalChangedDuringProvider:globalThis.Buffer!==bufferBeforeProvider});
}
export async function checkpointProbe(){
 const trace=[];let callbacks=0;
 await new Promise(resolve=>{provider.dependencies.nextTick(value=>{requireValue(value===42,'Selected scheduler argument');callbacks++;trace.push('selected-tick');resolve();},42);globalThis.queueMicrotask(()=>trace.push('microtask'));});
 await Promise.resolve();requireValue(callbacks===1&&trace.length===2,'Finite probe callbacks must settle once');
 return JSON.stringify({callbacks,trace,queueDepthObserved:false,terminalQueueEmptyObserved:false});
}
