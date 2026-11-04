// Ordinary source bundle on pinned host Node; no Wasm/component execution.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const hash=b=>createHash('sha256').update(b).digest('hex');
const root=resolve(process.env.NODE_COMPAT_COMMON_BYTE_BUNDLE_OUTPUT??''),oraclePath=resolve(process.env.NODE_COMPAT_COMMON_BYTE_ORACLE??''),out=resolve(process.env.NODE_COMPAT_COMMON_BYTE_STOCK_OUTPUT??'');
for(const path of [root,oraclePath,out])assert(path.startsWith('/tmp/starling-node-compat/'));
try{await lstat(out);assert.fail('Choose fresh output');}catch(e){if(e.code!=='ENOENT')throw e;}await mkdir(out,{recursive:true});
const graph=JSON.parse(await readFile(join(root,'bundle-results.json'))),oracle=JSON.parse(await readFile(oraclePath));assert.deepEqual(graph.imports,[]);assert.equal(graph.schedulerOverride,false);assert.equal(hash(await readFile(graph.bundlePath)),graph.bundleSha256);
const stock=await import(pathToFileURL(graph.bundlePath)),cases=[];
for(const row of oracle.cases){assert.equal(stock.setup(row.id),row.setup);const observed=JSON.parse(await stock.inspect(row.iterations));cases.push({id:row.id,iterations:row.iterations,expected:row.expected,observed,checksumEqual:observed.unsignedChecksum===row.expected.unsignedChecksum,traceExact:JSON.stringify(observed)===JSON.stringify(row.expected)});}
await writeFile(join(out,'stock-results.json'),JSON.stringify({schemaVersion:1,state:'NARROW_COMMON_BYTE_STOCK_HOST_TRACE_OBSERVATIONS',cases,bundleSha256:graph.bundleSha256,
 original39774Changed:false,providerOrSchedulerModified:false,guestOrNativeOrTimingExecuted:false,actualGuestCorrectnessRequiredBeforeTiming:true},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({cases:cases.length,checksums:cases.filter(row=>row.checksumEqual).length,traceExact:cases.filter(row=>row.traceExact).length,out}));
