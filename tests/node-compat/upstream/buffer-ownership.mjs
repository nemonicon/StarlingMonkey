// Run the actual pinned export-buffers.js callbacks with a minimal Node assert
// adapter instead of installing Vitest into the production toolchain.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { context, output, upstream, hash, verifyUpstreamSource } from './common.mjs';

const ctx = await context();
const fixturePath = join(upstream, 'test/export-buffers.js');
const fixture = await readFile(fixturePath, 'utf8');
const fixtureArchive = await verifyUpstreamSource('test/export-buffers.js', ctx.metadata);
const hooks = [], tests = [], components = [];
// The test modules run in the host harness. These are assertion/test runner
// adapters, not APIs exposed to guest JavaScript.
globalThis.__upstreamBufferGate = {
  beforeAll: callback => hooks.push(callback),
  suite: (_name, callback) => callback(),
  test: (name, callback) => tests.push({ name, callback }),
  assert: {
    equal: assert.equal, notEqual: assert.notEqual, deepEqual: assert.deepEqual,
    isFunction: value => assert.equal(typeof value, 'function'),
    lengthOf: (value, size) => assert.equal(value.length, size),
    isBelow: (value, bound, message) => assert(value < bound, message),
  },
  componentize: async (source, options) => {
    const result = await ctx.componentize(source, { ...options, selectedInterfaces: [], engine: ctx.engine, preview2Adapter: ctx.preview2Adapter });
    const wit = await ctx.componentWit(result.component);
    assert.deepEqual(wit.split('\n').filter(line => /^\s*import /.test(line)), []);
    const componentPath = join(output, 'export-buffers.component.wasm');
    await writeFile(componentPath, result.component);
    components.push({ componentPath, componentSha256: hash(result.component), componentBytes: result.component.length, emittedImports: [] });
    return result;
  },
  transpile: ctx.transpile,
};
let adapted = fixture
  .replace("import { componentize } from '@bytecodealliance/componentize-js';", 'const { componentize } = globalThis.__upstreamBufferGate;')
  .replace("import { transpile } from '@bytecodealliance/jco';", 'const { transpile } = globalThis.__upstreamBufferGate;')
  .replace("import { assert, beforeAll, suite, test } from 'vitest';", 'const { assert, beforeAll, suite, test } = globalThis.__upstreamBufferGate;')
  .replace("import { DEBUG_TEST_ENABLED, WEVAL_TEST_ENABLED, maybeLogging } from './util.js';", 'const DEBUG_TEST_ENABLED = false, WEVAL_TEST_ENABLED = false; const maybeLogging = value => value;');
assert(!/from ['"](?:vitest|\.\/util\.js|@bytecodealliance)/.test(adapted), 'Unexpected upstream fixture import drift');
const adaptedPath = join(output, 'export-buffers.adapted.mjs');
await writeFile(adaptedPath, adapted);
const results = [];
try {
  await import(pathToFileURL(adaptedPath));
  for (const hook of hooks) await hook();
  for (const test of tests) {
    try { await test.callback(); results.push({ name: test.name, pass: true }); }
    catch (error) { results.push({ name: test.name, pass: false, error: error.stack }); }
  }
} finally { delete globalThis.__upstreamBufferGate; }
const report = { schema: 1, fixturePath, fixtureArchive, fixtureSha256: hash(fixture), adaptedSha256: hash(adapted),
  componentizerProvenance: ctx.componentizerProvenance,
  engineSha256: ctx.engineSha256, sourceRoot: ctx.sourceRoot,
  adaptation: 'Same upstream source, hooks and test callbacks; Node strict assertions replace the used Vitest assertion subset; explicit engine/adapter; no retries',
  snapshotMeaning: 'Upstream snapshot() is a runtime retained-list accessor; pre-initialization GC/snapshot tested separately by Starling E2E fixtures',
  components, results, passed: results.filter(result => result.pass).length, failed: results.filter(result => !result.pass).length };
await writeFile(join(output, 'buffer-ownership-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
assert.equal(report.failed, 0);
assert.equal(report.passed, 2);
