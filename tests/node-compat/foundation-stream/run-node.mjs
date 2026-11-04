// Node reference only. No classic guest implementation is selected or tested.
import assert from 'node:assert/strict';
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import * as consumers from 'node:stream/consumers';
import { Buffer } from 'node:buffer';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { streamChecks } from './valid-api-checks.mjs';
assert.equal(process.version, 'v22.14.0');
const cases = await streamChecks(stream, promises, consumers, Buffer);
assert.deepEqual(cases.find(item => item.name === 'object pipeline and transform flush').result.values, [2, 4, 6, 'tail']);
assert.deepEqual(cases.find(item => item.name === 'consumer mutable Blob part timing').result, [67, 67]);
assert.equal(cases.find(item => item.name === 'consumer streaming UTF8 BOM and incomplete bytes').result, '€�');
assert.equal(cases.find(item => item.name === 'pipeline abort cleanup').result.code, 'ABORT_ERR');
const hash = value => createHash('sha256').update(value).digest('hex');
const sources = {};
for (const name of ['valid-api-checks.mjs', 'run-node.mjs']) sources[name] = hash(await readFile(new URL(name, import.meta.url)));
const report = { schema: 1, node: process.version, platform: process.platform, arch: process.arch,
  referenceCasesPassed: cases.length, cases, sources, candidateCompared: false, componentExecuted: false,
  scope: 'Small ordinary valid-API Node22 reference vectors for future bounded implementations. No classic Node stream support is established in StarlingMonkey; no detachment/shared/GC/OOM fault probes.' };
await writeFile(new URL('node-reference-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ nodeReferenceCases: cases.length, candidateCompared: false, componentExecuted: false }));
