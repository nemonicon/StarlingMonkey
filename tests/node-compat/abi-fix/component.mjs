// These u32 results are ordinary nonnegative JS Numbers. No s32 carrier is used.
export function directU32(value) { return value; }
export function constantHigh() { return 0x80000000; }
export function constantMax() { return 0xffffffff; }
export function computedU32(value) { return (value + 0x80000000) >>> 0; }
export function directS32(value) { return value; }
export function constantNegative() { return -2147483648; }
export function computedS32(value) { return (value * 3) | 0; }
export function directF32(value) { return value; }
export function directF64(value) { return value; }
export function listU32(values) { return new Uint32Array(values); }
export function recordU32(value) { return { ...value, values: new Uint32Array(value.values) }; }
export function resultU32(ok, value) { if (ok) return value; throw value; }
export function describe(value) {
  return JSON.stringify({ value, computed: computedU32(value), max: constantMax(), negative: constantNegative() });
}
