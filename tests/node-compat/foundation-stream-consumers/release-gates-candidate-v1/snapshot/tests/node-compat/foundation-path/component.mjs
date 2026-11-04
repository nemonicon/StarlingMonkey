import rootDefault, * as root from 'node:path';
import posixDefault, * as posix from 'node:path/posix';
import win32Default, * as win32 from 'node:path/win32';
import corpus from 'node-compat:path-oracles';
import cjs from './static-require.cjs';
function check(condition, message) { if (!condition) throw new Error(message); }
const snapshot = { cwd: root.resolve(), normalized: root.normalize('/a/../b'),
  glob: root.matchesGlob('src/a.ts', '**/*.{js,ts}') };
let calls = 0;
export function run() {
  try {
    check(snapshot.cwd === '/' && snapshot.normalized === '/b' && snapshot.glob, 'pure snapshot Path calls');
    const names = corpus.exportNames;
    for (const namespace of [root, posix, win32]) check(JSON.stringify(Object.keys(namespace).sort()) === JSON.stringify(names), 'exact exports');
    check(rootDefault === root.posix && rootDefault === posixDefault && root.default === rootDefault, 'default POSIX identity');
    check(win32.default === root.win32 && win32Default === root.win32, 'default Win32 identity');
    for (const variant of [rootDefault, win32Default]) {
      check(variant.posix === rootDefault && variant.win32 === win32Default, 'shared variant graph');
      check(variant._makeLong === variant.toNamespacedPath, 'legacy alias identity');
    }
    check(root.basename === rootDefault.basename && posix.basename === root.basename && win32.basename === win32Default.basename,
      'named/default function identities');
    check(cjs.root === rootDefault && cjs.posix === rootDefault && cjs.win32 === win32Default, 'static CommonJS default interop');
    check(typeof root.sep === 'string' && root.sep === '/' && root.delimiter === ':' && win32.sep === '\\' && win32.delimiter === ';', 'constant types');
    for (const vector of corpus.lexical) {
      const result = root[vector.variant][vector.method](...vector.args);
      check(JSON.stringify(result) === JSON.stringify(vector.expected), 'lexical ' + vector.variant + '.' + vector.method);
    }
    for (const vector of corpus.globs) {
      check(root[vector.variant].matchesGlob(vector.path, vector.pattern) === vector.expected, 'glob ' + vector.variant);
    }
    for (const vector of corpus.denied) {
      let caught = false;
      try { root.matchesGlob(vector.path, vector.pattern); }
      catch (error) { caught = error instanceof RangeError && error.code === 'ERR_SM_NODE_PATH_BUDGET' && error.resource === vector.resource; }
      check(caught, 'coded budget error ' + vector.resource);
      check(root.matchesGlob('a.js', '*.js'), 'budget state released');
    }
    for (const [path, pattern, expected] of corpus.acceptedAdversarial) check(root.matchesGlob(path, pattern) === expected, 'bounded adversarial case');
    let invalid = 0;
    for (const value of [undefined, null, 1, false, {}, []]) {
      for (const variant of [rootDefault, win32Default]) {
        try { variant.normalize(value); } catch (error) { if (error instanceof TypeError && error.code === 'ERR_INVALID_ARG_TYPE') invalid++; }
      }
    }
    check(invalid === 12, 'invalid input errors');
    const saved = rootDefault.basename;
    try {
      rootDefault.basename = () => 'mutated';
      check(rootDefault.basename() === 'mutated' && root.basename === saved && posix.basename === saved, 'mutable default with captured named bindings');
    } finally { rootDefault.basename = saved; }
    const random = Math.random;
    let randomCalls = 0;
    try {
      Math.random = () => { randomCalls++; throw new Error('Path must not use randomness'); };
      check(root.matchesGlob('file2.js', 'file{1..3}.js'), 'deterministic brace matching');
    } finally { Math.random = random; }
    check(randomCalls === 0, 'no entropy use');
    calls++;
    return JSON.stringify({ calls, lexical: corpus.lexical.length, globs: corpus.globs.length,
      budgets: corpus.denied.length, acceptedAdversarial: corpus.acceptedAdversarial.length,
      invalid, snapshotPure: true, identities: true, mutableDefaults: true, noEntropy: true });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
