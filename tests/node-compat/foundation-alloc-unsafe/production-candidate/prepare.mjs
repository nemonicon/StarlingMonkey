// Prepare isolated production candidates only. Never writes repository builtins.
import assert from 'node:assert/strict';
import { cp, mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../../..');
const original = join(repository, 'builtins/node-compat');
const base = join(here, 'base/builtins/node-compat'), candidate = join(here, 'source/builtins/node-compat');
const hash = value => createHash('sha256').update(value).digest('hex');
let baseExists = true;
try { await stat(base); } catch (error) { if (error.code !== 'ENOENT') throw error; baseExists = false; }
if (baseExists && !process.argv.includes('--from-base')) throw new Error('Isolated base already exists; use --from-base to rebuild only the candidate from that preserved base');
if (!baseExists) { await mkdir(dirname(base), { recursive: true }); await cp(original, base, { recursive: true }); }
await mkdir(dirname(candidate), { recursive: true }); await cp(base, candidate, { recursive: true });
const originalManifest = JSON.parse(await readFile(join(base, 'export-manifest.node-v22.14.0.json')));
assert.equal(originalManifest.profileVersion, 'sm-node-22.14.0-m0.1');
let facade = await readFile(join(base, 'buffer-facade.mjs'), 'utf8');
const boundary = '  Buffer.from = function from(value, encodingOrOffset, length) {';
assert.equal(facade.split(boundary).length, 2);
const implementation = `  // m0.8: retain the existing owned, zeroed allocator. Capture before app code.\n`+
`  const unsafeAlloc = Buffer.alloc, unsafeApply = Reflect.apply;\n`+
`  const unsafeTrunc = Math.trunc, unsafeFinite = Number.isFinite;\n`+
`  const UnsafeTypeError = TypeError, UnsafeRangeError = RangeError;\n`+
`  const unsafeDefine = Object.defineProperty;\n`+
`  function unsafeFailure(Ctor, code, message) {\n`+
`    const error = new Ctor(code + ': Buffer.allocUnsafe ' + message);\n`+
`    unsafeDefine(error, 'code', { __proto__: null, value: code, writable: true, enumerable: true, configurable: true });\n`+
`    unsafeDefine(error, 'module', { __proto__: null, value: 'node:buffer', writable: true, enumerable: true, configurable: true });\n`+
`    unsafeDefine(error, 'operation', { __proto__: null, value: 'Buffer.allocUnsafe', writable: true, enumerable: true, configurable: true });\n`+
`    throw error;\n`+
`  }\n`+
`  function allocUnsafe(length) {\n`+
`    if (typeof length !== 'number') unsafeFailure(UnsafeTypeError, 'ERR_INVALID_ARG_TYPE', 'size must be a number');\n`+
`    if (!unsafeFinite(length) || length < 0 || length > MAX_LENGTH)\n`+
`      unsafeFailure(UnsafeRangeError, 'ERR_OUT_OF_RANGE', 'size must be between 0 and ' + MAX_LENGTH);\n`+
`    return unsafeApply(unsafeAlloc, Buffer, [unsafeTrunc(length)]);\n`+
`  }\n`;
facade = facade.replace(boundary, implementation+boundary);
const install = '    Buffer[name] = unavailable(\'node:buffer\', \x60Buffer.\x24{name}\x60);';
assert.equal(facade.split(install).length, 2);
facade = facade.replace(install, '    // Keep constructor property order; promote only this existing slot.\n'+
  '    Buffer[name] = name === \'allocUnsafe\' ? allocUnsafe : unavailable(\'node:buffer\', \x60Buffer.\x24{name}\x60);');
await writeFile(join(candidate, 'buffer-facade.mjs'), facade);
let helper = await readFile(join(base, 'unsupported.mjs'), 'utf8');
assert.equal(helper.split("sm-node-22.14.0-m0.1").length, 2);
helper = helper.replace('sm-node-22.14.0-m0.1', 'sm-node-22.14.0-m0.8');
await writeFile(join(candidate, 'unsupported.mjs'), helper);
const manifest = structuredClone(originalManifest), buffer = manifest.modules['node:buffer'];
manifest.profileVersion = 'sm-node-22.14.0-m0.8';
buffer.supportedStatic.push('allocUnsafe(finite nonnegative number <=16777216): truncate length; fresh zeroed owned Buffer; no pool');
buffer.unsupportedStatic = buffer.unsupportedStatic.filter(name => name !== 'allocUnsafe');
buffer.deviations = buffer.deviations.map(value => value === 'No slab allocator or unsafe allocation' ?
  'No slab allocator or uninitialized storage; allocUnsafe guarantees fresh zeroed exact backing at offset 0 and ignores poolSize' :
  value === 'Fractional sizes/index coercion outside specified overloads unsupported' ?
    'Only allocUnsafe truncates finite nonnegative fractional sizes; other fractional sizes/index coercions remain outside the declared overloads' : value);
buffer.deviations.push('allocUnsafe validates the raw requested size before truncation; requests above 16777216 reject even if their truncated length would fit');
buffer.deviations.push('allocUnsafe uses captured constructors and own data code/module/operation fields for validation; detailed Node error text and pooled backing semantics differ');
buffer.deviations.push('allocUnsafeSlow remains explicitly deferred; no legacy Buffer constructor or other method support follows');
await writeFile(join(candidate, 'export-manifest.node-v22.14.0.json'), JSON.stringify(manifest, null, 2)+'\n');
const generated = spawnSync(process.execPath, [join(candidate, 'generate-factories.mjs')], { encoding: 'utf8' });
assert.equal(generated.status, 0, generated.stderr || generated.stdout);
const checked = spawnSync(process.execPath, [join(candidate, 'generate-factories.mjs'), '--check'], { encoding: 'utf8' });
assert.equal(checked.status, 0, checked.stderr || checked.stdout);
async function files(root) {
  const result = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) result.push(...await files(path)); else result.push(path);
  }
  return result.sort();
}
const changed = [], unchanged = [];
for (const path of await files(base)) {
  const name = relative(base, path), before = hash(await readFile(path)), after = hash(await readFile(join(candidate, name)));
  (before === after ? unchanged : changed).push({ path: 'builtins/node-compat/'+name, before, after });
}
assert.deepEqual(changed.map(item => item.path).sort(), ['buffer-facade.mjs', 'unsupported.mjs', 'export-manifest.node-v22.14.0.json', 'factories.generated.h'].map(name => 'builtins/node-compat/'+name).sort());
let patch = '';
for (const item of changed) {
  const name = item.path.slice('builtins/node-compat/'.length);
  const diff = spawnSync('diff', ['-u', '--label', 'a/'+item.path, join(base, name), '--label', 'b/'+item.path, join(candidate, name)], { encoding: 'utf8' });
  assert.equal(diff.status, 1); patch += diff.stdout;
}
await writeFile(join(here, 'core-m0.8.patch'), patch);
const receipt = { schema: 1, proposalVersion: 'buffer-allocunsafe-zeroed-production-v1', productionInstalled: false,
  baseCoreVersion: originalManifest.profileVersion, candidateCoreVersion: manifest.profileVersion,
  sourceCopy: 'source/builtins/node-compat', baseCopy: 'base/builtins/node-compat', changed, unchanged,
  patchSha256: hash(patch), generatorCheck: checked.stdout.trim(), nativeBufferCppUnchanged: unchanged.some(item => item.path === 'builtins/node-compat/buffer.cpp'),
  scope: 'Isolated source copies/header/patch only; repository builtins and active harnesses are unchanged. No compiled m0.8 engine or genuine OOM claim.' };
await writeFile(join(here, 'source-receipt.json'), JSON.stringify(receipt, null, 2)+'\n');
console.log(JSON.stringify({ changedFiles: changed.map(item => item.path), unchangedFiles: unchanged.length, nativeBufferCppUnchanged: receipt.nativeBufferCppUnchanged, productionInstalled: false }));
