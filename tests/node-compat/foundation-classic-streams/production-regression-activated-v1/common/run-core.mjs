// Source-preparation runner: deliberately fails at null pins before old runner import.
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {verifyProductionTicks,requireFreshOutput,completeRegression} from './preflight.mjs';
const admission=await verifyProductionTicks({gcStress:false});
await requireFreshOutput('NODE_COMPAT_OUTPUT');
if(process.env.NODE_COMPAT_SEMANTIC_ENTRY)assert.equal(resolve(process.env.NODE_COMPAT_SEMANTIC_ENTRY),fileURLToPath(new URL('../../../fixtures/component.mjs',import.meta.url)));
await import('../../../run.mjs');
await completeRegression('NODE_COMPAT_OUTPUT',admission);
