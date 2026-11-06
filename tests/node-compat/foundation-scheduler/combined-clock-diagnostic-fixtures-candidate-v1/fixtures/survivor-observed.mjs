// UNCOMPILED/UNEXECUTED. Public cancelled tasks are erased, not invalid queued rows.
import lifecycle from 'starling:test-clock-lifecycle';
import {run as observeSurvivor} from '../../combined-clock-lifecycle-candidate-v2/fixtures/surviving-interest.mjs';
const native = () => JSON.stringify(lifecycle.snapshot());
export async function run() {
  const beforeNativeRaw = native();
  const survivorRaw = await observeSurvivor();
  const afterNativeRaw = native();
  return JSON.stringify({schemaVersion: 1, kind: 'private-survivor-observation-v1',
    survivorRaw, beforeNativeRaw, afterNativeRaw});
}
export function snapshot() { return native(); }
