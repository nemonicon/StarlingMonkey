// Executable SEMANTIC TEMPLATE, not production Buffer support.
// The injected kernel is native in the proposed component. Tests use an explicit
// reference kernel; passing those tests does not validate the C++ kernel.
import { unavailable, unsupported } from './unsupported.mjs';

export const MAX_LENGTH = 16 * 1024 * 1024;
export const MAX_STRING_LENGTH = 2 * MAX_LENGTH;
export const MAX_SOURCE_CODE_UNITS = 1024 * 1024;

export function createBufferModule(kernel, web = globalThis) {
  const U8 = web.Uint8Array;
  const AB = web.ArrayBuffer;
  const encoder = new web.TextEncoder();
  // Node preserves a leading UTF-8 BOM in Buffer.toString().
  const decoder = new web.TextDecoder('utf-8', { ignoreBOM: true });
  const instances = new WeakSet();
  const reject = operation => unsupported('node:buffer', operation);
  function fail(Ctor, code, message) {
    const error = new Ctor(message);
    error.code = code;
    throw error;
  }
  function size(value) {
    if (typeof value !== 'number') fail(TypeError, 'ERR_INVALID_ARG_TYPE', 'size must be a number');
    if (!Number.isFinite(value) || value < 0 || value > MAX_LENGTH) {
      fail(RangeError, 'ERR_OUT_OF_RANGE', `size must be between 0 and ${MAX_LENGTH}`);
    }
    if (!Number.isInteger(value)) reject('fractional size');
    return value;
  }
  function sourceLimit(value) {
    if (value.length > MAX_SOURCE_CODE_UNITS) {
      fail(RangeError, 'ERR_OUT_OF_RANGE', 'source exceeds profile code-unit limit');
    }
  }
  function encoding(value = 'utf8') {
    if (typeof value !== 'string') reject('non-string encoding');
    const result = value.toLowerCase();
    if (result === 'utf8' || result === 'utf-8' || result === '') return 'utf8';
    if (result === 'hex') return result;
    if (['ascii', 'latin1', 'binary', 'base64', 'base64url', 'ucs2', 'ucs-2', 'utf16le', 'utf-16le'].includes(result)) {
      reject(`encoding:${result}`);
    }
    fail(TypeError, 'ERR_UNKNOWN_ENCODING', `Unknown encoding: ${value}`);
  }
  function tag(view) {
    size(view.byteLength);
    Object.setPrototypeOf(view, Buffer.prototype);
    instances.add(view);
    return view;
  }
  function requireBuffer(value) {
    if (!instances.has(value)) fail(TypeError, 'ERR_INVALID_ARG_TYPE', 'receiver must be a profile Buffer');
  }
  // A genuine typed-array allocation, including for TypedArray species methods.
  function FastBuffer(...args) {
    if (typeof args[0] === 'number') size(args[0]);
    return tag(new U8(...args));
  }
  function Buffer(arg, encodingOrOffset, length) {
    reject('Buffer constructor');
  }
  Buffer.prototype = Object.create(U8.prototype, {
    constructor: { value: Buffer, writable: true, configurable: true },
  });
  Object.setPrototypeOf(Buffer, U8);
  Object.defineProperty(Buffer, Symbol.species, { value: FastBuffer });
  Object.defineProperty(Buffer, 'poolSize', { value: 0, writable: true, enumerable: true });
  Buffer.alloc = function alloc(length, fill = 0) {
    size(length);
    if (typeof fill !== 'number') reject('alloc non-number fill');
    const value = tag(new U8(length));
    U8.prototype.fill.call(value, fill);
    return value;
  };
  Buffer.from = function from(value, encodingOrOffset, length) {
    if (typeof value === 'string') {
      sourceLimit(value);
      return tag(encoding(encodingOrOffset) === 'hex' ? kernel.hexDecode(value) : encoder.encode(value));
    }
    if (value instanceof AB) {
      if (value.resizable === true) reject('resizable ArrayBuffer');
      // Only integer nonnegative offsets/lengths are in the supported contract.
      const offset = encodingOrOffset === undefined ? 0 : encodingOrOffset;
      if (typeof offset !== 'number' || !Number.isInteger(offset) || offset < 0) reject('ArrayBuffer offset coercion');
      if (offset > value.byteLength) fail(RangeError, 'ERR_BUFFER_OUT_OF_BOUNDS', 'offset is outside buffer');
      const count = length === undefined ? value.byteLength - offset : length;
      if (typeof count !== 'number' || !Number.isInteger(count) || count < 0) reject('ArrayBuffer length coercion');
      size(count);
      if (count > value.byteLength - offset) fail(RangeError, 'ERR_BUFFER_OUT_OF_BOUNDS', 'length is outside buffer');
      return tag(new U8(value, offset, count));
    }
    if (value instanceof U8) {
      if (value.buffer.resizable === true ||
          (typeof web.SharedArrayBuffer === 'function' && value.buffer instanceof web.SharedArrayBuffer)) {
        reject('shared or resizable input');
      }
      size(value.byteLength);
      return tag(new U8(value)); // COPY the visible bytes, including nonzero offsets.
    }
    reject('from input kind');
  };
  Buffer.isBuffer = value => instances.has(value);
  Buffer.isEncoding = value => typeof value === 'string' && ['utf8', 'utf-8', 'hex'].includes(value.toLowerCase());
  Buffer.byteLength = function byteLength(value, enc) {
    if (typeof value === 'string') {
      sourceLimit(value);
      return encoding(enc) === 'hex' ? Math.floor(value.length / 2) : encoder.encode(value).length;
    }
    if (value instanceof AB || value instanceof U8) return value.byteLength;
    reject('byteLength input kind');
  };
  const methods = {
    toString(enc, start = 0, end = this.length) {
      requireBuffer(this);
      if (!Number.isInteger(start) || !Number.isInteger(end)) reject('toString index coercion');
      const first = Math.min(this.length, Math.max(start, 0));
      const last = Math.max(first, Math.min(this.length, Math.max(end, 0)));
      // Plain view: no copy and no allocation through user-overridden species.
      const bytes = new U8(this.buffer, this.byteOffset + first, last - first);
      return encoding(enc) === 'hex' ? kernel.hexEncode(bytes) : decoder.decode(bytes);
    },
    subarray(start, end) {
      requireBuffer(this);
      // Uint8Array's index normalization and species allocation produce shared
      // views; tag() preserves Buffer identity even with default constructors.
      return tag(U8.prototype.subarray.call(this, start, end));
    },
    slice(start, end) { return methods.subarray.call(this, start, end); },
  };
  for (const [name, value] of Object.entries(methods)) {
    Object.defineProperty(Buffer.prototype, name, { value, writable: true, configurable: true });
  }
  Object.defineProperties(Buffer.prototype, {
    parent: { get() { requireBuffer(this); return this.buffer; }, configurable: true },
    offset: { get() { requireBuffer(this); return this.byteOffset; }, configurable: true },
  });
  for (const name of ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']) {
    Buffer[name] = unavailable('node:buffer', `Buffer.${name}`);
  }
  // Explicit list from Node v22.14.0's Buffer prototype; U8 methods with Node
  // overloads must refuse invocation rather than silently use different rules.
  for (const name of [
    'readBigUInt64LE', 'readBigUInt64BE', 'readBigUint64LE', 'readBigUint64BE', 'readBigInt64LE', 'readBigInt64BE',
    'writeBigUInt64LE', 'writeBigUInt64BE', 'writeBigUint64LE', 'writeBigUint64BE', 'writeBigInt64LE', 'writeBigInt64BE',
    'readUIntLE', 'readUInt32LE', 'readUInt16LE', 'readUInt8', 'readUIntBE', 'readUInt32BE', 'readUInt16BE',
    'readUintLE', 'readUint32LE', 'readUint16LE', 'readUint8', 'readUintBE', 'readUint32BE', 'readUint16BE',
    'readIntLE', 'readInt32LE', 'readInt16LE', 'readInt8', 'readIntBE', 'readInt32BE', 'readInt16BE',
    'writeUIntLE', 'writeUInt32LE', 'writeUInt16LE', 'writeUInt8', 'writeUIntBE', 'writeUInt32BE', 'writeUInt16BE',
    'writeUintLE', 'writeUint32LE', 'writeUint16LE', 'writeUint8', 'writeUintBE', 'writeUint32BE', 'writeUint16BE',
    'writeIntLE', 'writeInt32LE', 'writeInt16LE', 'writeInt8', 'writeIntBE', 'writeInt32BE', 'writeInt16BE',
    'readFloatLE', 'readFloatBE', 'readDoubleLE', 'readDoubleBE', 'writeFloatLE', 'writeFloatBE', 'writeDoubleLE', 'writeDoubleBE',
    'asciiSlice', 'base64Slice', 'base64urlSlice', 'latin1Slice', 'hexSlice', 'ucs2Slice', 'utf8Slice',
    'asciiWrite', 'base64Write', 'base64urlWrite', 'latin1Write', 'hexWrite', 'ucs2Write', 'utf8Write',
    'copy', 'equals', 'inspect', 'compare', 'indexOf', 'lastIndexOf', 'includes', 'fill', 'write', 'toJSON',
    'swap16', 'swap32', 'swap64', 'toLocaleString',
  ]) {
    Object.defineProperty(Buffer.prototype, name, {
      value: unavailable('node:buffer', `Buffer.prototype.${name}`), writable: true, configurable: true,
    });
  }
  Object.defineProperty(Buffer.prototype, Symbol.for('nodejs.util.inspect.custom'), {
    value: unavailable('node:buffer', 'Buffer.prototype[util.inspect.custom]'),
    writable: true, configurable: true,
  });
  // Real web implementations can be selected after semantic validation. This
  // milestone deliberately exports constructors/functions that refuse use.
  const Blob = unavailable('node:buffer', 'Blob');
  const File = unavailable('node:buffer', 'File');
  const SlowBuffer = unavailable('node:buffer', 'SlowBuffer');
  const atob = unavailable('node:buffer', 'atob');
  const btoa = unavailable('node:buffer', 'btoa');
  const isAscii = unavailable('node:buffer', 'isAscii');
  const isUtf8 = unavailable('node:buffer', 'isUtf8');
  const resolveObjectURL = unavailable('node:buffer', 'resolveObjectURL');
  const transcode = unavailable('node:buffer', 'transcode');
  const constants = Object.freeze({ MAX_LENGTH, MAX_STRING_LENGTH });
  const namespace = {
    Blob, Buffer, File, INSPECT_MAX_BYTES: 50, SlowBuffer, atob, btoa, constants,
    isAscii, isUtf8, kMaxLength: MAX_LENGTH, kStringMaxLength: MAX_STRING_LENGTH,
    resolveObjectURL, transcode,
  };
  const defaultExport = Object.freeze({ ...namespace });
  return Object.freeze({ ...namespace, default: defaultExport });
}
