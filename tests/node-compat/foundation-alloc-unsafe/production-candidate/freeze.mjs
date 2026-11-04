// Verify and index this uninstalled candidate; never changes production files.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../..');
const hash = value => createHash('sha256').update(value).digest('hex');
const source = JSON.parse(await readFile(join(here,'source-receipt.json'))), harness = JSON.parse(await readFile(join(here,'harness-receipt.json')));
for (const item of [...source.changed,...source.unchanged]) {
  const name = item.path.slice('builtins/node-compat/'.length);
  assert.equal(hash(await readFile(join(here,'base/builtins/node-compat',name))),item.before);
  assert.equal(hash(await readFile(join(here,'source/builtins/node-compat',name))),item.after);
  assert.equal(hash(await readFile(join(repository,item.path))),item.before);
}
for (const item of harness.changes) {
  assert.equal(hash(await readFile(join(here,'harness/source',item.path))),item.after);
  if (item.before) {
    assert.equal(hash(await readFile(join(here,'harness/base',item.path))),item.before);
    assert.equal(hash(await readFile(join(repository,item.path))),item.before);
  }
}
const oldProposal = JSON.parse(await readFile(join(here,'../integration-proposal.json')));
assert.equal(hash(await readFile(join(here,'../node-results.json'))),oldProposal.evidence.nodeReportSha256);
assert.equal(hash(await readFile(join(here,'../component-results.json'))),oldProposal.evidence.componentReportSha256);
for (const item of oldProposal.productionUnchanged) assert.equal(hash(await readFile(join(repository,item.path))),item.sha256);
const oldNode = JSON.parse(await readFile(join(here,'../node-results.json')));
for (const [name, sha256] of Object.entries(oldNode.sources)) assert.equal(hash(await readFile(resolve(here,'..',name))),sha256);
const oldComponent = JSON.parse(await readFile(join(here,'../component-results.json')));
for (const item of oldComponent.sourceFiles) assert.equal(hash(await readFile(resolve(here,'..',item.name))),item.sha256);
const names = ['README.md','prepare.mjs','prepare-harness.mjs','run-host.mjs','run-harness-tests.mjs','freeze.mjs',
  'source-receipt.json','harness-receipt.json','host-results.json','harness-host-results.json','core-m0.8.patch','harness-m0.8.patch'];
const files = await Promise.all(names.map(async path => {const bytes=await readFile(join(here,path));return {path,sha256:hash(bytes),bytes:bytes.length};}));
const preserved = await Promise.all(['../README.md','../candidate.mjs','../checks.mjs','../node-results.json','../component-results.json','../integration-proposal.json']
  .map(async path => ({path,sha256:hash(await readFile(join(here,path)))})));
const report = {schema:1,proposalVersion:source.proposalVersion,coreVersion:source.candidateCoreVersion,installed:false,
  sourceFiles:{changed:source.changed.length,unchanged:source.unchanged.length},harnessChangedFiles:harness.changes.length,
  files,preserved,productionAndActiveHarnessUnchanged:true,legacyReportsAndReportedSourcesVerified:true,
  scope:'Candidate source/host-test freeze only. Neither patch applied; no compiled m0.8 proof.'};
await writeFile(join(here,'index.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({files:files.length,preserved:preserved.length,coreVersion:report.coreVersion,installed:false,legacyReportsAndReportedSourcesVerified:true}));
