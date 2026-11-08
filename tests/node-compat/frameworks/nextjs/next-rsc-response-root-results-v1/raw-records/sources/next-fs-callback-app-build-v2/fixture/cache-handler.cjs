'use strict';

// Optional, unexecuted Source prototype. Nothing below reads files or draws
// entropy at module evaluation. Next must instantiate it in the runtime phase.
const { lstatSync, readFileSync, writeFileSync, mkdirSync, renameSync,
  readdirSync, realpathSync } = require('node:fs');
const { createHash, randomBytes } = require('node:crypto');
const { Buffer } = require('node:buffer');
const path = require('node:path').posix;

const PROFILE = Object.freeze({
  namespace: 'portable-fetch-v2', slots: 64, associations: 64,
  recordBytes: 65536, valueBytes: 32768, epochBytes: 2048,
  // Read epochs include exact legacy/new primary and ordinary API soft tags.
  primaryTags: Object.freeze(['next-runtime-fixture-v1', 'portable-fetch-v1']),
  tags: Object.freeze(['next-runtime-fixture-v1', 'portable-fetch-v1',
    '_N_T_/layout', '_N_T_/api/layout', '_N_T_/api/cache/layout',
    '_N_T_/api/cache/route', '_N_T_/api/cache', '_N_T_/api/portable-cache/layout',
    '_N_T_/api/portable-cache/route', '_N_T_/api/portable-cache']),
});
const ROUTES = Object.freeze(['APP_PAGE', 'APP_ROUTE', 'PAGES']);
const own = Object.getOwnPropertyDescriptor;
const hex = (v) => typeof v === 'string' && v.length === 64 && /^[0-9a-f]{64}$/.test(v);
const same = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
function error(code, operation, message, cause) {
  const e = new Error(message);
  e.code = code; e.operation = operation; e.module = 'next-portable-cache-handler-v2';
  if (arguments.length === 4) e.cause = cause;
  return e;
}
function need(ok, code, operation, message) { if (!ok) throw error(code, operation, message); }
function field(o, k, operation) {
  need(o !== null && typeof o === 'object', 'ERR_SM_CACHE_PROFILE', operation, 'Expected context object');
  const d = own(o, k);
  need(d === undefined || Object.hasOwn(d, 'value'), 'ERR_SM_CACHE_PROFILE', operation, 'Context accessor is unsupported');
  return d === undefined ? undefined : d.value;
}
function exact(o, keys, operation) {
  need(o !== null && typeof o === 'object' && !Array.isArray(o), 'ERR_SM_CACHE_CORRUPT', operation, 'Expected record');
  need(same(Reflect.ownKeys(o).sort(), [...keys].sort()), 'ERR_SM_CACHE_CORRUPT', operation, 'Unexpected record fields');
}
function cloneJSON(value, depth = 0, budget = { nodes: 0 }) {
  need(++budget.nodes <= 1024 && depth <= 8, 'ERR_SM_CACHE_LIMIT', 'json', 'JSON structural bound exceeded');
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'number') {
    need(Number.isFinite(value), 'ERR_SM_CACHE_PROFILE', 'json', 'Non-finite JSON number');
    return value;
  }
  need(value !== null && typeof value === 'object', 'ERR_SM_CACHE_PROFILE', 'json', 'Non-JSON value');
  const proto = Object.getPrototypeOf(value), array = Array.isArray(value);
  need(array || proto === Object.prototype || proto === null, 'ERR_SM_CACHE_PROFILE', 'json', 'Non-plain JSON object');
  const names = Reflect.ownKeys(value);
  need(names.every((k) => typeof k === 'string'), 'ERR_SM_CACHE_PROFILE', 'json', 'Symbol key');
  if (array) {
    need(value.length <= 128 && names.length === value.length + 1, 'ERR_SM_CACHE_LIMIT', 'json', 'Sparse or extended array');
    const out = [];
    for (let i = 0; i < value.length; i++) {
      const d = own(value, String(i));
      need(d && Object.hasOwn(d, 'value') && d.enumerable, 'ERR_SM_CACHE_PROFILE', 'json', 'Array accessor or hole');
      out.push(cloneJSON(d.value, depth + 1, budget));
    }
    return out;
  }
  need(names.length <= 64, 'ERR_SM_CACHE_LIMIT', 'json', 'Too many object fields');
  const out = Object.create(null);
  for (const k of names) {
    const d = own(value, k);
    need(k.length <= 256 && Object.hasOwn(d, 'value') && d.enumerable,
      'ERR_SM_CACHE_PROFILE', 'json', 'Object accessor, hidden or oversized key');
    out[k] = cloneJSON(d.value, depth + 1, budget);
  }
  return out;
}
function tags(value, operation) {
  if (value === undefined) return [];
  const copy = cloneJSON(value);
  need(Array.isArray(copy) && copy.length <= PROFILE.tags.length, 'ERR_SM_CACHE_PROFILE', operation, 'Expected bounded tag array');
  need(copy.every((t) => typeof t === 'string' && PROFILE.tags.includes(t)),
    'ERR_SM_CACHE_UNSUPPORTED', operation, 'Undeclared tag');
  return [...new Set(copy)].sort();
}
function fetchValue(value) {
  const v = cloneJSON(value);
  exact(v, ['kind', 'data', 'revalidate'], 'value');
  need(v.kind === 'FETCH', 'ERR_SM_CACHE_UNSUPPORTED', 'value', 'Only FETCH values are persisted');
  exact(v.data, ['headers', 'body', 'status', 'url'], 'value.data');
  need(typeof v.data.body === 'string' && typeof v.data.url === 'string' && v.data.url.length <= 2048 &&
    Number.isInteger(v.data.status) && v.data.status >= 100 && v.data.status <= 599,
  'ERR_SM_CACHE_PROFILE', 'value.data', 'Unsupported FETCH data');
  const h = v.data.headers;
  need(h !== null && typeof h === 'object' && !Array.isArray(h) &&
    Object.values(h).every((x) => typeof x === 'string' && x.length <= 1024),
  'ERR_SM_CACHE_PROFILE', 'value.headers', 'Unsupported FETCH headers');
  need(v.revalidate === false || (typeof v.revalidate === 'number' && Number.isFinite(v.revalidate) && v.revalidate >= 0),
    'ERR_SM_CACHE_PROFILE', 'value.revalidate', 'Unsupported revalidation value');
  need(Buffer.byteLength(JSON.stringify(v), 'utf8') <= PROFILE.valueBytes,
    'ERR_SM_CACHE_LIMIT', 'value', 'FETCH value byte bound exceeded');
  return v;
}
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
function encode(payload, cap) {
  const text = JSON.stringify(payload);
  const bytes = Buffer.from(JSON.stringify({ schemaVersion: 1, sha256: sha(text), payload: text }), 'utf8');
  need(bytes.length <= cap, 'ERR_SM_CACHE_LIMIT', 'encode', 'Record byte bound exceeded');
  return bytes;
}
function decode(bytes, operation) {
  let envelope, payload;
  try {
    const text = bytes.toString('utf8');
    need(sha(Buffer.from(text, 'utf8')) === sha(bytes), 'ERR_SM_CACHE_CORRUPT', operation, 'Invalid UTF-8 record');
    envelope = JSON.parse(text);
    exact(envelope, ['schemaVersion', 'sha256', 'payload'], operation);
    need(envelope.schemaVersion === 1 && hex(envelope.sha256) && typeof envelope.payload === 'string' &&
      sha(envelope.payload) === envelope.sha256 && JSON.stringify(envelope) === text,
    'ERR_SM_CACHE_CORRUPT', operation, 'Record envelope or digest mismatch');
    payload = JSON.parse(envelope.payload);
    need(JSON.stringify(payload) === envelope.payload, 'ERR_SM_CACHE_CORRUPT', operation, 'Noncanonical JSON payload');
  } catch (e) {
    if (e && e.module === 'next-portable-cache-handler-v2') throw e;
    throw error('ERR_SM_CACHE_CORRUPT', operation, 'Unreadable JSON record', e);
  }
  return payload;
}

module.exports = class PortableFetchCacheHandler {
  #root; #delegate; #Delegate; #pending = new Map(); #started = false; #writesDisabled = false;
  constructor(ctx) {
    need(field(ctx, 'dev', 'constructor') === false && field(ctx, 'flushToDisk', 'constructor') === true &&
      field(ctx, 'maxMemoryCacheSize', 'constructor') === 0,
    'ERR_SM_CACHE_PROFILE', 'constructor', 'Requires production flushToDisk and real cacheMaxMemorySize:0');
    const dist = field(ctx, 'serverDistDir', 'constructor');
    need(typeof dist === 'string' && dist.length <= 2048 && dist.endsWith('/server') &&
      dist.startsWith('/') && !dist.includes('\0') && path.normalize(dist) === dist,
    'ERR_SM_CACHE_PROFILE', 'constructor', 'Expected canonical absolute serverDistDir');
    this.#root = path.join(path.dirname(dist), 'cache', PROFILE.namespace);
    // Genuine pinned Next class. Route writes/ISR persistence are deferred in
    // this read-only seed profile; FETCH retains the outer flushToDisk:true.
    // Loading this dependency requires the runtime filesystem/module loader.
    const Delegate = require('next/dist/server/lib/incremental-cache/file-system-cache.js').default;
    need(typeof Delegate === 'function' && Delegate.memoryCache === undefined,
      'ERR_SM_CACHE_DELEGATE', 'constructor', 'Existing Next static memory cache is outside this profile');
    this.#delegate = new Delegate({ ...ctx, maxMemoryCacheSize: 0, flushToDisk: false });
    this.#Delegate = Delegate;
  }
  #route(operation, ...args) {
    need(this.#Delegate.memoryCache === undefined, 'ERR_SM_CACHE_DELEGATE', operation, 'Next static memory cache became active');
    return this.#delegate[operation](...args);
  }
  #directory(p) {
    const s = lstatSync(p);
    need(s.isDirectory() && !s.isSymbolicLink() && realpathSync(p) === p,
      'ERR_SM_CACHE_PROFILE', 'directory', 'Expected canonical owned directory');
  }
  #layout() {
    // The parent is an externally owned private writable cache mount. Do not
    // create ancestors or infer its mode/WASI rights from guest Stats.
    try {
      this.#directory(path.dirname(this.#root));
      for (const p of [this.#root, this.#root + '/entries', this.#root + '/epochs']) {
        try { mkdirSync(p); } catch (e) { if (!e || e.code !== 'EEXIST') throw e; }
        this.#directory(p);
      }
      need(readdirSync(this.#root).every((n) => n === 'entries' || n === 'epochs'),
        'ERR_SM_CACHE_CORRUPT', 'layout', 'Unexpected namespace member');
      for (const [dir, count, cap] of [['entries', PROFILE.slots, PROFILE.recordBytes], ['epochs', PROFILE.tags.length, PROFILE.epochBytes]]) {
        const names = readdirSync(this.#root + '/' + dir);
        need(names.length <= count * 2, 'ERR_SM_CACHE_LIMIT', 'layout', 'Namespace file bound exceeded');
        for (const n of names) {
          const m = /^(0|[1-9][0-9]*)\.(json|pending)$/.exec(n);
          need(m && m[0] === n && Number(m[1]) < count, 'ERR_SM_CACHE_CORRUPT', 'layout', 'Unexpected namespace file');
          // A cooperative writer may rename a pending file after readdir.
          let s; try { s = lstatSync(this.#root + '/' + dir + '/' + n); }
          catch (e) { if (m[2] === 'pending' && e && e.code === 'ENOENT') continue; throw e; }
          need(s.isFile() && !s.isSymbolicLink() && s.nlink === 1 && s.size <= cap,
            'ERR_SM_CACHE_CORRUPT', 'layout', 'Unexpected file type, alias or size');
        }
      }
    } catch (e) {
      if (e && e.module === 'next-portable-cache-handler-v2') throw e;
      throw error('ERR_SM_CACHE_IO', 'layout', 'Cache directory operation failed', e);
    }
  }
  #read(p, cap) {
    let s;
    try { s = lstatSync(p); } catch (e) {
      if (e && e.code === 'ENOENT') return null;
      throw error('ERR_SM_CACHE_IO', 'read.stat', 'Cache stat failed', e);
    }
    need(s.isFile() && !s.isSymbolicLink() && s.nlink === 1 && s.size <= cap,
      'ERR_SM_CACHE_CORRUPT', 'read', 'Unexpected record type, alias or size');
    let bytes; try { bytes = readFileSync(p); }
    catch (e) { throw error('ERR_SM_CACHE_IO', 'read', 'Cache read failed after stat', e); }
    need(bytes.length <= cap, 'ERR_SM_CACHE_LIMIT', 'read', 'Record grew beyond bound');
    return decode(bytes, 'read');
  }
  #publish(p, payload, cap) {
    const bytes = encode(payload, cap), pending = p.replace(/\.json$/, '.pending');
    try { writeFileSync(pending, bytes, { flag: 'wx' }); }
    catch (e) { throw error(e && e.code === 'EEXIST' ? 'ERR_SM_CACHE_BUSY' : 'ERR_SM_CACHE_IO',
      'publish.write', 'Exclusive bounded pending file could not be written; no retry or reclamation', e); }
    try { renameSync(pending, p); }
    catch (e) { throw error('ERR_SM_CACHE_IO', 'publish.rename', 'Publication outcome is uncertain; pending files are never reclaimed online', e); }
  }
  #epochs(list) {
    return list.map((tag) => {
      const p = this.#root + '/epochs/' + PROFILE.tags.indexOf(tag) + '.json';
      let record = this.#read(p, PROFILE.epochBytes);
      if (record === null) {
        // Absence creates a fresh epoch, never a reusable static initial token.
        const epoch = randomBytes(32).toString('hex');
        need(hex(epoch), 'ERR_SM_CACHE_PROFILE', 'epoch', 'Random provider returned invalid token');
        this.#publish(p, { schemaVersion: 1, tag, epoch }, PROFILE.epochBytes);
        record = this.#read(p, PROFILE.epochBytes);
      }
      exact(record, ['schemaVersion', 'tag', 'epoch'], 'epoch');
      need(record.schemaVersion === 1 && record.tag === tag && hex(record.epoch), 'ERR_SM_CACHE_CORRUPT', 'epoch', 'Invalid tag epoch');
      return record.epoch;
    });
  }
  #context(key, ctx) {
    need(hex(key), 'ERR_SM_CACHE_PROFILE', 'context', 'Expected actual SHA256 cache key');
    const idx = field(ctx, 'fetchIdx', 'context'), inputTags = field(ctx, 'tags', 'context');
    const explicit = tags(inputTags, 'context');
    need(Number.isSafeInteger(idx) && idx >= 0 && Array.isArray(inputTags) && inputTags.length === 1 &&
      explicit.length === 1 && PROFILE.primaryTags.includes(explicit[0]),
    'ERR_SM_CACHE_PROFILE', 'context', 'Requires actual finite fetchIdx and exactly one declared primary tag');
    return { id: key + ':' + idx, explicit, combined: [...new Set([...explicit,
      ...tags(field(ctx, 'softTags', 'context'), 'context')])].sort() };
  }
  async get(key, ctx) {
    this.#started = true;
    const kind = field(ctx, 'kind', 'get');
    if (ROUTES.includes(kind)) return this.#route('get', key, ctx);
    need(kind === 'FETCH', 'ERR_SM_CACHE_UNSUPPORTED', 'get', 'Unsupported cache kind');
    const c = this.#context(key, ctx);
    this.#layout();
    const before = this.#epochs(c.combined);
    let association = null;
    if (!this.#writesDisabled) {
      if (this.#pending.has(c.id)) this.#pending.get(c.id).poisoned = true;
      else if (this.#pending.size === PROFILE.associations) { this.#writesDisabled = true; this.#pending.clear(); }
      else { association = { ...c, epochs: before, consumed: false, poisoned: false }; this.#pending.set(c.id, association); }
    }
    try {
      const row = this.#read(this.#root + '/entries/' + (parseInt(key.slice(0, 2), 16) % PROFILE.slots) + '.json', PROFILE.recordBytes);
      const after = this.#epochs(c.combined);
      if (row === null) return null;
      exact(row, ['schemaVersion', 'key', 'tags', 'epochs', 'lastModified', 'value'], 'entry');
      const checkedTags = tags(row.tags, 'entry'), value = fetchValue(row.value);
      need(row.schemaVersion === 1 && hex(row.key) && same(row.tags, checkedTags) &&
        Array.isArray(row.epochs) && row.epochs.length === row.tags.length && row.epochs.every(hex) &&
        Number.isSafeInteger(row.lastModified) && row.lastModified >= 0,
      'ERR_SM_CACHE_CORRUPT', 'entry', 'Invalid entry');
      if (row.key !== key || !same(row.tags, c.combined) || !same(before, after) || !same(row.epochs, after)) return null;
      return { lastModified: row.lastModified, value };
    } catch (e) { if (association) association.poisoned = true; throw e; }
  }
  async set(key, value, ctx) {
    this.#started = true;
    if (field(ctx, 'fetchCache', 'set') !== true) {
      need(value === null || (value && ROUTES.includes(value.kind)), 'ERR_SM_CACHE_UNSUPPORTED', 'set', 'Unsupported route value');
      return this.#route('set', key, value, ctx);
    }
    const c = this.#context(key, ctx), a = this.#pending.get(c.id);
    // Retain consumed/poisoned tuples. Reusing a request-local index never turns
    // an old delayed set into a new authenticated computation.
    if (this.#writesDisabled || !a || a.consumed || a.poisoned || !same(a.explicit, c.explicit)) return;
    a.consumed = true;
    const checked = fetchValue(value);
    this.#layout();
    if (!same(this.#epochs(a.combined), a.epochs)) return;
    this.#publish(this.#root + '/entries/' + (parseInt(key.slice(0, 2), 16) % PROFILE.slots) + '.json',
      { schemaVersion: 1, key, tags: a.combined, epochs: a.epochs, lastModified: Date.now(), value: checked }, PROFILE.recordBytes);
  }
  async revalidateTag(input, durations) {
    const list = tags(typeof input === 'string' ? [input] : input, 'revalidateTag');
    // Read-epoch tags do not grant route/path invalidation. Validate the whole
    // batch before changing local state or performing FS, entropy or delegation.
    need(list.every((tag) => PROFILE.primaryTags.includes(tag)),
      'ERR_SM_CACHE_UNSUPPORTED', 'revalidateTag', 'Implicit/path tag invalidation is outside this FETCH profile');
    need(durations === undefined || (durations !== null && typeof durations === 'object' &&
      Reflect.ownKeys(durations).length === 1 && field(durations, 'expire', 'revalidateTag') === 0),
    'ERR_SM_CACHE_UNSUPPORTED', 'revalidateTag', 'Only immediate expiration or expire:0 is supported');
    this.#started = true;
    this.#layout();
    const committedTags = [];
    try {
      for (const tag of list) {
        const epoch = randomBytes(32).toString('hex');
        need(hex(epoch), 'ERR_SM_CACHE_PROFILE', 'revalidateTag', 'Random provider returned invalid token');
        this.#publish(this.#root + '/epochs/' + PROFILE.tags.indexOf(tag) + '.json',
          { schemaVersion: 1, tag, epoch }, PROFILE.epochBytes);
        committedTags.push(tag);
      }
      await this.#route('revalidateTag', list, durations);
    } catch (cause) {
      const e = error('ERR_SM_CACHE_INVALIDATION_PARTIAL', 'revalidateTag', 'Invalidation is not atomic; retained committedTags are only completed publications', cause);
      e.committedTags = committedTags; throw e;
    }
  }
  resetRequestCache() {
    if (this.#started) { this.#writesDisabled = true; this.#pending.clear(); }
    // Next calls its initial reset before any get. That reset does not disable
    // this handler. Later resets cannot make delayed writes safe again.
    return this.#route('resetRequestCache');
  }
};
