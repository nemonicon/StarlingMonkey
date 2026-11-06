// Build-host inventory only. Never copied into the guest.
import {writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
assert.equal(process.version, 'v22.14.0');
const modules = {};
for (const id of ['http', 'https']) {
  const namespace = await import('node:' + id);
  const exports = Object.keys(namespace).sort();
  const types = Object.fromEntries(exports.map(name => [name, typeof namespace[name]]));
  modules['node:' + id] = {exports, types};
}
const http = await import('node:http');
const inventory = {schemaVersion: 1, inventoryVersion: 'next-http-node-v22.14.0-v1',
  node: process.version, modules, METHODS: http.METHODS, STATUS_CODES: http.STATUS_CODES,
  note: 'HTTP protocol constants only; no host sockets, TLS state, handles or environment copied.'};
const bytes = JSON.stringify(inventory, null, 2) + '\n';
writeFileSync(fileURLToPath(new URL('inventory.node-v22.14.0.json', import.meta.url)), bytes);
console.log(JSON.stringify({bytes: Buffer.byteLength(bytes), sha256: createHash('sha256').update(bytes).digest('hex')}));
