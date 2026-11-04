// Actual stock Jco API host bundling. No componentizer, guest, target or timing.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),tool='/tmp/starling-node-compat/native-toolchain-lock',hash=b=>createHash('sha256').update(b).digest('hex');
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const pins=JSON.parse(await readFile(join(here,'tool-inputs.json'))),pinned=new Map(pins.inputs.map(row=>[row.path,row]));
for(const row of pins.inputs){const bytes=await readFile(row.path);assert.equal(hash(bytes),row.sha256);assert.equal(bytes.length,row.bytes);}
const own=[];for(const name of ['entry.mjs','workload.mjs','stock-provider.mjs']){const path=join(here,name),bytes=await readFile(path);own.push({path,sha256:hash(bytes),bytes:bytes.length});}
const jco=join(tool,'node_modules/@bytecodealliance/jco'),{bundleComponentChunk}=await import(pathToFileURL(join(jco,'dist/bundle.js'))),{nodeBuiltinPlugin,nodeGlobals}=await import(pathToFileURL(join(jco,'dist/node-builtins/index.js')));
const scheduler=await realpath(join(tool,'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/scheduler.js'));
const provider=join(here,'stock-provider.mjs'),stock=nodeBuiltinPlugin({imports:[],exports:[]},{}),resolutions=[],modules=new Set(),virtual=[];
const plugin={...stock,async resolveId(id,importer,extra){const result=await stock.resolveId.call(this,id,importer,extra);if(result!==null&&result!==undefined)resolutions.push({request:id,importer:importer??null,result});return result;},load(id){const value=stock.load.call(this,id);if(typeof value==='string')virtual.push({id,sha256:hash(value),bytes:Buffer.byteLength(value)});return value;}};
const chunk=await bundleComponentChunk(join(here,'entry.mjs'),{inject:nodeGlobals(),config:{treeshake:false},plugins:[{name:'finite-proposed-common-domain',resolveId(id){if(id==='benchmark:provider')return provider;if(id==='benchmark:stock-scheduler')return scheduler;return null;}},plugin,{name:'read-only-graph',moduleParsed(info){modules.add(info.id);}}]});
assert.deepEqual(chunk.imports,[]);assert.equal([...modules].filter(id=>id.endsWith('/stream/scheduler.js')).length,1);
assert(resolutions.some(row=>row.request==='process/'&&row.result===scheduler));
const physical=[];
for(const id of modules)if(isAbsolute(id)&&!id.startsWith('\0')){const bytes=await readFile(id),canonical=await realpath(id),before=pinned.get(canonical)??own.find(row=>row.path===id);assert(before,'Unpinned bundled source '+id);assert.equal(hash(bytes),before.sha256);assert.equal(bytes.length,before.bytes);physical.push({path:id,sha256:hash(bytes),bytes:bytes.length});}
for(const row of [...pins.inputs,...own])assert.equal(hash(await readFile(row.path)),row.sha256,row.path);
const out=resolve(process.env.NODE_COMPAT_COMMON_BYTE_BUNDLE_OUTPUT??'');assert(out.startsWith('/tmp/starling-node-compat/'));
try{await lstat(out);assert.fail('Choose fresh output');}catch(e){if(e.code!=='ENOENT')throw e;}await mkdir(out,{recursive:true});
await writeFile(join(out,'application.bundle.mjs'),chunk.code,{flag:'wx'});
await writeFile(join(out,'bundle-results.json'),JSON.stringify({schemaVersion:1,state:'UNMODIFIED_STOCK_JCO_COMMON_BYTE_SOURCE_GRAPH_VERIFIED',bundlePath:join(out,'application.bundle.mjs'),bundleSha256:hash(chunk.code),imports:chunk.imports,exports:chunk.exports,
 modules:[...modules].sort(),physicalSources:physical,virtualSources:virtual,resolutions,scheduler,providerOptions:{},schedulerOverride:false,sourceBeforeAfter:own,guestOrNativeOrTimingExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({imports:chunk.imports,modules:modules.size,out}));
