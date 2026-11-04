// SAFE Node-only observations. Never run these cases against the old native codec.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
assert.equal(process.version, 'v22.14.0');
const encoder = new TextEncoder(), results = [];
function probe(name, callback) {
  const trace = [];
  try { results.push({name, result: callback(trace), trace}); }
  catch (error) { results.push({name, error: {name: error.name, code: error.code, message: error.message}, trace}); }
}
for (const [name, source] of [['empty', ''], ['ascii', 'abc'], ['astral', '🌍']]) {
  probe(`${name}-zero`, () => encoder.encodeInto(source, new Uint8Array(0)));
}
probe('detached', () => {
  const view = new Uint8Array(8);
  structuredClone(view.buffer, {transfer: [view.buffer]});
  return encoder.encodeInto('abc', view);
});
for (const fixed of [true, false]) {
  probe(`oob-${fixed ? 'fixed' : 'tracking'}`, () => {
    const buffer = new ArrayBuffer(8, {maxByteLength: 16});
    const view = fixed ? new Uint8Array(buffer, 4, 4) : new Uint8Array(buffer, 4);
    buffer.resize(2);
    return encoder.encodeInto('abc', view);
  });
}
probe('object-zero', trace => encoder.encodeInto({toString() { trace.push('toString'); return 'abc'; }}, new Uint8Array(0)));
probe('throwing-zero', trace => encoder.encodeInto({toString() { trace.push('toString'); throw Error('sentinel'); }}, new Uint8Array(0)));
probe('symbol-zero', () => encoder.encodeInto(Symbol('s'), new Uint8Array(0)));
probe('undefined-zero', () => encoder.encodeInto(undefined, new Uint8Array(0)));
probe('invalid-source-invalid-destination', trace => encoder.encodeInto({toString() { trace.push('toString'); throw Error('sentinel'); }}, {}));
probe('valid-source-invalid-destination', () => encoder.encodeInto('abc', {}));
for (const entry of results.slice(0, 6)) assert.deepEqual(entry.result, {read: 0, written: 0});
for (const entry of results.slice(6, 11)) {
  assert.equal(entry.error?.code, 'ERR_INVALID_ARG_TYPE');
  assert.deepEqual(entry.trace, []);
}
assert.equal(results.at(-1).error?.code, 'ERR_INVALID_ARG_TYPE');
const report = {node: process.version, scope: 'SAFE Node-only ordinary APIs; no StarlingMonkey execution', results};
await writeFile(new URL('./encode-into-oracle-results.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({node: process.version, passed: results.length, zeroResults: 6, sourceRejectionsWithoutCoercion: 5}));
