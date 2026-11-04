import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const here = dirname(fileURLToPath(import.meta.url));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export const DENIED_PREVIEW1 = Object.freeze({ version: 'sm-path-benchmark-denied-p1-v1',
  exports: Object.freeze(['args_get', 'args_sizes_get', 'environ_get', 'environ_sizes_get']),
  signature: '(i32,i32)->i32', behavior: 'unreachable on every call', imports: [],
  watSha256: '47a6d1759eec68c00258de82baf70ab93b062f1d2170dfea11c3123167725d55',
  wasmSha256: '7b451ff0643d1896880df1b9299f59af05c46b4473aca243112600429887f688', bytes: 108,
  scope: 'Benchmark-only denied internal Preview1 paths; not an environment implementation or host service' });
export async function buildDeniedPreview1(wasmTools, wasmtime, output) {
  const version = spawnSync(wasmTools, ['--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr); assert.match(version.stdout, /^wasm-tools 1\.235\.0\b/);
  const source = join(here, 'denied-preview1.wat'), path = join(output, 'denied-preview1.wasm');
  const parsed = spawnSync(wasmTools, ['parse', source, '-o', path], { encoding: 'utf8' });
  assert.equal(parsed.status, 0, parsed.stderr);
  const bytes = await readFile(path), module = new WebAssembly.Module(bytes);
  assert.equal(hash(await readFile(source)), DENIED_PREVIEW1.watSha256);
  assert.equal(hash(bytes), DENIED_PREVIEW1.wasmSha256); assert.equal(bytes.length, DENIED_PREVIEW1.bytes);
  assert.deepEqual(WebAssembly.Module.imports(module), []);
  assert.deepEqual(WebAssembly.Module.exports(module), DENIED_PREVIEW1.exports.map(name => ({ name, kind: 'function' })));
  const instance = new WebAssembly.Instance(module);
  const traps = [];
  for (const name of DENIED_PREVIEW1.exports) {
    assert.throws(() => instance.exports[name](0, 0), WebAssembly.RuntimeError);
    const host = spawnSync(wasmtime, ['run', '--invoke', name, path, '0', '0'], { encoding: 'utf8', timeout: 30000 });
    assert.notEqual(host.status, 0); assert.match(host.stderr, /unreachable/);
    traps.push({ name, v8: 'WebAssembly.RuntimeError', wasmtime: { status: host.status, signal: host.signal, stderr: host.stderr } });
  }
  const printed = spawnSync(wasmTools, ['print', path], { encoding: 'utf8' });
  assert.equal(printed.status, 0, printed.stderr);
  assert.equal((printed.stdout.match(/\(func \(;\d+;\) \(type 0\) \(param i32 i32\) \(result i32\)\s+unreachable\s+\)/g) ?? []).length, 4);
  await writeFile(join(output, 'denied-preview1.disassembled.wat'), printed.stdout);
  return { path, bytes, audit: { ...DENIED_PREVIEW1, source, watSha256: hash(await readFile(source)),
    wasmSha256: hash(bytes), bytes: bytes.length, traps, disassembledWatSha256: hash(printed.stdout),
    tool: { path: wasmTools, version: version.stdout.trim(), sha256: hash(await readFile(wasmTools)) } } };
}
