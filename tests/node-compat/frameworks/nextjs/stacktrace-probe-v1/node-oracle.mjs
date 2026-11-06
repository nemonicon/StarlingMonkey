// Root must separately authorize this host-only Node oracle.
import assert from 'node:assert/strict';
import {collectStacktraceProbe} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
console.log(JSON.stringify({kind:'node-oracle-identity',node:process.version,v8:process.versions.v8,guestExecuted:false}));
for(let call=1;call<=3;call++){const value=JSON.stringify(collectStacktraceProbe(call));console.log(JSON.stringify({call,kind:typeof value,value}));}
