import {nextTick} from 'starling:test-internal-ticks';
const trace=[];let getters=0;
export function inspectResult(){return JSON.stringify({trace,getters});}
export const api={get run(){getters++;trace.push('getter');nextTick(()=>trace.push('tick'));Promise.resolve().then(()=>{trace.push('job');nextTick(()=>trace.push('job-tick'));});return inspectResult;}};
