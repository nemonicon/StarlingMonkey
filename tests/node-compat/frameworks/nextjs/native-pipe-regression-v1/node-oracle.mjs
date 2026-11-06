// Dormant host-only Node oracle. A separate Root grant and owned monitor are required.
import assert from 'node:assert/strict';
import {collectPipeProbe} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
const originalPipeTo=ReadableStream.prototype.pipeTo;
console.log(JSON.stringify({kind:'node-oracle-identity',node:process.version,v8:process.versions.v8,suite:'NATIVE_SIGNAL_PIPE_REGRESSION_V1',candidateInstalled:false,guestExecuted:false}));
for(let call=1;call<=3;call++){const value=JSON.stringify(await collectPipeProbe(call,originalPipeTo));console.log(JSON.stringify({call,kind:typeof value,value}));}
