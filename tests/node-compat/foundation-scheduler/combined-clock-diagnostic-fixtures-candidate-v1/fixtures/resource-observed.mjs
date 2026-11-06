// UNCOMPILED/UNEXECUTED. Requires a genuine separate diagnostic native generation.
// Same component/linear memory. Only the real snapshot API is used.
import lifecycle from 'starling:test-clock-lifecycle';
import * as resource from '../../combined-clock-lifecycle-candidate-v2/fixtures/resource.mjs';
const native = () => JSON.stringify(lifecycle.snapshot());
export function inspect() {
  return JSON.stringify({schemaVersion: 1, kind: 'private-resource-inspect-v1',
    resourceRaw: resource.inspect(), nativeRaw: native()});
}
export async function run(caseId) {
  const beforeNativeRaw = native();
  const resourceRaw = await resource.run(caseId);
  const afterNativeRaw = native();
  return JSON.stringify({schemaVersion: 1, kind: 'private-resource-run-v1', caseId,
    resourceRaw, beforeNativeRaw, afterNativeRaw});
}
export async function validate() {
  const beforeNativeRaw = native();
  const resourceRaw = await resource.validate();
  const afterNativeRaw = native();
  return JSON.stringify({schemaVersion: 1, kind: 'private-resource-wrapper-v1',
    resourceRaw, beforeNativeRaw, afterNativeRaw});
}
// This export observes the PRIOR export boundary. A snapshot inside run cannot.
export function snapshot() { return native(); }
