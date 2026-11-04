// UNINSTALLED source template. No module registration or host imports.
import {constants, codes} from './constant-data.generated.mjs';

const MAX_INPUT = 1024 * 1024;
const MAX_OUTPUT = 16 * 1024 * 1024;
const PROFILE = 'sm-node-22.14.0-zlib-facade-template-v1';

// This factory is an internal integration input, not the node:zlib namespace.
// The future native installer must publish the returned finite binding record
// through the existing Engine::define_builtin_module mechanism.
export function createZlibModule(kernel, Buffer, web = globalThis) {
  const U8 = web.Uint8Array;
  const typed = Object.getPrototypeOf(U8.prototype);
  const getter = (prototype, key) => Object.getOwnPropertyDescriptor(prototype, key)?.get;
  const call = Function.prototype.call.bind(Function.prototype.call);
  const typedBuffer = getter(typed, 'buffer');
  const typedLength = getter(typed, 'byteLength');
  const typedOffset = getter(typed, 'byteOffset');
  const dataBuffer = getter(web.DataView.prototype, 'buffer');
  const dataLength = getter(web.DataView.prototype, 'byteLength');
  const dataOffset = getter(web.DataView.prototype, 'byteOffset');
  const abLength = getter(web.ArrayBuffer.prototype, 'byteLength');
  const abResizable = getter(web.ArrayBuffer.prototype, 'resizable');
  const abDetached = getter(web.ArrayBuffer.prototype, 'detached');
  const sabLength = web.SharedArrayBuffer && getter(web.SharedArrayBuffer.prototype, 'byteLength');
  const getPrototype = Object.getPrototypeOf;
  const descriptors = Object.getOwnPropertyDescriptors;
  const ownKeys = Reflect.ownKeys;
  const objectPrototype = Object.prototype;
  const bufferFrom = Buffer.from.bind(Buffer);
  const run = kernel.run.bind(kernel);

  function fail(Ctor, code, operation, message) {
    const error = new Ctor(message);
    Object.assign(error, {code, module: 'node:zlib', operation, profile: PROFILE});
    throw error;
  }
  function unsupported(operation) {
    fail(Error, 'ERR_SM_NODE_UNSUPPORTED', operation, `Unsupported bounded node:zlib operation: ${operation}`);
  }
  function probe(accessor, value) {
    try { return {ok: true, value: call(accessor, value)}; }
    catch { return {ok: false}; }
  }
  function fixed(buffer, operation) {
    const size = probe(abLength, buffer);
    if (!size.ok) unsupported(`${operation}: shared backing`);
    if (abResizable && call(abResizable, buffer)) unsupported(`${operation}: resizable backing`);
    if (abDetached && call(abDetached, buffer)) unsupported(`${operation}: detached backing`);
    // Also works on engines without ArrayBuffer.prototype.detached.
    try { new U8(buffer, 0, 0); }
    catch { unsupported(`${operation}: detached backing`); }
    return size.value;
  }
  function bytes(input, operation) {
    if (typeof input === 'string') unsupported(`${operation}: string input`);
    if (sabLength && probe(sabLength, input).ok) unsupported(`${operation}: shared backing`);
    const ab = probe(abLength, input);
    if (ab.ok) {
      const length = fixed(input, operation);
      if (length > MAX_INPUT) fail(RangeError, 'ERR_OUT_OF_RANGE', operation, 'Input exceeds 1 MiB');
      return new U8(input, 0, length);
    }
    let view = probe(typedBuffer, input), length, offset;
    if (view.ok) {
      fixed(view.value, operation);
      length = call(typedLength, input);
      offset = call(typedOffset, input);
    } else {
      view = probe(dataBuffer, input);
      if (!view.ok) fail(TypeError, 'ERR_INVALID_ARG_TYPE', operation, 'Input must be an ArrayBuffer or ArrayBufferView');
      fixed(view.value, operation);
      length = call(dataLength, input);
      offset = call(dataOffset, input);
    }
    if (length > MAX_INPUT) fail(RangeError, 'ERR_OUT_OF_RANGE', operation, 'Input exceeds 1 MiB');
    return new U8(view.value, offset, length);
  }
  function outputLimit(options, operation) {
    if (options === undefined) return MAX_OUTPUT;
    if (options === null || typeof options !== 'object')
      fail(TypeError, 'ERR_INVALID_ARG_TYPE', operation, 'Options must be an ordinary record');
    const prototype = getPrototype(options);
    if (prototype !== null && prototype !== objectPrototype) unsupported(`${operation}: options prototype`);
    // Only own data properties are admitted. Unknown properties, accessors and
    // symbols are explicit refusals. Reflective Proxy traps may still run;
    // arbitrary proxies are outside this ordinary-record contract.
    const properties = descriptors(options);
    let limit = MAX_OUTPUT;
    for (const key of ownKeys(properties)) {
      if (key !== 'maxOutputLength') unsupported(`${operation}: option ${String(key)}`);
      const descriptor = properties[key];
      if (!Object.hasOwn(descriptor, 'value')) unsupported(`${operation}: accessor option`);
      const value = descriptor.value;
      if (value === undefined) continue;
      if (typeof value !== 'number') fail(TypeError, 'ERR_INVALID_ARG_TYPE', operation, 'maxOutputLength must be a number');
      if (!Number.isInteger(value) || value < 1 || value > MAX_OUTPUT)
        fail(RangeError, 'ERR_OUT_OF_RANGE', operation, 'maxOutputLength must be an integer between 1 and 16 MiB');
      limit = value;
    }
    return limit;
  }
  function sync(input, options, operation, format, encode) {
    const limit = outputLimit(options, operation);
    const source = bytes(input, operation);
    // C++ stages input, owns codec allocations, and returns a fresh JS-owned
    // Uint8Array only after success. Native partial output is never exposed.
    const result = run(source, format, encode, limit);
    const buffer = call(typedBuffer, result);
    const length = call(typedLength, result);
    const offset = call(typedOffset, result);
    fixed(buffer, operation);
    if (length > limit) fail(Error, 'ERR_SM_ZLIB_INTERNAL', operation, 'Private kernel exceeded output limit');
    // Existing Buffer.from(ArrayBuffer, offset, length) shares this fresh
    // JS-owned backing; the facade introduces no further byte copy.
    return bufferFrom(buffer, offset, length);
  }
  function deflateSync(input, options) {
    if (new.target) unsupported('new deflateSync');
    return sync(input, options, 'deflateSync', 0, true);
  }
  function inflateSync(input, options) {
    if (new.target) unsupported('new inflateSync');
    return sync(input, options, 'inflateSync', 0, false);
  }
  function gzipSync(input, options) {
    if (new.target) unsupported('new gzipSync');
    return sync(input, options, 'gzipSync', 1, true);
  }
  function gunzipSync(input, options) {
    if (new.target) unsupported('new gunzipSync');
    return sync(input, options, 'gunzipSync', 1, false);
  }
  function deflateRawSync(input, options) {
    if (new.target) unsupported('new deflateRawSync');
    return sync(input, options, 'deflateRawSync', 2, true);
  }
  function inflateRawSync(input, options) {
    if (new.target) unsupported('new inflateRawSync');
    return sync(input, options, 'inflateRawSync', 2, false);
  }
  // Explicit named declarations and the finite record are generated solely
  // from the pinned Node22 inventory. No blank namespace or Proxy fallback.
  function BrotliCompress() { unsupported('BrotliCompress'); }
  function BrotliDecompress() { unsupported('BrotliDecompress'); }
  function Deflate() { unsupported('Deflate'); }
  function DeflateRaw() { unsupported('DeflateRaw'); }
  function Gunzip() { unsupported('Gunzip'); }
  function Gzip() { unsupported('Gzip'); }
  function Inflate() { unsupported('Inflate'); }
  function InflateRaw() { unsupported('InflateRaw'); }
  function Unzip() { unsupported('Unzip'); }
  function brotliCompress() { unsupported('brotliCompress'); }
  function brotliCompressSync() { unsupported('brotliCompressSync'); }
  function brotliDecompress() { unsupported('brotliDecompress'); }
  function brotliDecompressSync() { unsupported('brotliDecompressSync'); }
  function crc32() { unsupported('crc32'); }
  function createBrotliCompress() { unsupported('createBrotliCompress'); }
  function createBrotliDecompress() { unsupported('createBrotliDecompress'); }
  function createDeflate() { unsupported('createDeflate'); }
  function createDeflateRaw() { unsupported('createDeflateRaw'); }
  function createGunzip() { unsupported('createGunzip'); }
  function createGzip() { unsupported('createGzip'); }
  function createInflate() { unsupported('createInflate'); }
  function createInflateRaw() { unsupported('createInflateRaw'); }
  function createUnzip() { unsupported('createUnzip'); }
  function deflate() { unsupported('deflate'); }
  function deflateRaw() { unsupported('deflateRaw'); }
  function gunzip() { unsupported('gunzip'); }
  function gzip() { unsupported('gzip'); }
  function inflate() { unsupported('inflate'); }
  function inflateRaw() { unsupported('inflateRaw'); }
  function unzip() { unsupported('unzip'); }
  function unzipSync() { unsupported('unzipSync'); }
  const root = {BrotliCompress, BrotliDecompress, Deflate, DeflateRaw, Gunzip, Gzip, Inflate, InflateRaw, Unzip, brotliCompress, brotliCompressSync, brotliDecompress, brotliDecompressSync, codes, constants, crc32, createBrotliCompress, createBrotliDecompress, createDeflate, createDeflateRaw, createGunzip, createGzip, createInflate, createInflateRaw, createUnzip, deflate, deflateRaw, deflateRawSync, deflateSync, gunzip, gunzipSync, gzip, gzipSync, inflate, inflateRaw, inflateRawSync, inflateSync, unzip, unzipSync};
  for (const key of Object.keys(constants)) if (!key.startsWith('BROTLI'))
    Object.defineProperty(root, key, {value: constants[key], enumerable: false});
  Object.freeze(root);
  return Object.freeze({default: root, BrotliCompress, BrotliDecompress, Deflate, DeflateRaw, Gunzip, Gzip, Inflate, InflateRaw, Unzip, brotliCompress, brotliCompressSync, brotliDecompress, brotliDecompressSync, codes, constants, crc32, createBrotliCompress, createBrotliDecompress, createDeflate, createDeflateRaw, createGunzip, createGzip, createInflate, createInflateRaw, createUnzip, deflate, deflateRaw, deflateRawSync, deflateSync, gunzip, gunzipSync, gzip, gzipSync, inflate, inflateRaw, inflateRawSync, inflateSync, unzip, unzipSync});
}
