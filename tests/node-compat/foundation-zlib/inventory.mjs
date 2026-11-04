import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import * as namespace from 'node:zlib';
import * as bare from 'zlib';

assert.equal(process.version, 'v22.14.0');
assert(!process.env.NODE_OPTIONS, 'Oracle requires an empty NODE_OPTIONS');
const require = createRequire(import.meta.url);
const commonjs = require('node:zlib');
assert.equal(namespace, bare);
assert.equal(namespace.default, commonjs);
const sync = new Set(['deflateSync', 'deflateRawSync', 'gzipSync',
  'inflateSync', 'inflateRawSync', 'gunzipSync']);
const exports = Object.getOwnPropertyNames(namespace).map(name => {
  assert.equal(namespace[name], name === 'default' ? commonjs : commonjs[name]);
  return { name, type: typeof namespace[name], status: 'deferred',
    strategy: sync.has(name) ? 'Bounded native one-shot candidate plus JS validation; no installed binding' :
      name === 'crc32' ? 'Future native bulk CRC32; no binding or executed CRC kernel' :
      name === 'constants' || name === 'codes' ? 'Versioned typed guest data after exact manifest integration' :
      name === 'default' ? 'Ordinary finite CommonJS-style graph, initial named/default identity contract' :
      'Explicit callable deferral until streaming, options or algorithm gate passes',
    capability: 'none; compression must remain in guest',
    validation: sync.has(name) ? 'Owned-byte native/component, Node error/overload, GC, size and throughput gates' :
      'Exact export types/identities; deferred call/new errors until implemented' };
});
assert.equal(exports.length, 40);
const data = object => Object.fromEntries(Object.getOwnPropertyNames(object).map(key => {
  const descriptor = Object.getOwnPropertyDescriptor(object, key);
  assert('value' in descriptor);
  assert(['number', 'string'].includes(typeof descriptor.value));
  return [key, { type: typeof descriptor.value, value: descriptor.value,
    writable: descriptor.writable, enumerable: descriptor.enumerable, configurable: descriptor.configurable }];
}));
const report = { schema: 1, node: process.version,
  nodeRevision: '5d2feb257bcee090e57900eb51720171a6aa92f3', nodeZlib: process.versions.zlib,
  state: 'pinned-node-runtime-inventory-no-profile-support',
  runnerSha256: createHash('sha256').update(readFileSync(fileURLToPath(import.meta.url))).digest('hex'),
  namespaceAliasesIdentical: true, defaultEqualsCommonJS: true,
  exports, constants: data(commonjs.constants), codes: data(commonjs.codes) };
writeFileSync(fileURLToPath(new URL('./inventory.node-v22.14.0.json', import.meta.url)),
  JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ named: exports.length - 1, default: true,
  constants: Object.keys(report.constants).length, codes: Object.keys(report.codes).length }));
