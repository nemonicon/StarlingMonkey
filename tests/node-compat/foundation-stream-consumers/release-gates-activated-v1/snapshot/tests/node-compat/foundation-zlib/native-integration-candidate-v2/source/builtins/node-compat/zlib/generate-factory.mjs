// Source generation/check only. The returned factory is never invoked here.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),at=process.argv.indexOf('--repository');
assert(at>=0);const repository=resolve(process.argv[at+1]);
const {validateManifest}=await import(pathToFileURL(join(repository,'builtins/node-compat/validate-manifest.mjs')));
const manifestPath=join(here,'../export-manifest.zlib.node-v22.14.0.json');
const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
validateManifest(manifest,JSON.parse(await readFile(join(repository,'builtins/node-compat/manifest.schema.json'),'utf8')));
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.13');
assert.deepEqual(Object.keys(manifest.modules),['node:zlib']);
assert.deepEqual(manifest.modules['node:zlib'].aliases,['zlib']);
assert.equal(manifest.modules['node:zlib'].exports.length,40);
let constants=await readFile(join(here,'constant-data.generated.mjs'),'utf8');
let facade=await readFile(join(here,'facade.mjs'),'utf8');
const sources=[['constant-data.generated.mjs',constants],['facade.mjs',facade],['export-manifest.zlib.node-v22.14.0.json',await readFile(manifestPath,'utf8')]];
const dependency="import {createZlibData} from './constant-data.generated.mjs';";
assert.equal(facade.split(dependency).length-1,1);facade=facade.replace(dependency,'');
constants=constants.replace(/^export function /gm,'function ');facade=facade.replace(/^export function /gm,'function ');
assert(!/^\s*(?:import|export)\b/m.test(constants+facade));
assert(constants.includes('"ZLIB_VERNUM":backend.vernum')&&!constants.includes('"ZLIB_VERNUM":4865'));
assert(constants.includes('"Z_MAX_CHUNK":Infinity'));
const factory=`(function(argument){\n'use strict';\n${constants}\n${facade}\nreturn createZlibModule(argument.kernel, argument.Buffer);\n})`;
assert(!factory.includes(')SM_NODE_PROFILE"'));
new vm.Script(factory,{filename:'<unapplied-zlib-factory>'}); // Parse, do not run.
const digest=createHash('sha256');for(const[name,source]of sources)digest.update(name+'\0'+source+'\0');
const output='// Generated unapplied bounded zlib proposal; do not edit.\n'+
 `// Canonical-source SHA-256: ${digest.digest('hex')}\n`+
 `static constexpr const char kZlibFactorySource[] = R"SM_NODE_PROFILE(${factory})SM_NODE_PROFILE";\n`;
const target=join(here,'factories.generated.h');
if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),output);
else await writeFile(target,output,{flag:'wx'});
console.log(JSON.stringify({state:'ZLIB_SOURCE_FACTORY_SCHEMA_PARSE_ONLY_PASSED',namespaceBindings:40,aliases:['node:zlib','zlib'],headerSha256:createHash('sha256').update(output).digest('hex'),factoryInvoked:false,codecOrGuestExecuted:false}));
