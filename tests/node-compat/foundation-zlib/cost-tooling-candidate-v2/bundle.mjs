// Future action body only. No library or bundle is loaded at module evaluation.
import {readFile,realpath} from 'node:fs/promises';
import {dirname,join,isAbsolute,relative,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {hash,need} from './authority.mjs';
import {assertPackagingEnvironment} from './environment.mjs';
export async function bundleCost(admitted,{arm,entryPath,providerPath,oracleInputsPath}){
 need(['native-on','fflate-on','fflate-off'].includes(arm),'Finite codec arm');
 need(admitted?.action==='bundle-source'&&admitted.diagnosticCostOnly===true&&admitted.operationalAdmission===false,'Separate source-bundle action required');
 await admitted.recheck();
 assertPackagingEnvironment(admitted);
 const guestRoot=await realpath(admitted.guestRoot),browser=await realpath(admitted.fflateBrowserPath);
 need(arm===admitted.arm&&entryPath===join(guestRoot,'guest.mjs')&&providerPath===join(guestRoot,arm==='native-on'?'native-provider.mjs':'fflate-provider.mjs'),'Fixed exact guest entry/provider per admitted arm');
 for(const path of[entryPath,providerPath]){
  need(isAbsolute(path)&&resolve(path)===path,'Canonical guest source path');
  const local=relative(guestRoot,await realpath(path));need(local&&!local.startsWith('../')&&!isAbsolute(local),'Pinned guest root only');
  await admitted.checkGuestFile(path);
 }
 need(isAbsolute(oracleInputsPath)&&resolve(oracleInputsPath)===oracleInputsPath,'Canonical derived oracle module');
 await admitted.checkOracleFile(oracleInputsPath);
 need(hash(await readFile(browser))==='b7ca4450b19559a1d50eb381adcee94b82449674be4cd17789d9beba7e6122a1','Exact browser ESM');
 const {loadToolchain}=await import(pathToFileURL(join(admitted.packagingRoot,'tests/node-compat/toolchain.mjs')));
 const toolchain=await loadToolchain();need(await realpath(toolchain.directory)===admitted.toolchainRoot,'One reviewed tool tree');
 const jco=join(admitted.toolchainRoot,'node_modules/@bytecodealliance/jco');
 const {bundleComponentChunk}=await import(pathToFileURL(join(jco,'dist/bundle.js')));
 const {createProfilePlugin}=await import(pathToFileURL(join(admitted.packagingRoot,'tests/node-compat/profile-bundler.mjs')));
 const resolutions=[],modules=new Set();
 const finite={name:'bounded-zlib-cost-finite-inputs',resolveId(id,importer){
  let target=null;if(id==='codec:provider')target=providerPath;
  else if(id==='codec:oracle-inputs')target=oracleInputsPath;
  else if(id==='codec:fflate-browser')target=browser;
  if(target){resolutions.push({request:id,importer:importer??null,target});return target;}
  return null;
 }};
 const profile=createProfilePlugin(toolchain.parseAst,{builtinManifests:admitted.selectedManifests});
 const witness={name:'bounded-zlib-cost-source-graph',moduleParsed(info){modules.add(info.id);}};
 const chunk=await bundleComponentChunk(entryPath,{plugins:[finite,profile,witness],config:{treeshake:true}});
 need(Buffer.byteLength(chunk.code,'utf8')<=32*1024*1024,'Final guest bundle exceeds approved32MiB UTF8 bound');
 const expected=arm==='native-on'?['node:buffer','node:zlib']:['node:buffer'];
 need(JSON.stringify([...chunk.imports].sort())===JSON.stringify(expected),'Unexpected residual component module import');
 need(!chunk.code.includes('jco:node/zlib')&&!/__require/.test(chunk.code),'No custom zlib host or dynamic require');
 const physical=[],virtualIds=[];
 for(const id of[...modules].sort()){
  if(isAbsolute(id)&&!id.startsWith('\0')){
   const path=await realpath(id),raw=await readFile(path);
   const own=path.startsWith(guestRoot+'/'),oracle=path===await realpath(oracleInputsPath),ff=path===browser,tool=path.startsWith(admitted.toolchainRoot+'/node_modules/rolldown/');
   need(own||oracle||ff||tool,'Unreviewed physical guest dependency');
   need(!/node_modules\/(?:unenv|readable-stream|buffer)\//.test(path),'No JS native-builtin adapter');
   physical.push({path,sha256:hash(raw),bytes:raw.length,role:own?'guest':oracle?'reviewed-derived-oracle-inputs':ff?'fflate-browser':'rolldown-generated-runtime-source'});
  }else virtualIds.push(id);
 }
 if(arm!=='native-on')need(physical.some(row=>row.path===browser),'FF arm must contain the actual browser source');
 else need(!physical.some(row=>row.path===browser),'Native arm must not contain a bundled JS codec');
 // A real source-only bundle review MUST resolve/hash any virtual runtime
 // helper before component-build permission. No unobserved virtual API guessed.
 const graph={schemaVersion:1,arm,entryPath,providerPath,oracleInputsPath,fflateBrowserPath:arm==='native-on'?null:browser,
  imports:chunk.imports,exports:chunk.exports,modules:[...modules].sort(),physicalSources:physical,virtualModuleIds:virtualIds,resolutions,
  options:{config:{treeshake:true},nodeBuiltinPlugin:false,nodeGlobalsInjection:false},
  codeSha256:hash(chunk.code),codeBytes:Buffer.byteLength(chunk.code),virtualSourceReviewRequired:virtualIds.length>0,
  componentizationAllowedByThisResult:false,guestCompatibilityClaim:false};
 await admitted.recheck();return{code:chunk.code,graph};
}
