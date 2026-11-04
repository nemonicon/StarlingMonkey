// Preserve the unmodified prototype/oracles and the v1 reflection diagnostic.
// Generate a separate source candidate for bounded lazy-property materialization.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile,stat} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),archive=join(here,'reflection-v1'),v2=join(here,'metadata-v2');
const hash=value=>createHash('sha256').update(value).digest('hex');
try{await stat(v2);throw new Error('metadata-v2 already exists; inspect preserved sources instead of overwriting');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(archive,{recursive:true});await mkdir(v2,{recursive:true});
const names=['guest-oracle.mjs','component-checks.mjs','component.mjs','run-component.mjs','component-results.json'];
const archived=[];
for(const name of names){const bytes=await readFile(join(here,name));await writeFile(join(archive,name),bytes);archived.push({path:name,sha256:hash(bytes)});}
const diagnostic=JSON.parse(await readFile(join(here,'component-results.json')));
for(const name of ['text','json'])assert.deepEqual(diagnostic.calls[0].profile[2].result.ownKeys[name],['name','length']);
await writeFile(join(archive,'mismatch.json'),JSON.stringify({schema:1,acceptedAsExactNodeReflection:false,
  firstStrictGate:{name:'Error',message:'Consumer policy: async own keys',expected:['length','name'],
    initialFailedArtifactRetained:false,scope:'The initial failed output was replaced by the following diagnostic before this archive; the exact observed mismatch is retained here and in the full diagnostic report.'},
  diagnostic:{componentSha256:diagnostic.fixture.componentSha256,componentBytes:diagnostic.fixture.componentBytes,
    componentPath:diagnostic.fixture.componentPath,sourcePath:diagnostic.fixture.sourcePath,
    observedOwnKeys:diagnostic.calls[0].profile[2].result.ownKeys,wasmtimeOwnKeys:diagnostic.wasmtime.observed.profile[2].result.ownKeys,
    groups:18,policyGroups:12,initializationFailures:diagnostic.initialization.length,hostImports:[],
    scope:'Diagnostic checks the same function-property set but records and permits the order difference; this is not an exact Node reflection pass.'},
  archiveSources:archived,productionEdits:false},null,2)+'\n');
const original=await readFile(join(here,'create-module.mjs'),'utf8');
const start='  const Apply = Reflect.apply, Define = Object.defineProperty, Freeze = Object.freeze;';
assert.equal(original.split(start).length,2);
let candidate=original.replace(start,start+'\n  const Descriptor = Object.getOwnPropertyDescriptor;');
const boundary='  const defaultObject = { arrayBuffer, blob, buffer, text, json };';assert.equal(candidate.split(boundary).length,2);
candidate=candidate.replace(boundary,`  // Resolve SpiderMonkey lazy function properties before application reads.
  // The captured descriptors retain native values/attributes; no new property
  // is defined. Node creates length then name for these async functions.
  Descriptor(text, 'length'); Descriptor(text, 'name');
  Descriptor(json, 'length'); Descriptor(json, 'name');
${boundary}`);
await writeFile(join(v2,'create-module.mjs'),candidate);
await writeFile(join(v2,'prototype.mjs'),await readFile(join(here,'prototype.mjs')));
await writeFile(join(v2,'component.mjs'),await readFile(join(here,'component.mjs')));
let checks=await readFile(join(here,'component-checks.mjs'),'utf8');
const permissive="      check(ownKeys[name].length===2&&ownKeys[name].includes('length')&&ownKeys[name].includes('name'),'async own key set '+JSON.stringify(ownKeys[name]));";
assert.equal(checks.split(permissive).length,2);checks=checks.replace(permissive,"      equal(ownKeys[name],['length','name'],'exact Node async own-key order');");
await writeFile(join(v2,'component-checks.mjs'),checks);
let runner=await readFile(join(here,'run-component.mjs'),'utf8');
runner=runner.replace("import { dirname,join } from 'node:path';","import { dirname,join,resolve } from 'node:path';");
runner=runner.replace("from '../foundations/","from '../../foundations/").replace("from '../toolchain.mjs'","from '../../toolchain.mjs'").replace("from '../profile-bundler.mjs'","from '../../profile-bundler.mjs'");
runner=runner.replace("from './guest-oracle.mjs'","from '../guest-oracle.mjs'");
runner=runner.replace("const here=dirname(fileURLToPath(import.meta.url));","const here=dirname(fileURLToPath(import.meta.url)),sourceHere=resolve(here,'..');");
for(const name of ['index.json','node-results.json','prototype-node-results.json','node-checks.mjs','source-audit.json'])runner=runner.replaceAll("join(here,'"+name+"')","join(sourceHere,'"+name+"')");
runner=runner.replace('join(here,file.path)','join(sourceHere,file.path)');
runner=runner.replace("for(const name of ['text','json'])assert.deepEqual([...ownKeys[name]].sort(),['length','name']);","for(const name of ['text','json'])assert.deepEqual(ownKeys[name],['length','name']);");
runner=runner.replace("['guest-oracle.mjs','component-checks.mjs','component.mjs','run-component.mjs']","['create-module.mjs','prototype.mjs','component-checks.mjs','component.mjs','run-component.mjs']");
runner=runner.replace('installed:false,nativeBlobInvoked:false,sourceFreezeSha256:',"installed:false,implementationRevision:'metadata-v2',preservedV1ReflectionDiagnostic:'../reflection-v1/component-results.json',nativeBlobInvoked:false,sourceFreezeSha256:");
await writeFile(join(v2,'run-component.mjs'),runner);
await writeFile(join(v2,'source-receipt.json'),JSON.stringify({schema:1,implementationRevision:'metadata-v2',installed:false,
  originalFactorySha256:hash(original),candidateFactorySha256:hash(candidate),
  delta:'Capture Object.getOwnPropertyDescriptor and resolve text/json length then name before exposing either function. No property value/attribute redefinition or algorithm change.',
  originalSourceFreezeSha256:hash(await readFile(join(here,'index.json'))),reflectionDiagnosticSha256:hash(await readFile(join(archive,'mismatch.json')))},null,2)+'\n');
console.log(JSON.stringify({archive:'reflection-v1',candidate:'metadata-v2',originalFactorySha256:hash(original),candidateFactorySha256:hash(candidate),installed:false}));
