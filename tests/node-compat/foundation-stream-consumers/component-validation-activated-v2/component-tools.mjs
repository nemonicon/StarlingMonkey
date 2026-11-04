// Pure physical resolution/data audit. No owner modules or native actions imported.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
export const componentToolRoot=resolve(dirname(fileURLToPath(import.meta.url)),'packaging-tools');
const toolchainRoot='/tmp/starling-node-compat/native-toolchain-lock',packagerRoot='/tmp/starling-node-compat/import-abi-clock-v2-build/package';
export const entries=Object.freeze(['tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/foundations/native-scalar-harness.mjs']);
const modules=Object.freeze([...entries,'tests/node-compat/capability-policy.mjs','tests/node-compat/module-selection.mjs','tests/node-compat/private-ticks-admission.mjs','tests/node-compat/classic-streams-admission.mjs','builtins/node-compat/validate-manifest.mjs','tests/node-compat/zlib-admission.mjs','tests/node-compat/stream-consumers-admission.mjs','tests/node-compat/foundation-zlib/native-integration-candidate-v4/compile-input.mjs'].sort());
const activeData=Object.freeze(['tests/node-compat/wasi-0.2.10-interfaces.json','builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json','tests/node-compat/legacy-stream-web-receipts.json','tests/node-compat/oom/componentize-clock-errno-v2.patch','tests/node-compat/abi-fix/componentize-import-i32-v1.patch','tests/node-compat/abi-fix/splicer-Cargo.v1.lock','host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'].sort());
const inactiveData=Object.freeze(["tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json","tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json","tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py","tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/admission-pins.json","tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/policy.json","tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/layer-policy.py","tests/node-compat/foundation-zlib/native-integration-candidate-v4/admission-pins.json","tests/node-compat/foundation-zlib/native-integration-candidate-v4/policy.json","tests/node-compat/foundation-zlib/native-integration-candidate-v4/layer-policy.py","tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/admission-pins.json","tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/policy.json","tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/layer-policy.py"].sort());
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const exact=(a,b,label)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw new Error('Physical tool closure differs: '+label);};
async function file(path){const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink(),path);const raw=await readFile(path);return{path,realPath:await realpath(path),sha256:hash(raw),bytes:raw.length};}
function inside(root,path){const name=relative(root,path);return name!==''&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name);}
export async function captureComponentToolClosure(){
 assert.equal(process.version,'v22.14.0');const root=componentToolRoot;assert.equal(await realpath(root),root);
 const files=[],edges=[],texts=new Map(),pending=[...entries],visited=new Set();
 while(pending.length){const name=pending.shift();if(visited.has(name))continue;visited.add(name);const path=join(root,name),row=await file(path),text=await readFile(path,'utf8');assert.equal(row.realPath,path);texts.set(name,text);files.push({...row,relativePath:name,kind:'local-module'});
  for(const match of text.matchAll(/^\s*import\b[^\n;]*?\bfrom\s*(['"])([^'"]+)\1\s*;?/gm)){
   const request=match[2];if(request.startsWith('node:'))continue;assert(request.startsWith('.'),'Unknown bare repository loader import: '+request);const target=resolve(dirname(path),request);assert(inside(root,target));const local=relative(root,target);edges.push({importer:name,request,target:local});pending.push(local);
  }
 }
 exact([...visited].sort(),modules,'all twelve transitive modules');
 for(const name of activeData){const row=await file(join(root,name));assert.equal(row.realPath,row.path);files.push({...row,relativePath:name,kind:name.endsWith('.wasm')?'selected-adapter':'selected-data'});}
 const urls=[];
 for(const[name,text]of texts)for(const match of text.matchAll(/new URL\((['"])([^'"]+)\1,\s*import\.meta\.url\)/g)){
  const request=match[2],target=resolve(dirname(join(root,name)),request),local=relative(root,target);
  if(request==='../../'){assert.equal(target,root);continue;}
  const active=activeData.includes(local),inactive=inactiveData.includes(local);assert(active||inactive,'Unclassified relative data URL: '+name+' '+request);urls.push({importer:name,request,target:local,usage:active?'selected-import-time':'inactive-selector-only'});
 }
 exact([...new Set(urls.filter(row=>row.usage==='inactive-selector-only').map(row=>row.target))].sort(),inactiveData,'all twelve inactive lazy selector reads');
 const patches=[];for(const match of texts.get('tests/node-compat/componentizer.mjs').matchAll(/readFile\(join\(here,\s*(['"])([^'"]+)\1\)\)/g)){const target='tests/node-compat/'+match[2];assert(activeData.includes(target));patches.push(target);}
 exact(patches.sort(),activeData.filter(name=>/\.(?:patch|lock)$/.test(name)).sort(),'three selected ABI/clock files');
 assert(texts.get('tests/node-compat/module-selection.mjs').includes('readFileSync(resolve(repository, CORE_MANIFEST))'));
 const versions={'@bytecodealliance/componentize-js':'0.23.0','@bytecodealliance/jco':'1.40.0',rolldown:'1.2.16'},packages=[];
 for(const[name,version]of Object.entries(versions)){const path=join(toolchainRoot,'node_modules',name,'package.json'),actual=JSON.parse(await readFile(path));assert.equal(actual.version,version);packages.push({...await file(path),name,version});}
 const require=createRequire(join(toolchainRoot,'package.json')),endpoints=[];
 for(const request of['rolldown','rolldown/parseAst','@bytecodealliance/jco']){const path=require.resolve(request),canonical=await realpath(path);assert(inside(await realpath(toolchainRoot),canonical));endpoints.push({request,...await file(canonical),resolutionPath:path,realPath:canonical});}
 for(const name of['src/componentize.js','lib/spidermonkey-embedding-splicer.js']){const path=join(packagerRoot,name),canonical=await realpath(path);assert.equal(canonical,resolve(await realpath(packagerRoot),name));endpoints.push({request:'selected-packager:'+name,...await file(canonical),resolutionPath:path,realPath:canonical});}
 const selectedPackage=JSON.parse(await readFile(join(packagerRoot,'package.json')));assert.equal(selectedPackage.version,'0.23.0');packages.push({...await file(join(packagerRoot,'package.json')),name:'selected-componentizer',version:selectedPackage.version});
 const provenancePath=join(packagerRoot,'splicer-build.json'),provenance=JSON.parse(await readFile(provenancePath));assert.equal(provenance.packagingVersion,'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1');const packageData=[await file(provenancePath)];
 for(const row of provenance.checkedFiles){assert(typeof row.path==='string'&&!row.path.startsWith('/')&&!row.path.split(/[\\/]/).includes('..'));const actual=await file(join(packagerRoot,row.path));assert.equal(actual.sha256,row.sha256);packageData.push(actual);}
 const adapter=files.find(row=>row.kind==='selected-adapter');assert.equal(adapter.sha256,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');assert.equal(adapter.bytes,53512);
 const order=(a,b)=>a.path<b.path?-1:a.path>b.path?1:0;
 return{schemaVersion:1,state:'PINNED_CONSUMERS355_COMPONENT_TOOL_SNAPSHOT_CLOSURE_V1',componentToolRoot:root,nativeAuthorityRole:'NONE; genuine355 manifests/engine come only from genuine staged bootstrap',entries:[...entries],files:files.sort(order),staticImportEdges:edges.sort((a,b)=>JSON.stringify(a)<JSON.stringify(b)?-1:1),relativeDataReads:urls.sort((a,b)=>JSON.stringify(a)<JSON.stringify(b)?-1:1),inactiveLazyReads:inactiveData.map(path=>({path,usage:'EXCLUDED_NOT_CALLED',reason:'Old selectedManifestsForEngine/private/classic admission is not invoked for355'})),packages,endpoints,packageData:packageData.sort(order),scope:{localModules:12,selectedLocalDataAndAdapter:8,ownerModuleImported:false,packageModuleImported:false,nativeMetadataSelectorCalled:false,packageResolutionOnly:true}};
}
export async function verifyComponentToolClosure(expected){
 assert.equal(expected.componentToolRoot,componentToolRoot);exact(await captureComponentToolClosure(),expected,'complete physical module/data/package resolution');return expected.files.length;
}
