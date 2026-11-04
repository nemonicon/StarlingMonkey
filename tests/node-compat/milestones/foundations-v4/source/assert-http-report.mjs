// Host-side checks for the joint native foundation fixture, not a body adapter.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const eventsOracle = JSON.parse(readFileSync(new URL('../foundation-events/native-node-results.json', import.meta.url)));
export function checkFoundationsHTTPReport(body, audit) {
  if (!audit.foundationsIntegrationFixture) return;
  const report = body.native.foundations, expected = audit.foundationOracles;
  assert.equal(report.schema, 1); assert(report.calls >= 1);
  assert.equal(report.calls, body.componentInstanceRequestCount);
  assert.equal(report.aliases.phase, 'deployed'); assert.equal(report.aliases.firstDeployedCall, report.calls === 1);
  assert.equal(report.aliases.canonicalStaticLoaded, true); assert.equal(report.aliases.computedBareImports, true);
  assert.deepEqual(report.aliases.aliases.map(alias => alias.id), expected.dynamicBareAliases);
  const types = ['object', 'object', 'object', 'object', 'object', 'function'];
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
}
