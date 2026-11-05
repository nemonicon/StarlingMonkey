// Separate no-clock preservation component: no timer/host operation at INIT or run.
import { Buffer } from 'node:buffer';
const initial=0;let calls=0;
export function run(){calls++;const value=Buffer.from('c3a92201','hex');if(value.length!==4)throw new Error('RESOURCE_PURE_BYTES');return JSON.stringify({schemaVersion:1,initial,calls,hex:value.toString('hex'),timerRequested:false});}
