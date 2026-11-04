// Source-only entry: null fixed-production pins stop before harness imports.
import {verifyFollowonOff,requireFreshOutput,completeFollowon} from './preflight.mjs';
const admission=await verifyFollowonOff();
await requireFreshOutput('NODE_COMPAT_STRICT_EVENT_OUTPUT');
await import('./runners/sync.mjs');
await completeFollowon('NODE_COMPAT_STRICT_EVENT_OUTPUT',admission);
