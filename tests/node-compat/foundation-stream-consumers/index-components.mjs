// Verify the additional component evidence without rewriting the source freeze.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),hash=value=>createHash('sha256').update(value).digest('hex');
const sourceIndexBytes=await readFile(join(here,'index.json')),source=JSON.parse(sourceIndexBytes);
for(const item of source.files)assert.equal(hash(await readFile(join(here,item.path))),item.sha256,'Preserved source stage: '+item.path);
const main=JSON.parse(await readFile(join(here,'metadata-v2/component-results.json'))),reflection=JSON.parse(await readFile(join(here,'metadata-v2/reflection-results.json')));
const diagnostic=JSON.parse(await readFile(join(here,'reflection-v1/component-results.json'))),mismatch=JSON.parse(await readFile(join(here,'reflection-v1/mismatch.json')));
assert.equal(mismatch.acceptedAsExactNodeReflection,false);
for(const report of [main,reflection,diagnostic]){
  assert.equal(hash(await readFile(report.fixture.componentPath)),report.fixture.componentSha256);
  assert.equal(hash(await readFile(report.fixture.sourcePath)),report.fixture.sourceSha256);
  assert.deepEqual(report.fixture.interfaceAudit.emittedImports,[]);
  assert.equal(report.engineSha256,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09');
  assert.equal(report.sourceFilesVerified,293);assert.equal(report.installed,false);
}
assert.equal(reflection.mainReportSha256,hash(await readFile(join(here,'metadata-v2/component-results.json'))));
for(const report of [main,reflection])for(const item of report.sources)assert.equal(hash(await readFile(join(here,'metadata-v2',item.path))),item.sha256);
for(const item of diagnostic.sources)assert.equal(hash(await readFile(join(here,'reflection-v1',item.path))),item.sha256);
for(const item of main.engineReceipt.sourceManifest)assert.equal(hash(await readFile(join(main.sourceRoot,item.path))),item.sha256);
for(const name of ['text','json']){
  assert.deepEqual(main.calls[0].profile[2].result.ownKeys[name],['length','name']);
  assert.deepEqual(diagnostic.calls[0].profile[2].result.ownKeys[name],['name','length']);
}
assert.equal(main.initialization.length,11);assert.equal(main.differentialGroups,18);assert.equal(main.profileGroups,12);
assert.deepEqual(main.calls.map(c=>c.calls),[1,2]);assert.equal(main.wasmtime.observed.calls,1);
assert.equal(main.oracleSelection.excluded.length,1);assert.equal(main.oracleSelection.guestInvalidInputVectors,5);
const contract=JSON.parse(await readFile(join(here,'export-contract.node-v22.14.0.json')));
const names=['guest-oracle.mjs','component-checks.mjs','component.mjs','run-component.mjs','component-results.json','prepare-metadata-v2.mjs','component-status.md','index-components.mjs',
  ...['guest-oracle.mjs','component-checks.mjs','component.mjs','run-component.mjs','component-results.json','mismatch.json'].map(p=>'reflection-v1/'+p),
  ...['create-module.mjs','prototype.mjs','component-checks.mjs','component.mjs','run-component.mjs','component-results.json','source-receipt.json','reflection-component.mjs','run-reflection.mjs','reflection-results.json'].map(p=>'metadata-v2/'+p)];
const files=await Promise.all(names.map(async path=>{const bytes=await readFile(join(here,path));return{path,sha256:hash(bytes),bytes:bytes.length};}));
const index={schema:1,installed:false,contractVersion:main.contractVersion,implementationRevision:'metadata-v2',selectedProductionProfileVersion:null,
  sourceFreezeSha256:hash(sourceIndexBytes),sourceStageUnchanged:true,engineSha256:main.engineSha256,sourceInputsVerified:293,
  exactNativeDecoder:main.exactNativeDecoder,expectedHostImports:[],emittedHostImports:[],testedLimits:contract.limits,
  scalar:{componentSha256:main.fixture.componentSha256,componentBytes:main.fixture.componentBytes,differentialGroups:18,profileGroups:12,
    invalidKindVectors:'5 of 6; native Blob constructor vector deliberately remains Node-only',retainedCalls:[1,2],freshWasmtimeCall:1,initializationFailures:11},
  nativeReadableStream:main.calls[0].nativeReadableStream,
  reflection:{diagnosticV1Sha256:diagnostic.fixture.componentSha256,metadataV2Sha256:main.fixture.componentSha256,descriptorComponentSha256:reflection.fixture.componentSha256,
    nativeOwnKeyOrder:reflection.observed.text.ownKeys,valuesAndAttributesMatchNode:true},
  files,scope:'Isolated bundled text/json facade over actual native decoder, not an installed module. No Blob/lifetime/fault probe, classic/Web Stream support, HTTP deployment or performance claim.'};
await writeFile(join(here,'component-index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({files:files.length,component:main.fixture.componentSha256,groups:18,profileGroups:12,initializationFailures:11,imports:[],sourceStageUnchanged:true,installed:false}));
