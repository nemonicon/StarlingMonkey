// Actual guest-to-guest canonical ABI regression; final components require no host imports.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_IMPORT_ABI_OUTPUT ?? '/tmp/starling-node-compat/import-abi-regression');
assert(process.env.NODE_COMPAT_ENGINE);
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const metadata = JSON.parse(await readFile(engine + '.build.json'));
const hash = b => createHash('sha256').update(b).digest('hex');
assert.equal(metadata.engineSha256, hash(await readFile(engine)));
assert.equal(metadata.abiFixEnabled, true, 'Use the separate fixed scalar-export engine in both arms');
const toolchain = await loadToolchain();
const selected = await loadComponentizer(toolchain,{legacyDiagnostic:true});
assert(['patched-import-i32-v1','patched-import-i32-clock-v2'].includes(selected.provenance.selection));
const { componentWit, transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const stockDirectory = join(toolchain.directory, 'node_modules/@bytecodealliance/componentize-js');
const stock = await import(pathToFileURL(join(stockDirectory, 'src/componentize.js')));
const tools = resolve(process.env.NODE_COMPAT_WASM_TOOLS ?? '/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools');
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME ?? '/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
function exec(bin, args) { const r = spawnSync(bin,args,{encoding:'utf8',timeout:120000});assert.equal(r.status,0,r.error?.message ?? r.stderr);return r.stdout.trim(); }
assert.match(exec(tools,['--version']),/^wasm-tools 1\.235\.0\b/);
assert.match(exec(wasmtime,['--version']),/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});
await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const wit = await readFile(join(here,'import-v1.wit'),'utf8');
const source = await readFile(join(here,'import-v1-guest.mjs'),'utf8');
const helperSource = await readFile(join(here,'import-v1-helper.mjs'),'utf8');
const options = {engine,witWorld:wit,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event']};
const helper = await selected.componentize(helperSource,{...options,worldName:'helper'});
const helperPath = join(output,'helper.wasm');await writeFile(helperPath,helper.component);
const boundaries=[0,1,0x7fffffff,0x80000000,0x80000001,2342402100,0xfffffffe,0xffffffff];
let state=0x1a2b3c4d;const generated=Array.from({length:128},()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;});
function normalized(x) { if(ArrayBuffer.isView(x))return [...x];if(Array.isArray(x))return x.map(normalized);if(x&&typeof x==='object')return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,normalized(v)]));return x; }
const repr=x=>JSON.parse(JSON.stringify(x,(_,v)=>typeof v==='bigint'?v+'n':typeof v==='number'?(Object.is(v,-0)?'-0':Number.isFinite(v)?v:String(v)):v));
const variants=[];
for(const [name,componentize,mustPass] of [['stock-broken-control',stock.componentize,false],['patched-import-i32-v1',selected.componentize,true]]) {
 const app=await componentize(source,options);const appPath=join(output,name+'.app.wasm');await writeFile(appPath,app.component);
 const finalPath=join(output,name+'.wasm');exec(tools,['compose','--no-imports','-d',helperPath,'-o',finalPath,appPath]);
 const final=await readFile(finalPath);const emittedWit=await componentWit(final);assert.deepEqual(emittedWit.split('\n').filter(l=>/^\s*import /.test(l)),[]);
 const {files}=await transpile(final,{name});for(const [n,b]of Object.entries(files)){const p=join(output,n);await mkdir(dirname(p),{recursive:true});await writeFile(p,b);}
 console.error(name,'instantiate');
 const guest=await import(pathToFileURL(join(output,name+'.js')));
 console.error(name,'instantiated');
 const checks=[];function check(group,op,input,observed,expected){let matches=true;try{assert.deepEqual(normalized(observed),normalized(expected));}catch{matches=false;}checks.push({group,op,input:repr(input),observed:repr(observed),expected:repr(expected),matches});if(mustPass||group!=='u32-import')assert(matches,`${name} ${op}: ${String(observed)} != ${String(expected)}`);}
 console.error(name,'u32');
 for(const v of [...boundaries,...generated]){check('u32-import','directU32',v,guest.directU32(v),v);check('u32-import','computedU32',v,guest.computedU32(v),(v+0x80000000)>>>0);}
 check('u32-import','constantHigh',null,guest.constantHigh(),0x80000000);check('u32-import','constantMax',null,guest.constantMax(),0xffffffff);
 check('u32-return-control','helperConstant',null,guest.helperConstant(),0xffffffff);
 console.error(name,'s32');
 for(const v of [-2147483648,-123456789,-1,0,1,123456789,2147483647])check('s32-control','directS32',v,guest.directS32(v),v);
 console.error(name,'float');
 for(const v of [-Infinity,-123.5,-0,0,1,2147483648,4294967295,Math.PI,Infinity,NaN]){check('float-control','directF32',v,guest.directF32(v),Math.fround(v));check('float-control','directF64',v,guest.directF64(v),v);}
 console.error(name,'u64');
 for(const v of [0n,1n,0x7fffffffn,0x80000000n,0xffffffffn,0x8000000000000000n,0xffffffffffffffffn])check('i64-control','directU64',v,guest.directU64(v),v);
 console.error(name,'s64');
 for(const v of [0n,1n,0x7fffffffffffffffn])check('i64-control','directS64',v,guest.directS64(v),v);
 console.error(name,'list');
 for(const v of [[],boundaries,generated])check('indirect-control','listU32',v,guest.listU32(new Uint32Array(v)),v);
 console.error(name,'record');
 for(const value of JSON.parse(guest.recordCheck()))check('u32-import','recordCheck',value.input,value.observed,value.input);
 // A multi-argument result uses the same I32 import reader for its flattened u32 argument.
 console.error(name,'result');
 for(const v of boundaries){check('u32-import','resultU32-ok',v,guest.resultU32(true,v),v);let thrown;try{guest.resultU32(false,v);}catch(e){thrown=e.payload;}check('u32-import','resultU32-err',v,thrown,v);}
 const invokes=[['direct-u32(2147483648)','2147483648','u32-import'],['constant-max()','4294967295','u32-import'],['helper-constant()','4294967295','control'],['direct-s32(-2147483648)','-2147483648','control'],['direct-u64(18446744073709551615)','18446744073709551615','control'],['direct-s64(9223372036854775807)','9223372036854775807','control'],['list-u32([2147483648,4294967295])','[2147483648,4294967295]','control']];
 const wasmtimeChecks=[];for(const [call,expected,group]of invokes){const observed=exec(wasmtime,['run','--invoke',call,finalPath]).replace(/\s/g,'');const matches=observed===expected;if(mustPass||group==='control')assert(matches,`${call}: ${observed}`);wasmtimeChecks.push({call,expected,observed,matches});}
 const negativeI64 = spawnSync(wasmtime,['run','--invoke','direct-s64(-9223372036854775808)',finalPath],{encoding:'utf8',timeout:120000});assert.notEqual(negativeI64.status,0,'Separate negative-s64 defect must remain explicit');
 if(!mustPass)assert(checks.some(c=>!c.matches),'Stock control must fail');
 variants.push({name,legacyEngineDiagnosticAudit:app.legacyEngineDiagnosticAudit??null,componentPath:finalPath,componentSha256:hash(final),componentBytes:final.length,emittedImports:[],emittedWit,checks,wasmtimeChecks,negativeI64KnownIssue:{call:'direct-s64(-9223372036854775808)',status:negativeI64.status,stderr:negativeI64.stderr,scope:'Pre-existing native from_bigint64 accepts Uint64 only; independent of imported-I32 patch'},passed:checks.filter(c=>c.matches).length,failed:checks.filter(c=>!c.matches).length});
}
const report={schemaVersion:1,builtAtUtc:new Date().toISOString(),node:process.version,engine,engineSha256:metadata.engineSha256,scalarExportFix:true,packaging:selected.provenance,sourceSha256:hash(source),witSha256:hash(wit),helperSourceSha256:hash(helperSource),helperComponentSha256:hash(helper.component),helperComponentPath:helperPath,tools:{wasmTools:exec(tools,['--version']),wasmToolsSha256:hash(await readFile(tools)),wasmtime:exec(wasmtime,['--version']),wasmtimeSha256:hash(await readFile(wasmtime))},variants,scope:'All callbacks run from application guest to helper guest through actual canonical bindings. Final components import no host services. No u32 signed-carrier workaround.'};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,selected.provenance.selection==='patched-import-i32-clock-v2'?'import-v2-results.json':'import-v1-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(variants.map(v=>({name:v.name,passed:v.passed,failed:v.failed,wasmtime:v.wasmtimeChecks.filter(c=>c.matches).length})),null,2));
