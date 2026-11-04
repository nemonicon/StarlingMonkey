// Source-only entry: null fixed-production pins stop before harness imports.
import {verifyFollowonOff,requireFreshOutput,completeFollowon} from './preflight.mjs';
const admission=await verifyFollowonOff();
await requireFreshOutput('NODE_COMPAT_STREAM_WEB_OUTPUT');
await import('./runners/stream-web.mjs');
await completeFollowon('NODE_COMPAT_STREAM_WEB_OUTPUT',admission);
