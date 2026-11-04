// Finite ESM strict subpath; shared functions/state come from one root module.
export { AssertionError, CallTracker, deepStrictEqual as deepEqual,
  deepStrictEqual, doesNotMatch, doesNotReject, doesNotThrow,
  strictEqual as equal, fail, ifError, match, notDeepStrictEqual as notDeepEqual,
  notDeepStrictEqual, notStrictEqual as notEqual, notStrictEqual, ok,
  partialDeepStrictEqual, rejects, strict, strictEqual, throws, strict as default } from './assert.mjs';
