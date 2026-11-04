// Finite capability contracts, not measured imports or actual engine admission.
import assert from 'node:assert/strict';
export const RANDOM='wasi:random/random@0.2.10';
export const HTTP_IMPORTS=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10',RANDOM]);
export const HTTP_EXPORTS=Object.freeze(['wasi:http/incoming-handler@0.2.10']);
export function variantOptions(label){
 assert(['normal-off','normal-runtime','gc-off'].includes(label),'Choose an explicit finite production variant');
 return Object.freeze({gcStress:label==='gc-off',entropyPolicy:label==='normal-runtime'?'runtime-only':'off'});
}
export function scalarImports(entropyPolicy){assert(['off','runtime-only'].includes(entropyPolicy));return entropyPolicy==='runtime-only'?[RANDOM]:[];}
export function validateHTTPInterfaces(audit){
 assert.equal(audit.entropyPolicy,'runtime-only');assert.deepEqual(audit.emittedImports,HTTP_IMPORTS);assert.deepEqual(audit.emittedExports,HTTP_EXPORTS);
 assert.deepEqual(audit.selectedInterfaces,HTTP_IMPORTS);assert.deepEqual(audit.allowedImports,HTTP_IMPORTS);
 assert.equal(audit.clockDependency.typeOnly,true);assert.deepEqual(audit.clockDependency.callableImports,[]);assert.deepEqual(audit.clockDependency.coreClockImports,[]);
}
