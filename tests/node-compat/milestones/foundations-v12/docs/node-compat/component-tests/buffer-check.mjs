// Executed semantic facade test with a JS TEST DOUBLE kernel. No native kernel
// performance, GC-safety or ownership claim follows from this component.
import { createBufferModule, MAX_LENGTH } from '../templates/buffer-facade.mjs';
import * as referenceKernel from '../templates/reference-kernel.mjs';
const profile = createBufferModule(referenceKernel);
const { Buffer } = profile;
const snapshotText = '\ufeffé😀';
const snapshotBuffer = Buffer.from(snapshotText);
let calls = 0;
function assert(value, message) { if (!value) throw new Error(message); }
function refusal(operation) {
  try { operation(); throw new Error('unexpected supported operation'); }
  catch (error) { assert(error.code === 'ERR_SM_NODE_UNSUPPORTED', 'unsupported error identity'); }
}
export function run() {
  assert(Buffer.isBuffer(snapshotBuffer), 'snapshot Buffer brand');
  assert(snapshotBuffer instanceof Uint8Array, 'snapshot typed array');
  assert(snapshotBuffer.toString() === snapshotText, 'snapshot decoder preserves BOM');
  assert(profile.default.Buffer === Buffer, 'module default identity');
  assert(Object.getPrototypeOf(Buffer) === Uint8Array && Buffer.BYTES_PER_ELEMENT === 1, 'typed-array constructor inheritance');
  assert(typeof profile.constants.MAX_LENGTH === 'number', 'constant type');
  const cases = [
    ['hello', 'utf8'], ['é😀', 'UTF-8'], ['\ufeffBOM', 'utf8'], ['\ud800', 'utf8'],
    ['0001ff', 'hex'], ['AbCd', 'HEX'], ['a', 'hex'], ['12x4', 'hex'], ['12é4', 'hex'], ['12\0a', 'hex'],
  ].map(([input, encoding]) => {
    const buffer = Buffer.from(input, encoding);
    assert(buffer instanceof Uint8Array && buffer instanceof Buffer && Buffer.isBuffer(buffer), 'typed array identity');
    return { input, encoding, bytes: Array.from(buffer), text: buffer.toString(encoding), byteLength: Buffer.byteLength(input, encoding) };
  });
  const backing = new ArrayBuffer(12);
  const source = new Uint8Array(backing, 3, 5);
  source.set([1, 2, 3, 4, 5]);
  const shared = Buffer.from(backing, 3, 5);
  const copied = Buffer.from(source);
  assert(shared.buffer === backing && shared.byteOffset === 3 && shared.length === 5, 'shared backing and offset');
  assert(shared.parent === backing && shared.offset === 3, 'parent and offset aliases');
  assert(copied.buffer !== backing && copied.toString('hex') === '0102030405', 'copy visible source bytes');
  for (const name of ['slice', 'subarray']) {
    const slice = shared[name](1, -1);
    assert(Buffer.isBuffer(slice) && slice.buffer === backing && slice.byteOffset === 4, 'shared slice');
    slice[0] = 77;
    assert(shared[1] === 77 && copied[1] === 2, 'view mutation and copy independence');
    shared[1] = 2;
  }
  for (const name of ['map', 'filter']) {
    const result = shared[name](x => x);
    assert(Buffer.isBuffer(result) && result.buffer !== backing, 'species copy');
  }
  assert(Buffer.alloc(3, 261).toString('hex') === '050505', 'numeric fill');
  assert(Buffer.alloc(0).length === 0, 'empty allocation');
  const errors = [];
  for (const [operation, expected] of [
    [() => Buffer.alloc(-1), 'ERR_OUT_OF_RANGE'],
    [() => Buffer.alloc(MAX_LENGTH + 1), 'ERR_OUT_OF_RANGE'],
    [() => Buffer.alloc('2'), 'ERR_INVALID_ARG_TYPE'],
    [() => Buffer.from('x', 'imaginary'), 'ERR_UNKNOWN_ENCODING'],
    [() => Buffer.from(backing, 100), 'ERR_BUFFER_OUT_OF_BOUNDS'],
  ]) {
    try { operation(); throw new Error('missing error'); }
    catch (error) { assert(error.code === expected, 'error code ' + expected); errors.push(error.code); }
  }
  refusal(() => Buffer.from([1, 2]));
  refusal(() => Buffer.from('SGVsbG8=', 'base64'));
  refusal(() => Buffer.allocUnsafe(1));
  refusal(() => shared.readUInt8(0));
  refusal(() => profile.Blob());
  const malformedText = Buffer.from(new Uint8Array([0xc0, 0xaf, 0xef, 0xbb, 0xbf])).toString();
  return JSON.stringify({ calls: ++calls, kernel: 'JS reference test double; native kernel uncompiled', snapshotText: snapshotBuffer.toString(), cases, malformedText, errors, ownershipChecks: 8 });
}
