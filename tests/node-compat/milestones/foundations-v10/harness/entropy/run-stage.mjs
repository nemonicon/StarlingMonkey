// Local deterministic model tests only; no engine build or host service.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_ENTROPY_OUTPUT ?? '/tmp/starling-node-compat/entropy-stage');
await mkdir(output, { recursive: true });
const compiler = process.env.CXX ?? 'c++';
const compilerVersion = spawnSync(compiler, ['--version'], { encoding: 'utf8' });
assert.equal(compilerVersion.status, 0);
const binary = join(output, 'fill-algorithm-test');
const compileArgs = ['-std=c++17', '-Wall', '-Wextra', '-Werror', join(here, 'fill-algorithm-test.cpp'), '-o', binary];
const compilation = spawnSync(compiler, compileArgs, { encoding: 'utf8' });
assert.equal(compilation.status, 0, compilation.stderr);
const execution = spawnSync(binary, [], { encoding: 'utf8' });
assert.equal(execution.status, 0, execution.stderr);
const policy = spawnSync(process.execPath, [join(here, 'selection-policy-test.mjs')], { encoding: 'utf8' });
assert.equal(policy.status, 0, policy.stderr);
const sources = [];
for (const name of (await readdir(here)).sort()) {
  if (name.endsWith('.json')) continue;
  sources.push({ name, sha256: createHash('sha256').update(await readFile(join(here, name))).digest('hex') });
}
const report = { schema: 1, node: process.version, compiler, compilerVersion: compilerVersion.stdout.trim(),
  compileArgs, algorithm: JSON.parse(execution.stdout), policy: JSON.parse(policy.stdout), sources,
  scope: 'Only staged fill algorithm and build policy validators executed. Guest bridge, private lifecycle policy and OpenSSL patch are uncompiled proposals; no production code changed.' };
await writeFile(join(output, 'staged-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
