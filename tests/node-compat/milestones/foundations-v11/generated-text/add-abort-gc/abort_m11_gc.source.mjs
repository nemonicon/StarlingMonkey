import { Buffer } from "node:buffer";
import * as events from "node:events";
import { addAbortListener } from "node:events";
// tests/node-compat/foundation-add-abort/production-native-m0.11/public-cases.mjs
function assert(value, message) {
	if (!value) throw new Error(message ?? "Assertion failed");
}
assert.equal = (a, b, message) => assert(Object.is(a, b), message ?? `Expected ${String(b)}, got ${String(a)}`);
assert.notEqual = (a, b, message) => assert(!Object.is(a, b), message ?? "Values must differ");
assert.deepEqual = (a, b, message) => assert(JSON.stringify(a) === JSON.stringify(b), message ?? `Different observations: ${JSON.stringify(a)} vs ${JSON.stringify(b)}`);
function nestedOnceCases(events) {
	const cases = [];
	for (const mode of [
		"ordinary-once",
		"protected-once",
		"protected-after-stop"
	]) {
		const signal = new AbortController().signal, log = [], resources = [];
		let depth = 0, readded = false;
		function register() {
			if (mode === "ordinary-once") signal.addEventListener("abort", later, { once: true });
			else resources.push(events.addAbortListener(signal, later));
		}
		function earlier(event) {
			log.push("earlier:" + event.label);
			if (event.label !== "outer") return;
			depth++;
			const nested = new Event("abort");
			nested.label = "nested";
			signal.dispatchEvent(nested);
			depth--;
			log.push("earlier:after-nested");
			if (mode === "protected-after-stop") event.stopImmediatePropagation();
		}
		function later(event) {
			assert.equal(this, signal);
			log.push("later:" + event.label);
			if (!readded) {
				assert.equal(depth, 1);
				readded = true;
				register();
				log.push("later:readded");
			}
		}
		signal.addEventListener("abort", earlier);
		register();
		for (const label of [
			"outer",
			"second",
			"third"
		]) {
			const event = new Event("abort");
			event.label = label;
			signal.dispatchEvent(event);
		}
		assert.deepEqual(log, [
			"earlier:outer",
			"earlier:nested",
			"later:nested",
			"later:readded",
			"earlier:after-nested",
			"earlier:second",
			"later:second",
			"earlier:third"
		]);
		assert.equal(signal.aborted, false);
		for (const resource of resources) resource[Symbol.dispose]();
		cases.push({
			mode,
			log,
			laterInvocations: 2,
			laterRanInOuter: false,
			syntheticDispatchOnly: true,
			actualControllerAbortCalled: false
		});
	}
	const target = new EventTarget(), log = [];
	let first = true;
	const later = () => log.push("later");
	target.addEventListener("x", () => {
		log.push("earlier");
		if (first) {
			first = false;
			target.removeEventListener("x", later);
			target.addEventListener("x", later, { once: true });
		}
	});
	target.addEventListener("x", later, { once: true });
	target.dispatchEvent(new Event("x"));
	assert.deepEqual(log, ["earlier"]);
	target.dispatchEvent(new Event("x"));
	assert.deepEqual(log, [
		"earlier",
		"earlier",
		"later"
	]);
	cases.push({
		mode: "ordinary-remove-and-readd-control",
		log
	});
	return cases;
}
// tests/node-compat/foundation-add-abort/production-native-m0.11/gc-component.mjs
let calls = 0;
let snapshotCalls = 0;
const snapshot = new AbortController();
const snapshotResource = addAbortListener(snapshot.signal, () => snapshotCalls++);
function check(value, label) {
	if (!value) throw new Error(label);
}
function run() {
	calls++;
	let completed = 0, receiver = true, contextRestored = true, disposalCalls = 0;
	const order = [], c = new AbortController();
	let eventRef, later;
	c.signal.addEventListener("abort", function() {
		receiver &&= this === c.signal;
		order.push("ordinary");
	});
	addAbortListener(c.signal, function(event) {
		receiver &&= this === c.signal && event.currentTarget === c.signal;
		eventRef = event;
		order.push("protected");
		for (let i = 0; i < 8; i++) {
			check(Buffer.from("00017fff80", "hex").toString("hex") === "00017fff80", "valid native hex roundtrip");
			completed++;
		}
		const after = new AbortController();
		let afterCalls = 0;
		after.signal.addEventListener("abort", (event) => event.stopImmediatePropagation());
		const r = addAbortListener(after.signal, function(inner) {
			afterCalls++;
			receiver &&= this === after.signal && inner.currentTarget === after.signal;
			contextRestored &&= event.currentTarget === c.signal;
		});
		after.signal.dispatchEvent(new Event("abort"));
		check(afterCalls === 1, "post-GC protected registration");
		r[Symbol.dispose]();
		addAbortListener(after.signal, () => disposalCalls++)[Symbol.dispose]();
		after.signal.dispatchEvent(new Event("abort"));
		contextRestored &&= event.currentTarget === c.signal;
		later[Symbol.dispose]();
	});
	c.signal.addEventListener("abort", function() {
		receiver &&= this === c.signal;
		order.push("ordinary-once");
	}, { once: true });
	later = addAbortListener(c.signal, () => order.push("disposed-later"));
	c.signal.dispatchEvent(new Event("abort"));
	check(eventRef.currentTarget === null, "currentTarget cleared after dispatch");
	c.signal.dispatchEvent(new Event("abort"));
	check(completed === 8, "eight valid native roundtrips");
	check(receiver && contextRestored && disposalCalls === 0, "receiver/context/disposal retained");
	check(JSON.stringify(order) === JSON.stringify([
		"ordinary",
		"protected",
		"ordinary-once",
		"ordinary"
	]), "ordinary/protected/once order");
	const snapshotBefore = snapshotCalls;
	snapshot.signal.dispatchEvent(new Event("abort"));
	snapshotResource[Symbol.dispose]();
	return JSON.stringify({
		calls,
		completed,
		receiver,
		contextRestored,
		disposalCalls,
		order,
		snapshot: {
			before: snapshotBefore,
			after: snapshotCalls
		},
		nestedOnceCases: nestedOnceCases(events)
	});
}
export { run };
