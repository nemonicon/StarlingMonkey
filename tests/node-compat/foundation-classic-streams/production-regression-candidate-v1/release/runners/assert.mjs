// Requires an actual Assert-enabled ordinary Release entropy-OFF engine.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { nativeHarness, hash } from '../helpers/native-scalar-harness.mjs';
const here = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../foundation-assert');
const h = await nativeHarness({ kind: 'assert', here, enabledField: 'assertEnabled', option: 'NODE_COMPAT_ASSERT', outputVariable: 'NODE_COMPAT_ASSERT_OUTPUT' });
const oracle = JSON.parse(await readFile(join(here, 'native-node-results.json')));
h.verifyOracleSources(oracle, ['assert.mjs', 'assert-strict.mjs', 'assert-factories.generated.h', 'export-manifest.assert.node-v22.14.0.json']);
assert.equal(hash(await readFile(join(here, 'checks.mjs'))), oracle.checksSha256);
const input = join(here, 'native-component.mjs'), bundle = await h.bundle(input, ['node:assert', 'node:assert/strict']);
assert.doesNotMatch(bundle.code, /function innerOk\(/, 'Facade must come from installed native factory');
const fixture = await h.build('native_assert', bundle.code);
function validate(observed, count) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure));
  assert.equal(observed.calls, count); assert.equal(observed.snapshotCount, count);
  assert.equal(observed.snapshotIdentity, true); assert.equal(observed.namespaceIdentity, true);
  assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.profile, oracle.sourceProfile);
  assert.deepEqual(observed.aliases, { names: oracle.cases[0].result, strictNames: oracle.cases[0].result,
    canonicalNamespaceStable: true, bareCache: true, rootValues: true, strictValues: true,
    moduleTag: '[object Module]', nullNamespacePrototype: true, thenType: 'undefined', sharedMutation: true });
  assert.deepEqual(observed.commonJS, { rootType: 'function', strictType: 'function', same: true, strictGraph: true,
    aliasOverrides: true, defaultProperty: 'undefined', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  return observed;
}
const instance = await h.importFixture(fixture), calls = [validate(JSON.parse(await instance.run()), 1), validate(JSON.parse(await instance.run()), 2)];
const wasmtime = h.runHost(fixture); validate(wasmtime.observed, 1);
const initialization = [];
for (const [name, expression, specifier = 'node:assert'] of [
  ['deep-call', 'a.deepStrictEqual({}, {})'], ['async-new', 'new a.rejects()'],
  ['calltracker-new', 'new a.CallTracker()'], ['strict-deep-call', 'a.deepEqual({}, {})', 'node:assert/strict'],
  ['bare-call', 'a.rejects()', 'assert'], ['bare-strict-new', 'new a.doesNotReject()', 'assert/strict'],
  ['awaited-deferred', 'await Promise.resolve().then(()=>a.deepEqual({}, {}))'],
  ['detached-deferred', 'Promise.resolve().then(()=>a.deepEqual({}, {}))'],
]) initialization.push(await h.expectInitialization(name, `import * as a from ${JSON.stringify(specifier)}; ${expression}; export function run(){return '';}`));
const cjs = join(h.output, 'init-require.cjs'), entry = join(h.output, 'init-require-entry.mjs');
await writeFile(cjs, "require('assert/strict').deepEqual({}, {}); module.exports = {};\n");
await writeFile(entry, `import ${JSON.stringify(cjs)}; export function run(){return '';}`);
const lowered = await h.bundle(entry, ['node:assert/strict']); initialization.push(await h.expectInitialization('commonjs-deferred', lowered.code));
const offAdmission = await h.offAdmission('NODE_COMPAT_ASSERT_OFF_ENGINE', 'NODE_COMPAT_ASSERT_OFF_SOURCE_ROOT', input);
const sourceFiles = await Promise.all(['native-component.mjs', 'native-require.cjs', 'run-native-component.mjs', 'checks.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) })));
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, profileVersion: oracle.profileVersion,
  installedBuiltin: true, ...h.evidence, fixture, bundle: { imports: bundle.imports, moduleIds: bundle.moduleIds },
  differentialGroups: oracle.differentialGroups, primitiveEqualityComparisons: 784, profileCasesPerCall: oracle.sourceProfile.length,
  calls, wasmtime, initialization, offAdmission, sourceFiles,
  limitations: ['Partial synchronous Assert; deep comparisons, async helpers and CallTracker remain deferred',
    'Diagnostic formatting/native stacks/cross-realm error detection remain bounded as the manifest specifies',
    'Alias namespaces may differ by specifier while all exported values/default state are shared',
    'Static selected CommonJS lowering only; no runtime require or builtin export synchronization',
    'Scalar host proof only; standard HTTP host integration and performance measurements are separate gates'] };
await h.writeReport(report);
console.log(JSON.stringify({ output: h.output, groups: oracle.differentialGroups, primitiveComparisons: 784, profileCases: oracle.sourceProfile.length,
  componentCalls: 3, initializationFailures: initialization.length, offAdmission: !!offAdmission, imports: [] }));
