// Small source-only inventory. Does not bundle or componentize.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';
assert.equal(process.version, 'v22.14.0');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const hash = value => createHash('sha256').update(value).digest('hex');
const paths = [
  '@bytecodealliance/jco/dist/node-builtins/assert.js',
  '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/assert/index.js',
  '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/assert/assertion-error.js',
  '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/test/assert.js',
  'unenv/dist/runtime/node/assert.mjs',
  'unenv/dist/runtime/node/assert/strict.mjs',
  'readable-stream/lib/ours/errors.js',
];
const sourceFiles = await Promise.all(paths.map(async path => {
  const content = await readFile(join(toolchain, 'node_modules', path));
  return { path, sha256: hash(content), bytes: content.length };
}));
const versions = {};
for (const name of ['@bytecodealliance/jco', '@bytecodealliance/jco-std', 'unenv', 'readable-stream'])
  versions[name] = JSON.parse(await readFile(join(toolchain, 'node_modules', name, 'package.json'))).version;
const report = { schema: 1, node: process.version, toolchain, versions, sourceFiles,
  observations: [
    'Jco createAssertBuiltin/assertAdapter exports Node24 Assert; isolated pinned22 proposal intentionally excludes Assert',
    'Jco-std locked code lives under node/24.x.x; not a pinned22 conformance oracle',
    'unenv isDeepEqual/isDeepStrictEqual use JSON serialization equality; not reused',
    'unenv error-code constructors are generic Error aliases; not reused',
    'readable-stream4.7.0/lib uses no assert-module import in inspected tree; lib/ours/errors.js has its own private assert helper',
    'Published locked trees expose test/assert.js as node:test runtime helper, not a dedicated Assert adapter conformance suite',
  ],
  primaryReferences: [
    'https://github.com/nodejs/node/blob/v22.14.0/lib/assert.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/assert/strict.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/internal/assert/assertion_error.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/internal/assert/utils.js',
    'https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-assert.js',
  ],
  testSourceReview: 'Pinned Node test-assert basics, Error-message identity, exception matching, unmatched doesNotThrow propagation and generated diagnostics reviewed. Full Node upstream suite has NOT been executed against the prototype.',
  scope: 'Source inspection only; API oracle and prototype results are recorded separately in node-results.json' };
await writeFile(new URL('source-audit.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ filesHashed: sourceFiles.length, versions }));
