// Only ordinary public bindings are used. The dedicated debug engine selects
// the four first-use allocation faults; this component cannot arm/reset them.
import bufferDefault, { Buffer } from 'node:buffer';
import { spawn } from 'node:child_process';

function check(condition, description) {
  if (!condition) throw new Error(description);
}
const input = Array.from({ length: 64 }, (_, i) => (i * 17 + 11) & 255);
const hex = input.map(value => value.toString(16).padStart(2, '0')).join('');
const snapshotBuffer = Buffer.from(new Uint8Array(input));
const snapshotBacking = snapshotBuffer.buffer;
const snapshotView = snapshotBuffer.subarray(7, 39);
const independentCopy = Buffer.from(snapshotBuffer);
// Successful kernel calls during componentization prove that deployed-only
// faults are not armed in snapshot initialization. Keep both results alive.
const snapshotDecoded = Buffer.from(hex, 'hex');
const snapshotEncoded = snapshotBuffer.toString('hex');
check(snapshotEncoded === hex, 'snapshot hex encode');
let calls = 0;
let completedFirstCallBits = 0;

function intact() {
  check(bufferDefault.Buffer === Buffer && globalThis.Buffer === Buffer, 'native module identities');
  check(Buffer.isBuffer(snapshotBuffer) && Buffer.isBuffer(snapshotView) && Buffer.isBuffer(snapshotDecoded),
    'private brands survived failure/resumption');
  check(snapshotBuffer.buffer === snapshotBacking && snapshotView.buffer === snapshotBacking,
    'live backing identity');
  check(snapshotView.byteOffset === snapshotBuffer.byteOffset + 7 && snapshotView.length === 32,
    'live view offsets');
  check(independentCopy.buffer !== snapshotBacking, 'copy backing remained independent');
  check(snapshotEncoded === hex, 'retained snapshot string');
  for (let i = 0; i < input.length; i++) {
    check(snapshotBuffer[i] === input[i], 'live source contents');
    check(independentCopy[i] === input[i], 'live copy contents');
    check(snapshotDecoded[i] === input[i], 'retained snapshot decode');
    if (i >= 7 && i < 39) check(snapshotView[i - 7] === input[i], 'live view contents');
  }
}

function outOfMemory(operation, point) {
  let caught = false;
  try { operation(); }
  catch (error) {
    caught = true;
    // SpiderMonkey's preallocated OOM exception is a primitive string in this
    // pin. This tests the actual JS-visible value, not a fabricated Error code.
    check(typeof error === 'string' && error === 'out of memory', point + ': genuine OOM exception');
  }
  check(caught, point + ': selected native allocator did not fail');
  intact();
  return point;
}

export function run() {
  let stage = 1;
  try {
    intact();
    let bits = 3 | completedFirstCallBits; // Snapshot results and initial integrity.
    const faults = [];
    if (calls === 0) {
      stage = 2;
      faults.push(outOfMemory(() => Buffer.from(hex, 'hex'), 'decode-utf8-staging'));
      bits |= 4;
      stage = 3;
      faults.push(outOfMemory(() => Buffer.from(hex, 'hex'), 'decode-uint8array'));
      bits |= 8;
      stage = 4;
      const recoveredDecode = Buffer.from(hex, 'hex');
      check(recoveredDecode.length === input.length, 'decode recovered');
      for (let i = 0; i < input.length; i++) check(recoveredDecode[i] === input[i], 'decode recovery contents');
      bits |= 64;
      stage = 5;
      faults.push(outOfMemory(() => snapshotBuffer.toString('hex'), 'encode-malloc-staging'));
      bits |= 16;
      stage = 6;
      faults.push(outOfMemory(() => snapshotBuffer.toString('hex'), 'encode-js-string'));
      bits |= 32;
      check(faults.length === 4, 'all four actual faults completed');
      completedFirstCallBits = bits & 124;
    }
    // Both kernels remain usable after all simulator scopes have reset, and
    // repeated exported calls use the same resumed instance without new faults.
    stage = 7;
    for (let i = 0; i < 32; i++) {
      const recovered = Buffer.from(hex, 'hex');
      check(recovered.toString('hex') === hex, 'repeated allocation/recovery');
    }
    bits |= 128;
    stage = 8;
    let unsupported = false;
    try { spawn('ignored'); }
    catch (error) { unsupported = error instanceof Error && error.code === 'ERR_SM_NODE_UNSUPPORTED'; }
    check(unsupported, 'unsupported operation distinct from OOM');
    bits |= 256;
    stage = 9;
    let bounded = false;
    try { Buffer.alloc(16 * 1024 * 1024 + 1); }
    catch (error) { bounded = error instanceof RangeError && error.code === 'ERR_OUT_OF_RANGE'; }
    check(bounded, 'profile allocation bound distinct from allocator OOM');
    bits |= 512;
    stage = 10;
    intact();
    bits |= 1024;
    calls++;
    // Only the test result carrier changes. DEBUG ComponentizeJS indirect
    // canonical memory bindings are unavailable; the scalar s32 path is safe.
    return (calls << 16) | bits;
  } catch (error) {
    return -stage;
  }
}
