// Build-host reflection of pinned Node export declarations, not runtime adapters.
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
assert.equal(process.version, 'v22.14.0');
function describe(value, depth = 0) {
  const type = typeof value;
  if (value === null || ['string','number','boolean'].includes(type)) return {type, value};
  if (type === 'undefined') return {type};
  if (type === 'symbol') return {type, globalKey: Symbol.keyFor(value), description: value.description};
  if (type === 'function') return {type, name: value.name, length: value.length};
  assert.equal(type, 'object');
  assert(depth < 4, 'Unexpected deep exported object');
  const properties = {};
  for (const [key, descriptor] of Object.entries(Object.getOwnPropertyDescriptors(value))) {
    if (key === 'then' || key === '__proto__') throw Error('Unexpected namespace key');
    properties[key] = 'value' in descriptor ? describe(descriptor.value, depth + 1) : {type: 'undefined', accessorDeferred: true};
  }
  return {type, properties};
}
const modules = {};
for (const id of ['tty','inspector','v8','dns/promises']) {
  const ns = await import('node:' + id);
  modules['node:' + id] = Object.fromEntries(Object.keys(ns).sort().filter(name => name !== 'default').map(name => [name, describe(ns[name])]));
}
writeFileSync(new URL('inventory.node-v22.14.0.json', import.meta.url), JSON.stringify({schemaVersion: 1,
  inventoryVersion: 'next-imports-node-v22.14.0-v1', node: process.version, modules,
  note: 'Functions become guest throwing bindings. Data constants are a defined profile ABI; no V8/host statistics or live resources copied. Accessors are declared unavailable without invoking them.'}, null, 2) + '\n');
