// Shared workload for pinned Node, the native profile and Jco's actual adapter.
// No clocks, entropy, host capabilities, or retained operation results.
export const operations = ['hex-encode', 'hex-decode', 'byte-copy', 'utf8-encode', 'utf8-decode'];
export const sizes = [64, 4096, 65536, 524288];
export function iterationsFor(size) { return size === 64 ? 10000 : Math.max(2, Math.floor(1048576 / size)); }

export function fullChecksum(value) {
  let sum = 2166136261;
  const string = typeof value === 'string';
  for (let i = 0; i < value.length; i++) sum = Math.imul(sum ^ (string ? value.charCodeAt(i) : value[i]), 16777619) >>> 0;
  return sum;
}
export function fingerprint(value) {
  const length = value.length;
  const string = typeof value === 'string';
  const first = string ? value.charCodeAt(0) : value[0];
  const middle = string ? value.charCodeAt(length >>> 1) : value[length >>> 1];
  const last = string ? value.charCodeAt(length - 1) : value[length - 1];
  return (length ^ (first << 8) ^ (middle << 16) ^ last) >>> 0;
}
export function expectedRunChecksum(resultFingerprint, iterations) {
  let sum = 0;
  for (let i = 0; i < iterations; i++) sum = (sum + (resultFingerprint ^ i)) >>> 0;
  return sum;
}

export function createWorkload(Buffer) {
  let invoke;
  const asciiPattern = Array.from({ length: 95 }, (_, i) => String.fromCharCode(32 + ((i * 17 + 11) % 95))).join('');
  const hexPattern = Array.from(asciiPattern, c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');
  function bytes(size) {
    const raw = new Uint8Array(size);
    for (let i = 0; i < size; i++) raw[i] = asciiPattern.charCodeAt(i % 95);
    return Buffer.from(raw);
  }
  function setup(operation, size) {
    if (!operations.includes(operation) || !sizes.includes(size)) throw new Error('unadmitted benchmark operation or size');
    // Prepare ONLY the selected input, outside timed run(). Pattern repeat
    // avoids hundreds of thousands of tiny rope nodes in setup/peak RSS.
    // ASCII fixes the processed byte count; broad Unicode has separate tests.
    if (operation === 'hex-encode') {
      const source = bytes(size);
      invoke = () => source.toString('hex');
    } else if (operation === 'hex-decode') {
      const source = hexPattern.repeat(Math.ceil(size / 95)).slice(0, size * 2);
      invoke = () => Buffer.from(source, 'hex');
    } else if (operation === 'byte-copy') {
      const source = bytes(size);
      invoke = () => Buffer.from(source);
    } else if (operation === 'utf8-encode') {
      const source = asciiPattern.repeat(Math.ceil(size / 95)).slice(0, size);
      invoke = () => Buffer.from(source, 'utf8');
    } else if (operation === 'utf8-decode') {
      const source = bytes(size);
      invoke = () => source.toString('utf8');
    }
    return fullChecksum(invoke()) | 0;
  }
  function run(iterations) {
    if (!invoke || !Number.isInteger(iterations) || iterations < 1 || iterations > 1000000) throw new Error('benchmark must be set up with bounded iterations');
    let sum = 0;
    for (let i = 0; i < iterations; i++) sum = (sum + (fingerprint(invoke()) ^ i)) >>> 0;
    return sum | 0;
  }
  return { setup, run };
}
