// Source-only entry: actual null pins reject before any runner/loader/output.
import {verifyReleaseOff,requireFreshOutput,configureHistoricalControl,completeModule} from './preflight.mjs';
const admission=await verifyReleaseOff();
await requireFreshOutput('NODE_COMPAT_STRING_DECODER_OUTPUT');
const control=await configureHistoricalControl('string-decoder');
await import('./runners/string-decoder.mjs');
await completeModule('string-decoder','NODE_COMPAT_STRING_DECODER_OUTPUT',admission,control);
