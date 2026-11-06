// tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/clock-snapshot.mjs
const initialization = {
	dateNow: Date.now(),
	jobs: 0,
	moduleEvaluations: 1
};
Promise.resolve().then(() => {
	initialization.jobs++;
});
let calls = 0;
function check(value, message) {
	if (!value) throw new Error("COMBINED_CLOCK_CHECK:" + message);
}
function readClock() {
	const dateNow = Date.now();
	const dateObject = /* @__PURE__ */ new Date();
	const performanceNow = performance.now();
	const timeOrigin = performance.timeOrigin;
	check(Number.isFinite(dateNow) && Number.isInteger(dateNow), "finite Date milliseconds");
	check(Number.isFinite(dateObject.getTime()), "finite Date object");
	check(Number.isFinite(performanceNow) && performanceNow >= 0, "finite monotonic elapsed");
	check(Number.isFinite(timeOrigin), "finite first-call origin");
	return {
		dateNow,
		dateObject: dateObject.getTime(),
		iso: dateObject.toISOString(),
		performanceNow,
		timeOrigin
	};
}
async function run() {
	calls++;
	check(initialization.jobs === 1, "initialization Promise job drained once");
	const before = readClock();
	let callbacks = 0;
	await new Promise((resolve) => setTimeout(() => {
		callbacks++;
		resolve();
	}, 1));
	const after = readClock();
	check(callbacks === 1, "single timer callback");
	check(after.performanceNow >= before.performanceNow, "same-instance monotonic elapsed");
	check(after.timeOrigin === before.timeOrigin, "stable origin within export");
	return JSON.stringify({
		schemaVersion: 1,
		kind: "combined-clock-snapshot-observation-v1",
		calls,
		initialization: { ...initialization },
		before,
		after,
		callbacks,
		elapsed: after.performanceNow - before.performanceNow,
		initPerformanceCalled: false,
		entropyRequested: false,
		resetCalled: false,
		nativeMonotonicOffsetObserved: false,
		hostClockValuesAreExactOracle: false
	});
}
export { run };
