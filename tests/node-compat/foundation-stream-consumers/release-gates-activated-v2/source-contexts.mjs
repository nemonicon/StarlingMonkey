// Explicit contexts. No owner selector/preflight/tool/package is imported here.
import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {regular,safeLocal} from './physical.mjs';
const canonical=path=>{assert(typeof path==='string'&&path.startsWith('/')&&resolve(path)===path&&!path.includes('\0')&&!path.includes('\\'));return path;};
const alias=path=>path.replace(/^\/tmp(?=\/|$)/,'/private/tmp');
export function sourceContexts(config,native,pin){
 const admissionSourceRoot=canonical(config.admissionSourceRoot),runtimeSourceRoot=canonical(config.runtimeSourceRoot);
 assert.equal(admissionSourceRoot,config.nativeConfiguredSourceRoot);
 assert.equal(runtimeSourceRoot,config.nativeFrozenSourceRoot);
 assert.equal(runtimeSourceRoot,native.sourceRoot);assert.equal(runtimeSourceRoot,pin.sourceRoot);
 assert.notEqual(alias(admissionSourceRoot),alias(runtimeSourceRoot),'Configured native/tool and frozen native contexts must stay distinct');
 assert.equal(native.metadata.sourceManifest.length,355);assert.equal(new Set(native.metadata.sourceManifest.map(row=>row.path)).size,355);
 return Object.freeze({admissionSourceRoot,runtimeSourceRoot});
}
export async function verifyNativeContexts(metadata,roots){
 assert.equal(metadata.sourceManifest.length,355);
 for(const row of metadata.sourceManifest){
  await regular(await safeLocal(roots.admissionSourceRoot,row.path),row.sha256);
  await regular(await safeLocal(roots.runtimeSourceRoot,row.path),row.sha256);
 }
 return Object.freeze({nativeSources:355,configuredAndFrozenNativeBytesMatched:true,toolDependenciesVerifiedHere:false,metadataProjected:false});
}
export function assertCoreContext(core,metadata){
 assert.equal(core.schema,1);assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
 const names=['buffer-facade.mjs','unsupported.mjs','export-manifest.node-v22.14.0.json','factories.generated.h','buffer.cpp'].map(name=>'builtins/node-compat/'+name);
 assert.deepEqual(Object.keys(core.sourceHashes).sort(),[...names].sort());
 for(const name of names)assert.equal(core.sourceHashes[name],metadata.sourceManifest.find(row=>row.path===name)?.sha256);
 assert(!Object.hasOwn(core,'sourceRoot'),'Core contract is a no-path validated hash object, not a root projection');return core;
}
