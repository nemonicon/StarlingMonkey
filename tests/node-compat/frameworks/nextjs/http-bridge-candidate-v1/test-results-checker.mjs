// Inject incomplete/relaxed evidence plans. No Next server, browser or guest.
import assert from 'node:assert/strict';
import {cp, mkdtemp, readFile, rm, writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const here = dirname(fileURLToPath(import.meta.url));
assert.equal(process.version, 'v22.14.0');
const root = await mkdtemp(join(tmpdir(), 'starling-next-host-checker-'));
const results = [];
try {
  await cp(join(here, 'results'), join(root, 'results'), {recursive: true});
  const file = join(root, 'results/summary.json');
  const original = JSON.parse(await readFile(file, 'utf8'));
  const run = () => spawnSync(process.execPath, [join(here, 'check-results.mjs'), join(root, 'results')], {encoding: 'utf8', timeout: 5000});
  const control = run();
  assert.equal(control.status, 0, control.stderr);
  results.push({id: 'copied-positive-control', passed: true, rawExitCode: control.status});
  for (const [id, change] of [
    ['empty-run-plan', value => { value.runs = []; }],
    ['missing-required-run', value => { value.runs.splice(1, 1); }],
    ['disabled-browser-gate', value => { value.runs[2].browserPassed = 0; }],
    ['relabeled-failed-attempt', value => { value.runs[0].rawExitCode = 0; }],
  ]) {
    const changed = structuredClone(original); change(changed);
    await writeFile(file, JSON.stringify(changed, null, 2) + '\n');
    const observed = run();
    assert.equal(observed.signal, null); assert.equal(observed.error, undefined);
    assert.notEqual(observed.status, 0, id);
    results.push({id, passed: true, rawExitCode: observed.status});
  }
} finally { await rm(root, {recursive: true, force: true}); }
console.log(JSON.stringify({suite: 'FULL_NEXT_HOST_BRIDGE_CHECKER_NEGATIVES_V1', passed: true,
  checks: results.length, results, applicationExecuted: false, guestExecuted: false}));
