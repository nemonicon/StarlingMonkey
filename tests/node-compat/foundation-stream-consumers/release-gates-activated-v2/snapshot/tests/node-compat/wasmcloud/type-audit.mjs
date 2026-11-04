import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

// A world import name alone cannot distinguish clock functions from the
// transitive duration typedef used by HTTP request-options. Inspect the actual
// component type graph, not the upstream package's complete clock interface.
export async function auditClockDependency(wasmTools, componentPath, coreImports, output) {
  const version = spawnSync(wasmTools, ['--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.error?.message || version.stderr);
  assert.match(version.stdout, /^wasm-tools 1\.235\.0\b/, 'Use the repository-pinned wasm-tools release');
  const extracted = spawnSync(wasmTools, ['component', 'wit', '--json', componentPath], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  assert.equal(extracted.status, 0, extracted.error?.message || extracted.stderr);
  const graph = JSON.parse(extracted.stdout);
  const interfaces = graph.interfaces.filter(value => value.name === 'monotonic-clock' && graph.packages[value.package].name === 'wasi:clocks@0.2.10');
  assert.equal(interfaces.length, 1, 'Exactly one pinned monotonic-clock dependency is admitted');
  const clock = interfaces[0];
  assert.deepEqual(Object.keys(clock.functions), [], 'No clock functions may be imported');
  assert.deepEqual(Object.keys(clock.types), ['duration'], 'Only the HTTP duration typedef is admitted');
  assert.deepEqual(graph.types[clock.types.duration].kind, { type: 'u64' });
  const coreClockImports = coreImports.filter(value => /^wasi:clocks\//.test(value.module));
  assert.deepEqual(coreClockImports, [], 'No clock core imports may survive stubbing');
  const jsonPath = join(output, 'component-types.json');
  await writeFile(jsonPath, extracted.stdout);
  const digest = bytes => createHash('sha256').update(bytes).digest('hex');
  return {
    interface: 'wasi:clocks/monotonic-clock@0.2.10', typeOnly: true,
    types: ['duration'], durationRepresentation: 'u64', callableImports: [], coreClockImports,
    reason: 'Nominal type dependency of wasi:http/types request-options; no clock operation is selected or exercised',
    componentTypeGraph: { path: jsonPath, sha256: digest(extracted.stdout) },
    tool: { path: wasmTools, version: version.stdout.trim(), sha256: digest(await readFile(wasmTools)) },
  };
}
