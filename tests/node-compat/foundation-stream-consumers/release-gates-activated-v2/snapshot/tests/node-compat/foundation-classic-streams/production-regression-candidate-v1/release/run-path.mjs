// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_PATH_OUTPUT');
const control=await configureHistoricalControl('path');
await import('./runners/path.mjs');
await completeModule('path','NODE_COMPAT_PATH_OUTPUT',admission,control);
