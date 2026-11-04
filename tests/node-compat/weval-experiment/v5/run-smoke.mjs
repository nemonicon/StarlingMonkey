import assert from 'node:assert/strict';
import {Buffer} from 'node:buffer';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {bundleProfile} from '../../profile-bundler.mjs';
import {loadWevalContext} from './load-context.mjs';
import {runBufferCases} from './smoke-cases.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const ctx=await loadWevalContext(),output=resolve(process.env.NODE_COMPAT_WEVAL_SMOKE_OUTPUT??'/tmp/starling-node-compat/weval-experiment/v5-smoke');
await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),engine:ctx.engine})+'\n',{flag:'wx'});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const sourceFiles=[];
for(const name of ['run-smoke.mjs','load-context.mjs','smoke-cases.mjs','smoke-component.mjs','smoke.wit','pins.json','build-receipt.json']){const bytes=await readFile(join(here,name));await mkdir(join(output,'source'),{recursive:true});await writeFile(join(output,'source',name),bytes);sourceFiles.push({name,sha256:hash(bytes)});}
const bundle=await bundleProfile({rolldown:ctx.toolchain.rolldown,parseAst:ctx.toolchain.parseAst,input:join(here,'smoke-component.mjs'),builtinManifests:ctx.manifests});
assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:events','node:path']);assert.match(bundle.code,/import\(\s*['"]node:child_process['"]\s*\)/,'Keep first deployed native import dynamic');await writeFile(join(output,'bundle.mjs'),bundle.code);
const wit=await readFile(join(here,'smoke.wit'),'utf8');
const{component,interfaceAudit}=await ctx.componentize(bundle.code,{witWorld:wit,worldName:'profile'}),componentPath=join(output,'smoke.component.wasm');await writeFile(componentPath,component);
const{componentWit,transpile}=await import(pathToFileURL(ctx.toolchain.require.resolve('@bytecodealliance/jco'))),emittedWit=await componentWit(component);
assert.deepEqual(emittedWit.split('\n').filter(line=>/^\s*import /.test(line)),[]);assert.equal((emittedWit.match(/^\s*export /gm)??[]).length,12);await writeFile(join(output,'component.wit'),emittedWit);
const{files}=await transpile(component,{name:'smoke'});for(const[name,bytes]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,bytes);}
const guest=await import(pathToFileURL(join(output,'smoke.js'))),reports=[],expectedBuffer=runBufferCases(Buffer);let checks=0;
const check=(observed,expected,label)=>{assert.deepEqual(observed,expected,label);checks++;};
for(let call=1;call<=3;call++){const report=JSON.parse(guest.run());check(report,{calls:call,buffer:expectedBuffer,snapshotHex:Buffer.from('snapshot\u00e9').toString('hex'),backingIdentityPreserved:true,unsupportedCode:'ERR_SM_NODE_UNSUPPORTED',firstDeployedDynamicImport:true,eventCalls:1,path:'/b/c'},'native module/snapshot smoke');reports.push(report);}
for(const value of [0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff])check(guest.directU32(value),value,'u32');check(guest.constantMax(),0xffffffff,'u32 constant');
for(const value of [-2147483648,-1,0,2147483647])check(guest.directS32(value),value,'s32');
for(const value of [-Infinity,-123.5,-0,0,Math.PI,2147483648,4294967295,Infinity,NaN]){check(guest.directF32(value),Math.fround(value),'f32');check(guest.directF64(value),value,'f64');}
for(const value of [0n,1n,0x7fffffffffffffffn,0x8000000000000000n,0xffffffffffffffffn])check(guest.directU64(value),value,'u64');
for(const value of [-0x8000000000000000n,-1n,0n,1n,0x7fffffffffffffffn])check(guest.directS64(value),value,'s64');
for(const value of ['','A\0\u00e9\uD83D\uDE42'])check(guest.echoString(value),value,'string');
for(const value of [new Uint8Array(0),new Uint8Array([0,1,127,128,255])])check([...guest.echoBytes(value)],[...value],'list');
const record={unsigned:0xffffffff,signed:-2147483648,large:0xffffffffffffffffn,negative:-0x8000000000000000n,text:'record\u00e9',bytes:new Uint8Array([0,255])};
const echoed=guest.echoRecord(record);check({...echoed,bytes:[...echoed.bytes]},{...record,bytes:[...record.bytes]},'record');
check(guest.resultU32(true,0xffffffff),0xffffffff,'result ok');let thrown;try{guest.resultU32(false,0x80000000);}catch(error){thrown=error.payload;}check(thrown,0x80000000,'result err');
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const invoke=call=>{const result=spawnSync(wasmtime,['run','--invoke',call,componentPath],{encoding:'utf8',timeout:120000,maxBuffer:1048576});assert.equal(result.status,0,result.stderr);return result.stdout.trim();};
const wave=invoke('run()').replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,number)=>String.fromCodePoint(parseInt(number,16))),hostReport=JSON.parse(JSON.parse(wave));check(hostReport,{...reports[0]},'fresh Wasmtime run');
const hostChecks=[];for(const[call,expected]of [['direct-u32(2147483648)','2147483648'],['constant-max()','4294967295'],['direct-s32(-2147483648)','-2147483648'],['direct-u64(18446744073709551615)','18446744073709551615'],['direct-s64(-9223372036854775808)','-9223372036854775808'],['echo-bytes([0,128,255])','[0,128,255]'],['result-u32(true,4294967295)','ok(4294967295)'],['result-u32(false,2147483648)','err(2147483648)']]){const observed=invoke(call).replace(/\s/g,'');check(observed,expected,call);hostChecks.push({call,observed,expected});}
const initialization=[];
for(const[name,source,marker]of [
  ['unsupported-call',"import {spawn} from 'node:child_process'; spawn(); export function run(){return 'unreachable'}",'node:child_process.spawn is unavailable'],
  ['unsupported-construct',"import {ChildProcess} from 'node:child_process'; new ChildProcess(); export function run(){return 'unreachable'}",'node:child_process.ChildProcess is unavailable'],
  ['unhandled-initializer',"Promise.reject(new Error('WEVAL_STRICT_INITIALIZER')); export function run(){return 'unreachable'}",'WEVAL_STRICT_INITIALIZER'],
]){let error;try{await ctx.componentize(source,{witWorld:'package starling:weval-init@0.1.0; world profile { export run: func() -> string; }',worldName:'profile'});}catch(caught){error=String(caught);}
  assert(error&&error.includes(marker),name+': expected initialization failure');initialization.push({name,sourceSha256:hash(source),marker,rejected:true,error});}
await ctx.verify();for(const entry of sourceFiles)assert.equal(hash(await readFile(join(here,entry.name))),entry.sha256,entry.name);
const report={schemaVersion:1,atUtc:new Date().toISOString(),passed:true,provenance:ctx.provenance,sourceFiles,sourcesVerifiedBeforeAndAfter:true,bundleSha256:hash(bundle.code),witSha256:hash(wit),componentPath,componentSha256:hash(component),componentBytes:component.length,emittedImports:[],emittedWit,interfaceAudit,checks,reports,hostReport,hostChecks,initialization,wasmtime:{path:wasmtime,sha256:hash(await readFile(wasmtime))},scope:'Valid ordinary Release public WIT scalar/string/list/record/result and native Buffer/path/events/stub checks, including a first deployed uncached dynamic builtin import. No custom host interface, DEBUG, fault simulation, raw memory or private introspection. This bounded smoke is not the complete canonical ABI or codec/Buffer corpus.'};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,checks,componentSha256:report.componentSha256,emittedImports:[],initialization:initialization.map(value=>value.name),output},null,2));
