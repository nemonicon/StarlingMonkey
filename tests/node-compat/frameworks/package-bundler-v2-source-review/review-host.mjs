// Host parsing and packaging only. Never import or execute analyzed/generated JS.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dirname,join,resolve} from 'node:path';
const OWN=dirname(fileURLToPath(import.meta.url)),REPO=resolve(OWN,'../../../..');
const digest=b=>createHash('sha256').update(b).digest('hex'),sources=[];
async function verify(r){const b=await readFile(r.path);assert.equal(b.length,r.bytes);assert.equal(digest(b),r.sha256);sources.push(r);return b;}
for(const key of ['NODE_OPTIONS','NODE_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])assert(!process.env[key],key);
assert.equal(process.version,'v22.14.0');
await verify({path:await realpath(process.execPath),sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024});
const initial=JSON.parse(await readFile(join(OWN,'initial-sources.json')));
for(const r of initial.files)await verify(r);
const helperRoot=join(REPO,'tests/node-compat/frameworks/package-bundler-bindings-v2');
const helperIndex=JSON.parse(await readFile(join(helperRoot,'index.json')));
for(const r of helperIndex.files)await verify({...r,path:join(helperRoot,r.path)});
const {loadToolchain}=await import(pathToFileURL(join(REPO,'tests/node-compat/toolchain.mjs')));
const toolchain=await loadToolchain();
const {runtimeReferenceAudit}=await import(pathToFileURL(join(REPO,'tests/node-compat/package-environment-guards.mjs')));
const {findUnboundReferences}=await import(pathToFileURL(join(helperRoot,'bindings.mjs')));
const {bundlePackages}=await import(pathToFileURL(join(REPO,'tests/node-compat/framework-package-bundler-v2.mjs')));
const result={schemaVersion:1,scope:'Independent host-only parser/bundler source review; no analyzed module execution',cases:[],passed:false,sources};
const lexical=[
  ['plain-ambient','export function o(){return process;}',1],
  ['parameter-bound','export function o(process){return process;}',0],
  ['forward-lexical-bound','export function o(){return process;let process;}',0],
  ['default-before-body-var','export function o(x=process){var process;return x;}',1],
  ['computed-pattern-key','const {[process]:value}=obj;',1],
  ['noncomputed-pattern-bound','const {process}=obj;export {process};',0],
  ['static-var-isolated','class C{static{var process=1;}}export function o(){return process;}',1],
  ['loop-lexical-isolated','for(let process of []){}export function o(){return process;}',1],
  ['switch-lexical-isolated','switch(0){case 1:let process;}export function o(){return process;}',1],
  ['class-name-inner-only','const C=class process {field=process;};export function o(){return process;}',1],
  ['shorthand-is-reference','const x={process};',1],
  ['assignment-is-reference','({process}=obj);',1],
  ['property-key-not-reference','const x={process:1};x.process;',0],
];
for(const[id,code,count]of lexical){
  const ast=toolchain.parseAst(code),before=JSON.stringify(ast),refs=findUnboundReferences(ast,['process']);
  const r={kind:'lexical',id,expected:count,actual:refs.length,code,passed:refs.length===count};
  assert.equal(JSON.stringify(ast),before);assert.deepEqual(findUnboundReferences(ast,new Set(['process'])),refs);
  assert(refs.every(n=>code.slice(n.start,n.end)==='process'));result.cases.push(r);
}
const guards=[
 ['unguarded','export function o(){return process;}',1],
 ['typeof-only','export function o(){return typeof process;}',0],
 ['if-present','export function o(){if(typeof process!=="undefined")return process.env;return null;}',0],
 ['if-absent-wrong-branch','export function o(){if(typeof process==="undefined")return process.env;}',1],
 ['and-present','export function o(){return typeof process!=="undefined"&&process.env;}',0],
 ['and-absent-wrong','export function o(){return typeof process==="undefined"&&process.env;}',1],
 ['or-present','export function o(){return typeof process==="undefined"||process.env;}',0],
 ['or-wrong','export function o(){return typeof process!=="undefined"||process.env;}',1],
 ['conditional','export function o(){return typeof process==="undefined"?null:process.env;}',0],
 ['negated-conditional','export function o(){return !(typeof process==="undefined")?process.env:null;}',0],
 ['closure-not-authorized','if(typeof process!=="undefined"){const f=()=>process;}',1],
 ['local-provided','export function o(process){return process.env;}',0],
 ['two-variables-union','export function o(){if(typeof process!=="undefined"&&typeof global!=="undefined")return [process,global];}',0],
 ['or-not-enough','export function o(){if(typeof process!=="undefined"||typeof global!=="undefined")return [process,global];}',2],
 ['reflection-ordinary','export function o(){return globalThis.process;}',0],
 ['module-final-denied','export function o(){return typeof module;}',1],
 ['require-typeof-final-denied','export function o(){return typeof require;}',1],
];
for(const[id,code,count]of guards){const ast=toolchain.parseAst(code),before=JSON.stringify(ast),a=runtimeReferenceAudit(ast);result.cases.push({kind:'environment',id,code,expected:count,actual:a.blocked.length,blocked:a.blocked.map(n=>n.name),passed:a.blocked.length===count});assert.equal(JSON.stringify(ast),before);}
const frozen='/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze';
const metadata=JSON.parse(await readFile(join(frozen,'normal-off.engine.wasm.build.json')));
const builtinManifests=[];
for(const r of metadata.selectedModuleManifests){const p=join(frozen,'source',r.path),b=await readFile(p);assert.equal(digest(b),r.sha256);builtinManifests.push(JSON.parse(b));}
const bundles=[
 ['cjs-exports',`import x from './x.cjs';export function o(){return x;}`,`module.exports={a:1};`,false],
 ['cjs-typeof-module',`import x from './x.cjs';export function o(){return x;}`,`module.exports=typeof module;`,false],
 ['local-module',`export function o(){const module={x:1};return module.x;}`,null,false],
 ['native-default',`import x from './x.cjs';export function o(){return x;}`,`module.exports=require('buffer');`,false],
 ['optional-process',`export function o(){return typeof process==='undefined'?null:process.emit;}`,null,false],
 ['local-process',`export function o(process){return process.env.OTHER;}`,null,false],
 ['default-ambient-process',`export function o(x=process){var process;return x;}`,null,true],
 ['static-ambient-process',`class C{static{var process=1;}}export function o(){return process;}`,null,true],
 ['module-alias',`const m=module;export function o(){return m.exports;}`,null,true],
 ['computed-loader',`export function o(){return module['req'+'uire']('buffer');}`,null,true],
 ['require-empty',`export function o(){return require();}`,null,true],
 ['require-dynamic',`export function o(x){return require(x);}`,null,true],
 ['unselected-native',`import fs from 'node:fs';export function o(){return fs;}`,null,true],
 ['residual-dynamic-import',`export function o(x){return import(x);}`,null,true],
 ['ordinary-reflection',`export function o(){return globalThis['module'];}`,null,false],
];
const cases=join(OWN,'cases');await mkdir(cases);
for(const[id,code,cjs,reject]of bundles){
  const dir=join(cases,id);await mkdir(dir);await writeFile(join(dir,'entry.mjs'),code);if(cjs!==null)await writeFile(join(dir,'x.cjs'),cjs);
  const r={kind:'bundle',id,expectedRefusal:reject,accepted:false,passed:false};
  try{const b=await bundlePackages({...toolchain,input:join(dir,'entry.mjs'),builtinManifests});r.accepted=true;r.passed=!reject;r.imports=b.imports;r.policy=b.policy;await writeFile(join(dir,'bundle.mjs'),b.code);await writeFile(join(dir,'bundle.json'),JSON.stringify({...b,code:undefined},null,2)+'\n');}
  catch(error){r.error={code:error.code??null,message:error.message};r.passed=reject&&error.code==='ERR_SM_PACKAGE_BUNDLE_UNSUPPORTED';await writeFile(join(dir,'refusal.json'),JSON.stringify(r.error,null,2)+'\n');}
  result.cases.push(r);
}
for(const r of initial.files)await verify(r);
result.passed=result.cases.every(r=>r.passed);result.lexicalCases=lexical.length;result.environmentCases=guards.length;result.bundleCases=bundles.length;
result.generatedOrAnalyzedModuleExecuted=false;result.nativeManifestDataReadOnly=true;result.nativePreflightOrHelperOrComponentOrGuestInvoked=false;
await writeFile(join(OWN,'host-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({passed:result.passed,cases:result.cases.length,failures:result.cases.filter(r=>!r.passed)}));if(!result.passed)process.exitCode=1;
