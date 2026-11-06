// UNEXECUTED diagnostic entry. SAME component/linear memory as original cases.
// Future bundle policy must explicitly externalize this private native builtin.
import lifecycle from 'starling:test-clock-lifecycle';
export {inspect, run, validate} from '../../combined-clock-lifecycle-candidate-v2/fixtures/resource.mjs';
export function snapshot() { return JSON.stringify(lifecycle.snapshot()); }
