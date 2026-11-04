import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';
import { Buffer } from 'node:buffer';
import { loadToolchain } from './toolchain.mjs';
import { bundleProfile } from './profile-bundler.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const { rolldown, parseAst } = await loadToolchain();
const id = 'node-compat:bundle-unit';
const result = await bundleProfile({ rolldown, parseAst, input: id, virtualModules: {
  [id]: `import cjs from ${JSON.stringify(join(here, 'fixtures/static-require.cjs'))};
import buffer from 'node:buffer'; import child from 'node:child_process';
export const result = cjs.buffer === buffer && cjs.Buffer === buffer.Buffer && cjs.childProcess === child &&
  cjs.localMarker === 'local Buffer marker' && cjs.moduleMarker === 'local module marker' &&
  cjs.nestedChild({ spawn() {} }) === child;
`,
} });
assert.deepEqual(result.imports.sort(), ['node:buffer', 'node:child_process']);
assert.match(result.code, /from "node:buffer"/);
assert.doesNotMatch(result.code, /reference-kernel|buffer-facade|createBufferModule|hexEncode|hexDecode/);
const module = await import('data:text/javascript;base64,' + Buffer.from(result.code).toString('base64'));
assert.equal(module.result, true, 'Static CommonJS builtin require must receive native ESM default');
for (const [fixture, pattern] of [
  ['dynamic-require.cjs', /Only literal require/],
  ['shadowed-require.cjs', /require may only|Shadowed require/],
  ['inherited-manifest-require.cjs', /CommonJS require is not admitted/],
  ['unadmitted-module.mjs', /not admitted/],
]) {
  await assert.rejects(() => bundleProfile({ rolldown, parseAst, input: join(here, 'fixtures', fixture) }), pattern);
}
await assert.rejects(() => bundleProfile({ rolldown, parseAst, input: 'buffer', virtualModules: { buffer: 'export default {};' } }), /cannot replace a native builtin/);
console.log('PASS finite native builtin resolution, static CommonJS default mapping, dynamic/shadowed require rejection');
