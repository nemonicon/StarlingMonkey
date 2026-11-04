// Child entry selected only by an external Root action authority, not native pins.
import assert from 'node:assert/strict';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {here,regular} from './physical.mjs';
import {assertRuntimeAuthority,variantForScope} from './contracts.mjs';
import {verifyFamily} from './native-preflight.mjs';
const scope=process.argv[2],output=resolve(process.argv[3]);
const family=await verifyFamily();
const authority=JSON.parse(await regular(process.env.NODE_COMPAT_RELEASE_ACTION_AUTHORITY,process.env.NODE_COMPAT_RELEASE_ACTION_AUTHORITY_SHA256));
assertRuntimeAuthority(authority,{familyIndexSha256:family.indexSha256,scope,output});
for(const name of ['NODE_COMPAT_RELEASE_RESUME','NODE_COMPAT_OPTIONAL_RESUME','NODE_COMPAT_RESUME'])assert(!process.env[name],name);
const root=join(here,'snapshot/tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1');
const entries={
 'release-off':['release/run-release.mjs','NODE_COMPAT_PRODUCTION_RELEASE_OUTPUT'],
 'allocator-gc':['common/run-allocator-gc.mjs','NODE_COMPAT_ALLOCATOR_GC_OUTPUT'],
 'focused-off':['capability/run-focused.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT'],
 'focused-runtime':['capability/run-focused.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT'],
 'focused-gc':['capability/run-gc.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT'],
 'getter':['capability/run-getter.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT'],
};
assert(Object.hasOwn(entries,scope));const [entry,variable]=entries[scope];
for(const key of Object.keys(process.env))if(key.startsWith('NODE_COMPAT_')&&key.endsWith('_OUTPUT'))delete process.env[key];
process.env[variable]=output;process.env.NODE_COMPAT_FOLLOWON_VARIANT=variantForScope(scope);
process.env.NODE_COMPAT_RELEASE_SCOPE=scope;process.env.NODE_COMPAT_RELEASE_SCOPE_OUTPUT=output;
await import(pathToFileURL(join(root,entry)));
