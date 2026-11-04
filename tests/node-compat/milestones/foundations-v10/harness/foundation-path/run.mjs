import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { selectedManifestsForEngine } from '../module-selection.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
assert(process.env.NODE_COMPAT_ENGINE && process.env.NODE_COMPAT_WASMTIME, 'Explicit rebuilt Path engine and Wasmtime42 paths required');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME);
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const output = resolve(process.env.NODE_COMPAT_PATH_OUTPUT ?? '/tmp/starling-node-compat/foundation-path');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
assert.equal(metadata.pathEnabled, true);
assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_PATH, 'ON');
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE, 'Release', 'DEBUG indirect canonical memory is unavailable');
for (const entry of metadata.sourceManifest) {
  const path = resolve(sourceRoot, entry.path); assert(path.startsWith(sourceRoot + '/'));
  assert.equal(hash(await readFile(path)), entry.sha256, 'Stale engine source: ' + entry.path);
}
const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });
assert(builtinManifests.some(manifest => Object.hasOwn(manifest.modules, 'node:path')));
const toolchain = await loadToolchain();
const { componentize, provenance } = await loadComponentizer(toolchain);
const { componentWit, transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const hostVersion = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(hostVersion.status, 0, hostVersion.stderr); assert.match(hostVersion.stdout, /^wasmtime 42\.0\.1\b/);
for (const [file, flags] of [['semantic.mjs', []], ['glob.mjs', ['--expose-internals']]]) {
  const result = spawnSync(process.execPath, [...flags, join(here, file)], { encoding: 'utf8', timeout: 30000 });
  assert.equal(result.status, 0, result.stderr || result.stdout);
}
const lexical = JSON.parse(await readFile(join(here, 'lexical-vectors.json')));
const globs = JSON.parse(await readFile(join(here, 'glob-vectors.json')));
const globReport = JSON.parse(await readFile(join(here, 'glob-results.json')));
const manifest = builtinManifests.find(manifest => Object.hasOwn(manifest.modules, 'node:path'));
const corpus = { lexical, globs, denied: globReport.denied, acceptedAdversarial: globReport.acceptedAdversarial,
  exportNames: [...manifest.modules['node:path'].exports].sort() };
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const options = { engine, witWorld: await readFile(join(here, 'profile.wit'), 'utf8'), worldName: 'profile',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
async function artifact(name, source) {
  const { component, interfaceAudit } = await componentize(source, options);
  const path = join(output, name + '.component.wasm'); await writeFile(path, component);
  const wit = await componentWit(component);
  assert.deepEqual(wit.split('\n').filter(line => /^\s*import /.test(line)), [], 'Pure Path fixture must import no capabilities');
  await writeFile(join(output, name + '.wit'), wit);
  const { files } = await transpile(component, { name });
  for (const [filename, bytes] of Object.entries(files)) {
    const destination = join(output, filename); await mkdir(dirname(destination), { recursive: true }); await writeFile(destination, bytes);
  }
  const instance = await import(pathToFileURL(join(output, name + '.js')));
  return { path, instance, componentBytes: component.length, componentSha256: hash(component), emittedWit: wit,
    emittedImports: [], interfaceAudit };
}
const bundle = await bundleProfile({ ...toolchain, input: join(here, 'component.mjs'), builtinManifests,
  virtualModules: { 'node-compat:path-oracles': 'export default ' + JSON.stringify(corpus) + ';' } });
assert.deepEqual(bundle.imports.sort(), ['node:path', 'node:path/posix', 'node:path/win32']);
assert(bundle.moduleIds.every(id => !/node_modules|path-matcher|path-vendor|builtins\/node-compat\/path\.mjs/.test(id)),
  'Application bundle must use registered native modules, never inline a guest replacement');
await writeFile(join(output, 'application.bundle.mjs'), bundle.code);
const semantic = await artifact('path', bundle.code);
function check(report, call) {
  assert(!report.failure, JSON.stringify(report.failure)); assert.equal(report.calls, call);
  assert.equal(report.lexical, lexical.length); assert.equal(report.globs, globs.length);
  assert.equal(report.budgets, corpus.denied.length); assert.equal(report.acceptedAdversarial, corpus.acceptedAdversarial.length);
  assert.equal(report.invalid, 12);
  for (const field of ['snapshotPure', 'identities', 'mutableDefaults', 'noEntropy']) assert.equal(report[field], true, field);
}
const calls = [];
for (let i = 1; i <= 3; i++) { const report = JSON.parse(await semantic.instance.run()); check(report, i); calls.push(report); }
function hostRun(path) {
  const result = spawnSync(wasmtime, ['run', '--invoke', 'run()', path], { encoding: 'utf8', timeout: 180000 });
  assert.equal(result.status, 0, result.error?.message || result.stderr);
  return JSON.parse(JSON.parse(result.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,
    (_, hex) => String.fromCodePoint(parseInt(hex, 16)))));
}
const wasmtimeReport = hostRun(semantic.path); check(wasmtimeReport, 1);
const aliases = await artifact('aliases', await readFile(join(here, 'raw-aliases.mjs'), 'utf8'));
const aliasCalls = [];
for (let i = 1; i <= 2; i++) {
  const report = JSON.parse(await aliases.instance.run()); assert.equal(report.calls, i);
  assert.equal(report.nativeAliases, 6); assert(report.caching && report.identities); aliasCalls.push(report);
}
const aliasHost = hostRun(aliases.path); assert.equal(aliasHost.nativeAliases, 6); assert(aliasHost.caching && aliasHost.identities);
const topLevelFailures = [];
for (const [filename, expected] of [['top-level-invalid.mjs', /must be of type string/],
  ['top-level-budget.mjs', /node:path\.matchesGlob exceeds profile budget: brace-alternatives/]]) {
  const bundled = await bundleProfile({ ...toolchain, input: join(here, filename), builtinManifests });
  let message;
  try { await componentize(bundled.code, options); } catch (error) { message = error.message; }
  assert.match(message ?? '', expected, 'Top-level invalid/budget operation must fail componentization');
  topLevelFailures.push({ filename, failed: true, expected: String(expected) });
}
const result = { schema: 1, verifiedAtUtc: new Date().toISOString(), node: process.version,
  engine, engineSha256: metadata.engineSha256, metadata, sourceRoot, componentizer: provenance,
  builtinManifests: metadata.selectedModuleManifests, wasmtime: hostVersion.stdout.trim(),
  component: { path: semantic.path, sha256: semantic.componentSha256, bytes: semantic.componentBytes,
    emittedImports: [], emittedWit: semantic.emittedWit, interfaceAudit: semantic.interfaceAudit },
  bundle: { imports: bundle.imports, moduleIds: bundle.moduleIds }, calls, wasmtimeReport,
  aliases: { componentPath: aliases.path, sha256: aliases.componentSha256, bytes: aliases.componentBytes,
    emittedImports: [], interfaceAudit: aliases.interfaceAudit, calls: aliasCalls, wasmtimeReport: aliasHost }, topLevelFailures,
  hostSemanticResults: JSON.parse(await readFile(join(here, 'semantic-results.json'))), globReport,
  sourceManifest: await Promise.all(['component.mjs', 'static-require.cjs', 'raw-aliases.mjs', 'profile.wit',
    'top-level-budget.mjs', 'top-level-invalid.mjs', 'semantic.mjs', 'glob.mjs', 'run.mjs',
    'lexical-vectors.json', 'glob-vectors.json'].map(async path => ({ path, sha256: hash(await readFile(join(here, path))) }))),
  limitations: ['Virtual cwd and fixed POSIX-host glob case policy are explicit deviations; no host environment, filesystem or drive-state behavior is claimed.',
    'Matcher resource budgets intentionally exclude unbounded inputs and replace upstream silent truncation with coded RangeError.',
    'No broad DEBUG indirect Component Model ABI support is claimed. This uses the audited Release engine.'] };
await writeFile(join(output, 'results.json'), JSON.stringify(result, null, 2) + '\n');
await writeFile(join(here, 'results.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output, lexical: lexical.length, globs: globs.length, aliases: 6,
  zeroImports: true, wasmtimePassed: true, componentSha256: semantic.componentSha256 }, null, 2));
