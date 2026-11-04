// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_QUERYSTRING_OUTPUT');
const control=await configureHistoricalControl('querystring');
await import('./runners/querystring.mjs');
await completeModule('querystring','NODE_COMPAT_QUERYSTRING_OUTPUT',admission,control);
