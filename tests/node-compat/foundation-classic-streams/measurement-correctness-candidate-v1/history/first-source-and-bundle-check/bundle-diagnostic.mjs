// Existing Rolldown/profile plugin plus one finite guest-only external module.
// Production manifest admission is never weakened to accept diagnostics.
import assert from 'node:assert/strict';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
export async function bundleDiagnostic({toolchain,admission,input,allowedModuleIds}){
 const {createProfilePlugin}=await import(pathToFileURL(join(admission.toolSourceRoot,'tests/node-compat/profile-bundler.mjs')));
 assert.deepEqual(admission.diagnosticExternalIds,['starling:test-classic-benchmark']);
 const build=await toolchain.rolldown({input,platform:'neutral',treeshake:false,plugins:[
  {name:'finite-classic-correctness-diagnostic',resolveId(id){return id==='starling:test-classic-benchmark'?{id,external:true}:null;}},
  createProfilePlugin(toolchain.parseAst,{builtinManifests:admission.builtinManifests})]});
 try{const generated=await build.generate({format:'esm',codeSplitting:false});assert.equal(generated.output.length,1);const chunk=generated.output[0];
  const expected=['node:stream','node:stream/promises','node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark'];
  assert.deepEqual([...chunk.imports].sort(),expected.sort());const modules=Object.keys(chunk.modules??{});assert.deepEqual([...modules].sort(),[...allowedModuleIds].sort());
  assert.doesNotMatch(chunk.code,/node_modules\/(?:unenv|readable-stream)|createClassicStreams|classic-core\.generated|__require/);
  return{code:chunk.code,imports:chunk.imports,moduleIds:modules};
 }finally{await build.close();}
}
