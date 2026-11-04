// Focused policy/receipt tests and actual Jco component-WIT audits. The tiny
// components have empty instance types: this checks names/versions, not WASI
// function signatures, host instantiation or any production entropy engine.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from './toolchain.mjs';
import { loadComponentizer } from './componentizer.mjs';
import { selectedInterfacePolicy, auditSelectedInterfaces, SECURE_RANDOM_INTERFACE as RANDOM,
  ENTROPY_ENTRY_PATCH_SHA256, WASI_CATALOGUE_SHA256 } from './capability-policy.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_CAPABILITY_OUTPUT ?? '/tmp/starling-node-compat/capability-policy');
const toolchain = await loadToolchain();
const { parse } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadata = policy => ({ profileEnabled: true, entropyPolicy: policy,
  observedCMakeOptions: { ENABLE_BUILTIN_NODE_COMPAT: 'ON', NODE_COMPAT_ENTROPY_MODE: policy === 'off' ? 'OFF' : 'RUNTIME_ONLY' },
  entropyEntryPatchApplied: true,
  componentizeJsPatches: [{ name: 'node-compat-runtime-entry-v1', sha256: ENTROPY_ENTRY_PATCH_SHA256, applied: true }] });
const options = policy => ({ disableFeatures: ['stdio', 'clocks', 'http', 'fetch-event', ...(policy === 'off' ? ['random'] : [])],
  selectedInterfaces: policy === 'off' ? [] : [RANDOM] });
const records = [];
async function check(name, callback) {
  try { const detail = await callback(); records.push({ name, status: 'pass', ...(detail ?? {}) }); }
  catch (error) { records.push({ name, status: 'fail', error: error.stack ?? String(error) }); }
}
async function denies(callback, code = 'ERR_SM_NODE_CAPABILITY_SELECTION') {
  let failure;
  try { await callback(); } catch (error) { failure = error; }
  assert(failure, 'Malformed selection unexpectedly succeeded');
  if (code) assert.equal(failure.code, code, failure.stack);
  return { rejectedCode: failure.code ?? null, error: failure.message };
}
for (const policy of ['off', 'runtime-only']) await check(`valid-${policy}`, () => {
  const selection = selectedInterfacePolicy(metadata(policy), options(policy));
  assert.equal(selection.entropyPolicy, policy); assert(Object.isFrozen(selection)); assert(Object.isFrozen(selection.selectedInterfaces));
  assert.equal(selection.catalogueSha256, WASI_CATALOGUE_SHA256);
});
await check('historical-no-modern-fields-no-selection', () => assert.equal(selectedInterfacePolicy({}, {}), null));
await check('historical-explicit-selection', () => assert.equal(selectedInterfacePolicy({}, { selectedInterfaces: [] }).entropyPolicy, 'historical-unspecified'));
await check('selected-copy-independent-of-caller-mutation', () => {
  const opts = options('runtime-only'); const policy = selectedInterfacePolicy(metadata('runtime-only'), opts);
  opts.selectedInterfaces.push('wasi:cli/environment@0.2.10'); assert.deepEqual(policy.selectedInterfaces, [RANDOM]);
});
const cases = [
  ['missing-selected', s => delete s.options.selectedInterfaces],
  ['selected-string', s => { s.options.selectedInterfaces = RANDOM; }],
  ['selected-object', s => { s.options.selectedInterfaces = {}; }],
  ['selected-non-string', s => { s.options.selectedInterfaces = [7]; }],
  ['duplicate-selected', s => { s.options.selectedInterfaces = [RANDOM, RANDOM]; }],
  ['wrong-version', s => { s.options.selectedInterfaces = ['wasi:random/random@0.2.12']; }],
  ['unversioned', s => { s.options.selectedInterfaces = ['wasi:random/random']; }],
  ['wildcard', s => { s.options.selectedInterfaces = ['wasi:random/*']; }],
  ['custom-service', s => { s.options.selectedInterfaces = ['custom:host/entropy@1.0.0']; }],
  ['insecure-random', s => { s.options.selectedInterfaces = [RANDOM, 'wasi:random/insecure@0.2.10']; }],
  ['insecure-seed', s => { s.options.selectedInterfaces = [RANDOM, 'wasi:random/insecure-seed@0.2.10']; }],
  ['missing-entropy-policy-modern-mode', s => delete s.metadata.entropyPolicy],
  ['unknown-entropy-policy', s => { s.metadata.entropyPolicy = 'fallback'; }],
  ['missing-profile-flag', s => delete s.metadata.profileEnabled],
  ['profile-false', s => { s.metadata.profileEnabled = false; }],
  ['profile-string', s => { s.metadata.profileEnabled = 'true'; }],
  ['configured-profile-off', s => { s.metadata.observedCMakeOptions.ENABLE_BUILTIN_NODE_COMPAT = 'OFF'; }],
  ['configured-profile-missing', s => delete s.metadata.observedCMakeOptions.ENABLE_BUILTIN_NODE_COMPAT],
  ['wrong-configured-entropy', s => { s.metadata.observedCMakeOptions.NODE_COMPAT_ENTROPY_MODE = 'OFF'; }],
  ['missing-configured-entropy', s => delete s.metadata.observedCMakeOptions.NODE_COMPAT_ENTROPY_MODE],
  ['observed-options-array', s => { s.metadata.observedCMakeOptions = []; }],
  ['entry-patch-flag-missing', s => delete s.metadata.entropyEntryPatchApplied],
  ['entry-patch-flag-false', s => { s.metadata.entropyEntryPatchApplied = false; }],
  ['entry-patch-flag-string-false', s => { s.metadata.entropyEntryPatchApplied = 'false'; }],
  ['entry-patch-receipt-missing', s => { s.metadata.componentizeJsPatches = []; }],
  ['entry-patch-receipts-object', s => { s.metadata.componentizeJsPatches = {}; }],
  ['entry-patch-receipts-invalid-member', s => { s.metadata.componentizeJsPatches = [null]; }],
  ['entry-patch-receipt-duplicate', s => { s.metadata.componentizeJsPatches.push({ ...s.metadata.componentizeJsPatches[0] }); }],
  ['entry-patch-applied-false', s => { s.metadata.componentizeJsPatches[0].applied = false; }],
  ['entry-patch-applied-string-false', s => { s.metadata.componentizeJsPatches[0].applied = 'false'; }],
  ['entry-patch-wrong-hash', s => { s.metadata.componentizeJsPatches[0].sha256 = '0'.repeat(64); }],
  ['runtime-random-disabled', s => { s.options.disableFeatures.push('random'); }],
  ['runtime-random-not-selected', s => { s.options.selectedInterfaces = []; }],
  ['disabled-string', s => { s.options.disableFeatures = 'random'; }],
  ['disabled-non-string', s => { s.options.disableFeatures.push(1); }],
  ['disabled-duplicate', s => { s.options.disableFeatures.push('stdio'); }],
  ['disabled-unknown', s => { s.options.disableFeatures.push('imaginary'); }],
  ['enabled-override', s => { s.options.enableFeatures = ['random']; }],
  ['enabled-object', s => { s.options.enableFeatures = {}; }],
  ['enabled-non-string', s => { s.options.enableFeatures = [1]; }],
  ['enabled-duplicate', s => { s.options.enableFeatures = ['http', 'http']; }],
];
for (const [name, mutate] of cases) await check(name, async () => {
  const state = { metadata: metadata('runtime-only'), options: options('runtime-only') }; mutate(state);
  return denies(() => selectedInterfacePolicy(state.metadata, state.options));
});
for (const [name, meta, opts] of [
  ['off-random-feature-retained', metadata('off'), { ...options('off'), disableFeatures: [] }],
  ['off-random-selected', metadata('off'), { ...options('off'), selectedInterfaces: [RANDOM] }],
  ['malformed-metadata-null', null, {}],
  ['malformed-metadata-array', [], {}],
  ['malformed-options-null', metadata('off'), null],
  ['modern-entry-flag-no-policy', { entropyEntryPatchApplied: false }, {}],
  ['modern-entry-receipt-no-policy', { componentizeJsPatches: [{ name: 'node-compat-runtime-entry-v1' }] }, {}],
]) await check(name, () => denies(() => selectedInterfacePolicy(meta, opts)));
const component = async imports => parse(`(component (type $i (instance)) ${imports.map(id => `(import ${JSON.stringify(id)} (instance (type $i)))`).join(' ')})`);
const empty = await component([]);
const off = selectedInterfacePolicy(metadata('off'), options('off'));
const runtime = selectedInterfacePolicy(metadata('runtime-only'), options('runtime-only'));
await check('audit-off-empty-component', async () => {
  const result = await auditSelectedInterfaces(toolchain, empty, off); assert.deepEqual(result.emittedImports, []); assert.equal(result.componentSha256, hash(empty));
});
await check('audit-runtime-standard-component', async () => {
  const bytes = await component([RANDOM]); const result = await auditSelectedInterfaces(toolchain, bytes, runtime); assert.deepEqual(result.emittedImports, [RANDOM]);
});
await check('audit-unused-selected-capability-recorded', async () => {
  const policy = selectedInterfacePolicy(metadata('off'), { ...options('off'), selectedInterfaces: ['wasi:cli/environment@0.2.10'] });
  assert.deepEqual((await auditSelectedInterfaces(toolchain, empty, policy)).unusedSelectedInterfaces, ['wasi:cli/environment@0.2.10']);
});
for (const [name, imports, policy] of [
  ['audit-off-emits-random', [RANDOM], off],
  ['audit-runtime-missing-random', [], runtime],
  ['audit-unselected-standard', ['wasi:cli/environment@0.2.10'], off],
  ['audit-wrong-random-version', ['wasi:random/random@0.2.12'], runtime],
  ['audit-unversioned-random', ['wasi:random/random'], runtime],
  ['audit-insecure-random', [RANDOM, 'wasi:random/insecure@0.2.10'], runtime],
  ['audit-custom-import', ['custom:host/entropy@1.0.0'], off],
]) await check(name, async () => denies(() => component(imports).then(bytes => auditSelectedInterfaces(toolchain, bytes, policy))));
for (const [name, policy] of [
  ['audit-malformed-policy-false', false],
  ['audit-malformed-policy-undefined', undefined],
  ['audit-malformed-policy-schema', { ...off, schemaVersion: 2 }],
  ['audit-malformed-policy-catalogue', { ...off, catalogueSha256: '0'.repeat(64) }],
  ['audit-malformed-policy-entropy', { ...off, entropyPolicy: 'unknown' }],
  ['audit-malformed-policy-selected-type', { ...off, selectedInterfaces: {} }],
  ['audit-malformed-policy-selected-duplicate', { ...off, selectedInterfaces: ['wasi:cli/environment@0.2.10', 'wasi:cli/environment@0.2.10'] }],
  ['audit-malformed-policy-off-selects-random', { ...off, selectedInterfaces: [RANDOM] }],
  ['audit-malformed-policy-runtime-missing-selection', { ...runtime, selectedInterfaces: [] }],
]) await check(name, () => denies(() => auditSelectedInterfaces(toolchain, empty, policy)));
await check('audit-component-must-be-bytes', () => denies(() => auditSelectedInterfaces(toolchain, '(component)', off)));
await check('audit-malformed-component-binary-rejected', () => denies(() => auditSelectedInterfaces(toolchain, new Uint8Array([1, 2, 3]), off), null));
await check('audit-explicit-null-historical-sentinel', async () => assert.equal(await auditSelectedInterfaces(toolchain, empty, null), null));
if (process.env.NODE_COMPAT_CAPABILITY_WRAPPER_ENGINE) {
  await check('wrapper-audits-finalizer-replacement', async () => {
    const engine = resolve(process.env.NODE_COMPAT_CAPABILITY_WRAPPER_ENGINE);
    const receipt = JSON.parse(await readFile(engine + '.build.json')); assert.equal(hash(await readFile(engine)), receipt.engineSha256);
    const selected = await loadComponentizer(toolchain); let finalized = false;
    const replacement = await component(['custom:host/entropy@1.0.0']);
    const result = await denies(() => selected.componentize('export function run(){return 0;}', {
      engine, witWorld: 'package test:capability-finalizer; world test { export run: func() -> s32; }', worldName: 'test',
      disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [],
      finalizeComponent: () => { finalized = true; return replacement; },
    }));
    assert(finalized, 'Finalizer must run before its emitted import is rejected');
    return { ...result, engineSha256: receipt.engineSha256, scope: 'Existing Release engine exercises packaging callback only; no new production entropy engine claim' };
  });
}
const failures = records.filter(record => record.status !== 'pass');
await mkdir(output, { recursive: true });
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, catalogueSha256: WASI_CATALOGUE_SHA256,
  policySha256: hash(await readFile(join(here, 'capability-policy.mjs'))), testSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  passed: records.length - failures.length, failed: failures.length, records,
  scope: 'Build policy/receipt validation and real minimal component WIT names/versions. Empty imported instance types do not establish WASI ABI conformance, native entropy behavior or host instantiation.' };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, passed: report.passed, failed: report.failed, failures }));
process.exitCode = failures.length ? 1 : 0;
