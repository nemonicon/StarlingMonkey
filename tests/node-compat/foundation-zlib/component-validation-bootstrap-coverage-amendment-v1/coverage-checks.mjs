// Pure host validation only. No codec, bootstrap, component or tool imports.
import assert from 'node:assert/strict';

const nativeCodes = new Set([
  'ERR_BUFFER_TOO_LARGE', 'Z_DATA_ERROR', 'Z_BUF_ERROR',
  'ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED', 'ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED',
]);
const facadeCodes = new Set(['ERR_OUT_OF_RANGE', 'ERR_INVALID_ARG_TYPE', 'ERR_SM_NODE_UNSUPPORTED']);
const absent = Object.freeze({own:false, type:'undefined', value:null});

export function assertRunCounter(value, expected) {
  assert(Number.isSafeInteger(expected) && expected >= 0, 'Explicit nonnegative expected run count required');
  assert(Number.isSafeInteger(value.calls) && value.calls >= 0, 'Guest run count must be a nonnegative integer');
  assert.equal(value.calls, expected, 'Retained/fresh run lifecycle count');
}

export function assertErrorContract(error, row, profile) {
  const fields = error.fields;
  for (const [key, value] of Object.entries({code:row.profileCode, module:'node:zlib', profile})) {
    assert.deepEqual(fields[key], {own:true, type:'string', value}, key);
  }
  if (nativeCodes.has(row.profileCode)) {
    assert.equal(fields.errno.own, true, 'Native codec errno must be own');
    assert.equal(fields.errno.type, 'number', 'Native codec errno must be numeric');
    assert(Number.isSafeInteger(fields.errno.value), 'Native codec errno must be a finite integer');
    assert.deepEqual(fields.operation, absent, 'Native codec errors do not invent an operation field');
    return {origin:'native-codec', errno:fields.errno.value, operationAbsent:true};
  }
  assert(facadeCodes.has(row.profileCode), 'Finite facade error code required');
  const operation = row.id === 'unknown-option-level' ? row.operation + ': option level'
    : row.id === 'ordinary-string-input-refusal' ? row.operation + ': string input' : row.operation;
  assert.deepEqual(fields.operation, {own:true, type:'string', value:operation}, 'Facade operation');
  assert.deepEqual(fields.errno, absent, 'Facade validation errors do not invent a native errno');
  return {origin:'facade', operation, errnoAbsent:true};
}
