// Allocation/validation controls, NOT alternate public Buffer implementations.
// Pseudo-tagged outputs never acquire the production private WeakSet brand.
import { fullChecksum, fingerprint } from '../bench/workload.mjs';

export const operations = [
  'plain-copy', 'buffer-copy', 'weak-copy', 'prototype-copy',
  'buffer-weak-copy', 'buffer-prototype-copy', 'prototype-weak-copy',
  'buffer-prototype-weak-copy', 'source-checked-copy', 'output-checked-copy',
  'own-property-brand-copy', 'private-field-brand-copy',
  'both-checked-tagged-copy', 'source-checked-trusted-copy', 'native-copy', 'native-hex-decode',
  'intrinsic-hex-decode', 'intrinsic-hex-materialized', 'intrinsic-hex-checked-tag', 'intrinsic-hex-trusted-tag',
];

export function createProbes(Buffer, web = globalThis) {
  const U8 = web.Uint8Array;
  const typed = Object.getPrototypeOf(U8.prototype);
  const getBuffer = Object.getOwnPropertyDescriptor(typed, 'buffer').get;
  const getByteLength = Object.getOwnPropertyDescriptor(typed, 'byteLength').get;
  const getName = Object.getOwnPropertyDescriptor(typed, Symbol.toStringTag).get;
  const getABLength = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'byteLength').get;
  const getResizable = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'resizable')?.get;
  const getDetached = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'detached')?.get;
  const fromHex = U8.fromHex;
  const weakBrand = new WeakSet();
  const propertyBrand = Symbol('observable probe brand');
  class StampBase { constructor(object) { return object; } }
  class PrivateBrand extends StampBase {
    #brand = true;
    static stamp(object) { return new PrivateBrand(object); }
    static has(object) { return #brand in object; }
  }
  let invoke;
  function size(value) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 16777216 || !Number.isInteger(value)) throw new Error('invalid probe size');
    return value;
  }
  function backing(view) {
    if (getName.call(view) !== 'Uint8Array') throw new Error('invalid probe typed array');
    const buffer = getBuffer.call(view);
    const length = getABLength.call(buffer);
    if (getResizable?.call(buffer)) throw new Error('probe resizable excluded');
    if (getDetached?.call(buffer)) throw new Error('probe detached excluded');
    if (!getDetached && length === 0) new U8(buffer, 0, 0);
    return buffer;
  }
  function checked(view) { backing(view); size(getByteLength.call(view)); return view; }
  function trustedTag(view) { Object.setPrototypeOf(view, Buffer.prototype); weakBrand.add(view); return view; }
  const ascii = Array.from({ length: 95 }, (_, i) => String.fromCharCode(32 + ((i * 17 + 11) % 95))).join('');
  const hex = Array.from(ascii, c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');
  function setup(operation, length) {
    if (!operations.includes(operation) || ![64, 4096].includes(length)) throw new Error('unadmitted probe operation/length');
    const source = new U8(length);
    for (let i = 0; i < length; i++) source[i] = ascii.charCodeAt(i % 95);
    // All controls get the SAME already-materialized source, matching the
    // original benchmark's profile-Buffer source. Only output policy varies.
    getBuffer.call(source);
    if (operation === 'native-hex-decode' || operation.startsWith('intrinsic-hex-')) {
      const text = hex.repeat(Math.ceil(length / 95)).slice(0, 2 * length);
      if (operation === 'native-hex-decode') invoke = () => Buffer.from(text, 'hex');
      else invoke = () => {
        // Node22 lacks this intrinsic: only its untimed byte oracle falls
        // back to Node Buffer. The actual guest facts require native fromHex.
        const output = typeof fromHex === 'function' ? fromHex.call(U8, text) : Buffer.from(text, 'hex');
        if (operation === 'intrinsic-hex-materialized') getBuffer.call(output);
        if (operation === 'intrinsic-hex-checked-tag') trustedTag(checked(output));
        if (operation === 'intrinsic-hex-trusted-tag') trustedTag(output);
        return output;
      };
    } else if (operation === 'native-copy') invoke = () => Buffer.from(source);
    else if (operation === 'both-checked-tagged-copy') invoke = () => { checked(source); return trustedTag(checked(new U8(source))); };
    else if (operation === 'source-checked-trusted-copy') invoke = () => { checked(source); return trustedTag(new U8(source)); };
    else if (operation === 'source-checked-copy') invoke = () => { checked(source); return new U8(source); };
    else if (operation === 'output-checked-copy') invoke = () => checked(new U8(source));
    else if (operation === 'own-property-brand-copy') invoke = () => { const output = new U8(source); Object.defineProperty(output, propertyBrand, { value: true }); return output; };
    else if (operation === 'private-field-brand-copy') invoke = () => PrivateBrand.stamp(new U8(source));
    else {
      const materialize = operation.includes('buffer-');
      const weak = operation.includes('weak-');
      const prototype = operation.includes('prototype-');
      invoke = () => {
        const output = new U8(source);
        if (materialize) getBuffer.call(output);
        if (prototype) Object.setPrototypeOf(output, Buffer.prototype);
        if (weak) weakBrand.add(output);
        return output;
      };
    }
    const output = invoke();
    if (operation !== 'native-copy' && operation !== 'native-hex-decode' && Buffer.isBuffer(output)) {
      throw new Error('Probe unexpectedly acquired production private brand');
    }
    return fullChecksum(output) | 0;
  }
  function run(iterations) {
    if (!invoke || !Number.isInteger(iterations) || iterations < 1 || iterations > 1000000) throw new Error('invalid probe iterations');
    let sum = 0;
    for (let i = 0; i < iterations; i++) sum = (sum + (fingerprint(invoke()) ^ i)) >>> 0;
    return sum | 0;
  }
  function facts() {
    const spoof = Object.create(Buffer.prototype);
    const changed = new U8([1, 2]);
    Object.setPrototypeOf(changed, Buffer.prototype);
    const propertyTagged = new U8(1);
    Object.defineProperty(propertyTagged, propertyBrand, { value: true });
    const propertySpoof = new U8(1);
    propertySpoof[Reflect.ownKeys(propertyTagged).find(key => typeof key === 'symbol')] = true;
    const privateTagged = PrivateBrand.stamp(new U8(1));
    return JSON.stringify({
      capturedABDetached: !!getDetached, capturedABResizable: !!getResizable,
      uint8FromHex: typeof U8.fromHex, uint8ToHex: typeof U8.prototype.toHex,
      productionBrandRejectsPrototypeSpoof: !Buffer.isBuffer(spoof),
      productionBrandRejectsPseudoTaggedU8: !Buffer.isBuffer(changed),
      ownPropertyBrandObservableAndCopyable: Reflect.ownKeys(propertyTagged).includes(propertyBrand) && propertySpoof[propertyBrand] === true,
      privateStampRejectsSpoof: !PrivateBrand.has(changed),
      privateStampHasGenuineObject: PrivateBrand.has(privateTagged),
      privateStampAddsNoReflectableKey: Reflect.ownKeys(privateTagged).length === 1,
      scope: 'Factorial stage probes; control objects are Uint8Arrays, not supported alternate Buffers',
    });
  }
  return { setup, run, facts };
}
