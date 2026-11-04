import { access, readdir, readFile, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { join } from 'node:path';
import assert from 'node:assert/strict';
import { context, here, repository, output, hash } from './common.mjs';

const ctx = await context();
const names = (await readdir(join(repository, 'tests/e2e'), { withFileTypes: true })).filter(entry => entry.isDirectory()).map(entry => entry.name).sort();
const selected = process.argv.slice(2).filter(arg => arg !== '--collect-only');
const results = [];
for (const name of selected.length ? selected : names) {
  if (!process.argv.includes('--collect-only')) {
    const processResult = await new Promise(resolve => {
      const cp = spawn(process.execPath, [join(here, 'starling-worker.mjs'), name], { stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout = '', stderr = '';
      cp.stdout.on('data', bytes => { stdout += bytes; }); cp.stderr.on('data', bytes => { stderr += bytes; });
      const timer = setTimeout(() => cp.kill('SIGKILL'), 180000);
      cp.on('exit', (code, signal) => { clearTimeout(timer); resolve({ code, signal, stdout, stderr }); });
    });
    await writeFile(join(output, 'starling-' + name + '.worker.json'), JSON.stringify(processResult, null, 2) + '\n');
    console.log(name, processResult.code, processResult.stdout.trim().split('\n').at(-1));
  }
  try {
    const result = JSON.parse(await readFile(join(output, 'starling-' + name + '.result.json')));
    assert.equal(result.engineSha256, ctx.engineSha256, 'Do not collect stale results from a different engine');
    assert.equal(hash(await readFile(result.sourcePath)), result.sourceSha256);
    if (result.componentSha256) assert.equal(hash(await readFile(join(output, 'starling-e2e', name, name + '.component.wasm'))), result.componentSha256);
    const expectedPath = join(repository, 'tests/e2e', name, 'expect_wizer_stdout.txt');
    let hasExpected = false;
    try { await access(expectedPath); hasExpected = true; } catch {}
    if (hasExpected && result.status === 'pass') {
      const original = await readFile(expectedPath, 'utf8');
      const expected = original.replace(/^Componentizing .*\n/, '').replace(/^Log: /gm, '');
      const worker = JSON.parse(await readFile(join(output, 'starling-' + name + '.worker.json')));
      const actual = worker.stdout.split('\n').slice(0, -2).join('\n') + '\n';
      assert.equal(actual, expected, 'Preserve actual upstream Wizer console output assertion after shell/embedding formatting adaptation');
      result.initializationStdout = { pass: true, actual, originalExpectedSha256: hash(original), adaptation: 'Omit standalone shell banner and embedding-absent Log: prefix' };
    }
    results.push(result);
  }
  catch (error) { results.push({ name, status: 'fail', error: error.message }); }
}
const report = { schema: 1, engineSha256: ctx.engineSha256, engine: ctx.engine, sourceRoot: ctx.sourceRoot,
  componentizerProvenance: ctx.componentizerProvenance,
  originalCmakeGate: 'tests/tests.cmake test_e2e(): 19 registered fixtures',
  selected: selected.length ? selected : names,
  passed: results.filter(result => result.status === 'pass').length,
  failed: results.filter(result => result.status !== 'pass').length, results,
  excluded: ['WPT suite: separate harness and WPT_SUPPORT build option OFF',
    'integration_tests: separate server and ten HTTP routes; selected independently'],
};
await writeFile(join(output, 'starling-e2e-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: report.passed, failed: report.failed }));
process.exitCode = report.failed ? 1 : 0;
