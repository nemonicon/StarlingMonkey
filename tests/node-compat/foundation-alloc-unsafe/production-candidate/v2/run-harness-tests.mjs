// Host-only tests of the UNAPPLIED receipt-selected harness migration.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, cp } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../../..');
const hash = value => createHash('sha256').update(value).digest('hex');
const sourceReceipt = JSON.parse(await readFile(join(here, 'source-receipt.json')));
const receipt = JSON.parse(await readFile(join(here, 'harness-receipt.json')));
assert.equal(receipt.sourceReceiptSha256, hash(await readFile(join(here, 'source-receipt.json'))));
const root = join(here, 'harness/source'), cases = [];
for (const item of receipt.changes) {
  const candidate = join(root, item.path);
  assert.equal(hash(await readFile(candidate)), item.after);
  if (item.before) {
    assert.equal(hash(await readFile(join(here, 'harness/base', item.path))), item.before);
    assert.equal(hash(await readFile(join(repository, item.path))), item.before, 'Active harness unchanged: '+item.path);
  }
  const syntax = spawnSync(process.execPath, ['--check', candidate], { encoding: 'utf8' });
  assert.equal(syntax.status, 0, syntax.stderr);
}
const patchPath = join(here, 'harness-m0.8.patch');
assert.equal(hash(await readFile(patchPath)), receipt.patchSha256);
const patch = spawnSync('git', ['apply', '--check', patchPath], { cwd: repository, encoding: 'utf8' });
assert.equal(patch.status, 0, patch.stderr);
const helperPath = join(root, 'tests/node-compat/core-expectations.mjs');
const originalHelper = await readFile(helperPath, 'utf8');
// The isolated tree deliberately contains only changed files. Relocate this
// one host import to the actual unchanged module selector; helper body is exact.
const helperSource = originalHelper.replace("from './module-selection.mjs'", 'from '+JSON.stringify(pathToFileURL(join(repository, 'tests/node-compat/module-selection.mjs')).href));
assert.notEqual(helperSource, originalHelper);
const { selectCoreExpectations, validateCoreExpectations } = await import('data:text/javascript;base64,'+Buffer.from(helperSource).toString('base64'));
function pass(name, run) { const result = run(); cases.push({ name, passed: true }); return result; }
function deny(name, run) { assert.throws(run); cases.push({ name, rejected: true }); }
const clone = value => structuredClone(value);
const controls = [];
let baseMetadata;
for (const milestone of ['foundations-v6', 'foundations-v7']) {
  const sourceRoot = '/tmp/starling-node-compat/'+milestone+'/native-freeze/source';
  const metadata = JSON.parse(await readFile(resolve(sourceRoot, '../off-foundations.engine.wasm.build.json')));
  const selected = pass(milestone+' exact original core receipt', () => selectCoreExpectations(metadata, { sourceRoot }));
  assert.equal(selected.coreVersion, 'sm-node-22.14.0-m0.1'); assert.equal(selected.allocUnsafePolicy, 'deferred');
  assert.equal(selected.prototypeRefusals, 91); assert(selected.unsupportedStatic.includes('allocUnsafe'));
  assert(Object.isFrozen(selected) && Object.isFrozen(selected.sourceHashes) && Object.isFrozen(selected.unsupportedStatic));
  controls.push({ milestone, engineSha256: metadata.engineSha256, policy: selected });
  if (milestone === 'foundations-v7') baseMetadata = metadata;
}
// Constructed receipt data is only a selector unit-test fixture. It identifies
// no built m0.8 artifact and is never sent to a componentizer/host.
const metadata = clone(baseMetadata), candidateRoot = join(here, 'source');
for (const item of sourceReceipt.changed) {
  metadata.sourceManifest.find(input => input.path === item.path).sha256 = item.after;
  const selected = metadata.selectedModuleManifests.find(input => input.path === item.path);
  if (selected) { selected.sha256 = item.after; selected.profileVersion = 'sm-node-22.14.0-m0.8'; }
}
const candidate = pass('synthetic m0.8 receipt with exact staged source bytes', () => selectCoreExpectations(metadata, { sourceRoot: candidateRoot }));
assert.equal(candidate.coreVersion, 'sm-node-22.14.0-m0.8'); assert.equal(candidate.allocUnsafePolicy, 'zeroed-no-pool-v1');
assert(!candidate.unsupportedStatic.includes('allocUnsafe')); assert(candidate.unsupportedStatic.includes('allocUnsafeSlow'));
for (const policy of [controls[0].policy, candidate]) pass(policy.coreVersion+' JSON payload validates', () => validateCoreExpectations(clone(policy)));

for (const [name, edit] of [
  ['profile disabled', m => { m.profileEnabled = false; }],
  ['profile truthy string', m => { m.profileEnabled = 'true'; }],
  ['missing source manifest', m => { delete m.sourceManifest; }],
  ['source manifest object', m => { m.sourceManifest = {}; }],
  ['missing explicit optional selection', m => { delete m.selectedModuleManifests; }],
  ['omitted selected core manifest', m => { m.selectedModuleManifests = m.selectedModuleManifests.filter(e => !e.path.endsWith('export-manifest.node-v22.14.0.json')); }],
  ['duplicate selected core manifest', m => { m.selectedModuleManifests.push(clone(m.selectedModuleManifests[0])); }],
  ['wrong selected manifest SHA', m => { m.selectedModuleManifests[0].sha256 = '0'.repeat(64); }],
  ['wrong selected version', m => { m.selectedModuleManifests[0].profileVersion = 'sm-node-22.14.0-m0.1'; }],
  ['wrong compiled manifest SHA', m => { m.sourceManifest.find(e => e.path.endsWith('export-manifest.node-v22.14.0.json')).sha256 = '0'.repeat(64); }],
  ['old facade under new manifest', m => { const e = sourceReceipt.changed.find(e => e.path.endsWith('/buffer-facade.mjs')); m.sourceManifest.find(input => input.path === e.path).sha256 = e.before; }],
  ['omitted native Buffer source', m => { m.sourceManifest = m.sourceManifest.filter(e => e.path !== 'builtins/node-compat/buffer.cpp'); }],
  ['duplicate compiled input', m => { m.sourceManifest.push(clone(m.sourceManifest[0])); }],
  ['malformed compiled input', m => { m.sourceManifest.push({path:'arbitrary', sha256:123}); }],
  ['missing compiled hash', m => { delete m.sourceManifest[0].sha256; }],
  ['optional observed flag conflict', m => { m.observedCMakeOptions.NODE_COMPAT_UTIL = 'OFF'; }],
  ['optional flag truthy string', m => { m.utilEnabled = 'true'; }],
]) {
  const changed = clone(metadata); edit(changed);
  deny(name, () => selectCoreExpectations(changed, { sourceRoot: candidateRoot }));
}
deny('missing explicit source root', () => selectCoreExpectations(metadata, {}));
deny('old exact receipt cannot select staged new bytes', () => selectCoreExpectations(baseMetadata, { sourceRoot: candidateRoot }));
deny('new receipt cannot select archived old bytes', () => selectCoreExpectations(metadata, { sourceRoot: '/tmp/starling-node-compat/foundations-v7/native-freeze/source' }));
for (const value of [undefined, null, false, 'm0.8', [], {}, {coreVersion:'__proto__'}, {coreVersion:'sm-node-22.14.0-m0.9'}]) {
  deny('malformed or unknown policy '+String(value?.coreVersion ?? value), () => validateCoreExpectations(value));
}
for (const [name, edit] of [
  ['missing version', p => { delete p.coreVersion; }],
  ['unknown schema', p => { p.schema = 2; }],
  ['wrong allocator policy', p => { p.allocUnsafePolicy = 'deferred'; }],
  ['truthy allocator policy', p => { p.allocUnsafePolicy = true; }],
  ['wrong prototype count', p => { p.prototypeRefusals = 90; }],
  ['wrong manifest hash', p => { p.manifestSha256 = '0'.repeat(64); }],
  ['missing source hashes', p => { delete p.sourceHashes; }],
  ['extra runtime toggle', p => { p.enableAllocUnsafe = true; }],
  ['deferred static returned', p => { p.unsupportedStatic.push('allocUnsafe'); }],
  ['Slow removed', p => { p.unsupportedStatic = p.unsupportedStatic.filter(n => n !== 'allocUnsafeSlow'); }],
]) { const changed = clone(candidate); edit(changed); deny(name, () => validateCoreExpectations(changed)); }

const unknownRoot = join(here, 'harness/fixtures/unknown-core');
await mkdir(join(unknownRoot, 'builtins/node-compat'), { recursive: true });
const unknown = clone(metadata);
for (const entry of unknown.selectedModuleManifests) {
  const destination = join(unknownRoot, entry.path); await mkdir(dirname(destination), { recursive: true });
  await cp(join(candidateRoot, entry.path), destination);
}
const manifestPath = join(unknownRoot, 'builtins/node-compat/export-manifest.node-v22.14.0.json');
const manifest = JSON.parse(await readFile(manifestPath)); manifest.profileVersion = 'sm-node-22.14.0-m0.9';
const unknownBytes = JSON.stringify(manifest, null, 2)+'\n'; await writeFile(manifestPath, unknownBytes);
const manifestName = 'builtins/node-compat/export-manifest.node-v22.14.0.json';
unknown.sourceManifest.find(e => e.path === manifestName).sha256 = hash(unknownBytes);
Object.assign(unknown.selectedModuleManifests.find(e => e.path === manifestName), {sha256:hash(unknownBytes), profileVersion:manifest.profileVersion});
deny('well-shaped unknown source version rejected before source policy expansion', () => selectCoreExpectations(unknown, { sourceRoot: unknownRoot }));

// Exercise the staged existing source-only regression body against both source
// versions. Only import URLs relocate to preserved source/kernel files.
const regression = await readFile(join(root, 'tests/node-compat/optimized-profile-tests.mjs'), 'utf8');
for (const versionRoot of ['base', 'source']) {
  let text = regression;
  for (const name of ['buffer-facade.mjs', 'unsupported.mjs']) text = text.replace("'../../builtins/node-compat/"+name+"'", JSON.stringify(pathToFileURL(join(here, versionRoot, 'builtins/node-compat', name)).href));
  text = text.replace("'../../docs/node-compat/templates/reference-kernel.mjs'", JSON.stringify(pathToFileURL(join(repository, 'docs/node-compat/templates/reference-kernel.mjs')).href));
  await import('data:text/javascript;base64,'+Buffer.from(text).toString('base64'));
  cases.push({name:'staged original source regression body '+versionRoot, passed:true});
}
const report = {schema:1, installed:false, hostOnly:true, cases, syntaxCheckedFiles:receipt.changes.length,
  archivedReceiptSelections:controls, syntheticCandidatePolicy:candidate, syntheticCandidateReceiptIsNotABuild:true,
  patchApplyCheck:true, patchSha256:receipt.patchSha256, helperSha256:hash(originalHelper),
  testSha256:hash(await readFile(fileURLToPath(import.meta.url))), harnessReceiptSha256:hash(await readFile(join(here,'harness-receipt.json'))),
  scope:'Policy unit tests, syntax, patch applicability, and ordinary facade regression tests only. No active test file changed; no compiled or HTTP test of the staged migration has run.',
  importRelocation:'Exact helper body redirects only module-selection import to the existing selector; exact source regression body redirects three imports to preserved actual source versions/reference kernel.'};
await writeFile(join(here, 'harness-host-results.json'), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({cases:cases.length, rejected:cases.filter(c=>c.rejected).length, syntaxCheckedFiles:receipt.changes.length, patchApplyCheck:true, installed:false, hostOnly:true}));
