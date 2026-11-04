// Future approved entry only; preparing this file does not run componentization.
import {tracePreflight} from './preflight.mjs';
const admission=await tracePreflight();
const {runTraceGate}=await import('./component-driver.mjs');
await runTraceGate(admission);
