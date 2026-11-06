// Pure mutations of retained survivor DATA only; no target/API/module action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateSession} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
const P=dirname(fileURLToPath(import.meta.url)),read=async n=>JSON.parse(await readFile(join(P,n))),rows=[];
for(let i=1;i<=3;i++)rows.push(await read('raw/actual/retained/raw/'+String(i).padStart(3,'0')+'.json'));
const clone=x=>JSON.parse(JSON.stringify(x)),passed=[];
function reject(name,mutate){const r=clone(rows);mutate(r);assert.throws(()=>validateSession({id:'surviving-interest'},'retained',r,collectors));passed.push(name);}
function change(i,fn){return r=>{const v=JSON.parse(r[i].observed.value);fn(v);r[i].observed.value=JSON.stringify(v);};}
reject('missing whole scalar',r=>r.pop());
reject('typed number instead of string',r=>r[0].observed={type:'number',value:1});
reject('unexpected public scalar argument',r=>r[0].args=[0]);
reject('wrong raw sequence',r=>r[1].sequence=1);
reject('retained call counter reset',change(1,v=>v.calls=1));
reject('wrong Promise values order',change(0,v=>v.values.reverse()));
reject('missing Promise value',change(0,v=>v.values.pop()));
reject('wrong survivor event order',change(0,v=>[v.events[1],v.events[3]]=[v.events[3],v.events[1]]));
reject('missing job checkpoint',change(0,v=>v.events.splice(2,1)));
reject('missing fence',change(0,v=>v.events.pop()));
reject('duplicate timer ID within a call',change(0,v=>v.ids[10]=v.ids[9]));
reject('zero timer ID',change(0,v=>v.ids[10]=0));
reject('missing cancelled timer',change(0,v=>v.cancelled.pop()));
reject('wrong cancelled timer order',change(0,v=>v.cancelled.reverse()));
reject('cancelled callback fired',change(0,v=>v.cancelledCallbacks=1));
reject('pending Promise unresolved',change(0,v=>v.pendingPromiseResolved=false));
reject('ID reused across retained calls',r=>{const a=JSON.parse(r[0].observed.value),b=JSON.parse(r[1].observed.value);b.ids=a.ids;b.cancelled=a.cancelled;r[1].observed.value=JSON.stringify(b);});
reject('invented native interest count',change(0,v=>v.nativeInterestCountObserved=true));
reject('invented all-invalid task-selection coverage',change(0,v=>v.allInvalidTaskSelectionExercised=true));
reject('invented native resource drop count',change(0,v=>v.nativeResourceDropsObserved=true));
reject('invented reset',change(0,v=>v.resetCalled=true));
reject('invented entropy request',change(0,v=>v.entropyRequested=true));
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_SURVIVOR_DATA_MUTATIONS_REFUSED',passed:passed.length,cases:passed,noOperationalActions:true}));
