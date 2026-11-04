// Ordinary pinned Node public API oracle. No Starling guest is executed.
import assert from 'node:assert/strict';
import {addAbortListener} from 'node:events';
import {createHash} from 'node:crypto';
import {readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS);
const cases = [];

for (const mode of ['ordinary-once', 'protected-once', 'protected-after-stop']) {
  const controller = new AbortController(), signal = controller.signal;
  const log = [], resources = [];
  let depth = 0, readded = false;
  function register() {
    if (mode === 'ordinary-once') signal.addEventListener('abort', later, {once: true});
    else resources.push(addAbortListener(signal, later));
  }
  function earlier(event) {
    log.push('earlier:' + event.label);
    if (event.label !== 'outer') return;
    depth++;
    const nested = new Event('abort'); nested.label = 'nested';
    signal.dispatchEvent(nested);
    depth--;
    log.push('earlier:after-nested');
    if (mode === 'protected-after-stop') event.stopImmediatePropagation();
  }
  function later(event) {
    assert.equal(this, signal);
    log.push('later:' + event.label);
    if (!readded) {
      assert.equal(depth, 1);
      readded = true;
      register();
      log.push('later:readded');
    }
  }
  signal.addEventListener('abort', earlier);
  register();
  for (const label of ['outer', 'second', 'third']) {
    const event = new Event('abort'); event.label = label;
    signal.dispatchEvent(event);
  }
  const expected = ['earlier:outer', 'earlier:nested', 'later:nested', 'later:readded',
    'earlier:after-nested', 'earlier:second', 'later:second', 'earlier:third'];
  assert.deepEqual(log, expected);
  assert.equal(signal.aborted, false, 'Only synthetic ordinary dispatch was used');
  for (const resource of resources) resource[Symbol.dispose]();
  cases.push({mode, log, laterInvocations: 2, laterRanInOuter: false,
    syntheticDispatchOnly: true, actualControllerAbortCalled: false});
}

// Removing/readding an active ordinary record already creates a distinct node.
// Keep that separate control so the proposal does not broaden the changed path.
{
  const target = new EventTarget(), log = [];
  let first = true;
  const later = () => log.push('later');
  target.addEventListener('x', () => {
    log.push('earlier');
    if (first) {
      first = false;
      target.removeEventListener('x', later);
      target.addEventListener('x', later, {once: true});
    }
  });
  target.addEventListener('x', later, {once: true});
  target.dispatchEvent(new Event('x'));
  assert.deepEqual(log, ['earlier']);
  target.dispatchEvent(new Event('x'));
  assert.deepEqual(log, ['earlier', 'earlier', 'later']);
  cases.push({mode: 'ordinary-remove-and-readd-control', log});
}

const source = fileURLToPath(import.meta.url);
const report = {
  state: 'NODE_ORACLE_ONLY_NO_GUEST_EXECUTED', nodeRelease: process.version,
  nodeExecutable: process.execPath,
  nodeExecutableSha256: createHash('sha256').update(await readFile(process.execPath)).digest('hex'),
  sourceSha256: createHash('sha256').update(await readFile(source)).digest('hex'),
  cases, passed: cases.length,
  conclusion: 'A once record removed by a nested dispatch remains removed in the outer traversal; readding the callback creates a new record for a later dispatch.'
};
await writeFile(new URL('./node-results.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({passed: cases.length, state: report.state}));
