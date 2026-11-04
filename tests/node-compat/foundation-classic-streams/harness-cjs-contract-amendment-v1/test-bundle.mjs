// Host bundling only. No app bundle, componentizer or guest is executed.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadToolchain} from '../../toolchain.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
assert.equal(process.version,'v22.14.0');
assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const hash=data=>createHash('sha256').update(data).digest('hex');
const HERE=dirname(fileURLToPath(import.meta.url));
const root=await mkdtemp('/tmp/starling-node-compat/classic-cjs-bundle-v1-');
const authorityPath=join(HERE,'../production-adoption-v1/reviewed-runtime-pins-v1.json');
const authorityBytes=await readFile(authorityPath);assert.equal(hash(authorityBytes),'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e');
const pin=JSON.parse(authorityBytes).variants['normal-off'];
const metadataBytes=await readFile(pin.enginePath+'.build.json');assert.equal(hash(metadataBytes),pin.receiptSha256);
const metadata=JSON.parse(metadataBytes);
const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot:pin.sourceRoot});
const toolchain=await loadToolchain();
const sources=[];
for(const [name,path]of [
  ['guest.mjs',join(HERE,'proposed/harness/guest.mjs')],
  ['cjs-bindings.cjs',join(HERE,'proposed/harness/cjs-bindings.cjs')],
  ['checks.mjs',join(HERE,'../integration-candidate-v1/harness/checks.mjs')],
  ['original-guest.mjs',join(HERE,'before/guest.mjs')]]){
  const bytes=await readFile(path);await writeFile(join(root,name),bytes,{flag:'wx'});
  sources.push({name,path,sha256:hash(bytes),bytes:bytes.length});
}
let originalError;
try{await bundleProfile({...toolchain,builtinManifests,input:join(root,'original-guest.mjs')});}catch(error){originalError=error;}
assert(originalError);assert.match(originalError.message,/Only literal require of admitted builtins in \.cjs is supported/);
const bundled=await bundleProfile({...toolchain,builtinManifests,input:join(root,'guest.mjs')});
const expected=['node:buffer','node:events','node:stream','node:stream/promises','node:util'].sort();
assert.deepEqual([...bundled.imports].sort(),expected);
assert(bundled.moduleIds.some(id=>id.endsWith('/cjs-bindings.cjs.native-profile.mjs')));
assert(bundled.moduleIds.every(id=>!/(?:\/classic-core(?:\.generated)?\.mjs$|\/classic-streams\.mjs$|\/implementation-candidate-v1\/|\/builtins\/node-compat\/|\/node-builtins\/)/.test(id)));
assert(!bundled.code.includes('builtinFactory'));
await writeFile(join(root,'amended.bundle.mjs'),bundled.code,{flag:'wx'});
const result={schemaVersion:1,state:'ACTUAL_GUEST_HOST_BUNDLING_CJS_CONTRACT_PASSED',node:process.version,
  output:root,imports:bundled.imports,moduleIds:bundled.moduleIds,bundleSha256:hash(bundled.code),
  sources,engineSha256:metadata.engineSha256,metadataSha256:hash(metadataBytes),sourceRoot:pin.sourceRoot,
  selectedManifests:metadata.selectedModuleManifests,originalRefusal:originalError.message,
  originalRefusalBeforeComponentize:true,noFacadeOrAdapterBundled:true,guestOrBundleExecuted:false,
  componentizerInvoked:false,nativeBuildPerformed:false,targetHostExecuted:false};
await writeFile(join(root,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,output:root,imports:result.imports,bundleSha256:result.bundleSha256}));
