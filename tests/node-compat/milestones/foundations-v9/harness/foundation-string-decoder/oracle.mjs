// Host-only differential oracle for the unintegrated prototype. No native
// StringDecoder registration or generic TextDecoder memory-safety claim.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { StringDecoder as NodeDecoder } from 'node:string_decoder';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createStringDecoderModule, INPUT_LIMIT } from './prototype.mjs';
import { createBufferModule } from '../../../builtins/node-compat/buffer-facade.mjs';
import * as referenceKernel from '../../../docs/node-compat/templates/reference-kernel.mjs';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const profileBuffer = createBufferModule(referenceKernel).Buffer;
const variants = [['NodeBuffer native host', NodeBuffer], ['M0 facade with explicit JS reference kernel', profileBuffer]];
const stats = { sequences: 0, writes: 0, bytePairs: 0, errorCases: 0, mutationCases: 0 };
const observations = [];
function snapshot(decoder) { return { need: decoder.lastNeed, total: decoder.lastTotal, char: [...decoder.lastChar] }; }
function code(action) { try { action(); return null; } catch (error) { return { name: error.name, code: error.code }; } }
function sequence(Actual, encoding, chunks) {
  const expected = new NodeDecoder(encoding), actual = new Actual(encoding);
  for (const chunk of chunks) {
    assert.equal(actual.write(chunk), expected.write(chunk));
    assert.deepEqual(snapshot(actual), snapshot(expected)); stats.writes++;
  }
  assert.equal(actual.end(), expected.end()); assert.deepEqual(snapshot(actual), snapshot(expected));
  assert.equal(actual.end(Uint8Array.of(0x41)), expected.end(Uint8Array.of(0x41)), 'reuse after end');
  stats.sequences++;
}
for (const [label, Buffer] of variants) {
  const module = createStringDecoderModule(Buffer), Actual = module.StringDecoder;
  assert.deepEqual(Object.keys(module).sort(), ['StringDecoder', 'default']);
  assert.equal(module.default.StringDecoder, Actual);
  assert.equal(Actual.name, NodeDecoder.name); assert.equal(Actual.length, NodeDecoder.length);
  assert.deepEqual(Object.getOwnPropertyNames(Actual.prototype), Object.getOwnPropertyNames(NodeDecoder.prototype));
  for (const name of Object.getOwnPropertyNames(NodeDecoder.prototype)) {
    const a = Object.getOwnPropertyDescriptor(Actual.prototype, name), n = Object.getOwnPropertyDescriptor(NodeDecoder.prototype, name);
    for (const key of ['enumerable', 'configurable', 'writable']) assert.equal(a[key], n[key]);
    if (typeof a.value === 'function') { assert.equal(a.value.length, n.value.length); assert.equal(a.value.name, n.value.name); }
    if (a.get) { assert.equal(a.get.length, n.get.length); assert.equal(a.get.name, n.get.name); }
  }
  const sample = new Actual(), nodeSample = new NodeDecoder();
  assert.deepEqual(Object.keys(sample), Object.keys(nodeSample));
  assert.deepEqual(Object.getOwnPropertySymbols(sample).map(String), Object.getOwnPropertySymbols(nodeSample).map(String));
  const view = sample.lastChar;
  assert(Buffer.isBuffer(view)); assert.equal(view.length, 4); assert.equal(view.buffer.byteLength, 7);
  assert.equal(view.byteOffset, 0); assert.notEqual(view, sample.lastChar); assert.equal(view.buffer, sample.lastChar.buffer);
  for (const encoding of ['utf8', 'hex']) {
    const a = new Actual(encoding), n = new NodeDecoder(encoding);
    assert.deepEqual([...a[Object.getOwnPropertySymbols(a)[0]]], [...n[Object.getOwnPropertySymbols(n)[0]]]);
  }
  assert.equal(Actual.call({}, 'utf8'), undefined);
  assert.deepEqual(code(() => Actual()), code(() => NodeDecoder()));
  for (const encoding of [undefined, null, '', 'utf8', 'utf-8', 'UTF8', 'UTF-8', 'hex', 'HEX']) {
    assert.equal(new Actual(encoding).encoding, new NodeDecoder(encoding).encoding);
  }
  for (const [length, text] of [[4, 'utf8'], [5, 'UTF-8'], [3, 'HEX']]) {
    const traces = [];
    for (const Ctor of [Actual, NodeDecoder]) {
      const trace = [];
      const label = { get length() { trace.push('length'); return length; },
        toString() { trace.push('toString'); return text; } };
      trace.push(new Ctor(label).encoding); traces.push(trace);
    }
    assert.deepEqual(traces[0], traces[1]);
  }
  for (const encoding of [new String('utf8'), new String('HEX')]) {
    assert.equal(new Actual(encoding).encoding, new NodeDecoder(encoding).encoding);
  }
  for (const encoding of ['ascii', 'latin1', 'binary', 'base64', 'base64url', 'utf16le', 'utf-16le', 'ucs2', 'ucs-2']) {
    assert.equal(code(() => new Actual(encoding)).code, 'ERR_SM_NODE_UNSUPPORTED'); stats.errorCases++;
  }
  for (const encoding of [0, false, true, {}, [], 'rot13', 'utf16be', ' utf8 ']) {
    assert.deepEqual(code(() => new Actual(encoding)), code(() => new NodeDecoder(encoding))); stats.errorCases++;
  }
  for (const value of [undefined, null, 1, false, {}, [], new ArrayBuffer(2)]) {
    assert.deepEqual(code(() => new Actual().write(value)), code(() => new NodeDecoder().write(value))); stats.errorCases++;
  }
  for (const receiver of [undefined, null, {}]) {
    assert.equal(Actual.prototype.write.call(receiver, 'literal'), NodeDecoder.prototype.write.call(receiver, 'literal'));
    for (const input of [Uint8Array.of(0x41), {}]) {
      assert.deepEqual(code(() => Actual.prototype.write.call(receiver, input)), code(() => NodeDecoder.prototype.write.call(receiver, input))); stats.errorCases++;
    }
  }
  const seeds = ['24', 'c2a2', 'e282ac', 'f09f8c8d', 'efbbbf', 'eda0b5edb08d', 'c0', 'c080', 'f08f8080',
    'f69bd1', 'f4bde5', 'e2fbcc01', 'f0fb00', 'cce2b8b8', 'e2b8ccb8', 'ccB8cdB9'];
  for (const hex of seeds) {
    const bytes = NodeBuffer.from(hex, 'hex');
    for (let cuts = 0; cuts < 2 ** Math.max(0, bytes.length - 1); cuts++) {
      const chunks = []; let start = 0;
      for (let i = 1; i <= bytes.length; i++) if (i === bytes.length || (cuts & 2 ** (i - 1))) {
        chunks.push(new DataView(bytes.buffer, bytes.byteOffset + start, i - start)); start = i;
      }
      sequence(Actual, 'utf8', chunks); sequence(Actual, 'hex', chunks);
    }
  }
  // Exhaustive two-byte boundary space, including all invalid starters and
  // continuation pairs. Compare output AND all public carry-state bytes.
  for (let first = 0; first < 256; first++) for (let second = 0; second < 256; second++) {
    sequence(Actual, 'utf8', [Uint8Array.of(first), Uint8Array.of(second)]); stats.bytePairs++;
  }
  let seed = 0x5eed1234;
  const random = () => (seed = Math.imul(seed, 1664525) + 1013904223 >>> 0);
  for (let i = 0; i < 3000; i++) {
    const chunks = [];
    for (let j = 0, count = random() % 6 + 1; j < count; j++) {
      const data = new Uint8Array(random() % 17 + 2);
      for (let k = 0; k < data.length; k++) data[k] = random() & 255;
      chunks.push(j % 2 ? new DataView(data.buffer, 1, data.length - 2) : data.subarray(1, data.length - 1));
    }
    sequence(Actual, i % 2 ? 'utf8' : 'hex', chunks);
  }
  for (const Type of [Uint8Array, Uint8ClampedArray, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array, Float32Array, Float64Array, BigInt64Array, BigUint64Array]) {
    const raw = new Uint8Array(32).fill(0x61); const view = new Type(raw.buffer, 8, 16 / Type.BYTES_PER_ELEMENT);
    sequence(Actual, 'utf8', [view]);
  }
  for (const Ctor of [Actual, NodeDecoder]) {
    const decoder = new Ctor(); decoder.write(Uint8Array.of(0xe2)); decoder.encoding = 'hex';
    assert.equal(decoder.write('literal'), 'literal'); assert.equal(decoder.lastNeed, 2);
    decoder.lastChar[0] = 0x41; assert.equal(decoder.end(), 'A'); assert.equal(decoder.end(Uint8Array.of(0x42)), 'B');
    stats.mutationCases++;
  }
  for (const value of [NodeBuffer.from('skipvalue'), Uint8Array.from([0x73,0x6b,0x69,0x70,0x76]), new Uint16Array([0x4141,0x4242]), 'skipvalue']) {
    const a = new Actual(), n = new NodeDecoder(); a.write(Uint8Array.of(0xe2)); n.write(Uint8Array.of(0xe2));
    assert.equal(a.text(value, 1), n.text(value, 1)); assert.deepEqual(snapshot(a), snapshot(n));
  }
  for (const input of [{}, new DataView(new ArrayBuffer(4))]) {
    const a = new Actual(), n = new NodeDecoder(); a.write(Uint8Array.of(0xe2)); n.write(Uint8Array.of(0xe2));
    assert.deepEqual(code(() => a.text(input, 0)), code(() => n.text(input, 0)));
    assert.deepEqual(snapshot(a), snapshot(n));
  }
  const traces = [];
  for (const Ctor of [Actual, NodeDecoder]) {
    const decoder = new Ctor(); decoder.write(Uint8Array.of(0xe2));
    const trace = [];
    const input = { slice(offset) { trace.push([offset, decoder.lastNeed, decoder.lastTotal]); return Uint8Array.of(0x41); } };
    trace.push(decoder.text(input, 7));
    decoder.write = () => 'custom'; trace.push(decoder.end(Uint8Array.of(0x42)));
    traces.push(trace); stats.mutationCases++;
  }
  assert.deepEqual(traces[0], traces[1]);
  const shadowed = Uint8Array.of(0x41);
  for (const key of ['buffer', 'byteOffset', 'byteLength']) Object.defineProperty(shadowed, key, { get() { throw new Error('shadowed getter'); } });
  sequence(Actual, 'utf8', [shadowed]);
  const over = new Uint8Array(INPUT_LIMIT + 1), limited = new Actual(); limited.write(Uint8Array.of(0xe2));
  assert.equal(code(() => limited.write(over)).code, 'ERR_SM_NODE_LIMIT'); assert.equal(limited.lastNeed, 2);
  assert.equal(code(() => limited.text(over, 0)).code, 'ERR_SM_NODE_LIMIT'); assert.equal(limited.lastNeed, 0);
  observations.push({ label, constructor: Actual.name, stateBytes: 7, lastCharViewBytes: 4, viewsShareOneUnsharedBuffer: true });
}
const report = { schema: 1, node: process.version, scope: 'Host-only unintegrated UTF8/hex prototype; no generic native TextDecoder safety or registered builtin claim',
  stats, variants: observations, exclusions: ['Shared/resizable/detached backing stores are not exercised on old native TextDecoder.',
    'Other known encodings are explicit deferred constructor errors.', 'Detailed received-value messages, internal-state corruption and forged receivers are outside this prototype contract.'],
  sourceManifest: await Promise.all(['prototype.mjs', 'oracle.mjs', '../../../builtins/node-compat/buffer-facade.mjs',
    '../../../docs/node-compat/templates/reference-kernel.mjs'].map(async path => ({ path,
    sha256: createHash('sha256').update(await readFile(join(here, path))).digest('hex') }))) };
await writeFile(join(here, 'oracle-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
