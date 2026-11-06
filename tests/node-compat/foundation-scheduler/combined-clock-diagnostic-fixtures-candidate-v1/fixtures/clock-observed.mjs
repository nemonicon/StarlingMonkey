// UNCOMPILED/UNEXECUTED. Native offset is NOT exported by7aed.
import lifecycle from 'starling:test-clock-lifecycle';
import {run as observeClock} from '../../combined-clock-lifecycle-candidate-v2/fixtures/clock-snapshot.mjs';
const native = () => JSON.stringify(lifecycle.snapshot());
export async function run() {
  const beforeNativeRaw = native();
  const clockRaw = await observeClock();
  const afterNativeRaw = native();
  return JSON.stringify({schemaVersion: 1, kind: 'private-clock-observation-v1',
    clockRaw, beforeNativeRaw, afterNativeRaw});
}
export function snapshot() { return native(); }
