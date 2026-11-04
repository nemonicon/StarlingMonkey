'use strict';
const assert=require('node:assert/strict');
assert.equal(process.version,'v22.14.0');
let reads=0;
process.nextTick(()=>({get then(){reads++;return undefined;}}));
setImmediate(()=>{
 assert.equal(reads,0);
 process.stdout.write(JSON.stringify({node:process.version,reads,scope:'Benign own then getter on ignored nextTick return object; no callable then/prototype poisoning',guestExecuted:false})+'\n');
});
