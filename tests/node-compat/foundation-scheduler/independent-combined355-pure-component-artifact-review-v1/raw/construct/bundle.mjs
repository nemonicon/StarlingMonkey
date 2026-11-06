import { Buffer } from "node:buffer";
// tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/pure.mjs
const initial = 0;
let calls = 0;
function run() {
	calls++;
	const value = Buffer.from("c3a92201", "hex");
	if (value.length !== 4) throw new Error("RESOURCE_PURE_BYTES");
	return JSON.stringify({
		schemaVersion: 1,
		initial,
		calls,
		hex: value.toString("hex"),
		timerRequested: false
	});
}
export { run };
