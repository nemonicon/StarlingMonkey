import assert from 'node:assert/strict';
import native from 'node:path';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { createPathModules } from '../../../builtins/node-compat/path.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const graph = createPathModules();
const profile = graph.root.default;
const methods = ['normalize', 'isAbsolute', 'dirname', 'basename', 'extname', 'parse', 'toNamespacedPath', '_makeLong'];
const exports = ['_makeLong', 'basename', 'default', 'delimiter', 'dirname', 'extname', 'format', 'isAbsolute', 'join', 'matchesGlob', 'normalize', 'parse', 'posix', 'relative', 'resolve', 'sep', 'toNamespacedPath', 'win32'];
assert.deepEqual(Object.keys(graph.root).sort(), exports);
for (const record of [graph.root, graph.posix, graph.win32]) {
  assert.strictEqual(record.default.posix, profile.posix);
  assert.strictEqual(record.default.win32, profile.win32);
  for (const name of exports.filter(name => name !== 'default')) assert.strictEqual(record[name], record.default[name]);
}
assert.strictEqual(profile, profile.posix);
assert.strictEqual(profile.posix._makeLong, profile.posix.toNamespacedPath);
assert.strictEqual(profile.win32._makeLong, profile.win32.toNamespacedPath);
assert.equal(profile.sep, '/'); assert.equal(profile.delimiter, ':');
assert.equal(profile.win32.sep, '\\'); assert.equal(profile.win32.delimiter, ';');
const oldCwd = process.cwd();
process.chdir('/');
const vectors = [];
function compare(variant, method, args) {
  const expected = native[variant][method](...args);
  const actual = profile[variant][method](...args);
  assert.deepEqual(actual, expected, JSON.stringify({ variant, method, args }));
  vectors.push({ variant, method, args, expected });
}
let seed = 0x50415448;
function random(max) { seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; return (seed >>> 0) % max; }
const bases = ['', '.', '..', '/', '//', '///', '\\', '\\\\', 'a', '.a', 'a.', 'a..', '..a', '...', 'a/b', 'a\\b', '/a/../b', 'C:', 'C:a', 'C:\\', 'C:\\a\\..\\b', 'D:/a//b', '\\\\server\\share\\a', '//server//share/..', '\\\\?\\C:\\a', '\\\\.\\pipe\\a', 'é/東京/😀', 'x\0y', '\0SM_NODE_PATH\0OPEN\0'];
const atoms = ['a', 'bb', '.', '..', '', '/', '\\', ':', 'C:', 'D:', 'é', '😀', '.git', 'x.js'];
for (let i = 0; i < 500; i++) {
  let path = '';
  for (let j = 0, n = 1 + random(8); j < n; j++) path += atoms[random(atoms.length)];
  bases.push(path);
}
try {
  for (const variant of ['posix', 'win32']) {
    for (const path of bases) {
      for (const method of methods) compare(variant, method, [path]);
      compare(variant, 'basename', [path, '.js']);
      compare(variant, 'format', [native[variant].parse(path)]);
      compare(variant, 'resolve', [path]);
      compare(variant, 'join', [path, 'child', '..', 'end']);
    }
    for (let i = 0; i < 500; i++) {
      const a = bases[random(bases.length)], b = bases[random(bases.length)];
      compare(variant, 'relative', [a, b]);
      compare(variant, 'resolve', [a, b]);
      compare(variant, 'join', [a, b]);
    }
  }
} finally { process.chdir(oldCwd); }

let invalidCases = 0;
for (const variant of ['posix', 'win32']) {
  for (const value of [undefined, null, false, true, 1, NaN, [], {}, Symbol('x'), new String('x')]) {
    for (const method of ['normalize', 'isAbsolute', 'dirname', 'basename', 'extname', 'parse', 'join', 'resolve', 'matchesGlob']) {
      const args = method === 'matchesGlob' ? [value, '*'] : [value];
      assert.throws(() => profile[variant][method](...args), { name: 'TypeError', code: 'ERR_INVALID_ARG_TYPE' }); invalidCases++;
    }
    for (const args of [[value, 'a'], ['a', value]]) {
      assert.throws(() => profile[variant].relative(...args), { name: 'TypeError', code: 'ERR_INVALID_ARG_TYPE' }); invalidCases++;
    }
    assert.strictEqual(profile[variant].toNamespacedPath(value), value);
  }
}
let upstreamAssertions = 0, messageFormattingDeviations = 0;
const sourceManifest = JSON.parse(await readFile(join(here, 'upstream/sources.json')));
const upstreamTests = [];
for (const entry of sourceManifest.files) {
  const bytes = await readFile(join(here, 'upstream', entry.path));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256);
  let source = String(bytes);
  let skippedVirtualCwdFailureProbe = false;
  if (entry.path === 'test-path-resolve.js') {
    const marker = "if (!common.isWindows) {\n  // Test handling relative paths to be safe when process.cwd() fails.";
    assert(source.includes(marker)); source = source.slice(0, source.indexOf(marker));
    skippedVirtualCwdFailureProbe = true;
  }
  const counted = Object.assign((...args) => { upstreamAssertions++; return assert(...args); }, assert);
  for (const name of ['strictEqual', 'deepStrictEqual', 'match']) counted[name] = (...args) => { upstreamAssertions++; return assert[name](...args); };
  counted.deepStrictEqual = (actual, expected, ...args) => {
    upstreamAssertions++;
    return assert.deepStrictEqual(actual, structuredClone(expected), ...args);
  };
  counted.throws = (fn, expected, ...args) => {
    upstreamAssertions++;
    if (expected && typeof expected === 'object' && typeof expected.message === 'string') {
      const { message, ...fields } = expected; messageFormattingDeviations++;
      return assert.throws(fn, fields, ...args);
    }
    return assert.throws(fn, expected, ...args);
  };
  const common = { isWindows: false, invalidArgTypeHelper: () => ' (message formatting excluded by profile contract)' };
  const require = id => {
    if (id === '../common') return common;
    if (id === 'assert') return counted;
    if (id === 'path') return profile;
    if (id === 'path/posix') return profile.posix;
    if (id === 'path/win32') return profile.win32;
    if (id === '../common/fixtures') return { path: () => '/fixtures/a.js' };
    if (id === 'child_process') return {};
    throw new Error('Unexpected upstream dependency: ' + id);
  };
  vm.runInNewContext(source, { require, __filename: 'test/parallel/' + entry.path,
    __dirname: 'test/parallel', process: { cwd: () => '/', platform: 'linux', argv: [] }, console },
    { filename: entry.path, timeout: 5000 });
  upstreamTests.push({ name: entry.path, skippedVirtualCwdFailureProbe });
}
const report = { schema: 1, node: process.version, lexicalVectors: vectors.length, invalidCases,
  upstreamAssertions, upstreamTests, messageFormattingDeviations,
  virtualPolicy: { cwd: '/', platform: 'posix', globNoCase: false },
  deviations: ['Complex invalid-argument messages are not compared; TypeError/code are checked.',
    'The upstream probe replacing process.cwd with an empty provider is excluded: this profile intentionally has immutable virtual cwd.',
    'Windows-host-only filesystem/process blocks are not selected in the POSIX virtual profile.'] };
await writeFile(join(here, 'lexical-vectors.json'), JSON.stringify(vectors) + '\n');
await writeFile(join(here, 'semantic-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ lexicalVectors: vectors.length, invalidCases, upstreamAssertions,
  upstreamFiles: upstreamTests.length, messageFormattingDeviations }, null, 2));
