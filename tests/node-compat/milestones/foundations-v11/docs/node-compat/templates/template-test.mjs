// Run with the exact Node v22.14.0 oracle. This tests the ESM stub and facade;
// it does NOT compile or exercise native-buffer.cpp.in.
import assert from 'node:assert/strict';
import * as nodeChild from 'node:child_process';
import * as nodeBuffer from 'node:buffer';
import * as child from './child-process.mjs';
import { createBufferModule, MAX_LENGTH, MAX_SOURCE_CODE_UNITS } from './buffer-facade.mjs';
import * as kernel from './reference-kernel.mjs';

assert.equal(process.version, 'v22.14.0', 'use the pinned oracle');
const profile = createBufferModule(kernel);
const { Buffer } = profile;
const NativeBuffer = nodeBuffer.Buffer;
assert.equal(Object.getPrototypeOf(Buffer), Uint8Array);
assert.equal(Buffer.BYTES_PER_ELEMENT, NativeBuffer.BYTES_PER_ELEMENT);
assert.equal(Buffer.prototype.BYTES_PER_ELEMENT, NativeBuffer.prototype.BYTES_PER_ELEMENT);
const refusal = { code: 'ERR_SM_NODE_UNSUPPORTED' };
assert.deepEqual(Object.keys(child).sort(), Object.keys(nodeChild).sort());
assert.deepEqual(Object.keys(profile).sort(), Object.keys(nodeBuffer).sort());
for (const name of Object.keys(child).filter(name => name !== 'default')) {
  assert.equal(child[name], child.default[name]);
  assert.throws(() => child[name](), { ...refusal, module: 'node:child_process', operation: name });
  assert.throws(() => new child[name](), refusal);
}
assert.equal(child.then, undefined);
assert.equal(child.default.then, undefined);
assert.equal(await child.default, child.default);
assert.equal(await import('./child-process.mjs'), child);
assert.equal(JSON.stringify(child.default), '{}'); // Safe normal function serialization.
for (const name of Object.keys(profile).filter(name => name !== 'default')) assert.equal(profile[name], profile.default[name]);
assert.equal(typeof profile.constants.MAX_LENGTH, 'number');
assert.equal(profile.constants.MAX_LENGTH, MAX_LENGTH);
assert.equal(profile.kMaxLength, profile.constants.MAX_LENGTH);
assert.equal(profile.kStringMaxLength, profile.constants.MAX_STRING_LENGTH);
for (const name of ['Blob', 'File', 'SlowBuffer', 'atob', 'btoa', 'isAscii', 'isUtf8', 'resolveObjectURL', 'transcode']) {
  assert.throws(() => profile[name](), refusal);
  assert.throws(() => new profile[name](), refusal);
}
assert.throws(() => Buffer(1), refusal);
assert.throws(() => new Buffer(1), refusal);
for (const [input, encoding] of [['hello', 'utf8'], ['é😀', 'UTF-8'], ['\ufeffBOM', 'utf8'], ['\ud800', 'utf8'],
  ['0001ff', 'hex'], ['AbCd', 'HEX'], ['a', 'hex'], ['12x4', 'hex'], ['12é4', 'hex'], ['12\0a', 'hex']]) {
  const actual = Buffer.from(input, encoding);
  const expected = NativeBuffer.from(input, encoding);
  assert.deepEqual([...actual], [...expected]);
  assert.equal(actual.toString(encoding), expected.toString(encoding));
  assert.equal(Buffer.byteLength(input, encoding), NativeBuffer.byteLength(input, encoding));
  assert.ok(actual instanceof Uint8Array);
  assert.ok(actual instanceof Buffer);
  assert.ok(Buffer.isBuffer(actual));
  assert.equal(Object.prototype.toString.call(actual), '[object Uint8Array]');
}
for (const n of [0, 1, 13]) {
  assert.deepEqual([...Buffer.alloc(n)], [...NativeBuffer.alloc(n)]);
  assert.deepEqual([...Buffer.alloc(n, 261)], [...NativeBuffer.alloc(n, 261)]);
}
const backing = new ArrayBuffer(12);
const original = new Uint8Array(backing, 3, 5);
original.set([1, 2, 3, 4, 5]);
const shared = Buffer.from(backing, 3, 5);
assert.equal(shared.buffer, backing);
assert.equal(shared.byteOffset, 3);
assert.equal(shared.byteLength, 5);
assert.equal(shared.parent, backing);
assert.equal(shared.offset, 3);
const copied = Buffer.from(original);
assert.notEqual(copied.buffer, backing);
assert.deepEqual([...copied], [1, 2, 3, 4, 5]);
for (const method of ['slice', 'subarray']) {
  shared[1] = 2;
  const view = shared[method](1, -1);
  assert.ok(Buffer.isBuffer(view));
  assert.equal(view.buffer, backing);
  assert.equal(view.byteOffset, 4);
  assert.deepEqual([...view], [2, 3, 4]);
  view[0] = 77;
  assert.equal(shared[1], 77);
  assert.equal(copied[1], 2);
}
assert.equal(shared.toString('hex', 1, 4), NativeBuffer.from(shared).toString('hex', 1, 4));
for (const method of ['map', 'filter']) {
  const result = shared[method](x => x);
  assert.ok(Buffer.isBuffer(result));
  assert.notEqual(result.buffer, backing);
}
assert.equal(Buffer.isBuffer(new Uint8Array()), false);
for (const name of Object.getOwnPropertyNames(NativeBuffer.prototype)) {
  assert.ok(name in Buffer.prototype, `missing explicit prototype API ${name}`);
}
for (const name of ['spawn', 'kill', 'ref', 'unref']) {
  assert.throws(() => child.ChildProcess.prototype[name](), refusal);
}
assert.throws(() => child.ChildProcess.prototype[Symbol.for('nodejs.dispose')](), refusal);
assert.throws(() => Buffer.prototype[Symbol.for('nodejs.util.inspect.custom')](), refusal);
for (const name of Object.getOwnPropertyNames(NativeBuffer)) {
  assert.ok(name in Buffer, `missing explicit static API ${name}`);
}
for (const [call, name, code] of [
  [() => Buffer.alloc(-1), 'RangeError', 'ERR_OUT_OF_RANGE'],
  [() => Buffer.alloc('2'), 'TypeError', 'ERR_INVALID_ARG_TYPE'],
  [() => Buffer.from('x', 'imaginary'), 'TypeError', 'ERR_UNKNOWN_ENCODING'],
  [() => Buffer.from(backing, 100), 'RangeError', 'ERR_BUFFER_OUT_OF_BOUNDS'],
]) assert.throws(call, { name, code });
assert.throws(() => Buffer.alloc(MAX_LENGTH + 1), { code: 'ERR_OUT_OF_RANGE' });
assert.throws(() => Buffer.from('x'.repeat(MAX_SOURCE_CODE_UNITS + 1)), { code: 'ERR_OUT_OF_RANGE' });
for (const call of [() => Buffer.from('SGVsbG8=', 'base64'), () => Buffer.from([1, 2]), () => Buffer.alloc(2, 'a'),
  () => Buffer.alloc(1.5), () => Buffer.allocUnsafe(1), () => shared.readUInt8(0), () => shared.indexOf(1)]) {
  assert.throws(call, refusal);
}
console.log('PASS Node v22.14.0 differential facade + explicit-stub templates (native C++ uncompiled)');
