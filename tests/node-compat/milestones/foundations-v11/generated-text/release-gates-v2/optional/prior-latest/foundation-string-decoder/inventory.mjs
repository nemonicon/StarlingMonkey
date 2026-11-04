// Exact Node22 inventory and safe, mutation-only Web decoder comparisons.
import assert from 'node:assert/strict';
import * as namespace from 'node:string_decoder';
import { StringDecoder } from 'node:string_decoder';
import { writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
function outcome(call) { try { return { value: call() }; } catch (error) { return { error: { name: error.name, code: error.code, message: error.message } }; } }
function descriptor(value) {
  return Object.fromEntries(Object.entries(value).map(([key, value]) => [key, typeof value === 'function' ? { name: value.name, length: value.length } : value]));
}
const encodingLabels = [undefined, null, '', 'utf8', 'utf-8', 'UTF8', 'UTF-8', 'ucs2', 'ucs-2', 'utf16le', 'utf-16le',
  'ascii', 'latin1', 'binary', 'base64', 'base64url', 'hex', 'RAW', 'rot13', 'utf16be', ' utf8 ', 0, false, true, {}, []];
const encodings = encodingLabels.map(input => ({ input: input === undefined ? '<undefined>' : input,
  result: outcome(() => new StringDecoder(input).encoding) }));
const sample = new StringDecoder(), stateSymbol = Object.getOwnPropertySymbols(sample)[0];
const constructorCalls = { withoutNew: outcome(() => StringDecoder()), callOrdinaryReceiver: outcome(() => { const receiver = {}; const returned = StringDecoder.call(receiver); return { returned: String(returned), encoding: receiver.encoding, keys: Reflect.ownKeys(receiver).map(String) }; }) };
const malformedCases = [[[0xc0], [0x80]], [[0xf0, 0x8f], [0x80, 0x80]], [[0xed, 0xa0], [0x80]], [[0xe2], [0x41]], [[0xef], [0xbb], [0xbf]]];
const webDifferences = malformedCases.map(chunks => {
  const node = new StringDecoder('utf8'), web = new TextDecoder('utf-8', { ignoreBOM: true });
  return { chunks, node: chunks.map(chunk => ({ output: node.write(Uint8Array.from(chunk)), need: node.lastNeed,
    total: node.lastTotal, lastChar: [...node.lastChar] })), web: chunks.map(chunk => web.decode(Uint8Array.from(chunk), { stream: true })),
    nodeEnd: node.end(), webEnd: web.decode() };
});
const nonUtf8Differences = ['utf16le', 'ascii', 'latin1'].map(encoding => {
  const chunks = encoding === 'utf16le' ? [[0, 0xd8], [0x41], [0]] : [[0x80, 0xe9, 0xff]];
  const node = new StringDecoder(encoding), web = new TextDecoder(encoding === 'utf16le' ? 'utf-16le' : 'windows-1252', { ignoreBOM: true });
  return { encoding, chunks, node: chunks.map(chunk => node.write(Uint8Array.from(chunk))),
    web: chunks.map(chunk => web.decode(Uint8Array.from(chunk), { stream: true })), nodeEnd: node.end(), webEnd: web.decode() };
});
const conversionOrder = [];
for (const label of ['utf-8', 'utf-16le']) for (const stream of [false, true]) {
  const trace = [];
  const result = outcome(() => new TextDecoder(label).decode({}, { get stream() { trace.push('stream'); return stream; } }));
  conversionOrder.push({ label, stream, invalidInput: {}, trace, result });
}
const bytes = Uint8Array.of(0x61), trace = [];
const validInputMutation = { result: new TextDecoder().decode(bytes, { get stream() { trace.push('stream'); bytes[0] = 0x62; return false; } }), trace };
const changed = new StringDecoder(); changed.encoding = 'hex';
const mutableEncoding = { publicEncoding: changed.encoding, decoded: changed.end(Uint8Array.of(0x41)) };
const encodingCoercions = [[4, 'utf8'], [3, 'HEX'], [9, 'base64url']].map(([length, text]) => {
  const trace = [];
  const label = { get length() { trace.push('length'); return length; }, toString() { trace.push('toString'); return text; } };
  return { length, text, result: outcome(() => new StringDecoder(label).encoding), trace };
});
const report = { schema: 1, node: process.version, exports: Object.keys(namespace), defaultNames: Object.keys(namespace.default),
  defaultNamedIdentity: namespace.default.StringDecoder === StringDecoder,
  constructor: { name: StringDecoder.name, length: StringDecoder.length, calls: constructorCalls },
  prototype: Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(StringDecoder.prototype)).map(([key, value]) => [key, descriptor(value)])),
  instance: { ownKeys: Reflect.ownKeys(sample).map(String), encoding: sample.encoding, stateBytes: [...sample[stateSymbol]],
    stateByteLength: sample[stateSymbol].byteLength, stateBackingBytes: sample[stateSymbol].buffer.byteLength,
    lastCharBytes: sample.lastChar.byteLength, freshViewPerRead: sample.lastChar !== sample.lastChar,
    sameBackingPerRead: sample.lastChar.buffer === sample.lastChar.buffer },
  encodings, encodingCoercions, mutableEncoding, webDifferences, nonUtf8Differences, conversionOrder, validInputMutation,
  scope: 'Pinned Node observations only; no detached/shared/resizable native inputs or generic native safety test is executed' };
await writeFile(join(here, 'inventory-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ node: process.version, exports: report.exports, stateBytes: report.instance.stateByteLength,
  knownEncodingLabels: encodings.filter(entry => !entry.result.error).length, safeWebComparisons: webDifferences.length + nonUtf8Differences.length }, null, 2));
