// tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/fatal.mjs
async function run() {
	await new Promise(() => setTimeout(() => {
		throw new Error("RESOURCE_UNHANDLED_TIMER_CALLBACK");
	}, 0));
	return "unreachable";
}
export { run };
