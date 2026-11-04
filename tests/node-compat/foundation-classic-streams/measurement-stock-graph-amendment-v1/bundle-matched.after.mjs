// Future real Jco bundling, never invoked by source tests.
import assert from 'node:assert/strict';
import {readFile,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {priorStockModules} from './stock-graph.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
export async function bundleMatched(toolchain,admission,arm){
 assert(['native-on','canonical-on','canonical-off','stock-on'].includes(arm));await admission.recheck();
 const stockArm=arm==='stock-on',canonical=arm.startsWith('canonical-');
 const provider=join(here,stockArm?'stock-provider.mjs':canonical?'canonical-provider.mjs':'native-provider.mjs');
 const jco=join(toolchain.directory,'node_modules/@bytecodealliance/jco');
 const {bundleComponentChunk}=await import(pathToFileURL(join(jco,'dist/bundle.js')));
 const {nodeBuiltinPlugin,nodeGlobals}=await import(pathToFileURL(join(jco,'dist/node-builtins/index.js')));
 const scheduler=await realpath(join(toolchain.directory,'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/scheduler.js'));
 const stock=nodeBuiltinPlugin({imports:[],exports:[]},{}),resolutions=[],virtual=[],modules=new Set();
 const stockPlugin={...stock,async resolveId(id,importer,extra){const result=await stock.resolveId.call(this,id,importer,extra);if(result!==null&&result!==undefined)resolutions.push({request:id,importer:importer??null,result});return result;},load(id){const source=stock.load.call(this,id);if(typeof source==='string')virtual.push({id,sha256:hash(source),bytes:Buffer.byteLength(source)});return source;}};
 const finite={name:'finite-common-byte-provider',resolveId(id){if(id==='benchmark:provider')return provider;if(stockArm&&id==='benchmark:stock-scheduler')return scheduler;if(!stockArm&&(id.startsWith('node:')||id==='starling:test-classic-benchmark'))return{id,external:true};return null;}};
 const chunk=await bundleComponentChunk(join(here,'guest.mjs'),{plugins:[finite,...(stockArm?[stockPlugin]:[]),{name:'finite-graph-witness',moduleParsed(info){modules.add(info.id);}}],...(stockArm?{inject:nodeGlobals()}:{}),config:{treeshake:false}});
 const own=['guest.mjs','capture-before.mjs','workload.mjs','control-workload.mjs','protocol.mjs',stockArm?'stock-provider.mjs':canonical?'canonical-provider.mjs':'native-provider.mjs'].map(name=>join(here,name));
 if(stockArm){
  assert.deepEqual(chunk.imports,[]);
  const previous=JSON.parse(await readFile(join(here,'stock-source-graph.json')));
  const prior=priorStockModules(previous);
  assert.equal(prior.length,99);assert.deepEqual([...modules].sort(),[...prior,...own].sort());
  assert.deepEqual(virtual.sort((a,b)=>a.id.localeCompare(b.id)),[...previous.virtualSources].sort((a,b)=>a.id.localeCompare(b.id)));
  const processEdges=resolutions.filter(row=>row.request==='process/'&&row.importer?.includes('/readable-stream/lib/'));
  assert.equal(processEdges.length,7);assert(processEdges.every(row=>row.result===scheduler));
  assert.equal([...modules].filter(id=>id.endsWith('/stream/scheduler.js')).length,1);
  assert.equal(scheduler,previous.scheduler); // default plugin {}, no source or scheduler option override
 }else{
  const imports=canonical?['node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark']:['node:stream','node:stream/promises','node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark'];
  assert.deepEqual([...chunk.imports].sort(),imports.sort());
  const physical=[...modules].filter(id=>isAbsolute(id)&&!id.startsWith('\0'));
  assert.deepEqual(physical.sort(),[...own,...(canonical?[join(here,'classic-streams.mjs'),join(here,'classic-core.generated.mjs')]:[])].sort());
  assert.doesNotMatch(chunk.code,/node_modules\/(?:unenv|readable-stream)/);
 }
 const physical=[];for(const id of modules)if(isAbsolute(id)&&!id.startsWith('\0')){const raw=await readFile(id);physical.push({path:id,sha256:hash(raw),bytes:raw.length});}
 if(canonical){
  const core=await readFile(join(here,'classic-core.generated.mjs'),'utf8');let facade=await readFile(join(here,'classic-streams.mjs'),'utf8');
  facade=facade.replace("import {createClassicCore} from './classic-core.generated.mjs';\n",'').replace(/^export function /gm,'function ');
  const factory=`(function(dependencies){\n'use strict';\n${core.replace(/^export function /gm,'function ')}\n${facade}\nreturn createClassicStreams(dependencies);\n})`;
  const header=await readFile(join(admission.toolSourceRoot,'builtins/node-compat/classic-streams/factories.generated.h'),'utf8');assert.equal(header.split('R"SM_NODE_PROFILE(')[1].split(')SM_NODE_PROFILE";')[0],factory);
 }
 await admission.recheck();
 return{code:chunk.code,graph:{arm,imports:chunk.imports,exports:chunk.exports,modules:[...modules].sort(),physicalSources:physical,virtualSources:virtual,resolutions,bundleSha256:hash(chunk.code),bundleBytes:Buffer.byteLength(chunk.code),stockOptions:stockArm?{}:null,stockSchedulerOverride:false,
  dependencyScope:stockArm?'Untouched Jco1.40/readable4.7 provider, own Buffer/EE/SD and queueMicrotask FIFO; ambient native Web APIs remain':'Native Buffer/EE/SD/private nextTick slots; util is the same byte-exact private5c module, no node:util injection slot'}};
}
