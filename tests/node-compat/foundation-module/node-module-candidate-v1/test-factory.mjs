// Host Source model only. It does not call the uncompiled C++ provider.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {createModuleAPI} from './module-core.mjs';
import {validateManifest} from '../../../../builtins/node-compat/validate-manifest.mjs';
const read=n=>JSON.parse(readFileSync(new URL(n,import.meta.url),'utf8'));
const inventory=read('./node-inventory.json'),manifest=read('./export-manifest.module.node-v22.14.0.json');
validateManifest(manifest,read('../../../../builtins/node-compat/manifest.schema.json'));
const header=readFileSync(new URL('./module-factory.generated.h',import.meta.url),'utf8');
const source=header.slice(header.indexOf('R"SM_MODULE(')+12,header.lastIndexOf(')SM_MODULE";'));
const provider={cwd(){throw new Error('No native calls during factory installation');},kind(){throw new Error('No native calls during factory installation');},readText(){throw new Error('No native calls during factory installation');},realpath(){throw new Error('No native calls during factory installation');},compile(){throw new Error('No native calls during factory installation');},getBuiltin(){throw new Error('No native calls during factory installation');}};
const generated=vm.runInThisContext(source,{filename:'<actual-generated-module-factory>'})(provider);
const canonical=createModuleAPI(provider,inventory.builtinNames,inventory.prefixOnlyNames,inventory.namespaceKeys,inventory.constants);
assert.deepEqual(Object.keys(generated).sort(),inventory.namespaceKeys);assert.deepEqual(Object.keys(generated).sort(),Object.keys(canonical).sort());
assert.equal(generated.default,generated.Module);assert.equal(generated.default.isBuiltin('node:path'),true);assert.equal(generated.default.isBuiltin('node:test'),true);assert.equal(generated.default.isBuiltin('test'),false);
assert.equal(generated.default.createRequire('/tmp/source-only.js')('module'),generated.default);
assert.throws(()=>generated.register('x'),{code:'ERR_SM_NODE_UNSUPPORTED'});
console.log(JSON.stringify({schemaVersion:1,state:'GENERATED_GUEST_FACTORY_HOST_SOURCE_CHECK_PASSED',checks:8,manifestSchemaPassed:true,nativeProviderCalled:false,guestOrApplicationExecuted:false}));
