// Host-only packaging experiment. Never imports/evaluates application or output.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {builtinModules} from 'node:module';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../../../toolchain.mjs';
import {builtinMap} from '../../../module-selection.mjs';
import {runtimeReferenceAudit} from '../../../package-environment-guards.mjs';

const HERE=dirname(fileURLToPath(import.meta.url));
const RECORD=resolve(HERE,'../results/2026-11-06-post-77659217-replay');
const OUTPUT=resolve(process.argv[2]);
assert(OUTPUT.startsWith('/private/tmp/starling-node-compat/next-standalone-bundler-diagnostic-v1-'));
const hash=b=>createHash('sha256').update(b).digest('hex');
async function descriptor(path){const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};}
const captured=new Map();
async function check(r){const s=await lstat(r.path);assert(s.isFile()&&!s.isSymbolicLink());assert.deepEqual(await descriptor(r.path),r);captured.set(r.path,r);return r;}
async function save(path,data){await writeFile(path,typeof data==='string'?data:JSON.stringify(data,null,2)+'\n',{flag:'wx',mode:0o600});}
function walk(node,fn,parent=null,key=''){if(!node||typeof node!=='object')return;if(typeof node.type==='string')fn(node,parent,key);for(const[k,v]of Object.entries(node)){if(['parent','loc','range','comments','tokens'].includes(k))continue;if(Array.isArray(v))for(const c of v)walk(c,fn,node,k);else if(v&&typeof v==='object')walk(v,fn,node,k);}}
function errorData(e){return{name:e?.name??null,code:e?.code??null,message:e?.message??String(e),stack:e?.stack??null};}
await mkdir(OUTPUT,{mode:0o700});
const baseline=JSON.parse(await readFile(join(RECORD,'results.json')));
const tools=JSON.parse(await readFile(join(RECORD,'wasm/next-standalone/tooling-preflight.json')));
const native=JSON.parse(await readFile(join(RECORD,'wasm/next-standalone/native-preflight.json')));
assert(process.version==='v22.14.0');await check(tools.node);
assert(process.execPath===tools.node.path);
for(const r of baseline.generatedArtifacts)await check(r);
for(const r of Object.values(tools.packages))await check(r);
assert(native.selectedModuleManifests.length===9&&native.builtinManifests.length===9);
for(let i=0;i<native.selectedModuleManifests.length;i++){
 const r=native.selectedModuleManifests[i],p=join(native.sourceRoot,r.path),b=await readFile(p);assert(hash(b)===r.sha256);assert.deepEqual(JSON.parse(b),native.builtinManifests[i]);await check(await descriptor(p));
}
const toolchain=await loadToolchain();
const {esmExternalRequirePlugin}=await import(pathToFileURL(toolchain.require.resolve('rolldown/plugins')));
const admitted=builtinMap(native.builtinManifests);
const nodeNames=new Set(builtinModules);
const isBuiltin=s=>s.startsWith('node:')||nodeNames.has(s);
const canonical=s=>'node:'+s.replace(/^node:/,'');
const allNatives=[...new Set([...builtinModules.map(canonical),...Object.values(admitted)])];
const standalone=baseline.generatedArtifacts.find(r=>r.path.endsWith('/standalone/server.js'));
const application=resolve(dirname(standalone.path),'../..');
const cjsRoot=join(application,'node_modules/next/dist/server/lib/start-server.js');
const nextPackage=join(application,'node_modules/next/package.json');
assert(JSON.parse(await readFile(nextPackage)).version==='16.4.5');await check(await descriptor(nextPackage));await check(await descriptor(cjsRoot));
const report={schemaVersion:1,state:'HOST_ONLY_NEXT_SERVER_BUNDLER_DIAGNOSTIC',
 source:await descriptor(fileURLToPath(import.meta.url)),record:await descriptor(join(RECORD,'results.json')),
 node:tools.node,rolldown:tools.packages.rolldown,next:await descriptor(nextPackage),generatedArtifacts:baseline.generatedArtifacts,
 experiments:[],applicationOrBundleEvaluated:false,compilerOrComponentizerInvoked:false,guestInvoked:false,serverStarted:false,
 fullNextServerInWasm:false,nativeAdmissionGranted:false,sourceInputs:[]};
await save(join(OUTPUT,'executed-run.mjs'),await readFile(fileURLToPath(import.meta.url),'utf8'));

async function experiment(id,input,policy){
 const root=join(OUTPUT,id);await mkdir(root,{mode:0o700});const sourceRows=new Map(),nativeEdges=[],loaderUses=[],assetEdges=[],warnings=[];
 const row={id,input:await descriptor(input),policy,startedAtUtc:new Date().toISOString(),status:'pending',nativeEdges,loaderUses,assetEdges,warnings,
  canonicalBuiltinBridge:'existing rolldown/plugins esmExternalRequirePlugin',builtinAdapters:false,applicationEvaluated:false};
 let build;
 const plugin={name:'next-host-only-native-edge-diagnostic',
  async resolveId(source,importer){
   if(isBuiltin(source)){
    const name=canonical(source),accepted=Object.hasOwn(admitted,source)||Object.values(admitted).includes(name);
    nativeEdges.push({source,canonical:name,importer:importer??null,admittedByV13:accepted});
    if(policy==='v13-only'&&!accepted)throw new Error('V13_NATIVE_BUILTIN_NOT_ADMITTED: '+source);
    return null; // Existing builtin plugin owns external require/default conversion.
   }
   if(/^(?:jco:|wasmcloud:)/.test(source))throw new Error('NONSTANDARD_HOST_ADAPTER: '+source);
   if(/\.(?:node|wasm)(?:\?|$)/.test(source)){
    // A request ending .node can resolve to ordinary .node.js. Classify the
    // actual resolver result, never the request suffix alone.
    const resolved=await this.resolve(source,importer,{skipSelf:true});
    const executable=resolved&&/\.(?:node|wasm)(?:\?|$)/.test(resolved.id);
    assetEdges.push({source,importer:importer??null,resolved:resolved?.id??null,executable:Boolean(executable),
     diagnosticExternal:(!resolved||executable)&&policy==='all-node-and-assets-diagnostic'});
    if(!resolved||executable){
     if(policy==='all-node-and-assets-diagnostic')return{id:resolved?.id??source,external:true};
     throw new Error('UNRESOLVED_OR_EXECUTABLE_ASSET: '+source+' -> '+(resolved?.id??'unresolved'));
    }
    return resolved;
   }
   return null;
  },
  transform(code,id){
   if(id.startsWith('\0'))return null;
   sourceRows.set(id,{id,transformInputSha256:hash(code),transformInputBytes:Buffer.byteLength(code)});
   if(id.endsWith('.json')){JSON.parse(code);return null;}
   const ast=toolchain.parseAst(code,{},id),changes=[];
   walk(ast,(n,p,k)=>{
    if(n.type==='CallExpression'&&n.callee.type==='Identifier'&&n.callee.name==='require'){
     const a=n.arguments[0];
     if(n.arguments.length!==1||a?.type!=='Literal'||typeof a.value!=='string')loaderUses.push({id,kind:'nonliteral-require',start:n.start,source:code.slice(n.start,Math.min(n.end,n.start+200))});
     else if(isBuiltin(a.value)){
      nativeEdges.push({source:a.value,canonical:canonical(a.value),importer:id,admittedByV13:Object.values(admitted).includes(canonical(a.value)),kind:'source-require'});
      if(a.value!==canonical(a.value))changes.push({start:a.start,end:a.end,value:canonical(a.value)});
     }
    }
    if(n.type==='MemberExpression'&&!n.computed&&n.object.type==='Identifier'&&n.object.name==='require')loaderUses.push({id,kind:'require-property',property:n.property.name,start:n.start});
    if(n.type==='CallExpression'&&n.callee.type==='MemberExpression'&&!n.callee.computed&&n.callee.property.name==='createRequire')loaderUses.push({id,kind:'createRequire',start:n.start});
    if(['ImportDeclaration','ExportNamedDeclaration','ExportAllDeclaration'].includes(n.type)&&n.source&&isBuiltin(n.source.value)){
     nativeEdges.push({source:n.source.value,canonical:canonical(n.source.value),importer:id,admittedByV13:Object.values(admitted).includes(canonical(n.source.value)),kind:'source-esm'});
     if(n.source.value!==canonical(n.source.value))changes.push({start:n.source.start,end:n.source.end,value:canonical(n.source.value)});
    }
   });
   if(!changes.length)return null;
   for(const c of changes.sort((a,b)=>b.start-a.start))code=code.slice(0,c.start)+JSON.stringify(c.value)+code.slice(c.end);
   return{code,map:null};
  }};
 try{
  build=await toolchain.rolldown({input,platform:'neutral',resolve:{mainFields:['main','module'],conditionNames:['node']},
   transform:{define:{'process.env.NODE_ENV':JSON.stringify('production')}},treeshake:true,
   plugins:[plugin,esmExternalRequirePlugin({external:policy==='v13-only'?[...new Set(Object.values(admitted))]:allNatives})],
   onLog(level,log){warnings.push({level,code:log.code??null,message:log.message});}});
  const generated=await build.generate({format:'esm',codeSplitting:false,externalLiveBindings:true});
  assert(generated.output.length===1&&generated.output[0].type==='chunk');const chunk=generated.output[0];
  await save(join(root,'bundle.mjs'),chunk.code);
  const audit=runtimeReferenceAudit(toolchain.parseAst(chunk.code));
  const names=nodes=>Object.fromEntries([...new Set(nodes.map(n=>n.name))].sort().map(name=>[name,nodes.filter(n=>n.name===name).length]));
  const unadmitted=chunk.imports.filter(n=>!Object.values(admitted).includes(n));
  Object.assign(row,{status:'bundle-generated-diagnostic-only',bundle:await descriptor(join(root,'bundle.mjs')),imports:chunk.imports,
   unadmittedImports:unadmitted,moduleIds:Object.keys(chunk.modules??{}),blockedRuntimeGlobals:names(audit.blocked),guardedRuntimeGlobals:names(audit.guarded),
   unclosedLoaderReferences:loaderUses.length>0,guestAdmissible:false,graphClosureClaim:false});
 }catch(e){row.status='bundling-refused';row.failure=errorData(e);}
 finally{if(build)try{await build.close();}catch(e){row.closeFailure=errorData(e);}row.sourceInputs=[...sourceRows.values()].sort((a,b)=>a.id.localeCompare(b.id));row.finishedAtUtc=new Date().toISOString();await save(join(root,'result.json'),row);report.experiments.push(row);}
 console.log(JSON.stringify({id,status:row.status,modules:row.moduleIds?.length??null,imports:row.imports??null,failure:row.failure?.message??null}));
}
await experiment('standalone-stock-commonjs-diagnostic',standalone.path,'all-node-externals-diagnostic');
await experiment('standalone-v13-admission',standalone.path,'v13-only');
await experiment('start-server-stock-commonjs-diagnostic',cjsRoot,'all-node-externals-diagnostic');
await experiment('start-server-v13-admission',cjsRoot,'v13-only');
await experiment('start-server-assets-external-diagnostic',cjsRoot,'all-node-and-assets-diagnostic');
for(const r of captured.values())await check(r);
report.sourceInputs=[...captured.values()];report.finishedAtUtc=new Date().toISOString();await save(join(OUTPUT,'results.json'),report);
