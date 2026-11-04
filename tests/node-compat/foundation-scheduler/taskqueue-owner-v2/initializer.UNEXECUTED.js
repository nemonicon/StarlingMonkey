// Classic INIT_SCRIPT_GLOBAL fixture, for a NEW scheduler engine only.
// Existing defineBuiltinModule supplies the observation record; no new global.
const state = { ticks: 0 };
defineBuiltinModule('starling:test-initializer-observation', { state, default: state });
import('starling:test-initializer-ticks').then(({ nextTick }) => {
  nextTick(() => { ++state.ticks; });
});
