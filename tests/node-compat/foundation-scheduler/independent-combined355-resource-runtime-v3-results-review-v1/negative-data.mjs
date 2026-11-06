// Pure mutations of already retained DATA; no guest/module/API invocation.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateSession,validateWasmtime} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
const own=dirname(fileURLToPath(import.meta.url)),read=async p=>JSON.parse(await readFile(join(own,p))),rows=[];
for(let i=1;i<=23;i++)rows.push(await read('raw/actual/retained/raw/'+String(i).padStart(3,'0')+'.json'));
const fixture={id:'resource'},clone=x=>JSON.parse(JSON.stringify(x)),passed=[];
function reject(name,mutate){const r=clone(rows);mutate(r);assert.throws(()=>validateSession(fixture,'retained',r,collectors));passed.push(name);}
reject('missing whole return',r=>r.pop());
reject('typed number instead of string',r=>{r[1].observed={type:'number',value:1};});
reject('wrong public case argument',r=>r[1].args=[1]);
reject('wrong public sequence',r=>r[1].sequence++);
function change(i,fn){return r=>{const v=JSON.parse(r[i].observed.value);fn(v);r[i].observed.value=JSON.stringify(v);};}
reject('callback counter loss',change(1,v=>v.after.counters.timerCallbacks--));
reject('wrong strict receiver',change(1,v=>v.result.events[0].strictReceiverNull=false));
reject('wrong pressure checksum',change(1,v=>v.result.pressureChecksum--));
reject('double cancellation fired',change(2,v=>v.result.fired=1));
reject('interval missing callback',change(3,v=>v.result.events.pop()));
reject('nested victim fired',change(4,v=>v.result.victimCalls=1));
reject('invented sole temporary root proof',change(5,v=>v.result.soleTemporaryRootProved=true));
reject('handled exception identity mismatch',change(6,v=>v.result.same=false));
reject('retirement missing ID',change(7,v=>v.result.cleared.pop()));
reject('duplicate instance timer ID',change(1,v=>v.after.registeredIds[1]=v.after.registeredIds[0]));
reject('retained counter discontinuity',change(8,v=>v.before.counters.timerCallbacks++));
reject('final inspection discarded IDs',change(22,v=>v.state.registeredIds.pop()));
const decoded=await read('raw/actual/wasmtime-0.decoded.json'),wrapper=JSON.parse(decoded.value);
for(const [name,mutate]of [['missing within-export case',v=>v.records.pop()],['false interleaving proof',v=>v.separateHostCallInterleavingProved=true],['false reset proof',v=>v.resetOrReuseProved=true],['invented resource table',v=>v.before.state.hostResourceTableObserved=true]]){const v=clone(wrapper);mutate(v);assert.throws(()=>validateWasmtime(fixture,JSON.stringify(v),decoded.hostWallBeforeMs,decoded.hostWallAfterMs,collectors));passed.push(name);}
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_DATA_MUTATIONS_REFUSED',passed:passed.length,cases:passed,noOperationalActions:true}));
