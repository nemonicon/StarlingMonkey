import { Buffer } from "node:buffer";
// \0allocation:private-workload
const sizes = [
	64,
	4096,
	524288
];
function createWorkload(Buffer) {
	const unsafe = Buffer.allocUnsafe, safe = Buffer.alloc, U8 = Uint8Array;
	function batch(operation, size, iterations) {
		if (!sizes.includes(size) || !Number.isInteger(iterations) || iterations < 0 || iterations > 1048576 || size * iterations > 67108864) throw new RangeError("Bounded allocation experiment inputs");
		if (operation === 4) {
			const a = unsafe(size), b = unsafe(size);
			if (!Buffer.isBuffer(a) || !Buffer.isBuffer(b) || a.buffer === b.buffer || a.byteOffset !== 0 || a.buffer.byteLength !== size) throw new Error("Fresh exact no-pool backing/brand");
			for (let i = 0; i < size; i++) if (a[i] !== 0 || b[i] !== 0) throw new Error("Expected adapter/profile zeroing");
			return (size ^ 1909039917) >>> 0;
		}
		let allocate;
		switch (operation) {
			case 0:
				allocate = unsafe;
				break;
			case 1:
				allocate = function(n) {
					return new unsafe(n);
				};
				break;
			case 2:
				allocate = safe;
				break;
			case 3:
				allocate = function(n) {
					return new U8(n);
				};
				break;
			case 5: {
				const reused = new U8(size);
				allocate = function() {
					return reused;
				};
				break;
			}
			default: throw new RangeError("Unknown allocation operation");
		}
		let checksum = 2166136261;
		for (let i = 0; i < iterations; i++) {
			const value = allocate(size);
			value[0] = i & 255;
			value[size - 1] = i * 17 + 3 & 255;
			checksum = Math.imul(checksum ^ value.length + value[0] + value[size - 1], 16777619) >>> 0;
		}
		return checksum >>> 0;
	}
	return { batch };
}
// \0allocation:private-entry
if (globalThis.Buffer !== Buffer) throw new Error("Private installed Buffer/global identity");
if (Buffer.isEncoding("base64")) throw new Error("Unexpected JS adapter");
const batch = createWorkload(Buffer).batch;
export { batch };
