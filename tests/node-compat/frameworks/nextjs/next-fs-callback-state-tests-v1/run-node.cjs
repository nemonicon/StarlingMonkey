'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { runCallbackStateSuite, describeThrown } = require('./cases.cjs');
const PREFIX = '/private/tmp/starling-node-compat/next-fs-callback-state-tests-v1-';
const report = { passed: false };
let failed = false, primary, outputRoot, createdRoot = false;
try {
  assert.equal(process.argv.length, 3, 'Node run-node.cjs FRESH_ABSOLUTE_TEST_ROOT');
  outputRoot = process.argv[2];
  assert.equal(path.resolve(outputRoot), outputRoot);
  assert(outputRoot.startsWith(PREFIX));
  const runId = outputRoot.slice(PREFIX.length), match = /^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId);
  assert(match && match[0] === runId, 'Exact fresh run suffix');
  assert.equal(fs.realpathSync(path.dirname(outputRoot)), path.dirname(outputRoot));
  fs.mkdirSync(outputRoot, { mode: 0o700 }); // EEXIST fails; no reuse or cleanup.
  createdRoot = true;
  assert.equal(fs.lstatSync(outputRoot).mode & 0o777, 0o700);
  assert.equal(runCallbackStateSuite({ testRoot: outputRoot, report }), report);
  assert.equal(report.passed, true);
} catch (error) { failed = true; primary = error; report.passed = false; report.originalFailure = describeThrown(error); }
try {
  const json = JSON.stringify(report, null, 2) + '\n';
  assert(Buffer.byteLength(json, 'utf8') <= 65536, 'Bounded conformance report');
  if (createdRoot)
    fs.writeFileSync(path.join(outputRoot, 'report.json'), json, { flag: 'wx', mode: 0o600 });
  fs.writeFileSync(1, json);
} catch (error) {
  if (!failed) { failed = true; primary = error; }
  fs.writeFileSync(2, JSON.stringify({ publicationFailed: true, originalFailure: describeThrown(primary) }) + '\n');
}
process.exitCode = failed ? 1 : 0;
