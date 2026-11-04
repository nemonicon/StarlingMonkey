import assert from 'node:assert/strict';
import { Buffer, constants } from 'node:buffer';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';
import { runInThisContext } from 'node:vm';
import { createRequire } from 'node:module';
import { createAllocUnsafeCandidate } from './candidate.mjs';
import { allocationChecks, candidateChecks, temporarilyPatch } from './checks.mjs';
import { bufferListDemandModule } from './demand-source.mjs';
import { demandChecks } from './demand-checks.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const path = join(toolchain, 'node_modules/readable-stream/lib/internal/streams/buffer_list.js');
const original = Buffer.allocUnsafe, candidate = createAllocUnsafeCandidate(Buffer);
const oracle = allocationChecks(Buffer, original), observed = allocationChecks(Buffer, candidate);
assert.deepEqual(observed, oracle);
const profile = candidateChecks(Buffer, candidate, createAllocUnsafeCandidate);
const source = await readFile(path, 'utf8'), demand = bufferListDemandModule(source);
const factory = runInThisContext('"use strict";\n'+demand.text.replace('export function createDemandList', 'function createDemandList')+'\ncreateDemandList;');
const require = createRequire(import.meta.url), ActualList = require(path);
const actualDemand = demandChecks(Buffer, ActualList), excerptDemand = demandChecks(Buffer, factory(Buffer));
assert.deepEqual(excerptDemand, actualDemand);
const candidateDemand = temporarilyPatch(Buffer, candidate, () => demandChecks(Buffer, factory(Buffer)));
assert.deepEqual(candidateDemand, actualDemand); assert.equal(Buffer.allocUnsafe, original);
// Observe pool metadata only. Never read or print an uninitialized Node byte.
const pooled = original(1), fractional = original(0.5), bounded = candidate(1);
const sources = {};
for (const name of ['candidate.mjs', 'checks.mjs', 'demand-source.mjs', 'demand-checks.mjs', 'run-node.mjs'])
  sources[name] = hash(await readFile(new URL(name, import.meta.url)));
const report = { schema: 1, proposalVersion: 'buffer-allocunsafe-zeroed-v1', node: process.version,
  installed: false, productionManifestChanged: false, sources,
  nodeEmbeddedSourceSha256: Object.fromEntries(['buffer', 'internal/buffer', 'internal/validators'].map(name => [name, hash(process.binding('natives')[name])])),
  differentialGroups: oracle.length, cases: oracle, candidateCases: profile, callerDemand: actualDemand,
  demandSource: { path, sha256: hash(source), excerpts: Object.fromEntries(Object.entries(demand.excerpts).map(([name, text]) => [name, { text, sha256: hash(text) }])),
    injectedModuleSha256: hash(demand.text), slowAllocationDemand: false },
  referencePoolMetadata: { nodePoolSize: Buffer.poolSize, nodeMaximum: constants.MAX_LENGTH,
    small: { length: pooled.length, byteOffset: pooled.byteOffset, backingBytes: pooled.buffer.byteLength },
    positiveFractionToZero: { length: fractional.length, byteOffset: fractional.byteOffset, backingBytes: fractional.buffer.byteLength },
    candidate: { length: bounded.length, byteOffset: bounded.byteOffset, backingBytes: bounded.buffer.byteLength } },
  scope: 'Node22 reference versus isolated zeroed captured-alloc candidate and exact readable-stream demand excerpts. No initial Node contents inspected, no genuine OOM injected, no production registration or guest component proof yet.' };
await writeFile(new URL('node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ differentialGroups: oracle.length, candidateGroups: profile.length, callerDemand: true, restored: Buffer.allocUnsafe === original, installed: false }));
