// Stage a reviewable test-policy patch only. Never writes active harness files.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../..');
const directory = join(here, 'harness'), base = join(directory, 'base'), source = join(directory, 'source');
const receipt = JSON.parse(await readFile(join(here, 'source-receipt.json')));
const hash = value => createHash('sha256').update(value).digest('hex');
let existing = true;
try { await stat(directory); } catch (error) { if (error.code !== 'ENOENT') throw error; existing = false; }
if (existing && !process.argv.includes('--from-base')) throw new Error('Harness candidates already staged; use --from-base to preserve and reuse the saved bases');
const paths = ['fixtures/component.mjs', 'optimization/intrinsics-checks.mjs', 'run.mjs',
  'wasmcloud/build-http.mjs', 'wasmcloud/test-wasmtime-http.mjs', 'wasmcloud/run-host.mjs', 'optimized-profile-tests.mjs'];
const files = new Map();
for (const name of paths) {
  const path = 'tests/node-compat/'+name, text = await readFile(join(existing ? base : repository, path), 'utf8');
  if (!existing) { await mkdir(dirname(join(base, path)), { recursive: true }); await writeFile(join(base, path), text); }
  files.set(path, text);
}
function change(path, before, after) {
  const full = 'tests/node-compat/'+path, text = files.get(full);
  assert.equal(text.split(before).length, 2, 'Expected exact single edit boundary: '+path+' '+before);
  files.set(full, text.replace(before, after));
}
const relevant = receipt.changed.concat(receipt.unchanged.filter(item => item.path === 'builtins/node-compat/buffer.cpp'));
const known = Object.fromEntries([
  ['sm-node-22.14.0-m0.1', 'before', 'deferred', ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']],
  ['sm-node-22.14.0-m0.8', 'after', 'zeroed-no-pool-v1', ['copyBytesFrom', 'of', 'allocUnsafeSlow', 'compare', 'concat']],
].map(([version, side, allocUnsafePolicy, unsupportedStatic]) => [version, {
  allocUnsafePolicy, unsupportedStatic, hashes: Object.fromEntries(relevant.map(item => [item.path, item[side]])),
}]));
const helper = `// TEST EXPECTATIONS ONLY. No guest API or runtime feature toggle.\n`+
`// Select solely from an exact recognized core source receipt, after engine-byte verification.\n`+
`import assert from 'node:assert/strict';\nimport { createHash } from 'node:crypto';\n`+
`import { readFileSync } from 'node:fs';\nimport { resolve } from 'node:path';\n`+
`import { CORE_MANIFEST, selectedManifestsForEngine } from './module-selection.mjs';\n`+
`const known = ${JSON.stringify(known, null, 2)};\n`+
`const hash = value => createHash('sha256').update(value).digest('hex');\n`+
`function expected(version) {\n`+
`  const core = known[version]; assert(core && Object.hasOwn(known, version), 'Unrecognized core compatibility version');\n`+
`  return { schema: 1, coreVersion: version, allocUnsafePolicy: core.allocUnsafePolicy,\n`+
`    unsupportedStatic: [...core.unsupportedStatic], prototypeRefusals: 91,\n`+
`    manifestSha256: core.hashes[CORE_MANIFEST], sourceHashes: { ...core.hashes } };\n}\n`+
`export function validateCoreExpectations(value) {\n`+
`  assert(value && typeof value === 'object' && !Array.isArray(value), 'Missing core expectations');\n`+
`  assert.deepEqual(value, expected(value.coreVersion), 'Core expectation fields disagree with the recognized source contract');\n`+
`  return value;\n}\n`+
`export function selectCoreExpectations(metadata, { sourceRoot }) {\n`+
`  assert(typeof sourceRoot === 'string' && sourceRoot.length, 'Core policy requires explicit sourceRoot');\n`+
`  const root = resolve(sourceRoot);\n`+
`  const manifests = selectedManifestsForEngine(metadata, { sourceRoot: root });\n`+
`  const manifest = manifests.find(item => Object.hasOwn(item.modules, 'node:buffer'));\n`+
`  assert(manifest, 'Core manifest must contain Buffer'); const version = manifest.profileVersion;\n`+
`  const value = expected(version), sources = new Map();\n`+
`  for (const entry of metadata.sourceManifest) {\n`+
`    assert(entry && typeof entry.path === 'string' && typeof entry.sha256 === 'string' && /^[0-9a-f]{64}$/.test(entry.sha256), 'Malformed source receipt');\n`+
`    assert(!sources.has(entry.path), 'Duplicate compiled input path'); sources.set(entry.path, entry.sha256);\n`+
`  }\n`+
`  for (const [path, digest] of Object.entries(value.sourceHashes)) {\n`+
`    assert.equal(sources.get(path), digest, 'Core source receipt does not match selected profile: '+path);\n`+
`    const absolute = resolve(root, path); assert(absolute.startsWith(root+'/'), 'Core source escapes selected root');\n`+
`    assert.equal(hash(readFileSync(absolute)), digest, 'Core source bytes do not match selected profile: '+path);\n`+
`  }\n`+
`  assert.deepEqual(manifest.modules['node:buffer'].unsupportedStatic, value.unsupportedStatic);\n`+
`  return Object.freeze({ ...value, unsupportedStatic: Object.freeze(value.unsupportedStatic), sourceHashes: Object.freeze(value.sourceHashes) });\n}\n`;
files.set('tests/node-compat/core-expectations.mjs', helper);
change('fixtures/component.mjs', "import corpus from 'node-compat:oracle-vectors';", "import corpus from 'node-compat:oracle-vectors';\nimport coreExpectations from 'node-compat:core-expectations';");
change('fixtures/component.mjs', "equal(value.profile, 'sm-node-22.14.0-m0.1', 'unsupported profile version')", "equal(value.profile, coreExpectations.coreVersion, 'unsupported profile version')");
change('fixtures/component.mjs', "  for (const name of ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']) unsupported(() => Buffer[name]());", `  for (const name of coreExpectations.unsupportedStatic) {
    unsupported(() => Buffer[name]());
    unsupported(() => new Buffer[name]());
  }
  // Build-time receipt policy is mandatory; never probe a truthy deferred function.
  if (coreExpectations.allocUnsafePolicy === 'zeroed-no-pool-v1') {
    for (const size of [0, 0.5, 1.9, 17, 1024]) {
      const a = Buffer.allocUnsafe(size), b = new Buffer.allocUnsafe(size);
      equal(a.length, Math.trunc(size), 'allocUnsafe truncated size');
      equal(a.byteOffset, 0, 'allocUnsafe zero offset');
      equal(a.buffer.byteLength, a.length, 'allocUnsafe exact backing');
      check(a.buffer !== b.buffer && Buffer.isBuffer(a) && Buffer.isBuffer(b), 'allocUnsafe fresh owned brand');
      for (const byte of a) equal(byte, 0, 'allocUnsafe zero initialization');
    }
    for (const value of [-1, -0.5, NaN, Infinity, 16777216.25, 16777217]) error(() => Buffer.allocUnsafe(value), 'ERR_OUT_OF_RANGE');
    for (const value of [undefined, null, '1', 1n]) error(() => Buffer.allocUnsafe(value), 'ERR_INVALID_ARG_TYPE');
  } else if (coreExpectations.allocUnsafePolicy !== 'deferred') {
    throw new Error('Unrecognized allocUnsafe test policy');
  }`);
change('fixtures/component.mjs', '  return JSON.stringify({ calls: ++calls, snapshot:', '  equal(unavailableMethods, coreExpectations.prototypeRefusals, \'own prototype refusal count\');\n  return JSON.stringify({ coreVersion: coreExpectations.coreVersion, allocUnsafePolicy: coreExpectations.allocUnsafePolicy, calls: ++calls, snapshot:');
change('optimization/intrinsics-checks.mjs', '// Guest-safe checks against the ACTUAL registered native module.', "import coreExpectations from 'node-compat:core-expectations';\n// Guest-safe checks against the ACTUAL registered native module.");
change('optimization/intrinsics-checks.mjs', "equal(error.profile, 'sm-node-22.14.0-m0.1', 'unsupported profile')", "equal(error.profile, coreExpectations.coreVersion, 'unsupported profile')");
change('run.mjs', "import { selectedManifestsForEngine } from './module-selection.mjs';", "import { selectedManifestsForEngine } from './module-selection.mjs';\nimport { selectCoreExpectations } from './core-expectations.mjs';");
change('run.mjs', 'const corpus = makeOracleCorpus();', 'const coreExpectations = selectCoreExpectations(engineMetadata, { sourceRoot });\nconst corpus = makeOracleCorpus();');
change('run.mjs', "const virtualModules = { 'node-compat:oracle-vectors': `export default ${JSON.stringify(corpus)};` };", "const virtualModules = { 'node-compat:oracle-vectors': `export default ${JSON.stringify(corpus)};`,\n  'node-compat:core-expectations': `export default ${JSON.stringify(coreExpectations)};` };");
change('run.mjs', '  semanticEntry, sourceRoot,', '  semanticEntry, sourceRoot, coreExpectations,');
change('wasmcloud/build-http.mjs', "import { selectedManifestsForEngine } from '../module-selection.mjs';", "import { selectedManifestsForEngine } from '../module-selection.mjs';\nimport { selectCoreExpectations } from '../core-expectations.mjs';");
change('wasmcloud/build-http.mjs', 'const corpus = makeOracleCorpus();', 'const coreExpectations = selectCoreExpectations(engineMetadata, { sourceRoot: engineSourceRoot });\nconst corpus = makeOracleCorpus();');
change('wasmcloud/build-http.mjs', "const virtualModules = { 'node-compat:oracle-vectors':", "const virtualModules = { 'node-compat:core-expectations': `export default ${JSON.stringify(coreExpectations)};`, 'node-compat:oracle-vectors':");
change('wasmcloud/build-http.mjs', '  world: \'starling:node-compat-http-test/profile@0.1.0\',', '  coreExpectations,\n  world: \'starling:node-compat-http-test/profile@0.1.0\',');
for (const name of ['wasmcloud/test-wasmtime-http.mjs', 'wasmcloud/run-host.mjs']) {
  change(name, "import assert from 'node:assert/strict';", "import assert from 'node:assert/strict';\nimport { validateCoreExpectations } from '../core-expectations.mjs';");
  const auditRead = name.endsWith('run-host.mjs') ? 'const audit = JSON.parse(await readFile(auditPath, \'utf8\'));' : 'const audit = JSON.parse(await readFile(auditPath));';
  change(name, auditRead, auditRead+'\nconst coreExpectations = validateCoreExpectations(audit.coreExpectations);');
  change(name, "assert.equal(body[field].profile, 'sm-node-22.14.0-m0.1');", "assert.equal(body[field].profile, coreExpectations.coreVersion);");
  change(name, '    assert.equal(body.native.strings, 381);', '    assert.equal(body.native.coreVersion, coreExpectations.coreVersion);\n    assert.equal(body.native.allocUnsafePolicy, coreExpectations.allocUnsafePolicy);\n    assert.equal(body.native.strings, 381);');
}
change('optimized-profile-tests.mjs', "import { createBufferModule, MAX_LENGTH } from '../../builtins/node-compat/buffer-facade.mjs';", "import { createBufferModule, MAX_LENGTH } from '../../builtins/node-compat/buffer-facade.mjs';\nimport { PROFILE_VERSION } from '../../builtins/node-compat/unsupported.mjs';");
change('optimized-profile-tests.mjs', "profile: 'sm-node-22.14.0-m0.1'", 'profile: PROFILE_VERSION');
let patch = '';
const changes = [];
for (const [path, text] of files) {
  await mkdir(dirname(join(source, path)), { recursive: true }); await writeFile(join(source, path), text);
  const before = paths.includes(path.replace('tests/node-compat/', '')) ? join(base, path) : '/dev/null';
  const diff = spawnSync('diff', ['-u', '--label', before === '/dev/null' ? '/dev/null' : 'a/'+path, before, '--label', 'b/'+path, join(source, path)], { encoding: 'utf8' });
  assert.equal(diff.status, 1); patch += diff.stdout;
  changes.push({ path, before: before === '/dev/null' ? null : hash(await readFile(before)), after: hash(text) });
}
await writeFile(join(here, 'harness-m0.8.patch'), patch);
await writeFile(join(here, 'harness-receipt.json'), JSON.stringify({ schema: 1, installed: false,
  sourceReceiptSha256: hash(await readFile(join(here, 'source-receipt.json'))), patchSha256: hash(patch), changes,
  controls: ['sm-node-22.14.0-m0.1', 'sm-node-22.14.0-m0.8'],
  immutable: ['Historical JSON reports and milestone copies', 'Original isolated m0.1 allocUnsafe wrapper experiment and receipts'],
  scope: 'Unapplied active-harness migration candidate. No native/component execution of these staged harness copies yet.' }, null, 2)+'\n');
console.log(JSON.stringify({ installed: false, paths: changes.map(item => item.path), versions: Object.keys(known) }));
