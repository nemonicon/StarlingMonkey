// Raw build/validation selection only. Never an operational engine admission.
import assert from 'node:assert/strict';
import {readFileSync,lstatSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function selectBuildManifests(metadata,{sourceRoot,buildAdmission}){
 assert.equal(buildAdmission.sourceInputs,355);assert.equal(buildAdmission.runtimeOrGuestExecutionProof,false);
 const root=resolve(sourceRoot),sources=new Map(metadata.sourceManifest.map(row=>[row.path,row.sha256]));
 assert.equal(sources.size,355);
 const expected=['builtins/node-compat/export-manifest.node-v22.14.0.json'];
 for(const[field,name]of [['pathEnabled','path'],['eventsEnabled','events'],['stringDecoderEnabled','string-decoder'],['assertEnabled','assert'],['querystringEnabled','querystring'],['utilEnabled','util'],['streamWebEnabled','stream-web'],['classicStreamsEnabled','classic-streams'],['zlibEnabled','zlib'],['streamConsumersEnabled','stream-consumers']]){
  assert.equal(typeof metadata[field],'boolean');
  if(metadata[field])expected.push(name==='classic-streams'?'builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json':`builtins/node-compat/export-manifest.${name}.node-v22.14.0.json`);
 }
 assert.deepEqual(metadata.selectedModuleManifests.map(row=>row.path).sort(),[...expected].sort());
 const {validateManifest}=await import(pathToFileURL(join(root,'builtins/node-compat/validate-manifest.mjs')));
 const {builtinMap}=await import(pathToFileURL(join(root,'tests/node-compat/module-selection.mjs')));
 const {validateCoreExpectations}=await import(pathToFileURL(join(root,'tests/node-compat/core-expectations.mjs')));
 const schema=JSON.parse(readFileSync(join(root,'builtins/node-compat/manifest.schema.json')));
 const manifests=metadata.selectedModuleManifests.map(entry=>{
  assert(expected.includes(entry.path));let path=root;
  for(const part of entry.path.split('/')){assert(part&&part!=='.'&&part!=='..');path=join(path,part);assert(!lstatSync(path).isSymbolicLink());}
  const bytes=readFileSync(path);assert.equal(hash(bytes),sources.get(entry.path));
  assert.equal(entry.sha256,sources.get(entry.path));const manifest=validateManifest(JSON.parse(bytes),schema);
  if(entry.profileVersion!==undefined)assert.equal(entry.profileVersion,manifest.profileVersion);
  return manifest;
 });
 builtinMap(manifests); // Collision/inventory checks only; does not admit metadata.
 const buffer=manifests.find(manifest=>Object.hasOwn(manifest.modules,'node:buffer'));
 assert.equal(buffer.profileVersion,'sm-node-22.14.0-m0.11');
 const coreNames=['buffer-facade.mjs','unsupported.mjs','export-manifest.node-v22.14.0.json','factories.generated.h','buffer.cpp'];
 const sourceHashes=Object.fromEntries(coreNames.map(name=>{const path='builtins/node-compat/'+name;return[path,sources.get(path)];}));
 const core=validateCoreExpectations({schema:1,coreVersion:buffer.profileVersion,allocUnsafePolicy:'zeroed-no-pool-direct-u8-v1',unsupportedStatic:['copyBytesFrom','of','allocUnsafeSlow','compare','concat'],prototypeRefusals:91,manifestSha256:sources.get(expected[0]),sourceHashes});
 assert.deepEqual(buffer.modules['node:buffer'].unsupportedStatic,core.unsupportedStatic);
 return{manifests,core,validationBootstrapOnly:true,operationalAdmission:false};
}
