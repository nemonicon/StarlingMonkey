// Read-only offline regression check for retained host evidence. No app execution.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname, resolve, join} from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2] ?? join(here, 'results'));
const json = async path => JSON.parse(await readFile(path, 'utf8'));
const summary = await json(join(root, 'summary.json'));
const contract = await json(join(here, '../fixture-contract.json'));
const expectedRuns = [
  {name: 'next-http-bridge-v1', rawExitCode: 1, httpObserved: 22, httpPassed: 0, browserPassed: 0, passed: false},
  {name: 'next-http-bridge-v2', rawExitCode: 0, httpObserved: 24, httpPassed: 24, browserPassed: 0, passed: true},
  {name: 'next-http-bridge-v3-browser', rawExitCode: 0, httpObserved: 24, httpPassed: 24, browserPassed: 2, passed: true},
];
const modulePlan = [{name: 'next-http-bridge-module-v1', rawExitCode: 0, httpObserved: 24, httpPassed: 24, browserPassed: 2, passed: true}];
const plan = summary.runs.length === 1 && summary.runs[0].name === modulePlan[0].name ? modulePlan : expectedRuns;
assert.equal(summary.suite, 'FULL_NEXT_HOST_HTTP_BRIDGE_RESULTS_V1');
assert.equal(summary.runs.length, plan.length);
for (let i = 0; i < plan.length; i++) for (const [key, value] of Object.entries(plan[i])) assert.deepEqual(summary.runs[i][key], value, key);
assert.equal(summary.copies.length, plan === modulePlan ? 47 : 108);
assert.equal(summary.nativeGuestExecuted, false);
assert.equal(summary.componentExecuted, false);
const files = new Set();
for (const row of summary.copies) {
  const file = resolve(root, row.file);
  assert(file.startsWith(root + '/') && !files.has(row.file)); files.add(row.file);
  const bytes = await readFile(file);
  assert.equal(bytes.length, row.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), row.sha256);
}
for (const item of summary.runs) {
  const directory = join(root, item.name);
  const result = await json(join(directory, 'result.json'));
  const terminal = await json(join(directory, 'monitor/terminal.json'));
  assert.equal(result.guestExecuted, false);
  assert.equal(result.applicationModified, false);
  assert.equal(result.node, 'v22.14.0');
  assert.deepEqual(result.installed, {next: '16.4.5', react: '19.3.1', 'react-dom': '19.3.1'});
  assert.equal(result.http.length, item.httpObserved);
  assert.equal(result.http.filter(row => row.passed).length, item.httpPassed);
  assert.equal(result.browser?.tests.filter(row => row.passed).length ?? 0, item.browserPassed);
  assert.equal(terminal.rawExitCode, item.rawExitCode);
  for (const key of ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']) assert.deepEqual(terminal[key], []);
  for (const key of ['allObservedOwnedGroupsGone', 'parentOwnedGroupGone']) assert.equal(terminal[key], true);
  for (const key of ['timeout', 'forcedCleanup']) assert.equal(terminal[key], false);
  if (!item.passed) { assert.equal(result.passed, false); assert.equal(item.httpPassed, 0); continue; }
  assert.equal(result.passed, true); assert.deepEqual(result.errors, []); assert.deepEqual(result.transportErrors, []);
  assert.equal(result.http.length, contract.requests.length + 1);
  const bodies = new Map();
  for (const expected of contract.requests) {
    const row = result.http.find(row => row.id === expected.id); assert(row, expected.id);
    const bytes = await readFile(join(directory, 'responses', expected.id + '.txt'));
    assert.equal(bytes.length, row.bodyBytes);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), row.bodySha256);
    const body = bytes.toString('utf8'); bodies.set(expected.id, body);
    assert.equal(row.status, expected.status); assert.equal(row.passed, true); assert.deepEqual(row.failures, []);
    for (const text of expected.includes ?? []) assert(body.includes(text), expected.id + ': ' + text);
    if (expected.json) { const value = JSON.parse(body); for (const [key, item] of Object.entries(expected.json)) assert.deepEqual(value[key], item); }
    if (expected.location) assert.equal(row.headers.location, expected.location);
    for (const [key, value] of Object.entries(expected.responseHeaders ?? {})) assert.equal(row.headers[key], value);
    for (const [key, values] of Object.entries(expected.responseHeaderIncludes ?? {})) for (const value of values) assert(row.headers[key].includes(value));
    if (expected.equalJsonTo) assert.equal(body, bodies.get(expected.equalJsonTo));
  }
  const action = result.http.find(row => row.id === 'server-action-submit');
  assert.equal(action.status, 303); assert.equal(action.passed, true);
  assert.equal(action.headers.location, '/action-result?value=fixture-action');
  assert.equal(result.cacheInvalidation.before.generation, 1);
  assert.equal(result.cacheInvalidation.after.generation, 2);
  const chunks = await json(join(directory, 'stream-chunks.json'));
  const texts = chunks.map(row => { const b = Buffer.from(row.base64, 'base64'); assert.equal(b.length, row.bytes); return b.toString('utf8'); });
  const shell = texts.findIndex(text => text.includes('NEXT_STREAM_SHELL'));
  const ready = texts.findIndex(text => text.includes('NEXT_STREAM_READY'));
  assert.equal(shell, result.streaming.shellChunk); assert.equal(ready, result.streaming.readyChunk);
  assert(shell >= 0 && ready > shell); assert.equal(chunks.length, result.streaming.chunks);
  if (item.browserPassed) {
    assert.equal(result.browserExit.code, 0); assert.equal(result.browser.passed, true);
    assert.equal(result.browser.tests.length, 2); assert(result.browser.tests.every(row => row.passed && !row.timedOut));
    for (const key of ['pageerrors', 'consoleerrors', 'failedrequests', 'errors']) assert.deepEqual(result.browser[key], []);
    const counter = result.browser.tests.find(row => row.id === 'client-counter');
    assert.equal(counter.observations.initial, 'NEXT_CLIENT_COUNT:0'); assert.equal(counter.observations.afterClick, 'NEXT_CLIENT_COUNT:1');
    const action = result.browser.tests.find(row => row.id === 'server-action');
    assert.equal(action.observations.actualFormPostObserved, true);
    assert.equal(action.observations.builtActionIdNotHardcoded, true);
  }
}
console.log(JSON.stringify({suite: 'FULL_NEXT_HOST_BRIDGE_RETAINED_RESULTS_CHECK', passed: true,
  files: files.size, runs: summary.runs.length, guestExecuted: false}));
