// New source-only wrapper: null actual pins stop before any legacy harness.
import assert from 'node:assert/strict';
import {variantOptions} from './capabilities.mjs';
import {verifyProductionTicks,requireFreshOutput,completeRegression} from './preflight.mjs';
const label=process.env.NODE_COMPAT_FOLLOWON_VARIANT;
assert.equal(label,'gc-off');
const admission=await verifyProductionTicks(variantOptions(label));
await requireFreshOutput('NODE_COMPAT_ADD_ABORT_OUTPUT');
await import('./focused/run-gc.mjs');
await completeRegression('NODE_COMPAT_ADD_ABORT_OUTPUT',admission);
