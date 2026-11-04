import {spawn} from 'node:child_process';
let calls=0,handled=null;
const t=new EventTarget();t.addEventListener('test',()=>{calls++;try{throw undefined}catch(error){handled=error===undefined?'caught-undefined':'bad'}});t.dispatchEvent(new Event('test'));
export function run(){return JSON.stringify({calls,handled});}
