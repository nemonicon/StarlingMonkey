// Read-only pinned inventory. This does not load a Node adapter into the guest.
import assert from 'node:assert/strict';
import * as events from 'node:events';
import * as prototype from './prototype.mjs';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const deferred = new Set(['EventEmitterAsyncResource', 'addAbortListener', 'on', 'once']);
const constants = new Set(['captureRejectionSymbol', 'captureRejections', 'errorMonitor', 'usingDomains']);
function inspect(value) {
  const type = typeof value;
  return { type, ...(type === 'function' ? { functionName: value.name, arity: value.length, functionKind: Object.prototype.toString.call(value) } : {}),
    ...(type === 'symbol' ? { description: value.description, registryKey: Symbol.keyFor(value) ?? null } : {}),
    ...(['number', 'boolean', 'string'].includes(type) ? { value } : {}) };
}
function own(object) { return Object.getOwnPropertyNames(object).map(name => { const descriptor = Object.getOwnPropertyDescriptor(object, name); return { name, ...inspect(object[name]), enumerable: descriptor.enumerable, configurable: descriptor.configurable,
  ...(Object.hasOwn(descriptor, 'value') ? { writable: descriptor.writable } : { accessor: true }) }; }); }
const exports = Object.getOwnPropertyNames(events).sort(); assert.deepEqual(Object.getOwnPropertyNames(prototype).sort(), exports);
const inventory = exports.map(name => ({ name, node: inspect(events[name]), prototype: inspect(prototype[name]),
  status: deferred.has(name) ? 'deferred' : constants.has(name) ? 'supported' : 'partial',
  requiredHostInterfaces: [], strategy: deferred.has(name) ? 'Explicit throwing guest JS binding' : 'Audited guest JS semantics; no host service' }));
for (const row of inventory) { assert.equal(row.node.type, row.prototype.type); if (row.node.type === 'function') { assert.equal(row.node.functionName, row.prototype.functionName); assert.equal(row.node.arity, row.prototype.arity); } }
const tc = await loadToolchain();
const sourceFiles = [
  'node_modules/@bytecodealliance/jco/dist/node-builtins/events.js',
  'node_modules/unenv/dist/runtime/node/events.mjs',
  'node_modules/unenv/dist/runtime/node/internal/events/events.mjs',
  'node_modules/events/events.js', 'node_modules/events/tests/modify-in-emit.js', 'node_modules/events/tests/once.js',
  'node_modules/events/tests/remove-all-listeners.js', 'node_modules/events/tests/symbols.js', 'node_modules/events/tests/max-listeners.js',
  'node_modules/readable-stream/lib/internal/streams/readable.js', 'node_modules/readable-stream/lib/internal/streams/writable.js',
  'node_modules/readable-stream/lib/internal/streams/legacy.js', 'node_modules/readable-stream/lib/ours/util.js',
];
const sources = await Promise.all(sourceFiles.map(async path => ({ path, sha256: hash(await readFile(join(tc.directory, path))) })));
for (const path of ['builtins/web/event/event-target.cpp', 'builtins/web/abort/abort-signal.h']) sources.push({ path, sha256: hash(await readFile(join(repository, path))) });
const packages = await Promise.all(['@bytecodealliance/jco', 'unenv', 'events', 'readable-stream'].map(async name => { const value = JSON.parse(await readFile(join(tc.directory, 'node_modules', name, 'package.json'))); return { name, version: value.version }; }));
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: false, nodeEmbeddedSourceSha256: hash(process.binding('natives').events),
  prototypeSha256: hash(await readFile(join(here, 'prototype.mjs'))), inventory,
  commonJS: { nodeDefault: own(events.default), prototypeDefault: own(prototype.default), defaultRelationship: events.default === events.EventEmitter, prototypeDefaultRelationship: prototype.default === prototype.EventEmitter,
    propertyOrderClaimed: false, scope: 'All initial constant/function types and symbol descriptions are preserved. Internal EventTarget storage and complete property descriptors are not claimed.' },
  prototypes: { node: own(events.EventEmitter.prototype), prototype: own(prototype.EventEmitter.prototype) }, packages, inspectedSources: sources,
  scope: 'Pinned Node22 inventory and read-only dependency source hashes; prototype has16 real ESM exports but is not installed. AsyncFunction kind of deferred once is not preserved because the explicit stub must also throw on construction.' };
await writeFile(join(here, 'inventory.node-v22.14.0.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ exports: inventory.length, sources: sources.length, packages, callableNamesAndAritiesMatch: true }));
