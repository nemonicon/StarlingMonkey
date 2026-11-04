import {spawn} from 'node:child_process';
let calls=0,handled=null;
calls++;handled='clean';
export function run(){return JSON.stringify({calls,handled});}
