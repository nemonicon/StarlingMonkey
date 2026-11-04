import { state } from 'starling:test-initializer-observation';
// Must already be 1 when content-module body starts, not just after its checkpoint.
const observedBeforeContentEvaluation = state.ticks;
export function run() {
  if (observedBeforeContentEvaluation !== 1 || state.ticks !== 1)
    throw new Error('initializer checkpoint must finish before content evaluation');
  return JSON.stringify({ observedBeforeContentEvaluation, ticks: state.ticks });
}
