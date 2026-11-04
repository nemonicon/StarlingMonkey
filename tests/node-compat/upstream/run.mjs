import assert from 'node:assert/strict';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import { context, here, output, upstream, hash } from './common.mjs';

const ctx = await context();
const names = (await readdir(join(upstream, 'test/builtins'))).filter(name => name.endsWith('.js')).map(name => name.slice(0, -3)).sort();
const collectOnly = process.argv.includes('--collect-only');
const requested = process.argv.slice(2).filter(arg => arg !== '--collect-only');
const selected = requested.length ? requested : names;
for (const name of selected) assert(names.includes(name), `No such upstream builtin fixture: ${name}`);
const results = [];
for (const name of selected) {
  const status = collectOnly ? {} : await new Promise(resolve => {
    const child = spawn(process.execPath, [join(here, 'fixture-worker.mjs'), name], { stdio: ['ignore', 'pipe', 'pipe'] });
    child.stdout.pipe(process.stdout); child.stderr.pipe(process.stderr);
    const timer = setTimeout(() => child.kill('SIGKILL'), 180000);
    child.on('exit', (code, signal) => { clearTimeout(timer); resolve({ code, signal }); });
  });
  try {
    const result = JSON.parse(await readFile(join(output, name + '.result.json')));
    assert.equal(result.engineSha256, ctx.engineSha256, 'Do not collect stale results from a different engine');
    assert.equal(hash(await readFile(result.fixturePath)), result.fixtureSha256);
    if (result.componentSha256) assert.equal(hash(await readFile(join(result.directory, name + '.component.wasm'))), result.componentSha256);
    results.push(result);
  }
  catch { results.push({ name, status: 'fail', process: status, error: 'Worker did not produce a result' }); }
}
const report = { schema: 1, node: process.version, engine: ctx.engine, engineSha256: ctx.engineSha256,
  componentizerProvenance: ctx.componentizerProvenance,
  engineMetadata: ctx.metadataPath, sourceRoot: ctx.sourceRoot, sourceFilesVerified: ctx.metadata.sourceManifest.length,
  upstreamSource: upstream, upstreamRevision: ctx.metadata.componentizeJsRevision,
  originalHarnessSha256: hash(await readFile(join(upstream, 'test/builtins.js'))),
  adapter: ctx.preview2Adapter, adapterSha256: ctx.adapterSha256,
  harnessAdaptations: ['Explicit custom engine, pinned old standard Preview1 adapter, external outputs',
    'Sequential fixture workers; no upstream concurrent execution/retry masking',
    'Await exported run and kill child on timeout; enforce actual failure for catch-only negative tests',
    'Globals: retain original failure and allow exactly the selected profile Buffer addition'],
  selected, unselected: names.filter(name => !selected.includes(name)),
  passed: results.filter(result => result.status === 'pass').length, failed: results.filter(result => result.status !== 'pass').length,
  results,
};
await writeFile(join(output, 'componentize-builtins-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: report.passed, failed: report.failed, output }));
process.exitCode = report.failed ? 1 : 0;
