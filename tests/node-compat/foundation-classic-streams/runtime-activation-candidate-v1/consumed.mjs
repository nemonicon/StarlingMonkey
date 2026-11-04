// Host-side source/tool integrity only; no package, codec or guest imports.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, readFile, readdir, readlink, realpath } from 'node:fs/promises';
import { isAbsolute, join, relative, resolve, sep } from 'node:path';

const hash = data => createHash('sha256').update(data).digest('hex');
const SHA = /^[0-9a-f]{64}$/;
const within = (root, path) => {
  const name = relative(root, path);
  return name === '' || (name !== '..' && !name.startsWith('..' + sep) && !isAbsolute(name));
};
async function ordinary(path, expected, bytes) {
  const stat = await lstat(path);
  assert(stat.isFile() && !stat.isSymbolicLink(), path);
  const data = await readFile(path);
  assert.equal(hash(data), expected, path);
  assert.equal(data.length, bytes, path);
  return data;
}
async function noLinks(root, path) {
  assert(within(root, path) && root !== path);
  const boundary = await lstat(root);
  assert(boundary.isDirectory() && !boundary.isSymbolicLink(), root);
  let cursor = path;
  while (cursor !== root) {
    assert(!(await lstat(cursor)).isSymbolicLink(), cursor);
    cursor = resolve(cursor, '..');
  }
}
async function tree(root) {
  const stat = await lstat(root);
  assert(stat.isDirectory() && !stat.isSymbolicLink(), root);
  const rows = [];
  async function visit(path) {
    for (const name of (await readdir(path)).sort()) {
      const current = join(path, name), info = await lstat(current);
      const kind = info.isSymbolicLink() ? 'symlink' : info.isDirectory() ? 'directory' : info.isFile() ? 'file' : null;
      assert(kind, 'Unexpected special file in sealed tool root');
      rows.push({path:relative(root, current), kind});
      if (kind === 'directory') await visit(current);
    }
  }
  await visit(root);
  return rows.sort((a,b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
}

export async function verifyConsumedSeal(here, expectedManifestSha, replacements, { invocation = true } = {}) {
  assert(SHA.test(expectedManifestSha));
  const raw = await readFile(join(here, 'input-freeze.json'));
  // Hash these exact bytes before parsing or following any row.
  assert.equal(hash(raw), expectedManifestSha, 'Consumed-input manifest changed');
  const document = JSON.parse(raw);
  assert.equal(document.schemaVersion, 1);
  const seen = new Set(); let templateBytes;
  for (const row of document.inputs) {
    assert(typeof row.path === 'string' && !row.path.includes('\0'));
    assert(SHA.test(row.sha256) && Number.isSafeInteger(row.bytes) && row.bytes >= 0);
    const path = resolve(here, row.path);
    assert(!seen.has(path), 'Duplicate consumed path'); seen.add(path);
    if (row.boundary !== undefined) await noLinks(resolve(here, row.boundary), path);
    const data = await ordinary(path, row.sha256, row.bytes);
    if (path === join(here, 'runtime-preflight.template.mjs')) templateBytes = data;
  }
  const roots = document.toolTrees.map(row => row.path), canonicalRoots = document.toolTrees.map(row => row.realPath);
  for (const row of document.toolTrees) {
    assert.equal(await realpath(row.path), row.realPath);
    assert.deepEqual(await tree(row.path), row.entries, 'Tool-root membership changed: ' + row.path);
  }
  for (const row of document.toolLinks) {
    assert(roots.some(root => within(root, row.path)));
    assert((await lstat(row.path)).isSymbolicLink());
    assert.equal(await readlink(row.path), row.linkText);
    assert.equal(await realpath(row.path), row.resolvedTarget);
    assert(canonicalRoots.some(root => within(root, row.resolvedTarget)), 'Link escapes selected tool roots');
    const target = await lstat(row.resolvedTarget);
    assert.equal(target.isDirectory() ? 'directory' : target.isFile() ? 'file' : null, row.targetKind);
    if (row.targetKind === 'file') await ordinary(row.resolvedTarget, row.targetSha256, row.targetBytes);
  }
  if (invocation) {
    const env = document.invocation;
    assert.equal(await realpath(process.execPath), env.nodeRealPath, 'Use the selected Node binary');
    assert.equal(resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/toolchain'), env.toolchainRoot);
    assert.equal(resolve(process.env.NODE_COMPAT_COMPONENTIZE_MODULE ?? ''), env.componentizeModule);
    if (process.env.NODE_COMPAT_WASMTIME) assert.equal(await realpath(process.env.NODE_COMPAT_WASMTIME), env.wasmtimeRealPath);
    for (const key of Object.keys(process.env)) assert(!key.startsWith('NAPI_RS_'), 'Native binding overrides are not admitted');
    for (const key of ['NODE_PATH', 'NODE_OPTIONS', 'NODE_COMPAT_LEGACY_COMPONENTIZER']) assert(!process.env[key], key + ' is not admitted');
  }
  if (replacements) {
    const templatePath = join(here, 'runtime-preflight.template.mjs');
    assert(seen.has(templatePath));
    assert(templateBytes);
    let expected = templateBytes.toString();
    for (const [key, value] of Object.entries(replacements)) expected = expected.replaceAll('@' + key + '@', value);
    const compiled = await readFile(join(here, 'runtime-preflight.mjs'));
    assert.equal(hash(compiled), hash(expected), 'Compiled preflight differs from its sealed template');
  }
  return document.inputs.length;
}

