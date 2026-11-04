// Approved retry entry; inner body preserves all original host checks.
import {verifyRetrySource,requireSupportedFixtureOptions} from './verify-retry.mjs';
requireSupportedFixtureOptions(process.env); // Reject the known incompatible extra assertion before any host body is imported.
const source=await verifyRetrySource();
await import('./run-http-wasmtime-body.mjs');
await source.recheck();
