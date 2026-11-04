// Owned host JSON records only. No workload, guest, artifact or backend import.
import assert from 'node:assert/strict';
import {writeFile,readFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {inspect} from 'node:util';
import {requireExactJSON,RecordedMismatch} from './bounded-comparison.mjs';
assert.equal(process.argv.length,3);const output=resolve(process.argv[2]);assert(output.startsWith('/tmp/starling-node-compat/'));await mkdir(output,{recursive:false});
let writes=0;const checks=[],pass=name=>checks.push(name);
const writer=async record=>{writes++;await writeFile(join(output,'counterexample.json'),JSON.stringify(record),{flag:'wx'});};
const expected=Array.from({length:2000},(_,index)=>({index,trace:['complete',index]})),actual=JSON.parse(JSON.stringify(expected));actual[1999].trace[1]=-1;
let inspected=0;actual[inspect.custom]=()=>{inspected++;throw new Error('Unexpected assert inspection');};
await requireExactJSON({label:'equal',actual:expected,expected,writeCounterexample:writer});assert.equal(writes,0);pass('complete equal record needs no write or error');
let caught;try{await requireExactJSON({label:'owned-last-row',actual,expected,context:{stdout:'complete owned raw carrier'},writeCounterexample:writer});}catch(error){caught=error;}
assert(caught instanceof RecordedMismatch);assert(caught.message.length<120);assert.equal(writes,1);assert.equal(inspected,0);pass('full mismatch written once before short error without assert inspection');
const saved=JSON.parse(await readFile(join(output,'counterexample.json')));assert.deepEqual(saved.actual,JSON.parse(JSON.stringify(actual)));assert.deepEqual(saved.expected,expected);assert.equal(saved.context.stdout,'complete owned raw carrier');pass('last-row/full records and raw context retained without truncation');
let failed;try{await requireExactJSON({label:'writer-failure',actual:[1],expected:[2],writeCounterexample:async()=>{throw new Error('Owned writer refused');}});}catch(error){failed=error;}
assert(!(failed instanceof RecordedMismatch));assert.equal(failed.message,'Owned writer refused');pass('writer failure propagates without claiming recorded mismatch');
await writeFile(join(output,'results.json'),JSON.stringify({schemaVersion:1,state:'BOUNDED_EXACT_JSON_REPORTING_SOURCE_TESTS_PASSED',passed:checks.length,checks,ownerGuestOrWorkloadOrNativeOrPackagerOrHostInvoked:false},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:checks.length,output}));
