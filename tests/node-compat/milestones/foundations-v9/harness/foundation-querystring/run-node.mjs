import assert from 'node:assert/strict';
import * as oracle from 'node:querystring';
import * as prototype from './prototype.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { querystringChecks, prototypeOnlyChecks } from './checks.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
const manifest = JSON.parse(await readFile(new URL('export-manifest.querystring.node-v22.14.0.json', import.meta.url)));
assert.deepEqual(manifest.modules['node:querystring'].exports, Object.getOwnPropertyNames(oracle).sort());
assert.deepEqual(manifest.requiredHostInterfaces, []);
const cases = querystringChecks(oracle), observed = querystringChecks(prototype);
assert.equal(observed.length, cases.length);
for (let i = 0; i < cases.length; i++) assert.deepEqual(observed[i], cases[i], cases[i].name);
const profileCases = prototypeOnlyChecks(prototype);
const sources = {};
for (const name of ['prototype.mjs', 'checks.mjs', 'run-node.mjs', 'export-manifest.querystring.node-v22.14.0.json'])
  sources[name] = hash(await readFile(new URL(name, import.meta.url)));
const inventory = { schema: 1, node: process.version,
  nodeEmbeddedSourceSha256: Object.fromEntries(['querystring', 'internal/querystring'].map(name => [name, hash(process.binding('natives')[name])])),
  exports: Object.getOwnPropertyNames(oracle).map(name => ({ name, type: typeof oracle[name], functionName: oracle[name]?.name, length: oracle[name]?.length })),
  defaultOwnNames: Object.getOwnPropertyNames(oracle.default), defaultPrototypeIsObjectPrototype: Object.getPrototypeOf(oracle.default) === Object.prototype,
  initialAliases: { encodeIsStringify: oracle.encode === oracle.stringify, decodeIsParse: oracle.decode === oracle.parse },
  nonstringUnescapeBufferOracle: [undefined, null, 3, true, { length: 1 }].map(value => { try { const bytes = oracle.unescapeBuffer(value); return { type: typeof value, bytes: [...bytes] }; } catch (error) { return { type: typeof value, error: { name: error.name, code: error.code } }; } }),
};
await writeFile(new URL('inventory.node-v22.14.0.json', import.meta.url), JSON.stringify(inventory, null, 2)+'\n');
const report = { schema: 1, node: process.version, installedBuiltin: false, sources,
  nodeEmbeddedSourceSha256: inventory.nodeEmbeddedSourceSha256, differentialGroupsPassed: cases.length,
  customSeparatorVectors: 210, byteFallbackVectors: 1536, cases, profileCases,
  scope: 'Node22 oracle versus isolated guest prototype using Node Buffer; native guest Buffer/component decoder equivalence not established. No native registration, component execution or target-host claim.' };
await writeFile(new URL('node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ differentialGroupsPassed: cases.length, customSeparatorVectors: 210, byteFallbackVectors: 1536, profileCasesPassed: profileCases.length }));
