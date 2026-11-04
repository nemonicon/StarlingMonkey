// Generated UNAPPLIED stream-consumers factory.
// Canonical-source SHA-256: aa8a4a5b9199e1fa5eccdc582ecb806ec55e9a5ac231d5c7879da96b2850b3d1
static constexpr const char kStreamConsumersFactorySource[] = R"SM_NODE_PROFILE((function(argument){
'use strict';
// UNAPPLIED optional production text/JSON source. Fresh355 native/registration/guest gates pending.
// The text/json algorithm follows Node v22.14.0 stream/consumers (LICENSE.node).
// Blob-dependent operations deliberately do not call the existing native Blob.
const CONTRACT_VERSION = 'sm-node-22.14.0-m0.14';
const MAX_BYTE_INPUT = 1048576;
const MAX_STRING_INPUT_CODE_UNITS = 1048576;
const MAX_OUTPUT_CODE_UNITS = 1048576;
const MAX_CHUNKS = 4096;

function createConsumersModule(web) {
  const Apply = Reflect.apply, Define = Object.defineProperty, Freeze = Object.freeze;
  const Descriptor = Object.getOwnPropertyDescriptor;
  const TypeErrorCtor = TypeError, RangeErrorCtor = RangeError, ErrorCtor = Error;
  const Parse = JSON.parse, IsView = web.ArrayBuffer.isView;
  const Decoder = web.TextDecoder, Decode = Decoder.prototype.decode;
  const U8 = web.Uint8Array;
  const ABLength = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'byteLength').get;
  const ABResizable = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'resizable')?.get;
  const ABDetached = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'detached')?.get;
  const typed = Object.getPrototypeOf(U8.prototype);
  const TypedBuffer = Object.getOwnPropertyDescriptor(typed, 'buffer').get;
  const TypedLength = Object.getOwnPropertyDescriptor(typed, 'byteLength').get;
  const ViewBuffer = Object.getOwnPropertyDescriptor(web.DataView.prototype, 'buffer').get;
  const ViewLength = Object.getOwnPropertyDescriptor(web.DataView.prototype, 'byteLength').get;
  const streamOptions = Freeze({ __proto__: null, stream: true });
  const finalOptions = Freeze({ __proto__: null, stream: false });
  function failure(Ctor, code, operation, message) {
    const error = new Ctor(code+': node:stream/consumers.'+operation+' '+message);
    Define(error, 'code', { __proto__: null, value: code, writable: true, enumerable: true, configurable: true });
    Define(error, 'module', { __proto__: null, value: 'node:stream/consumers', writable: true, enumerable: true, configurable: true });
    Define(error, 'operation', { __proto__: null, value: operation, writable: true, enumerable: true, configurable: true });
    Define(error, 'profile', { __proto__: null, value: CONTRACT_VERSION, writable: true, enumerable: true, configurable: true });
    throw error;
  }
  function deferred(operation) { failure(ErrorCtor, 'ERR_SM_NODE_UNSUPPORTED', operation, 'requires the separate Blob ownership/identity gate'); }
  function invalid() { failure(TypeErrorCtor, 'ERR_INVALID_ARG_TYPE', 'text', 'chunk must be a string or supported BufferSource'); }
  function limit(name) { failure(RangeErrorCtor, 'ERR_SM_NODE_LIMIT', 'text', 'exceeds '+name); }
  function inputLength(value) {
    if (value === undefined) return 0; // Node passes undefined to TextDecoder.
    let buffer, length;
    if (IsView(value)) {
      try { buffer = Apply(TypedBuffer, value, []); length = Apply(TypedLength, value, []); }
      catch {
        try { buffer = Apply(ViewBuffer, value, []); length = Apply(ViewLength, value, []); }
        catch { return invalid(); }
      }
    } else {
      buffer = value;
      try { length = Apply(ABLength, buffer, []); }
      catch { return invalid(); }
    }
    // Validate backing with captured internal-slot getters only. No byte is
    // copied early and no native borrowed pointer survives this JS operation.
    try { Apply(ABLength, buffer, []); }
    catch { failure(ErrorCtor, 'ERR_SM_NODE_UNSUPPORTED', 'text', 'shared backing is outside this prototype'); }
    if (ABResizable && Apply(ABResizable, buffer, [])) failure(ErrorCtor, 'ERR_SM_NODE_UNSUPPORTED', 'text', 'resizable backing is outside this prototype');
    if (ABDetached && Apply(ABDetached, buffer, [])) failure(ErrorCtor, 'ERR_SM_NODE_UNSUPPORTED', 'text', 'detached backing is outside this prototype');
    if (!ABDetached) {
      try { new U8(buffer, 0, 0); }
      catch { failure(ErrorCtor, 'ERR_SM_NODE_UNSUPPORTED', 'text', 'detached backing is outside this prototype'); }
    }
    return length;
  }
  async function text(stream) {
    const decoder = new Decoder();
    let result = '', bytes = 0, stringUnits = 0, chunks = 0;
    // Built-in for-await preserves Sync/Async iterator distinctions and body
    // failure close precedence; a failed next() is not manually closed again.
    for await (const chunk of stream) {
      if (++chunks > MAX_CHUNKS) limit('MAX_CHUNKS');
      let part;
      if (typeof chunk === 'string') {
        stringUnits += chunk.length;
        if (stringUnits > MAX_STRING_INPUT_CODE_UNITS) limit('MAX_STRING_INPUT_CODE_UNITS');
        part = chunk; // A string does not flush pending decoder bytes.
      } else {
        bytes += inputLength(chunk);
        if (bytes > MAX_BYTE_INPUT) limit('MAX_BYTE_INPUT');
        part = Apply(Decode, decoder, [chunk, streamOptions]);
      }
      if (part.length > MAX_OUTPUT_CODE_UNITS - result.length) limit('MAX_OUTPUT_CODE_UNITS');
      result += part;
    }
    const final = Apply(Decode, decoder, [undefined, finalOptions]);
    if (final.length > MAX_OUTPUT_CODE_UNITS - result.length) limit('MAX_OUTPUT_CODE_UNITS');
    return result + final;
  }
  async function json(stream) { return Parse(await text(stream)); }
  function arrayBuffer(stream) { deferred('arrayBuffer'); }
  function blob(stream) { deferred('blob'); }
  function buffer(stream) { deferred('buffer'); }
  // Resolve SpiderMonkey lazy function properties before application reads.
  // The captured descriptors retain native values/attributes; no new property
  // is defined. Node creates length then name for these async functions.
  Descriptor(text, 'length'); Descriptor(text, 'name');
  Descriptor(json, 'length'); Descriptor(json, 'name');
  const defaultObject = { arrayBuffer, blob, buffer, text, json };
  // The future embedding would declare real module bindings from this finite
  // record. This factory itself does not install a native module or a global.
  return Freeze({ arrayBuffer, blob, buffer, text, json, default: defaultObject });
}

return createConsumersModule(argument);
}))SM_NODE_PROFILE";
