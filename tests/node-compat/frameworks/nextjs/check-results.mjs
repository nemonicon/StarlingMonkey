// Reusable observation comparator. Never invokes Next, a worker, or a guest.
// Usage: node check-results.mjs BASELINE_RESULTS CURRENT_RESULTS
// Pure injected checks: node check-results.mjs --self-test
import { readFile, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SUITE = 'nextjs-component-compatibility-v1';
const VERSIONS = { node: 'v22.14.0', next: '16.4.5', react: '19.3.1', acceptedRuntime: 'foundations-v13' };
const INSTALLED = { next: '16.4.5', react: '19.3.1', 'react-dom': '19.3.1' };
const STATUSES = new Set(['passed', 'failed', 'refused', 'missing-fixture']);
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']'
  : object(x) ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x);
const same = (a, b) => canonical(a) === canonical(b);

// Recognize only the observed Rolldown aggregate grammar. Separator newlines
// are represented explicitly, not trimmed from diagnostics. Sorting this array
// preserves duplicate blocks (a multiset), prefix, count and every block byte.
// Unknown headers/counts/block shapes remain the original exact string.
export function canonicalRolldownMessage(message) {
  if (typeof message !== 'string') return message;
  const match = /^(Build failed with ([1-9][0-9]*) errors:\n\n)/.exec(message);
  if (!match) return message;
  const count = Number(match[2]);
  if (!Number.isSafeInteger(count) || count < 2 || count > 1024) return message;
  const body = message.slice(match[1].length);
  const pieces = body.split('\n[plugin ');
  const blocks = pieces.map((part, index) => index === 0 ? part : '[plugin ' + part);
  if (blocks.length !== count) return message;
  for (const block of blocks) {
    const lines = block.split('\n');
    if (!/^\[plugin [A-Za-z0-9][A-Za-z0-9_.:/@-]*\](?: [^\n]*)?$/.test(lines[0])
        || !/^Error: [^\n]+$/.test(lines[1] ?? '')
        || lines.slice(2).some(line => !/^    at [^\n]+$/.test(line))) return message;
  }
  return { format: 'recognized-rolldown-multi-error', prefix: match[1], actualErrorCount: count,
    separator: '\n', blocks: blocks.slice().sort() };
}

// Only literal roots reported by this run are normalized, retaining module names
// and original diagnostics. No stack, timestamp or process ID defines a blocker.
function blocker(row, suite) {
  const replacements = [];
  if (typeof suite.output === 'string' && suite.output) replacements.push([suite.output, '<RUN_OUTPUT>']);
  if (typeof row.report.output === 'string' && row.report.output) replacements.push([row.report.output, '<CASE_OUTPUT>']);
  const original = row.report.originalSource?.path;
  if (typeof original === 'string' && original.includes('/application/')) replacements.push([original.split('/application/')[0] + '/application', '<APPLICATION>']);
  replacements.sort((a, b) => b[0].length - a[0].length);
  const normalize = value => typeof value === 'string' ? replacements.reduce((s, [before, after]) => s.split(before).join(after), value) : value;
  const failures = (row.report.failures ?? []).map(f => Object.fromEntries(
    ['stage', 'reason', 'name', 'code', 'message', 'thrownString', 'diagnosticClipped', 'errorPropertiesUnavailable']
      .filter(k => Object.hasOwn(f, k)).map(k => [k, k === 'message' && f.stage === 'bundling' ? canonicalRolldownMessage(normalize(f[k])) : normalize(f[k])])));
  return { status: row.report.status, stage: row.report.stage, reason: normalize(row.report.reason ?? null), failures };
}

/** Pure DATA audit. Evidence maps contain actual retained parsed/string returns.
 * CLI loads them relative to each supplied results.json, never report.output.
 * Missing successful-return evidence is incomplete, rather than silently equal.
 */
export function auditResults(baseline, current, evidence = { baseline: {}, current: {} }) {
  const regressions = [], improvements = [], changedBlockers = [], outstandingKnownFailures = [];
  const coverage = { complete: true, http: {}, wasm: {}, commands: {}, returnComparisons: [] };
  const fail = (scope, id, kind, detail = {}) => regressions.push({ scope, id, kind, ...detail });
  const incomplete = (scope, id, kind, detail = {}) => { coverage.complete = false; fail(scope, id, kind, detail); };
  const oracle = { suite: SUITE, interpretation: 'Exit0 means no observation regression; unchanged known failures remain failures, not Next.js compatibility.', baseline: {}, current: {}, frameworkCompatible: {
    baseline: (baseline?.frameworkCompatible ?? baseline?.fullNextServerInWasm) === true, current: (current?.frameworkCompatible ?? current?.fullNextServerInWasm) === true,
    scope: 'Copied explicit framework claim only; observation comparison never declares Next.js compatible.' } };
  for (const [label, value] of [['baseline', baseline], ['current', current]]) {
    if (!object(value)) { incomplete('input', label, 'results-not-an-object'); continue; }
    oracle[label] = { suite: value.suite, schemaVersion: value.schemaVersion, oraclePassed: value.oraclePassed,
      observationsComplete: value.observationsComplete, requiredDifferentialPassed: value.requiredDifferentialPassed, browserRequested: value.browserRequested, browserWorkerExit: value.browserWorkerExit, browserPassed: value.browser?.passed, versions: Object.fromEntries(Object.keys(VERSIONS).map(k => [k, value[k]])), installedVersions: value.installedVersions };
    if (value.schemaVersion !== 1 || value.suite !== SUITE) incomplete('identity', label, 'suite-or-schema-mismatch');
    for (const [key, expected] of Object.entries(VERSIONS)) if (value[key] !== expected) incomplete('identity', label, 'version-mismatch', { field: key, expected, actual: value[key] ?? null });
    if (!same(value.installedVersions, INSTALLED)) incomplete('identity', label, 'installed-version-mismatch', { expected: INSTALLED, actual: value.installedVersions ?? null });
  }
  if (!object(baseline) || !object(current)) return { oracle, coverage, regressions, improvements, changedBlockers, outstandingKnownFailures };
  if (baseline.oraclePassed !== true || baseline.observationsComplete !== true || !Array.isArray(baseline.errors) || baseline.errors.length) incomplete('oracle', 'baseline', 'baseline-oracle-or-observations-incomplete');
  if (current.oraclePassed !== true) fail('oracle', 'current', 'node-http-oracle-not-passed');
  if (current.observationsComplete !== true) incomplete('coverage', 'current', 'observations-not-complete');
  if (!Array.isArray(current.errors) || current.errors.length) incomplete('oracle', 'current', 'suite-errors', { errors: current.errors ?? null });
  const differentialRequired = baseline.requiredDifferentialPassed === true || current.wasm?.some?.(r => r?.id === 'compat' && r.report?.status === 'passed') === true;
  const differentialObserved = Object.hasOwn(baseline, 'requiredDifferentialPassed') || Object.hasOwn(current, 'requiredDifferentialPassed');
  oracle.requiredDifferentialEnforced = differentialRequired;
  if (differentialRequired) {
    if (current.requiredDifferentialPassed !== true || current.sameSourceDifferential?.performed !== true || current.sameSourceDifferential?.passed !== true
        || !same(current.sameSourceDifferential.node, current.sameSourceDifferential.guest)) fail('oracle', 'current', 'required-same-source-differential-not-passed');
  } else if (differentialObserved) {
    // A complete observed failed compat case can be a regression baseline.
    // Absence or an invented success flag is never silently accepted.
    if (current.requiredDifferentialPassed !== false || current.sameSourceDifferential?.passed !== false) incomplete('oracle', 'current', 'missing-or-inconsistent-known-failing-differential');
    if (baseline.requiredDifferentialPassed === false && current.requiredDifferentialPassed === false) {
      const summarize = x => Object.fromEntries(['performed', 'passed', 'reason', 'actualStage'].filter(k => Object.hasOwn(x ?? {}, k)).map(k => [k, x[k]]));
      const before = summarize(baseline.sameSourceDifferential), after = summarize(current.sameSourceDifferential);
      if (!same(before, after)) changedBlockers.push({ id: 'required-differential', before, after, disposition: 'REVIEW: failing differential observation changed, not automatically accepted.' });
    }
  }
  if (baseline.browserRequested === true || current.browserRequested === true) {
    if (current.browserRequested !== true || current.browserWorkerExit !== 0 || current.browser?.passed !== true) fail('browser', 'current', 'required-browser-check-not-passed');
  }


  function indexed(value, key, label) {
    const result = new Map();
    if (!Array.isArray(value[key]) || value[key].length === 0) { incomplete(key, label, 'missing-or-empty-case-list'); return result; }
    for (const row of value[key]) {
      if (!object(row) || typeof row.id !== 'string' || !/^[a-z0-9][a-z0-9-]*$/.test(row.id)) { incomplete(key, label, 'invalid-case-id'); continue; }
      if (result.has(row.id)) incomplete(key, row.id, 'duplicate-' + label + '-case');
      else result.set(row.id, row);
    }
    return result;
  }
  const maps = {};
  for (const key of ['http', 'wasm', 'commands']) {
    const before = indexed(baseline, key, 'baseline'), after = indexed(current, key, 'current'); maps[key] = [before, after];
    const missing = [...before.keys()].filter(id => !after.has(id));
    const added = [...after.keys()].filter(id => !before.has(id));
    coverage[key] = { baseline: [...before.keys()], current: [...after.keys()], missing, added };
    for (const id of missing) incomplete(key, id, 'missing-baseline-case');
  }
  // New observations may be added, but every old HTTP ID must appear once and
  // every current HTTP assertion must pass, including newly added assertions.
  for (const [id, row] of maps.http[1]) {
    if (row.passed !== true || (Array.isArray(row.failures) && row.failures.length)) fail('http', id, 'http-assertion-failed', { status: row.status ?? null, failures: row.failures ?? null });
    const before = maps.http[0].get(id);
    if (before && (before.path !== row.path || before.method !== row.method)) fail('http', id, 'request-identity-changed');
    if (before && row.status !== before.status) fail('http', id, 'http-status-changed', { before: before.status, after: row.status });
  }
  for (const [label, value] of [['baseline', baseline], ['current', current]]) {
    const commandMap = maps.commands[label === 'baseline' ? 0 : 1];
    for (const [id, row] of commandMap) {
      const intentionalServerStop = id === 'next-server' && ((row.signal === 'SIGTERM' && row.code === null)
        || (row.code === 143 && row.signal === null && row.signals?.includes('SIGTERM') && row.ownedGroupGone === true && row.groupObservationError === null));
      const previous = maps.commands[0].get(id);
      if (Object.hasOwn(row, 'signals') || Object.hasOwn(previous ?? {}, 'signals')) {
        if (!Array.isArray(row.signals) || (id === 'next-server' ? row.signals.length > 1 || row.signals.some(s => s !== 'SIGTERM') : row.signals.length !== 0)) incomplete('commands', id, 'unexpected-' + label + '-process-signalling');
      }
      if (Object.hasOwn(row, 'ownedGroupGone') || Object.hasOwn(previous ?? {}, 'ownedGroupGone')) {
        if (row.ownedGroupGone !== true || row.groupObservationError !== null) incomplete('commands', id, 'unproved-' + label + '-owned-group-cleanup');
      }

      if (row.timedOut !== false || row.spawnError !== null || (!intentionalServerStop && (row.code !== 0 || row.signal !== null))) {
        incomplete('commands', id, 'unclean-' + label + '-command', { code: row.code ?? null, signal: row.signal ?? null, timedOut: row.timedOut ?? null, spawnError: row.spawnError ?? null });
      }
    }
  }

  function validReport(row, label) {
    const report = row.report;
    if (row.missingReport !== false || !object(report)) { incomplete('wasm', row.id, 'missing-' + label + '-report'); return false; }
    if (row.workerExit !== 0) incomplete('wasm', row.id, 'unclean-' + label + '-worker', { workerExit: row.workerExit ?? null });
    const previous = maps.wasm[0].get(row.id);
    for (const [key, expected] of Object.entries({ workerSignal: null, workerTimedOut: false, workerOwnedGroupGone: true, workerSpawnError: null })) {
      if ((Object.hasOwn(row, key) || Object.hasOwn(previous ?? {}, key)) && row[key] !== expected) incomplete('wasm', row.id, 'unclean-or-missing-' + label + '-' + key);
    }

    if (report.schemaVersion !== 1 || report.case !== row.id || !STATUSES.has(report.status) || typeof report.stage !== 'string' || !Array.isArray(report.failures) || !report.failures.every(object) || typeof report.finishedAtUtc !== 'string') {
      incomplete('wasm', row.id, 'invalid-or-partial-' + label + '-report'); return false;
    }
    if (report.status === 'passed' && (report.stage !== 'complete' || report.jco?.passed !== true || report.jco?.retainedCalls !== 3 || report.wasmtime?.passed !== true || report.postNativeRecheck !== true || report.failures.length !== 0)) {
      incomplete('wasm', row.id, 'inconsistent-' + label + '-success'); return false;
    }
    const terminal = maps.commands[label === 'baseline' ? 0 : 1].get('wasm-' + row.id);
    if (!terminal || terminal.code !== row.workerExit) incomplete('wasm', row.id, 'missing-or-inconsistent-' + label + '-worker-command');
    return true;
  }
  const validity = { baseline: new Map(), current: new Map() };
  for (const [label, which] of [['baseline', 0], ['current', 1]]) for (const [id, row] of maps.wasm[which]) validity[label].set(id, validReport(row, label));
  for (const [id, before] of maps.wasm[0]) {
    const after = maps.wasm[1].get(id);
    if (!after || !validity.baseline.get(id) || !validity.current.get(id)) continue;
    const oldPass = before.report.status === 'passed', newPass = after.report.status === 'passed';
    if (oldPass && !newPass) fail('wasm', id, 'successful-case-regressed', { before: blocker(before, baseline), after: blocker(after, current) });
    else if (!oldPass && newPass) improvements.push({ scope: 'wasm', id, kind: 'previous-blocker-now-passed', before: blocker(before, baseline) });
    else if (!oldPass) {
      const oldBlocker = blocker(before, baseline), newBlocker = blocker(after, current);
      if (same(oldBlocker, newBlocker)) outstandingKnownFailures.push({ id, ...newBlocker, requiredDifferentialBlocked: id === 'compat' && current.requiredDifferentialPassed === false, rawBefore: { reason: before.report.reason ?? null, failures: before.report.failures }, rawAfter: { reason: after.report.reason ?? null, failures: after.report.failures } });
      if (!same(oldBlocker, newBlocker)) changedBlockers.push({ id, before: oldBlocker, after: newBlocker,
        rawBefore: { reason: before.report.reason ?? null, failures: before.report.failures }, rawAfter: { reason: after.report.reason ?? null, failures: after.report.failures },
        disposition: 'REVIEW: may expose the next blocker after a fix; no automatic acceptance.' });
    }
  }
  for (const [id, row] of maps.wasm[1]) if (!maps.wasm[0].has(id) && validity.current.get(id)) {
    if (row.report.status === 'passed') improvements.push({ scope: 'wasm', id, kind: 'new-case-passed' });
    else changedBlockers.push({ id, after: blocker(row, current), disposition: 'REVIEW: newly added case exposes an unbaselined blocker.' });
  }
  function successfulValue(label, id) {
    const row = maps.wasm[label === 'baseline' ? 0 : 1].get(id);
    if (!row || !validity[label].get(id) || row.report.status !== 'passed') return null;
    const observed = evidence[label]?.[id];
    if (!object(observed) || !Array.isArray(observed.jcoStrings) || observed.jcoStrings.length !== 3 || observed.jcoStrings.some(s => typeof s !== 'string') || typeof observed.wasmtimeString !== 'string') {
      incomplete('returns', id, 'missing-' + label + '-successful-return-evidence'); return null;
    }
    if (!observed.jcoStrings.every(s => s === observed.jcoStrings[0]) || observed.wasmtimeString !== observed.jcoStrings[0]) {
      fail('returns', id, 'whole-return-mismatch-' + label); return null;
    }
    try { return { value: JSON.parse(observed.jcoStrings[0]) }; }
    catch { incomplete('returns', id, 'non-json-successful-return-' + label); return null; }
  }
  const values = { baseline: new Map(), current: new Map() };
  for (const [label, which] of [['baseline', 0], ['current', 1]]) for (const id of maps.wasm[which].keys()) {
    const observed = successfulValue(label, id); if (observed) values[label].set(id, observed.value);
  }
  for (const [id, value] of values.current) {
    if (values.baseline.has(id)) {
      const equal = same(value, values.baseline.get(id)); coverage.returnComparisons.push({ id, kind: 'baseline-to-current-json', equal });
      if (!equal) fail('returns', id, 'successful-json-result-changed', { before: values.baseline.get(id), after: value });
    }
    if (id === 'compat' && Object.hasOwn(current, 'sameSourceNodeValue')) {
      const equal = same(value, current.sameSourceNodeValue); coverage.returnComparisons.push({ id, kind: 'current-same-source-node-json', equal });
      if (!equal) fail('returns', id, 'same-source-node-json-mismatch', { expected: current.sameSourceNodeValue, actual: value });
    }
  }
  for (const label of ['baseline', 'current']) if (values[label].has('compat') && Object.hasOwn(label === 'baseline' ? baseline : current, 'sameSourceNodeValue')) {
    const suite = label === 'baseline' ? baseline : current;
    if (!same(values[label].get('compat'), suite.sameSourceNodeValue)) fail('returns', 'compat', 'same-source-node-json-mismatch-' + label);
    const source = suite.fixture?.find(r => r.path === 'lib/compat.mjs');
    const original = maps.wasm[label === 'baseline' ? 0 : 1].get('compat').report.originalSource;
    if (!source || !original || source.sha256 !== original.sha256 || source.bytes !== original.bytes) incomplete('returns', 'compat', 'same-source-' + label + '-descriptor-mismatch');
  }
  return { oracle, coverage, regressions, improvements, changedBlockers, outstandingKnownFailures };
}

export const auditExitCode = audit => audit.regressions.length || !audit.coverage.complete ? 1 : audit.changedBlockers.length ? 2 : 0;

async function readBounded(path, maximum = 64 * 1024 * 1024) {
  const info = await stat(path); if (!info.isFile() || info.size > maximum) throw new Error('Not a bounded regular input: ' + path);
  return readFile(path, 'utf8');
}
async function retainedEvidence(path, result) {
  const evidence = {};
  for (const row of result.wasm ?? []) {
    if (row?.report?.status !== 'passed' || typeof row.id !== 'string' || !/^[a-z0-9][a-z0-9-]*$/.test(row.id)) continue;
    try {
      const directory = join(dirname(path), 'wasm', row.id);
      evidence[row.id] = { jcoStrings: await Promise.all([0, 1, 2].map(i => readBounded(join(directory, `jco-${i}.string.txt`), 16 * 1024 * 1024))),
        wasmtimeString: await readBounded(join(directory, 'wasmtime.string.txt'), 16 * 1024 * 1024) };
    } catch (error) { evidence[row.id] = { unavailable: error.code ?? error.message }; }
  }
  return evidence;
}

export function selfTest() {
  const ensure = (condition, name) => { if (!condition) throw new Error('Synthetic check failed: ' + name); };
  const clone = x => JSON.parse(JSON.stringify(x));
  const command = id => ({ id, code: 0, signal: null, timedOut: false, spawnError: null });
  const positive = { id: 'compat', workerExit: 0, missingReport: false, report: { schemaVersion: 1, case: 'compat', stage: 'complete', status: 'passed', failures: [], finishedAtUtc: 'synthetic', jco: { passed: true, retainedCalls: 3 }, wasmtime: { passed: true }, postNativeRecheck: true, originalSource: { sha256: 'fixture', bytes: 3 } } };
  const negative = { id: 'blocked', workerExit: 0, missingReport: false, report: { schemaVersion: 1, case: 'blocked', stage: 'bundling', status: 'refused', reason: 'BUNDLE_PROFILE_REFUSED', failures: [{ stage: 'bundling', message: 'unsupported API' }], finishedAtUtc: 'synthetic' } };
  const baseline = { schemaVersion: 1, suite: SUITE, ...VERSIONS, installedVersions: INSTALLED, oraclePassed: true, observationsComplete: true, errors: [], fullNextServerInWasm: false,
    fixture: [{ path: 'lib/compat.mjs', sha256: 'fixture', bytes: 3 }], sameSourceNodeValue: { marker: 'OK' }, requiredDifferentialPassed: true, sameSourceDifferential: { performed: true, passed: true, node: { marker: 'OK' }, guest: { marker: 'OK' } },
    http: [{ id: 'health', path: '/health', method: 'GET', status: 200, passed: true, failures: [] }], wasm: [positive, negative],
    commands: [command('npm-install'), command('next-build'), { ...command('next-server'), code: null, signal: 'SIGTERM' }, command('wasm-compat'), command('wasm-blocked')] };
  const value = { jcoStrings: ['{"marker":"OK"}', '{"marker":"OK"}', '{"marker":"OK"}'], wasmtimeString: '{"marker":"OK"}' };
  const evidence = { baseline: { compat: value }, current: { compat: value } };
  let count = 0;
  function test(name, mutate, expected, predicate = () => true) { const current = clone(baseline), ev = clone(evidence); mutate(current, ev); const audit = auditResults(baseline, current, ev); ensure(auditExitCode(audit) === expected && predicate(audit), name); count++; }
  test('valid unchanged observations', () => {}, 0);
  test('deleted Wasm case refuses even if completion flag true', c => c.wasm.pop(), 1);
  test('deleted HTTP case refuses', c => c.http.pop(), 1);
  test('missing report refuses', c => { c.wasm[1].report = null; c.wasm[1].missingReport = true; }, 1);
  test('duplicate case refuses', c => c.wasm.push(clone(c.wasm[0])), 1);
  test('positive regression', c => { c.wasm[0].report = clone(negative.report); c.wasm[0].report.case = 'compat'; }, 1);
  test('changed blocker requires review', c => { c.wasm[1].report.failures[0].message = 'next unsupported API'; }, 2, a => a.changedBlockers.length === 1);
  test('changed stage requires review', c => { c.wasm[1].report.stage = 'componentization'; }, 2);
  test('improvement allowed explicitly', (c, ev) => { c.wasm[1].report = clone(positive.report); c.wasm[1].report.case = 'blocked'; ev.current.blocked = clone(value); }, 0, a => a.improvements.length === 1);
  test('positive return regression', (c, ev) => { ev.current.compat = { jcoStrings: Array(3).fill('{"marker":"CHANGED"}'), wasmtimeString: '{"marker":"CHANGED"}' }; }, 1);
  test('missing successful retained returns', (c, ev) => { delete ev.current.compat; }, 1);
  test('same source node mismatch', c => { c.sameSourceNodeValue = { marker: 'WRONG' }; }, 1);
  test('version mismatch', c => { c.next = 'other'; }, 1);
  test('oracle incomplete', c => { c.oraclePassed = false; }, 1);
  test('timeout never accepted as intentional stop', c => { c.commands[2].timedOut = true; }, 1);
  test('unexpected signal refuses', c => { c.commands[0].signal = 'SIGTERM'; c.commands[0].code = null; }, 1);
  test('missing worker command refuses', c => { c.commands.pop(); }, 1);

  test('explicit differential failure refuses', c => { c.requiredDifferentialPassed = false; }, 1);
  test('browser requested failure refuses', c => { c.browserRequested = true; c.browserWorkerExit = 0; c.browser = { passed: false }; }, 1);
  test('owned group cleanup refuses', c => { c.commands[0].ownedGroupGone = false; c.commands[0].groupObservationError = null; }, 1);
  test('worker signal refuses', c => { c.wasm[1].workerSignal = 'SIGTERM'; }, 1);
  test('pending report refuses', c => { c.wasm[1].report.status = 'pending'; }, 1);
  test('forced cleanup after raw zero refuses', c => { c.commands[0].signals = ['SIGTERM']; }, 1);
  test('Next intentional SIGTERM converted to143 accepts only clean server', c => { Object.assign(c.commands[2], { code: 143, signal: null, signals: ['SIGTERM'], ownedGroupGone: true, groupObservationError: null }); }, 0);
  test('Next143 without observed stop refuses', c => { Object.assign(c.commands[2], { code: 143, signal: null, signals: [], ownedGroupGone: true, groupObservationError: null }); }, 1);
  test('other command143 refuses', c => { Object.assign(c.commands[0], { code: 143, signal: null, signals: ['SIGTERM'], ownedGroupGone: true, groupObservationError: null }); }, 1);
  const rootedBaseline = clone(baseline), rootedCurrent = clone(baseline);
  rootedBaseline.output = '/private/run-before'; rootedCurrent.output = '/private/run-after';
  rootedBaseline.wasm[1].report.output = '/private/run-before/wasm/blocked'; rootedCurrent.wasm[1].report.output = '/private/run-after/wasm/blocked';
  rootedBaseline.wasm[1].report.failures[0].message = 'Cannot load /private/run-before/application/module.js at /private/run-before/wasm/blocked/bundle.mjs';
  rootedCurrent.wasm[1].report.failures[0].message = 'Cannot load /private/run-after/application/module.js at /private/run-after/wasm/blocked/bundle.mjs';
  ensure(auditExitCode(auditResults(rootedBaseline, rootedCurrent, evidence)) === 0, 'literal declared roots normalize without hiding module name'); count++;
  const strictBaseline = clone(baseline), downgradedCurrent = clone(baseline);
  strictBaseline.requiredDifferentialPassed = true; delete downgradedCurrent.requiredDifferentialPassed;
  ensure(auditExitCode(auditResults(strictBaseline, downgradedCurrent, evidence)) === 1, 'new baseline differential requirement cannot be omitted'); count++;
  const failingBaseline = clone(baseline);
  failingBaseline.wasm[0].report = clone(negative.report); failingBaseline.wasm[0].report.case = 'compat';
  failingBaseline.requiredDifferentialPassed = false;
  failingBaseline.sameSourceDifferential = { performed: false, passed: false, reason: 'compat did not finish', actualStage: 'bundling' };
  const failingEvidence = { baseline: {}, current: {} };
  let known = auditResults(failingBaseline, clone(failingBaseline), failingEvidence);
  ensure(auditExitCode(known) === 0 && known.outstandingKnownFailures.length === 2 && known.oracle.frameworkCompatible.current === false, 'unchanged failed baseline explicit and not compatible'); count++;
  const changedFailure = clone(failingBaseline); changedFailure.wasm[0].report.failures[0].message = 'next blocker';
  ensure(auditExitCode(auditResults(failingBaseline, changedFailure, failingEvidence)) === 2, 'changed blocker from failing baseline is review'); count++;
  const newlyPassing = clone(baseline);
  known = auditResults(failingBaseline, newlyPassing, { baseline: {}, current: { compat: value } });
  ensure(auditExitCode(known) === 0 && known.improvements.some(i => i.id === 'compat'), 'failing compat can improve with genuine differential and returns'); count++;
  newlyPassing.requiredDifferentialPassed = false;
  ensure(auditExitCode(auditResults(failingBaseline, newlyPassing, { baseline: {}, current: { compat: value } })) === 1, 'newly successful compat must pass differential'); count++;
  const blockA = '[plugin starling-native-node-profile] react/index.js\nError: unsupported React require\n    at file:///actual/profile.mjs:1:2';
  const blockB = '[plugin starling-native-node-profile] react-dom/server.node.js\nError: unsupported ReactDOM require\n    at file:///actual/profile.mjs:3:4';
  const multi = blocks => `Build failed with ${blocks.length} errors:\n\n${blocks.join('\n')}`;
  const diagnosticBaseline = clone(baseline);
  diagnosticBaseline.wasm[1].report.failures[0].message = multi([blockA, blockB]);
  const diagnosticCheck = (name, message, expected) => {
    const current = clone(diagnosticBaseline); current.wasm[1].report.failures[0].message = message;
    const audit = auditResults(diagnosticBaseline, current, evidence);
    ensure(auditExitCode(audit) === expected, name); count++;
    return audit;
  };
  const swapped = diagnosticCheck('recognized aggregate block order is irrelevant', multi([blockB, blockA]), 0);
  ensure(swapped.outstandingKnownFailures[0].rawBefore.failures[0].message === multi([blockA, blockB])
    && swapped.outstandingKnownFailures[0].rawAfter.failures[0].message === multi([blockB, blockA]), 'raw aggregate order retained'); count++;
  diagnosticCheck('changed diagnostic block reviews', multi([blockA, blockB.replace('ReactDOM', 'OTHER')]), 2);
  diagnosticCheck('added diagnostic block reviews', multi([blockA, blockB, blockA]), 2);
  diagnosticCheck('removed diagnostic block reviews', multi([blockA]), 2);
  diagnosticCheck('duplicated block replaces another reviews; not a set', multi([blockA, blockA]), 2);
  diagnosticCheck('changed prefix reviews', multi([blockB, blockA]).replace('Build failed', 'Build FAILED'), 2);
  diagnosticCheck('mismatched declared count remains exact', multi([blockB, blockA]).replace('2 errors', '3 errors'), 2);
  diagnosticCheck('unrecognized extra block bytes remain exact', multi([blockB + '\nUNKNOWN DETAIL', blockA]), 2);
  const unknownBaseline = clone(diagnosticBaseline), unknownCurrent = clone(diagnosticBaseline);
  unknownBaseline.wasm[1].report.failures[0].message = multi([blockA, blockB]).replace('Build failed', 'Other aggregate');
  unknownCurrent.wasm[1].report.failures[0].message = multi([blockB, blockA]).replace('Build failed', 'Other aggregate');
  ensure(auditExitCode(auditResults(unknownBaseline, unknownCurrent, evidence)) === 2, 'unknown aggregate swapped order still exact-compares'); count++;
  ensure(same(canonicalRolldownMessage(multi([blockA, blockA])), { format: 'recognized-rolldown-multi-error', prefix: 'Build failed with 2 errors:\n\n', actualErrorCount: 2, separator: '\n', blocks: [blockA, blockA] }), 'prefix count separator every duplicate block byte retained'); count++;
  return { syntheticChecks: count, passed: true, suiteExecuted: false };
}

async function main(argv) {
  if (argv.length === 1 && argv[0] === '--self-test') { process.stdout.write(JSON.stringify(selfTest(), null, 2) + '\n'); return; }
  if (argv.length !== 2) throw new Error('Usage: check-results.mjs BASELINE_RESULTS CURRENT_RESULTS (or --self-test)');
  const [beforePath, afterPath] = argv.map(p => resolve(p));
  const [baseline, current] = await Promise.all([beforePath, afterPath].map(async p => JSON.parse(await readBounded(p))));
  const [beforeEvidence, afterEvidence] = await Promise.all([retainedEvidence(beforePath, baseline), retainedEvidence(afterPath, current)]);
  const audit = auditResults(baseline, current, { baseline: beforeEvidence, current: afterEvidence });
  process.stdout.write(JSON.stringify(audit, null, 2) + '\n'); process.exitCode = auditExitCode(audit);
}
if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) main(process.argv.slice(2)).catch(error => {
  process.stdout.write(JSON.stringify({ oracle: { suite: SUITE }, coverage: { complete: false }, regressions: [{ scope: 'input', kind: 'audit-input-error', message: error.message }], improvements: [], changedBlockers: [], outstandingKnownFailures: [] }, null, 2) + '\n'); process.exitCode = 1;
});
