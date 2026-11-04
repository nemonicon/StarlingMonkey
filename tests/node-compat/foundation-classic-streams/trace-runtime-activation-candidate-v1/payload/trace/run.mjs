import {tracePreflight} from './preflight.mjs';
const admission=await tracePreflight();
const {runTraceGate}=await import('./component-driver.mjs');
await runTraceGate(admission);
