import assert from 'node:assert/strict';
import * as oracle from 'node:assert';
import * as oracleStrict from 'node:assert/strict';
import * as prototype from './prototype.mjs';
import * as prototypeStrict from './strict.mjs';
import { assertChecks, prototypeOnlyChecks } from './checks.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
const cases = assertChecks(oracle, oracleStrict);
const observed = assertChecks(prototype, prototypeStrict);
const manifest = JSON.parse(await readFile(new URL('export-manifest.assert.node-v22.14.0.json', import.meta.url)));
assert.deepEqual(Object.keys(manifest.modules).sort(), ['node:assert', 'node:assert/strict']);
assert.deepEqual(manifest.requiredHostInterfaces, []);
for (const [id, namespace] of [['node:assert', oracle], ['node:assert/strict', oracleStrict]])
  assert.deepEqual(manifest.modules[id].exports, Object.getOwnPropertyNames(namespace).sort(), id);
assert.equal(observed.length, cases.length);
for (let i = 0; i < cases.length; i++) assert.deepEqual(observed[i], cases[i], cases[i].name);
const deferredAndMutationCases = prototypeOnlyChecks(prototype);
const sources = {};
for (const file of ['prototype.mjs', 'strict.mjs', 'checks.mjs', 'run-node.mjs', 'export-manifest.assert.node-v22.14.0.json'])
  sources[file] = hash(await readFile(new URL(file, import.meta.url)));
const inventory = {
  schema: 1, node: process.version,
  nodeEmbeddedSourceSha256: Object.fromEntries(['assert', 'assert/strict', 'internal/assert/assertion_error', 'internal/assert/utils']
    .map(name => [name, hash(process.binding('natives')[name])])),
  modules: Object.fromEntries([['node:assert', oracle], ['node:assert/strict', oracleStrict]].map(([id, module]) => [id, {
    exports: Object.getOwnPropertyNames(module).sort().map(name => ({ name, type: typeof module[name], functionName: module[name].name, length: module[name].length })),
    defaultOwnNames: Object.getOwnPropertyNames(module.default),
  }])),
  aliases: cases.find(item => item.name === 'root and strict graph'),
};
await writeFile(new URL('inventory.node-v22.14.0.json', import.meta.url), JSON.stringify(inventory, null, 2)+'\n');
const report = { schema: 1, node: process.version, prototypeInstalledAsBuiltin: false, sources,
  nodeEmbeddedSourceSha256: inventory.nodeEmbeddedSourceSha256,
  differentialCasesPassed: cases.length, cases, deferredAndMutationCases,
  scope: 'Pinned Node22 host differential versus isolated JS proposal. No native registration, bundler builtin selection, real component execution or target-host proof established.' };
await writeFile(new URL('node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ differentialCasesPassed: cases.length, prototypeOnlyCasesPassed: deferredAndMutationCases.length }));
