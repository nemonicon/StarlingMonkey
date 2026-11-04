import {state} from 'starling:test-initializer-observation';
const beforeContent=state.ticks;
export function run(){if(beforeContent!==1||state.ticks!==1)throw new Error('TICK_INITIALIZER_ORDER');return JSON.stringify({beforeContent,ticks:state.ticks});}
