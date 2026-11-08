// Root-owned finite parent-Node I/O tests. No child process, Wasm or network.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,open,readFile,realpath,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {Readable,PassThrough} from 'node:stream';
import {setTimeout as pause} from 'node:timers/promises';
import {fileURLToPath} from 'node:url';
import {captureRawStdout} from '../next-guest-completion-runtime-candidate-v1/capture-stdout.mjs';

assert.equal(process.version,'v22.14.0');
assert.equal(process.argv.length,3);
const output=resolve(process.argv[2]);
assert(output.startsWith('/private/tmp/starling-node-compat/next-guest-stdout-capture-unit-'));
await mkdir(output,{mode:0o700}); // Exclusive new directory; never overwrite a prior test.
assert.equal(await realpath(output),output);
const helper=fileURLToPath(new URL('../next-guest-completion-runtime-candidate-v1/capture-stdout.mjs',import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const source=await readFile(helper);
assert.equal(hash(source),'bedbbf2146373c0b9f2e65b81454a4d9d4db26e1c259eb4617496d7033218781');
const limit=8*1024*1024,records=[];

async function within(promise){
  let timer;
  try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Finite capture test exceeded10s')),10000);})]);}
  finally{clearTimeout(timer);}
}
async function setup(name,readable,decorate=handle=>handle){
  const path=join(output,name+'.stdout.bin'),real=await open(path,'wx',0o600);
  const cap=captureRawStdout({readable,handle:decorate(real),path,limitBytes:limit});
  return{path,real,cap};
}
async function finish(name,test,expected,complete){
  const state=await within(test.cap.done),bytes=await readFile(test.path);
  assert(bytes.equals(expected),name+': exact retained bytes');
  assert(bytes.length<=limit,name+': hard file bound');
  assert.equal(state.fileBytes,bytes.length);
  assert.equal(state.complete,complete);
  assert.equal(state.fileClosed,true);
  assert.equal(state.fileBoundVerified,true);
  await assert.rejects(async()=>test.real.stat(),error=>error.code==='EBADF');
  records.push({name,passed:true,bytes:bytes.length,sha256:hash(bytes),capture:state});
  return state;
}
function wrapper(real,overrides){
  return{stat:real.stat.bind(real),writeFile:real.writeFile.bind(real),sync:real.sync.bind(real),close:real.close.bind(real),...overrides};
}
async function waitForBytes(test,size){
  for(let n=0;n<1000;n++){
    if((await test.real.stat()).size===size)return;
    await pause(2);
  }
  throw Error('Expected retained prefix did not arrive');
}

await finish('empty',await setup('empty',Readable.from([])),Buffer.alloc(0),true);
const first=Buffer.from([0,255,13,10,128]),second=Buffer.from('raw\nbytes');
await finish('binary-chunks',await setup('binary-chunks',Readable.from([first,second])),Buffer.concat([first,second]),true);
const exact=Buffer.alloc(limit,0x5a);
await finish('exact-cap',await setup('exact-cap',Readable.from([exact])),exact,true);

const prefix=Buffer.alloc(4*1024*1024,0x31),rejected=Buffer.alloc(5*1024*1024,0x32);
const overflow=await finish('overflow-whole-chunk',await setup('overflow-whole-chunk',Readable.from([prefix,rejected])),prefix,false);
assert.equal(overflow.overflow,true);
assert.equal(overflow.rejectedWholeChunkBytes,rejected.length);
assert.equal(overflow.unretainedBytesUnknown,true);
assert(overflow.errors.some(error=>error.stage==='stdout-limit'));

const pendingInput=new PassThrough(),pending=await setup('eof-required',pendingInput);
let settled=false;void pending.cap.done.then(()=>{settled=true;});
pendingInput.write(Buffer.from('before'));
await waitForBytes(pending,6);
assert.equal(settled,false,'Written bytes alone cannot finalize a live pipe');
pendingInput.end(Buffer.from('-after'));
await finish('eof-required',pending,Buffer.from('before-after'),true);

const partialBytes=Buffer.alloc(64,0x44);
const partial=await setup('partial-write',Readable.from([partialBytes]),real=>wrapper(real,{
  async writeFile(bytes){await real.writeFile(bytes.subarray(0,3));throw Object.assign(Error('Synthetic partial write'),{code:'EIO'});},
}));
const partialState=await finish('partial-write',partial,partialBytes.subarray(0,3),false);
assert.equal(partialState.partialWritePossible,true);
assert.equal(partialState.completeWriteBytes,0);
assert.equal(partialState.lastReservedWriteCeiling,64);

let closeAttempts=0;
const syncError=await setup('sync-failure',Readable.from([Buffer.from('sync')]),real=>wrapper(real,{
  async sync(){throw Object.assign(Error('Synthetic sync rejection'),{code:'EIO'});},
  async close(){closeAttempts++;await real.close();},
}));
const syncState=await finish('sync-failure',syncError,Buffer.from('sync'),false);
assert.equal(closeAttempts,1,'A sync rejection must still close the descriptor');
assert(syncState.errors.some(error=>error.stage==='stdout-sync'));

const abortInput=new PassThrough(),aborted=await setup('abort-pending',abortInput);
abortInput.write(Buffer.from('prefix'));
await waitForBytes(aborted,6);
aborted.cap.abort('finite-test-pending-pipe');
const abortedState=await finish('abort-pending',aborted,Buffer.from('prefix'),false);
assert.equal(abortedState.pipeEof,false);
assert.equal(abortedState.unretainedBytesUnknown,true);
assert(abortedState.errors.some(error=>error.stage==='capture-aborted'));

// A close rejection cannot establish finalization even when a test double closed
// the real fd before rejecting; production must preserve that uncertainty.
const closeError=await setup('close-failure',Readable.from([Buffer.from('close')]),real=>wrapper(real,{
  async close(){await real.close();throw Object.assign(Error('Synthetic close rejection'),{code:'EIO'});},
}));
const closeState=await within(closeError.cap.done),closeRaw=await readFile(closeError.path);
assert(closeRaw.equals(Buffer.from('close')));
assert.equal(closeState.complete,false);assert.equal(closeState.finalized,false);
assert.equal(closeState.fileClosed,false);assert(closeState.errors.some(error=>error.stage==='stdout-close'));
await assert.rejects(async()=>closeError.real.stat(),error=>error.code==='EBADF');
records.push({name:'close-failure',passed:true,bytes:closeRaw.length,sha256:hash(closeRaw),capture:closeState});

const report={schemaVersion:1,state:'FINITE_PARENT_STDOUT_CAPTURE_UNIT_TESTS_PASSED_V1',passed:true,
  nodeVersion:process.version,helper:{path:helper,sha256:hash(source),bytes:source.length},output,
  caseCount:records.length,records,syntheticNodeIoOnly:true,wasmGuestOrWasmtimeOrNetworkExecuted:false};
const reportPath=join(output,'unit-results.json'),reportHandle=await open(reportPath,'wx',0o600);
try{await reportHandle.writeFile(JSON.stringify(report,null,2)+'\n');await reportHandle.sync();}finally{await reportHandle.close();}
console.log(JSON.stringify({passed:true,caseCount:records.length,report:reportPath,
  bytesWritten:records.reduce((sum,record)=>sum+record.bytes,0),wasmGuestOrWasmtimeOrNetworkExecuted:false}));
