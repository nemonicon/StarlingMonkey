import coreExpectations from 'node-compat:core-expectations';
// Guest-safe checks against the ACTUAL registered native module. No facade
// factory, reference kernel, Node assert shim or replacement Buffer is loaded.
export function checkCapturedIntrinsics(module) {
  const { Buffer } = module;
  const U8 = Uint8Array;
  const AB = ArrayBuffer;
  const setPrototypeOf = Object.setPrototypeOf;
  function check(value, message) { if (!value) throw new Error(message); }
  function equal(actual, expected, message) { check(Object.is(actual, expected), message); }
  function bytes(actual, expected, message) {
    equal(actual.length, expected.length, message + ' length');
    for (let i = 0; i < expected.length; i++) equal(actual[i], expected[i], message + ' byte ' + i);
  }
  function unsupported(call, operation) {
    try { call(); } catch (error) {
      equal(error.code, 'ERR_SM_NODE_UNSUPPORTED', 'unsupported code');
      equal(error.module, 'node:buffer', 'unsupported module');
      equal(error.profile, coreExpectations.coreVersion, 'unsupported profile');
      if (operation) equal(error.operation, operation, 'unsupported operation');
      return;
    }
    throw new Error('Excluded operation unexpectedly returned');
  }
  for (const size of [0, 1, 63, 64, 65, 255, 256, 4096]) {
    const input = U8.from({ length: size }, (_, i) => i & 255);
    const copy = Buffer.from(input);
    bytes(copy, input, 'copy visible bytes');
    check(Buffer.isBuffer(copy) && copy instanceof Buffer && copy instanceof U8, 'genuine privately branded typed array');
    // Access backing storage only when the application observes it. Trusted
    // construction must preserve the same resulting AB relationships.
    check(copy.buffer !== input.buffer, 'copy has independent backing');
    equal(copy.byteOffset, 0, 'copy offset');
    equal(copy.buffer.byteLength, size, 'on-demand backing length');
    for (const method of ['map', 'filter']) {
      const derived = copy[method](method === 'map' ? value => value : () => true);
      check(Buffer.isBuffer(derived) && derived.buffer !== copy.buffer, 'species copy brand/backing');
      bytes(derived, copy, 'species values');
    }
    for (const method of ['slice', 'subarray']) {
      const view = copy[method](0, size);
      check(Buffer.isBuffer(view) && view.buffer === copy.buffer, 'shared view brand/backing');
      equal(view.byteOffset, copy.byteOffset, 'shared view offset');
    }
  }
  const fake = Object.create(U8.prototype);
  const wrongKind = new Uint16Array([1, 2]);
  setPrototypeOf(wrongKind, U8.prototype);
  for (const value of [fake, wrongKind, new Proxy(new U8(2), {})]) {
    unsupported(() => Buffer.from(value), 'invalid Uint8Array');
    equal(Buffer.isBuffer(value), false, 'input spoof cannot acquire private brand');
  }
  const backingKinds = [];
  if (typeof SharedArrayBuffer === 'function') {
    const shared = new SharedArrayBuffer(8);
    unsupported(() => Buffer.from(shared));
    unsupported(() => Buffer.from(new U8(shared)), 'shared or invalid ArrayBuffer');
    unsupported(() => new Buffer[Symbol.species](shared), 'shared or invalid ArrayBuffer');
    backingKinds.push('shared-rejected');
  }
  const resizable = new AB(8, { maxByteLength: 16 });
  if (resizable.resizable === true) {
    unsupported(() => Buffer.from(resizable), 'resizable ArrayBuffer');
    unsupported(() => Buffer.from(new U8(resizable)), 'resizable ArrayBuffer');
    unsupported(() => new Buffer[Symbol.species](resizable), 'resizable ArrayBuffer');
    backingKinds.push('resizable-rejected');
  }
  if (typeof structuredClone === 'function') {
    const detached = new AB(8);
    const detachedView = new U8(detached);
    structuredClone(detached, { transfer: [detached] });
    unsupported(() => Buffer.from(detached), 'detached ArrayBuffer');
    unsupported(() => Buffer.from(detachedView), 'detached ArrayBuffer');
    backingKinds.push('detached-rejected');
  }
  const shadowed = new U8([1, 2, 3]);
  for (const name of ['buffer', 'byteLength', 'byteOffset', 'length']) {
    Object.defineProperty(shadowed, name, { get() { throw new Error('read public input ' + name); } });
  }
  bytes(Buffer.from(shadowed), [1, 2, 3], 'external properties cannot substitute for slots');
  try { new Buffer[Symbol.species](16777217); throw new Error('species limit unexpectedly accepted'); }
  catch (error) { equal(error.code, 'ERR_OUT_OF_RANGE', 'species allocation limit'); }

  const originals = {
    encode: TextEncoder.prototype.encode, decode: TextDecoder.prototype.decode,
    fill: U8.prototype.fill, add: WeakSet.prototype.add, has: WeakSet.prototype.has,
    setPrototypeOf: Object.setPrototypeOf,
  };
  let replacedCalls = 0;
  try {
    TextEncoder.prototype.encode = () => { replacedCalls++; return new U8(resizable); };
    TextDecoder.prototype.decode = () => { replacedCalls++; return 'replaced'; };
    U8.prototype.fill = () => { replacedCalls++; throw new Error('replaced fill'); };
    WeakSet.prototype.add = () => { replacedCalls++; throw new Error('replaced private brand'); };
    WeakSet.prototype.has = () => { replacedCalls++; return true; };
    Object.setPrototypeOf = () => { replacedCalls++; throw new Error('replaced prototype installation'); };
    const allocated = Buffer.alloc(64, 261);
    bytes(allocated, Array(64).fill(5), 'captured numeric fill');
    check(Buffer.isBuffer(allocated), 'captured private add/has');
    equal(Buffer.isBuffer(new U8(1)), false, 'poisoned has cannot spoof Uint8Array brand');
    equal(Buffer.isBuffer(Object.create(Buffer.prototype)), false, 'poisoned has cannot spoof prototype brand');
    const text = Buffer.from('\ufeffé😀', 'utf8');
    equal(text.toString(), '\ufeffé😀', 'captured native encoder/decoder');
    bytes(Buffer.from('00ff', 'hex'), [0, 255], 'private native hex producer');
    bytes(Buffer.from(new U8([4, 5])), [4, 5], 'captured trusted copy tagging');
    equal(replacedCalls, 0, 'public replacements were not invoked');
  } finally {
    TextEncoder.prototype.encode = originals.encode;
    TextDecoder.prototype.decode = originals.decode;
    U8.prototype.fill = originals.fill;
    WeakSet.prototype.add = originals.add;
    WeakSet.prototype.has = originals.has;
    Object.setPrototypeOf = originals.setPrototypeOf;
  }
  equal(module.Buffer, module.default.Buffer, 'default Buffer identity after mutations');
  equal(Object.getPrototypeOf(Buffer), U8, 'constructor inheritance retained');
  equal(Buffer.BYTES_PER_ELEMENT, 1, 'element size retained');
  return { nativeModule: true, sizesChecked: 8, inputSpoofsRejected: 3, publicInputShadowsChecked: 4,
    backingKinds, sharedConstructionAvailable: typeof SharedArrayBuffer === 'function', publicReplacementCalls: replacedCalls,
    capturedProducerAndBrandChecksPassed: true };
}
