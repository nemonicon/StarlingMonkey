// Separate bundle process only. Does not evaluate the fixture or load packager.
import {readFile,statfs,realpath} from 'node:fs/promises';
import {dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {isDeepStrictEqual as same} from 'node:util';
import {DurableOutput,retainRecord,need,absolute,finish,observed} from './io.mjs';
export async function run(f){
 need(f.root.phase==='bundle'&&process.env.NODE_COMPAT_TOOLCHAIN===f.refs.loaderPackageRoot,'Genuine private bundle toolchain in separate owned process');const space=await statfs(dirname(f.root.outputRoot));need(space.bavail*space.bsize>=2*1024**3,'Operational output headroom');const out=await DurableOutput.create(f.root.outputRoot),primary={present:false};let detail={},finalErrors=[];
 try{
  try{
   await retainRecord(out,f.record);const h=f.record.bootstrap;await out.write('fixture.mjs',await readFile(f.fixture.source.path));await out.write('public-abi.wit',await readFile(f.fixture.wit.path));
   const {validateManifest}=await import(pathToFileURL(f.refs.manifestValidator.path)),schema=await f.c.read(f.refs.manifestSchema);for(const m of h.selectedManifests)validateManifest(m,schema);
   const {builtinMap}=await import(pathToFileURL(f.refs.moduleSelectionApi.path)),map=builtinMap(h.selectedManifests);need(!Object.hasOwn(map,'node:crypto')&&!Object.hasOwn(map,'crypto'),'Public Nodecrypto stays unadmitted');
   const {loadToolchain}=await import(pathToFileURL(f.refs.toolchainApi.path)),toolchain=await loadToolchain();need(await realpath(toolchain.directory)===f.refs.loaderPackageRoot,'Actual reviewed private toolchain, no generic fallback');
   const {bundleProfile}=await import(pathToFileURL(f.refs.bundleApi.path));await f.recheck();const bundle=await bundleProfile({rolldown:toolchain.rolldown,parseAst:toolchain.parseAst,input:f.fixture.source.path,builtinManifests:h.selectedManifests,virtualModules:{}});
   await out.write('bundle-return.json',bundle,{json:true});need(typeof bundle.code==='string','Actual whole bundle source');const row=await out.write('bundle.mjs',bundle.code);need(row.bytes<=f.root.maxBundleBytes,'Bounded bundle AFTER full return capture');
   need(same(bundle.imports,f.fixture.expectedNativeResidualImports)&&bundle.moduleIds.length===1&&await realpath(bundle.moduleIds[0])===f.fixture.source.path,'Exact native residual imports/single physical fixture; no JS adapter or other application modules');need(same(bundle.admittedBuiltins,[...new Set(Object.values(map))].sort()),'Actual full11 manifest builtinMap, no9-selector cast');
   await out.write('selected-whole-manifests.json',h.selectedManifests,{json:true});await out.write('native-builtin-map.json',map,{json:true});detail={bundle:absolute(out,row),bundleReturn:absolute(out,out.rows.get('bundle-return.json')),expectedNativeResidualImports:f.fixture.expectedNativeResidualImports,allElevenManifestsUsed:true,fixtureEvaluated:false,packagerLoaded:false,componentizationAttempted:false};
  }catch(error){primary.present=true;primary.value=error;}
  finally{for(const[scope,fn]of [['native/source',f.recheck],['output',()=>out.recheck()]])try{await fn();}catch(error){finalErrors.push({scope,error:observed(error)});}}
  return await finish(out,f,'bundle',detail,primary,finalErrors);
 }finally{await out.close();}
}
