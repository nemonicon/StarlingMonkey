// Host-only validation of the exact positive/handled m0.10 native corpus.
// Fatal initializer/deployed cases live in the separate focused runner.
import assert from 'node:assert/strict';

export function checkProtectedAbortReport(report, expected, calls) {
  assert.equal(report.failure, undefined, JSON.stringify(report.failure));
  assert.equal(report.calls, calls);
  assert.deepEqual(expected.counts, { public: 16, nested: 4, receivers: 9, total: 29 });
  assert.equal(report.publicCases.length, 16);
  assert.equal(report.nestedOnceCases.length, 4);
  assert.equal(report.receiverCases.length, 9);
  assert.deepEqual(report.publicCases, expected.publicCases);
  assert.deepEqual(report.nestedOnceCases, expected.nestedOnceCases);
  assert.deepEqual(report.receiverCases, expected.receiverCases);
  assert.deepEqual(report.namespace, {
    names: expected.names, defaultNamed: true, canonicalCached: true,
    aliasValues: true, defaultAlias: true, then: 'undefined',
    errorMonitorType: 'symbol', captureRejectionSymbol: true,
    defaultMaxListeners: 10, captureRejections: false, usingDomains: false,
  });
  assert.deepEqual(report.commonJS, {
    same: true, constructorAlias: true, defaultProperty: 'undefined',
    addAbortListenerType: 'function', errorMonitorType: 'symbol',
    rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED',
  });
  assert.equal(report.profileErrors.hooks, 0);
  assert.equal(report.profileErrors.ambient, 0);
  assert.deepEqual(report.profileErrors.errors.map(error => error.name), [
    'once-call', 'once-new', 'on-call', 'on-new',
    'async-resource-call', 'async-resource-new', 'invalid-signal',
  ]);
  for (const error of report.profileErrors.errors) {
    assert.equal(error.profile, expected.profileVersion);
    assert.equal(error.module, 'node:events');
    assert.equal(error.own, true);
    assert.equal(error.type, error.name === 'invalid-signal' ? 'TypeError' : 'Error');
    assert.equal(error.operation, error.name.startsWith('once') ? 'once'
      : error.name.startsWith('on-') ? 'on'
      : error.name.startsWith('async-resource') ? 'EventEmitterAsyncResource' : 'addAbortListener');
    assert.equal(error.code, error.name === 'invalid-signal' ? 'ERR_INVALID_ARG_TYPE' : 'ERR_SM_NODE_UNSUPPORTED');
  }
  assert.deepEqual(report.snapshot, {
    before: calls === 1 ? 0 : 1, after: 1,
    signalThis: true, currentTarget: true, aborted: false,
  });
  assert.deepEqual(report.symbol.descriptor, expected.nodeSymbol.descriptor);
  // The target well-known symbol is observed separately: Node registry
  // identity/description are explicit deviations, not normalized into parity.
  assert.equal(typeof report.symbol.description, 'string');
  assert(report.symbol.registryKey === null || typeof report.symbol.registryKey === 'string');
  assert.equal(typeof report.symbol.sameAsNodeRegistry, 'boolean');
}
