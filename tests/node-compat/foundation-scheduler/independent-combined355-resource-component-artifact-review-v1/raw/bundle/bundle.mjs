import { Buffer } from "node:buffer";
// tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/fixtures/resource.mjs
const initial = {
	timerCallbacks: 0,
	startedCases: 0,
	completedCases: 0
};
const count = {
	inspect: 0,
	run: 0,
	validate: 0,
	timerCallbacks: 0,
	startedCases: 0,
	completedCases: 0
};
const initDenials = [];
for (const name of ["setTimeout", "setInterval"]) {
	let error;
	try {
		globalThis[name](() => {}, 0);
	} catch (value) {
		error = value;
	}
	initDenials.push({
		name,
		installed: typeof globalThis[name] === "function",
		typeError: error instanceof TypeError,
		message: error instanceof Error ? error.message : null
	});
}
let sequence = 0;
const ids = [];
function check(v, m) {
	if (!v) throw new Error("RESOURCE_TIMER_CHECK:" + m);
}
function pressure() {
	let checksum = 0;
	for (let i = 0; i < 8; i++) {
		const b = Buffer.from("c3a92201", "hex");
		check(b.length === 4 && b[0] === 195 && b[3] === 1, "valid native Buffer pressure bytes");
		checksum = checksum + b[0] + b[1] + b[2] + b[3] >>> 0;
	}
	return checksum;
}
function remember(id) {
	check(Number.isInteger(id) && id > 0, "positive finite timer ID");
	check(!ids.includes(id), "no timer ID reuse within retained module");
	ids.push(id);
	return id;
}
function delay() {
	return new Promise((resolve) => remember(setTimeout(() => {
		count.timerCallbacks++;
		resolve();
	}, 0)));
}
function snapshot() {
	return {
		initial: { ...initial },
		counters: { ...count },
		registeredIds: [...ids],
		ownPendingNativeHandleCountInstrumented: false,
		hostResourceTableObserved: false,
		resetCalled: false
	};
}
function inspect() {
	count.inspect++;
	check(initDenials.every((r) => r.installed && r.typeError && r.message.includes(r.name + " can only be used during request handling")), "genuine installed timer INIT refusal");
	return JSON.stringify({
		schemaVersion: 1,
		kind: "scheduler-resource-inspect-v1",
		initDenials,
		state: snapshot(),
		snapshotHasLiveTimerRequested: false,
		initStateGuardSourceCoupled: true
	});
}
async function run(caseId) {
	count.run++;
	count.startedCases++;
	const current = ++sequence, events = [], before = snapshot();
	let result;
	check(Number.isInteger(caseId) && caseId >= 0 && caseId < 7, "finite seven ordinary cases");
	if (caseId === 0) {
		let id;
		const done = new Promise((resolve) => {
			id = remember(setTimeout(function(value) {
				count.timerCallbacks++;
				events.push({
					kind: "one-shot",
					value: value.token,
					strictReceiverNull: this === null
				});
				resolve();
			}, 0, { token: "queued-" + current }));
		});
		const pressureChecksum = pressure();
		await done;
		await delay();
		check(events.length === 1 && events[0].value === "queued-" + current, "one-shot full argument value");
		result = {
			id,
			pressureChecksum,
			events
		};
	} else if (caseId === 1) {
		let fired = 0;
		const id = remember(setTimeout(() => {
			count.timerCallbacks++;
			fired++;
		}, 0));
		clearTimeout(id);
		clearTimeout(id);
		await delay();
		check(fired === 0, "queued clear never dispatches");
		result = {
			id,
			fired,
			doubleClear: true
		};
	} else if (caseId === 2) {
		let id, ticks = 0;
		await new Promise((resolve) => {
			id = remember(setInterval(() => {
				count.timerCallbacks++;
				ticks++;
				events.push(ticks);
				if (ticks === 3) {
					clearInterval(id);
					clearInterval(id);
					resolve();
				}
			}, 0));
		});
		await delay();
		check(ticks === 3, "self-cleared interval never reschedules");
		result = {
			id,
			ticks,
			events
		};
	} else if (caseId === 3) {
		let victim, outer, victimCalls = 0;
		await new Promise((resolve) => {
			outer = remember(setTimeout(() => {
				count.timerCallbacks++;
				clearTimeout(victim);
				events.push("outer");
				resolve();
			}, 0));
			victim = remember(setTimeout(() => {
				count.timerCallbacks++;
				victimCalls++;
			}, 0));
		});
		await delay();
		check(victimCalls === 0, "nested queued cancellation");
		result = {
			outer,
			victim,
			victimCalls,
			events
		};
	} else if (caseId === 4) {
		let id, reads;
		await new Promise((resolve) => {
			id = remember(setTimeout(function(value) {
				count.timerCallbacks++;
				clearTimeout(id);
				const pressureChecksum = pressure();
				reads = {
					token: value.token,
					pressureChecksum
				};
				resolve();
			}, 0, { token: "active-" + current }));
		});
		await delay();
		check(reads.token === "active-" + current, "rooted active argv survives self-clear and public pressure");
		result = {
			id,
			...reads,
			combinedOwnersOnly: true,
			soleTemporaryRootProved: false
		};
	} else if (caseId === 5) {
		let caught;
		await new Promise((resolve) => remember(setTimeout(() => {
			count.timerCallbacks++;
			const error = /* @__PURE__ */ new Error("RESOURCE_HANDLED_CALLBACK");
			try {
				throw error;
			} catch (value) {
				caught = {
					same: value === error,
					message: value.message
				};
			}
			resolve();
		}, 0)));
		await delay();
		check(caught.same && caught.message === "RESOURCE_HANDLED_CALLBACK", "handled callback positive control");
		result = caught;
	} else {
		const cleared = [];
		let fired = 0;
		for (let i = 0; i < 32; i++) {
			const id = remember(setTimeout(() => {
				count.timerCallbacks++;
				fired++;
			}, 0));
			cleared.push(id);
			clearTimeout(id);
		}
		await delay();
		check(fired === 0, "bounded batch retires before dispatch");
		result = {
			cleared,
			fired,
			allocationFailureInjected: false
		};
	}
	count.completedCases++;
	return JSON.stringify({
		schemaVersion: 1,
		kind: "scheduler-resource-run-v1",
		caseId,
		current,
		completed: true,
		result,
		before,
		after: snapshot(),
		nativeResourceCountsObserved: false,
		hostClockValuesUsedAsOracle: false
	});
}
async function validate() {
	count.validate++;
	const before = JSON.parse(inspect()), records = [];
	for (let id = 0; id < 7; id++) records.push(JSON.parse(await run(id)));
	return JSON.stringify({
		schemaVersion: 1,
		kind: "scheduler-resource-within-export-v1",
		before,
		records,
		after: JSON.parse(inspect()),
		withinOneOuterExport: true,
		separateHostCallInterleavingProved: false,
		resetOrReuseProved: false
	});
}
export { inspect, run, validate };
