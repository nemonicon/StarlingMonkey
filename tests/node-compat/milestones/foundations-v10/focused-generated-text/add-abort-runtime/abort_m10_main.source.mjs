import __smBuiltin0, * as events from "node:events";
// tests/node-compat/foundation-add-abort/production-native-m0.10/require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	const events = __smBuiltin0;
	const canonical = __smBuiltin0;
	module.exports = function inspectCommonJS() {
		let call, newCall;
		try {
			events.once();
		} catch (error) {
			call = error.code;
		}
		try {
			new events.EventEmitterAsyncResource();
		} catch (error) {
			newCall = error.code;
		}
		return {
			same: events === canonical,
			constructorAlias: events.EventEmitter === events,
			defaultProperty: typeof events.default,
			addAbortListenerType: typeof events.addAbortListener,
			errorMonitorType: typeof events.errorMonitor,
			rejectedCall: call,
			rejectedConstruction: newCall
		};
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var require_cjs_native_profile_default = __smModule.exports;
// tests/node-compat/foundation-add-abort/production-native-m0.10/public-cases.mjs
function assert(value, message) {
	if (!value) throw new Error(message ?? "Assertion failed");
}
assert.equal = (a, b, message) => assert(Object.is(a, b), message ?? `Expected ${String(b)}, got ${String(a)}`);
assert.notEqual = (a, b, message) => assert(!Object.is(a, b), message ?? "Values must differ");
assert.deepEqual = (a, b, message) => assert(JSON.stringify(a) === JSON.stringify(b), message ?? `Different observations: ${JSON.stringify(a)} vs ${JSON.stringify(b)}`);
function caught(fn) {
	try {
		fn();
	} catch (error) {
		return error;
	}
	throw new Error("Expected throw");
}
const errorShape = (error) => ({
	name: error?.name ?? null,
	code: error?.code ?? null
});
async function publicCases(events) {
	const addAbortListener = events.addAbortListener, disposeSymbol = Symbol.dispose;
	assert.equal(typeof disposeSymbol, "symbol");
	const cases = [];
	async function test(name, run) {
		cases.push({
			name,
			observations: await run()
		});
	}
	await test("normalized disposable resource contract", () => {
		const c = new AbortController(), r = addAbortListener(c.signal, () => {}), d = Object.getOwnPropertyDescriptor(r, disposeSymbol);
		const value = {
			nullPrototype: Object.getPrototypeOf(r) === null,
			onlyDisposeKey: Reflect.ownKeys(r).length === 1 && Reflect.ownKeys(r)[0] === disposeSymbol,
			enumerable: d.enumerable,
			writable: d.writable,
			configurable: d.configurable,
			length: d.value.length,
			noFunctionPrototype: !Object.hasOwn(d.value, "prototype"),
			then: typeof r.then
		};
		assert.deepEqual(value, {
			nullPrototype: true,
			onlyDisposeKey: true,
			enumerable: true,
			writable: true,
			configurable: true,
			length: 0,
			noFunctionPrototype: true,
			then: "undefined"
		});
		r[disposeSymbol]();
		return value;
	});
	await test("signal validation precedes listener validation", () => {
		const rows = [];
		for (const [label, signal] of [
			["undefined", void 0],
			["null", null],
			["boolean", true],
			["number", 1],
			["string", "signal"],
			["symbol", Symbol("signal")],
			["bigint", 1n],
			["plain object", {}],
			["array", []],
			["function with aborted property", Object.assign(function signal() {}, { aborted: true })]
		]) {
			const error = caught(() => addAbortListener(signal, null));
			assert.equal(error.name, "TypeError");
			assert.equal(error.code, "ERR_INVALID_ARG_TYPE");
			assert(error.message.includes("signal"));
			rows.push({
				label,
				...errorShape(error)
			});
		}
		const controller = new AbortController();
		for (const [label, listener] of [
			["undefined", void 0],
			["null", null],
			["number", 1],
			["object", {}]
		]) {
			const error = caught(() => addAbortListener(controller.signal, listener));
			assert.equal(error.code, "ERR_INVALID_ARG_TYPE");
			assert(error.message.includes("listener"));
			rows.push({
				label: `listener ${label}`,
				...errorShape(error)
			});
		}
		let handleEventReads = 0;
		const listenerObject = { get handleEvent() {
			handleEventReads++;
			throw new Error("unexpected handleEvent read");
		} };
		assert.equal(caught(() => addAbortListener(controller.signal, listenerObject)).code, "ERR_INVALID_ARG_TYPE");
		assert.equal(handleEventReads, 0);
		return {
			rows,
			handleEventReads
		};
	});
	await test("aborted getter read follows listener validation and preserves thrown value", () => {
		const marker = {}, reads = [];
		const fake = { get aborted() {
			reads.push("get aborted");
			throw marker;
		} };
		const invalid = caught(() => addAbortListener(fake, null));
		assert.equal(invalid.code, "ERR_INVALID_ARG_TYPE");
		assert(invalid.message.includes("listener"));
		assert.deepEqual(reads, []);
		assert.equal(caught(() => addAbortListener(fake, () => {})), marker);
		assert.deepEqual(reads, ["get aborted"]);
		let hasCalls = 0;
		const hasMarker = {}, proxy = new Proxy({}, { has(target, key) {
			hasCalls++;
			assert.equal(key, "aborted");
			throw hasMarker;
		} });
		assert.equal(caught(() => addAbortListener(proxy, null)), hasMarker);
		assert.equal(hasCalls, 1);
		return {
			invalidListenerCheckedBeforeAbortedRead: true,
			getterExceptionIdentity: true,
			getterReads: reads,
			hasExceptionIdentity: true,
			hasCalls
		};
	});
	await test("structural fake signal calls and disposer method lookup", () => {
		const calls = [];
		let listener;
		const target = {
			get aborted() {
				calls.push("get aborted");
				return false;
			},
			get addEventListener() {
				calls.push("get addEventListener");
				return function(type, callback, options) {
					assert.equal(this, fake);
					assert.equal(type, "abort");
					listener = callback;
					assert.equal(Object.getPrototypeOf(options), null);
					assert.equal(options.once, true);
					calls.push("call addEventListener:abort:once");
				};
			},
			get removeEventListener() {
				calls.push("get original removeEventListener");
				return () => {
					calls.push("original removal");
				};
			}
		};
		const fake = new Proxy(target, { has(object, key) {
			calls.push(`has:${String(key)}`);
			return Reflect.has(object, key);
		} });
		const callback = () => {};
		const resource = addAbortListener(fake, callback);
		assert.equal(listener, callback);
		Object.defineProperty(target, "removeEventListener", {
			configurable: true,
			value: function(type, callback) {
				assert.equal(this, fake);
				assert.equal(type, "abort");
				assert.equal(callback, listener);
				calls.push("replacement removal");
			}
		});
		assert.equal(resource[disposeSymbol](), void 0);
		assert.equal(resource[disposeSymbol](), void 0);
		assert.deepEqual(calls, [
			"has:aborted",
			"get aborted",
			"get addEventListener",
			"call addEventListener:abort:once",
			"replacement removal",
			"replacement removal"
		]);
		const missingAdd = caught(() => addAbortListener({ aborted: false }, () => {}));
		assert.equal(missingAdd.name, "TypeError");
		assert.equal(missingAdd.code, void 0);
		return {
			calls,
			deferredRemovalReadsCurrentMethod: true,
			repeatedFakeDisposalRepeatsRemoval: true,
			missingAddEventListener: errorShape(missingAdd),
			scope: "Public structural acceptance; no private option symbol or listener storage is inspected."
		};
	});
	await test("already-aborted structural object schedules without event methods", async () => {
		const order = [], receiver = [];
		const fake = {
			get aborted() {
				order.push("get aborted");
				return {};
			},
			get addEventListener() {
				throw new Error("unexpected addEventListener read");
			},
			get removeEventListener() {
				throw new Error("unexpected removeEventListener read");
			}
		};
		order.push("before registration");
		const resource = addAbortListener(fake, function(...args) {
			order.push("listener");
			receiver.push({
				undefinedThis: this === void 0,
				argumentCount: args.length
			});
		});
		resource[disposeSymbol]();
		resource[disposeSymbol]();
		order.push("after dispose");
		await Promise.resolve();
		order.push("after microtask checkpoint");
		assert.deepEqual(order, [
			"before registration",
			"get aborted",
			"after dispose",
			"listener",
			"after microtask checkpoint"
		]);
		assert.deepEqual(receiver, [{
			undefinedThis: true,
			argumentCount: 0
		}]);
		return {
			order,
			receiver,
			queuedCallbackUnaffectedByDisposal: true
		};
	});
	await test("fresh signal callback is synchronous with signal receiver and Event", () => {
		const controller = new AbortController(), order = [], details = [];
		addAbortListener(controller.signal, function(...args) {
			const event = args[0];
			order.push("listener");
			details.push({
				signalThis: this === controller.signal,
				argumentCount: args.length,
				eventInstance: event instanceof Event,
				type: event.type,
				targetIsSignal: event.target === controller.signal,
				currentTargetIsSignal: event.currentTarget === controller.signal,
				abortedDuringCallback: controller.signal.aborted,
				reasonDuringCallback: controller.signal.reason,
				isTrusted: event.isTrusted,
				cancelable: event.cancelable
			});
		});
		order.push("before abort");
		controller.abort("first reason");
		order.push("after abort");
		controller.abort("second reason");
		controller.signal.dispatchEvent(new Event("abort"));
		assert.deepEqual(order, [
			"before abort",
			"listener",
			"after abort"
		]);
		assert.equal(details.length, 1);
		assert.equal(details[0].signalThis, true);
		assert.equal(details[0].argumentCount, 1);
		assert.equal(details[0].eventInstance, true);
		assert.equal(details[0].targetIsSignal, true);
		assert.equal(details[0].currentTargetIsSignal, true);
		assert.equal(details[0].abortedDuringCallback, true);
		assert.equal(details[0].reasonDuringCallback, "first reason");
		return {
			order,
			details,
			onceAcrossRepeatedAbortAndManualEvent: true
		};
	});
	await test("already-aborted signal callback is a zero-argument microtask despite disposal", async () => {
		const controller = new AbortController(), order = [], details = [];
		controller.abort("already");
		queueMicrotask(() => order.push("earlier queued microtask"));
		order.push("before registration");
		addAbortListener(controller.signal, function(...args) {
			order.push("listener");
			details.push({
				undefinedThis: this === void 0,
				argumentCount: args.length
			});
		})[disposeSymbol]();
		queueMicrotask(() => order.push("later queued microtask"));
		order.push("after registration/dispose");
		await Promise.resolve();
		order.push("await continuation");
		assert.deepEqual(order, [
			"before registration",
			"after registration/dispose",
			"earlier queued microtask",
			"listener",
			"later queued microtask",
			"await continuation"
		]);
		assert.deepEqual(details, [{
			undefinedThis: true,
			argumentCount: 0
		}]);
		return {
			order,
			details,
			queuedCallbackUnaffectedByDisposal: true
		};
	});
	await test("stopImmediatePropagation skips ordinary listeners but not protected registrations", () => {
		const controller = new AbortController(), order = [];
		controller.signal.addEventListener("abort", (event) => {
			order.push("ordinary stopper");
			event.stopImmediatePropagation();
		});
		addAbortListener(controller.signal, (event) => {
			order.push("protected one");
			event.stopImmediatePropagation();
		});
		controller.signal.addEventListener("abort", () => order.push("ordinary later"));
		addAbortListener(controller.signal, () => order.push("protected two"));
		controller.abort();
		assert.deepEqual(order, [
			"ordinary stopper",
			"protected one",
			"protected two"
		]);
		return { order };
	});
	await test("fresh disposal is effect-idempotent and can remove a later listener during dispatch", () => {
		const disposed = new AbortController();
		let disposedCalls = 0;
		const resource = addAbortListener(disposed.signal, () => disposedCalls++);
		assert.equal(resource[disposeSymbol](), void 0);
		assert.equal(resource[disposeSymbol](), void 0);
		disposed.signal.dispatchEvent(new Event("abort"));
		disposed.abort();
		assert.equal(disposedCalls, 0);
		const controller = new AbortController(), order = [];
		let later;
		addAbortListener(controller.signal, () => {
			order.push("first listener");
			later[disposeSymbol]();
		});
		later = addAbortListener(controller.signal, () => order.push("disposed later listener"));
		controller.abort();
		later[disposeSymbol]();
		assert.deepEqual(order, ["first listener"]);
		return {
			disposedCalls,
			order,
			realSignalRemovalEffectIdempotent: true
		};
	});
	await test("manual abort event consumes once registration without changing signal state", () => {
		const controller = new AbortController(), callbacks = [];
		addAbortListener(controller.signal, function(event) {
			callbacks.push({
				signalThis: this === controller.signal,
				type: event.type,
				aborted: controller.signal.aborted,
				isTrusted: event.isTrusted
			});
		});
		const first = controller.signal.dispatchEvent(new Event("abort"));
		const beforeRealAbort = controller.signal.aborted;
		const second = controller.signal.dispatchEvent(new Event("abort"));
		controller.abort("real reason");
		assert.deepEqual(callbacks, [{
			signalThis: true,
			type: "abort",
			aborted: false,
			isTrusted: false
		}]);
		assert.equal(beforeRealAbort, false);
		assert.equal(controller.signal.aborted, true);
		return {
			callbacks,
			beforeRealAbort,
			realAbortState: controller.signal.aborted,
			dispatchReturnValues: [first, second]
		};
	});
	await test("manual event after already-aborted registration does not replace queued callback", async () => {
		const controller = new AbortController(), order = [];
		controller.abort();
		addAbortListener(controller.signal, (...args) => {
			order.push(`queued listener:${args.length}`);
		});
		controller.signal.dispatchEvent(new Event("abort"));
		order.push("after manual dispatch");
		await Promise.resolve();
		assert.deepEqual(order, ["after manual dispatch", "queued listener:0"]);
		return { order };
	});
	await test("registration inside real abort callback observes already-aborted microtask path", async () => {
		const controller = new AbortController(), order = [];
		addAbortListener(controller.signal, () => {
			order.push("first listener");
			addAbortListener(controller.signal, (...args) => order.push(`late listener:${args.length}`));
		});
		controller.abort();
		order.push("after abort");
		await Promise.resolve();
		order.push("after checkpoint");
		assert.deepEqual(order, [
			"first listener",
			"after abort",
			"late listener:0",
			"after checkpoint"
		]);
		return { order };
	});
	await test("duplicate protected registrations share one listener tuple and either disposer removes it", () => {
		const controller = new AbortController();
		let calls = 0;
		const callback = () => calls++;
		const first = addAbortListener(controller.signal, callback), second = addAbortListener(controller.signal, callback);
		assert.notEqual(first, second);
		second[disposeSymbol]();
		controller.abort();
		controller.signal.dispatchEvent(new Event("abort"));
		first[disposeSymbol]();
		second[disposeSymbol]();
		assert.equal(calls, 0);
		const other = new AbortController();
		let undisposedCalls = 0;
		const same = () => undisposedCalls++;
		addAbortListener(other.signal, same);
		addAbortListener(other.signal, same);
		other.abort();
		other.signal.dispatchEvent(new Event("abort"));
		assert.equal(undisposedCalls, 1);
		return {
			disposableObjectsDistinct: true,
			callsAfterOneDisposer: calls,
			undisposedDuplicateCalls: undisposedCalls
		};
	});
	await test("ordinary callback registered first is not upgraded to protected or once", () => {
		const stopped = new AbortController(), stoppedOrder = [];
		const callback = () => stoppedOrder.push("ordinary duplicate");
		stopped.signal.addEventListener("abort", (event) => {
			stoppedOrder.push("stopper");
			event.stopImmediatePropagation();
		});
		stopped.signal.addEventListener("abort", callback);
		addAbortListener(stopped.signal, callback);
		addAbortListener(stopped.signal, () => stoppedOrder.push("different protected callback"));
		stopped.abort();
		assert.deepEqual(stoppedOrder, ["stopper", "different protected callback"]);
		const repeated = new AbortController();
		let calls = 0;
		const ordinary = () => calls++;
		repeated.signal.addEventListener("abort", ordinary);
		const resource = addAbortListener(repeated.signal, ordinary);
		repeated.signal.dispatchEvent(new Event("abort"));
		repeated.signal.dispatchEvent(new Event("abort"));
		repeated.abort();
		assert.equal(calls, 3);
		resource[disposeSymbol]();
		repeated.signal.dispatchEvent(new Event("abort"));
		assert.equal(calls, 3);
		return {
			stoppedOrder,
			ordinaryFirstRemainsNonOnceCalls: calls,
			protectedDuplicateDoesNotReplaceExistingTupleFlags: true
		};
	});
	await test("protected callback registered first keeps its flags after an ordinary duplicate", () => {
		const controller = new AbortController(), order = [];
		controller.signal.addEventListener("abort", (event) => {
			order.push("stopper");
			event.stopImmediatePropagation();
		});
		const callback = () => order.push("protected callback");
		addAbortListener(controller.signal, callback);
		controller.signal.addEventListener("abort", callback);
		controller.abort();
		controller.signal.dispatchEvent(new Event("abort"));
		assert.deepEqual(order, [
			"stopper",
			"protected callback",
			"stopper"
		]);
		return {
			order,
			laterOrdinaryDuplicateDidNotRemoveProtectionOrOnce: true
		};
	});
	await test("queued callback return thenable is ignored", async () => {
		let calls = 0, thenReads = 0;
		const c = new AbortController();
		c.abort();
		addAbortListener(c.signal, () => {
			calls++;
			return { get then() {
				thenReads++;
				throw new Error("Must not assimilate queued return");
			} };
		})[disposeSymbol]();
		await Promise.resolve();
		assert.deepEqual([calls, thenReads], [1, 0]);
		return {
			calls,
			thenReads
		};
	});
	return cases;
}
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
function receiverCases(events) {
	const results = [];
	function rejected(name, fn) {
		const error = caught(fn);
		assert(error instanceof TypeError);
		assert.equal(error.code, void 0);
		results.push({
			name,
			nameOfError: error.name,
			code: null
		});
	}
	for (const [label, prototype] of [["EventTarget", EventTarget.prototype], ["AbortSignal", AbortSignal.prototype]]) {
		rejected(label + ".prototype.addEventListener", () => Reflect.apply(EventTarget.prototype.addEventListener, prototype, ["x", () => {}]));
		rejected(label + ".prototype.removeEventListener", () => Reflect.apply(EventTarget.prototype.removeEventListener, prototype, ["x", () => {}]));
		rejected(label + ".prototype.dispatchEvent", () => Reflect.apply(EventTarget.prototype.dispatchEvent, prototype, [new Event("x")]));
		const old = Object.getOwnPropertyDescriptor(prototype, "aborted");
		try {
			Object.defineProperty(prototype, "aborted", {
				configurable: true,
				value: false
			});
			rejected("structural addAbortListener " + label + ".prototype", () => events.addAbortListener(prototype, () => {}));
		} finally {
			if (old) Object.defineProperty(prototype, "aborted", old);
			else Reflect.deleteProperty(prototype, "aborted");
		}
	}
	let calls = 0, correctReceiver = true;
	const target = new EventTarget(), c = new AbortController();
	target.addEventListener("x", function() {
		calls++;
		correctReceiver &&= this === target;
	}, { once: true });
	target.dispatchEvent(new Event("x"));
	events.addAbortListener(c.signal, function() {
		calls++;
		correctReceiver &&= this === c.signal;
	});
	c.abort();
	assert.equal(calls, 2);
	assert.equal(correctReceiver, true);
	results.push({
		name: "initialized EventTarget and native-derived AbortSignal",
		calls,
		correctReceiver
	});
	return results;
}
function targetSymbolInfo() {
	const key = Symbol.dispose, d = Object.getOwnPropertyDescriptor(Symbol, "dispose");
	return {
		description: key?.description ?? null,
		registryKey: Symbol.keyFor(key) ?? null,
		sameAsNodeRegistry: key === Symbol.for("nodejs.dispose"),
		descriptor: {
			enumerable: d.enumerable,
			writable: d.writable,
			configurable: d.configurable
		}
	};
}
// tests/node-compat/foundation-add-abort/production-native-m0.10/component.mjs
let calls = 0;
let snapshotCallbacks = 0;
let snapshotThis = false;
let snapshotTarget = false;
const snapshotController = new AbortController();
const snapshotResource = events.addAbortListener(snapshotController.signal, function(event) {
	snapshotCallbacks++;
	snapshotThis = this === snapshotController.signal;
	snapshotTarget = event.currentTarget === snapshotController.signal;
});
function profileErrors() {
	const ErrorCtor = Error, TypeErrorCtor = TypeError, define = Object.defineProperty, keys = [
		"code",
		"module",
		"operation",
		"profile"
	];
	const old = keys.map((key) => Object.getOwnPropertyDescriptor(ErrorCtor.prototype, key));
	let hooks = 0, ambient = 0;
	const errors = [];
	try {
		for (const key of keys) define(ErrorCtor.prototype, key, {
			configurable: true,
			set() {
				hooks++;
				throw new ErrorCtor("inherited metadata hook");
			}
		});
		globalThis.Error = function() {
			ambient++;
		};
		globalThis.TypeError = function() {
			ambient++;
		};
		for (const [name, operation] of [
			["once-call", () => events.once()],
			["once-new", () => new events.once()],
			["on-call", () => events.on()],
			["on-new", () => new events.on()],
			["async-resource-call", () => events.EventEmitterAsyncResource()],
			["async-resource-new", () => new events.EventEmitterAsyncResource()],
			["invalid-signal", () => events.addAbortListener(null, () => {})]
		]) {
			let error;
			try {
				operation();
			} catch (value) {
				error = value;
			}
			if (!error) throw new ErrorCtor("Expected profile error " + name);
			errors.push({
				name,
				type: error.name,
				code: error.code,
				module: error.module,
				operation: error.operation,
				profile: error.profile,
				own: keys.every((key) => Object.hasOwn(error, key))
			});
		}
	} finally {
		globalThis.Error = ErrorCtor;
		globalThis.TypeError = TypeErrorCtor;
		for (let i = 0; i < keys.length; i++) if (old[i]) define(ErrorCtor.prototype, keys[i], old[i]);
		else Reflect.deleteProperty(ErrorCtor.prototype, keys[i]);
	}
	return {
		errors,
		hooks,
		ambient
	};
}
async function run() {
	calls++;
	try {
		const publicObserved = await publicCases(events), nested = nestedOnceCases(events), receivers = receiverCases(events);
		const snapshotBefore = snapshotCallbacks;
		snapshotController.signal.dispatchEvent(new Event("abort"));
		snapshotResource[Symbol.dispose]();
		return JSON.stringify({
			calls,
			publicCases: publicObserved,
			nestedOnceCases: nested,
			receiverCases: receivers,
			namespace: {
				names: Object.getOwnPropertyNames(events).sort(),
				defaultNamed: __smBuiltin0 === events.EventEmitter,
				canonicalCached: events === events,
				aliasValues: Object.keys(events).every((key) => events[key] === events[key]),
				defaultAlias: __smBuiltin0 === __smBuiltin0,
				then: typeof events.then,
				errorMonitorType: typeof events.errorMonitor,
				captureRejectionSymbol: events.captureRejectionSymbol === Symbol.for("nodejs.rejection"),
				defaultMaxListeners: events.defaultMaxListeners,
				captureRejections: events.captureRejections,
				usingDomains: events.usingDomains
			},
			commonJS: require_cjs_native_profile_default(),
			profileErrors: profileErrors(),
			symbol: targetSymbolInfo(),
			snapshot: {
				before: snapshotBefore,
				after: snapshotCallbacks,
				signalThis: snapshotThis,
				currentTarget: snapshotTarget,
				aborted: snapshotController.signal.aborted
			}
		});
	} catch (error) {
		return JSON.stringify({
			calls,
			failure: {
				name: error?.name ?? null,
				code: error?.code ?? null,
				message: String(error?.message ?? error)
			}
		});
	}
}
export { run };
