// Execute only the actual extracted call body against fake session/writer DATA seams.
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const text=await readFile(new URL('./worker.mjs',import.meta.url),'utf8'),start=text.indexOf('  async function call('),end=text.indexOf('\n  let c=zeroCounters()',start);assert(start>=0&&end>start);const body=text.slice(start,end),cases=[];
async function scenario(name,{value='{"ok":true}',invokeThrow=false,writeThrow=false,expectedWritten,expectedSuccess}){
 const saved=[];const context=vm.createContext({need:(v,m)=>assert(v,m),session:{invoke(){if(invokeThrow)throw new Error('fake-session-data-error');return value;}},out:{async write(name,row){if(writeThrow)throw new Error('fake-writer-data-error');saved.push({name,row});}}});
 vm.runInContext('let seq=0,rawWritten=0;'+body+';this.run=async()=>{let ok=true;try{await call("inspect",[]);}catch{ok=false;}return{ok,seq,rawWritten};};',context,{timeout:1000});const r=await context.run();assert.equal(r.seq,1);assert.equal(r.rawWritten,expectedWritten);assert.equal(saved.length,expectedWritten);assert.equal(r.ok,expectedSuccess);if(saved.length&&typeof value!=='string'&&!invokeThrow)assert.equal(saved[0].row.fullOpaqueValueClaim,false);cases.push({name,passed:true,attempts:r.seq,retained:r.rawWritten,accepted:r.ok});
}
await scenario('full valid string before parse',{expectedWritten:1,expectedSuccess:true});
await scenario('source invocation throw raw capture',{invokeThrow:true,expectedWritten:1,expectedSuccess:false});
await scenario('writer failure is not retained',{writeThrow:true,expectedWritten:0,expectedSuccess:false});
await scenario('non-string captured opaque before refusal',{value:{opaque:'model-only'},expectedWritten:1,expectedSuccess:false});
await scenario('invalid JSON retained whole before refusal',{value:'not json',expectedWritten:1,expectedSuccess:false});
await scenario('over-cap string written whole before refusal',{value:'x'.repeat(2*1024*1024+1),expectedWritten:1,expectedSuccess:false});
process.stdout.write(JSON.stringify({schemaVersion:1,state:'EXTRACTED_RAW_CAPTURE_DATA_SEAMS_PASSED_V1',cases,count:cases.length,ownerModulesImported:false,sessionAlwaysMocked:true,writerAlwaysMocked:true,guestOrKeyOrPressureInvoked:false})+'\n');
