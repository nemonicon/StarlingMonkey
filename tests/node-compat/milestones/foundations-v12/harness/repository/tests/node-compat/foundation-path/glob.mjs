// Run with pinned Node22.14 --expose-internals. Only ordinary, bounded patterns
// reach the historical Node matcher; hostile regression inputs run in profile only.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createPathModules } from '../../../builtins/node-compat/path.mjs';
const { minimatch } = createRequire(import.meta.url)('internal/deps/minimatch/index');
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const graph = createPathModules().root.default;
const paths = ['', '.', '..', 'a', 'aa', 'b', 'ab', 'abc', 'foo', 'bar', 'foobar', '.git', '.a.js',
  'file.js', 'file.ts', 'file.md', 'file2.js', 'src/file.js', 'src/deep/file.ts', 'a/b', 'a//b',
  'a\\b', 'C:\\a\\b.js', '//server/share/a.js', 'é', '東京', '😀', '😀é', '\ud83d', '\ude00', '$', '\0',
  '\0SM_NODE_PATH\0OPEN\0', '\0SM_NODE_PATH\0a', 'a\0SM_NODE_PATH\0OPEN\0'];
const patterns = ['', '*', '**', '?', '??', 'a?', '*a', 'a*', '*a*', '*.js', '**/*.js', '**/*.{js,ts}',
  '{a,b}', '{a,{b,c}}', 'file{1..3}.js', '@(a|b)', '+(a|b)', '?(a|b)', '*(a|b)', '!(foo|bar)',
  '[abc]', '[!abc]', '[a-z]', '[]', '[[]', '[😀]', '[[:alpha:]]', '?[[:alpha:]]', '[[:print:]]',
  '[[:punct:]]', '[[:graph:]]', '[[:ascii:]]', '[[:xdigit:]]', 'src/**', 'a/**/b', 'a\\*',
  '#literal', '!literal', '.git', '😀', '\0', '\0SM_NODE_PATH\0OPEN\0', '{a},b}',
  '\0SM_NODE_PATH\0{a,b}', '{a\0SM_NODE_PATH\0OPEN\0,b}'];
const vectors = [], differences = [];
for (const variant of ['posix', 'win32']) {
  const options = { nocase: false, windowsPathsNoEscape: true, nonegate: true, nocomment: true,
    optimizationLevel: 2, platform: variant, nocaseMagicOnly: true };
  for (const path of paths) for (const pattern of patterns) {
    const expected = minimatch(path, pattern, options);
    const actual = graph[variant].matchesGlob(path, pattern);
    const vector = { variant, path, pattern, expected };
    vectors.push(vector);
    if (actual !== expected) differences.push({ ...vector, actual });
  }
  // Portable category expansion: astral/new-Unicode16 letters/digits, lone
  // surrogates, combining marks, separators and unions/negations of classes.
  const unicodePaths = ['A', 'a', '9', '_', '!', '+', '\u2160', '\u0301', '\u2003', '\0',
    '\ud800', '\udfff', '\u{10400}', '\u{10428}', '\u{1e4f0}', '\u{2ebf0}'];
  const classes = ['alnum', 'alpha', 'ascii', 'blank', 'cntrl', 'digit', 'graph', 'lower',
    'print', 'punct', 'space', 'upper', 'word', 'xdigit'];
  for (const path of unicodePaths) for (const name of classes) for (const negate of ['', '!']) {
    const pattern = '[' + negate + '[:' + name + ':]]';
    const expected = minimatch(path, pattern, options);
    const actual = graph[variant].matchesGlob(path, pattern);
    const vector = { variant, path, pattern, expected }; vectors.push(vector);
    if (actual !== expected) differences.push({ ...vector, actual });
  }
}
await writeFile(join(here, 'glob-vectors.json'), JSON.stringify(vectors) + '\n');
await writeFile(join(here, 'glob-differences.json'), JSON.stringify(differences, null, 2) + '\n');
console.log(JSON.stringify({ vectors: vectors.length, differences: differences.length,
  firstDifferences: differences.slice(0, 12) }, null, 2));
assert.equal(differences.length, 0, 'Every normal-domain difference must be fixed or explicitly documented');

const denied = [
  ['x', '{1..10000000}', 'brace-alternatives'],
  ['x', '{1..2..0}', 'brace-zero-step'],
  ['x', '{9007199254740992..9007199254740993}', 'brace-numeric-domain'],
  ['x', '{a,b}'.repeat(8), 'brace-alternatives'],
  ['x', '{'.repeat(9) + 'a,b' + '}'.repeat(9), 'brace-depth'],
  ['x', '@('.repeat(9) + 'a' + ')'.repeat(9), 'extglob-depth'],
  ['x', '@('.repeat(8) + '@{(x|y),literal}' + ')'.repeat(8), 'extglob-depth'],
  ['x', '*'.repeat(257), 'magic-segment-code-units'],
  ['x'.repeat(4097), '*', 'path-code-units'],
  ['x', 'a'.repeat(1025), 'pattern-code-units'],
  ['x'.repeat(4096), 'a'.repeat(200) + '*', 'work-estimate'],
  [Array.from({ length: 512 }, (_, i) => String.fromCharCode(0x400 + i)).join('') + 'c',
    '*(?|??)'.repeat(24) + 'c', 'matcher-work'],
  ['a'.repeat(22), '[[:alnum:]]'.repeat(22), 'matcher-work'],
];
for (const [path, pattern, resource] of denied) {
  assert.throws(() => graph.matchesGlob(path, pattern), { name: 'RangeError', code: 'ERR_SM_NODE_PATH_BUDGET', resource });
  assert.equal(graph.matchesGlob('a.js', '*.js'), true, 'Budget exception must release call state');
}
const acceptedAdversarial = [
  ['a'.repeat(128), '*a*a*a*a*a*Z', false],
  ['a'.repeat(100) + 'b', '*(a|aa)', false],
  ['a'.repeat(100), '*(a|aa)', true],
  ['aaa', '!(b|c)', true],
];
for (const [path, pattern, expected] of acceptedAdversarial) assert.equal(graph.matchesGlob(path, pattern), expected);
await writeFile(join(here, 'glob-results.json'), JSON.stringify({ schema: 1, node: process.version,
  vectors: vectors.length, differences: [], denied: denied.map(([path, pattern, resource]) => ({ path, pattern, resource })),
  acceptedAdversarial, historicalOraclePolicy: 'Only nocase is fixed false to select the portable POSIX-host policy; all other options are exactly Node22 path.glob. Hostile patterns never reach the vulnerable historical oracle.',
  patchedMatcher: 'minimatch11.0.1 + nonrecursive-glob-match1.0.3 + strict profile budgets and Node22 UTF16/class shim' }, null, 2) + '\n');
