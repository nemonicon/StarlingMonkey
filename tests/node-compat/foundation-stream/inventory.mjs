// Source/reflection inventory only. Installs no module and creates no streams.
import assert from 'node:assert/strict';
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import * as consumers from 'node:stream/consumers';
import { promisify } from 'node:util';
import { createHash } from 'node:crypto';
import { writeFile } from 'node:fs/promises';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
function keyName(key) { return typeof key === 'symbol' ? { symbol: key.description, registryKey: Symbol.keyFor(key) } : { name: key }; }
function members(value) {
  return Reflect.ownKeys(value).map(key => {
    const d = Object.getOwnPropertyDescriptor(value, key);
    return { ...keyName(key), enumerable: d.enumerable, configurable: d.configurable,
      ...(Object.hasOwn(d, 'value') ? { type: typeof d.value, writable: d.writable,
        ...(typeof d.value === 'function' ? { functionName: d.value.name, length: d.value.length } : {}) }
        : { getter: !!d.get, setter: !!d.set }) };
  });
}
const modules = Object.fromEntries([['node:stream', stream], ['node:stream/promises', promises], ['node:stream/consumers', consumers]].map(([id, namespace]) => [id, {
  exports: Object.getOwnPropertyNames(namespace).map(name => ({ name, type: typeof namespace[name],
    ...(typeof namespace[name] === 'function' ? { functionName: namespace[name].name, length: namespace[name].length } : {}) })),
  defaultMembers: members(namespace.default),
  initialDefaultBindings: Object.keys(namespace).filter(name => name !== 'default').map(name => ({ name, same: namespace.default[name] === namespace[name] })),
}]));
const constructors = Object.fromEntries(['Stream', 'Readable', 'Writable', 'Duplex', 'Transform', 'PassThrough'].map(name => [name, {
  static: members(stream[name]), prototype: members(stream[name].prototype),
  parentConstructorName: Object.getPrototypeOf(stream[name])?.name,
  parentPrototypeConstructorName: Object.getPrototypeOf(stream[name].prototype)?.constructor?.name,
}]));
const report = { schema: 1, node: process.version, platform: process.platform, arch: process.arch,
  modules, constructors, graph: { defaultIsStream: stream.default === stream.Stream,
    streamSelf: stream.default.Stream === stream.default, promisesObject: stream.promises === promises.default,
    callbackPipelinePromisify: stream.pipeline[promisify.custom] === promises.pipeline,
    callbackFinishedPromisify: stream.finished[promisify.custom] === promises.finished },
  defaultHighWaterMark: { byteMode: stream.getDefaultHighWaterMark(false), objectMode: stream.getDefaultHighWaterMark(true), scope: 'Pinned Node on this recorded host platform; not guest OS introspection' },
  embeddedSourceSha256: Object.fromEntries(['stream', 'stream/promises', 'stream/consumers', 'internal/streams/state', 'internal/process/task_queues'].map(name => [name, hash(process.binding('natives')[name])])),
  scope: 'Actual pinned Node reflection only. No StarlingMonkey node:stream installation or compatibility claim.' };
await writeFile(new URL('inventory.node-v22.14.0.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ exportCounts: Object.fromEntries(Object.entries(modules).map(([id, module]) => [id, module.exports.length])), graph: report.graph, highWaterMark: report.defaultHighWaterMark }));
