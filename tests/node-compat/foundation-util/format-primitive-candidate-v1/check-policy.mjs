// Read-only host policy regression. Does not call a guest, engine or native API.
import assert from 'node:assert/strict';
import * as canonical from './after/builtins/node-compat/util.mjs';
import {readFile} from 'node:fs/promises';
const header=await readFile(new URL('./after/builtins/node-compat/util-factories.generated.h',import.meta.url),'utf8');
const text=header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";\n$/)[1];
const graph=(0,eval)('"use strict"; ('+text+')')(undefined);
const manifest=JSON.parse(await readFile(new URL('./after/builtins/node-compat/export-manifest.util.node-v22.14.0.json',import.meta.url)));
let rejected=0;
for(const util of[canonical,graph.root]){
 for(const operation of manifest.modules['node:util'].unsupportedStatic)for(const construct of[false,true]){
  let threw=false;
  try{if(construct)Reflect.construct(util[operation],[]);else util[operation]();}
  catch(error){threw=true;assert.equal(error.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(error.module,'node:util');assert.equal(error.operation,operation==='debug'?'debuglog':operation);assert.equal(error.profile,manifest.profileVersion);}
  assert(threw,operation);rejected++;
 }
 assert.equal(util.default.format,util.format);
}
assert.equal(graph.root.types,graph.types.default);assert.equal(graph.root.default.types,graph.types.default);
assert.deepEqual(manifest.modules['node:util'].exports,manifest.modules['node:sys'].exports);
assert.deepEqual(manifest.modules['node:util'].supportedStatic,manifest.modules['node:sys'].supportedStatic);
assert.deepEqual(manifest.modules['node:util'].unsupportedStatic,manifest.modules['node:sys'].unsupportedStatic);
assert(manifest.modules['node:util'].supportedStatic.includes('format'));
assert(!manifest.modules['node:util'].unsupportedStatic.includes('format'));
console.log(JSON.stringify({schemaVersion:1,state:'M0_8_REMAINING_DEFERRED_POLICY_AND_EXPORT_IDENTITIES_PASSED',deferredCallsAndConstructions:rejected,utilSysInventoryIdentical:true,formatDefaultIdentity:true,typesIdentity:true,guestOrEngineInvoked:false}));
