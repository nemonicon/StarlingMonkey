import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../..');
const hash=value=>createHash('sha256').update(value).digest('hex');
const node=JSON.parse(await readFile(join(here,'node-results.json'))),prototype=JSON.parse(await readFile(join(here,'prototype-node-results.json'))),audit=JSON.parse(await readFile(join(here,'source-audit.json')));
for(const report of [node,prototype])for(const[path,sha256]of Object.entries(report.sources))assert.equal(hash(await readFile(join(here,path))),sha256);
assert.equal(hash(await readFile(join(here,'node-results.json'))),prototype.oracleSha256);
for(const item of audit.sources.filter(item=>item.origin==='repository'))assert.equal(hash(await readFile(join(repository,item.path))),item.sha256,'Audited source/test changed: '+item.path);
const matrix=JSON.parse(await readFile(join(here,'api-matrix.json'))),contract=JSON.parse(await readFile(join(here,'export-contract.node-v22.14.0.json')));
assert.deepEqual(matrix.apis.map(row=>row.export).sort(),node.inventory.exports);assert.deepEqual(contract.exports,node.inventory.exports);
assert.equal(matrix.productionModuleInstalled,false);assert.equal(contract.installed,false);assert.equal(contract.selectedProductionProfileVersion,null);
const names=['README.md','api-matrix.json','export-contract.node-v22.14.0.json','create-module.mjs','prototype.mjs','LICENSE.node','node-checks.mjs','run-node.mjs','run-prototype-node.mjs','audit-sources.mjs','freeze.mjs','node-results.json','prototype-node-results.json','source-audit.json'];
const files=await Promise.all(names.map(async path=>{const bytes=await readFile(join(here,path));return{path,sha256:hash(bytes),bytes:bytes.length};}));
const index={schema:1,contractVersion:contract.contractVersion,installed:false,selectedProductionProfileVersion:null,
  sourceOnlyAndNodeHost:true,guestProbesRun:false,nativeBlobChangesCompiled:false,
  nodeOracle:{textGroups:node.text.length,blobGroups:node.blob.length},prototype:{differentialGroups:prototype.differentialGroups,profileGroups:prototype.profileGroups},
  sourceAudit:{files:audit.sources.length,nativeSymbols:audit.nativeSymbols.length,frozenRelevantInputs:audit.nativeSourcePin.verifiedRelevantInputs.length,engineSha256:audit.nativeSourcePin.engineSha256},
  files,scope:'Integrity index for isolated source/Node-host evidence only. No production/native/component support result.'};
await writeFile(join(here,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({files:files.length,nodeGroups:node.text.length+node.blob.length,prototypeDifferentialGroups:prototype.differentialGroups,prototypeProfileGroups:prototype.profileGroups,guestProbesRun:false,installed:false}));
