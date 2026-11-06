// Authoring-only metadata query; no explicit ALS instance/hook/workload call.
import assert from 'node:assert/strict';
import * as hooks from 'node:async_hooks';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);
const executable=await readFile(process.execPath),sha=createHash('sha256').update(executable).digest('hex');
assert.equal(sha,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const providers=hooks.asyncWrapProviders;
assert(Object.isFrozen(providers)&&Object.getPrototypeOf(providers)===null);
for(const value of Object.values(providers))assert(Number.isSafeInteger(value)&&value>=0);
const result={schemaVersion:1,node:process.version,executableSha256:sha,
 exports:Object.keys(hooks).sort(),defaultExports:Object.keys(hooks.default).sort(),
 providers,sourceMetadataReadOnly:true,alsInstancesCreated:0,hooksEnabled:0,asyncWorkloadsInvoked:false};
await writeFile(new URL('./node22-surface.json',import.meta.url),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({namedExports:result.exports.length,defaultExports:result.defaultExports.length,providerConstants:Object.keys(providers).length,asyncWorkloadsInvoked:false}));
