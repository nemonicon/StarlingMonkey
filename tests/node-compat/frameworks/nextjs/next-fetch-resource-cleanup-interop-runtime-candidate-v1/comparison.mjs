// Pure captured-DATA comparison. No Node oracle, guest or constructor invocation.
import assert from 'node:assert/strict';
const IDS = Object.freeze([
  'cjs-dynamic-builtin', 'default-require-cache-identity', 'same-namespace',
  'thenable-default-not-assimilated', 'class-default-construction',
  'undefined-default', 'nan-default', 'negative-zero-default', 'throw-null-preserved',
  'query-refusal', 'fragment-refusal', 'encoded-separator-refusal',
  'uppercase-scheme-refusal', 'extension-refusal', 'url-byte-limit-refusal',
  'decoded-path-limit-refusal',
]);
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function keys(value, expected) {
  assert(object(value));
  assert.deepEqual(Object.keys(value).sort(), [...expected].sort());
}
function namespace(value, extra) {
  keys(value, ['prototypeNull', 'ownNames', 'noOwnThen', 'defaultSame', ...extra]);
  assert.equal(value.prototypeNull, true); assert.deepEqual(value.ownNames, ['default']);
  assert.equal(value.noOwnThen, true); assert.equal(value.defaultSame, true);
}
const undefinedData = {type: 'undefined'};
function refusal(value, specifier, reason) {
  keys(value, ['rejected', 'isTypeError', 'code', 'operation', 'moduleMatchesActualSpecifier', 'error']);
  assert.equal(value.rejected, true); assert.equal(value.isTypeError, true);
  assert.equal(value.code, 'ERR_SM_MODULE_FILE_URL_UNSUPPORTED');
  assert.equal(value.operation, 'module_file_url'); assert.equal(value.moduleMatchesActualSpecifier, true);
  const e = value.error;
  keys(e, ['type', 'isNull', 'name', 'message', 'code', 'operation', 'module']);
  assert.equal(e.type, 'object'); assert.equal(e.isNull, false);
  assert.deepEqual(e.name, undefinedData);
  assert.deepEqual(e.message, {type: 'string', value: 'CommonJS file URL import is unsupported: ' + reason});
  assert.deepEqual(e.code, {type: 'string', value: 'ERR_SM_MODULE_FILE_URL_UNSUPPORTED'});
  assert.deepEqual(e.operation, {type: 'string', value: 'module_file_url'});
  // The sealed Source collector retains at most512 chars per string own field;
  // moduleMatchesActualSpecifier is separately the real full-value comparison.
  assert.deepEqual(e.module, {type: 'string', value: specifier.slice(0, 512)});
}
export function validateInteropResponse(value) {
  keys(value, ['schemaVersion', 'suite', 'mode', 'call', 'caseCount', 'expectedCaseCount',
    'records', 'exactCaseIds', 'profilePassed', 'guardRefusalIsNodeCompatibilityPass',
    'nodeReferenceExecuted', 'applicationImported', 'fullNextClaim',
    'namespaceLimit8192Exercised', 'symlinkReentrancyRealmOrRaceParityProved']);
  assert.equal(value.schemaVersion, 1); assert.equal(value.suite, 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1');
  assert.equal(value.mode, 'interop'); assert.equal(value.call, 1);
  assert.equal(value.caseCount, 16); assert.equal(value.expectedCaseCount, 16);
  assert.equal(value.exactCaseIds, true); assert.equal(value.profilePassed, true);
  for (const key of ['guardRefusalIsNodeCompatibilityPass', 'nodeReferenceExecuted', 'applicationImported',
    'fullNextClaim', 'namespaceLimit8192Exercised', 'symlinkReentrancyRealmOrRaceParityProved'])
    assert.equal(value[key], false, key);
  assert(Array.isArray(value.records)); assert.deepEqual(value.records.map(row => row.id), IDS);
  for (const row of value.records) {
    keys(row, ['id', 'passed', 'observation']); assert.equal(row.passed, true); assert(object(row.observation));
  }
  const observations = value.records.map(row => row.observation);
  assert.deepEqual(observations[0], {sameJoin: true, joined: '/probe/child'});
  namespace(observations[1], ['filename', 'loaded', 'cacheSame', 'marker']);
  assert.equal(observations[1].filename, '/probe/target.cjs'); assert.equal(observations[1].loaded, true);
  assert.equal(observations[1].cacheSame, true); assert.equal(observations[1].marker, 'target-value');
  assert.deepEqual(observations[2], {same: true});
  namespace(observations[3], ['thenReads']); assert.equal(observations[3].thenReads, 0);
  namespace(observations[4], ['prototypeSame', 'result']);
  assert.equal(observations[4].prototypeSame, true); assert.equal(observations[4].result, 'class:7');
  for (const i of [5, 6, 7]) { namespace(observations[i], ['expectedPrimitive']); assert.equal(observations[i].expectedPrimitive, true); }
  assert.deepEqual(observations[8], {rejectedNull: true, noCompletedCacheEntry: true,
    error: {type: 'object', isNull: true, value: null, name: undefinedData, message: undefinedData,
      code: undefinedData, operation: undefinedData, module: undefinedData}});
  const target = 'file:///probe/target.cjs';
  const canonical = 'Only bounded canonical local file URLs without query/fragment are selected';
  const bounded = 'Only bounded absolute .cjs files are selected';
  for (const [i, specifier, reason] of [
    [9, target + '?probe=1', canonical], [10, target + '#probe', canonical],
    [11, 'file:///probe%2ftarget.cjs', 'Encoded path separator is unsupported'],
    [12, 'FILE:///probe/target.cjs', canonical], [13, 'file:///probe/target.js', bounded],
    [14, 'file:///probe/' + 'x'.repeat(12297) + '.cjs', canonical],
    [15, 'file:///probe/' + 'x'.repeat(4096) + '.cjs', bounded],
  ]) refusal(observations[i], specifier, reason);
  return {interopProfileMatched: true, cases: 16, builtinDynamicImportObserved: true,
    defaultRequireCacheIdentityObserved: true, sameNamespaceObserved: true,
    thenableDefaultNotAssimilatedObserved: true, classAndSelectedPrimitivePredicatesObserved: true,
    originalNullThrowObserved: true, selectedNativeRefusalsObserved: 7,
    nodeCompatibilityAccepted: false, namespaceLimit8192Exercised: false,
    symlinkReentrancyRealmOrRaceParityProved: false, fullNextAcceptance: false};
}
