import __smBuiltin0, * as events from "node:events";
// tests/node-compat/foundation-events/checks.mjs
function eventsChecks(events) {
	const E = events.EventEmitter, output = [];
	const test = (name, run) => output.push({
		name,
		result: run()
	});
	const names = (value) => value.map((key) => typeof key === "symbol" ? `symbol:${key.description}` : key);
	const error = (run) => {
		try {
			run();
			return null;
		} catch (value) {
			return {
				name: value.name,
				code: value.code ?? null
			};
		}
	};
	test("namespace", () => ({
		names: Object.getOwnPropertyNames(events).sort(),
		defaultIdentity: events.default === E,
		staticIdentity: E.EventEmitter === E,
		types: [
			typeof events.errorMonitor,
			typeof events.captureRejectionSymbol,
			typeof events.defaultMaxListeners,
			typeof events.captureRejections,
			typeof events.usingDomains
		],
		errorMonitorKey: Symbol.keyFor(events.errorMonitor) ?? null,
		rejectionKey: Symbol.keyFor(events.captureRejectionSymbol),
		eventTargetSymbolTypes: [typeof E.kMaxEventTargetListeners, typeof E.kMaxEventTargetListenersWarned],
		eventTargetSymbolDescriptions: [E.kMaxEventTargetListeners.description, E.kMaxEventTargetListenersWarned.description],
		eventTargetSymbolKeys: [Symbol.keyFor(E.kMaxEventTargetListeners) ?? null, Symbol.keyFor(E.kMaxEventTargetListenersWarned) ?? null],
		defaultThen: E.then ?? null,
		namespaceThen: events.then ?? null
	}));
	test("listener-aliases", () => ({
		on: E.prototype.on === E.prototype.addListener,
		off: E.prototype.off === E.prototype.removeListener
	}));
	test("emit-receiver-arguments-return", () => {
		const e = new E(), payload = {};
		let result;
		e.on("x", function(...args) {
			result = [
				this === e,
				args[0] === payload,
				...args.slice(1)
			];
			return "ignored";
		});
		return [
			e.emit("missing"),
			e.emit("x", payload, 2, 3, 4, 5, 6),
			result
		];
	});
	test("prepend-once-order", () => {
		const e = new E(), trace = [];
		const a = () => trace.push("a"), b = () => trace.push("b"), c = () => trace.push("c");
		e.on("x", a).prependListener("x", b).prependOnceListener("x", c);
		e.emit("x");
		e.emit("x");
		return trace;
	});
	test("mutation-during-emit", () => {
		const e = new E(), trace = [];
		let first = true;
		const b = () => trace.push("b"), c = () => trace.push("c");
		e.on("x", () => {
			trace.push("a");
			if (first) {
				first = false;
				e.off("x", b);
				e.on("x", c);
			}
		});
		e.on("x", b);
		e.emit("x");
		e.emit("x");
		return trace;
	});
	test("new-listener-before-insert", () => {
		const e = new E(), trace = [];
		let nested = false;
		function original() {
			trace.push("original");
		}
		e.on("newListener", (type, listener) => {
			if (type === "x") {
				trace.push(`new:${listener === original}`);
				if (!nested) {
					nested = true;
					e.on("x", () => trace.push("nested"));
				}
			}
		});
		e.once("x", original);
		e.emit("x");
		return trace;
	});
	test("remove-latest-duplicate", () => {
		const e = new E(), trace = [];
		function f() {
			trace.push("f");
		}
		function g() {
			trace.push("g");
		}
		e.on("x", f).on("x", g).on("x", f);
		e.removeListener("x", f);
		e.emit("x");
		return trace;
	});
	test("remove-once-original-and-wrapper", () => {
		const e = new E(), trace = [];
		function f() {}
		e.on("removeListener", (type, listener) => trace.push([type, listener === f]));
		e.once("x", f);
		const wrapper = e.rawListeners("x")[0];
		const copy = e.listeners("x");
		const identities = [copy[0] === f, wrapper.listener === f];
		copy.length = 0;
		e.removeListener("x", wrapper);
		e.once("x", f);
		e.removeListener("x", f);
		return {
			identities,
			trace,
			count: e.listenerCount("x")
		};
	});
	test("once-wrapper-manual-call", () => {
		const e = new E(), trace = [];
		function f(value) {
			trace.push([this === e, value]);
			return 42;
		}
		e.once("x", f);
		const wrapper = e.rawListeners("x")[0];
		return {
			trace,
			first: wrapper.call({}, "manual"),
			second: wrapper("again") ?? null,
			count: e.listenerCount("x")
		};
	});
	test("once-reentrant-emit", () => {
		const e = new E(), trace = [];
		e.once("x", () => {
			trace.push("once");
			e.emit("x");
		});
		e.on("x", () => trace.push("regular"));
		e.emit("x");
		return trace;
	});
	test("remove-all-lifo-and-symbols", () => {
		const e = new E(), trace = [], symbol = Symbol("s");
		function a() {}
		function b() {}
		e.on("removeListener", (type, listener) => trace.push([typeof type === "symbol" ? type.description : type, listener.name]));
		e.on("x", a).on("x", b).on(symbol, a);
		e.removeAllListeners();
		return {
			trace,
			names: names(e.eventNames()),
			count: e._eventsCount
		};
	});
	test("event-key-order-special-names", () => {
		const e = new E(), f = () => {}, a = Symbol("a"), b = Symbol("b");
		for (const key of [
			"__proto__",
			"constructor",
			"10",
			"2",
			"z",
			a,
			b
		]) e.on(key, f);
		return {
			names: names(e.eventNames()),
			nullPrototype: Object.getPrototypeOf(e._events) === null,
			count: e._eventsCount
		};
	});
	test("error-monitor-is-not-handler", () => {
		const e = new E(), expected = /* @__PURE__ */ new Error("same"), trace = [];
		let same;
		e.on(events.errorMonitor, (value) => trace.push(value === expected));
		try {
			e.emit("error", expected);
		} catch (value) {
			same = value === expected;
		}
		e.on("error", (value) => trace.push(["handled", value === expected]));
		e.emit("error", expected);
		return {
			same,
			trace
		};
	});
	test("unhandled-non-error-context", () => {
		const e = new E(), context = { value: 1 };
		let result;
		try {
			e.emit("error", context);
		} catch (value) {
			result = {
				name: value.name,
				code: value.code,
				context: value.context === context
			};
		}
		return result;
	});
	test("listener-throw-stops-dispatch", () => {
		const e = new E(), expected = /* @__PURE__ */ new Error("same"), trace = [];
		let same;
		e.on("x", () => {
			trace.push(1);
			throw expected;
		}).on("x", () => trace.push(2));
		try {
			e.emit("x");
		} catch (value) {
			same = value === expected;
		}
		return {
			trace,
			same
		};
	});
	test("listener-inspection-copies-and-filter", () => {
		const e = new E();
		function f() {}
		function g() {}
		e.on("x", f).once("x", f).on("x", g);
		events.getEventListeners(e, "x").pop();
		e.rawListeners("x").pop();
		return [
			e.listenerCount("x"),
			e.listenerCount("x", f),
			e.listenerCount("x", g),
			e.listenerCount("x", null),
			e.listenerCount("x", 7),
			events.listenerCount(e, "x")
		];
	});
	test("numeric-listener-thresholds", () => {
		const a = new E(), b = new E();
		events.setMaxListeners(7, a, b);
		const values = [events.getMaxListeners(a), b.getMaxListeners()];
		a.setMaxListeners(0);
		values.push(a.getMaxListeners());
		a.setMaxListeners(Infinity);
		values.push(String(a.getMaxListeners()));
		return values;
	});
	test("default-threshold-esm-snapshot", () => {
		const saved = E.defaultMaxListeners;
		try {
			E.defaultMaxListeners = 25;
			return [
				new E().getMaxListeners(),
				E.defaultMaxListeners,
				events.defaultMaxListeners
			];
		} finally {
			E.defaultMaxListeners = saved;
		}
	});
	test("mutable-default-static-named-snapshot", () => {
		const original = E.getMaxListeners, emitter = new E();
		try {
			E.getMaxListeners = () => 77;
			return [
				E.getMaxListeners(emitter),
				events.getMaxListeners(emitter),
				E.EventEmitter === E,
				Reflect.set(events, "getMaxListeners", () => 99)
			];
		} finally {
			E.getMaxListeners = original;
		}
	});
	test("legacy-subclass-mixin", () => {
		function Legacy() {
			E.call(this);
		}
		Object.setPrototypeOf(Legacy.prototype, E.prototype);
		const e = new Legacy(), receiver = {};
		E.call(receiver);
		E.prototype.on.call(receiver, "x", () => {});
		return [
			e instanceof E,
			e.emit("none"),
			receiver._eventsCount,
			Object.getPrototypeOf(receiver._events) === null
		];
	});
	test("modern-subclass", () => {
		class Child extends E {}
		const e = new Child();
		return [
			e instanceof E,
			e.on("x", () => {}) === e,
			e.emit("x")
		];
	});
	test("invalid-listener-and-limits", () => {
		const e = new E();
		return [
			error(() => e.on("x", null)),
			error(() => e.removeListener("x", 7)),
			error(() => e.setMaxListeners("3")),
			error(() => e.setMaxListeners(-1)),
			error(() => e.setMaxListeners(NaN)),
			error(() => new E({ captureRejections: 1 }))
		];
	});
	test("capture-disabled-normal-listener-return", () => {
		const e = new E({ captureRejections: false });
		let read = 0;
		e.on("x", () => ({ get then() {
			read++;
			throw new Error("must not inspect then");
		} }));
		return [
			e.emit("x"),
			read,
			E.captureRejections
		];
	});
	return output;
}
// tests/node-compat/foundation-events/native-checks.mjs
function nativeEventsChecks(events) {
	const E = events.EventEmitter, result = [];
	{
		const original = E.init, trace = [];
		try {
			E.init = function(options) {
				trace.push(options.value);
				return Reflect.apply(original, this, [options]);
			};
			const e = new E({ value: 7 });
			e.on("x", () => {});
			result.push({
				name: "mutable-init-with-named-snapshot",
				trace,
				count: e.listenerCount("x"),
				namedUnchanged: events.init === original
			});
		} finally {
			E.init = original;
		}
	}
	{
		const descriptor = Object.getOwnPropertyDescriptor(E, "defaultMaxListeners");
		let errorName;
		try {
			Object.defineProperty(E, "defaultMaxListeners", {
				configurable: true,
				get() {
					return 17;
				}
			});
		} catch (error) {
			errorName = error.name;
		}
		result.push({
			name: "protected-default-threshold-descriptor",
			configurable: descriptor.configurable,
			errorName,
			value: new E().getMaxListeners(),
			namedSnapshot: events.defaultMaxListeners
		});
	}
	{
		const e = new E();
		let called = 0;
		e.getMaxListeners = () => {
			called++;
			throw new Error("internal insertion must not call public method");
		};
		e.on("x", () => {}).on("x", () => {});
		result.push({
			name: "internal-threshold-does-not-call-public-override",
			count: e.listenerCount("x"),
			called
		});
	}
	{
		const saved = {
			apply: Reflect.apply,
			keys: Reflect.ownKeys,
			create: Object.create,
			bind: Function.prototype.bind,
			slice: Array.prototype.slice,
			push: Array.prototype.push,
			unshift: Array.prototype.unshift,
			splice: Array.prototype.splice,
			iterator: Array.prototype[Symbol.iterator],
			nan: Number.isNaN,
			error: globalThis.Error
		};
		const a = new E(), expected = /* @__PURE__ */ new Error("same"), trace = {
			calls: 0,
			sameError: false,
			max: null
		};
		const callback = () => {
			trace.calls++;
		};
		a.on("x", callback).on("x", callback);
		a.once("y", callback);
		const OriginalError = globalThis.Error;
		function poison() {
			throw new OriginalError("public intrinsic replacement must not run");
		}
		try {
			Reflect.apply = poison;
			Reflect.ownKeys = poison;
			Object.create = poison;
			Function.prototype.bind = poison;
			Array.prototype.slice = poison;
			Array.prototype.push = poison;
			Array.prototype.unshift = poison;
			Array.prototype.splice = poison;
			Array.prototype[Symbol.iterator] = poison;
			Number.isNaN = () => false;
			globalThis.Error = function ChangedError() {};
			a.emit("x");
			a.removeListener("x", callback);
			a.emit("y");
			a.setMaxListeners(0);
			trace.max = a.getMaxListeners();
			try {
				a.emit("error", expected);
			} catch (error) {
				trace.sameError = error === expected;
			}
			trace.names = a.eventNames().length;
			a.removeAllListeners();
			trace.remaining = a.eventNames().length;
		} finally {
			Reflect.apply = saved.apply;
			Reflect.ownKeys = saved.keys;
			Object.create = saved.create;
			Function.prototype.bind = saved.bind;
			Array.prototype.slice = saved.slice;
			Array.prototype.push = saved.push;
			Array.prototype.unshift = saved.unshift;
			Array.prototype.splice = saved.splice;
			Array.prototype[Symbol.iterator] = saved.iterator;
			Number.isNaN = saved.nan;
			globalThis.Error = saved.error;
		}
		result.push({
			name: "retained-language-primordials",
			...trace
		});
	}
	return result;
}
// tests/node-compat/foundation-events/prototype-checks.mjs
function prototypeChecks(events, { addAbortListenerSupported = false } = {}) {
	let deferred = 0;
	function expect(callback, code) {
		let error;
		try {
			callback();
		} catch (failure) {
			error = failure;
		}
		if (error?.code !== code) throw new Error(`Expected ${code}, got ${error?.name}: ${error?.code}`);
	}
	for (const name of addAbortListenerSupported ? [
		"on",
		"once",
		"EventEmitterAsyncResource"
	] : [
		"on",
		"once",
		"addAbortListener",
		"EventEmitterAsyncResource"
	]) {
		expect(() => events[name](), "ERR_SM_NODE_UNSUPPORTED");
		expect(() => new events[name](), "ERR_SM_NODE_UNSUPPORTED");
		deferred += 2;
	}
	for (const operation of [
		() => new events.EventEmitter({ captureRejections: true }),
		() => {
			events.EventEmitter.captureRejections = true;
		},
		() => events.getEventListeners(new EventTarget(), "x"),
		() => events.getMaxListeners(new EventTarget()),
		() => events.setMaxListeners(2, new EventTarget())
	]) {
		expect(operation, "ERR_SM_NODE_UNSUPPORTED");
		deferred++;
	}
	const listener = () => {};
	const e = new events.EventEmitter();
	e.setMaxListeners(0);
	for (let i = 0; i < 65536; i++) e.on("x", listener);
	expect(() => e.on("x", listener), "ERR_SM_NODE_LIMIT");
	if (e.listenerCount("x") !== 65536) throw new Error("Listener limit changed previous state");
	const names = new events.EventEmitter();
	for (let i = 0; i < 4096; i++) names.on("x" + i, listener);
	expect(() => names.on("extra", listener), "ERR_SM_NODE_LIMIT");
	if (names.eventNames().length !== 4096) throw new Error("Name limit changed previous state");
	const recursive = new events.EventEmitter();
	recursive.on("x", () => recursive.emit("x"));
	expect(() => recursive.emit("x"), "ERR_SM_NODE_LIMIT");
	recursive.removeAllListeners();
	if (recursive.emit("x") !== false) throw new Error("Depth unwind recovery");
	expect(() => new events.EventEmitter().on(7, listener), "ERR_SM_NODE_UNSUPPORTED");
	return {
		deferred,
		limits: 3,
		eventNameCoercionDeferred: true
	};
}
// tests/node-compat/foundation-events/native-require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	const bare = __smBuiltin0;
	const canonical = __smBuiltin0;
	module.exports = function inspectCommonJS(EventEmitter) {
		let callCode, constructCode;
		try {
			bare.once();
		} catch (error) {
			callCode = error.code;
		}
		try {
			new canonical.EventEmitterAsyncResource();
		} catch (error) {
			constructCode = error.code;
		}
		return {
			same: bare === canonical && bare === EventEmitter,
			constructorAlias: bare.EventEmitter === bare,
			defaultProperty: typeof bare.default,
			errorMonitorType: typeof bare.errorMonitor,
			rejectedCall: callCode,
			rejectedConstruction: constructCode
		};
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var native_require_cjs_native_profile_default = __smModule.exports;
// tests/node-compat/foundation-events/native-component.mjs
const snapshotEmitter = new events.EventEmitter();
let snapshotTicks = 0;
snapshotEmitter.on("tick", () => {
	snapshotTicks++;
});
snapshotEmitter.emit("tick");
let calls = 0;
async function run() {
	try {
		snapshotEmitter.emit("tick");
		return JSON.stringify({
			calls: ++calls,
			snapshotTicks,
			namespaceIdentity: await Promise.resolve(events) === events,
			cases: eventsChecks(events),
			nativeCases: nativeEventsChecks(events),
			profile: prototypeChecks(events, { addAbortListenerSupported: true }),
			commonJS: native_require_cjs_native_profile_default(events.EventEmitter)
		});
	} catch (error) {
		return JSON.stringify({ failure: {
			name: error.name,
			code: error.code,
			message: error.message,
			stack: error.stack
		} });
	}
}
export { run };
