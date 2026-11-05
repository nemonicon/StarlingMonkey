// Probe the real moduleParsed/getModuleInfo source API; bundle only, no import.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire('/private/tmp/starling-node-compat/toolchain/package.json');
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
const { esmExternalRequirePlugin } = await import(pathToFileURL(require.resolve('rolldown/plugins')));
assert.equal(process.version, 'v22.14.0');
const root = join(HERE, 'virtual-source-evidence'); await mkdir(root);
await writeFile(join(root, 'entry.cjs'), "module.exports=require('node:buffer');\n", { flag: 'wx' });
const modules = [];
const build = await rolldown({ input: join(root, 'entry.cjs'), platform: 'neutral', treeshake: false,
  plugins: [esmExternalRequirePlugin({ external: ['node:buffer'] }), { name: 'retain-real-module-source', moduleParsed(info) {
    const reread = this.getModuleInfo(info.id);
    if (info.id.startsWith('builtin:') || info.id.startsWith('\0')) {
      assert.equal(reread.code, info.code); assert.equal(typeof info.code, 'string');
      modules.push({ id: info.id, code: info.code, sha256: createHash('sha256').update(info.code).digest('hex'), bytes: Buffer.byteLength(info.code), importedIds: info.importedIds });
    }
  } }] });
let result; try { result = await build.generate({ format: 'esm', codeSplitting: false }); } finally { await build.close(); }
assert.equal(result.output.length, 1);
await writeFile(join(root, 'bundle.mjs'), result.output[0].code, { flag: 'wx' });
const output = { schemaVersion: 1, node: process.version, modules, imports: result.output[0].imports, generatedModuleImported: false, guestExecuted: false };
await writeFile(join(root, 'results.json'), JSON.stringify(output, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify(modules.map(x => ({ id: x.id, bytes: x.bytes, sha256: x.sha256, importedIds: x.importedIds })), null, 2) + '\n');
