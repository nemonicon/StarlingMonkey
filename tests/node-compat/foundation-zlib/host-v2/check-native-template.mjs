// Node22 source/host test only. Never exercises the known-unhardened guest
// CompressionStream or DecompressionStream implementations.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as zlib from 'node:zlib';

assert.equal(process.version, 'v22.14.0');
assert(!process.env.NODE_OPTIONS, 'NODE_OPTIONS is not permitted for the oracle');
const here = dirname(fileURLToPath(import.meta.url));
const out = resolve(process.env.NODE_COMPAT_ZLIB_OUTPUT || '/tmp/starling-node-compat/zlib-template-v2');
mkdirSync(out, { recursive: true });
const reportPath = resolve(out, 'results.json');
assert(!existsSync(reportPath), 'Preserve earlier result: choose a fresh output path');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const sources = ['../bounded-zlib.template.h', 'native-driver.cpp', 'check-native-template.mjs']
  .map(path => ({ path, sha256: hash(readFileSync(resolve(here, path))) }));
const compiler = process.env.CXX || 'c++';
const binary = resolve(out, 'native-driver');
const compileArgs = ['-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror', '-fno-exceptions',
  resolve(here, 'native-driver.cpp'), '-lz', '-o', binary];
execFileSync(compiler, compileArgs, { stdio: 'pipe' });
const formats = [
  ['zlib', zlib.deflateSync, zlib.inflateSync],
  ['gzip', zlib.gzipSync, zlib.gunzipSync],
  ['raw', zlib.deflateRawSync, zlib.inflateRawSync],
];
const inputs = [0, 1, 31, 16384, 16385, 65536, 262144].map(length =>
  Buffer.from(Array.from({ length }, (_, index) => (index * 73 + (index >> 8)) & 255)));
inputs.push(Buffer.alloc(1024 * 1024, 0x61));
// Reproducible computation-only bytes: exercise several deflate output chunks.
let randomState = 0x12345678;
inputs.push(Buffer.from(Array.from({length: 262144}, () => {
  randomState ^= randomState << 13; randomState ^= randomState >>> 17;
  randomState ^= randomState << 5; return randomState & 255;
})));
const cases = [];
for (let format = 0; format < formats.length; format++) {
  const [name, compress] = formats[format];
  for (const input of inputs) {
    const compressed = compress(input);
    cases.push({ name: `${name}-encode-${input.length}`, operation: 1, format,
      input: input.toString('hex'), limit: 16 * 1024 * 1024, status: 0,
      expectedDecoded: input.toString('hex') });
    cases.push({ name: `${name}-decode-${input.length}`, operation: 0, format,
      input: compressed.toString('hex'), limit: 16 * 1024 * 1024, status: 0,
      expected: input.toString('hex') });
  }
  const input = Buffer.alloc(4096, 0x61), compressed = compress(input);
  cases.push({ name: `${name}-exact-limit`, operation: 0, format,
    input: compressed.toString('hex'), limit: input.length, status: 0, expected: input.toString('hex') });
  cases.push({ name: `${name}-output-limit`, operation: 0, format,
    input: compressed.toString('hex'), limit: input.length - 1, status: 2 });
  cases.push({ name: `${name}-incomplete`, operation: 0, format,
    input: compressed.subarray(0, compressed.length - 1).toString('hex'), limit: 16 * 1024 * 1024, status: 5 });
  cases.push({ name: `${name}-trailing`, operation: 0, format,
    input: Buffer.concat([compressed, Buffer.from([0x71])]).toString('hex'), limit: 16 * 1024 * 1024, status: 7 });
  cases.push({ name: `${name}-empty-compressed-input`, operation: 0, format, input: '',
    limit: 16 * 1024 * 1024, status: 5 });
}
cases.push({ name: 'input-limit', operation: 1, format: 0,
  input: Buffer.alloc(1024 * 1024 + 1).toString('hex'), limit: 16 * 1024 * 1024, status: 1 });
const dictionary = Buffer.from('dictionary useful words');
cases.push({ name: 'dictionary-deferred', operation: 0, format: 0,
  input: zlib.deflateSync(Buffer.from('useful words'), { dictionary }).toString('hex'),
  limit: 16 * 1024 * 1024, status: 6 });
const damaged = zlib.deflateSync(Buffer.from('checksum'));
damaged[damaged.length - 1] ^= 1;
cases.push({ name: 'checksum', operation: 0, format: 0,
  input: damaged.toString('hex'), limit: 16 * 1024 * 1024, status: 4 });
const fullBoundary = Buffer.alloc(16 * 1024 * 1024, 0x61);
cases.push({ name: 'zlib-exact-default-output-cap', operation: 0, format: 0,
  input: zlib.deflateSync(fullBoundary).toString('hex'), limit: fullBoundary.length,
  status: 0, expected: fullBoundary.toString('hex') });
cases.push({ name: 'gzip-one-over-default-output-cap', operation: 0, format: 1,
  input: zlib.gzipSync(Buffer.alloc(fullBoundary.length + 1, 0x61)).toString('hex'),
  limit: fullBoundary.length, status: 2 });
for (let format = 0; format < formats.length; format++) {
  const [name, compress] = formats[format];
  cases.push({name: name+'-zero-limit-empty-result', operation: 0, format,
    input: compress(Buffer.alloc(0)).toString('hex'), limit: 0, status: 0, expected: ''});
  cases.push({name: name+'-zero-limit-nonempty-result', operation: 0, format,
    input: compress(Buffer.from('a')).toString('hex'), limit: 0, status: 2});
  cases.push({name: name+'-zero-limit-encode', operation: 1, format,
    input: '', limit: 0, status: 2});
}
for (const [name, tail] of [['concatenated-member',zlib.gzipSync('b')], ['zero-padding',Buffer.alloc(8)]]) {
  const input=Buffer.concat([zlib.gzipSync('a'),tail]);
  cases.push({name:'gzip-'+name+'-profile-deviation', operation:0, format:1,
    input:input.toString('hex'), limit:16*1024*1024, status:7,
    nodeAcceptedOutput:zlib.gunzipSync(input).toString('hex')});
}
const gzipDamaged=zlib.gzipSync('gzip checksum');gzipDamaged[gzipDamaged.length-8]^=1;
cases.push({name:'gzip-crc-corrupt', operation:0, format:1,
  input:gzipDamaged.toString('hex'), limit:16*1024*1024, status:4});
const stdin = cases.map(c => `${c.operation} ${c.format} ${c.limit} ${c.input || '-'}`).join('\n') + '\n';
const stdout = execFileSync(binary, [], { input: stdin, maxBuffer: 64 * 1024 * 1024, encoding: 'utf8' });
const lines = stdout.trim().split('\n');
assert.equal(lines.length, cases.length);
const results = cases.map((test, index) => {
  const [statusText, zlibText, encoded] = lines[index].split(' ');
  const status = Number(statusText), zlibStatus = Number(zlibText), output = encoded === '-' ? '' : encoded;
  assert.equal(status, test.status, test.name);
  if (test.expected !== undefined) assert.equal(output, test.expected, test.name);
  if (test.expectedDecoded !== undefined) {
    assert.equal(formats[test.format][2](Buffer.from(output, 'hex')).toString('hex'), test.expectedDecoded, test.name);
  }
  if (status !== 0) assert.equal(output, '', `${test.name}: no partial output`);
  return { name: test.name, status, zlibStatus, outputBytes: output.length / 2,
    outputSha256: hash(Buffer.from(output, 'hex')),
    ...(test.nodeAcceptedOutput!==undefined?{nodeAcceptedOutput:test.nodeAcceptedOutput}:{} ) };
});
const nodeInventory = Object.fromEntries(Object.keys(zlib).map(key => [key, typeof zlib[key]]));
const [hostHeaderZlib, hostRuntimeZlib, compilerMacro] = execFileSync(binary, ['--version'], {encoding:'utf8'}).trim().split('\n');
const compilerVersion = execFileSync(compiler, ['--version'], {encoding:'utf8'}).trim();
const dynamicLinkage = execFileSync('/usr/bin/otool', ['-L',binary], {encoding:'utf8'}).trim();
const report = { schema: 1, state: 'host-native-template-ordinary-cases-pass',
  scope: 'Host system zlib only; not guest engine, real component, final imports, GC, OOM, streaming or Node module support.',
  node: process.version, nodeZlib: process.versions.zlib,
  sources, compiler, compilerVersion, compilerMacro, hostHeaderZlib, hostRuntimeZlib, dynamicLinkage,
  hostLibraryIdentityScope:'otool install-name/compatibility/current version only; macOS dyld shared-cache bytes not individually hashed',
  compileArgs, binarySha256: hash(readFileSync(binary)),
  inputSha256: hash(stdin), stdoutSha256: hash(stdout), nodeInventory,
  checks: cases.length, results };
writeFileSync(resolve(out, 'stdin.txt'), stdin);
writeFileSync(resolve(out, 'stdout.txt'), stdout);
writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ state: report.state, checks: report.checks, output: reportPath }));
