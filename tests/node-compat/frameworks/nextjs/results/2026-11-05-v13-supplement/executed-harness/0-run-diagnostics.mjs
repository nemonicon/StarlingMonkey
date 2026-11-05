// Supplemental observations only: original19-case/Next results remain intact.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, open, readdir, cp, realpath, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { runOwnedCommand } from '../../foundation-zlib/cost-jco-correctness-candidate-v2/durable-host.mjs';

const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const descriptor = async path => { const bytes = await readFile(path); return { path: resolve(path), sha256: hash(bytes), bytes: bytes.length }; };
async function durable(path, bytes) {
  const file = await open(path, 'wx', 0o600);
  try { await file.writeFile(bytes); await file.sync(); } finally { await file.close(); }
}
const json = (path, value) => durable(path, JSON.stringify(value, null, 2) + '\n');
function diagnosticError(error) { return { name: error?.name, code: error?.code, message: error?.message, stack: error?.stack }; }
async function copyTextFiles(source, destination) {
  await mkdir(destination, { recursive: true, mode: 0o700 });
  for (const entry of await readdir(source, { withFileTypes: true })) {
    if (entry.isFile() && /\.(?:json|wit|log|txt)$/.test(entry.name)) await durable(join(destination, entry.name), await readFile(join(source, entry.name)));
  }
}
async function main() {
  assert.equal(process.version, 'v22.14.0');
  const args = process.argv.slice(2), option = (name, fallback) => { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; };
  const application = await realpath(resolve(option('--application'))), output = resolve(option('--output'));
  assert((await stat(application)).isDirectory()); assert(!output.startsWith(repository + '/'));
  const record = option('--record'), engine = resolve(option('--engine', '/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm'));
  const sourceRoot = resolve(option('--source-root', '/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source'));
  await mkdir(output, { mode: 0o700 }); await mkdir(join(output, 'processes'), { mode: 0o700 });
  await mkdir(join(output, 'wasm'), { mode: 0o700 }); await mkdir(join(output, 'executed-harness'), { mode: 0o700 });
  const probe = join(here, 'probes/native-modules.mjs');
  const files = [fileURLToPath(import.meta.url), join(here, 'wasm-worker.mjs'), probe, join(application, 'lib/compat.mjs')];
  const report = { schemaVersion: 1, suite: 'nextjs-supported-native-supplement-v1', application, output,
    originalSuiteReplaced: false, originalCompatFailureReplaced: false, fullNextServerInWasm: false,
    selectedInterfaces: [], startedAtUtc: new Date().toISOString(), commands: [], wasm: [], errors: [],
    sourceFiles: await Promise.all(files.map(descriptor)), engine: await descriptor(engine), metadata: await descriptor(engine + '.build.json'),
    runtimeAcceptance: false, generalNodeCompatibility: false };
  for (let i = 0; i < files.length; i++) await durable(join(output, 'executed-harness', i + '-' + files[i].split('/').at(-1)), await readFile(files[i]));
  const save = async () => {
    const file = await open(join(output, 'results.json'), 'w', 0o600);
    try { await file.writeFile(JSON.stringify(report, null, 2) + '\n'); await file.sync(); } finally { await file.close(); }
  };
  await save();
  async function command(name, argv, timeoutMs) {
    const result = await runOwnedCommand({ output, name, executable: process.execPath, args: argv,
      write: writeFile, register: () => {}, timeoutMs, maxOutputBytes: 16 * 1024 * 1024 });
    const terminal = JSON.parse(await readFile(result.terminalPath)); report.commands.push(terminal);
    for (const [kind, row] of [['stdout', result.stdoutFile], ['stderr', result.stderrFile]]) await durable(join(output, name + '.' + kind + '.log'), await readFile(row.path));
    await json(join(output, name + '.terminal.json'), terminal); await save();
    return result;
  }
  try {
    process.env.NODE_COMPAT_TOOLCHAIN ??= '/private/tmp/starling-node-compat/toolchain';
    process.env.NODE_COMPAT_COMPONENTIZE_MODULE ??= '/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js';
    process.env.NODE_COMPAT_WASMTIME ??= '/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime';
    report.toolEnvironment = Object.fromEntries(['NODE_COMPAT_TOOLCHAIN', 'NODE_COMPAT_COMPONENTIZE_MODULE', 'NODE_COMPAT_WASMTIME'].map(k => [k, process.env[k]]));
    const oracle = await command('node-native-modules', [fileURLToPath(import.meta.url), '--node-probe', probe], 30000);
    assert(oracle.terminalExitZeroObserved && oracle.ownedGroupGone, 'Same-source Node control did not exit zero and clean');
    const raw = await readFile(oracle.stdoutFile.path, 'utf8');
    assert(raw.endsWith('\n') && !raw.endsWith('\n\n'), 'Node control must print exactly one full returned string plus LF');
    const nodeString = raw.slice(0, -1); await durable(join(output, 'node-native-modules.string.txt'), nodeString);
    const nodeValue = JSON.parse(nodeString); await json(join(output, 'node-native-modules.parsed.json'), nodeValue);
    report.nodeControl = { rawStdout: oracle.stdoutFile, string: await descriptor(join(output, 'node-native-modules.string.txt')),
      source: report.sourceFiles[2], passed: true, value: nodeValue };
    await save();
    for (const name of ['compat-caught', 'native-modules']) {
      const destination = join(output, 'wasm', name);
      const result = await command('wasm-' + name, [join(here, 'wasm-worker.mjs'), '--case', name, '--application', application,
        '--output', destination, '--engine', engine, '--source-root', sourceRoot], 240000);
      const observed = JSON.parse(await readFile(join(destination, 'result.json')));
      const terminalComplete = result.terminalExitZeroObserved && result.ownedGroupGone && observed.case === name &&
        typeof observed.finishedAtUtc === 'string' && ['passed', 'failed', 'refused', 'missing-fixture'].includes(observed.status);
      report.wasm.push({ id: name, report: observed, actualWorkerTerminal: result.terminalPath, terminalComplete });
      await save(); assert(terminalComplete, name + ' did not produce a complete zero-exit clean observation');
    }
    const caught = report.wasm.find(row => row.id === 'compat-caught');
    if (caught.report.status === 'passed') {
      const value = JSON.parse(await readFile(join(output, 'wasm/compat-caught/jco-0.parsed.json')));
      report.originalFailureDiagnostic = { diagnosticOnly: true, value,
        matched: value.caught === true && value.code === 'ERR_SM_NODE_UNSUPPORTED' && typeof value.message === 'string' && value.message.includes('node:util.format') };
    } else report.originalFailureDiagnostic = { diagnosticOnly: true, matched: false, stage: caught.report.stage };
    const positive = report.wasm.find(row => row.id === 'native-modules');
    if (positive.report.status === 'passed') {
      const guestString = await readFile(join(output, 'wasm/native-modules/jco-0.string.txt'), 'utf8');
      const wasmtimeString = await readFile(join(output, 'wasm/native-modules/wasmtime.string.txt'), 'utf8');
      const value = JSON.parse(guestString);
      report.supportedDifferential = { performed: true, fullNodeStringEqual: guestString === nodeString,
        fullWasmtimeStringEqual: wasmtimeString === nodeString, fullStructuredValueEqual: isDeepStrictEqual(value, nodeValue), value,
        passed: guestString === nodeString && wasmtimeString === nodeString && isDeepStrictEqual(value, nodeValue),
        scope: 'Exact supported-API fixture only; no repair of original util.format case or framework acceptance' };
    } else report.supportedDifferential = { performed: false, passed: false, actualStage: positive.report.stage };
  } catch (error) { report.errors.push(diagnosticError(error)); }
  for (const before of report.sourceFiles) {
    try { assert.deepEqual(await descriptor(before.path), before); }
    catch (error) { report.errors.push({ stage: 'post-source-check', ...diagnosticError(error) }); }
  }
  report.finishedAtUtc = new Date().toISOString();
  report.passed = report.errors.length === 0 && report.originalFailureDiagnostic?.matched === true && report.supportedDifferential?.passed === true &&
    report.wasm.length === 2 && report.wasm.every(row => row.terminalComplete);
  await save();
  if (record) {
    const destination = resolve(record); await mkdir(dirname(destination), { recursive: true }); await mkdir(destination, { mode: 0o700 });
    await copyTextFiles(output, destination); await cp(join(output, 'executed-harness'), join(destination, 'executed-harness'), { recursive: true });
    for (const row of report.wasm) await copyTextFiles(join(output, 'wasm', row.id), join(destination, 'wasm', row.id));
  }
  process.stdout.write(JSON.stringify({ output, passed: report.passed, originalFailureDiagnostic: report.originalFailureDiagnostic,
    supportedDifferential: report.supportedDifferential, errors: report.errors }, null, 2) + '\n');
  if (!report.passed) process.exitCode = 1;
}
if (process.argv[2] === '--node-probe') {
  assert.equal(process.version, 'v22.14.0'); assert.equal(process.argv.length, 4);
  const source = await import(pathToFileURL(resolve(process.argv[3])));
  const value = await source.run(); assert.equal(typeof value, 'string'); process.stdout.write(value + '\n');
} else await main();
