import {spawn} from 'node:child_process';
let calls=0,handled=null;
const t=new EventTarget();t.addEventListener('test',()=>{calls++;try{spawn();}catch(error){handled=error.code;}});t.dispatchEvent(new Event('test'));
export function run(){return JSON.stringify({calls,handled});}
