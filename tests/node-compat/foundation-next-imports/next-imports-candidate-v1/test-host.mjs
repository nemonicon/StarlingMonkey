import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInThisContext} from 'node:vm';
import {createNextImportFacades} from './imports-core.mjs';
import {validateManifest} from '../../../../builtins/node-compat/validate-manifest.mjs';
assert.equal(process.version, 'v22.14.0');
const read = n => readFileSync(new URL(n, import.meta.url), 'utf8');
const inventory = JSON.parse(read('inventory.node-v22.14.0.json'));
const source = read('next-imports-factory.generated.h').split('R"SM_IMPORTS(')[1].split(')SM_IMPORTS"')[0];
const graphs = [createNextImportFacades(inventory), runInThisContext(source)()];
let checks = 0;
const schema = JSON.parse(readFileSync(new URL('../../../../builtins/node-compat/manifest.schema.json', import.meta.url), 'utf8'));
validateManifest(JSON.parse(read('export-manifest.next-imports.node-v22.14.0.json')), schema); checks++;
for (const graph of graphs) for (const [id, rows] of Object.entries(inventory.modules)) {
  const real = await import(id), record = graph[id];
  assert.deepEqual(Object.keys(record).sort(), Object.keys(real).sort()); checks++;
  assert.equal(record.then, undefined); assert.equal(record.default.then, undefined); checks += 2;
  assert.doesNotThrow(() => { Object.entries(record); Object.getOwnPropertyDescriptors(record); JSON.stringify(record); }); checks++;
  for (const [name, row] of Object.entries(rows)) {
    assert.equal(record[name], record.default[name]); checks++;
    if (row.type === 'function' && !(id === 'node:tty' && name === 'isatty') && !(id === 'node:inspector' && name === 'url')) {
      for (const mode of ['call', 'new']) {
        assert.throws(() => mode === 'call' ? record[name]() : new record[name](), {code: 'ERR_SM_NODE_UNSUPPORTED', module: id, operation: name}); checks++;
      }
    }
    if (['string','number','boolean'].includes(row.type)) { assert.equal(record[name], real[name]); checks++; }
  }
  await Promise.resolve(record); checks++;
}
assert.equal(graphs[0]['node:tty'].isatty(1), false); checks++;
assert.equal(graphs[0]['node:inspector'].url(), undefined); checks++;
// An actual top-level call is still a failure; there is no initialization escape.
assert.throws(() => Function('module', 'module.getHeapStatistics()')(graphs[0]['node:v8'].default), {code: 'ERR_SM_NODE_UNSUPPORTED'}); checks++;
console.log(JSON.stringify({passed: true, checks, canonicalAndGenerated: true, guestExecuted: false}));
