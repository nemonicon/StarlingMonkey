// Host-side checks for the installed m0.9 API corpus, never bundled into a guest.
import assert from 'node:assert/strict';
export function checkStreamWebReport(report, expected, calls) {
  assert.equal(report.failure, undefined, JSON.stringify(report.failure));
  assert.equal(report.passed, true); assert.equal(report.calls, calls);
  assert.deepEqual(report.names, expected.names);
  for (const [name, count] of Object.entries({constructors:41, codecs:250, cancellations:4,
    guards:24, views:12, controllers:6, iterations:67, data:26})) assert.equal(report[name], count, name);
  assert.deepEqual(report.guardDeviations, ['min-two','proxy-genuine-receiver','shadowed-view-fields']);
  assert.deepEqual(report.dataDeviations, ['released-reader-rejects-before-transfer']);
  assert.equal(report.policies.checks.length, 14); assert.equal(report.dataPolicies.checks.length, 6);
  assert.deepEqual(report.ownErrors, {checks:9,inheritedGets:0,inheritedSets:0});
  for (const key of ['codecIntrinsics','iterationIntrinsics','dataIntrinsics']) assert.equal(report[key].replacementInvocations, 0);
  assert.equal(report.aliases, 2); assert.equal(report.commonJS, true); assert.equal(report.snapshotResumption, true);
  assert.deepEqual(report.identities, {globalNativeConstructors:10,hiddenNativeConstructors:3,
    uninstalledGlobalCodecs:true,signalMissing:true});
  assert.equal(report.fixtureRegistryUsed, false); assert.equal(report.applicationFactoryUsed, false);
}
