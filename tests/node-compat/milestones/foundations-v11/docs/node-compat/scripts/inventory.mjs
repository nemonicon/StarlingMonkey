// Run with EXACT Node v22.14.0. No getters are evaluated during reflection.
import { builtinModules } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { collectDocumentationAPI } from './documentation-inventory.mjs';

if (process.version !== 'v22.14.0') throw new Error(`Expected v22.14.0, got ${process.version}`);
const root = new URL('../', import.meta.url);
const policy = JSON.parse(readFileSync(new URL('policy.json', root)));
const docsBytes = readFileSync(process.argv[2]);
const docsSHA256 = createHash('sha256').update(docsBytes).digest('hex');
if (docsSHA256 !== 'fdbeac15985adfb8b5298d9e3175263900d0d4dbf49c6c80a96dd5724a080301') {
  throw new Error('Node API JSON does not match the pinned release bytes');
}
const docs = JSON.parse(docsBytes);
// These four modules require node: and are omitted from builtinModules in 22.14.0.
const prefixOnly = ['test', 'test/reporters', 'sea', 'sqlite'];
const ids = [...new Set([...builtinModules.map(n => n.replace(/^node:/, '')), ...prefixOnly])].sort();
const rows = [];
// Only documented structured API objects have their members inventoried.
// Runtime data (process.env/argv, loader caches, loaded modules) is not an API
// member inventory and would make output environment-dependent.
const structuredObjects = new Set(['constants', 'types', 'promises', 'webcrypto', 'assert', 'mock', 'snapshot', 'scheduler']);
const inventory = { schema: 1, node: process.version, platform: process.platform,
  arch: process.arch, docsURL: 'https://nodejs.org/download/release/v22.14.0/docs/api/all.json',
  docsSHA256,
  note: 'Runtime export inventory is darwin-arm64 specific. Constants and some exports vary by platform. No reflected getters were invoked.', modules: [], globals: [] };
const kind = d => d.get || d.set ? 'accessor' : typeof d.value;
const keyName = key => typeof key === 'symbol' ? `[${String(key)}]` : key;
function plan(id, api) {
  let p = policy.modules[id] ?? policy.modules[id.split('/')[0]] ?? policy.fallback;
  if (id.startsWith('_')) p = policy.privateModules;
  for (const rule of policy.patternOverrides ?? []) {
    if (new RegExp(rule.module).test(id) && new RegExp(rule.api).test(api)) p = { ...p, ...rule.plan };
  }
  const override = policy.overrides[`${id}:${api}`];
  return { ...p, ...override };
}
function add(id, api, type, origin, detail = '') {
  const p = plan(id, api);
  rows.push({ module: id, api, kind: type, origin, status: p.status,
    implementation: p.implementation, capability: p.capability,
    deviation: p.deviation, validation: p.validation, detail,
    checkoutIntegration: 'not implemented by this deliverable' });
}
for (const id of ids) {
  const ns = await import(`node:${id}`);
  const rec = { specifier: `node:${id}`, aliases: prefixOnly.includes(id) ? [] : [id], exports: [] };
  for (const key of Object.getOwnPropertyNames(ns).sort()) {
    const d = Object.getOwnPropertyDescriptor(ns, key);
    rec.exports.push({ name: key, type: kind(d) });
    add(id, key, kind(d), 'ESM namespace');
    if (key === 'default' || !d.value || !['object', 'function'].includes(typeof d.value)) continue;
    const value = d.value;
    if (typeof value === 'object' && !structuredObjects.has(key)) continue;
    for (const member of Reflect.ownKeys(value)) {
      if (['name', 'length', 'caller', 'arguments', 'prototype'].includes(member)) continue;
      const md = Object.getOwnPropertyDescriptor(value, member);
      add(id, `${key}.${keyName(member)}`, kind(md), 'own static/object descriptor');
    }
    const pd = Object.getOwnPropertyDescriptor(value, 'prototype');
    if (pd?.value && typeof pd.value === 'object') {
      for (const member of Reflect.ownKeys(pd.value)) {
        if (member === 'constructor') continue;
        const md = Object.getOwnPropertyDescriptor(pd.value, member);
        add(id, `${key}.prototype.${keyName(member)}`, kind(md), 'own prototype descriptor');
      }
    }
  }
  inventory.modules.push(rec);
}
for (const name of Object.getOwnPropertyNames(globalThis).sort()) {
  const d = Object.getOwnPropertyDescriptor(globalThis, name);
  inventory.globals.push({ name, type: kind(d), enumerable: d.enumerable, configurable: d.configurable,
    ...('writable' in d ? { writable: d.writable } : {}) });
  add('@globals', name, kind(d), 'global own descriptor');
}
for (const name of ['require', 'module', 'exports', '__dirname', '__filename']) {
  add('@globals', name, 'CommonJS lexical binding', 'Node CommonJS contract', 'These are CommonJS wrapper bindings, not ESM globalThis properties');
}
// Documentation supplements reflection: signatures/overloads, events, options,
// globals, and instance properties that cannot be enumerated on prototypes.
// Retain identifiers/titles only, never the documentation prose.
const supplement = collectDocumentationAPI(docs, { moduleIds: ids, reflectedRows: rows });
for (const { module: id, api: canonical, kind, detail } of supplement.rows) {
    const before = rows.length;
    add(id, canonical, kind, 'Node API documentation', detail);
    // Node documents overloads independently. A supported name does not admit
    // every overload under that name in this deliberately bounded profile.
    if (id === 'buffer' && canonical === 'Buffer.from' && /from\((?:array\)|object)/.test(detail)) {
      Object.assign(rows[before], { status: 'unavailable', implementation: 'Explicit rejection of excluded from overload',
        deviation: 'Arrays and generic object coercion are outside the baseline', validation: 'Excluded overload throws ERR_SM_NODE_UNSUPPORTED' });
    }
}
inventory.documentationExclusions = supplement.excluded;
const csvFields = ['module', 'api', 'kind', 'origin', 'status', 'implementation', 'capability', 'deviation', 'validation', 'detail', 'checkoutIntegration'];
const quote = v => `"${String(v ?? '').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,
  c => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`).replaceAll('"', '""')}"`;
inventory.apiRows = rows.length;
writeFileSync(new URL('node-v22.14.0-exports.json', root), JSON.stringify(inventory, null, 2) + '\n');
writeFileSync(new URL('api-matrix.csv', root), [csvFields.join(','), ...rows.map(r => csvFields.map(k => quote(r[k])).join(','))].join('\n') + '\n');
console.log(JSON.stringify({ node: process.version, modules: inventory.modules.length, apiRows: rows.length,
  docsSHA256: inventory.docsSHA256, outputs: ['node-v22.14.0-exports.json', 'api-matrix.csv'] }));
