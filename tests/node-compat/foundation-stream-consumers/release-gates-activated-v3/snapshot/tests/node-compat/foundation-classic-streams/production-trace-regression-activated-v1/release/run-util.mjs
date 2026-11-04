// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_UTIL_OUTPUT');
const control=await configureHistoricalControl('util');
await import('./runners/util.mjs');
await completeModule('util','NODE_COMPAT_UTIL_OUTPUT',admission,control);
