// Production facade/header correctness only; no componentizer/native build.
import assert from 'node:assert/strict';
import * as node from 'node:querystring';
import { Buffer } from 'node:buffer';
import * as source from '../../../builtins/node-compat/querystring.mjs';
import { querystringChecks, prototypeOnlyChecks } from './checks.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { runInThisContext } from 'node:vm';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { validateManifest } from '../../../builtins/node-compat/validate-manifest.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
const production = new URL('../../../builtins/node-compat/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('export-manifest.querystring.node-v22.14.0.json', production)));
validateManifest(manifest, JSON.parse(await readFile(new URL('manifest.schema.json', production))));
assert.equal(manifest.profileVersion, 'sm-node-22.14.0-m0.6');
assert.deepEqual(manifest.modules['node:querystring'].exports, Object.getOwnPropertyNames(node).sort());
const oracle = querystringChecks(node), observed = querystringChecks(source); assert.deepEqual(observed, oracle);
const accepted = JSON.parse(await readFile(new URL('node-results.json', import.meta.url)));
assert.deepEqual(JSON.parse(JSON.stringify(oracle)), accepted.cases);
const header = await readFile(new URL('querystring-factories.generated.h', production), 'utf8');
const match = header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";/); assert(match);
const globalsBefore = Object.getOwnPropertyNames(globalThis), originalGlobalBuffer = globalThis.Buffer;
const registrar = await readFile(new URL('register.cpp', production), 'utf8');
assert.match(registrar, /options\.setForceStrictMode\(\)/, 'Native factory evaluation must preserve ESM strictness');
let generated;
try {
  globalThis.Buffer = undefined;
  const factory = runInThisContext('"use strict";\n'+match[1], { filename: '<generated-querystring-factory>' });
  assert.equal(typeof factory, 'function'); assert.equal(factory.length, 1);
  generated = factory(Buffer);
} finally { globalThis.Buffer = originalGlobalBuffer; }
assert.deepEqual(Object.getOwnPropertyNames(globalThis), globalsBefore, 'no factory global injection');
assert(Object.isFrozen(generated));
assert.deepEqual(querystringChecks(generated), oracle);
const sourceProfile = prototypeOnlyChecks(source), generatedProfile = prototypeOnlyChecks(generated);
assert.deepEqual(sourceProfile, accepted.profileCases); assert.deepEqual(generatedProfile, sourceProfile);
const generator = spawnSync(process.execPath, [fileURLToPath(new URL('generate-querystring-factories.mjs', production)), '--check'], { encoding: 'utf8' });
assert.equal(generator.status, 0, generator.stderr);
const sources = {};
for (const name of ['querystring.mjs', 'export-manifest.querystring.node-v22.14.0.json', 'generate-querystring-factories.mjs', 'querystring-factories.generated.h', 'LICENSE.querystring'])
  sources[name] = hash(await readFile(new URL(name, production)));
const report = { schema: 1, node: process.version, profileVersion: manifest.profileVersion,
  installedBuiltin: false, sources, checksSha256: hash(await readFile(new URL('checks.mjs', import.meta.url))),
  runnerSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  differentialGroups: oracle.length, customSeparatorVectors: 210, byteFallbackVectors: 1536,
  sourceGroupsPassed: observed.length, generatedFactoryGroupsPassed: oracle.length,
  sourceProfile, generatedProfile, schemaValidated: true, noGlobalInjection: true, independentOfGlobalBuffer: true,
  strictFactoryScript: true, registrarSha256: hash(registrar),
  generatorCheck: generator.stdout.trim(), cases: oracle,
  factoryContract: 'kQuerystringFactorySource evaluates to function length1; pass the existing rooted Buffer constructor as sole argument; returns frozen8-export record with mutable default object',
  scope: 'Pinned Node execution of production facade and exact generated factory with Node Buffer. Shared registration/CMake and actual native engine/component gates remain pending.' };
await writeFile(new URL('native-node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ profileVersion: manifest.profileVersion, sourceGroups: observed.length, generatedGroups: oracle.length,
  profileCasesEach: sourceProfile.length, schemaValidated: true, privateBufferInjection: true }));
