// Actual-entry host bundling only. Never componentizes or starts a target host.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),tool='/tmp/starling-node-compat/native-toolchain-lock';
const hash=b=>createHash('sha256').update(b).digest('hex');
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const pinned=JSON.parse(await readFile(join(here,'tool-inputs.json')));
for(const row of pinned.inputs){const bytes=await readFile(row.path);assert.equal(hash(bytes),row.sha256,row.path);assert.equal(bytes.length,row.bytes,row.path);}
const extension=resolve(here,'../measurement-extension-candidate-v1'),extensionBytes=await readFile(join(extension,'input-freeze.json'));
assert.equal(hash(extensionBytes),'ffaa680b9e30eb26499c335e041ba650f384866ae7d11792a7d4ebcb0df8519b');
const sourceChecks=JSON.parse(extensionBytes).inputs.map(row=>({...row,path:resolve(extension,row.path)}));
for(const name of ['workload.mjs','entry.mjs','timing-entry.mjs','native-provider.mjs','canonical-provider.mjs','stock-provider.mjs']){const path=join(here,name),bytes=await readFile(path);sourceChecks.push({path,sha256:hash(bytes),bytes:bytes.length});}
for(const row of sourceChecks){const bytes=await readFile(row.path);assert.equal(hash(bytes),row.sha256,row.path);assert.equal(bytes.length,row.bytes,row.path);}
const jco=join(tool,'node_modules/@bytecodealliance/jco');
const {bundleComponentChunk}=await import(pathToFileURL(join(jco,'dist/bundle.js')));
const {nodeBuiltinPlugin,nodeGlobals}=await import(pathToFileURL(join(jco,'dist/node-builtins/index.js')));
const scheduler=await realpath(join(tool,'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/scheduler.js'));
const output=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_BUNDLE_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Choose fresh host bundle output');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(output,{recursive:true});
const reports=[];
for(const arm of ['native','canonical','stock']){
 const physical=new Map(),virtual=new Map(),resolutions=[],modules=new Set();
 const provider=join(here,arm+'-provider.mjs');
 const stock=nodeBuiltinPlugin({imports:[],exports:[]},{});
 const stockPlugin={...stock,resolveId:async function(id,importer,extra){const result=await stock.resolveId.call(this,id,importer,extra);if(result!==null&&result!==undefined)resolutions.push({request:id,importer:importer??null,result});return result;},
  load:function(id){const result=stock.load.call(this,id);if(typeof result==='string')virtual.set(id,result);return result;}};
 const finite={name:'finite-benchmark-provider-selection',resolveId(id,importer){
  if(id==='benchmark:provider'){resolutions.push({request:id,importer,result:provider});return provider;}
  if(arm==='stock'&&id==='benchmark:stock-scheduler'){resolutions.push({request:id,importer,result:scheduler});return scheduler;}
  if(arm!=='stock'&&(id.startsWith('node:')||id==='starling:test-classic-benchmark'))return{id,external:true};
  return null;}};
 const inspection={name:'read-only-benchmark-graph',moduleParsed(info){modules.add(info.id);}};
 const chunk=await bundleComponentChunk(join(here,'entry.mjs'),{plugins:[finite,...(arm==='stock'?[stockPlugin]:[]),inspection],
  ...(arm==='stock'?{inject:nodeGlobals()}:{}),config:{treeshake:false}});
 if(arm==='stock')assert.deepEqual(chunk.imports,[]);else assert.deepEqual([...chunk.imports].sort(),['node:buffer','node:events','node:stream','node:stream/promises','node:string_decoder','starling:test-classic-benchmark'].filter(id=>arm==='native'||!['node:stream','node:stream/promises'].includes(id)).sort());
 for(const id of modules){if(isAbsolute(id)&&!id.startsWith('\0')){const stat=await lstat(id);assert(stat.isFile()&&!stat.isSymbolicLink());const bytes=await readFile(id);physical.set(id,{path:id,sha256:hash(bytes),bytes:bytes.length});}}
 const directory=join(output,arm);await mkdir(directory);
 await writeFile(join(directory,'application.bundle.mjs'),chunk.code,{flag:'wx'});
 await writeFile(join(directory,'graph-before-contract.json'),JSON.stringify({resolutions,moduleIds:[...modules].sort()},null,2)+'\n',{flag:'wx'});
 for(const [index,[id,source]]of [...virtual].entries())await writeFile(join(directory,'virtual-'+index+'.mjs'),source,{flag:'wx'});
 if(arm==='stock'){
  assert(!chunk.imports.some(id=>id.startsWith('node:')||id.startsWith('jco:node/')||id==='starling:test-classic-benchmark'));
  assert([...modules].some(id=>id===scheduler));
  const coreImporter=[...modules].find(id=>id.replaceAll('\\','/').endsWith('/readable-stream/lib/internal/streams/readable.js'));assert(coreImporter);
  assert(resolutions.some(row=>row.request==='process/'&&row.result===scheduler&&row.importer?.includes('/readable-stream/lib/')));
  assert([...virtual.values()].some(source=>source.includes('callableEmitter(events.EventEmitter)')));
  assert([...modules].some(id=>id.includes('/unenv/'))&&[...modules].some(id=>id.includes('/readable-stream/lib/')));
  assert(![...modules].some(id=>id.includes('/builtins/node-compat/classic-streams/')));
 }
 const sourceRecords=[...physical.values()];
 for(const row of sourceRecords)assert.equal(hash(await readFile(row.path)),row.sha256,row.path);
 reports.push({arm,entry:join(here,'entry.mjs'),provider,imports:chunk.imports,exports:chunk.exports,bundlePath:join(directory,'application.bundle.mjs'),bundleSha256:hash(chunk.code),bundleBytes:Buffer.byteLength(chunk.code),
  moduleIds:[...modules].sort(),physicalSources:sourceRecords.sort((a,b)=>a.path.localeCompare(b.path)),virtualSources:[...virtual].map(([id,source])=>({id,sha256:hash(source),bytes:Buffer.byteLength(source)})),resolutions,
  scheduler:arm==='stock'?{path:scheduler,sha256:hash(await readFile(scheduler)),override:false,queue:'unmodified queueMicrotask array FIFO'}:{path:'future actual private native queue binding',artifactUnverified:true},
  guestOrComponentExecuted:false,scope:arm==='stock'?'Different provider/dependency/scheduler graph':'Future common-native-dependency source graph; no actual extension engine yet'});
}
const core=await readFile(resolve(here,'../../../../builtins/node-compat/classic-streams/classic-core.generated.mjs'),'utf8');
let facade=await readFile(resolve(here,'../../../../builtins/node-compat/classic-streams/classic-streams.mjs'),'utf8');
facade=facade.replace("import {createClassicCore} from './classic-core.generated.mjs';\n",'').replace(/^export function /gm,'function ');
const factory=`(function(dependencies){\n'use strict';\n${core.replace(/^export function /gm,'function ')}\n${facade}\nreturn createClassicStreams(dependencies);\n})`;
const header=await readFile(resolve(here,'../../../../builtins/node-compat/classic-streams/factories.generated.h'),'utf8');
assert.equal(header.split('R"SM_NODE_PROFILE(')[1].split(')SM_NODE_PROFILE";')[0],factory);
for(const row of pinned.inputs)assert.equal(hash(await readFile(row.path)),row.sha256,row.path);
for(const row of sourceChecks)assert.equal(hash(await readFile(row.path)),row.sha256,row.path);
const result={schemaVersion:1,state:'ACTUAL_ENTRY_CLASSIC_WORKLOAD_HOST_BUNDLES_SOURCE_GRAPHS_VERIFIED',reports,
 canonicalFactoryHeaderExact:true,canonicalFactorySourceSha256:hash(factory),toolInputSha256:hash(await readFile(join(here,'tool-inputs.json'))),
 stockProviderOptions:{},stockSchedulerOverride:false,sourceInputsCheckedBeforeAfter:sourceChecks,
 actualEngineOrComponentUsed:false,checksumAndTraceCorrectnessRequiredSeparately:true};
await writeFile(join(output,'bundle-results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,arms:reports.map(row=>({arm:row.arm,imports:row.imports,modules:row.moduleIds.length})),output}));
