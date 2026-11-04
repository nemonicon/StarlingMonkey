import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {runComposed} from './checks.mjs';
assert.equal(process.version,'v22.14.0');
const expected={};
for(const[key,path]of Object.entries({codecs:'candidate/codec-node-results.json',guards:'candidate/byob-node-results.json',views:'candidate/typed-view-node-results.json',
  controllers:'candidate/controller-node-results.json',iteration:'iteration/node-results.json',data:'dataview/node-results.json'}))
  expected[key]=JSON.parse(await readFile(new URL('../'+path,import.meta.url)));
const report=await runComposed(expected);
await writeFile(new URL('./host-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
assert(!report.failure,JSON.stringify(report.failure));assert(report.passed&&report.originalDescriptorsRestored);console.log(JSON.stringify(report));
