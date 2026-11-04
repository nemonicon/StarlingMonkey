import * as events from "node:events";
// tests/node-compat/foundation-add-abort/production-native-m0.11/callback-return-cases.mjs
async function callbackReturnObservation(events) {
	let ordinary = 0, protectedSignal = 0, alreadyAborted = 0;
	const target = new EventTarget();
	target.addEventListener("observe", () => ({ get then() {
		ordinary++;
	} }));
	target.dispatchEvent(new Event("observe"));
	const fresh = new AbortController();
	events.addAbortListener(fresh.signal, () => ({ get then() {
		protectedSignal++;
	} }));
	fresh.abort();
	const already = new AbortController();
	already.abort();
	events.addAbortListener(already.signal, () => ({ get then() {
		alreadyAborted++;
	} }));
	await Promise.resolve();
	return {
		ordinary,
		protectedSignal,
		alreadyAborted
	};
}
// tests/node-compat/foundation-add-abort/production-native-m0.11/callback-return-component.mjs
async function run() {
	return JSON.stringify(await callbackReturnObservation(events));
}
export { run };
