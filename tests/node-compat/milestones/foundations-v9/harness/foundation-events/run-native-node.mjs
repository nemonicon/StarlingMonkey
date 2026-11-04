import assert from 'node:assert/strict';
import * as node from 'node:events';
import * as events from '../../../builtins/node-compat/events.mjs';
import { eventsChecks } from './checks.mjs';
import { nativeEventsChecks } from './native-checks.mjs';
import { prototypeChecks } from './prototype-checks.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { runInThisContext } from 'node:vm';
import { validateManifest } from '../../../builtins/node-compat/validate-manifest.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const oracle = eventsChecks(node), observed = eventsChecks(events); assert.deepEqual(observed, oracle);
const nativeOracle = nativeEventsChecks(node), nativeObserved = nativeEventsChecks(events); assert.deepEqual(nativeObserved, nativeOracle);
const header = await readFile(new URL('../../../builtins/node-compat/events-factories.generated.h', import.meta.url), 'utf8');
const match = header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";/); assert(match);
const factory = runInThisContext(match[1], {filename:'<generated-events-factory>'}); const generated = factory();
assert.deepEqual(eventsChecks(generated), oracle); assert.deepEqual(nativeEventsChecks(generated), nativeOracle);
const profile = prototypeChecks(events); assert.deepEqual(profile, { deferred: 13, limits: 3, eventNameCoercionDeferred: true });
const manifest = JSON.parse(await readFile(new URL('../../../builtins/node-compat/export-manifest.events.node-v22.14.0.json', import.meta.url)));
validateManifest(manifest, JSON.parse(await readFile(new URL('../../../builtins/node-compat/manifest.schema.json', import.meta.url))));
assert.deepEqual(manifest.modules['node:events'].exports, Object.getOwnPropertyNames(node).sort());
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: false,
  facadeSha256: hash(await readFile(new URL('../../../builtins/node-compat/events.mjs', import.meta.url))),
  checksSha256: hash(await readFile(new URL('./native-checks.mjs', import.meta.url))), generatedHeaderSha256: hash(header), generatedFactoryCasesPassed: oracle.length + nativeOracle.length, cases: oracle, nativeCases: nativeOracle, profile,
  scope: 'Actual production-source facade imported in pinned Node only; native registration and component runtime await v4 build' };
await writeFile(new URL('./native-node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ differentialCases: oracle.length + nativeOracle.length, profile }));
