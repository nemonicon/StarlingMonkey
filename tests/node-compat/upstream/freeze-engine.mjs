import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

assert(process.env.NODE_COMPAT_ENGINE, 'Set NODE_COMPAT_ENGINE to the custom built engine');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const out = resolve(process.env.NODE_COMPAT_UPSTREAM_FREEZE ?? '/tmp/starling-node-compat/upstream-gate/freeze');
const repository = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const metadata = JSON.parse(await readFile(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
async function preserve(source, destination, expected) {
  const bytes = await readFile(source);
  assert.equal(hash(bytes), expected, `Source changed before freeze: ${source}`);
  let exists = false;
  try { await access(destination); exists = true; } catch {}
  if (exists) assert.equal(hash(await readFile(destination)), expected, `Do not overwrite a different frozen artifact: ${destination}`);
  else { await mkdir(dirname(destination), { recursive: true }); await writeFile(destination, bytes); }
}
for (const entry of metadata.sourceManifest) {
  assert(!entry.path.startsWith('/') && !entry.path.split('/').includes('..'));
  await preserve(join(repository, entry.path), join(out, 'source', entry.path), entry.sha256);
}
await preserve(engine, join(out, 'engine.wasm'), metadata.engineSha256);
const metadataBytes = await readFile(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json');
await mkdir(out, { recursive: true });
await preserve(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json', join(out, 'engine.wasm.build.json'), hash(metadataBytes));
console.log(JSON.stringify({ engine: join(out, 'engine.wasm'), sourceRoot: join(out, 'source'), engineSha256: metadata.engineSha256, sourceFilesVerified: metadata.sourceManifest.length }));
