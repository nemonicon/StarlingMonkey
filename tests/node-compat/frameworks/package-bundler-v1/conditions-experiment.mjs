// Probe configured exports conditions without running the generated module.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url)), require = createRequire('/private/tmp/starling-node-compat/toolchain/package.json');
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
assert.equal(process.version, 'v22.14.0');
const root = join(HERE, 'conditions-evidence'); await mkdir(root); const results = [];
for (const [name, conditions] of [['default', null], ['node-only', ['node']], ['production-node', ['production', 'node']]]) {
  const folder = join(root, name), packages = join(folder, 'packages'); await mkdir(join(packages, 'audit-conditions'), { recursive: true });
  const files = { 'package.json': '{"type":"module"}',
    'entry.mjs': "import p from 'audit-conditions';import c from './caller.cjs';export const value={p,c};",
    'caller.cjs': "module.exports=require('audit-conditions');",
    'packages/audit-conditions/package.json': JSON.stringify({ name: 'audit-conditions', exports: { require: './require.cjs', import: './import.mjs', production: './production.mjs', node: './node.mjs', default: './default.mjs' } }),
    'packages/audit-conditions/require.cjs': "module.exports='require-branch';",
    'packages/audit-conditions/import.mjs': "export default 'import-branch';",
    'packages/audit-conditions/production.mjs': "export default 'production-branch';",
    'packages/audit-conditions/node.mjs': "export default 'node-branch';",
    'packages/audit-conditions/default.mjs': "export default 'default-branch';" };
  for (const [path, code] of Object.entries(files)) await writeFile(join(folder, path), code + '\n', { flag: 'wx' });
  const build = await rolldown({ input: join(folder, 'entry.mjs'), platform: 'neutral', treeshake: false, resolve: { modules: [packages], mainFields: ['main', 'module'], ...(conditions ? { conditionNames: conditions } : {}) } });
  let output; try { output = await build.generate({ format: 'esm', codeSplitting: false }); } finally { await build.close(); }
  assert.equal(output.output.length, 1); const chunk = output.output[0]; await writeFile(join(folder, 'bundle.mjs'), chunk.code, { flag: 'wx' });
  results.push({ name, configuredConditions: conditions, modules: Object.keys(chunk.modules), branchesPresent: ['require', 'import', 'production', 'node', 'default'].filter(x => chunk.code.includes(x + '-branch')), generatedModuleImported: false });
}
await writeFile(join(root, 'results.json'), JSON.stringify({ schemaVersion: 1, node: process.version, cases: results, nativeEngineExecuted: false, guestExecuted: false }, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify(results, null, 2) + '\n');
