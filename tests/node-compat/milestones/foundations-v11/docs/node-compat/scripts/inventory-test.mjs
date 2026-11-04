// Regression against the pinned real documentation, not a mirror of the parser.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { collectDocumentationAPI } from './documentation-inventory.mjs';

assert.equal(process.version, 'v22.14.0');
const bytes = readFileSync(process.argv[2]);
assert.equal(createHash('sha256').update(bytes).digest('hex'), 'fdbeac15985adfb8b5298d9e3175263900d0d4dbf49c6c80a96dd5724a080301');
const inventory = JSON.parse(readFileSync(new URL('../node-v22.14.0-exports.json', import.meta.url)));
const moduleIds = inventory.modules.map(m => m.specifier.slice(5));
const reflectedRows = [
  ...inventory.modules.flatMap(m => m.exports.map(e => ({ module: m.specifier.slice(5), api: e.name }))),
  { module: 'buffer', api: 'constants.MAX_LENGTH' },
  { module: 'buffer', api: 'constants.MAX_STRING_LENGTH' },
];
const { rows, excluded } = collectDocumentationAPI(JSON.parse(bytes), { moduleIds, reflectedRows });
function has(module, api) { return rows.some(r => r.module === module && r.api === api); }
assert(has('buffer', 'Blob.prototype.type'));
assert(has('buffer', 'File.prototype.name'));
assert(has('buffer', 'File.prototype.lastModified'));
assert(has('buffer', 'constants.MAX_LENGTH'));
assert(has('buffer', 'constants.MAX_STRING_LENGTH'));
assert(has('async_hooks', 'asyncWrapProviders'));
assert(rows.some(r => r.module === 'events' && r.api.endsWith('.prototype.asyncId')));
assert(rows.some(r => r.module === 'diagnostics_channel' && r.api.endsWith('.prototype.hasSubscribers')));
assert(rows.some(r => r.module === 'stream/web' && r.api === 'TransformStream.prototype.readable'));
assert(!rows.some(r => /(?:^|[./])(?:Type|return)$/.test(r.api)), 'JSON parser headings must not become API members');
assert(excluded.some(r => r.module === 'errors'));
assert(excluded.some(r => r.module === 'n-api'));
assert(!rows.some(r => ![...moduleIds, '@globals'].includes(r.module)));
assert.equal(inventory.modules.length, 72);
console.log(JSON.stringify({ passed: true, node: process.version, moduleNamespaces: 72,
  documentationRows: rows.length, excludedChapterRecords: excluded.length,
  properties: ['Blob.type', 'File.name', 'File.lastModified', 'asyncWrapProviders',
    'EventEmitterAsyncResource.asyncId', 'Channel.hasSubscribers', 'TransformStream.readable'] }));
