// Source/schema/parse checks only; never invoke the consumer factory.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),at=process.argv.indexOf('--repository');assert(at>=0);const repository=resolve(process.argv[at+1]);
const {validateManifest}=await import(pathToFileURL(join(repository,'builtins/node-compat/validate-manifest.mjs')));
const name='export-manifest.stream-consumers.node-v22.14.0.json',manifestSource=await readFile(join(here,'../'+name),'utf8'),manifest=JSON.parse(manifestSource);
validateManifest(manifest,JSON.parse(await readFile(join(repository,'builtins/node-compat/manifest.schema.json'),'utf8')));
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.14');assert.deepEqual(Object.keys(manifest.modules),['node:stream/consumers']);assert.deepEqual(manifest.modules['node:stream/consumers'].exports,['arrayBuffer','blob','buffer','default','json','text']);
const facade=await readFile(join(here,'facade.mjs'),'utf8');assert(!facade.includes('globalThis'));const script=facade.replace(/^export const /gm,'const ').replace(/^export function /gm,'function ');assert(!/^\s*(?:import|export)\b/m.test(script));
const factory="(function(argument){\n'use strict';\n"+script+'\nreturn createConsumersModule(argument);\n})';assert(!factory.includes(')SM_NODE_PROFILE"'));new vm.Script(factory,{filename:'<unapplied-stream-consumers-factory>'});
const digest=createHash('sha256');for(const[n,s]of[['facade.mjs',facade],[name,manifestSource]])digest.update(n+'\0'+s+'\0');
const output='// Generated UNAPPLIED stream-consumers factory.\n// Canonical-source SHA-256: '+digest.digest('hex')+'\nstatic constexpr const char kStreamConsumersFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\n';
const target=join(here,'factories.generated.h');if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),output);else await writeFile(target,output,{flag:'wx'});
console.log(JSON.stringify({state:'STREAM_CONSUMERS_SCHEMA_SOURCE_PARSE_ONLY_PASSED',bindings:6,factoryInvoked:false,guestExecuted:false}));
