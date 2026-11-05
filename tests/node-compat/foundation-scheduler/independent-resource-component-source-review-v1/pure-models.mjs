// Independent synthetic policy/parser checks. No native or packaging imports.
import assert from 'node:assert/strict';
import {
  authorityModel, fixtureModel, optionsModel, checkInterfaces,
  scalarAbiFromWit, checkTranspileMetadata,
} from '../resource-component-candidate-v1/models.mjs';

let checks = 0;
const yes = (value) => { assert(value); checks++; };
const no = (fn) => { assert.throws(fn); checks++; };
const sha = '9'.repeat(64);
const interfaces = ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:io/poll@0.2.10'];
const denied = [
  'nativeBuildAllowed', 'nativeFreezeAllowed', 'sourcePromotionAllowed',
  'ordinaryExportsAllowed', 'timerRuntimeAllowed', 'guestLoadingAllowed',
  'hostRequestsAllowed', 'gcAllowed', 'keyOrCryptoAllowed', 'timingAllowed',
  'operationalAdmission', 'runtimeAcceptanceClaim', 'metadataProjectionAllowed',
];
const fixtures = ['resource', 'pure', 'fatal', 'init-fatal'];
for (const name of fixtures) {
  const clocks = name !== 'pure';
  const expected = name === 'resource'
    ? {inspect: '() -> string', run: '(u32) -> string', validate: '() -> string'}
    : {run: '() -> string'};
  const root = {
    schemaVersion: 1,
    state: 'ROOT_REVIEWED_SCHEDULER_RESOURCE342_COMPONENT_CONSTRUCTION_PHASE_V1',
    sourceIndexSha256: sha, fixture: name, phase: 'construct-component',
    outputRoot: '/private/tmp/starling-node-compat/scheduler-resource-component-v1-' + name,
    workerTimeoutMs: 600000, maxComponentBytes: 67108864, maxBundleBytes: 33554432,
    componentConstructionAllowed: true, initializationOnly: true,
    ...Object.fromEntries(denied.map(key => [key, false])),
  };
  yes(authorityModel(root, sha).name === name);
  assert.deepEqual(fixtureModel(name).expectedAbi, expected); checks++;
  for (const key of denied) {
    for (const value of [true, null, undefined, 0, 'false']) {
      no(() => authorityModel({...root, [key]: value}, sha));
    }
  }
  for (const [key, value] of [
    ['phase', 'runtime'], ['fixture', 'unknown'], ['initializationOnly', false],
    ['componentConstructionAllowed', false], ['workerTimeoutMs', 600001],
    ['maxComponentBytes', 67108865], ['maxBundleBytes', 33554433],
    ['outputRoot', root.outputRoot + '/old'], ['sourceIndexSha256', '0'.repeat(64)],
  ]) no(() => authorityModel({...root, [key]: value}, sha));
  const finalizer = () => {};
  const options = optionsModel({engine: {path: '/pinned/engine'}, adapter: {path: '/pinned/adapter'}, fixture: name, wit: 'pinned world', finalizeComponent: finalizer});
  assert.deepEqual(options.selectedInterfaces, clocks ? interfaces : []); checks++;
  assert.deepEqual(options.disableFeatures, clocks ? ['stdio', 'random', 'http', 'fetch-event'] : ['stdio', 'random', 'http', 'fetch-event', 'clocks']); checks++;
  assert.deepEqual(options.env, {}); checks++;
  yes(options.enableAot === false && options.finalizeComponent === finalizer && options.engine === '/pinned/engine' && options.preview2Adapter === '/pinned/adapter');
  const selected = clocks ? [...interfaces] : [];
  yes(checkInterfaces({state: 'verified-final-component', emittedImports: selected}, name));
  for (const extra of ['wasi:clocks/wall-clock@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.12', 'custom:clock/now']) {
    no(() => checkInterfaces({state: 'verified-final-component', emittedImports: [...selected, extra]}, name));
  }
  no(() => checkInterfaces({state: 'unreviewed', emittedImports: selected}, name));
  const body = [...selected.map(value => `import ${value};`), ...Object.entries(expected).map(([key, type]) => `export ${key}: func(${type.includes('u32') ? 'case-id: u32' : ''}) -> string;`)].join('\n');
  const wit = `package root:component;\nworld root {\n${body}\n}\n`;
  assert.deepEqual(scalarAbiFromWit(wit, name), expected); checks++;
  for (const invalid of [
    wit.replace('-> string', '-> u32'), wit.replace('world root', 'world other'),
    wit + '\nworld root {}', wit.replace('world root {', 'world root { export then: func() -> string;'),
    wit.replace('world root {', 'world root { import wasi:random/random@0.2.10;'),
    wit.replace('export run:', 'export Run:'), wit.replace('export run:', 'export run: func() -> string; export run:'),
  ]) no(() => scalarAbiFromWit(invalid, name));
  const metadata = {imports: selected, exports: Object.keys(expected).map(key => [key, 'function'])};
  yes(checkTranspileMetadata(metadata, name));
  for (const exports of [[], [...metadata.exports, ['then', 'function']], metadata.exports.map(([key]) => [key, 'instance']), metadata.exports.map(() => ['run', 'function', 'extra'])]) {
    no(() => checkTranspileMetadata({...metadata, exports}, name));
  }
}
for (const name of ['', 'constructor', 'then', null, undefined, 0]) no(() => fixtureModel(name));
console.log(JSON.stringify({schemaVersion: 1, state: 'INDEPENDENT_RESOURCE_COMPONENT_PURE_MODELS_PASSED_V1', checks, sourceOnly: true, ownerActionsInvoked: false}));
