// Read-only source/native/tool admission; no guest exports or target host.
import {executionPreflight} from '../measurement-execution-activated-v2/runtime-preflight.mjs';
const observations = [];
for (const variant of ['benchmark-classic-on', 'benchmark-classic-off']) {
  const admitted = await executionPreflight({variant});
  await admitted.recheck();
  observations.push({variant, engineSha256: admitted.pin.engineSha256,
    metadataSha256: admitted.pin.metadataSha256,
    freezeReceiptSha256: admitted.pin.freezeReceiptSha256,
    pairSha256: admitted.pairSha256});
}
console.log(JSON.stringify({state: 'COMMON_BYTE_PAIR_SOURCE_PREFLIGHTS_PASSED',
  observations, guestExecuted: false, timingAllowed: false}));
