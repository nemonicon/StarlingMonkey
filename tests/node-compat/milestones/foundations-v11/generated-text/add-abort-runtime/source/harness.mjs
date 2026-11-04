import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {preflight,hash} from './preflight.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {decodeCliString} from '../../foundations/native-scalar-harness.mjs';

export async function harness({gcStress=false}={}){
 const admitted=await preflight({gcStress}),{engine,sourceRoot,metadata}=admitted;
 const here=dirname(fileURLToPath(import.meta.url)),output=resolve(process.env.NODE_COMPAT_ADD_ABORT_OUTPUT??'/tmp/starling-node-compat/foundations-v11/add-abort-'+metadata.entropyPolicy+(gcStress?'-gc':''));
 await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),JSON.stringify({engine,engineSha256:metadata.engineSha256})+'\n',{flag:'wx'});
 await writeFile(join(output,'package.json'),'{"type":"module"}\n');await writeFile(join(output,'preflight.json'),JSON.stringify(admitted.report,null,2)+'\n');
 const sourceFiles=[];
 for(const name of ['engine-pins.json','public-cases.mjs','run-node.mjs','node-results.json','component.mjs','require.cjs','profile.wit','preflight.mjs','harness.mjs','run-component.mjs','gc-component.mjs','run-gc.mjs']){
  const original=join(here,name);let bytes;try{bytes=await readFile(original);}catch(error){if(error.code==='ENOENT')continue;throw error;}
  const saved=join(output,'source',name);await mkdir(dirname(saved),{recursive:true});await writeFile(saved,bytes);sourceFiles.push({path:original,sha256:hash(bytes),saved});
 }
 const tc=await loadToolchain(),selected=await loadComponentizer(tc);assert.equal(selected.provenance.selection,'patched-import-i32-clock-v2');
 await symlink(join(tc.directory,'node_modules'),join(output,'node_modules'));
 const runtime=metadata.entropyPolicy==='runtime-only',selectedInterfaces=runtime?['wasi:random/random@0.2.10']:[];
 const adapter=join(sourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
 const options={engine,preview2Adapter:adapter,witWorld:await readFile(join(here,'profile.wit'),'utf8'),worldName:'profile',disableFeatures:runtime?['stdio','clocks','http','fetch-event']:['stdio','random','clocks','http','fetch-event'],selectedInterfaces};
 const{transpile,componentWit}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
 async function build(name,source){
  await writeFile(join(output,name+'.source.mjs'),source);
  const{component,interfaceAudit}=await selected.componentize(source,options);assert.deepEqual(interfaceAudit.emittedImports,selectedInterfaces);
  const wit=await componentWit(component),imports=[...wit.matchAll(/^\s*import\s+([^;]+);/gm)].map(match=>match[1].trim()).sort();assert.deepEqual(imports,selectedInterfaces);
  assert.match(wit,/export run: func\(\) -> string;/);
  const componentPath=join(output,name+'.component.wasm');await writeFile(componentPath,component);await writeFile(join(output,name+'.wit'),wit);
  const{files}=await transpile(component,{name,wasiShim:runtime});for(const[file,bytes]of Object.entries(files)){await mkdir(dirname(join(output,file)),{recursive:true});await writeFile(join(output,file),bytes);}
  return{componentPath,modulePath:join(output,name+'.js'),componentSha256:hash(component),componentBytes:component.length,sourceSha256:hash(source),interfaceAudit,emittedImports:imports,emittedWit:wit};
 }
 async function bundle(input,expectedImports){const result=await bundleProfile({...tc,builtinManifests:admitted.builtinManifests,input});assert.deepEqual(result.imports.sort(),[...expectedImports].sort());assert(result.moduleIds.every(id=>!id.includes('/builtins/node-compat/')&&!id.includes('node-builtins/')));return result;}
 const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
 const version=spawnSync(host,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
 const hostInfo={path:host,sha256:hash(await readFile(host)),version:version.stdout.trim()};
 function freshHost(fixture){const value=spawnSync(host,['run','--invoke','run()',fixture.componentPath],{encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});assert.equal(value.status,0,value.error?.message??value.stderr);return{...hostInfo,stdout:value.stdout,stderr:value.stderr,observed:JSON.parse(decodeCliString(value.stdout.trim()))};}
 async function expectInitialization(name,source,marker){await writeFile(join(output,name+'.init.mjs'),source);let message;try{await selected.componentize(source,options);}catch(error){message=error.message;}assert(message,name+' unexpectedly componentized');assert.match(message,marker,name);return{name,sourceSha256:hash(source),message};}
 async function fatal(name,source){
  const fixture=await build(name,source),childPath=join(output,name+'-child.mjs');
  await writeFile(childPath,`import{run}from${JSON.stringify(fixture.modulePath)};try{await run();console.log('UNEXPECTED_RETURN');process.exitCode=2;}catch(error){console.log('EXPECTED_FATAL_DISCARD');}`);
  const child=spawnSync(process.execPath,[childPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.equal(child.status,0,child.stderr);assert.match(child.stdout,/EXPECTED_FATAL_DISCARD/);assert.doesNotMatch(child.stdout,/UNEXPECTED_RETURN/);
  const fresh=spawnSync(host,['run','--invoke','run()',fixture.componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.notEqual(fresh.status,0);assert.doesNotMatch(fresh.stdout,/must-not-return/);
  return{name,fixture,jcoChild:{status:child.status,stdout:child.stdout,stderr:child.stderr},wasmtime:{...hostInfo,status:fresh.status,stdout:fresh.stdout,stderr:fresh.stderr},policy:'Failure is terminal; both instances discarded, never reused'};
 }
 async function finish(){for(const item of sourceFiles)assert.equal(hash(await readFile(item.path)),item.sha256,item.path);assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(hash(await readFile(engine+'.build.json')),admitted.report.engineMetadataSha256);await preflight({gcStress});}
 const evidence={preflight:admitted.report,engineSha256:metadata.engineSha256,engineReceipt:metadata,sourceRoot,sourceFiles,packaging:selected.provenance,capabilityOptions:options,host:hostInfo};
 return{here,output,metadata,evidence,build,bundle,freshHost,expectInitialization,fatal,finish,importFixture:fixture=>import(pathToFileURL(fixture.modulePath)),
  save:async report=>writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n')};
}
