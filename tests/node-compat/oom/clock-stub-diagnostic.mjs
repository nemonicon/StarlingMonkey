// Isolate the disabled-clock P1 stub independently of Buffer/SpiderMonkey GC.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const expected = process.env.NODE_COMPAT_CLOCK_STUB_EXPECT ?? 'broken';
assert(['broken', 'fixed'].includes(expected), 'NODE_COMPAT_CLOCK_STUB_EXPECT must be broken or fixed');
const output = resolve(process.env.NODE_COMPAT_OOM_CLOCK_OUTPUT ?? '/tmp/starling-node-compat/oom-clock-diagnostic');
const wasmTools = resolve(process.env.NODE_COMPAT_WASM_TOOLS ?? '/tmp/starling-node-compat/improved-build/cache/wasm-tools/1448/wasm-tools');
const toolchain = await loadToolchain();
const { splicer, provenance } = await loadComponentizer(toolchain, { legacyDiagnostic: expected === 'broken' });
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const version = spawnSync(wasmTools, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^wasm-tools 1\.235\.0\b/);
await mkdir(output, { recursive: true });
const source = `(module
  (import "wasi_snapshot_preview1" "clock_time_get"
    (func $clock (param i32 i64 i32) (result i32)))
  (memory (export "memory") 1)
  (func (export "errno") (param $pointer i32) (result i32)
    i32.const 1 i64.const 0 local.get $pointer call $clock))\n`;
const watPath = join(output, 'clock.wat'), inputPath = join(output, 'clock.wasm');
await writeFile(watPath, source);
const parse = spawnSync(wasmTools, ['parse', watPath, '-o', inputPath], { encoding: 'utf8' });
assert.equal(parse.status, 0, parse.stderr);
// Leave unrelated features enabled: their absent imports add no capabilities,
// and the random stubbing pass otherwise assumes an entire engine's exports.
const stubbed = splicer.stubWasi(await readFile(inputPath), ['random', 'stdio', 'http', 'fetch-event'],
  'package test:clock; world empty {}', undefined, 'empty');
await writeFile(join(output, 'clock.stubbed.wasm'), stubbed);
const module = await WebAssembly.compile(stubbed);
assert.deepEqual(WebAssembly.Module.imports(module), []);
const { exports } = await WebAssembly.instantiate(module, {});
const observations = [0, 8, 64, 1024].map(pointer => {
  const errno = exports.errno(pointer);
  const timestamp = new DataView(exports.memory.buffer).getBigUint64(pointer, true);
  assert(timestamp > 0n, 'Stub must write its build timestamp');
  return { pointer, errno, expectedSuccessErrno: 0, timestamp: String(timestamp),
    correctSuccessErrno: errno === 0, errnoEqualsPointer: errno === pointer };
});
if (expected === 'broken') {
  assert(observations.some(item => !item.correctSuccessErrno), 'Expected the pinned clock stub errno defect');
  assert(observations.every(item => item.errnoEqualsPointer));
} else {
  assert(observations.every(item => item.correctSuccessErrno), 'The corrected stub must return success at every destination');
}
const report = { schema: 1, verifiedAtUtc: new Date().toISOString(), node: process.version,
  componentizer: provenance, tool: { path: wasmTools, version: version.stdout.trim(), sha256: hash(await readFile(wasmTools)) },
  source, sourceSha256: hash(source), runnerSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  stubbedSha256: hash(stubbed), emittedImports: [], observations,
  expected, verifiedFinding: expected === 'broken'
    ? 'The pinned disabled-clock preview1 stub writes a nonzero timestamp but returns the destination pointer as errno instead of success 0.'
    : 'The selected corrected disabled-clock preview1 stub writes a nonzero timestamp and returns success 0 at every destination.',
  limits: 'This independent stub repro does not capture either TimeStamp operand at the observed DEBUG GC assertion; it establishes the syscall-result defect, not its complete runtime consequence.' };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
await writeFile(join(here, expected === 'broken' ? 'clock-stub-results.json' : 'clock-stub-fixed-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, observations, emittedImports: [] }, null, 2));
