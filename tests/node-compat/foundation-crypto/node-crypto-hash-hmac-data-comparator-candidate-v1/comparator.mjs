// Pure DATA validation. Caller authenticates provenance and DURABLY RETAINS each
// entire typed raw return BEFORE calling. No fixture/import/crypto/provider/I/O.
import { CONTRACT as C } from './contract.mjs';

export class HashHmacDataError extends Error {
  constructor(path, message) { super(`${path}: ${message}`); this.name = 'HashHmacDataError'; this.code = 'ERR_HASH_HMAC_DATA'; this.path = path; }
}
const requireData = (value, path, message) => { if (!value) throw new HashHmacDataError(path, message); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const hex = (x, bytes) => typeof x === 'string' && /^[0-9a-f]*$/.test(x) && x.length === bytes * 2;
function keys(x, expected, path) {
  requireData(object(x), path, 'ordinary record required');
  const actual = Object.keys(x); requireData(actual.length === expected.length && expected.every(k => Object.hasOwn(x, k)), path, 'exact fields required');
}
function ordinary(x, path = '$', active = new Set(), depth = 0) {
  requireData(depth <= 64, path, 'maximum DATA depth');
  if (x === null || ['string', 'boolean'].includes(typeof x)) return;
  if (typeof x === 'number') { requireData(Number.isFinite(x), path, 'finite number required'); return; }
  requireData(typeof x === 'object' && !active.has(x), path, 'ordinary acyclic JSON DATA required');
  const descriptors = Object.getOwnPropertyDescriptors(x);
  if (Array.isArray(x)) {
    requireData(Object.getPrototypeOf(x) === Array.prototype && Reflect.ownKeys(x).length === x.length + 1, path, 'dense plain array required');
    for (let i = 0; i < x.length; i++) requireData(Object.hasOwn(descriptors, i) && Object.hasOwn(descriptors[i], 'value'), `${path}[${i}]`, 'dense data item required');
  } else {
    requireData([null, Object.prototype].includes(Object.getPrototypeOf(x)), path, 'plain JSON record required');
    requireData(Reflect.ownKeys(x).length === Object.keys(x).length, path, 'no hidden or symbol DATA fields');
    for (const d of Object.values(descriptors)) requireData(Object.hasOwn(d, 'value'), path, 'accessor DATA rejected');
  }
  active.add(x);
  for (const [k, d] of Object.entries(descriptors)) if (k !== 'length' || !Array.isArray(x)) ordinary(d.value, `${path}.${k}`, active, depth + 1);
  active.delete(x);
}
function same(actual, expected, path, diagnostics = null) {
  if (diagnostics && path.endsWith('.error.message')) {
    requireData(typeof actual === 'string' && typeof expected === 'string', path, 'complete error messages must remain strings');
    diagnostics.push({ path, nodeMessage: expected, guestMessage: actual, comparedForParity: false }); return;
  }
  requireData(typeof actual === typeof expected && (actual === null) === (expected === null) && Array.isArray(actual) === Array.isArray(expected), path, 'value type mismatch');
  if (Array.isArray(expected)) {
    requireData(actual.length === expected.length, path, 'array length mismatch');
    for (let i = 0; i < expected.length; i++) same(actual[i], expected[i], `${path}[${i}]`, diagnostics);
  } else if (object(expected)) {
    keys(actual, Object.keys(expected), path);
    for (const k of Object.keys(expected)) same(actual[k], expected[k], `${path}.${k}`, diagnostics);
  } else requireData(Object.is(actual, expected), path, 'value mismatch');
}
// JSON.parse alone drops duplicate keys. This bounded lexical pass rejects them
// before parsing, without rewriting the raw string, ordinal, array or record IDs.
export function parseHashHmacRaw(raw) {
  requireData(typeof raw === 'string', '$raw', 'full scalar string required');
  requireData(new TextEncoder().encode(raw).length <= C.maximumRawUtf8Bytes, '$raw', 'raw UTF8 bound exceeded');
  let i = 0, nodes = 0;
  const ws = () => { while (/[\x20\t\r\n]/.test(raw[i] ?? '') && i < raw.length) i++; };
  function string() {
    const start = i++; requireData(raw[start] === '"', '$raw', 'JSON string required');
    while (i < raw.length) {
      const c = raw[i++];
      if (c === '"') { try { return JSON.parse(raw.slice(start, i)); } catch { throw new HashHmacDataError('$raw', 'invalid JSON string'); } }
      if (c === '\\') { requireData(i < raw.length, '$raw', 'unfinished escape'); i++; }
      else requireData(c.charCodeAt(0) >= 32, '$raw', 'unescaped control byte');
    }
    throw new HashHmacDataError('$raw', 'unfinished JSON string');
  }
  function value(depth) {
    ws(); requireData(depth <= 64 && ++nodes <= 50000, '$raw', 'JSON bounds exceeded');
    if (raw[i] === '"') { string(); return; }
    if (raw[i] === '{') {
      i++; ws(); const names = new Set(); if (raw[i] === '}') { i++; return; }
      while (true) { ws(); const name = string(); requireData(!names.has(name), '$raw', 'duplicate JSON key'); names.add(name); ws(); requireData(raw[i++] === ':', '$raw', 'missing colon'); value(depth + 1); ws(); const c = raw[i++]; if (c === '}') return; requireData(c === ',', '$raw', 'missing object separator'); }
    }
    if (raw[i] === '[') {
      i++; ws(); if (raw[i] === ']') { i++; return; }
      while (true) { value(depth + 1); ws(); const c = raw[i++]; if (c === ']') return; requireData(c === ',', '$raw', 'missing array separator'); }
    }
    for (const literal of ['true', 'false', 'null']) if (raw.startsWith(literal, i)) { i += literal.length; return; }
    const number = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(raw.slice(i));
    requireData(number && Number.isFinite(Number(number[0])), '$raw', 'finite JSON value required'); i += number[0].length;
  }
  value(0); ws(); requireData(i === raw.length, '$raw', 'trailing or malformed JSON');
  let record; try { record = JSON.parse(raw); } catch { throw new HashHmacDataError('$raw', 'invalid JSON'); }
  ordinary(record); return record;
}
function errorRecord(x, path, name = null, code = null) {
  keys(x, ['type', 'name', 'code', 'message', 'originalIdentityClaim'], path);
  requireData(x.type === 'object' && typeof x.name === 'string' && typeof x.message === 'string' && (x.code === null || typeof x.code === 'string') && x.originalIdentityClaim === false, path, 'typed complete error record required');
  if (name) requireData(x.name === name, path, 'error name mismatch');
  if (code) requireData(x.code === code, path, 'error code mismatch');
}
function observed(x, path) {
  requireData(object(x) && typeof x.type === 'string', path, 'typed return required');
  if (['Buffer', 'Uint8Array'].includes(x.type)) { keys(x, ['type', 'bytes', 'hex'], path); requireData(Number.isSafeInteger(x.bytes) && x.bytes >= 0 && hex(x.hex, x.bytes), path, 'complete byte return required'); }
  else { keys(x, ['type', 'value'], path); requireData(['string', 'boolean', 'number', 'null', 'undefined'].includes(x.type), path, 'opaque return rejected'); requireData(x.type === 'null' || x.type === 'undefined' ? x.value === null : typeof x.value === x.type, path, 'return value type mismatch'); }
}
function outcome(x, path) {
  if (x?.kind === 'return') { keys(x, ['kind', 'observed'], path); observed(x.observed, path + '.observed'); }
  else { keys(x, ['kind', 'error'], path); requireData(x.kind === 'throw', path, 'return/throw kind required'); errorRecord(x.error, path + '.error'); }
}
function context(x, path, consuming = true) {
  keys(x, ['outcome', 'cleanup'], path); outcome(x.outcome, path + '.outcome');
  requireData(object(x.cleanup), path + '.cleanup', 'typed cleanup record required');
  if (consuming) { same(x.cleanup, { attempted: false }, path + '.cleanup'); requireData(x.outcome.kind === 'return', path, 'accepted consuming operation threw'); }
  else if (x.cleanup.attempted === false) keys(x.cleanup, ['attempted'], path + '.cleanup');
  else { requireData(x.cleanup.attempted === true, path, 'cleanup attempted flag required'); const { attempted, ...rest } = x.cleanup; outcome(rest, path + '.cleanup'); requireData(rest.kind === 'return', path, 'unexpected cleanup throw'); }
}
function records(x, ids, path) {
  requireData(Array.isArray(x) && x.length === ids.length, path, 'exact record count required');
  for (let i = 0; i < ids.length; i++) requireData(x[i]?.id === ids[i], `${path}[${i}]`, 'missing/duplicate/reordered/unexpected ID');
}
function manifest(m) {
  ordinary(m, '$manifest'); requireData(object(m) && m.schemaVersion === 1 && m.expectedPositiveRecordCount === 20 && m.expectedProfileRecordCount === 8 && m.nativeProfileDefaultFrozenExpected === true && m.nodeComparisonProjection?.componentJcoVsWasmtimeWholeJsonEqualityForSameOrdinalRequired === true, '$manifest', 'fixture schema/count/scope mismatch');
  for (const [actual, expected, path] of [[m.nodeComparableCases, C.positiveIds, 'positiveIds'], [m.profileOnlyCases, C.profileIds, 'profileIds'], [m.requiredAliasBooleans, C.aliases, 'aliases'], [m.profileExpectedErrorCodes, C.profileErrors, 'profileErrors'], [m.knownHashVectors, C.knownHashVectors, 'hashVectors'], [m.knownHmacVectors, C.knownHmacVectors, 'hmacVectors']]) same(actual, expected, '$manifest.' + path);
}
function accepted(x, path) {
  records(x, C.positiveIds, path);
  for (const r of x) {
    keys(r, ['id', 'value'], path + '.' + r.id); keys(r.value, C.valueFields[r.id], path + '.' + r.id + '.value');
    for (const field of ['actual', 'whole', 'partitioned', 'bufferWindow', 'first', 'second']) if (Object.hasOwn(r.value, field)) context(r.value[field], `${path}.${r.id}.${field}`);
  }
  const get = id => x.find(r => r.id === id).value;
  const digest = c => { context(c, path); requireData(c.outcome.observed.type === 'string' && hex(c.outcome.observed.value, 32), path, 'full SHA256/HMAC hex required'); return c.outcome.observed.value; };
  const messageHex = ['', '616263', 'c3a9'];
  for (const [i, v] of C.knownHashVectors.entries()) { const r = get(v.id); requireData(r.messageUtf8Hex === messageHex[i] && r.expectedHex === v.expectedHex && digest(r.actual) === v.expectedHex, path, 'literal SHA256 answer/input mismatch'); }
  requireData(get('hash-unicode-surrogate').messageUtf8Hex === 'c3a9f09d849eefbfbd' && get('hash-unicode-surrogate').expectedUtf8Hex === 'c3a9f09d849eefbfbd' && get('hash-unicode-surrogate').expectedDigest === null && digest(get('hash-unicode-surrogate').actual) === C.additionalOracleHex.unicodeSurrogate, path, 'Unicode surrogate bytes/digest mismatch');
  requireData(get('hash-partition-abc').expectedHex === C.knownHashVectors[1].expectedHex && digest(get('hash-partition-abc').actual) === C.knownHashVectors[1].expectedHex, path, 'partitioned abc mismatch');
  for (const n of [55, 56, 63, 64, 65]) { const r = get('hash-block-' + n); let message = ''; for (let i = 0; i < n; i++) message += ((i * 17 + 3) & 255).toString(16).padStart(2, '0'); requireData(r.messageHex === message && digest(r.whole) === digest(r.partitioned), path, 'full boundary/chunk result mismatch'); }
  const w = get('hash-nonzero-window-copy'); for (const f of ['sameReceiver', 'sentinelsPreserved', 'bufferInputIsBuffer', 'bufferSameReceiver', 'bufferSentinelsPreserved']) requireData(w[f] === true, path, 'window/copy identity mismatch');
  requireData(w.expectedMessageHex === '616263' && w.expectedHex === C.knownHashVectors[1].expectedHex && w.afterCallerMutationHex === 'd1787878e2' && w.bufferAfterCallerMutationHex === 'd1787878e2' && digest(w.actual) === C.knownHashVectors[1].expectedHex && digest(w.bufferWindow) === C.knownHashVectors[1].expectedHex, path, 'window snapshot/full sentinels mismatch');
  const o = get('hash-output-ownership'); requireData(o.priorStableAfterSecond === true && o.secondStableAfterFirstMutation === true && o.expectedFirstHex === C.knownHashVectors[1].expectedHex && o.expectedSecondHex === C.knownHashVectors[0].expectedHex, path, 'output ownership flags/expectations');
  for (const [r, expected] of [[o.first, C.knownHashVectors[1].expectedHex], [o.second, C.knownHashVectors[0].expectedHex]]) requireData(r.outcome.observed.type === 'Buffer' && r.outcome.observed.bytes === 32 && r.outcome.observed.hex === expected, path, 'complete Buffer digest required');
  for (const v of C.knownHmacVectors) { const r = get(v.id); requireData(r.expectedHex === v.expectedHex && digest(r.actual) === v.expectedHex && r.keyHex === (v.keyHex ?? null) && r.keyUtf8 === (v.keyUtf8 ?? null), path, 'literal HMAC answer/key mismatch'); }
  requireData(get('hmac-empty').expectedDigest === null && digest(get('hmac-empty').actual) === C.additionalOracleHex.emptyHmac, path, 'empty HMAC mismatch');
  const k = get('hmac-key-window-snapshot'); requireData(k.expectedHex === C.knownHmacVectors[0].expectedHex && k.callerUnchangedAfterCreate === true && k.sentinelsPreserved === true && k.callerAfterMutationHex === '00'.repeat(20) && digest(k.actual) === C.knownHmacVectors[0].expectedHex, path, 'key snapshot mismatch');
  const th = get('terminal-hash'), tm = get('terminal-hmac'); keys(th.terminal, ['first', 'repeated', 'updateAfter'], path + '.terminalHash'); keys(tm.terminal, ['first', 'repeatedHex', 'repeatedBuffer', 'updateAfter'], path + '.terminalHmac');
  requireData(th.expectedFinalizedErrorCode === 'ERR_CRYPTO_HASH_FINALIZED' && tm.expectedFinalizedErrorCode === 'ERR_CRYPTO_HASH_FINALIZED' && tm.expectedFirstHex === C.knownHmacVectors[1].expectedHex && tm.expectedRepeatedHex === '' && tm.expectedRepeatedBufferBytes === 0, path, 'terminal declared expectations mismatch');
  requireData(digest(th.actual) === C.knownHashVectors[1].expectedHex && th.terminal.first === C.knownHashVectors[1].expectedHex && digest(tm.actual) === C.knownHmacVectors[1].expectedHex && tm.terminal.first === C.knownHmacVectors[1].expectedHex, path, 'first terminal operation failed');
  for (const r of [th.terminal.repeated, th.terminal.updateAfter, tm.terminal.updateAfter]) { outcome(r, path + '.terminal'); requireData(r.kind === 'throw', path, 'finalized operation must throw'); errorRecord(r.error, path, 'Error', 'ERR_CRYPTO_HASH_FINALIZED'); }
  same(tm.terminal.repeatedHex, { kind: 'return', observed: { type: 'string', value: '' } }, path + '.repeatedHex'); same(tm.terminal.repeatedBuffer, { kind: 'return', observed: { type: 'Buffer', bytes: 0, hex: '' } }, path + '.repeatedBuffer');
}
function dataValue(x, path) {
  requireData(object(x) && typeof x.type === 'string', path, 'typed descriptor value required');
  if (['null', 'undefined', 'string', 'number', 'boolean'].includes(x.type)) { keys(x, ['type', 'value'], path); requireData(x.type === 'null' || x.type === 'undefined' ? x.value === null : typeof x.value === x.type, path, 'descriptor value type mismatch'); }
  else { keys(x, ['type', 'functionName', 'opaque', 'fullOpaqueValueClaim'], path); requireData(['function', 'object', 'symbol', 'bigint'].includes(x.type) && x.opaque === true && x.fullOpaqueValueClaim === false && (x.type === 'function' ? typeof x.functionName === 'string' : x.functionName === null), path, 'typed opaque descriptor required'); }
}
function descriptors(rows, path) {
  requireData(Array.isArray(rows), path, 'full descriptors array required'); const names = [], seen = new Set();
  for (const d of rows) {
    keys(d, ['key', 'kind', 'enumerable', 'configurable', 'writable', 'value', 'getter', 'setter'], path);
    requireData(object(d.key), path, 'typed property key required');
    const name = d.key.type === 'string' ? (keys(d.key, ['type', 'value'], path), requireData(typeof d.key.value === 'string', path, 'string key required'), 's:' + d.key.value) : (keys(d.key, ['type', 'description'], path), requireData(d.key.type === 'symbol' && (d.key.description === null || typeof d.key.description === 'string'), path, 'symbol key required'), 'y:' + d.key.description);
    requireData(!seen.has(name), path, 'duplicate descriptor key'); seen.add(name); if (d.key.type === 'string') names.push(d.key.value);
    requireData(typeof d.enumerable === 'boolean' && typeof d.configurable === 'boolean' && ['function', 'undefined'].includes(d.getter) && ['function', 'undefined'].includes(d.setter), path, 'descriptor flags/types required');
    if (d.kind === 'data') { requireData(typeof d.writable === 'boolean' && d.getter === 'undefined' && d.setter === 'undefined', path, 'data descriptor required'); dataValue(d.value, path); }
    else requireData(d.kind === 'accessor' && d.writable === null && d.value === null, path, 'accessor descriptor required');
  }
  return names;
}
function namespace(record, native) {
  same(record.aliases, C.aliases, '$.aliases');
  const n = record.namespaceInspection; keys(n, ['actualNames', 'expectedInitialNames', 'nativeAndNodeNamespaceObjectIdentityNotRequired', 'namespaceObjectsSame', 'namespaceDescriptors', 'defaultDescriptors', 'defaultFrozen', 'namespaceExtensible'], '$.namespaceInspection');
  same(n.actualNames, C.namespaceNames, '$.namespaceInspection.actualNames'); same(n.expectedInitialNames, C.namespaceNames, '$.namespaceInspection.expectedInitialNames');
  requireData(n.nativeAndNodeNamespaceObjectIdentityNotRequired === true && typeof n.namespaceObjectsSame === 'boolean' && typeof n.defaultFrozen === 'boolean' && typeof n.namespaceExtensible === 'boolean', '$.namespaceInspection', 'identity/descriptor scopes required');
  const named = descriptors(n.namespaceDescriptors, '$.namespaceDescriptors'); same(named, C.namespaceNames, '$.namespaceDescriptors.names');
  const def = descriptors(n.defaultDescriptors, '$.defaultDescriptors'); requireData(def.length === 71 && C.defaultNames.every(x => def.includes(x)), '$.defaultDescriptors', 'all71 default names required');
  if (native) {
    requireData(n.defaultFrozen === true, '$.defaultFrozen', 'native profile default must be frozen');
    for (const d of n.namespaceDescriptors) {
      if (d.key.type === 'symbol') {
        requireData(d.key.description === 'Symbol.toStringTag' && d.kind === 'data' && d.value.type === 'string' && d.value.value === 'Module', '$.namespaceDescriptors.symbol', 'only genuine Module tag allowed');
      } else {
        requireData(d.kind === 'data' && d.value.type === (['default', 'constants', 'webcrypto', 'subtle'].includes(d.key.value) ? 'object' : 'function'), '$.namespaceDescriptors.' + d.key.value, 'native named binding type mismatch');
      }
    }
    for (const d of n.defaultDescriptors) {
      requireData(d.key.type === 'string' && d.configurable === false && (d.kind === 'data' ? d.writable === false : true), '$.defaultDescriptors', 'native frozen descriptors required');
      const name = d.key.value;
      if (name === 'fips') requireData(d.kind === 'accessor' && d.getter === 'function' && d.setter === 'undefined' && d.enumerable === false, '$.defaultDescriptors.fips', 'source-defined fips accessor');
      else requireData(d.kind === 'data' && d.value.type === (['constants', 'webcrypto', 'subtle'].includes(name) ? 'object' : 'function') && d.enumerable === !['prng', 'rng', 'pseudoRandomBytes'].includes(name), '$.defaultDescriptors.' + name, 'native binding type/enumerability mismatch');
    }
  }
}
function provider(record, native, expected) {
  const p = record.providerAndConstants; keys(p, ['constantsType', 'ownDescriptors', 'nativeSubsetExpectedNames', 'constantsNodeParityRequired', 'headerNumberIsRuntimeBackendProof', 'providerRuntimeIdentityObserved', 'opensslVersionNumber'], '$.providerAndConstants');
  requireData(p.constantsType === 'object' && p.constantsNodeParityRequired === false && p.headerNumberIsRuntimeBackendProof === false && p.providerRuntimeIdentityObserved === false, '$.providerAndConstants', 'provider proof scope mismatch');
  same(p.nativeSubsetExpectedNames, C.constantNames, '$.nativeSubsetExpectedNames'); const names = descriptors(p.ownDescriptors, '$.constantDescriptors'); dataValue(p.opensslVersionNumber, '$.opensslVersionNumber');
  if (native) {
    requireData(names.length === 9 && C.constantNames.every(x => names.includes(x)) && p.ownDescriptors.length === 9, '$.constantDescriptors', 'exact nine native header constants');
    same(expected, C.nativeConstants, '$expectedNativeConstants');
    for (const d of p.ownDescriptors) requireData(d.kind === 'data' && d.enumerable === true && d.configurable === false && d.writable === false && d.value.type === 'number' && Number.isSafeInteger(d.value.value) && d.value.value === expected[d.key.value], '$.constantDescriptors.' + d.key.value, 'native typed header constant mismatch');
    same(p.opensslVersionNumber, { type: 'number', value: expected.OPENSSL_VERSION_NUMBER }, '$.opensslVersionNumber');
  }
}
function policies(record, native) {
  records(record.profilePolicy, C.profileIds, '$.profilePolicy');
  for (const r of record.profilePolicy) {
    keys(r, ['id', 'expectedProfileErrorCode', 'actual', 'nodeParityRequired', ...(r.id === 'invalid-algorithm-type' ? ['algorithmConversions'] : [])], '$.profilePolicy.' + r.id);
    requireData(r.expectedProfileErrorCode === C.profileErrors[r.id] && r.nodeParityRequired === false, '$.profilePolicy', 'fixed native policy scope/code required');
    if (r.id === 'invalid-algorithm-type') requireData(r.algorithmConversions === 0, '$.algorithmConversions', 'algorithm object was converted');
    if (r.id === 'invalid-receiver') outcome(r.actual, '$.profilePolicy.' + r.id); else context(r.actual, '$.profilePolicy.' + r.id, false);
    if (!native) continue; // Node accepts SIX; never force native profile parity.
    const result = r.id === 'invalid-receiver' ? r.actual : r.actual.outcome;
    requireData(result.kind === 'throw', '$.profilePolicy.' + r.id, 'native policy refusal required');
    errorRecord(result.error, '$.profilePolicy.' + r.id, r.id.startsWith('invalid-') ? 'TypeError' : 'Error', C.profileErrors[r.id]);
    if (r.id !== 'invalid-receiver') {
      const cleanup = ['unsupported-input-encoding-hex', 'unsupported-output-encoding-base64'].includes(r.id) ? { attempted: true, kind: 'return', observed: { type: 'string', value: C.knownHashVectors[0].expectedHex } } : { attempted: false };
      same(r.actual.cleanup, cleanup, '$.profilePolicy.' + r.id + '.cleanup');
    }
  }
}
function recordShape(record, ordinal) {
  keys(record, ['schemaVersion', 'kind', 'calls', 'nodeComparable', 'aliases', 'profilePolicy', 'namespaceInspection', 'providerAndConstants', 'limits'], '$');
  requireData(record.schemaVersion === 1 && record.kind === C.fixtureKind && Number.isSafeInteger(ordinal) && ordinal >= 1 && ordinal <= 3 && record.calls === ordinal, '$.calls', 'exact actual call ordinal required; no normalization');
  same(record.limits, { moduleInitCryptoCalls: 0, stateCreationOnlyInsideOrdinaryRun: true, everyReturnedContextDrivenToDigest: true, nativeFinalizationOrZeroizationProved: false, liveEvpSnapshotAdmission: false, gcPressureInvoked: false, borrowVariantInvoked: false, cryptoKeyOrKeyObjectUsed: false, entropyOperationInvoked: false, resetInvoked: false, streamInheritanceOrFullNodeCryptoProved: false, fullNextCompatibilityProved: false, runtimeAcceptanceClaim: false }, '$.limits');
}
export function validateHashHmacNodeOracle(nodeRawStrings, { fixtureManifest }) {
  manifest(fixtureManifest); ordinary(nodeRawStrings, '$nodeRawStrings'); requireData(Array.isArray(nodeRawStrings) && nodeRawStrings.length === 3, '$nodeRawStrings', 'three complete retained Node strings required');
  const values = nodeRawStrings.map((raw, i) => { const r = parseHashHmacRaw(raw); recordShape(r, i + 1); accepted(r.nodeComparable, '$node.nodeComparable'); namespace(r, false); provider(r, false); policies(r, false); return r; });
  for (const v of values.slice(1)) for (const key of Object.keys(values[0])) if (key !== 'calls') same(v[key], values[0][key], '$node.' + key);
  return { records: values, acceptedByOrdinal: values.map(x => x.nodeComparable), rawStrings: nodeRawStrings.slice(), summary: { nodeCalls: 3, acceptedPerCall: 20, separatePolicyPerCall: 8, hostOracleOnly: true, provenanceAuthenticationIsCallerResponsibility: true } };
}
export function compareHashHmacReturn(rawString, { expectedCallOrdinal, nodeAcceptedRecords, fixtureManifest, expectedNativeConstants = C.nativeConstants }) {
  manifest(fixtureManifest); ordinary(nodeAcceptedRecords, '$nodeAcceptedRecords'); ordinary(expectedNativeConstants, '$expectedNativeConstants'); accepted(nodeAcceptedRecords, '$nodeAcceptedRecords');
  const record = parseHashHmacRaw(rawString); recordShape(record, expectedCallOrdinal); accepted(record.nodeComparable, '$.nodeComparable');
  const errorDiagnostics = []; same(record.nodeComparable, nodeAcceptedRecords, '$.nodeComparable', errorDiagnostics);
  namespace(record, true); provider(record, true, expectedNativeConstants); policies(record, true);
  return { record, rawString, comparison: { passed: true, callOrdinal: expectedCallOrdinal, acceptedRecordComparisons: 20, profileOnlyRecordChecks: 8, aliasChecks: 13, namespaceNames: 68, defaultNames: 71, typedNativeHeaderConstants: 9, nativeHeaderNumbersCompared: true, constantsComparedToNode: false, providerRuntimeIdentityProved: false, namespaceObjectIdentityComparedToNode: false, namespaceAndDefaultDescriptorsComparedToNode: false, finalizedErrorMessagesComparedForParity: false, errorDiagnostics, limitsAreFixtureDeclarations: true, nativeFinalizationOrZeroizationProved: false, runtimeAcceptanceClaim: false } };
}
export function compareHashHmacSequence({ nodeRawStrings, guestRawStrings, fixtureManifest, expectedNativeConstants = C.nativeConstants }) {
  const node = validateHashHmacNodeOracle(nodeRawStrings, { fixtureManifest });
  ordinary(guestRawStrings, '$guestRawStrings');
  requireData(Array.isArray(guestRawStrings) && guestRawStrings.length === 7 && guestRawStrings.every(x => typeof x === 'string'), '$guestRawStrings', 'exact seven durably retained guest strings required');
  const calls = guestRawStrings.map((raw, i) => compareHashHmacReturn(raw, { expectedCallOrdinal: C.guestCallOrdinals[i], nodeAcceptedRecords: node.acceptedByOrdinal[C.guestCallOrdinals[i] - 1], fixtureManifest, expectedNativeConstants }));
  for (const i of [3, 4, 5, 6]) same(calls[i].record, calls[0].record, '$sameOrdinalWholeGuest[' + i + ']');
  return { calls, node, summary: { passed: true, guestStrings: 7, nodeStrings: 3, guestCallOrdinals: C.guestCallOrdinals.slice(), jcoRetainedCalls: 3, jcoFreshCalls: 1, freshWasmtimeCalls: 3, acceptedRecordComparisons: 140, separateNativePolicyChecks: 56, sameOrdinalWholeGuestComparisons: 4, fullNodeGuestJsonParityClaim: false, sourceOrProcessAuthorityGranted: false, runtimeAcceptanceClaim: false } };
}
