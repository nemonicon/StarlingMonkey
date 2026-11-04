// Host-side checks for the joint native foundation fixture, not a body adapter.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { checkStreamWebReport } from './assert-stream-web-report.mjs';
import { checkProtectedAbortReport } from './assert-protected-abort-report.mjs';
const eventsOracle = JSON.parse(readFileSync(new URL('../foundation-events/native-node-results.json', import.meta.url)));
export function checkFoundationsHTTPReport(body, audit) {
  if (!audit.foundationsIntegrationFixture) return;
  const report = body.native.foundations, expected = audit.foundationOracles;
  assert.equal(report.schema, audit.protectedAbortFoundationsFixture ? 5 : audit.streamWebFoundationsFixture ? 4 : audit.utilFoundationsFixture ? 3 : audit.expandedFoundationsFixture ? 2 : 1); assert(report.calls >= 1);
  assert.equal(report.calls, body.componentInstanceRequestCount);
  assert.equal(report.aliases.phase, 'deployed'); assert.equal(report.aliases.firstDeployedCall, report.calls === 1);
  assert.equal(report.aliases.canonicalStaticLoaded, true); assert.equal(report.aliases.computedBareImports, true);
  assert.deepEqual(report.aliases.aliases.map(alias => alias.id), expected.dynamicBareAliases);
  const types = ['object', 'object', 'object', 'object', 'object', 'function',
    ...(audit.expandedFoundationsFixture ? ['object', 'function', 'function', 'object'] : []),
    ...(audit.utilFoundationsFixture ? ['object', 'object', 'object'] : []),
    ...(audit.streamWebFoundationsFixture ? ['object'] : [])];
  report.aliases.aliases.forEach((alias, index) => {
    assert.equal(alias.namespaceType, 'object'); assert.equal(alias.defaultType, types[index]); assert(alias.exportCount > 0);
    for (const flag of ['cache', 'exportValues', 'defaultIdentity']) assert.equal(alias[flag], true);
    assert.equal(alias.thenType, 'undefined');
  });
  assert.equal(report.aliases.rejectedCall, 'ERR_SM_NODE_UNSUPPORTED'); assert.equal(report.aliases.rejectedConstruction, 'ERR_SM_NODE_UNSUPPORTED');
  assert.deepEqual(report.aliases.typedConstants, { pathSep: 'string', eventErrorMonitor: 'symbol', captureRejections: 'boolean', defaultMaxListeners: 'number' });
  const path = report.path;
  for (const count of ['lexical', 'globs', 'budgets', 'acceptedAdversarial']) assert.equal(path[count], expected.path[count]);
  assert.equal(path.calls, report.calls); assert.equal(path.invalid, 12);
  for (const flag of ['snapshotPure', 'identities', 'mutableDefaults', 'noEntropy']) assert.equal(path[flag], true);
  const events = report.events;
  assert.equal(events.failure, undefined, JSON.stringify(events.failure)); assert.equal(events.calls, report.calls); assert.equal(events.snapshotTicks, report.calls + 1);
  assert.equal(events.namespaceIdentity, true); assert.deepEqual(events.cases, eventsOracle.cases); assert.deepEqual(events.nativeCases, eventsOracle.nativeCases); assert.deepEqual(events.profile, expected.events.profile);
  assert.deepEqual(events.commonJS, { same: true, constructorAlias: true, defaultProperty: 'undefined', errorMonitorType: 'symbol', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  if (!audit.expandedFoundationsFixture) return;
  assert.deepEqual(report.aliases.newDeferred, [
    'string_decoder.encoding', 'assert.deepStrictEqual', 'assert.CallTracker', 'querystring.unescapeBuffer.nonstring',
    ...(audit.utilFoundationsFixture ? ['util.inspect', 'util/types.isProxy', 'sys.callbackify'] : []),
    ...(audit.streamWebFoundationsFixture ? ['stream/web.CompressionStream', 'stream/web.DecompressionStream'] : []),
  ].map(operation => ({ operation, code: 'ERR_SM_NODE_UNSUPPORTED' })));
  const decoder = report.stringDecoder;
  assert.equal(decoder.failure, undefined, JSON.stringify(decoder.failure)); assert.equal(decoder.calls, report.calls);
  for (const key of ['sequences', 'writes', 'genericCases', 'preservedOrderingDeviations']) assert.equal(decoder[key], expected.stringDecoder[key]);
  assert.equal(decoder.mutationChecks, 2); assert.equal(decoder.detachedInternalStateChecks, 5);
  assert.equal(decoder.primordialReplacementCalls, 0); assert.equal(decoder.nativeAliases, 2);
  for (const flag of ['commonJS', 'snapshotResumption', 'identities', 'noGlobalPollution', 'passed']) assert.equal(decoder[flag], true);
  assert(['unavailable in guest', 'explicitly rejected by private candidate'].includes(decoder.shared));
  const assertion = report.assert;
  assert.equal(assertion.failure, undefined, JSON.stringify(assertion.failure)); assert.equal(assertion.calls, report.calls);
  assert.equal(assertion.snapshotCount, report.calls); assert.equal(assertion.snapshotIdentity, true); assert.equal(assertion.namespaceIdentity, true);
  assert.deepEqual(assertion.cases, expected.assert.cases); assert.deepEqual(assertion.profile, expected.assert.profile);
  assert.deepEqual(assertion.aliases, { names: expected.assert.cases[0].result, strictNames: expected.assert.cases[0].result,
    canonicalNamespaceStable: true, bareCache: true, rootValues: true, strictValues: true,
    moduleTag: '[object Module]', nullNamespacePrototype: true, thenType: 'undefined', sharedMutation: true });
  assert.deepEqual(assertion.commonJS, { rootType: 'function', strictType: 'function', same: true, strictGraph: true,
    aliasOverrides: true, defaultProperty: 'undefined', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  const querystring = report.querystring;
  assert.equal(querystring.failure, undefined, JSON.stringify(querystring.failure)); assert.equal(querystring.calls, report.calls);
  assert.equal(querystring.snapshotByte, 65+report.calls); assert.equal(querystring.snapshotValues, 2+report.calls);
  assert.equal(querystring.snapshotIdentity, true); assert.equal(querystring.namespaceIdentity, true);
  assert.deepEqual(querystring.cases, expected.querystring.cases); assert.deepEqual(querystring.profile, expected.querystring.profile);
  assert.deepEqual(querystring.aliases, { names: expected.querystring.cases[0].result.names,
    canonicalNamespaceStable: true, bareCache: true, sharedValues: true, moduleTag: '[object Module]',
    nullNamespacePrototype: true, thenType: 'undefined', sharedMutation: true, privateBuffer: true });
  assert.deepEqual(querystring.commonJS, { type: 'object', same: true, encodeAlias: true, decodeAlias: true,
    nullParsePrototype: true, defaultProperty: 'undefined', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  if (!audit.utilFoundationsFixture) return;
  const util = report.util;
  assert.equal(util.failure, undefined, util.failure); assert.equal(util.calls, report.calls);
  const variant = expected.util.variants.find(value => JSON.stringify(value.features) === JSON.stringify(util.cases.features));
  assert(variant, 'Validated util feature variant'); assert.deepEqual(util.cases, variant);
  assert.deepEqual(util.exports, expected.util.expectedExports);
  assert.equal(util.snapshotIdentity, true); assert.equal(util.noFacadeBundled, true);
  assert.equal(util.deferred.length, 108);
  assert(util.deferred.every(value => value.code === 'ERR_SM_NODE_UNSUPPORTED' && value.profile === 'sm-node-22.14.0-m0.7'));
  assert.deepEqual(util.aliases, { bareCanonicalNamespaces: true, cachedDynamicNamespaces: true,
    sysNamespaceDistinct: true, sharedDefault: true, sharedTypes: true, thenType: 'undefined', namespacePrototypeNull: true });
  assert.deepEqual(util.common, { same: true, textIdentity: true, customSymbol: true, defaultProperty: 'undefined' });
  assert.deepEqual(util.hardening, { unsupportedCode: 'ERR_SM_NODE_UNSUPPORTED', invalidCode: 'ERR_INVALID_ARG_TYPE', setterCalls: 0, depth: 4 });
  if (audit.streamWebFoundationsFixture) checkStreamWebReport(report.streamWeb, expected.streamWeb, report.calls);
  if (audit.protectedAbortFoundationsFixture) checkProtectedAbortReport(report.protectedAbort, expected.protectedAbort, report.calls);
}
