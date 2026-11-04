// Actual immutable metadata/source selection only; no engine execution.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {selectedManifestsForEngine,builtinMap} from '../source/tests/node-compat/module-selection.mjs';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),reports=[];
for(const[name,engine,sourceRoot]of [
  ['v5-assert-querystring-off','/tmp/starling-node-compat/foundations-v5/native-freeze/off-path-events.engine.wasm','/tmp/starling-node-compat/foundations-v5/native-freeze/source'],
  ['v6-util-off','/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v6/native-freeze/source'],
  ['v8-off','/tmp/starling-node-compat/foundations-v8/native-freeze/off-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v8/native-freeze/source'],
  ['v8-gc','/tmp/starling-node-compat/foundations-v8/native-freeze/gc-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v8/native-freeze/source'],
  ['v8-runtime','/tmp/starling-node-compat/foundations-v8/native-freeze/runtime-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v8/native-freeze/source'],
]){
  const bytes=await readFile(engine+'.build.json'),metadata=JSON.parse(bytes);
  assert.equal(hash(await readFile(engine)),metadata.engineSha256);
  const manifests=selectedManifestsForEngine(metadata,{sourceRoot});assert.equal(builtinMap(manifests)['node:stream/web'],undefined);
  reports.push({name,engineSha256:metadata.engineSha256,receiptSha256:hash(bytes),sourceRoot,selectedManifests:manifests.length,newModuleAbsent:true});
}
const result={scope:'Actual historical receipt admission only; no engine or JavaScript stream operation executed',reports};
await writeFile(new URL('./legacy-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({legacyReceipts:reports.length,passed:true,engineExecuted:false}));
