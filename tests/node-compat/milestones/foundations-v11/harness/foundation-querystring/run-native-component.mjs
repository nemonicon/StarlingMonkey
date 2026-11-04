// Requires an actual Querystring-enabled ordinary Release entropy-OFF engine.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { nativeHarness, hash } from '../foundations/native-scalar-harness.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const h = await nativeHarness({ kind: 'querystring', here, enabledField: 'querystringEnabled', option: 'NODE_COMPAT_QUERYSTRING', outputVariable: 'NODE_COMPAT_QUERYSTRING_OUTPUT' });
const oracle = JSON.parse(await readFile(join(here, 'native-node-results.json')));
h.verifyOracleSources(oracle, ['querystring.mjs', 'querystring-factories.generated.h', 'export-manifest.querystring.node-v22.14.0.json']);
assert.equal(hash(await readFile(join(here, 'checks.mjs'))), oracle.checksSha256);
const input = join(here, 'native-component.mjs'), bundle = await h.bundle(input, ['node:buffer', 'node:querystring']);
assert.doesNotMatch(bundle.code, /function qsEscape\(/, 'Facade must come from installed native factory');
const fixture = await h.build('native_querystring', bundle.code);
function validate(observed, count) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure)); assert.equal(observed.calls, count);
  assert.equal(observed.snapshotByte, 65+count); assert.equal(observed.snapshotValues, 2+count);
  assert.equal(observed.snapshotIdentity, true); assert.equal(observed.namespaceIdentity, true);
  assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.profile, oracle.sourceProfile);
  assert.deepEqual(observed.aliases, { names: oracle.cases[0].result.names,
    canonicalNamespaceStable: true, bareCache: true, sharedValues: true, moduleTag: '[object Module]',
    nullNamespacePrototype: true, thenType: 'undefined', sharedMutation: true, privateBuffer: true });
  assert.deepEqual(observed.commonJS, { type: 'object', same: true, encodeAlias: true, decodeAlias: true,
    nullParsePrototype: true, defaultProperty: 'undefined', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  return observed;
}
const instance = await h.importFixture(fixture), calls = [validate(JSON.parse(await instance.run()), 1), validate(JSON.parse(await instance.run()), 2)];
const wasmtime = h.runHost(fixture); validate(wasmtime.observed, 1);
const initialization = [];
for (const [name, expression, specifier = 'node:querystring', code = /ERR_SM_NODE_UNSUPPORTED/] of [
  ['unsupported-call', 'q.unescapeBuffer(3)'], ['unsupported-new', 'new q.unescapeBuffer(3)'],
  ['nonstring-fallback', 'q.unescape(Symbol("x"))'], ['bare-call', 'q.unescapeBuffer(3)', 'querystring'],
  ['input-cap', 'q.parse("x".repeat(1048577))', 'node:querystring', /ERR_SM_NODE_LIMIT/],
  ['awaited-deferred', 'await Promise.resolve().then(()=>q.unescapeBuffer(3))'],
  ['detached-deferred', 'Promise.resolve().then(()=>q.unescapeBuffer(3))'],
]) initialization.push(await h.expectInitialization(name, `import * as q from ${JSON.stringify(specifier)}; ${expression}; export function run(){return '';}`, code));
const cjs = join(h.output, 'init-require.cjs'), entry = join(h.output, 'init-require-entry.mjs');
await writeFile(cjs, "new (require('querystring').unescapeBuffer)(3); module.exports = {};\n");
await writeFile(entry, `import ${JSON.stringify(cjs)}; export function run(){return '';}`);
const lowered = await h.bundle(entry, ['node:querystring']); initialization.push(await h.expectInitialization('commonjs-deferred', lowered.code));
const offAdmission = await h.offAdmission('NODE_COMPAT_QUERYSTRING_OFF_ENGINE', 'NODE_COMPAT_QUERYSTRING_OFF_SOURCE_ROOT', input);
const sourceFiles = await Promise.all(['native-component.mjs', 'native-require.cjs', 'run-native-component.mjs', 'checks.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) })));
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, profileVersion: oracle.profileVersion,
  installedBuiltin: true, ...h.evidence, fixture, bundle: { imports: bundle.imports, moduleIds: bundle.moduleIds },
  differentialGroups: oracle.differentialGroups, customSeparatorVectors: 210, byteFallbackVectors: 1536, profileCasesPerCall: oracle.sourceProfile.length,
  calls, wasmtime, initialization, offAdmission, sourceFiles,
  limitations: ['Partial bounded Querystring; nonstring unescapeBuffer overloads remain explicit deferred operations',
    'Profile limits and bounded core Buffer allocation/pooling/encoding restrictions remain',
    'Alias namespace objects may differ while all values/default state are shared',
    'Static selected CommonJS lowering only; no runtime require or builtin export synchronization',
    'Scalar host proof only; standard HTTP target hosts and empirical performance/size comparisons are separate gates'] };
await h.writeReport(report);
console.log(JSON.stringify({ output: h.output, groups: oracle.differentialGroups, delimiterVectors: 210, byteVectors: 1536,
  profileCases: oracle.sourceProfile.length, componentCalls: 3, initializationFailures: initialization.length, offAdmission: !!offAdmission, imports: [] }));
