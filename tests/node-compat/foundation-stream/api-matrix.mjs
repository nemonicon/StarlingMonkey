// Derived from exact pinned inventory; rows are planning status, not support.
import { readFile, writeFile } from 'node:fs/promises';
const inventory = JSON.parse(await readFile(new URL('inventory.node-v22.14.0.json', import.meta.url)));
const rows = [];
function strategy(module, api) {
  if (module.endsWith('/consumers')) return 'Small audited async facade over native Blob/TextDecoder/Buffer after ownership and iterable/cancellation parity gates';
  if (/fromWeb|toWeb/.test(api)) return 'Explicit native Web/classic adapter; validate brands, locks, ownership, cancellation and backpressure';
  if (/pipeline|finished|compose|Abort|asyncIterator|iterator|asyncDispose/.test(api)) return 'Audited JS lifecycle facade; private nextTick/Promise/ALS resources and abort/error sequencing first';
  if (module.endsWith('/promises')) return 'Promise facade sharing root callback implementation and exact default/promisify graph';
  if (/isArrayBufferView|isUint8Array|uint8ArrayToBuffer/.test(api)) return 'Native typed-array predicates and shared Buffer ArrayBuffer views within bounded backing policy';
  return 'Pinned semantic JS core/facade; reuse native byte storage/codecs only where Node observations match';
}
function add(module, api, kind) {
  rows.push({ module, api, kind, status: 'deferred', installed: false,
    implementationStrategy: strategy(module, api), requiredHostInterfaces: [],
    capabilityBoundary: 'Pure in-memory operations need no host capability; concrete filesystem/HTTP/socket/timer resources require separately selected standard interfaces',
    deviations: 'No production Node stream registration; finite subset, caps, unsupported operations, scheduler and resource policies remain to be selected',
    validation: 'Pinned Node differential plus actual native component aliases/ESM/CJS, callback order/error/cancel/snapshot/ALS and target-host gates; successful package import is insufficient' });
}
for (const [module, record] of Object.entries(inventory.modules)) for (const item of record.exports) add(module, item.name, 'module export '+item.type);
for (const [name, record] of Object.entries(inventory.constructors)) for (const where of ['static', 'prototype']) for (const member of record[where]) {
  if (['name', 'length', 'prototype', 'constructor'].includes(member.name)) continue;
  if (member.type !== 'function' && !member.getter && !member.setter) continue;
  add('node:stream', `${name}${where === 'prototype' ? '.prototype' : ''}.${member.name ?? '['+member.symbol+']'}`, member.type === 'function' ? 'method' : 'accessor');
}
const result = { schema: 1, node: inventory.node, installed: false, rows,
  exclusions: ['node:stream/iter is not admitted by the pinned22 inventory', 'stream/consumers.bytes is not a pinned22 export', 'node:stream/web is a separately owned audit, not implied by this matrix'],
  scope: 'Exact pinned names with engineering proposals. Every row is deferred; no implementation support follows from native web globals or package bundling.' };
await writeFile(new URL('api-matrix.json', import.meta.url), JSON.stringify(result, null, 2)+'\n');
console.log(JSON.stringify({ rows: rows.length, installed: false, allStatus: 'deferred' }));
