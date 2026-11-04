// Small valid-API reference experiments only. No runtime/builtin source edits.
import assert from 'node:assert/strict';
import * as consumers from 'node:stream/consumers';
import { readFile, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const directory = join(toolchain, 'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream');
const hash = value => createHash('sha256').update(value).digest('hex');
const scheduler = join(directory, 'scheduler.js'), candidateConsumers = join(directory, 'consumers.js');
const traces = [];
for (const boundary of ['task', 'microtask']) for (const mode of ['node', 'jco-scheduler']) {
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('scheduler-probe.cjs', import.meta.url)), mode, boundary, scheduler], { encoding: 'utf8', timeout: 10000 });
  assert.equal(result.status, 0, result.stderr); traces.push(JSON.parse(result.stdout));
}
const candidate = await import(pathToFileURL(candidateConsumers));
async function* mutableChunks() { const bytes = new Uint8Array([65]); yield bytes; bytes[0] = 66; yield bytes; bytes[0] = 67; }
const nodeBytes = [...new Uint8Array(await consumers.arrayBuffer(mutableChunks()))];
const jcoBytes = [...new Uint8Array(await candidate.arrayBuffer(mutableChunks()))];
assert.deepEqual(nodeBytes, [67, 67]); assert.deepEqual(jcoBytes, [65, 66]);
const report = { schema: 1, node: process.version, schedulerTraces: traces,
  mutableChunkCollection: { nodeBytes, jcoBytes, matches: false,
    explanation: 'Pinned Node collects Blob parts by reference until Blob construction; Jco collectParts/toArrayBuffer copies each byte chunk during consumption.' },
  sources: Object.fromEntries(await Promise.all([['jcoScheduler', scheduler], ['jcoConsumers', candidateConsumers],
    ['jcoShared', join(directory, 'shared.js')], ['probe', fileURLToPath(new URL('scheduler-probe.cjs', import.meta.url))],
    ['runner', fileURLToPath(import.meta.url)]].map(async ([name, path]) => [name, { path, sha256: hash(await readFile(path)) }]))),
  scope: 'Pinned Node host evidence versus the exact standalone installed scheduler/consumer source. This is not a bundled Jco graph, StarlingMonkey component, or Node stream compatibility test.' };
await writeFile(new URL('reference-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ schedulerTraces: traces, nodeBytes, jcoBytes }));
