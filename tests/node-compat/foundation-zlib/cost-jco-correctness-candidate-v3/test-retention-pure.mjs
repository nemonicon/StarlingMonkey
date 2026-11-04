// Pure byte/JSON retention tests only: no decoder, provider, Node-zlib, generated
// module, guest, worker, preflight or owner action is imported or invoked.
import assert from 'node:assert/strict';
import {Buffer} from 'node:buffer';
import {readFile,realpath} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {createNodeRetention,MAX_NODE_RETAINED_BINARY_BYTES} from './node-edges.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {stageRecord} from '../cost-guest-oracle-candidate-v2/contract.mjs';
const checks=[];
function check(name,fn){fn();checks.push({name,passed:true});}
async function asyncCheck(name,fn){await fn();checks.push({name,passed:true});}
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const requested=process.env.COST_JCO_RETENTION_PURE_OUTPUT;
assert.equal(typeof requested,'string','Fresh external owned scratch output required');
const root=join(await realpath(dirname(resolve(requested))),resolve(requested).split('/').at(-1));
assert.ok(!root.includes('/tests/node-compat/'),'No frozen/source packet output');
const output=await DurableOutput.create(root),retained=[];
const writes=[];
const write=async(path,value)=>{writes.push({path,kind:'json'});return output.write(path,value,{json:true});};
const writeBytes=async(path,value)=>{writes.push({path,kind:'binary'});return output.write(path,value);};
const retain=createNodeRetention({Buffer,write,writeBytes,retained,name:'actual-callback'});
async function binary(label,value,expected){
 const before=retained.length,row=await retain(label,value);
 assert.equal(row.path,'actual-callback-'+label+'.bin');assert.equal(row.bytes,expected.length);
 assert.equal(sha(await readFile(join(root,row.path))),sha(expected));
 assert.equal(retained.length,before+1);assert.strictEqual(retained.at(-1),row);
 assert.equal(writes.at(-1).kind,'binary');return row;
}
try{
 await asyncCheck('plain Uint8Array is full binary, not nonplain JSON',()=>binary('u8',new Uint8Array([1,2,3]),Buffer.from([1,2,3])));
 await asyncCheck('ordinary Buffer is full binary',()=>binary('buffer',Buffer.from([4,5,6]),Buffer.from([4,5,6])));
 const guarded=new Uint8Array([200,201,10,11,12,202,203]);
 await asyncCheck('Uint8Array subarray copies only byteOffset/byteLength window',()=>binary('u8-window',guarded.subarray(2,5),Buffer.from([10,11,12])));
 check('Uint8Array sentinels and source bytes stay unchanged',()=>assert.equal(Buffer.from(guarded).toString('hex'),'c8c90a0b0ccacb'));
 const pooled=Buffer.from([210,211,20,21,22,212]);
 await asyncCheck('Buffer subarray excludes surrounding backing bytes',()=>binary('buffer-window',pooled.subarray(2,5),Buffer.from([20,21,22])));
 check('Buffer sentinels stay unchanged',()=>assert.equal(pooled.toString('hex'),'d2d3141516d4'));
 await asyncCheck('empty Uint8Array persists an exclusive zero-byte binary',()=>binary('empty-u8',new Uint8Array(0),Buffer.alloc(0)));
 await asyncCheck('empty Buffer persists an exclusive zero-byte binary',()=>binary('empty-buffer',Buffer.alloc(0),Buffer.alloc(0)));
 const shadows=new Uint8Array([30,31]);let getterCalls=0;
 Object.defineProperties(shadows,{buffer:{get(){getterCalls++;throw new Error('own buffer getter must not run');}},byteOffset:{get(){getterCalls++;return 100;}},byteLength:{get(){getterCalls++;return 0;}}});
 await asyncCheck('intrinsic branded getters preserve actual view despite own shadows',()=>binary('shadowed-view',shadows,Buffer.from([30,31])));
 check('binary snapshot invokes no own window getter',()=>assert.equal(getterCalls,0));
 const mutable=new Uint8Array([41,42,43]);let forwarded;
 const delayed=createNodeRetention({Buffer,write,writeBytes:async(path,value)=>{forwarded=value;mutable.fill(99);await Promise.resolve();return writeBytes(path,value);},retained,name:'snapshot'});
 await asyncCheck('snapshot precedes asynchronous writer and caller mutation',async()=>{
  const row=await delayed('mutable',mutable);assert.notStrictEqual(forwarded,mutable);assert.notStrictEqual(forwarded.buffer,mutable.buffer);
  assert.equal((await readFile(join(root,row.path))).toString('hex'),'292a2b');assert.equal(Buffer.from(mutable).toString('hex'),'636363');
 });
 const jsonCases=[['object',{kind:'typed-return',value:7}],['array',[1,'two',null,true]],['null',null],['string','ordinary JSON string'],['boolean',false],['number',123]];
 for(const[label,value]of jsonCases)await asyncCheck('ordinary JSON '+label+' keeps strict JSON path',async()=>{const row=await retain('json-'+label,value);assert.equal(row.path,'actual-callback-json-'+label+'.json');assert.equal(JSON.stringify(JSON.parse(await readFile(join(root,row.path),'utf8'))),JSON.stringify(value));assert.equal(writes.at(-1).kind,'json');});
 const unknowns=[['uint16',new Uint16Array([1])],['data-view',new DataView(new ArrayBuffer(2))],['class',new(class Unknown{})()],['fake-buffer',Object.create(Buffer.prototype)],['u8-subclass',new(class UnknownU8 extends Uint8Array{})([1])],['function',()=>1]];
 for(const[label,value]of unknowns)await asyncCheck('unknown '+label+' is not widened into binary/JSON',async()=>{const before=retained.length;await assert.rejects(retain('reject-'+label,value));assert.equal(retained.length,before);});
 let accessorCalls=0;const accessor={};Object.defineProperty(accessor,'bad',{enumerable:true,get(){accessorCalls++;return 1;}});
 await asyncCheck('strict JSON rejection does not invoke unknown accessors',async()=>{await assert.rejects(retain('reject-accessor',accessor));assert.equal(accessorCalls,0);});
 await asyncCheck('unknown thenable object is not assimilated or coerced',async()=>{let calls=0;await assert.rejects(retain('reject-thenable',{then(){calls++;},toJSON(){calls++;}}));assert.equal(calls,0);});
 await asyncCheck('oversized binary refuses without clipping or writing',async()=>{const before=writes.length;await assert.rejects(retain('oversized',new Uint8Array(MAX_NODE_RETAINED_BINARY_BYTES+1)),/exceeds16MiB/);assert.equal(writes.length,before);});
 for(const label of['../escape','a/b','a\\b','', 'with space'])await asyncCheck('unsafe label refuses '+JSON.stringify(label),async()=>{const before=writes.length;await assert.rejects(retain(label,new Uint8Array([1])));assert.equal(writes.length,before);});
 const oraclePath='/private/tmp/starling-node-compat/zlib-cost-node-oracle-v3/node-oracle.json',oracleRaw=await readFile(oraclePath);
 check('genuine already-retained Node oracle is pinned as DATA',()=>assert.equal(sha(oracleRaw),'bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5'));
 const oracle=JSON.parse(oracleRaw),record=oracle.encodedStreams[0],checked=stageRecord(record);
 check('genuine contract.stageRecord produces ordinary Uint8Array, not Buffer',()=>{assert.equal(Object.getPrototypeOf(checked.bytes),Uint8Array.prototype);assert.equal(Buffer.isBuffer(checked.bytes),false);});
 await asyncCheck('genuine stageRecord checked.bytes reaches the actual callback as .bin',async()=>{const row=await binary('cross-input-'+record.streamId,checked.bytes,Buffer.from(record.encodedBase64,'base64'));assert.equal(row.sha256,record.encodedSha256);});
 await asyncCheck('legacy Buffer-only callback deterministically rejects that same U8',async()=>{const old=async(label,value)=>Buffer.isBuffer(value)?writeBytes('legacy-'+label+'.bin',value):write('legacy-'+label+'.json',value);await assert.rejects(old('cross-input',checked.bytes),/Plain JSON/);});
 const nodeSource=await readFile(new URL('./node-edges.mjs',import.meta.url),'utf8');
 check('the production Node-edge path uses the tested callback factory',()=>assert.equal(nodeSource.includes('const retain=createNodeRetention({Buffer,write,writeBytes,retained,name});'),true));
 await output.recheck();
 await output.write('results.json',{schemaVersion:1,state:'PURE_EXACT_WINDOW_NODE_RETENTION_CHECKS_PASSED_V3',passed:true,checks:checks.length,details:checks,providerCodecDecoderGuestPreflightWorkerOrOwnerActionsInvoked:0,genuinePinnedOracleDataRead:true,genuineStageRecordPureContractCalled:true,ordinaryDataRetentionOnly:true,corpusChanged:false},{json:true});
 await output.recheck();process.stdout.write(JSON.stringify({passed:true,checks:checks.length,providerCodecCalls:0,output:root})+'\n');
}finally{await output.close();}
