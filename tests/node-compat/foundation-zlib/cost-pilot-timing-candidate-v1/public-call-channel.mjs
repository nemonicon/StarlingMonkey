// Private owned Node harness IPC only; no guest/WASI host capability.
import {createInterface} from 'node:readline';
import {need} from './planner.mjs';
import {validateArmedAck} from './lifecycle-policy.mjs';
export function createParentHandshake({input,output}){
 const lines=createInterface({input,crlfDelay:Infinity}),acks=lines[Symbol.asyncIterator]();
 return Object.freeze({
  async start(event){output.write(JSON.stringify(event)+'\n');const next=await acks.next();need(!next.done,'owned parent ACK channel closed before call');validateArmedAck(next.value,event);},
  end(event){output.write(JSON.stringify(event)+'\n');},
  close(){lines.close();input.destroy();}
 });
}
