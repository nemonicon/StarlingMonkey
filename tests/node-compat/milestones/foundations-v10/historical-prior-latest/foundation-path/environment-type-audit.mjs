// Compare actual canonical component function types with checked-in WASI0.2.10.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function signatures(graph) {
  const matches = graph.interfaces.filter(value => value.name === 'environment' &&
    graph.packages[value.package].name === 'wasi:cli@0.2.10');
  assert.equal(matches.length, 1);
  const environment = matches[0];
  assert.deepEqual(Object.keys(environment.types), []);
  assert.deepEqual(Object.keys(environment.functions).sort(), ['get-arguments', 'get-environment', 'initial-cwd']);
  function type(value) {
    if (typeof value === 'number') return type(graph.types[value].kind);
    if (typeof value === 'string' || value === null) return value;
    if (Array.isArray(value)) return value.map(type);
    const entries = Object.entries(value);
    assert.equal(entries.length, 1);
    assert(['type', 'list', 'tuple', 'option'].includes(entries[0][0]), 'Unexpected environment type constructor');
    if (entries[0][0] === 'tuple') {
      assert.deepEqual(Object.keys(entries[0][1]), ['types']);
      return { tuple: entries[0][1].types.map(type) };
    }
    return Object.fromEntries(entries.map(([key, value]) => [key, type(value)]));
  }
  return Object.fromEntries(Object.entries(environment.functions).map(([name, fn]) =>
    [name, { kind: fn.kind, params: fn.params.map(param => ({ name: param.name, type: type(param.type) })), result: type(fn.result) }]));
}
export async function auditEnvironmentTypes(wasmTools, componentPath, referenceWorld, output, name) {
  const version = spawnSync(wasmTools, ['--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr); assert.match(version.stdout, /^wasm-tools 1\.235\.0\b/);
  function graph(input) {
    const result = spawnSync(wasmTools, ['component', 'wit', '--json', input], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
    assert.equal(result.status, 0, result.error?.message || result.stderr);
    return { text: result.stdout, graph: JSON.parse(result.stdout) };
  }
  const actual = graph(componentPath), reference = graph(referenceWorld);
  const checkedIn = new URL('../../../host-apis/wasi-0.2.10/wit/deps/wasi-cli-0.2.10/package.wit', import.meta.url);
  const checkedInBytes = await readFile(checkedIn);
  assert.deepEqual(await readFile(join(referenceWorld, 'deps/wasi-cli-0.2.10/package.wit')), checkedInBytes);
  const canonicalFunctions = signatures(actual.graph);
  assert.deepEqual(canonicalFunctions, signatures(reference.graph), 'Actual canonical types must match checked-in WASI0.2.10');
  const actualPath = join(output, name + '.component-types.json');
  const referencePath = join(output, 'reference-types.json');
  await writeFile(actualPath, actual.text); await writeFile(referencePath, reference.text);
  return { interface: 'wasi:cli/environment@0.2.10', canonicalFunctions,
    checkedInWit: { path: checkedIn.pathname, sha256: hash(checkedInBytes) },
    actual: { path: actualPath, sha256: hash(actual.text) }, reference: { path: referencePath, sha256: hash(reference.text) },
    tool: { path: wasmTools, version: version.stdout.trim(), sha256: hash(await readFile(wasmTools)) },
    scope: 'Actual post-adapter component function/anonymous list, tuple and option types; no version text rewriting' };
}
