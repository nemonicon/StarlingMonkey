// Source-only inventory; never invokes a componentizer or native build.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const hash = value => createHash('sha256').update(value).digest('hex');
const entries = [
  ['toolchain', '@bytecodealliance/jco/dist/node-builtins/querystring.js'],
  ['toolchain', 'unenv/dist/runtime/node/querystring.mjs'],
  ['toolchain', 'unenv/dist/runtime/node/internal/querystring/querystring.mjs'],
  ['repository', 'runtime/engine.cpp'], ['repository', 'runtime/encode.cpp'],
  ['repository', 'crates/rust-url/src/lib.rs'], ['repository', 'builtins/web/url.cpp'],
  ['repository', 'builtins/web/text-codec/text-decoder.cpp'],
  ['repository', 'builtins/node-compat/buffer-facade.mjs'],
  ['repository', 'tests/integration/urlsearchparams/urlsearchparams.js'],
  ['repository', 'tests/integration/textdecoder/textdecoder.js'],
];
const sourceFiles = [];
for (const [origin, path] of entries) {
  const absolute = join(origin === 'repository' ? repository : join(toolchain, 'node_modules'), path);
  const bytes = await readFile(absolute); sourceFiles.push({ origin, path, sha256: hash(bytes), bytes: bytes.length });
}
const versions = {};
for (const name of ['@bytecodealliance/jco', 'unenv', 'readable-stream'])
  versions[name] = JSON.parse(await readFile(join(toolchain, 'node_modules', name, 'package.json'))).version;
const report = { schema: 1, node: process.version, toolchain, versions, sourceFiles,
  nodeEmbeddedSourceSha256: Object.fromEntries(['querystring', 'internal/querystring'].map(name => [name, hash(process.binding('natives')[name])])),
  observations: [
    'Jco querystringAdapter imports UNENV_BUFFER_CORE and reexports unenv; it is a JS adapter, not a native module',
    'Unenv percent scanner and encodeStr derive from Node22.7; its default hook reads differ from pinned22 mutable QueryString.escape/unescape/unescapeBuffer semantics',
    'runtime/engine.cpp::Engine::init uses JS::InitRealmStandardClasses: native URI intrinsics need no host capabilities',
    'rust-url::params_init strips leading question mark and calls form_urlencoded::parse; URLSearchParams is not a compatible replacement',
    'Querystring malformed percent fallback truncates raw UTF16 units modulo256, then performs replacement UTF8 decode preserving BOM',
    'Native Buffer facade captures TextDecoder(ignoreBOM:true); profile allocUnsafe is deferred, so this scanner uses supported captured alloc and shared slice',
    'Node internal/querystring::encodeStr pairs ANY surrogate with a following code unit; only terminal surrogate throws URIError ERR_INVALID_URI',
    'Node maxKeys defaults1000 segments; empty segments count; fractional/nonpositive/NaN/Infinity behavior is not ordinary positive-integer validation',
    'No readable-stream4.7 lib Querystring module demand was found in inspected tree',
    'Published locked adapter trees do not contain a dedicated Querystring conformance suite; existing native URL/TextDecoder tests do not establish Querystring compatibility',
  ],
  primaryReferences: [
    'https://github.com/nodejs/node/blob/v22.14.0/lib/querystring.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/internal/querystring.js',
    'https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-querystring.js',
  ],
  testReview: 'Pinned Node test-querystring source inspected for null-prototype/prototype-name keys, arrays, empty segments, custom delimiters, URI escaping, malformed escapes and primitive stringify behavior. Full upstream suite not executed.',
  scope: 'Read-only source inventory plus pinned runtime reflection; Node oracle results and future component proof are separate' };
await writeFile(new URL('source-audit.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ filesHashed: sourceFiles.length, versions }));
