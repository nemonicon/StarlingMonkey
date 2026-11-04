// Production facade/header correctness only; no native compilation is invoked.
import assert from 'node:assert/strict';
import * as node from 'node:assert';
import * as nodeStrict from 'node:assert/strict';
import * as source from '../../../builtins/node-compat/assert.mjs';
import * as sourceStrict from '../../../builtins/node-compat/assert-strict.mjs';
import { assertChecks, prototypeOnlyChecks } from './checks.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { runInThisContext } from 'node:vm';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { validateManifest } from '../../../builtins/node-compat/validate-manifest.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = value => createHash('sha256').update(value).digest('hex');
const production = new URL('../../../builtins/node-compat/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('export-manifest.assert.node-v22.14.0.json', production)));
validateManifest(manifest, JSON.parse(await readFile(new URL('manifest.schema.json', production))));
assert.equal(manifest.profileVersion, 'sm-node-22.14.0-m0.5');
assert.deepEqual(manifest.modules['node:assert'].exports, Object.getOwnPropertyNames(node).sort());
assert.deepEqual(manifest.modules['node:assert/strict'].exports, Object.getOwnPropertyNames(nodeStrict).sort());
const oracle = assertChecks(node, nodeStrict);
const accepted = JSON.parse(await readFile(new URL('node-results.json', import.meta.url)));
assert.deepEqual(JSON.parse(JSON.stringify(oracle)), accepted.cases);
const observed = assertChecks(source, sourceStrict); assert.deepEqual(observed, oracle);
const header = await readFile(new URL('assert-factories.generated.h', production), 'utf8');
const match = header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";/); assert(match);
const globalsBefore = Object.getOwnPropertyNames(globalThis);
const registrar = await readFile(new URL('register.cpp', production), 'utf8');
assert.match(registrar, /options\.setForceStrictMode\(\)/, 'Native factory evaluation must preserve ESM strictness');
const factory = runInThisContext('"use strict";\n'+match[1], { filename: '<generated-assert-factory>' });
assert.equal(typeof factory, 'function'); assert.equal(factory.length, 0);
const graph = factory(undefined);
assert.deepEqual(Object.getOwnPropertyNames(graph).sort(), ['root', 'strict']);
assert.deepEqual(Object.getOwnPropertyNames(globalThis), globalsBefore, 'no factory global injection');
assert(Object.isFrozen(graph) && Object.isFrozen(graph.root) && Object.isFrozen(graph.strict));
assert.deepEqual(assertChecks(graph.root, graph.strict), oracle);
const sourceProfile = prototypeOnlyChecks(source), generatedProfile = prototypeOnlyChecks(graph.root);
assert.deepEqual(sourceProfile, accepted.deferredAndMutationCases); assert.deepEqual(generatedProfile, sourceProfile);
const generator = spawnSync(process.execPath, [fileURLToPath(new URL('generate-assert-factories.mjs', production)), '--check'], { encoding: 'utf8' });
assert.equal(generator.status, 0, generator.stderr);
const sources = {};
for (const name of ['assert.mjs', 'assert-strict.mjs', 'export-manifest.assert.node-v22.14.0.json', 'generate-assert-factories.mjs', 'assert-factories.generated.h', 'LICENSE.assert'])
  sources[name] = hash(await readFile(new URL(name, production)));
const report = { schema: 1, node: process.version, profileVersion: manifest.profileVersion,
  installedBuiltin: false, sources, checksSha256: hash(await readFile(new URL('checks.mjs', import.meta.url))),
  runnerSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  differentialGroups: oracle.length, primitiveEqualityComparisons: 784,
  sourceGroupsPassed: observed.length, generatedFactoryGroupsPassed: oracle.length,
  sourceProfile, generatedProfile, schemaValidated: true, noGlobalInjection: true,
  strictFactoryScript: true, registrarSha256: hash(registrar),
  generatorCheck: generator.stdout.trim(), cases: oracle,
  factoryContract: 'kAssertFactorySource evaluates to function length0; evaluate_factory argument undefined is ignored; result frozen{root,strict} finite22-export records share callable default/strict graph',
  scope: 'Pinned Node execution of production ESM facades and exact generated factory script only. Shared registration/CMake integration and native engine/component gates remain pending.' };
await writeFile(new URL('native-node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ profileVersion: manifest.profileVersion, sourceGroups: observed.length, generatedGroups: oracle.length,
  profileCasesEach: sourceProfile.length, schemaValidated: true, noGlobalInjection: true }));
