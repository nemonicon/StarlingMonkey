import assert from 'node:assert/strict';
import * as events from 'node:events';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {publicCases,nestedOnceCases,receiverCases,targetSymbolInfo} from './public-cases.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const publicObserved=await publicCases(events),nested=nestedOnceCases(events),receivers=receiverCases(events);
const previousNested=JSON.parse(await readFile(new URL('../m0.10-proposal/reentrant-once-v1/node-results.json',import.meta.url)));
const previousReceiver=JSON.parse(await readFile(new URL('../integration-candidate-m0.10/checks/node-receiver-results.json',import.meta.url)));
assert.deepEqual(nested,previousNested.cases);assert.deepEqual(receivers,previousReceiver.results);
const originalBytes=await readFile(new URL('../node-results.json',import.meta.url));
const report={state:'PINNED_NODE_ORACLE_ONLY',node:process.version,executable:process.execPath,executableSha256:hash(await readFile(process.execPath)),
 sourceSha256:hash(await readFile(new URL('./public-cases.mjs',import.meta.url))),runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),
 publicCases:publicObserved,nestedOnceCases:nested,receiverCases:receivers,targetSymbolInfo:targetSymbolInfo(),
 originalOracleSha256:hash(originalBytes),originalOracleCaseCount:JSON.parse(originalBytes).caseCount,
 previousNestedOracleSha256:hash(await readFile(new URL('../m0.10-proposal/reentrant-once-v1/node-results.json',import.meta.url))),
 previousReceiverOracleSha256:hash(await readFile(new URL('../integration-candidate-m0.10/checks/node-receiver-results.json',import.meta.url))),
 passed:{public:publicObserved.length,nested:nested.length,receivers:receivers.length,total:publicObserved.length+nested.length+receivers.length},
 deviationsNotNormalizedIntoParity:['Detailed received-value messages are omitted from the explicitly bounded error-class/code comparison.','Global Symbol.dispose description/registry identity is measured separately.','Original ALS registration/dispatch oracle is preserved, but no deployed ALS implementation is claimed.','Node process uncaughtException behavior remains a separate reference; selected guest fatal/discard policy differs.']};
await writeFile(new URL('./node-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.passed));
