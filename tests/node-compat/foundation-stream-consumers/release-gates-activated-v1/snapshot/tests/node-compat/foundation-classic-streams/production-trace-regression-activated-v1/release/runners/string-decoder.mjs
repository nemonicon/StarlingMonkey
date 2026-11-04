import {selectedManifestsForValidation} from "../../../../../../../native-preflight.mjs";
// Ordinary gates for the installed, explicitly selected m0.4 builtin.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../../../../toolchain.mjs';
import {loadComponentizer} from '../../../../componentizer.mjs';
import {STRING_DECODER_MANIFEST} from '../../../../module-selection.mjs';
import {bundleProfile} from '../../../../profile-bundler.mjs';
const here=resolve(dirname(fileURLToPath(import.meta.url)), '../../../../foundation-string-decoder'),repository=resolve(here,'../../..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_WASMTIME,'Explicit rebuilt production engine and stock Wasmtime42 paths required');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??repository);
const output=resolve(process.env.NODE_COMPAT_STRING_DECODER_OUTPUT??'/tmp/starling-node-compat/foundations-v6/string-decoder');
const metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.stringDecoderEnabled,true);assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_STRING_DECODER,'ON');
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release','Only ordinary Release indirect ABI is admitted');
assert.equal(metadata.oomTesting,false,'No fault-instrumented engine is admitted');
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const decoderPins=JSON.parse(await readFile(join(here,'production-candidate-pins.json')));
assert.equal(metadata.sourceManifest.find(entry=>entry.path==='builtins/web/text-codec/text-decoder.cpp')?.sha256,decoderPins.candidateSha256,
  'Mutation/detach ordinary cases require the corrected native decoder');
const helperPath='builtins/node-compat/register.cpp',helper=await readFile(join(sourceRoot,helperPath));
assert.equal(hash(helper),metadata.sourceManifest.find(entry=>entry.path===helperPath)?.sha256);
assert(helper.toString().includes('options.setForceStrictMode();'),'Factory compilation must preserve strict ESM semantics');
const builtinManifests=selectedManifestsForValidation(metadata,{sourceRoot});
assert(metadata.selectedModuleManifests.some(entry=>entry.path===STRING_DECODER_MANIFEST));
const selected=builtinManifests.find(manifest=>Object.hasOwn(manifest.modules,'node:string_decoder'));
assert.equal(selected.profileVersion,'sm-node-22.14.0-m0.4');
assert.deepEqual(selected.modules['node:string_decoder'].exports,['StringDecoder','default']);
const toolchain=await loadToolchain();
const {componentize,provenance}=await loadComponentizer(toolchain);
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
const corpus=JSON.parse(await readFile(join(here,'component-corpus.json')));
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const options={engine,witWorld:await readFile(join(here,'profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]};
async function artifact(name,source){
  const{component,interfaceAudit}=await componentize(source,options);
  const path=join(output,name+'.component.wasm');await writeFile(path,component);
  const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
  await writeFile(join(output,name+'.wit'),wit);
  const{files}=await transpile(component,{name});
  for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
  const instance=await import(pathToFileURL(join(output,name+'.js')));
  return{path,instance,bytes:component.length,sha256:hash(component),emittedWit:wit,emittedImports:[],interfaceAudit};
}
function hostRun(path){
  const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
  assert.equal(host.status,0,host.error?.message||host.stderr);
  return JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
}
const bundled=await bundleProfile({...toolchain,input:join(here,'native-component.mjs'),builtinManifests,
  virtualModules:{'node-compat:string-decoder-oracles':'export default '+JSON.stringify(corpus)+';'}});
assert.deepEqual([...bundled.imports].sort(),['node:buffer','node:string_decoder']);
assert(!bundled.moduleIds.some(id=>/node_modules|(?:^|\/)prototype\.mjs|buffer-facade|reference-kernel|builtins\/node-compat\/string-decoder\.mjs/.test(id)),
  'Application must use the installed native module, never bundle an adapter or factory');
await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const semantic=await artifact('string-decoder',bundled.code);
function check(report,calls){
  assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.passed,true);assert.equal(report.calls,calls);
  assert.equal(report.genericCases,corpus.decoderCases.length);assert.equal(report.preservedOrderingDeviations,2);
  assert.equal(report.sequences,corpus.sequences.length);assert.equal(report.writes,corpus.sequences.reduce((sum,value)=>sum+value.chunks.length,0));
  assert.equal(report.mutationChecks,2);assert.equal(report.detachedInternalStateChecks,5);assert.equal(report.primordialReplacementCalls,0);
  assert.equal(report.nativeAliases,2);assert(report.commonJS&&report.snapshotResumption&&report.identities&&report.noGlobalPollution);
}
const calls=[];
for(let index=1;index<=3;index++){
  const report=JSON.parse(await semantic.instance.run());calls.push(report);await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);
}
const wasmtimeReport=hostRun(semantic.path);check(wasmtimeReport,1);
const aliases=await artifact('aliases',await readFile(join(here,'native-aliases.mjs'),'utf8'));
const aliasCalls=[];
for(let index=1;index<=2;index++){
  const report=JSON.parse(await aliases.instance.run());assert(!report.failure,JSON.stringify(report.failure));
  assert.equal(report.calls,index);assert.equal(report.nativeAliases,2);assert(report.caching&&report.identities);aliasCalls.push(report);
}
const aliasHost=hostRun(aliases.path);assert(!aliasHost.failure,JSON.stringify(aliasHost.failure));assert.equal(aliasHost.nativeAliases,2);assert(aliasHost.caching&&aliasHost.identities);
const topLevelFailures=[];
for(const[filename,expected]of [['top-level-unsupported.mjs',/node:string_decoder\.encoding base64 is unavailable in sm-node-22\.14\.0-m0\.4/],
  ['top-level-unknown.mjs',/Unknown encoding/],['top-level-no-new.mjs',/StringDecoder requires an object receiver/]]){
  const bundle=await bundleProfile({...toolchain,input:join(here,filename),builtinManifests});
  let message;try{await componentize(bundle.code,options);}catch(error){message=error.message;}
  assert.match(message??'',expected,'Top-level unsupported/invalid operation must fail componentization');
  topLevelFailures.push({filename,failed:true,expected:String(expected)});
}
const result={schema:1,atUtc:new Date().toISOString(),node:process.version,
  scope:'Installed opt-in bounded StringDecoder and corrected ordinary native TextDecoder; no fault injection, raw-memory or old-native hazardous probes',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,
  nativeFactoryHelper:{path:helperPath,sha256:hash(helper),strictModeSymbol:'CompileOptions::setForceStrictMode'},
  component:{path:semantic.path,sha256:semantic.sha256,bytes:semantic.bytes,emittedWit:semantic.emittedWit,emittedImports:[],interfaceAudit:semantic.interfaceAudit},
  bundle:{imports:bundled.imports,moduleIds:bundled.moduleIds},calls,wasmtime:version.stdout.trim(),wasmtimeReport,
  aliases:{path:aliases.path,sha256:aliases.sha256,bytes:aliases.bytes,emittedImports:[],interfaceAudit:aliases.interfaceAudit,calls:aliasCalls,wasmtimeReport:aliasHost},
  topLevelFailures,preservedOrderingDeviations:corpus.deviations,
  sourceManifest:await Promise.all(['native-component.mjs','native-require.cjs','native-aliases.mjs','top-level-unsupported.mjs','top-level-unknown.mjs',
    'top-level-no-new.mjs','decoder-cases.mjs','profile.wit','run-native-component.mjs','component-corpus.json'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  limitations:['UTF8/hex only; other recognized Node encodings fail explicitly; no full StringDecoder claim.',
    'Shared, resizable and detached byte inputs excluded by the selected facade; SharedArrayBuffer availability recorded per component call.',
    'Existing native type-first input validation and single-read constructor options are explicit Node ordering deviations.',
    'Generic fatal-decoding recovery, complete WebIDL, allocator-recovery and exotic cross-realm/species behavior remain unclaimed.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
await writeFile(join(output,'native-component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,engineSha256:metadata.engineSha256,genericCases:corpus.decoderCases.length,sequences:corpus.sequences.length,
  writes:wasmtimeReport.writes,nativeAliases:2,zeroImports:true,wasmtimePassed:true,topLevelFailures:topLevelFailures.length},null,2));
