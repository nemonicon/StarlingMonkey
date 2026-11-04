import __smBuiltin0, * as util from "node:util";
import __smBuiltin2, * as types from "node:util/types";
import __smBuiltin1, * as sys from "node:sys";
// tests/node-compat/foundation-util/native-require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	module.exports = {
		util: __smBuiltin0,
		sys: __smBuiltin1,
		types: __smBuiltin2,
		canonical: __smBuiltin0
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var native_require_cjs_native_profile_default = __smModule.exports;
// tests/node-compat/foundation-util/component-cases.mjs
async function runComponentCases({ util, types, sys, predicateNames, features }) {
	let checks = 0;
	const observations = [];
	const check = (condition, label) => {
		checks++;
		if (!condition) throw new Error("UTIL_COMPONENT_ASSERT: " + label);
	};
	const errorOf = (fn) => {
		try {
			fn();
		} catch (error) {
			return error;
		}
		throw new Error("Expected throw");
	};
	const expectedSysNames = Object.keys(util).slice().sort();
	check(Object.keys(sys).slice().sort().join(",") === expectedSysNames.join(","), "sys names");
	check(sys !== util, "distinct sys namespace");
	check(sys.default === util.default, "shared sys default");
	check(util.types === types.default, "types default");
	for (const name of Object.keys(util).filter((name) => name !== "default")) {
		check(util[name] === util.default[name], "util named/default " + name);
		check(sys[name] === util[name], "sys named " + name);
	}
	check(util.TextEncoder === globalThis.TextEncoder && util.TextDecoder === globalThis.TextDecoder, "native web constructor identities");
	check(util.debug === util.debuglog, "debug alias");
	check(util.inspect.custom === Symbol.for("nodejs.util.inspect.custom"), "inspect symbol");
	check(util.promisify.custom === Symbol.for("nodejs.util.promisify.custom"), "promisify symbol");
	check(util.default.then === void 0 && util.types.then === void 0 && util.then === void 0, "safe namespace then reads");
	check(util.inspect.colors.grey === util.inspect.colors.gray, "palette alias");
	check(typeof util.inspect.colors.gray[0] === "number", "palette values");
	const encoded = new util.TextEncoder().encode("Aé🙂");
	observations.push({
		textEncoding: [...encoded],
		textDecoding: new util.TextDecoder().decode(encoded)
	});
	const fixtures = [
		["undefined", void 0],
		["null", null],
		["boolean", true],
		["number", 1],
		["nan", NaN],
		["string", "s"],
		["symbol", Symbol("s")],
		["bigint", 1n],
		["object", {}],
		["null-prototype", Object.create(null)],
		["array", []],
		["function", function() {}],
		["promise", Promise.resolve(1)],
		["boolean-box", Object(false)],
		["number-box", Object(1)],
		["string-box", Object("s")],
		["symbol-box", Object(Symbol("s"))],
		["bigint-box", Object(1n)],
		["date", /* @__PURE__ */ new Date(0)],
		["regexp", /x/u],
		["map", /* @__PURE__ */ new Map()],
		["set", /* @__PURE__ */ new Set()],
		["weakmap", /* @__PURE__ */ new WeakMap()],
		["weakset", /* @__PURE__ */ new WeakSet()],
		["error", /* @__PURE__ */ new Error("ordinary")]
	];
	for (const Constructor of [
		Boolean,
		Number,
		String,
		Symbol,
		BigInt,
		Date,
		RegExp,
		Map,
		Set,
		WeakMap,
		WeakSet,
		ArrayBuffer,
		DataView,
		Uint8Array
	]) fixtures.push([Constructor.name + ".prototype", Constructor.prototype], [Constructor.name + "-prototype-forgery", Object.create(Constructor.prototype)]);
	for (const Constructor of [
		Int8Array,
		Uint8Array,
		Uint8ClampedArray,
		Int16Array,
		Uint16Array,
		Int32Array,
		Uint32Array,
		Float32Array,
		Float64Array,
		BigInt64Array,
		BigUint64Array
	]) fixtures.push([Constructor.name, new Constructor(3)]);
	const ab = /* @__PURE__ */ new ArrayBuffer(12);
	fixtures.push(["ab", ab], ["dataview", new DataView(ab, 2, 4)]);
	class Subclass extends Uint8Array {}
	fixtures.push(["u8-subclass", new Subclass(2)]);
	if (features.sharedArrayBuffer) {
		const shared = new SharedArrayBuffer(8);
		fixtures.push(["sab", shared], ["sab-u8", new Uint8Array(shared)], ["sab-view", new DataView(shared)]);
	}
	if (features.transfer) {
		const ab = /* @__PURE__ */ new ArrayBuffer(12), view = new DataView(ab, 1, 3), bytes = new Uint8Array(ab);
		ab.transfer();
		fixtures.push(["detached-ab", ab], ["detached-dataview", view], ["detached-u8", bytes]);
	}
	if (features.resizable) {
		const ab = new ArrayBuffer(16, { maxByteLength: 32 }), fixed = new Uint8Array(ab, 8, 4), tracking = new Uint8Array(ab, 8), view = new DataView(ab, 8, 4);
		ab.resize(4);
		fixtures.push(["rab", ab], ["oob-fixed-u8", fixed], ["oob-tracking-u8", tracking], ["oob-dataview", view]);
	}
	let traps = 0;
	const handler = {
		get() {
			traps++;
			throw new Error("get trap");
		},
		getPrototypeOf() {
			traps++;
			throw new Error("prototype trap");
		},
		ownKeys() {
			traps++;
			throw new Error("keys trap");
		},
		getOwnPropertyDescriptor() {
			traps++;
			throw new Error("descriptor trap");
		},
		has() {
			traps++;
			throw new Error("has trap");
		}
	};
	for (const [name, target] of [
		["plain", {}],
		["typed", /* @__PURE__ */ new Uint8Array(2)],
		["boxed", Object(1)],
		["map", /* @__PURE__ */ new Map()]
	]) fixtures.push(["proxy-" + name, new Proxy(target, handler)]);
	const revoked = Proxy.revocable(/* @__PURE__ */ new Uint8Array(1), handler);
	revoked.revoke();
	fixtures.push(["revoked", revoked.proxy]);
	const spoof = {};
	Object.defineProperty(spoof, Symbol.toStringTag, { get() {
		traps++;
		throw new Error("tag getter");
	} });
	fixtures.push(["spoofed-tag", spoof]);
	const matrix = [];
	for (const [label, value] of fixtures) {
		const accepted = [];
		for (const name of predicateNames) {
			const result = types[name](value);
			check(typeof result === "boolean", "predicate result " + name);
			if (result) accepted.push(name);
		}
		matrix.push({
			label,
			accepted
		});
	}
	check(traps === 0, "no proxy/tag getter calls");
	observations.push({
		predicateInputs: fixtures.length,
		predicates: predicateNames.length,
		traps,
		matrix
	});
	function Parent() {}
	function Child() {}
	util.inherits(Child, Parent);
	check(Child.super_ === Parent && Object.getPrototypeOf(Child.prototype) === Parent.prototype, "inherits");
	const superDescriptor = Object.getOwnPropertyDescriptor(Child, "super_");
	observations.push({ superDescriptor: [
		superDescriptor.enumerable,
		superDescriptor.writable,
		superDescriptor.configurable
	] });
	for (const args of [
		[null, Parent],
		[Child, null],
		[Child, () => {}]
	]) {
		const error = errorOf(() => util.inherits(...args));
		observations.push({ inheritsError: [error.name, error.code] });
	}
	observations.push({
		usv: [
			void 0,
			null,
			1n,
			"\ud800x\udc00🙂"
		].map((value) => util.toUSVString(value)),
		symbolUSV: errorOf(() => util.toUSVString(Symbol("x"))).name
	});
	const marker = {};
	check(errorOf(() => util.toUSVString({ toString() {
		throw marker;
	} })) === marker, "coercion exception identity");
	function original(value, callback) {
		callback(null, this.offset + value, "ignored");
	}
	original.extra = 7;
	const fn = util.promisify(original), custom = Symbol.for("nodejs.util.promisify.custom"), descriptor = Object.getOwnPropertyDescriptor(fn, custom);
	observations.push({
		promisify: await fn.call({ offset: 4 }, 3),
		name: fn.name,
		length: fn.length,
		extra: fn.extra,
		customFlags: [
			descriptor.enumerable,
			descriptor.writable,
			descriptor.configurable
		]
	});
	check(fn[custom] === fn && util.promisify(fn) === fn, "promisified identity");
	let gets = 0;
	function selected() {}
	function special() {}
	Object.defineProperty(special, custom, {
		get() {
			gets++;
			return selected;
		},
		configurable: true
	});
	check(util.promisify(special) === selected && gets === 2, "two custom reads");
	try {
		await util.promisify((callback) => callback(marker))();
		throw new Error("missing rejection");
	} catch (error) {
		check(error === marker, "error callback rejection");
	}
	check(await util.promisify((callback) => {
		callback(null, 1);
		callback(null, 2);
		throw marker;
	})() === 1, "first settlement");
	check(await util.promisify((callback) => queueMicrotask(() => callback(null, "queued")))() === "queued", "pure guest microtask");
	let thenReads = 0;
	const thenable = { get then() {
		thenReads++;
		throw new Error("then getter");
	} };
	check(await util.promisify((callback) => {
		callback(null, 5);
		return thenable;
	})() === 5 && thenReads === 0, "no accidental thenable read");
	const customProperty = util.promisify.custom;
	try {
		util.promisify.custom = Symbol("other");
		function target() {}
		target[custom] = selected;
		check(util.promisify(target) === selected, "private symbol independent of public field");
	} finally {
		util.promisify.custom = customProperty;
	}
	const typedPrototype = Object.getPrototypeOf(Uint8Array.prototype), oldTag = Object.getOwnPropertyDescriptor(typedPrototype, Symbol.toStringTag), oldSize = Object.getOwnPropertyDescriptor(Map.prototype, "size");
	try {
		Object.defineProperty(typedPrototype, Symbol.toStringTag, {
			get() {
				throw new Error("poisoned tag");
			},
			configurable: true
		});
		Object.defineProperty(Map.prototype, "size", {
			get() {
				throw new Error("poisoned map");
			},
			configurable: true
		});
		check(types.isUint8Array(/* @__PURE__ */ new Uint8Array(1)) && types.isMap(/* @__PURE__ */ new Map()), "captured brand intrinsics");
	} finally {
		Object.defineProperty(typedPrototype, Symbol.toStringTag, oldTag);
		Object.defineProperty(Map.prototype, "size", oldSize);
	}
	return {
		checks,
		observations,
		features,
		explicitLimits: ["No portable cross-realm factory; cross-realm cases are covered by the separate Node-only prototype, not this component."].concat(features.sharedArrayBuffer ? [] : ["SharedArrayBuffer constructor unavailable; SAB inputs not exercised."]),
		scope: "Shared supported public APIs only; no native-helper delegation, faults or private engine inspection."
	};
}
// tests/node-compat/foundation-util/prototype-scope.mjs
var prototype_scope_default = {
	"state": "isolated-node-reference-prototype; no native/component integration",
	"typesImplemented": [
		"isAnyArrayBuffer",
		"isArrayBuffer",
		"isArrayBufferView",
		"isBigInt64Array",
		"isBigIntObject",
		"isBigUint64Array",
		"isBooleanObject",
		"isBoxedPrimitive",
		"isDataView",
		"isDate",
		"isFloat32Array",
		"isFloat64Array",
		"isInt16Array",
		"isInt32Array",
		"isInt8Array",
		"isMap",
		"isNumberObject",
		"isRegExp",
		"isSet",
		"isSharedArrayBuffer",
		"isStringObject",
		"isSymbolObject",
		"isTypedArray",
		"isUint16Array",
		"isUint32Array",
		"isUint8Array",
		"isUint8ClampedArray",
		"isWeakMap",
		"isWeakSet"
	],
	"typesDeferred": [
		"isArgumentsObject",
		"isAsyncFunction",
		"isCryptoKey",
		"isExternal",
		"isGeneratorFunction",
		"isGeneratorObject",
		"isKeyObject",
		"isMapIterator",
		"isModuleNamespaceObject",
		"isNativeError",
		"isPromise",
		"isProxy",
		"isSetIterator"
	],
	"utilImplemented": [
		"TextDecoder",
		"TextEncoder",
		"inherits",
		"promisify",
		"toUSVString"
	],
	"knownDeviations": [
		"No sys DEP0025 emission or process warning channel.",
		"promisify does not implement Node internal customArgs metadata and suppresses DEP0174 warning on Promise-returning originals; functional err-first/custom-symbol path only.",
		"inspect/format remain callable stubs; versioned inspection metadata is meaningful ordinary data.",
		"JavaScript brand references can allocate wrong-receiver TypeErrors; source-reviewed native helpers remain uncompiled/untested."
	],
	"rootCandidate": "35 core predicates plus optional CryptoKey support only with explicit existing WebCrypto target dependency; six other engine/Node-only predicates deferred.",
	"scope": "Source-only proposal and ordinary public Node differential prototype. No prototype result validates a SpiderMonkey native helper or real component."
};
// tests/node-compat/foundation-util/native-component.mjs
const snapshot = {
	util,
	types,
	sys,
	defaults: util.default,
	options: util.inspect.defaultOptions,
	encoder: util.TextEncoder,
	decoder: util.TextDecoder
};
let calls = 0;
async function run() {
	try {
		const features = {
			sharedArrayBuffer: typeof SharedArrayBuffer === "function",
			transfer: typeof ArrayBuffer.prototype.transfer === "function",
			resizable: typeof ArrayBuffer.prototype.resize === "function" && new ArrayBuffer(1, { maxByteLength: 2 }).resizable === true
		};
		const cases = await runComponentCases({
			util,
			types,
			sys,
			predicateNames: prototype_scope_default.typesImplemented,
			features
		});
		const deferred = [];
		for (const [module, namespace, names] of [[
			"node:util",
			util,
			Object.keys(util).filter((name) => name !== "default" && name !== "types" && !prototype_scope_default.utilImplemented.includes(name))
		], [
			"node:util/types",
			types,
			prototype_scope_default.typesDeferred
		]]) for (const name of names) for (const construct of [false, true]) {
			let error;
			try {
				if (construct) Reflect.construct(namespace[name], []);
				else namespace[name]();
			} catch (caught) {
				error = caught;
			}
			if (error?.code !== "ERR_SM_NODE_UNSUPPORTED" || error.module !== module || error.operation !== (name === "debug" ? "debuglog" : name) || error.profile !== "sm-node-22.14.0-m0.7") throw new Error("deferred binding " + name);
			deferred.push({
				module,
				name,
				construct,
				code: error.code,
				profile: error.profile
			});
		}
		const dynamic = await import("node:util"), dynamicTypes = await import("node:util/types"), dynamicSys = await import("node:sys");
		const aliases = {
			bareCanonicalNamespaces: util === util && types === types && sys === sys,
			cachedDynamicNamespaces: dynamic === util && dynamicTypes === types && dynamicSys === sys,
			sysNamespaceDistinct: sys !== util,
			sharedDefault: sys.default === util.default,
			sharedTypes: util.types === types.default,
			thenType: typeof util.then,
			namespacePrototypeNull: Object.getPrototypeOf(util) === null
		};
		const common = {
			same: native_require_cjs_native_profile_default.util === util.default && native_require_cjs_native_profile_default.sys === util.default && native_require_cjs_native_profile_default.canonical === util.default && native_require_cjs_native_profile_default.types === types.default,
			textIdentity: native_require_cjs_native_profile_default.util.TextEncoder === globalThis.TextEncoder,
			customSymbol: native_require_cjs_native_profile_default.util.promisify.custom === Symbol.for("nodejs.util.promisify.custom"),
			defaultProperty: typeof native_require_cjs_native_profile_default.util.default
		};
		const identity = snapshot.util === util && snapshot.types === types && snapshot.sys === sys && snapshot.defaults === util.default && snapshot.options === util.inspect.defaultOptions && snapshot.encoder === util.TextEncoder && snapshot.decoder === util.TextDecoder;
		const E = globalThis.Error, T = globalThis.TypeError, A = Object.assign, oldCode = Object.getOwnPropertyDescriptor(E.prototype, "code");
		let unsupported, invalid, setterCalls = 0, depth;
		try {
			Object.defineProperty(E.prototype, "code", {
				set() {
					setterCalls++;
					throw new E("inherited setter");
				},
				configurable: true
			});
			globalThis.Error = function() {
				throw new E("replaced Error");
			};
			globalThis.TypeError = function() {
				throw new E("replaced TypeError");
			};
			Object.assign = function() {
				throw new E("replaced assign");
			};
			try {
				util.inspect();
			} catch (error) {
				unsupported = error;
			}
			try {
				util.inherits(null, function() {});
			} catch (error) {
				invalid = error;
			}
			const previous = util.inspect.defaultOptions.depth;
			util.inspect.defaultOptions = { depth: 4 };
			depth = util.inspect.defaultOptions.depth;
			util.inspect.defaultOptions = { depth: previous };
		} finally {
			globalThis.Error = E;
			globalThis.TypeError = T;
			Object.assign = A;
			if (oldCode) Object.defineProperty(E.prototype, "code", oldCode);
			else delete E.prototype.code;
		}
		const hardening = {
			unsupportedCode: unsupported?.code,
			invalidCode: invalid?.code,
			setterCalls,
			depth
		};
		return JSON.stringify({
			calls: ++calls,
			cases,
			deferred,
			aliases,
			common,
			snapshotIdentity: identity,
			hardening,
			exports: {
				util: Object.keys(util).sort(),
				types: Object.keys(types).sort(),
				sys: Object.keys(sys).sort()
			},
			noFacadeBundled: true
		});
	} catch (error) {
		return JSON.stringify({
			failure: String(error),
			stack: error?.stack
		});
	}
}
export { run };
