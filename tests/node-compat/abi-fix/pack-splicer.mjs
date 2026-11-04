// Isolate a locally rebuilt, pinned ComponentizeJS splicer from the stock npm control.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { cp, mkdir, readFile, writeFile, readdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const profile = process.env.NODE_COMPAT_SPLICER_PROFILE ?? 'import-i32-clock-v2';
assert(['import-i32-v1','import-i32-clock-v2'].includes(profile));
const v2 = profile === 'import-i32-clock-v2';
const work = resolve(process.env.NODE_COMPAT_SPLICER_BUILD_ROOT ?? (v2 ? '/tmp/starling-node-compat/import-abi-clock-v2-build' : '/tmp/starling-node-compat/import-abi-build'));
const source = join(work, 'source');
const pkg = join(work, 'package');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const { directory: toolchain } = await loadToolchain();
const base = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
assert.equal(hash(await readFile(join(base, 'src/componentize.js'))), 'e58ef4f3b126f4a3fd07c61b368930bbf02dd0029f0f03e4c6928528e994e559');
assert.equal(hash(await readFile(join(source, 'Cargo.lock'))), '6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd');
assert.equal(hash(await readFile(join(source, 'crates/spidermonkey-embedding-splicer/src/splice.rs'))), 'f54d9d7562c525131def2a89d512883118d3c7a6af29a1e1021dfec76c31a048');
assert.equal(hash(await readFile(join(source,'crates/spidermonkey-embedding-splicer/src/stub_wasi.rs'))),v2?'a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8':'8443685806c22b2308d33aba2871ab700dea3f9028de7dc475b235df1f2d6992');
await mkdir(join(pkg, 'lib'), { recursive: true });
await mkdir(join(work, 'obj'), { recursive: true });
await cp(join(base, 'src'), join(pkg, 'src'), { recursive: true });
await cp(join(base, 'package.json'), join(pkg, 'package.json'));
await cp(join(base, 'types.d.ts'), join(pkg, 'types.d.ts'));
await cp(join(base, 'lib/interfaces'), join(pkg, 'lib/interfaces'), { recursive: true });
try { await symlink(join(toolchain, 'node_modules'), join(pkg, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const cli = join(toolchain, 'node_modules/@bytecodealliance/jco/dist/jco.js');
const core = join(work, 'target/wasm32-wasip1/release/splicer_component.wasm');
const component = join(work, 'obj/splicer.component.wasm');
const commands = [
  [process.execPath, cli, 'new', core, '-o', component, '--wasi-reactor'],
  [process.execPath, cli, 'transpile', '-q', '--name', 'spidermonkey-embedding-splicer', component, '-o', join(pkg, 'lib'), '--', '-O1'],
];
for (const [command, ...args] of commands) {
  const result = spawnSync(command, args, { encoding: 'utf8', timeout: 180000, maxBuffer: 4 * 1024 * 1024 });
  assert.equal(result.status, 0, result.error?.message || result.stderr || result.stdout);
}
async function filesBelow(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await filesBelow(path));
    else if (entry.isFile()) files.push(path);
  }
  return files;
}
const checkedFiles = [];
for (const file of [...await filesBelow(join(pkg, 'src')), ...await filesBelow(join(pkg, 'lib')), join(pkg, 'package.json')].sort()) {
  checkedFiles.push({ path: relative(pkg, file), sha256: hash(await readFile(file)) });
}
const { splicer } = await import(pathToFileURL(join(pkg, 'lib/spidermonkey-embedding-splicer.js')));
assert.equal(typeof splicer.spliceBindings, 'function');
assert.equal(typeof splicer.stubWasi, 'function');
const sourceVerificationPath = join(work,'source-verification.after.json');
const verification = spawnSync('python3',[join(here,'verify-splicer-source.py'),join(work,'componentize-source.tar.gz'),source,profile,sourceVerificationPath],{encoding:'utf8'});
assert.equal(verification.status,0,verification.stderr);
const beforeVerification = JSON.parse(await readFile(join(work,'source-verification.before.json')));
const afterVerification = JSON.parse(await readFile(sourceVerificationPath));
assert.equal(beforeVerification.treeSha256,afterVerification.treeSha256,'Source changed during Rust compilation/packaging');
const patch = join(here, 'componentize-import-i32-v1.patch');
const rustVersion = spawnSync('rustc', ['+1.96.1', '--version'], { encoding: 'utf8' });
const cargoVersion = spawnSync('cargo', ['+1.96.1', '--version'], { encoding: 'utf8' });
assert.equal(rustVersion.status, 0, rustVersion.stderr); assert.equal(cargoVersion.status, 0, cargoVersion.stderr);
const manifest = {
  schemaVersion: 1, builtAtUtc: new Date().toISOString(), packagingVersion: v2 ? 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1' : 'componentize-js-0.23.0+sm-import-i32.v1',
  baseRevision: '4d812f5a7b524cea5bcfd565cac55f3fab876a57', basePackageVersion: '0.23.0',
  module: 'src/componentize.js', packageDirectory: pkg,
  patch: { id: 'sm-import-i32.v1', path: patch, sha256: hash(await readFile(patch)),
    source: 'crates/spidermonkey-embedding-splicer/src/splice.rs',
    baseSourceSha256: 'abb62bc9580a9f8b8e8026950f6bb285f64373a905ae770718612508dafa301a',
    patchedSourceSha256: hash(await readFile(join(source, 'crates/spidermonkey-embedding-splicer/src/splice.rs'))) },
  lock: { path: join(here, 'splicer-Cargo.v1.lock'), sha256: hash(await readFile(join(source, 'Cargo.lock'))),
    baseSha256: 'c8b5312c03dc69cb3b5747149ea2bf4820b0e8763fc73f6bd60e771a873c09f0',
    repair: 'Only replace the inconsistent js-component-bindgen 2.10.1 local lock entry with the declared published 2.11.0 registry package and its checksum; all other lock entries are unchanged.',
    registryPackage: { name: 'js-component-bindgen', version: '2.11.0', sha256: 'd73b9c04f15dd549239f5302dd6a80be973d055b93c6ad60b7d8d0c9ab07f9b9' } },
  build: { rustc: rustVersion.stdout.trim(), cargo: cargoVersion.stdout.trim(), target: 'wasm32-wasip1', profile: 'release', locked: true,
    corePath: core, coreSha256: hash(await readFile(core)), componentPath: component, componentSha256: hash(await readFile(component)),
    jcoVersion: '1.40.0', commands },
  checkedFiles,
  sourceVerification: {beforePath:join(work,'source-verification.before.json'),afterPath:sourceVerificationPath,treeSha256:afterVerification.treeSha256,archiveSha256:afterVerification.archiveSha256,fileCount:afterVerification.fileCount,beforeAndAfterBuildMatch:true},
  sources: await Promise.all(['Cargo.toml', 'Cargo.lock', 'crates/spidermonkey-embedding-splicer/src/splice.rs', 'crates/spidermonkey-embedding-splicer/src/stub_wasi.rs'].map(async path => ({ path, sha256: hash(await readFile(join(source, path))) }))),
  APIs: ['splicer.spliceBindings', 'splicer.stubWasi'],
  scope: 'Locally rebuilt guest-packaging splicer only. No native guest engine bytes, shared npm package, Wasmtime or wasmCloud host binary is modified. Native engine must still be selected explicitly.',
};
if(v2)manifest.additionalPatches=[{id:'sm-clock-errno.v1',path:join(here,'../oom/componentize-clock-errno-v2.patch'),sha256:'57ace551f7d723cbf9faa41c42eda08feace9370f571175284e36c67d4c24da3',source:'crates/spidermonkey-embedding-splicer/src/stub_wasi.rs',baseSourceSha256:'8443685806c22b2308d33aba2871ab700dea3f9028de7dc475b235df1f2d6992',patchedSourceSha256:'a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8'}];
const manifestPath = join(pkg, 'splicer-build.json');
await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({ componentizeModule: join(pkg, manifest.module), manifestPath, packagingVersion: manifest.packagingVersion, patchSha256: manifest.patch.sha256, coreSha256: manifest.build.coreSha256 }, null, 2));
