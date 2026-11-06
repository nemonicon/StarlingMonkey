// tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/init-fatal.mjs
setTimeout(() => {}, 0);
function run() {
	return "unreachable";
}
export { run };
