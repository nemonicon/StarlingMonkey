// PREPARED/UNEXECUTED ordinary component harness, same existing pinned tools.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {nativePreflight} from './native-preflight.mjs';
import {decodeCliString} from '../../foundations/native-scalar-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
export async function nativeHarness({streamWebEnabled,output}){
  // First operation is fail-closed source/flag admission, before any fixture.
  const preflight=await nativePreflight({streamWebEnabled});
  output=resolve(output);
  const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
  const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
  const version=spawnSync(preflight.wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
  await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
  try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
  const options={engine:preflight.engine,witWorld:await readFile(join(here,'../profile.wit'),'utf8'),worldName:'profile',
    disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]};
  async function bundle(input,virtualModules){return bundleProfile({...toolchain,input,builtinManifests:preflight.builtinManifests,virtualModules});}
  async function artifact(name,source){
    const{component,interfaceAudit}=await componentize(source,options),path=join(output,name+'.component.wasm');await writeFile(path,component);
    const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);await writeFile(join(output,name+'.wit'),wit);
    const{files}=await transpile(component,{name});for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
    const instance=await import(pathToFileURL(join(output,name+'.js')));
    return{path,instance,bytes:component.length,sha256:preflight.hash(component),emittedWit:wit,emittedImports:[],interfaceAudit};
  }
  async function hostRun(name,path){
    const host=spawnSync(preflight.wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
    await writeFile(join(output,name+'.wasmtime.log'),JSON.stringify(host,null,2)+'\n');assert.equal(host.status,0,host.error?.message||host.stderr);
    return JSON.parse(decodeCliString(host.stdout.trim()));
  }
  async function failsAtComponentization(name,input,expected){
    const bundled=await bundle(input);let message;
    try{await componentize(bundled.code,options);}catch(error){message=error.message;}
    await writeFile(join(output,name+'.componentization.log'),message??'UNEXPECTED SUCCESS');
    assert.match(message??'',expected,'Top-level unsupported/unknown export must fail componentization');
    return{name,input,failed:true,expected:String(expected),message};
  }
  return{...preflight,output,toolchain,componentizer:provenance,wasmtimeVersion:version.stdout.trim(),bundle,artifact,hostRun,failsAtComponentization};
}
