// Isolate cached versus first deployed builtin imports. A trap is evidence,
// never treated as an accepted compatibility result by the main Path runner.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME);
const output = resolve(process.env.NODE_COMPAT_PATH_DIAGNOSTIC_OUTPUT ?? '/tmp/starling-node-compat/foundations-v2/path-dynamic-diagnostic');
const tools = await loadToolchain();
const { componentize, provenance } = await loadComponentizer(tools);
const { componentWit, transpile } = await import(pathToFileURL(tools.require.resolve('@bytecodealliance/jco')));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
const keepStdio = process.env.NODE_COMPAT_DIAGNOSTIC_STDIO === '1';
const preview1AdapterPath = resolve('host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(preview1AdapterPath)), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const selectedInterfaces = keepStdio ? ['wasi:cli/stdin@0.2.10', 'wasi:cli/stdout@0.2.10', 'wasi:cli/stderr@0.2.10',
  'wasi:cli/terminal-input@0.2.10', 'wasi:cli/terminal-output@0.2.10', 'wasi:cli/terminal-stdin@0.2.10',
  'wasi:cli/terminal-stdout@0.2.10', 'wasi:cli/terminal-stderr@0.2.10',
  'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10'] : [];
const hostVersion = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.match(hostVersion.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(tools.directory, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const fixtures = {
  'pure-async': 'export async function run(){await Promise.resolve();return "ok";}',
  'cached-buffer': 'import * as initial from "node:buffer"; export async function run(){const m=await import("node:buffer");return m===initial?"ok":"wrong";}',
  'cached-path': 'import * as initial from "node:path"; export async function run(){const m=await import("node:path");return m===initial?"ok":"wrong";}',
  'first-buffer': 'export async function run(){const m=await import("node:buffer");return typeof m.Buffer==="function"?"ok":"wrong";}',
  'first-path': 'export async function run(){const m=await import("node:path");return m.sep==="/"?"ok":"wrong";}',
  'first-child': 'export async function run(){const m=await import("node:child_process");return typeof m.spawn==="function"?"ok":"wrong";}',
  'first-buffer-caught': 'export async function run(){try{await import("node:buffer");return "ok";}catch(error){return JSON.stringify({name:error.name,message:error.message,stack:error.stack});}}',
  'first-path-caught': 'export async function run(){try{await import("node:path");return "ok";}catch(error){return JSON.stringify({name:error.name,message:error.message,stack:error.stack});}}',
  'first-child-caught': 'export async function run(){try{await import("node:child_process");return "ok";}catch(error){return JSON.stringify({name:error.name,message:error.message,stack:error.stack});}}',
};
if (process.env.NODE_COMPAT_DIAGNOSTIC_CASE) assert(Object.hasOwn(fixtures, process.env.NODE_COMPAT_DIAGNOSTIC_CASE));
const results = [];
for (const [name, source] of Object.entries(fixtures)) {
  if (process.env.NODE_COMPAT_DIAGNOSTIC_CASE && name !== process.env.NODE_COMPAT_DIAGNOSTIC_CASE) continue;
  const { component, interfaceAudit } = await componentize(source, { engine,
    witWorld: 'package audit:dynamic-import; world profile { export run: func() -> string; }', worldName: 'profile',
    preview2Adapter: preview1AdapterPath,
    disableFeatures: [...(keepStdio ? [] : ['stdio']), 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces });
  const path = join(output, name + '.component.wasm'); await writeFile(path, component);
  await writeFile(join(output, name + '.mjs'), source + '\n');
  const wit = await componentWit(component);
  if (!keepStdio) assert.deepEqual(wit.split('\n').filter(line => /^\s*import /.test(line)), []);
  const { files } = await transpile(component, { name });
  for (const [file, bytes] of Object.entries(files)) {
    const destination = join(output, file); await mkdir(dirname(destination), { recursive: true }); await writeFile(destination, bytes);
  }
  let jco;
  try { const instance = await import(pathToFileURL(join(output, name + '.js'))); jco = { values: [instance.run(), instance.run()] }; }
  catch (error) { jco = { name: error.name, message: error.message, stack: error.stack }; }
  const host = spawnSync(wasmtime, ['run', '--invoke', 'run()', path], { encoding: 'utf8', timeout: 120000 });
  results.push({ name, source, sourceSha256: hash(source), componentPath: path, componentSha256: hash(component),
    bytes: component.length, emittedWit: wit, interfaceAudit, jco,
    wasmtime: { status: host.status, signal: host.signal, stdout: host.stdout, stderr: host.stderr, error: host.error?.message } });
  await writeFile(join(output, 'results.json'), JSON.stringify({ engine, engineSha256: metadata.engineSha256,
    keepStdio, selectedInterfaces, componentizer: provenance, wasmtime: hostVersion.stdout.trim(), results }, null, 2) + '\n');
  console.log(JSON.stringify({ name, jco: jco.values ?? jco.message, wasmtime: host.status }));
}
