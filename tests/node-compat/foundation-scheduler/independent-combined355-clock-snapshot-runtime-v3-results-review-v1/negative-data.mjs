// Mutations of retained clock DATA only; no application/guest operation.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateSession} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
const P=dirname(fileURLToPath(import.meta.url)),read=async n=>JSON.parse(await readFile(join(P,n))),rows=[];
for(let i=1;i<=3;i++)rows.push(await read('raw/actual/retained/raw/'+String(i).padStart(3,'0')+'.json'));
const clone=x=>JSON.parse(JSON.stringify(x)),passed=[];
function reject(name,mutate){const r=clone(rows);mutate(r);assert.throws(()=>validateSession({id:'clock-snapshot'},'retained',r,collectors));passed.push(name);}
function change(i,fn){return r=>{const v=JSON.parse(r[i].observed.value);fn(v);r[i].observed.value=JSON.stringify(v);};}
reject('missing retained whole string',r=>r.pop());
reject('raw typed number',r=>r[0].observed={type:'number',value:1});
reject('wrong public scalar arguments',r=>r[0].args=[0]);
reject('wrong raw call ordinal',r=>r[1].sequence=1);
reject('initial job did not drain',change(0,v=>v.initialization.jobs=0));
reject('module evaluated twice',change(0,v=>v.initialization.moduleEvaluations=2));
reject('retained initialization changed',change(1,v=>v.initialization.dateNow++));
reject('retained public call counter reset',change(1,v=>v.calls=1));
reject('Date ISO differs from full Date object',change(0,v=>v.before.iso='2000-01-01T00:00:00.000Z'));
reject('monotonic time decreases within export',change(0,v=>v.after.performanceNow=v.before.performanceNow-1));
reject('timeOrigin changes within export',change(0,v=>v.after.timeOrigin++));
reject('retained timeOrigin changes',change(1,v=>{v.before.timeOrigin++;v.after.timeOrigin++;}));
reject('missing timer callback',change(0,v=>v.callbacks=0));
reject('reported elapsed does not match full samples',change(0,v=>v.elapsed++));
reject('Date outside own whole-call wall bracket',change(0,v=>v.before.dateNow=rows[0].hostWallBeforeMs-2));
reject('decreasing host wall bracket',r=>r[0].hostWallAfterMs=r[0].hostWallBeforeMs-1);
reject('invented native monotonic-offset observation',change(0,v=>v.nativeMonotonicOffsetObserved=true));
reject('invented initialization performance read',change(0,v=>v.initPerformanceCalled=true));
reject('invented exact host clock oracle',change(0,v=>v.hostClockValuesAreExactOracle=true));
reject('invented reset',change(0,v=>v.resetCalled=true));
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_CLOCK_DATA_MUTATIONS_REFUSED',passed:passed.length,cases:passed,noOperationalActions:true}));
