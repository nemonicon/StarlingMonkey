'use strict';

// UNEXECUTED test Source. All cache FS, entropy and Next delegate calls below
// are in-memory fakes. Only this test's own module Source is read from disk.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { createHash } = require('node:crypto');
const source = readFileSync(__dirname + '/cache-handler.cjs', 'utf8');
const key = (n) => n.toString(16).padStart(64, '0');
const context = (idx = 1, extra = {}) => ({ kind: 'FETCH', fetchIdx: idx, tags: ['portable-fetch-v1'], ...extra });
const writeContext = (idx = 1, extra = {}) => ({ fetchCache: true, fetchIdx: idx, tags: ['portable-fetch-v1'], ...extra });
const value = (body) => ({ kind: 'FETCH', data: { headers: {}, body, status: 200, url: '' }, revalidate: 60 });
let checks = 0;
function check(v, message) { assert.ok(v, message); checks++; }
async function refuses(action, code) {
  let caught = false;
  try { await action(); } catch (e) { caught = true; assert.equal(e.code, code); checks++; return e; }
  assert.ok(caught, 'expected ' + code);
}
function fixture() {
  const files = new Map([['/fixture/.next/cache', { dir: true }]]), calls = [];
  let nonce = 0, delegateRequires = 0, beforeRename = null, afterRename = null, afterWrite = null;
  const fail = (code) => { const e = new Error(code); e.code = code; throw e; };
  const fs = {
    lstatSync(p) { calls.push(['stat', p]); const row = files.get(p); if (!row) fail('ENOENT');
      return { size: row.dir ? 0 : row.bytes.length, nlink: 1, isDirectory: () => !!row.dir,
        isFile: () => !row.dir, isSymbolicLink: () => false }; },
    realpathSync(p) { if (!files.has(p)) fail('ENOENT'); return p; },
    readFileSync(p) { calls.push(['read', p]); const row = files.get(p); if (!row) fail('ENOENT'); return Buffer.from(row.bytes); },
    mkdirSync(p) { calls.push(['mkdir', p]); if (files.has(p)) fail('EEXIST'); files.set(p, { dir: true }); },
    readdirSync(p) { const prefix = p + '/'; return [...files.keys()].filter((n) => n.startsWith(prefix) && !n.slice(prefix.length).includes('/')).map((n) => n.slice(prefix.length)); },
    writeFileSync(p, bytes, options) { calls.push(['write', p, options]); assert.equal(options.flag, 'wx');
      assert.equal(Object.hasOwn(options, 'mode'), false); assert.equal(Object.hasOwn(options, 'flush'), false);
      if (files.has(p)) fail('EEXIST'); files.set(p, { bytes: Buffer.from(bytes) }); if (afterWrite) afterWrite(p); },
    renameSync(a, b) { calls.push(['rename', a, b]); if (beforeRename) beforeRename(a, b);
      if (!files.has(a)) fail('ENOENT'); files.set(b, files.get(a)); files.delete(a); if (afterRename) afterRename(a, b); },
  };
  class Delegate {
    constructor(ctx) { this.ctx = ctx; }
    get(...args) { calls.push(['route.get', ...args]); return { delegated: true }; }
    set(...args) { calls.push(['route.set', ...args]); }
    revalidateTag(...args) { calls.push(['route.revalidateTag', ...args]); }
    resetRequestCache() { calls.push(['route.reset']); }
  }
  const requireFake = (name) => {
    if (name === 'node:fs') return fs;
    if (name === 'node:crypto') return { createHash, randomBytes(n) { calls.push(['entropy', n]); return Buffer.from((++nonce).toString(16).padStart(n * 2, '0'), 'hex'); } };
    if (name === 'node:path') return require('node:path');
    if (name === 'node:buffer') return { Buffer };
    if (name === 'next/dist/server/lib/incremental-cache/file-system-cache.js') { delegateRequires++; return { default: Delegate }; }
    throw new Error('Unexpected require ' + name);
  };
  const module = { exports: {} };
  new Function('require', 'module', 'exports', source)(requireFake, module, module.exports);
  check(calls.length === 0 && delegateRequires === 0, 'no module-evaluation FS, entropy or Next import');
  const make = () => new module.exports({ dev: false, flushToDisk: true, maxMemoryCacheSize: 0, serverDistDir: '/fixture/.next/server', fs: {} });
  const root = '/fixture/.next/cache/portable-fetch-v1';
  return { files, calls, make, root, Delegate, Handler: module.exports,
    beforeRename(fn) { beforeRename = fn; }, afterRename(fn) { afterRename = fn; }, afterWrite(fn) { afterWrite = fn; } };
}
async function main() {
  {
    const f = fixture(), a = f.make(); a.resetRequestCache();
    check(await a.get(key(1), context()) === null, 'first miss');
    await a.set(key(1), value('one'), writeContext());
    check((await f.make().get(key(1), context())).value.data.body === 'one', 'fresh instance reads shared bytes');
    const old = f.make(); await old.get(key(1), context(2));
    await f.make().revalidateTag('portable-fetch-v1', { expire: 0 });
    await old.set(key(1), value('stale'), writeContext(2));
    const fresh = f.make(); check(await fresh.get(key(1), context()) === null, 'old epoch rejected after invalidation');
    await fresh.set(key(1), value('two'), writeContext());
    check((await f.make().get(key(1), context())).value.data.body === 'two', 'new computation publishes new epoch');
    const json = f.files.get(f.root + '/entries/0.json'); json.bytes[0] = 33;
    await refuses(() => f.make().get(key(1), context()), 'ERR_SM_CACHE_CORRUPT');
  }
  {
    const f = fixture(), a = f.make(); await a.get(key(2), context());
    let invalidation;
    f.beforeRename((a, b) => { if (b.includes('/entries/')) { f.beforeRename(null); invalidation = f.make().revalidateTag('portable-fetch-v1'); } });
    await a.set(key(2), value('raced'), writeContext()); await invalidation;
    check(await f.make().get(key(2), context()) === null, 'invalidation after set check but before rename rejects stale record');
  }
  {
    const f = fixture(), a = f.make(); await a.get(key(3), context()); await a.set(key(3), value('old'), writeContext());
    f.files.delete(f.root + '/epochs/0.json');
    check(await f.make().get(key(3), context()) === null, 'missing epoch cannot revive an old initial token');
    f.files.set(f.root + '/epochs/0.json', { bytes: Buffer.from('{}') });
    await refuses(() => f.make().get(key(3), context()), 'ERR_SM_CACHE_CORRUPT');
  }
  {
    const f = fixture(), a = f.make(); await a.set(key(4), value('unassociated'), writeContext());
    check(f.calls.length === 0, 'bypassed get does not persist or initialize storage');
    await a.get(key(4), context()); await a.get(key(4), context()); await a.set(key(4), value('ambiguous'), writeContext());
    check(!f.files.has(f.root + '/entries/0.json'), 'repeated tuple poisoned');
    const b = f.make(); await b.get(key(4), context()); b.resetRequestCache(); await b.set(key(4), value('reset'), writeContext());
    check(!f.files.has(f.root + '/entries/0.json'), 'later reset never re-enables delayed writes');
  }
  {
    const f = fixture(), a = f.make();
    for (let i = 0; i < 65; i++) await a.get(key(i), context(i));
    await a.set(key(0), value('overflow'), writeContext(0));
    check(!f.files.has(f.root + '/entries/0.json'), 'overflow disables persistence, not token eviction/reuse');
  }
  {
    const f = fixture(), a = f.make(); await a.get(key(5), context());
    f.afterWrite((p) => { if (p.includes('/entries/')) { f.afterWrite(null); throw 0; } });
    const e = await refuses(() => a.set(key(5), value('partial'), writeContext()), 'ERR_SM_CACHE_IO');
    check(e.cause === 0 && f.files.has(f.root + '/entries/0.pending'), 'falsy failure and uncertain pending preserved');
    const b = f.make(); await b.get(key(5), context());
    await refuses(() => b.set(key(5), value('busy'), writeContext()), 'ERR_SM_CACHE_BUSY');
    check(f.files.has(f.root + '/entries/0.pending'), 'pending is never reclaimed online');
  }
  {
    const f = fixture(), a = f.make(); await a.get(key(6), context());
    f.afterRename((a, b) => { if (b.includes('/entries/')) { f.afterRename(null); throw false; } });
    const e = await refuses(() => a.set(key(6), value('committed'), writeContext()), 'ERR_SM_CACHE_IO');
    check(e.cause === false && (await f.make().get(key(6), context())).value.data.body === 'committed', 'ambiguous committed rename remains an error');
  }
  {
    const f = fixture(), a = f.make(); let accessed = false;
    const ctx = context(); Object.defineProperty(ctx, 'tags', { get() { accessed = true; return []; } });
    await refuses(() => a.get(key(7), ctx), 'ERR_SM_CACHE_PROFILE'); check(!accessed, 'context getter not called');
    await refuses(() => a.get(key(7), context(1, { tags: ['unknown'] })), 'ERR_SM_CACHE_UNSUPPORTED');
    await refuses(() => a.revalidateTag('portable-fetch-v1', { expire: 1 }), 'ERR_SM_CACHE_UNSUPPORTED');
    const v = value('x'); Object.defineProperty(v.data, 'body', { enumerable: true, get() { accessed = true; return 'x'; } });
    await a.get(key(7), context()); await refuses(() => a.set(key(7), v, writeContext()), 'ERR_SM_CACHE_PROFILE');
    check(!accessed, 'value getter not called');
  }
  {
    const f = fixture(), a = f.make(), c = { kind: 'APP_PAGE' }, v = { kind: 'APP_PAGE' };
    check((await a.get('/route', c)).delegated, 'pinned route get delegated');
    await a.set('/route', v, { fetchCache: false });
    check(f.calls.some((x) => x[0] === 'route.get' && x[2] === c) && f.calls.some((x) => x[0] === 'route.set' && x[2] === v), 'route values and contexts are passed unchanged');
    f.Delegate.memoryCache = {};
    await refuses(() => a.get('/route', c), 'ERR_SM_CACHE_DELEGATE');
    assert.throws(() => f.make(), { code: 'ERR_SM_CACHE_DELEGATE' }); checks++;
  }
  {
    const f = fixture();
    for (let i = 0; i < 128; i++) { const a = f.make(), k = (i % 64).toString(16).padStart(2, '0') + key(i).slice(2); await a.get(k, context()); await a.set(k, value(String(i)), writeContext()); }
    const rows = [...f.files].filter(([p, v]) => p.startsWith(f.root + '/') && !v.dir);
    check(rows.length <= 140 && rows.reduce((n, [, v]) => n + v.bytes.length, 0) <= 8413184, 'fixed file and logical-byte bounds');
    check(rows.every(([p]) => /\/(entries|epochs)\/(0|[1-9][0-9]*)\.(json|pending)$/.test(p)), 'no random temporary filename growth');
  }
  console.log(JSON.stringify({ sourceTestsOnly: true, checks, actualCacheFilesystemUsed: false,
    actualEntropyUsed: false, actualNextImported: false, actualHandlerLoadedInGuest: false }));
}
main().catch((e) => { console.error(e); process.exitCode = 1; });
