// Exact-release oracle for the shared bounded UTF-8 codec cases.
import assert from 'node:assert/strict';
import { Buffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runCodecCases } from './codec-cases.mjs';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Use the pinned Node release without feature flags');
const sourcePath = fileURLToPath(import.meta.url), here = dirname(sourcePath);
const result = runCodecCases({ TextEncoder, Buffer });
assert.equal(result.caseCount, 8);
assert.equal(result.unicodeVectorCount, 14);
assert(result.cases.every(item => item.passed));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const report = {
  schemaVersion: 1, verifiedAtUtc: new Date().toISOString(),
  node: process.version, versions: process.versions,
  executable: process.execPath, executableSha256: hash(await readFile(process.execPath)),
  execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
  sharedCasesSha256: hash(await readFile(join(here, 'codec-cases.mjs'))),
  runnerSha256: hash(await readFile(sourcePath)),
  injectedImplementations: { TextEncoder: 'actual Node global', Buffer: 'actual node:buffer', gc: 'not injected' },
  ...result,
};
await writeFile(join(here, 'node-oracle-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ node: report.node, caseCount: report.caseCount,
  assertionCount: report.assertionCount, observationCount: report.observationCount,
  unicodeVectorCount: report.unicodeVectorCount, bufferChecked: true, passed: true }, null, 2));
