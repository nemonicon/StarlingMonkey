// Every negative is a fresh componentization initializer, never a reused instance.
const prefix="import {arrayBuffer,blob,buffer,text,json} from 'node:stream/consumers';\n";
export const initializationFailures=Object.freeze([
 ...['arrayBuffer','blob','buffer'].flatMap(name=>[
  {name:'deferred-'+name+'-call',statement:name+'([]);'},
  {name:'deferred-'+name+'-new',statement:'new '+name+'([]);'},
 ]),
 {name:'awaited-text-invalid',statement:'await text([{}]);'},
 {name:'unawaited-text-invalid',statement:'text([{}]);'},
 {name:'microtask-text-invalid',statement:'Promise.resolve().then(()=>text([{}]));'},
 {name:'awaited-json-invalid',statement:"await json(['{']);"},
 {name:'awaited-input-cap',statement:'await text([new Uint8Array(1048577)]);'},
].map(row=>({...row,source:prefix+row.statement+"\nexport function run(){return '';}\n"})));
export const refusalControlScope=Object.freeze({initializationFailures:11,caughtInitializationRefusals:6,uncaughtFieldsAcrossAbiObserved:false,sourceFailureCauseIdentityClaim:false,instanceAfterFailedInitializationReused:false});
