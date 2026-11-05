// Generated unapplied bounded zlib proposal; do not edit.
// Canonical-source SHA-256: 5778767523bd6492367cd28ab86f73537cdcfd91615aed5d387f24b74ebc6478
static constexpr const char kZlibFactorySource[] = R"SM_NODE_PROFILE((function(argument){
'use strict';
// Node baseline shape with a private native-backend version overlay.
// No guest version value is selected by this source proposal.
function createZlibData(backend) {
  if (!backend || typeof backend.headerVersion !== 'string' ||
      backend.headerVersion.length === 0 || backend.runtimeVersion !== backend.headerVersion ||
      !Number.isInteger(backend.vernum) || backend.vernum <= 0 || backend.vernum > 0x7fffffff) {
    const error = new Error('Unverified bounded zlib backend');
    Object.defineProperty(error, 'code', {value:'ERR_SM_ZLIB_BACKEND_MISMATCH', enumerable:true});
    throw error;
  }
  const constants = Object.freeze(Object.assign(Object.create(null), {"Z_NO_FLUSH":0,"Z_PARTIAL_FLUSH":1,"Z_SYNC_FLUSH":2,"Z_FULL_FLUSH":3,"Z_FINISH":4,"Z_BLOCK":5,"Z_OK":0,"Z_STREAM_END":1,"Z_NEED_DICT":2,"Z_ERRNO":-1,"Z_STREAM_ERROR":-2,"Z_DATA_ERROR":-3,"Z_MEM_ERROR":-4,"Z_BUF_ERROR":-5,"Z_VERSION_ERROR":-6,"Z_NO_COMPRESSION":0,"Z_BEST_SPEED":1,"Z_BEST_COMPRESSION":9,"Z_DEFAULT_COMPRESSION":-1,"Z_FILTERED":1,"Z_HUFFMAN_ONLY":2,"Z_RLE":3,"Z_FIXED":4,"Z_DEFAULT_STRATEGY":0,"ZLIB_VERNUM":backend.vernum,"DEFLATE":1,"INFLATE":2,"GZIP":3,"GUNZIP":4,"DEFLATERAW":5,"INFLATERAW":6,"UNZIP":7,"BROTLI_DECODE":8,"BROTLI_ENCODE":9,"Z_MIN_WINDOWBITS":8,"Z_MAX_WINDOWBITS":15,"Z_DEFAULT_WINDOWBITS":15,"Z_MIN_CHUNK":64,"Z_MAX_CHUNK":Infinity,"Z_DEFAULT_CHUNK":16384,"Z_MIN_MEMLEVEL":1,"Z_MAX_MEMLEVEL":9,"Z_DEFAULT_MEMLEVEL":8,"Z_MIN_LEVEL":-1,"Z_MAX_LEVEL":9,"Z_DEFAULT_LEVEL":-1,"BROTLI_OPERATION_PROCESS":0,"BROTLI_OPERATION_FLUSH":1,"BROTLI_OPERATION_FINISH":2,"BROTLI_OPERATION_EMIT_METADATA":3,"BROTLI_PARAM_MODE":0,"BROTLI_MODE_GENERIC":0,"BROTLI_MODE_TEXT":1,"BROTLI_MODE_FONT":2,"BROTLI_DEFAULT_MODE":0,"BROTLI_PARAM_QUALITY":1,"BROTLI_MIN_QUALITY":0,"BROTLI_MAX_QUALITY":11,"BROTLI_DEFAULT_QUALITY":11,"BROTLI_PARAM_LGWIN":2,"BROTLI_MIN_WINDOW_BITS":10,"BROTLI_MAX_WINDOW_BITS":24,"BROTLI_LARGE_MAX_WINDOW_BITS":30,"BROTLI_DEFAULT_WINDOW":22,"BROTLI_PARAM_LGBLOCK":3,"BROTLI_MIN_INPUT_BLOCK_BITS":16,"BROTLI_MAX_INPUT_BLOCK_BITS":24,"BROTLI_PARAM_DISABLE_LITERAL_CONTEXT_MODELING":4,"BROTLI_PARAM_SIZE_HINT":5,"BROTLI_PARAM_LARGE_WINDOW":6,"BROTLI_PARAM_NPOSTFIX":7,"BROTLI_PARAM_NDIRECT":8,"BROTLI_DECODER_RESULT_ERROR":0,"BROTLI_DECODER_RESULT_SUCCESS":1,"BROTLI_DECODER_RESULT_NEEDS_MORE_INPUT":2,"BROTLI_DECODER_RESULT_NEEDS_MORE_OUTPUT":3,"BROTLI_DECODER_PARAM_DISABLE_RING_BUFFER_REALLOCATION":0,"BROTLI_DECODER_PARAM_LARGE_WINDOW":1,"BROTLI_DECODER_NO_ERROR":0,"BROTLI_DECODER_SUCCESS":1,"BROTLI_DECODER_NEEDS_MORE_INPUT":2,"BROTLI_DECODER_NEEDS_MORE_OUTPUT":3,"BROTLI_DECODER_ERROR_FORMAT_EXUBERANT_NIBBLE":-1,"BROTLI_DECODER_ERROR_FORMAT_RESERVED":-2,"BROTLI_DECODER_ERROR_FORMAT_EXUBERANT_META_NIBBLE":-3,"BROTLI_DECODER_ERROR_FORMAT_SIMPLE_HUFFMAN_ALPHABET":-4,"BROTLI_DECODER_ERROR_FORMAT_SIMPLE_HUFFMAN_SAME":-5,"BROTLI_DECODER_ERROR_FORMAT_CL_SPACE":-6,"BROTLI_DECODER_ERROR_FORMAT_HUFFMAN_SPACE":-7,"BROTLI_DECODER_ERROR_FORMAT_CONTEXT_MAP_REPEAT":-8,"BROTLI_DECODER_ERROR_FORMAT_BLOCK_LENGTH_1":-9,"BROTLI_DECODER_ERROR_FORMAT_BLOCK_LENGTH_2":-10,"BROTLI_DECODER_ERROR_FORMAT_TRANSFORM":-11,"BROTLI_DECODER_ERROR_FORMAT_DICTIONARY":-12,"BROTLI_DECODER_ERROR_FORMAT_WINDOW_BITS":-13,"BROTLI_DECODER_ERROR_FORMAT_PADDING_1":-14,"BROTLI_DECODER_ERROR_FORMAT_PADDING_2":-15,"BROTLI_DECODER_ERROR_FORMAT_DISTANCE":-16,"BROTLI_DECODER_ERROR_DICTIONARY_NOT_SET":-19,"BROTLI_DECODER_ERROR_INVALID_ARGUMENTS":-20,"BROTLI_DECODER_ERROR_ALLOC_CONTEXT_MODES":-21,"BROTLI_DECODER_ERROR_ALLOC_TREE_GROUPS":-22,"BROTLI_DECODER_ERROR_ALLOC_CONTEXT_MAP":-25,"BROTLI_DECODER_ERROR_ALLOC_RING_BUFFER_1":-26,"BROTLI_DECODER_ERROR_ALLOC_RING_BUFFER_2":-27,"BROTLI_DECODER_ERROR_ALLOC_BLOCK_TYPE_TREES":-30,"BROTLI_DECODER_ERROR_UNREACHABLE":-31}));
  const codes = Object.freeze(Object.assign(Object.create(null), {"0":"Z_OK","1":"Z_STREAM_END","2":"Z_NEED_DICT","Z_OK":0,"Z_STREAM_END":1,"Z_NEED_DICT":2,"Z_ERRNO":-1,"Z_STREAM_ERROR":-2,"Z_DATA_ERROR":-3,"Z_MEM_ERROR":-4,"Z_BUF_ERROR":-5,"Z_VERSION_ERROR":-6,"-1":"Z_ERRNO","-2":"Z_STREAM_ERROR","-3":"Z_DATA_ERROR","-4":"Z_MEM_ERROR","-5":"Z_BUF_ERROR","-6":"Z_VERSION_ERROR"}));
  return Object.freeze({constants, codes});
}

// UNINSTALLED source template. No module registration or host imports.


const MAX_INPUT = 1024 * 1024;
const MAX_OUTPUT = 16 * 1024 * 1024;
const PROFILE = 'sm-node-22.14.0-m0.13';

// This factory is an internal integration input, not the node:zlib namespace.
// The future native installer must publish the returned finite binding record
// through the existing Engine::define_builtin_module mechanism.
function createZlibModule(kernel, Buffer, web = globalThis) {
  const {constants, codes} = createZlibData(kernel.backendInfo());
  const U8 = web.Uint8Array;
  const {Error, TypeError, RangeError} = web;
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
  const defineProperties = Object.defineProperties;
  const hasOwn = Object.hasOwn;
  const isInteger = Number.isInteger;
  const stringify = String;
  const bufferFrom = Buffer.from.bind(Buffer);
  const run = kernel.run.bind(kernel);

  function fail(Ctor, code, operation, message) {
    const error = new Ctor(message);
    defineProperties(error, {
      code: {__proto__: null, value: code, writable: true, configurable: true, enumerable: true},
      module: {__proto__: null, value: 'node:zlib', writable: true, configurable: true, enumerable: true},
      operation: {__proto__: null, value: operation, writable: true, configurable: true, enumerable: true},
      profile: {__proto__: null, value: PROFILE, writable: true, configurable: true, enumerable: true},
    });
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
      if (key !== 'maxOutputLength') unsupported(`${operation}: option ${stringify(key)}`);
      const descriptor = properties[key];
      if (!hasOwn(descriptor, 'value')) unsupported(`${operation}: accessor option`);
      const value = descriptor.value;
      if (value === undefined) continue;
      if (typeof value !== 'number') fail(TypeError, 'ERR_INVALID_ARG_TYPE', operation, 'maxOutputLength must be a number');
      if (!isInteger(value) || value < 1 || value > MAX_OUTPUT)
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

return createZlibModule(argument.kernel, argument.Buffer);
}))SM_NODE_PROFILE";
