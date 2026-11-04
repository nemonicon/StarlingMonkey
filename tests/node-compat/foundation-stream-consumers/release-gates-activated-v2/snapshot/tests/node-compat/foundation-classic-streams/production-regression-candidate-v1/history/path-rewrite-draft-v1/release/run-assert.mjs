// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_ASSERT_OUTPUT');
const control=await configureHistoricalControl('assert');
await import('./runners/assert.mjs');
await completeModule('assert','NODE_COMPAT_ASSERT_OUTPUT',admission,control);
