// Targeted facade semantics for trusted fresh-output tagging. Production uses
// the private C++ kernel; this host test deliberately uses the known reference
// kernel only to exercise JavaScript validation, captures and object identity.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createBufferModule, MAX_LENGTH } from '../../builtins/node-compat/buffer-facade.mjs';
import { PROFILE_VERSION } from '../../builtins/node-compat/unsupported.mjs';
import * as kernel from '../../docs/node-compat/templates/reference-kernel.mjs';

assert.equal(process.version, 'v22.14.0');
const module = createBufferModule(kernel);
const { Buffer } = module;
function unavailable(call, operation) {
  assert.throws(call, {
    code: 'ERR_SM_NODE_UNSUPPORTED', module: 'node:buffer',
    profile: PROFILE_VERSION, ...(operation ? { operation } : {}),
  });
}

for (const size of [0, 1, 63, 64, 65, 255, 256, 4096]) {
  const input = Uint8Array.from({ length: size }, (_, i) => i & 255);
  const copy = Buffer.from(input);
  assert.deepEqual([...copy], [...input]);
  assert(Buffer.isBuffer(copy));
  assert(copy instanceof Buffer && copy instanceof Uint8Array);
  assert.notEqual(copy.buffer, input.buffer);
  assert.equal(copy.byteOffset, 0);
  assert.equal(copy.buffer.byteLength, size);
  assert.equal(copy.toString('hex'), NodeBuffer.from(input).toString('hex'));
  for (const method of ['map', 'filter']) {
    const derived = copy[method](method === 'map' ? x => x : () => true);
    assert(Buffer.isBuffer(derived));
    assert.notEqual(derived.buffer, copy.buffer);
    assert.deepEqual([...derived], [...copy]);
  }
  for (const method of ['slice', 'subarray']) {
    const derived = copy[method](0, size);
    assert(Buffer.isBuffer(derived));
    assert.equal(derived.buffer, copy.buffer);
    assert.equal(derived.byteOffset, copy.byteOffset);
  }
}
for (const text of ['', 'abcd', '12x4', '12é4', '12\0a', 'a', '00ff1020']) {
  const actual = Buffer.from(text, 'hex');
  assert.deepEqual([...actual], [...NodeBuffer.from(text, 'hex')]);
  assert(Buffer.isBuffer(actual));
}

// Brand spoofing and every excluded backing store remain checked at entry.
const fake = Object.create(Uint8Array.prototype);
const wrongKind = new Uint16Array([1, 2]);
Object.setPrototypeOf(wrongKind, Uint8Array.prototype);
for (const value of [fake, wrongKind, new Proxy(new Uint8Array(2), {})]) {
  unavailable(() => Buffer.from(value), 'invalid Uint8Array');
  assert.equal(Buffer.isBuffer(value), false);
}
const shared = new SharedArrayBuffer(8);
unavailable(() => Buffer.from(shared));
unavailable(() => Buffer.from(new Uint8Array(shared)), 'shared or invalid ArrayBuffer');
const resizable = new ArrayBuffer(8, { maxByteLength: 16 });
unavailable(() => Buffer.from(resizable), 'resizable ArrayBuffer');
unavailable(() => Buffer.from(new Uint8Array(resizable)), 'resizable ArrayBuffer');
const detached = new ArrayBuffer(8);
const detachedView = new Uint8Array(detached);
structuredClone(detached, { transfer: [detached] });
unavailable(() => Buffer.from(detached), 'detached ArrayBuffer');
unavailable(() => Buffer.from(detachedView), 'detached ArrayBuffer');
assert.throws(() => Buffer.alloc(MAX_LENGTH + 1), { code: 'ERR_OUT_OF_RANGE' });
assert.throws(() => new Buffer[Symbol.species](MAX_LENGTH + 1), { code: 'ERR_OUT_OF_RANGE' });
unavailable(() => new Buffer[Symbol.species](resizable), 'resizable ArrayBuffer');
unavailable(() => new Buffer[Symbol.species](shared), 'shared or invalid ArrayBuffer');

// External public property shadows never substitute for typed-array slots.
const shadowed = new Uint8Array([1, 2, 3]);
for (const name of ['buffer', 'byteLength', 'byteOffset', 'length']) {
  Object.defineProperty(shadowed, name, { get() { throw new Error(`read public ${name}`); } });
}
assert.deepEqual([...Buffer.from(shadowed)], [1, 2, 3]);

// Capture installation intrinsics before trusting fresh outputs. Public method
// replacements cannot detach a just-created output or forge its private brand.
const originals = {
  encode: TextEncoder.prototype.encode, decode: TextDecoder.prototype.decode,
  fill: Uint8Array.prototype.fill, add: WeakSet.prototype.add, has: WeakSet.prototype.has,
  setPrototypeOf: Object.setPrototypeOf,
};
let replacedCalls = 0;
try {
  TextEncoder.prototype.encode = () => { replacedCalls++; return new Uint8Array(resizable); };
  TextDecoder.prototype.decode = () => { replacedCalls++; return 'replaced'; };
  Uint8Array.prototype.fill = () => { replacedCalls++; throw new Error('replaced fill'); };
  WeakSet.prototype.add = () => { replacedCalls++; throw new Error('replaced private brand'); };
  WeakSet.prototype.has = () => { replacedCalls++; return true; };
  Object.setPrototypeOf = () => { replacedCalls++; throw new Error('replaced prototype installation'); };
  const allocated = Buffer.alloc(64, 261);
  assert.deepEqual([...allocated], Array(64).fill(5));
  assert(Buffer.isBuffer(allocated));
  assert.equal(Buffer.isBuffer(new Uint8Array(1)), false);
  assert.equal(Buffer.isBuffer(Object.create(Buffer.prototype)), false);
  const text = Buffer.from('\ufeffé😀', 'utf8');
  assert.equal(text.toString(), '\ufeffé😀');
  assert.deepEqual([...Buffer.from('00ff', 'hex')], [0, 255]);
  assert.deepEqual([...Buffer.from(new Uint8Array([4, 5]))], [4, 5]);
  assert.equal(replacedCalls, 0);
} finally {
  TextEncoder.prototype.encode = originals.encode;
  TextDecoder.prototype.decode = originals.decode;
  Uint8Array.prototype.fill = originals.fill;
  WeakSet.prototype.add = originals.add;
  WeakSet.prototype.has = originals.has;
  Object.setPrototypeOf = originals.setPrototypeOf;
}
assert.equal(module.Buffer, module.default.Buffer);
assert.equal(Object.getPrototypeOf(Buffer), Uint8Array);
assert.equal(Buffer.BYTES_PER_ELEMENT, 1);
console.log('PASS trusted-output facade semantics, captured native producers and strict external-input policy');
