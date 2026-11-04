import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export async function loadToolchain() {
  assert.equal(process.version, 'v22.14.0', 'Use the exact Node v22.14.0 oracle');
  const directory = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/toolchain');
  const require = createRequire(join(directory, 'package.json'));
  for (const [name, version] of Object.entries({ '@bytecodealliance/componentize-js': '0.23.0', '@bytecodealliance/jco': '1.40.0', rolldown: '1.2.16' })) {
    const pkg = JSON.parse(await readFile(join(directory, 'node_modules', name, 'package.json')));
    assert.equal(pkg.version, version, `Toolchain version mismatch for ${name}`);
  }
  const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
  const { parseAst } = await import(pathToFileURL(require.resolve('rolldown/parseAst')));
  return { directory, require, rolldown, parseAst };
}
