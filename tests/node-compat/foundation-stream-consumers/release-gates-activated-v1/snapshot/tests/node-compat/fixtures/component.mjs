import bufferDefault, * as bufferNamespace from 'node:buffer';
import bareBufferDefault, { Buffer as BareBuffer } from 'buffer';
import childDefault, * as childNamespace from 'node:child_process';
import bareChildDefault from 'child_process';
import commonjs from './static-require.cjs';
import corpus from 'node-compat:oracle-vectors';
import coreExpectations from 'node-compat:core-expectations';

const { Buffer } = bufferNamespace;
const snapshotBacking = new ArrayBuffer(12);
const snapshotBuffer = Buffer.from(snapshotBacking, 3, 5);
snapshotBuffer.set([1, 2, 3, 4, 5]);
const snapshotText = Buffer.from('\ufeffé😀');
let calls = 0;
function check(value, message) { if (!value) throw new Error(message); }
function equal(actual, expected, message) {
  if (!Object.is(actual, expected)) throw new Error(`${message}: mismatched ${typeof actual}/${typeof expected} values`);
}
function sameBytes(actual, expected, message) {
  equal(actual.length, expected.length, `${message} length`);
  for (let i = 0; i < actual.length; i++) equal(actual[i], expected[i], `${message} byte ${i}`);
}
function error(call, code, module, operation) {
  try { call(); } catch (value) {
    equal(value.code, code, 'error code');
    if (code === 'ERR_SM_NODE_UNSUPPORTED') equal(value.profile, coreExpectations.coreVersion, 'unsupported profile version');
    if (module) equal(value.module, module, 'error module');
    if (operation) equal(value.operation, operation, 'error operation');
    return;
  }
  throw new Error(`Missing expected ${code}`);
}
const unsupported = call => error(call, 'ERR_SM_NODE_UNSUPPORTED');

async function runChecks() {
  const bufferExports = ['Blob', 'Buffer', 'File', 'INSPECT_MAX_BYTES', 'SlowBuffer', 'atob', 'btoa', 'constants', 'default', 'isAscii', 'isUtf8', 'kMaxLength', 'kStringMaxLength', 'resolveObjectURL', 'transcode'];
  const childExports = ['ChildProcess', '_forkChild', 'exec', 'execFile', 'execFileSync', 'execSync', 'fork', 'spawn', 'spawnSync'];
  equal(JSON.stringify(Object.keys(bufferNamespace).sort()), JSON.stringify(bufferExports.sort()), 'Buffer export inventory');
  equal(JSON.stringify(Object.keys(childNamespace).sort()), JSON.stringify([...childExports, 'default'].sort()), 'stub export inventory');
  equal(bufferDefault, bareBufferDefault, 'bare/prefixed Buffer default');
  equal(Buffer, BareBuffer, 'bare/prefixed Buffer constructor');
  equal(globalThis.Buffer, Buffer, 'native global Buffer');
  equal(commonjs.Buffer, Buffer, 'static CJS constructor');
  equal(commonjs.buffer, bufferDefault, 'static CJS Buffer default');
  equal(commonjs.childProcess, childDefault, 'static CJS stub default');
  equal(commonjs.localMarker, 'local Buffer marker', 'CJS local import-name collision preserved');
  equal(commonjs.moduleMarker, 'local module marker', 'CJS local wrapper-name collision preserved');
  equal(commonjs.nestedChild({ spawn() {} }), childDefault, 'CJS nested parameter cannot capture native default');
  equal(childDefault, bareChildDefault, 'bare/prefixed child default');
  for (const name of bufferExports.filter(name => name !== 'default')) equal(bufferNamespace[name], bufferDefault[name], `Buffer default ${name}`);
  for (const name of childExports) {
    equal(childNamespace[name], childDefault[name], `stub default ${name}`);
    error(() => childDefault[name](), 'ERR_SM_NODE_UNSUPPORTED', 'node:child_process', name);
    error(() => new childDefault[name](), 'ERR_SM_NODE_UNSUPPORTED', 'node:child_process', name);
  }
  for (const name of ['spawn', 'kill', 'ref', 'unref']) unsupported(() => childDefault.ChildProcess.prototype[name]());
  unsupported(() => childDefault.ChildProcess.prototype[Symbol.for('nodejs.dispose')]());
  equal(bufferNamespace.then, undefined, 'Buffer namespace then');
  equal(childNamespace.then, undefined, 'stub namespace then');
  equal(bufferDefault.then, undefined, 'Buffer default then');
  equal(childDefault.then, undefined, 'stub default then');
  equal(await Promise.resolve(bufferNamespace), bufferNamespace, 'await Buffer namespace');
  equal(await Promise.resolve(childNamespace), childNamespace, 'await stub namespace');
  equal(await Promise.resolve(bufferDefault), bufferDefault, 'await Buffer default');
  equal(JSON.stringify(childDefault), '{}', 'stub JSON inspection');
  check(JSON.stringify(bufferDefault).includes('MAX_LENGTH'), 'Buffer JSON inspection');
  equal(bufferNamespace.missing, undefined, 'missing property');
  equal(Object.getOwnPropertyDescriptor(bufferNamespace, 'Buffer').value, Buffer, 'module descriptor');
  equal(Object.getPrototypeOf(Buffer), Uint8Array, 'constructor inheritance');
  equal(Buffer.BYTES_PER_ELEMENT, 1, 'constructor element size');
  equal(Buffer.prototype.BYTES_PER_ELEMENT, 1, 'prototype element size');
  equal(Buffer.kMaxLength, undefined, 'constant belongs to module');
  equal(typeof bufferDefault.INSPECT_MAX_BYTES, 'number', 'inspect constant type');
  equal(bufferDefault.constants.MAX_LENGTH, 16777216, 'maximum allocation');
  equal(bufferDefault.kMaxLength, bufferDefault.constants.MAX_LENGTH, 'limit identity');
  equal(bufferDefault.kStringMaxLength, 33554432, 'string limit');
  equal(Buffer.poolSize, 0, 'no pool');
  check(Buffer.isBuffer(snapshotBuffer), 'snapshot private brand');
  equal(snapshotBuffer.buffer, snapshotBacking, 'snapshot shared backing');
  equal(snapshotBuffer.byteOffset, 3, 'snapshot offset');
  equal(snapshotText.toString(), '\ufeffé😀', 'snapshot codec/BOM');
  let stringChecks = 0;
  let byteChecks = 0;
  for (const vector of corpus.strings) {
    const actual = Buffer.from(vector.input, vector.encoding);
    sameBytes(actual, vector.bytes, 'string differential');
    equal(actual.toString(vector.encoding), vector.text, 'string round trip');
    equal(Buffer.byteLength(vector.input, vector.encoding), vector.byteLength, 'encoded byte length');
    check(actual instanceof Uint8Array && actual instanceof Buffer && Buffer.isBuffer(actual), 'typed array and brand');
    equal(Object.prototype.toString.call(actual), '[object Uint8Array]', 'typed array tag');
    stringChecks++;
  }
  for (const vector of corpus.bytes) {
    const actual = Buffer.from(new Uint8Array(vector.value));
    equal(actual.toString('hex'), vector.hex, 'native hex encoding');
    equal(actual.toString(), vector.text, 'malformed UTF-8 differential');
    sameBytes(Buffer.from(vector.hex, 'hex'), vector.value, 'native hex round trip');
    byteChecks++;
  }
  for (const size of [0, 1, 13, 1024]) {
    const value = Buffer.alloc(size);
    equal(value.length, size, 'allocation size');
    for (const byte of value) equal(byte, 0, 'zero initialized');
    for (const byte of Buffer.alloc(size, 261)) equal(byte, 5, 'numeric fill');
  }
  const cap = Buffer.alloc(16777216);
  equal(cap.length, 16777216, 'maximum allocation supported');
  equal(cap[0], 0, 'maximum first byte');
  equal(cap[cap.length - 1], 0, 'maximum final byte');
  const backing = new ArrayBuffer(12);
  const source = new Uint8Array(backing, 3, 5);
  source.set([1, 2, 3, 4, 5]);
  const shared = Buffer.from(backing, 3, 5);
  const copied = Buffer.from(source);
  const copiedBuffer = Buffer.from(shared);
  equal(shared.buffer, backing, 'shared AB');
  equal(shared.byteOffset, 3, 'shared byteOffset');
  equal(shared.byteLength, 5, 'shared byteLength');
  equal(shared.parent, backing, 'legacy parent');
  equal(shared.offset, 3, 'legacy offset');
  check(copied.buffer !== backing && copiedBuffer.buffer !== backing, 'independent copies');
  sameBytes(copied, [1, 2, 3, 4, 5], 'visible view copied');
  for (const method of ['slice', 'subarray']) {
    for (const [start, end, offset, expected] of [[1, -1, 4, [2, 3, 4]], [-99, 99, 3, [1, 2, 3, 4, 5]], [5, 1, 8, []], [5, 5, 8, []]]) {
      const view = shared[method](start, end);
      check(Buffer.isBuffer(view), 'view brand');
      equal(view.buffer, backing, 'view shares buffer');
      equal(view.byteOffset, offset, 'normalized view offset');
      sameBytes(view, expected, 'normalized view bytes');
    }
    const view = shared[method](1, -1);
    view[0] = 77;
    equal(shared[1], 77, 'view writes propagate');
    equal(copied[1], 2, 'copy is independent');
    shared[1] = 2;
  }
  for (const method of ['map', 'filter']) {
    const result = shared[method](value => value);
    check(Buffer.isBuffer(result) && result.buffer !== backing, 'species copy');
  }
  equal(shared.toString('hex', -2, 99), '0102030405', 'toString clipping');
  equal(shared.toString('hex', 3, 1), '', 'end precedes start');
  equal(Buffer.isBuffer(new Uint8Array()), false, 'no Uint8Array spoof');
  equal(Buffer.isBuffer(Object.create(Buffer.prototype)), false, 'no prototype spoof');
  equal(Buffer.isEncoding('UTF-8'), true, 'encoding alias');
  equal(Buffer.isEncoding('hex'), true, 'encoding hex');
  equal(Buffer.isEncoding('base64'), false, 'encoding excluded');
  equal(Buffer.byteLength(source), 5, 'view byteLength');
  equal(Buffer.byteLength(backing), 12, 'AB byteLength');
  for (const call of [() => Buffer(), () => new Buffer(1), () => Buffer.from([1]), () => Buffer.from(new Uint16Array(1)),
    () => Buffer.from(new DataView(backing)), () => Buffer.alloc(1.5), () => Buffer.alloc(2, 'a'), () => Buffer.from('eA==', 'base64'),
    () => Buffer.from(backing, '0'), () => shared.toString('hex', 1.5)]) unsupported(call);
  for (const value of [-1, NaN, Infinity, 16777217]) error(() => Buffer.alloc(value), 'ERR_OUT_OF_RANGE');
  error(() => Buffer.alloc('1'), 'ERR_INVALID_ARG_TYPE');
  error(() => Buffer.from(backing, 13), 'ERR_BUFFER_OUT_OF_BOUNDS');
  error(() => Buffer.from(backing, 1, 12), 'ERR_BUFFER_OUT_OF_BOUNDS');
  error(() => Buffer.from('x', 'unknown'), 'ERR_UNKNOWN_ENCODING');
  error(() => Buffer.from('x'.repeat(1048577)), 'ERR_OUT_OF_RANGE');
  for (const name of coreExpectations.unsupportedStatic) {
    unsupported(() => Buffer[name]());
    unsupported(() => new Buffer[name]());
  }
  // Build-time receipt policy is mandatory; never probe a truthy deferred function.
  let allocUnsafePrimordialCalls = null;
  if (['zeroed-no-pool-v1', 'zeroed-no-pool-direct-u8-v1'].includes(coreExpectations.allocUnsafePolicy)) {
    for (const size of [0, 0.5, 1.9, 17, 1024]) {
      const a = Buffer.allocUnsafe(size), b = new Buffer.allocUnsafe(size);
      equal(a.length, Math.trunc(size), 'allocUnsafe truncated size');
      equal(a.byteOffset, 0, 'allocUnsafe zero offset');
      equal(a.buffer.byteLength, a.length, 'allocUnsafe exact backing');
      check(a.buffer !== b.buffer && Buffer.isBuffer(a) && Buffer.isBuffer(b), 'allocUnsafe fresh owned brand');
      for (const byte of a) equal(byte, 0, 'allocUnsafe zero initialization');
    }
    for (const value of [-1, -0.5, NaN, Infinity, 16777216.25, 16777217]) error(() => Buffer.allocUnsafe(value), 'ERR_OUT_OF_RANGE');
    for (const value of [undefined, null, '1', 1n]) error(() => Buffer.allocUnsafe(value), 'ERR_INVALID_ARG_TYPE');
    const savedInteger=Number.isInteger, savedFinite=Number.isFinite; let integerCalls=0, finiteCalls=0, value;
    try { Number.isInteger=()=>{integerCalls++;return true;}; Number.isFinite=()=>{finiteCalls++;return true;}; value=Buffer.allocUnsafe(3.75); }
    finally { Number.isInteger=savedInteger; Number.isFinite=savedFinite; }
    const expectedCalls=coreExpectations.allocUnsafePolicy==='zeroed-no-pool-direct-u8-v1'?0:1;
    equal(integerCalls,expectedCalls,'source-selected integer-hook policy'); equal(finiteCalls,expectedCalls,'source-selected secondary finite-hook policy');
    equal(value.length,3,'captured truncation'); check(Buffer.isBuffer(value),'actual allocator brand');
    allocUnsafePrimordialCalls={integerCalls,finiteCalls,truncatedLength:value.length};
  } else if (coreExpectations.allocUnsafePolicy !== 'deferred') {
    throw new Error('Unrecognized allocUnsafe test policy');
  }
  // All excluded own callable properties have identifiable refusals, including
  // methods that otherwise could silently inherit incompatible U8 overloads.
  const supported = new Set(['constructor', 'toString', 'slice', 'subarray']);
  let unavailableMethods = 0;
  for (const name of Reflect.ownKeys(Buffer.prototype)) {
    const descriptor = Object.getOwnPropertyDescriptor(Buffer.prototype, name);
    if (typeof descriptor.value === 'function' && !supported.has(name)) {
      unsupported(() => descriptor.value.call(shared));
      unavailableMethods++;
    }
  }
  for (const name of ['Blob', 'File', 'SlowBuffer', 'atob', 'btoa', 'isAscii', 'isUtf8', 'resolveObjectURL', 'transcode']) {
    unsupported(() => bufferDefault[name]());
    unsupported(() => new bufferDefault[name]());
  }
  const backingCases = [];
  if (typeof SharedArrayBuffer === 'function') {
    const sharedBacking = new SharedArrayBuffer(8);
    unsupported(() => Buffer.from(sharedBacking));
    unsupported(() => Buffer.from(new Uint8Array(sharedBacking)));
    backingCases.push('shared-rejected');
  }
  const resizable = new ArrayBuffer(8, { maxByteLength: 16 });
  if (resizable.resizable === true) {
    unsupported(() => Buffer.from(resizable));
    unsupported(() => Buffer.from(new Uint8Array(resizable)));
    backingCases.push('resizable-rejected');
  }
  if (typeof structuredClone === 'function') {
    const detached = new ArrayBuffer(8);
    const detachedView = new Uint8Array(detached);
    structuredClone(detached, { transfer: [detached] });
    unsupported(() => Buffer.from(detached));
    unsupported(() => Buffer.from(detachedView));
    backingCases.push('detached-rejected');
  }
  equal(unavailableMethods, coreExpectations.prototypeRefusals, 'own prototype refusal count');
  return JSON.stringify({ coreVersion: coreExpectations.coreVersion, allocUnsafePolicy: coreExpectations.allocUnsafePolicy, allocUnsafePrimordialCalls, calls: ++calls, snapshot: 'native Buffer/brand/codecs survive', strings: stringChecks,
    bytes: byteChecks, seed: corpus.seed, unavailableMethods, backingCases, nativeImports: ['node:buffer', 'node:child_process'],
    staticCommonJS: true, globalBufferIdentity: true, stubCalls: childExports.length, stubConstructors: childExports.length });
}

export async function run() {
  try { return await runChecks(); }
  catch (error) {
    return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } });
  }
}
