// Public sys/util descriptor and alias inventory. No exported utility function
// is called. Fresh child processes preserve Node's default warning behavior.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const sourcePath = fileURLToPath(import.meta.url), here = dirname(sourcePath);
const hash = value => createHash('sha256').update(value).digest('hex');
const require = createRequire(import.meta.url);
const nodePin = Object.freeze({ release: 'v22.14.0', tagObject: 'ddf66aca0766567c70bf16a92610f03ce0cd2bcd',
  revision: '5d2feb257bcee090e57900eb51720171a6aa92f3' });
assert.equal(process.version, nodePin.release); assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Run the pinned Node release without extra flags');
const flushWarnings = () => new Promise(done => setImmediate(done));

async function inspectCase(kind, firstSpecifier) {
  const warnings = [];
  let phase = 'util imports';
  const listener = warning => warnings.push({ phase, name: warning.name, code: warning.code ?? null, message: warning.message });
  process.on('warning', listener);
  try {
    const util = await import('node:util'), utilAlias = await import('util');
    const cjsUtil = require('node:util');
    await flushWarnings();
    const warningsAfterUtilOnly = [...warnings];
    phase = 'first sys import';
    if (kind === 'esm') await import(firstSpecifier);
    else require(firstSpecifier);
    await flushWarnings();
    const warningsAfterFirstSys = [...warnings];
    phase = 'cached sys imports and aliases';
    const sys = await import('node:sys'), sysAlias = await import('sys');
    const cjsSys = require('node:sys'), cjsSysAlias = require('sys');
    // Repeat the first spelling to distinguish initial load from cached use.
    if (kind === 'esm') await import(firstSpecifier);
    else require(firstSpecifier);
    await flushWarnings();
    const relationships = {
      sysAliasesSameESMNamespace: sys === sysAlias,
      utilAliasesSameESMNamespace: util === utilAlias,
      sysNamespaceSameAsUtilNamespace: sys === util,
      sysDefaultSameAsUtilDefault: sys.default === util.default,
      sysCommonJSSameAsUtilCommonJS: cjsSys === cjsUtil,
      sysCommonJSAliasesSameObject: cjsSys === cjsSysAlias,
      sysDefaultSameAsSysCommonJS: sys.default === cjsSys,
      sysNamespaceNamedValuesSameAsUtil: Object.getOwnPropertyNames(sys).every(name =>
        Object.getOwnPropertyDescriptor(sys, name).value === Object.getOwnPropertyDescriptor(util, name)?.value),
      sysAndUtilExportNameListsSame: JSON.stringify(Object.getOwnPropertyNames(sys)) === JSON.stringify(Object.getOwnPropertyNames(util)),
    };
    assert.equal(relationships.sysNamespaceSameAsUtilNamespace, false);
    for (const [name, value] of Object.entries(relationships)) if (name !== 'sysNamespaceSameAsUtilNamespace') assert.equal(value, true, name);
    function primitive(value) {
      if (typeof value === 'symbol') return { type: 'symbol', description: value.description ?? null, registryKey: Symbol.keyFor(value) ?? null };
      if (value === null || !['object', 'function'].includes(typeof value)) return { type: typeof value, ...(value === undefined ? {} : { value }) };
      if (typeof value === 'function') {
        const d = Object.getOwnPropertyDescriptors(value);
        return { type: 'function', name: d.name?.value ?? null, length: d.length?.value ?? null,
          ownsPrototype: Object.hasOwn(d, 'prototype') };
      }
      return { type: 'object', array: Array.isArray(value), nullPrototype: Object.getPrototypeOf(value) === null };
    }
    function descriptor(object, key) {
      const d = Object.getOwnPropertyDescriptor(object, key);
      const row = { key: typeof key === 'symbol' ? primitive(key) : key,
        enumerable: d.enumerable, configurable: d.configurable };
      if ('value' in d) return { ...row, writable: d.writable, value: primitive(d.value) };
      return { ...row, kind: 'accessor', get: d.get ? primitive(d.get) : null,
        set: d.set ? primitive(d.set) : null, valueNotRead: true };
    }
    const report = { firstImport: { kind, specifier: firstSpecifier }, relationships,
      exportNames: Object.getOwnPropertyNames(sys), exportCount: Object.getOwnPropertyNames(sys).length,
      namespaceDescriptors: Reflect.ownKeys(sys).map(key => descriptor(sys, key)),
      defaultObjectDescriptors: Reflect.ownKeys(cjsSys).map(key => descriptor(cjsSys, key)),
      sameDataPropertyDescriptorsAsUtil: Reflect.ownKeys(cjsSys).every(key => {
        const a = Object.getOwnPropertyDescriptor(cjsSys, key), b = Object.getOwnPropertyDescriptor(cjsUtil, key);
        return a.enumerable === b.enumerable && a.configurable === b.configurable && a.writable === b.writable &&
          a.value === b.value && a.get === b.get && a.set === b.set;
      }),
      warningsAfterUtilOnly, warningsAfterFirstSys, warningsAfterCachedAliases: [...warnings],
      utilityExportsInvoked: false, accessorsInvokedByInspector: false };
    assert.equal(report.sameDataPropertyDescriptorsAsUtil, true);
    assert.deepEqual(warningsAfterUtilOnly, []);
    assert.deepEqual(warningsAfterFirstSys, [{ phase: 'first sys import', name: 'DeprecationWarning',
      code: 'DEP0025', message: 'sys is deprecated. Use util instead.' }]);
    assert.deepEqual(warnings, warningsAfterFirstSys);
    return report;
  } finally { process.off('warning', listener); }
}

if (process.argv[2] === '--case') {
  const kind = process.argv[3], specifier = process.argv[4];
  assert(['esm', 'commonjs'].includes(kind)); assert(['node:sys', 'sys'].includes(specifier));
  console.log(JSON.stringify(await inspectCase(kind, specifier)));
} else {
  const cases = [];
  for (const kind of ['esm', 'commonjs']) for (const specifier of ['node:sys', 'sys']) {
    const result = spawnSync(process.execPath, [sourcePath, '--case', kind, specifier], {
      encoding: 'utf8', env: process.env, timeout: 30000, maxBuffer: 1024 * 1024,
    });
    assert.equal(result.status, 0, result.error?.message ?? result.stderr);
    const observed = JSON.parse(result.stdout);
    assert(result.stderr.includes('[DEP0025] DeprecationWarning: sys is deprecated. Use util instead.'),
      'Default warning printer must remain active');
    cases.push({ ...observed, defaultStderrObserved: true,
      stderrWithPidNormalized: result.stderr.replace(/\(node:\d+\)/g, '(node:<PID>)') });
  }
  const previousUtil = JSON.parse(await readFile(join(here, 'node-inventory.json')));
  assert.equal(previousUtil.node, nodePin.release);
  assert.deepEqual(cases[0].exportNames, previousUtil.modules.find(module => module.id === 'node:util').exports);
  const report = { schemaVersion: 1, state: 'verified-public-sys-util-bindings-and-natural-import-warnings',
    recordedAtUtc: new Date().toISOString(), node: process.version, executable: process.execPath,
    executableSha256: hash(await readFile(process.execPath)), runnerSha256: hash(await readFile(sourcePath)),
    nodePin, execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
    utilInventorySha256: hash(await readFile(join(here, 'node-inventory.json'))), cases,
    scope: 'Four fresh exact-Node processes inspect public ESM/CommonJS bindings only, with either sys spelling imported first. Node default warning printer remains active; a listener captures its natural warning event. No utility export is invoked, warning emitter replaced, flag changed, or private binding accessed.',
    limitations: ['The first-load warning is observed with util already imported; this is not a claim about every application import order.',
      'Named/default descriptor and identity observations apply at module initialization; mutation/syncBuiltinESMExports behavior is not exercised.',
      'Function metadata is not invocation or constructibility conformance.'] };
  await writeFile(join(here, 'sys-inventory.json'), JSON.stringify(report, null, 2) + '\n');
  const sourceRoot = resolve(process.env.NODE_COMPAT_UTIL_NODE_SOURCE ?? '/tmp/starling-node-compat/foundation-util/node-v22.14.0-source');
  const files = [];
  for (const path of ['lib/sys.js', 'test/parallel/test-sys.js']) {
    const url = `https://raw.githubusercontent.com/nodejs/node/${nodePin.revision}/${path}`;
    const response = await fetch(url); assert(response.ok, `${response.status}: ${url}`);
    const bytes = new Uint8Array(await response.arrayBuffer()), localPath = join(sourceRoot, path);
    await mkdir(dirname(localPath), { recursive: true }); await writeFile(localPath, bytes);
    files.push({ path, url, localPath, bytes: bytes.length, sha256: hash(bytes) });
  }
  const sourceReport = { schemaVersion: 1, state: 'official-pinned-sys-source-selected-ledger',
    recordedAtUtc: new Date().toISOString(), nodePin, runnerSha256: hash(await readFile(sourcePath)),
    files, utilSourceInventorySha256: hash(await readFile(join(here, 'node-source-inventory.json'))),
    sourceObservations: [
      { path: 'lib/sys.js', line: 29, kind: 'CommonJS forwarding', target: 'util' },
      { path: 'lib/sys.js', line: 30, kind: 'module initialization warning', name: 'DeprecationWarning', code: 'DEP0025',
        message: 'sys is deprecated. Use util instead.' },
      { path: 'test/parallel/test-sys.js', line: 28, kind: 'official identity assertion', assertion: 'require(sys) is strictly identical to require(util)' },
    ], scope: 'Official sys shim and existing identity test downloaded at the same immutable Node commit. Test source inspected, not executed; runtime findings come only from the public imports/reflection receipt.' };
  await writeFile(join(here, 'sys-source-inventory.json'), JSON.stringify(sourceReport, null, 2) + '\n');
  console.log(JSON.stringify({ node: process.version, cases: cases.length, exports: cases[0].exportCount,
    sysNamespaceSameAsUtilNamespace: cases[0].relationships.sysNamespaceSameAsUtilNamespace,
    defaultAndCommonJSSameAsUtil: cases[0].relationships.sysDefaultSameAsUtilDefault,
    naturalWarningsPerFreshCase: cases.map(item => item.warningsAfterCachedAliases.length), sourceFiles: files.length }, null, 2));
}
