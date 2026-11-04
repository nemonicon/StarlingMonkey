// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_EVENTS_OUTPUT');
const control=await configureHistoricalControl('events');
await import('./runners/events.mjs');
await completeModule('events','NODE_COMPAT_EVENTS_OUTPUT',admission,control);
