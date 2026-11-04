// Isolated static-field patch fixture only. Production allocUnsafe stays deferred.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { nativeHarness, hash } from '../foundations/native-scalar-harness.mjs';
import { loadToolchain } from '../toolchain.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
import { bufferListDemandModule } from './demand-source.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const h = await nativeHarness({ kind: 'alloc-unsafe-proposal', here, enabledField: 'profileEnabled', option: 'ENABLE_BUILTIN_NODE_COMPAT', outputVariable: 'NODE_COMPAT_ALLOC_UNSAFE_OUTPUT' });
const oracle = JSON.parse(await readFile(join(here, 'node-results.json'))), toolchain = await loadToolchain();
for (const [name, expected] of Object.entries(oracle.sources)) assert.equal(hash(await readFile(join(here, name))), expected, name);
const demandSource = await readFile(oracle.demandSource.path, 'utf8'); assert.equal(hash(demandSource), oracle.demandSource.sha256);
const demand = bufferListDemandModule(demandSource); assert.equal(hash(demand.text), oracle.demandSource.injectedModuleSha256);
const bundle = await bundleProfile({ ...toolchain, builtinManifests: h.builtinManifests, input: join(here, 'component.mjs'),
  virtualModules: { 'node-compat:buffer-list-demand': demand.text } });
assert.deepEqual(bundle.imports, ['node:buffer']);
assert(bundle.moduleIds.every(id => !id.includes('/builtins/node-compat/') && !id.includes('/node_modules/buffer/')));
const fixture = await h.build('isolated_alloc_unsafe', bundle.code);
function validate(observed, count) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure));
  assert.equal(observed.calls, count); assert.equal(observed.snapshotByte, 17+count);
  assert.equal(observed.snapshotIdentity, true); assert.equal(observed.namespaceIdentity, true); assert.equal(observed.aliases, true);
  assert.equal(observed.installed, false);
  const baseline = { methods: 91, allocUnsafe: 'ERR_SM_NODE_UNSUPPORTED', allocUnsafeSlow: 'ERR_SM_NODE_UNSUPPORTED' };
  assert.deepEqual(observed.before, baseline); assert.deepEqual(observed.after, baseline);
  assert.deepEqual(observed.patch, { canonical: true, bare: true, defaultAlias: true, global: true, commonJS: true,
    writable: true, enumerable: true, configurable: true });
  assert.deepEqual(observed.restore, { sameFunction: true, writable: true, enumerable: true, configurable: true, commonJS: true });
  assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.profile, oracle.candidateCases); assert.deepEqual(observed.demand, oracle.callerDemand);
  return observed;
}
const instance = await h.importFixture(fixture), calls = [validate(JSON.parse(await instance.run()), 1), validate(JSON.parse(await instance.run()), 2)];
const wasmtime = h.runHost(fixture); validate(wasmtime.observed, 1);
const initialization = [];
for (const [name, expression] of [['baseline-call', 'Buffer.allocUnsafe(1)'], ['baseline-new', 'new Buffer.allocUnsafe(1)']])
  initialization.push(await h.expectInitialization(name, `import {Buffer} from 'node:buffer'; ${expression}; export function run(){return '';}`,
    /node:buffer\.Buffer\.allocUnsafe is unavailable in sm-node-22\.14\.0-m0\.1/));
for (const [name, expression, expected] of [
  ['candidate-type', "a('2')", /ERR_INVALID_ARG_TYPE/], ['candidate-cap', 'a(16777217)', /ERR_OUT_OF_RANGE/],
  ['candidate-unawaited-microtask', 'Promise.resolve().then(()=>a(-1))', /ERR_OUT_OF_RANGE/],
]) {
  const input = join(h.output, name+'.mjs');
  await writeFile(input, `import {Buffer} from 'node:buffer'; import {createAllocUnsafeCandidate} from ${JSON.stringify(join(here, 'candidate.mjs'))}; const a=createAllocUnsafeCandidate(Buffer); ${expression}; export function run(){return '';}`);
  const lowered = await bundleProfile({ ...toolchain, builtinManifests: h.builtinManifests, input });
  initialization.push(await h.expectInitialization(name, lowered.code, expected));
}
const sourceFiles = await Promise.all(['candidate.mjs', 'checks.mjs', 'component.mjs', 'static-require.cjs', 'demand-source.mjs', 'demand-checks.mjs', 'run-component.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) })));
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, proposalVersion: oracle.proposalVersion,
  installedBuiltin: false, productionManifestChanged: false, ...h.evidence, fixture,
  bundle: { imports: bundle.imports, moduleIds: bundle.moduleIds }, differentialGroups: oracle.differentialGroups,
  candidateGroups: oracle.candidateCases.length, callerDemand: oracle.demandSource, calls, wasmtime, initialization, sourceFiles,
  limitations: ['Isolated wrapper and scoped static-field patch with finally restoration; production core remains unchanged',
    'Fresh zeroed no-pool storage deliberately differs from Node slab/backing/uninitialized-content behavior',
    'Raw requested sizes above16MiB rejected; detailed messages differ',
    'Mocked allocator exception identity is not a genuine OOM/allocator-fault test',
    'Only actual concat/_getBuffer excerpts exercised; classic stream, abort listener and scheduler support remain deferred',
    'No component size or performance benefit claimed'] };
await writeFile(join(h.output, 'results.json'), JSON.stringify(report, null, 2)+'\n');
await writeFile(join(here, 'component-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ output: h.output, groups: oracle.differentialGroups, candidateGroups: oracle.candidateCases.length,
  callerDemand: true, componentCalls: 3, baselineMethods: 91, initFailures: initialization.length, imports: [], installed: false }));
