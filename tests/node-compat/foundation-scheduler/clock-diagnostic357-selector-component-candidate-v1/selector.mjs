// UNCOMPILED/UNEXECUTED. A separate default-OFF diagnostic generation is mandatory.
import lifecycle from 'starling:test-clock-lifecycle';
// No INIT calls. The ordinary scalar lowering's synchronous prefix has interest1
// and loopRunning=false; this is NOT a natural-loop all-invalid settlement test.
export function run(count) { return JSON.stringify(lifecycle.probeAllInvalidV2(count)); }
export function snapshot() { return JSON.stringify(lifecycle.snapshot()); }
export function clockState() { return JSON.stringify(lifecycle.clockStateV2()); }
