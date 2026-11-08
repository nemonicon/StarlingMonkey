'use strict';

// Node-only conformance fixtures. Every helper invocation uses the real fs.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const HELPER = path.resolve(__dirname,
  '../next-fs-callback-app-build-v1/fixture/app/api/cache/callback-generation.cjs');
const HELPER_SHA256 = '48186fd2099c7a3c361971784c8578473b487b95a41921ddf036e0d1b0fa63b1';
const IDS = Object.freeze(['lazy-import', 'sequential', 'pending-busy', 'corrupt-record',
  'generation-limits', 'unexpected-member', 'oversized-record', 'hardlink-alias']);
const encode = (generation) => '{"schemaVersion":1,"generation":' + generation + '}\n';
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');

function describeThrown(value) {
  return { type: typeof value, name: value && typeof value.name === 'string' ? value.name : null,
    code: value && typeof value.code === 'string' ? value.code : null,
    message: value && typeof value.message === 'string' ? value.message : String(value) };
}
function helperSource() {
  const stat = fs.lstatSync(HELPER);
  assert(stat.isFile() && !stat.isSymbolicLink() && stat.nlink === 1);
  assert.equal(fs.realpathSync(HELPER), HELPER);
  const bytes = fs.readFileSync(HELPER);
  assert.equal(bytes.length, 5490);
  assert.equal(digest(bytes), HELPER_SHA256);
  const final = fs.lstatSync(HELPER);
  for (const field of ['dev', 'ino', 'size', 'mode', 'nlink', 'mtimeMs', 'ctimeMs'])
    assert.equal(final[field], stat[field], 'Helper Source read bookend: ' + field);
  return { path: HELPER, sha256: HELPER_SHA256, bytes: bytes.length };
}
function snapshot(root) {
  const rows = [];
  function walk(directory) {
    for (const name of fs.readdirSync(directory).sort()) {
      const absolute = path.join(directory, name), stat = fs.lstatSync(absolute);
      assert(!stat.isSymbolicLink(), 'No symbolic fixture paths are selected');
      const row = { path: path.relative(root, absolute), mode: stat.mode & 0o777,
        nlink: stat.nlink, kind: stat.isDirectory() ? 'directory' : 'file' };
      if (stat.isDirectory()) { rows.push(row); walk(absolute); }
      else {
        assert(stat.isFile() && stat.size <= 512);
        const bytes = fs.readFileSync(absolute);
        assert.equal(bytes.length, stat.size);
        Object.assign(row, { bytes: bytes.length, sha256: digest(bytes), base64: bytes.toString('base64') });
        rows.push(row);
      }
      assert(rows.length <= 32, 'Snapshot fixture member bound');
    }
  }
  walk(root);
  return rows;
}

function runCallbackStateSuite({ testRoot, report }) {
  assert(report && Object.getPrototypeOf(report) === Object.prototype);
  assert.equal(fs.realpathSync(testRoot), testRoot);
  assert(fs.lstatSync(testRoot).isDirectory());
  assert.deepEqual(fs.readdirSync(testRoot), []);
  Object.assign(report, { schemaVersion: 1, suite: 'NEXT_FS_CALLBACK_STATE_CONFORMANCE_V1',
    executionKind: 'node-only', guestExecuted: false, fullNextAccepted: false,
    helperSource: helperSource(), helperImported: false, helperCalls: 0, passed: false, cases: [] });
  const originalCwd = process.cwd();
  let helper;
  function app(name, withCache = true) {
    const root = path.join(testRoot, name, 'app');
    fs.mkdirSync(root, { recursive: true, mode: 0o700 });
    if (withCache) fs.mkdirSync(path.join(root, '.next/cache'), { recursive: true, mode: 0o700 });
    return root;
  }
  function namespace(root) {
    const directory = path.join(root, '.next/cache/app-callback-generation-v1');
    fs.mkdirSync(directory, { mode: 0o700 });
    return directory;
  }
  function invoke(root) {
    process.chdir(root);
    try { ++report.helperCalls; return helper.nextCallbackGeneration(); }
    finally { process.chdir(originalCwd); }
  }
  function rejectedWithoutMutation(row, root, expectedCode) {
    const before = snapshot(root);
    let rejected = false, original;
    try { invoke(root); } catch (error) { rejected = true; original = error; }
    const after = snapshot(root);
    Object.assign(row, { expectedCode, originalRejection: rejected ? describeThrown(original) : null, before, after });
    assert(rejected, 'Selected invalid fixture must reject');
    assert.equal(original && original.code, expectedCode);
    assert.deepEqual(after, before, 'Rejected fixture bytes/membership/modes/link counts must remain unchanged');
  }
  function group(id, body) {
    const row = { id, passed: false }; report.cases.push(row);
    try { body(row); row.passed = true; }
    catch (error) { row.failure = describeThrown(error); throw error; }
  }
  try {
    group('lazy-import', (row) => {
      const root = app('01-lazy-import', false), before = snapshot(root);
      assert.equal(require.cache[HELPER], undefined);
      process.chdir(root);
      try { helper = require(HELPER); report.helperImported = true; }
      finally { process.chdir(originalCwd); }
      assert.equal(typeof helper.nextCallbackGeneration, 'function');
      const after = snapshot(root);
      assert.deepEqual(after, before);
      assert.equal(fs.existsSync(path.join(root, '.next/cache')), false);
      Object.assign(row, { cacheParentAbsentBeforeAndAfter: true, before, after });
    });
    group('sequential', (row) => {
      const root = app('02-sequential'), state = path.join(root, '.next/cache/app-callback-generation-v1/generation.json');
      const first = invoke(root), firstBytes = fs.readFileSync(state, 'utf8');
      assert.equal(first, 1); assert.equal(firstBytes, encode(1));
      const afterFirst = snapshot(root);
      const second = invoke(root), secondBytes = fs.readFileSync(state, 'utf8');
      assert.equal(second, 2); assert.equal(secondBytes, encode(2));
      assert.deepEqual(fs.readdirSync(path.dirname(state)), ['generation.json']);
      Object.assign(row, { returned: [first, second], canonicalRecords: [firstBytes, secondBytes], afterFirst, afterSecond: snapshot(root) });
    });
    group('pending-busy', (row) => {
      const root = app('03-pending-busy'), directory = namespace(root);
      fs.writeFileSync(path.join(directory, 'generation.json'), encode(7), { flag: 'wx' });
      fs.writeFileSync(path.join(directory, 'generation.pending'), 'incomplete-pending\n', { flag: 'wx' });
      rejectedWithoutMutation(row, root, 'ERR_SM_CALLBACK_BUSY');
    });
    group('corrupt-record', (row) => {
      const root = app('04-corrupt-record'), directory = namespace(root);
      fs.writeFileSync(path.join(directory, 'generation.json'), encode(0), { flag: 'wx' });
      rejectedWithoutMutation(row, root, 'ERR_SM_CALLBACK_CORRUPT');
    });
    group('generation-limits', (row) => {
      row.subcases = [];
      for (const [label, generation] of [['above-limit', 1000001], ['at-limit', 1000000]]) {
        const root = app('05-generation-limits/' + label), directory = namespace(root);
        fs.writeFileSync(path.join(directory, 'generation.json'), encode(generation), { flag: 'wx' });
        const detail = { label }; row.subcases.push(detail);
        rejectedWithoutMutation(detail, root, 'ERR_SM_CALLBACK_LIMIT');
      }
    });
    group('unexpected-member', (row) => {
      const root = app('06-unexpected-member'), directory = namespace(root);
      fs.writeFileSync(path.join(directory, 'unselected.txt'), 'keep-this-byte-exact\n', { flag: 'wx' });
      rejectedWithoutMutation(row, root, 'ERR_SM_CALLBACK_CORRUPT');
    });
    group('oversized-record', (row) => {
      const root = app('07-oversized-record'), directory = namespace(root);
      fs.writeFileSync(path.join(directory, 'generation.json'), 'x'.repeat(129), { flag: 'wx' });
      rejectedWithoutMutation(row, root, 'ERR_SM_CALLBACK_CORRUPT');
    });
    group('hardlink-alias', (row) => {
      const root = app('08-hardlink-alias'), directory = namespace(root);
      const reference = path.join(root, 'reference.json'), state = path.join(directory, 'generation.json');
      fs.writeFileSync(reference, encode(9), { flag: 'wx' }); fs.linkSync(reference, state);
      assert.equal(fs.lstatSync(state).nlink, 2);
      rejectedWithoutMutation(row, root, 'ERR_SM_CALLBACK_CORRUPT');
    });
    assert.deepEqual(report.cases.map((row) => row.id), IDS);
    assert.equal(report.helperCalls, 9);
    assert.deepEqual(helperSource(), report.helperSource);
    report.passed = report.cases.every((row) => row.passed === true);
    return report;
  } finally { process.chdir(originalCwd); }
}

module.exports = { runCallbackStateSuite, describeThrown };
