// Ordinary source/factory tests only: no compiled m0.8 engine is used here.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { runInThisContext } from 'node:vm';
import { spawnSync } from 'node:child_process';
import * as kernel from '../../../../docs/node-compat/templates/reference-kernel.mjs';
import { allocationChecks, preserveCoreUnsupported } from '../checks.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../..');
const hash = value => createHash('sha256').update(value).digest('hex');
const Base = join(here, 'base/builtins/node-compat'), Source = join(here, 'source/builtins/node-compat');
const Apply = Reflect.apply, Construct = Reflect.construct, Define = Object.defineProperty;
const Descriptor = Object.getOwnPropertyDescriptor, OwnKeys = Reflect.ownKeys, Proto = Object.getPrototypeOf;
const TypeErrorCtor = TypeError, RangeErrorCtor = RangeError, ErrorCtor = Error;
const receipt = JSON.parse(await readFile(join(here, 'source-receipt.json')));
for (const item of [...receipt.changed, ...receipt.unchanged]) {
  const name = item.path.slice('builtins/node-compat/'.length);
  assert.equal(hash(await readFile(join(Base, name))), item.before);
  assert.equal(hash(await readFile(join(Source, name))), item.after);
  assert.equal(hash(await readFile(join(repository, item.path))), item.before, 'Production source must stay at the preserved base: '+item.path);
}
assert.equal(hash(await readFile(join(here, 'core-m0.8.patch'))), receipt.patchSha256);
const patchCheck = spawnSync('git', ['apply', '--check', join(here, 'core-m0.8.patch')], { cwd: repository, encoding: 'utf8' });
assert.equal(patchCheck.status, 0, patchCheck.stderr);
const generated = spawnSync(process.execPath, [join(Source, 'generate-factories.mjs'), '--check'], { encoding: 'utf8' });
assert.equal(generated.status, 0, generated.stderr || generated.stdout);
const registrar = await readFile(join(repository, 'builtins/node-compat/register.cpp'), 'utf8');
assert.match(registrar, /options\.setForceStrictMode\(\)/, 'Generated factory must model the actual strict embedding helper');

async function load(root, generatedFactory) {
  if (!generatedFactory) {
    const module = await import(pathToFileURL(join(root, 'buffer-facade.mjs')));
    const child = await import(pathToFileURL(join(root, 'child-process.mjs')));
    return { buffer: module.createBufferModule(kernel), child };
  }
  const header = await readFile(join(root, 'factories.generated.h'), 'utf8');
  function factory(name) {
    const literal = new RegExp('static constexpr const char '+name+'\\[\\] = R"SM_NODE_PROFILE\\(([\\s\\S]*?)\\)SM_NODE_PROFILE";').exec(header)?.[1];
    assert(literal, 'Missing exact generated factory '+name);
    return runInThisContext('"use strict";\n'+literal, { filename: root+'/'+name });
  }
  return { buffer: factory('kBufferFactorySource')(kernel), child: factory('kChildProcessFactorySource')() };
}
function refusal(call, version, module, operation) {
  let result;
  try { call(); } catch (error) { result = error; }
  assert(result instanceof ErrorCtor, 'Deferred operation must throw an Error');
  assert.equal(result.code, 'ERR_SM_NODE_UNSUPPORTED'); assert.equal(result.profile, version);
  assert.equal(result.module, module); assert.equal(result.operation, operation);
}
function shape(object) {
  return OwnKeys(object).map(key => {
    const d = Descriptor(object, key);
    return { key: typeof key === 'symbol' ? String(key) : key, configurable: d.configurable,
      enumerable: d.enumerable, writable: d.writable, valueType: typeof d.value,
      getType: typeof d.get, setType: typeof d.set };
  });
}
function preservation(buffer, child, baseline) {
  const B = buffer.Buffer, version = 'sm-node-22.14.0-m0.8';
  assert.deepEqual(OwnKeys(buffer), OwnKeys(baseline));
  assert.equal(OwnKeys(buffer).length, 15);
  assert(Object.isFrozen(buffer) && Object.isFrozen(buffer.default) && Object.isFrozen(buffer.constants));
  for (const name of OwnKeys(buffer).filter(key => key !== 'default')) assert.equal(buffer[name], buffer.default[name]);
  assert.equal(buffer.then, undefined); assert.equal(buffer.default.then, undefined);
  assert.equal(Proto(B), Uint8Array); assert.equal(B.poolSize, 0);
  assert.deepEqual(shape(B), shape(baseline.Buffer), 'Static declaration order/types/attributes are preserved');
  assert.deepEqual(shape(B.prototype), shape(baseline.Buffer.prototype));
  const supported = new Set(['constructor', 'toString', 'slice', 'subarray']), value = B.alloc(1);
  let prototypes = 0;
  for (const name of OwnKeys(B.prototype)) {
    const d = Descriptor(B.prototype, name);
    if (typeof d.value !== 'function' || supported.has(name)) continue;
    const operation = typeof name === 'symbol' ? 'Buffer.prototype[util.inspect.custom]' : 'Buffer.prototype.'+name;
    refusal(() => Apply(d.value, value, []), version, 'node:buffer', operation);
    refusal(() => Construct(d.value, []), version, 'node:buffer', operation); prototypes++;
  }
  assert.equal(prototypes, 91);
  const staticNames = ['copyBytesFrom', 'of', 'allocUnsafeSlow', 'compare', 'concat'];
  for (const name of staticNames) {
    refusal(() => B[name](1), version, 'node:buffer', 'Buffer.'+name);
    refusal(() => new B[name](1), version, 'node:buffer', 'Buffer.'+name);
  }
  refusal(() => B(1), version, 'node:buffer', 'Buffer constructor');
  refusal(() => new B(1), version, 'node:buffer', 'Buffer constructor');
  for (const name of ['Blob', 'File', 'SlowBuffer', 'atob', 'btoa', 'isAscii', 'isUtf8', 'resolveObjectURL', 'transcode']) {
    refusal(() => buffer[name](), version, 'node:buffer', name);
    refusal(() => new buffer[name](), version, 'node:buffer', name);
  }
  const childNames = ['ChildProcess', '_forkChild', 'exec', 'execFile', 'execFileSync', 'execSync', 'fork', 'spawn', 'spawnSync'];
  for (const name of childNames) {
    assert.equal(child[name], child.default[name]);
    refusal(() => child[name](), version, 'node:child_process', name);
    refusal(() => new child[name](), version, 'node:child_process', name);
  }
  for (const name of ['spawn', 'kill', 'ref', 'unref']) refusal(() => child.ChildProcess.prototype[name](), version, 'node:child_process', 'ChildProcess.prototype.'+name);
  refusal(() => child.ChildProcess.prototype[Symbol.for('nodejs.dispose')](), version, 'node:child_process', 'ChildProcess.prototype[Symbol.dispose]');
  assert.equal(child.then, undefined); assert.equal(child.default.then, undefined);
  return { exports: 15, prototypeRefusals: prototypes, otherStaticRefusals: staticNames.length,
    childCallAndConstruct: childNames.length, profile: version, staticDescriptorOrderPreserved: true };
}
function policy(buffer) {
  const B = buffer.Buffer, allocate = B.allocUnsafe, result = [];
  function check(name, run) { result.push({ name, result: run() }); }
  check('fresh zeroed exact backing including empty buffers', () => {
    return [0, 0.5, 1, 17, 1024].map(size => {
      const a = allocate(size), b = allocate(size);
      assert.equal(a.byteOffset, 0); assert.equal(a.buffer.byteLength, a.length);
      assert.notEqual(a.buffer, b.buffer); assert([...a].every(value => value === 0));
      return { size, length: a.length, offset: a.byteOffset, backingBytes: a.buffer.byteLength, zeroed: true };
    });
  });
  check('inclusive cap and raw fractional size rejection', () => {
    const a = allocate(16777216); assert.equal(a.length, 16777216);
    assert.equal(a.buffer.byteLength, a.length); assert.equal(a.byteOffset, 0);
    assert.deepEqual([a[0], a[8388608], a[16777215]], [0, 0, 0]);
    for (const value of [16777216.25, 16777217, Number.MAX_SAFE_INTEGER]) {
      assert.throws(() => allocate(value), { name: 'RangeError', code: 'ERR_OUT_OF_RANGE' });
    }
    return { length: a.length, samples: [0, 0, 0], rejectedRawSizes: 3 };
  });
  check('captured public allocator Math.trunc and Reflect.apply', () => {
    const oldAlloc = B.alloc, oldTrunc = Math.trunc, oldApply = Reflect.apply;
    let calls = 0, a;
    function replaced() { calls++; throw new ErrorCtor('Public mutable function called'); }
    try { B.alloc = replaced; Math.trunc = replaced; Reflect.apply = replaced; a = allocate(3.9); }
    finally { B.alloc = oldAlloc; Math.trunc = oldTrunc; Reflect.apply = oldApply; }
    assert.equal(calls, 0); assert.equal(a.length, 3); assert(B.isBuffer(a));
    assert.deepEqual([...a], [0, 0, 0]); return { length: 3, replacementCalls: calls };
  });
  check('captured validation constructors finite check and safe own error fields', () => {
    const descriptors = Object.fromEntries(['code', 'module', 'operation'].map(name => [name, Descriptor(ErrorCtor.prototype, name)]));
    const saved = { TypeError: globalThis.TypeError, RangeError: globalThis.RangeError, define: Object.defineProperty, finite: Number.isFinite };
    let poisonCalls = 0, type, range;
    const poison = () => { poisonCalls++; throw new ErrorCtor('Mutable error or descriptor hook called'); };
    try {
      for (const name of ['code', 'module', 'operation']) Define(ErrorCtor.prototype, name, { get: poison, set: poison, configurable: true });
      globalThis.TypeError = poison; globalThis.RangeError = poison;
      Object.defineProperty = poison; Number.isFinite = poison;
      try { allocate('3'); } catch (error) { type = error; }
      try { allocate(Infinity); } catch (error) { range = error; }
    } finally {
      globalThis.TypeError = saved.TypeError; globalThis.RangeError = saved.RangeError;
      Object.defineProperty = saved.define; Number.isFinite = saved.finite;
      for (const name of ['code', 'module', 'operation']) {
        if (descriptors[name]) Define(ErrorCtor.prototype, name, descriptors[name]); else delete ErrorCtor.prototype[name];
      }
    }
    assert(type instanceof TypeErrorCtor); assert(range instanceof RangeErrorCtor); assert.equal(poisonCalls, 0);
    for (const [error, code] of [[type, 'ERR_INVALID_ARG_TYPE'], [range, 'ERR_OUT_OF_RANGE']]) {
      for (const [key, value] of [['code', code], ['module', 'node:buffer'], ['operation', 'Buffer.allocUnsafe']]) {
        assert.deepEqual(Descriptor(error, key), { value, writable: true, enumerable: true, configurable: true });
      }
    }
    return { poisonCalls, codes: [type.code, range.code], ownDataFields: ['code', 'module', 'operation'] };
  });
  check('poolSize mutation has no allocation effect', () => {
    const old = B.poolSize; let a;
    try { B.poolSize = 8192; a = allocate(3); } finally { B.poolSize = old; }
    assert.equal(a.buffer.byteLength, 3); assert.equal(a.byteOffset, 0);
    assert.equal(a.parent, a.buffer); assert.equal(a.offset, 0); return { backingBytes: 3, offset: 0 };
  });
  return result;
}
const globalBuffer = globalThis.Buffer;
const oracle = allocationChecks(NodeBuffer, NodeBuffer.allocUnsafe);
const variants = [];
for (const generatedFactory of [false, true]) {
  const base = await load(Base, generatedFactory), candidate = await load(Source, generatedFactory);
  const baseControl = preserveCoreUnsupported(base.buffer.Buffer);
  refusal(() => base.child.spawn(), 'sm-node-22.14.0-m0.1', 'node:child_process', 'spawn');
  const differential = allocationChecks(candidate.buffer.Buffer, candidate.buffer.Buffer.allocUnsafe);
  assert.deepEqual(differential, oracle);
  const profile = policy(candidate.buffer), preserved = preservation(candidate.buffer, candidate.child, base.buffer);
  assert.equal(globalThis.Buffer, globalBuffer, 'Factory does not inject a global');
  variants.push({ kind: generatedFactory ? 'exact-generated-strict-factory' : 'actual-candidate-esm', baseControl,
    differentialGroups: differential.length, cases: differential, profileGroups: profile.length, profile, preserved });
}
assert.deepEqual(variants[0].cases, variants[1].cases); assert.deepEqual(variants[0].profile, variants[1].profile);
const controls = [];
for (const name of ['foundations-v6', 'foundations-v7']) {
  const root = '/tmp/starling-node-compat/'+name+'/native-freeze';
  const engine = join(root, 'off-foundations.engine.wasm'), metadata = JSON.parse(await readFile(engine+'.build.json'));
  assert.equal(hash(await readFile(engine)), metadata.engineSha256);
  const relevant = receipt.changed.concat(receipt.unchanged.filter(item => item.path === 'builtins/node-compat/buffer.cpp'));
  for (const item of relevant) {
    assert.equal(metadata.sourceManifest.find(input => input.path === item.path)?.sha256, item.before);
    assert.equal(hash(await readFile(join(root, 'source', item.path))), item.before);
  }
  controls.push({ milestone: name, engineSha256: metadata.engineSha256, sourceInputs: metadata.sourceManifest.length,
    coreVersion: 'sm-node-22.14.0-m0.1', relevantSourceHashes: Object.fromEntries(relevant.map(item => [item.path, item.before])) });
}
const report = { schema: 1, proposalVersion: receipt.proposalVersion, node: process.version, installed: false,
  candidateCoreVersion: receipt.candidateCoreVersion, variants, archivedControls: controls,
  sourceReceiptSha256: hash(await readFile(join(here, 'source-receipt.json'))), patchSha256: receipt.patchSha256,
  generatorCheck: generated.stdout.trim(), patchApplyCheck: true, strictRegistrarSha256: hash(registrar),
  testSources: Object.fromEntries(await Promise.all(['run-host.mjs', 'prepare.mjs', '../checks.mjs', '../../../../docs/node-compat/templates/reference-kernel.mjs'].map(async name => [name, hash(await readFile(resolve(here, name)))]))),
  nodeEmbeddedSourceSha256: Object.fromEntries(['buffer', 'internal/buffer', 'internal/validators'].map(name => [name, hash(process.binding('natives')[name])])),
  limitations: ['Host tests of actual candidate ESM and exact generated strict factory use a JS reference hex kernel; allocation is the facade owned Uint8Array path, not compiled C++ evidence.',
    'No m0.8 native engine/component or target-host test has run. Accepted isolated wrapper component evidence belongs to core m0.1 v6 only.',
    'Only new validation and named captures are hardened here. The existing captured Buffer.alloc retains its existing mutable Number.isFinite/Number.isInteger checks; whole-facade primordial hardening is outside this patch.',
    'Node initial allocUnsafe bytes are never read. Maximum storage is sampled, not exhaustively checked. No genuine allocation failure/OOM is induced or claimed.',
    'All 91 own prototype refusals remain deferred. No allocUnsafeSlow, pooling, other Buffer method, scheduler or classic-stream support is introduced.'] };
await writeFile(join(here, 'host-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ variants: variants.map(({kind, differentialGroups, profileGroups, preserved}) => ({kind, differentialGroups, profileGroups, preserved})),
  archivedControls: controls.map(({milestone, coreVersion}) => ({milestone, coreVersion})), patchApplyCheck: true, installed: false }));
