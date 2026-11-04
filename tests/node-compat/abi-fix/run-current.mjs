// Regression for scalar WIT u32 results. The u32 tests use WIT u32 throughout;
// no signed result carrier or host-side bit reinterpretation is permitted.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import * as oracle from './component.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_ABI_OUTPUT ?? '/tmp/starling-node-compat/abi-current-regression');
const controlOnly = process.env.NODE_COMPAT_ABI_CONTROL_ONLY === '1';
const fixedEngine = process.env.NODE_COMPAT_ENGINE && resolve(process.env.NODE_COMPAT_ENGINE);
assert(controlOnly || fixedEngine, 'Set NODE_COMPAT_ENGINE to the ABI-fixed embedding engine');
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME ?? '/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const toolchainContext = await loadToolchain();
const { directory: toolchain, require } = toolchainContext;
const packageDirectory = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
const { componentize, splicer, provenance: componentizer } = await loadComponentizer(toolchainContext,{legacyDiagnostic:true});
const { transpile, componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const source = await readFile(join(here, 'component.mjs'), 'utf8');
const wit = await readFile(join(here, 'profile.wit'), 'utf8');
const patchPath = join(here, 'componentize-u32-result.patch');
const patchSha256 = hash(await readFile(patchPath));
const releasedEngine = join(packageDirectory, 'lib/starlingmonkey_embedding.wasm');
assert.equal(hash(await readFile(releasedEngine)), '6094cd93d966f9bec9b01332db6e0eedbaf22f60b745c9f823f21e33cbd4d365');
const version = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }

const emitted = splicer.spliceBindings(await readFile(releasedEngine), [], wit, undefined, 'profile', false);
await writeFile(join(output, 'emitted-bindings.js'), emitted.jsBindings);
assert.match(emitted.jsBindings, /function toUint32\(val\)[\s\S]*?return val >>> 0/);
assert.match(emitted.jsBindings, /async function export_directU32[\s\S]*?return toUint32\(ret\)/);
assert.match(emitted.jsBindings, /setInt32\([^\n]*toUint32/);
const bindingsEvidence = {
  sha256: hash(emitted.jsBindings),
  path: join(output, 'emitted-bindings.js'),
  excerpts: emitted.jsBindings.split('\n').filter(line => /function toUint32|return val >>> 0|export_directU32|return toUint32\(ret\)|setInt32.*toUint32/.test(line)),
  signatures: emitted.exports,
};
const boundaries = [0, 1, 0x7fffffff, 0x80000000, 0x80000001, 2342402100, 0xfffffffe, 0xffffffff];
let state = 0x41424932;
const generated = Array.from({ length: 128 }, () => {
  state ^= state << 13; state ^= state >>> 17; state ^= state << 5;
  return state >>> 0;
});
const unsignedValues = [...boundaries, ...generated];
const signedValues = [-2147483648, -123456789, -1, 0, 1, 123456789, 2147483647];
const floatValues = [-Infinity, -123.5, -0, 0, 1, 2147483648, 4294967295, Math.PI, Infinity, NaN];
function representation(value) {
  if (typeof value === 'number') return Number.isNaN(value) ? 'NaN' : Object.is(value, -0) ? '-0' : String(value);
  if (ArrayBuffer.isView(value)) return Array.from(value);
  if (Array.isArray(value)) return value.map(representation);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, representation(item)]));
  return value;
}
function normalized(value) {
  if (ArrayBuffer.isView(value)) return [...value];
  if (Array.isArray(value)) return value.map(normalized);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, normalized(item)]));
  return value;
}
const variants = [];
for (const [name, engine, mustPass] of [
  ['released-broken-control', releasedEngine, false],
  ...(!controlOnly ? [['fixed', fixedEngine, true]] : []),
]) {
  let metadata;
  if (mustPass) {
    metadata = JSON.parse(await readFile(engine + '.build.json'));
    assert.equal(metadata.engineSha256, hash(await readFile(engine)));
    assert.equal(metadata.abiFixEnabled, true);
    assert(metadata.componentizeJsPatches.some(patch => patch.applied && patch.sha256 === patchSha256));
    const embedding = metadata.componentizeSourceManifest.find(entry => entry.path === 'embedding/embedding.cpp');
    assert.equal(embedding.sha256, metadata.bigIntFixEnabled ? '5893c8989d317d3aee95faea3048ad8665b7273c74f33e85e244d13c34c6b00b' : 'b1ec3c77059aeeb793610eed31e802a5a9b6fcdd08e96ce3a2e62dbec18ea51e');
  }
  const { component, legacyEngineDiagnosticAudit } = await componentize(source, { engine, witWorld: wit, worldName: 'profile',
    disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
  const componentPath = join(output, name + '.component.wasm');
  await writeFile(componentPath, component);
  const emittedWit = await componentWit(component);
  assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
  const { files } = await transpile(component, { name });
  for (const [filename, bytes] of Object.entries(files)) {
    const path = join(output, filename); await mkdir(dirname(path), { recursive: true }); await writeFile(path, bytes);
  }
  const guest = await import(pathToFileURL(join(output, name + '.js')));
  const checks = [];
  function check(group, operation, input, observed, expected) {
    let matches = true;
    try { assert.deepEqual(normalized(observed), normalized(expected)); } catch { matches = false; }
    checks.push({ group, operation, input: representation(input), observed: representation(observed), expected: representation(expected), matches });
    if (mustPass || group !== 'scalar-u32') assert(matches, `${name} ${operation}(${input}): got ${observed}, expected ${expected}`);
  }
  for (const value of unsignedValues) {
    check('scalar-u32', 'directU32', value, guest.directU32(value), oracle.directU32(value));
    check('scalar-u32', 'computedU32', value, guest.computedU32(value), oracle.computedU32(value));
  }
  check('scalar-u32', 'constantHigh', [], guest.constantHigh(), oracle.constantHigh());
  check('scalar-u32', 'constantMax', [], guest.constantMax(), oracle.constantMax());
  for (const value of signedValues) {
    check('s32-control', 'directS32', value, guest.directS32(value), oracle.directS32(value));
    check('s32-control', 'computedS32', value, guest.computedS32(value), oracle.computedS32(value));
  }
  check('s32-control', 'constantNegative', [], guest.constantNegative(), oracle.constantNegative());
  for (const value of floatValues) {
    check('float-control', 'directF32', value, guest.directF32(value), Math.fround(value));
    check('float-control', 'directF64', value, guest.directF64(value), value);
  }
  for (const values of [[], boundaries, generated]) {
    check('list-control', 'listU32', values, guest.listU32(new Uint32Array(values)), new Uint32Array(values));
  }
  for (const [first, last, signed] of [[0x80000000, 0xffffffff, -2147483648], [0xffffffff, 0x80000000, -1], [0, 1, 2147483647]]) {
    const value = { first, last, signed, values: new Uint32Array(boundaries) };
    check('record-control', 'recordU32', value, guest.recordU32(value), value);
  }
  for (const value of boundaries) {
    check('result-control', 'resultU32-ok', value, guest.resultU32(true, value), value);
    let thrown;
    try { guest.resultU32(false, value); } catch (error) { thrown = error.payload; }
    check('result-control', 'resultU32-err', value, thrown, value);
    check('internal-control', 'describe', value, JSON.parse(guest.describe(value)), JSON.parse(oracle.describe(value)));
  }
  const invokeCases = mustPass ? [
    ...boundaries.map(value => [`direct-u32(${value})`, value]),
    ['constant-high()', 0x80000000], ['constant-max()', 0xffffffff],
    ['computed-u32(0)', 0x80000000], ['computed-u32(2147483647)', 0xffffffff],
    ['direct-s32(-2147483648)', -2147483648], ['constant-negative()', -2147483648],
    ['direct-f32(2147483648)', 2147483648], ['direct-f64(4294967295)', 4294967295],
  ] : [['direct-u32(2147483648)', 0x80000000], ['constant-max()', 0xffffffff], ['direct-s32(-2147483648)', -2147483648]];
  const wasmtimeChecks = [];
  for (const [call, expected] of invokeCases) {
    const result = spawnSync(wasmtime, ['run', '--invoke', call, componentPath], { encoding: 'utf8', timeout: 120000 });
    assert.equal(result.status, 0, result.error?.message || result.stderr);
    const observed = Number(result.stdout.trim());
    // WAVE prints the shortest decimal that round-trips to f32, not an exact f64 decimal.
    const canonicalObserved = call.startsWith('direct-f32(') ? Math.fround(observed) : observed;
    const matches = canonicalObserved === expected;
    if (mustPass || call.startsWith('direct-s32')) assert(matches, `${name} Wasmtime ${call}: ${observed} != ${expected}`);
    wasmtimeChecks.push({ call, expected, observed, canonicalObserved, matches });
  }
  const wasmtimeIndirectChecks = [];
  for (const [call, expectedWave] of [
    ['list-u32([0,2147483648,4294967295])', '[0,2147483648,4294967295]'],
    ['record-u32({first:2147483648,last:4294967295,signed:-2147483648,values:[2147483648,4294967295]})', '{first:2147483648,last:4294967295,signed:-2147483648,values:[2147483648,4294967295]}'],
    ['result-u32(true,4294967295)', 'ok(4294967295)'],
    ['result-u32(false,4294967295)', 'err(4294967295)'],
  ]) {
    const result = spawnSync(wasmtime, ['run', '--invoke', call, componentPath], { encoding: 'utf8', timeout: 120000 });
    assert.equal(result.status, 0, result.error?.message || result.stderr);
    const observedWave = result.stdout.trim().replace(/\s/g, '');
    assert.equal(observedWave, expectedWave, `${name} Wasmtime indirect ${call}`);
    wasmtimeIndirectChecks.push({ call, expectedWave, observedWave, matches: true });
  }
  if (!mustPass) {
    assert(checks.some(check => check.group === 'scalar-u32' && !check.matches), 'Released control must reproduce the defect');
    assert(wasmtimeChecks.some(check => !check.matches), 'Wasmtime must also reproduce the released defect');
  }
  variants.push({ name, engine, legacyEngineDiagnosticAudit:legacyEngineDiagnosticAudit??null, engineSha256: hash(await readFile(engine)), metadata,
    componentPath, componentBytes: component.length, componentSha256: hash(component), emittedImports: [], emittedWit,
    checkCount: checks.length, passed: checks.filter(check => check.matches).length,
    failures: checks.filter(check => !check.matches),
    boundaryObservations: checks.filter(check => check.group === 'scalar-u32' && (boundaries.includes(Number(check.input)) || check.operation.startsWith('constant'))),
    groupCounts: Object.fromEntries([...new Set(checks.map(check => check.group))].map(group => [group, checks.filter(check => check.group === group).length])),
    wasmtimeChecks, wasmtimeIndirectChecks,
  });
}
const report = {
  schema: 1, node: process.version, componentizeJsRevision: '4d812f5a7b524cea5bcfd565cac55f3fab876a57',
  componentizer, wasmtime: version.stdout.trim(), sourceSha256: hash(source), world: wit, patchPath, patchSha256,
  bindingsEvidence, unsignedBoundaryValues: boundaries, generatedSeed: '0x41424932', generatedValues: generated.length,
  variants, complete: !controlOnly,
  scope: 'Scalar exported CoreVal::I32 results: numeric conversion reads boxed Double values correctly and preserves signed bits. This fixture isolates exported results; the separately versioned packaging splicer is recorded above.',
  limitations: ['Imported callback arguments are covered by import-v1.mjs and raw-i32-reader.mjs, rather than this export-focused fixture.', 'Lists, records and results use indirect memory returns and serve as regression controls; this is not a complete Component Model ABI audit.', 'No signed carrier is used by any WIT u32 regression API.'],
};
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
if (!controlOnly) await writeFile(join(here, 'results.current.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ complete: report.complete, variants: variants.map(({ name, checkCount, passed, failures }) => ({ name, checkCount, passed, failureCount: failures.length })), output }, null, 2));
