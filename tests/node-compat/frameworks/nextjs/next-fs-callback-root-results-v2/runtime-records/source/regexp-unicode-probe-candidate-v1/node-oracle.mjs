// UNEXECUTED host-only oracle Source. Root must authorize before invocation.
import assert from 'node:assert/strict';
import {collectRegExpProbe} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
console.log(JSON.stringify({kind:'node-oracle-identity',node:process.version,v8:process.versions.v8,unicode:process.versions.unicode,icu:process.versions.icu,guestExecuted:false}));
for(let call=1;call<=3;call++){
 const result=collectRegExpProbe(call),value=JSON.stringify(result);
 console.log(JSON.stringify({call,kind:typeof value,value}));
}
