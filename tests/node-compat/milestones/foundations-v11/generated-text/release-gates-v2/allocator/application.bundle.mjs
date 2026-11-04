import __smBuiltin0, * as buffer from "node:buffer";
import __smBuiltin1, * as child from "node:child_process";
// tests/node-compat/foundation-alloc-unsafe/installed/static-require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	const buffer = __smBuiltin0;
	const child = __smBuiltin1;
	module.exports = {
		buffer,
		Buffer: buffer.Buffer,
		child
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var static_require_cjs_native_profile_default = __smModule.exports;
// \0node-compat:installed-allocation-checks
const Apply$1 = Reflect.apply;
const Construct$1 = Reflect.construct;
const Descriptor$2 = Object.getOwnPropertyDescriptor;
const Proto = Object.getPrototypeOf;
const ErrorCtor$2 = Error;
const U8 = Uint8Array;
function must$1(value, label) {
	if (!value) throw new ErrorCtor$2("allocUnsafe check failed: " + label);
}
function code(fn) {
	try {
		fn();
	} catch (error) {
		return {
			name: error.name,
			code: error.code
		};
	}
	throw new ErrorCtor$2("Missing allocation failure");
}
function allocationChecks(BufferCtor, allocate) {
	const cases = [];
	function check(name, run) {
		cases.push({
			name,
			result: run()
		});
	}
	check("function name arity and ordinary prototype", () => ({
		name: allocate.name,
		length: allocate.length,
		callable: typeof allocate,
		prototypeConstructor: allocate.prototype.constructor === allocate,
		prototypeWritable: Descriptor$2(allocate, "prototype").writable,
		then: typeof allocate.then
	}));
	check("invalid argument type and no implicit numeric coercion", () => {
		let calls = 0;
		const result = [
			void 0,
			null,
			false,
			true,
			"3",
			3n,
			Symbol("x"),
			[],
			/* @__PURE__ */ new Number(3),
			{
				valueOf() {
					calls++;
					return 3;
				},
				toString() {
					calls++;
					return "3";
				},
				[Symbol.toPrimitive]() {
					calls++;
					return 3;
				}
			}
		].map((size) => code(() => allocate(size)));
		must$1(calls === 0, "no size coercion");
		return {
			result,
			coercionCalls: calls
		};
	});
	check("negative NaN and infinity", () => [
		NaN,
		Infinity,
		-Infinity,
		-1,
		-.5,
		-Number.MIN_VALUE
	].map((size) => code(() => allocate(size))));
	check("integer fraction and signed zero lengths", () => [
		-0,
		0,
		Number.MIN_VALUE,
		.5,
		.999,
		1,
		1.9,
		7.75,
		64
	].map((size) => {
		const bytes = allocate(size);
		must$1(BufferCtor.isBuffer(bytes) && bytes instanceof U8, "owned Buffer brand");
		return {
			input: String(size),
			length: bytes.length,
			byteLength: bytes.byteLength,
			isBuffer: BufferCtor.isBuffer(bytes)
		};
	}));
	check("written bytes only differential", () => {
		const bytes = allocate(257);
		for (let i = 0; i < bytes.length; i++) bytes[i] = i * 17 + 3 & 255;
		return [...bytes];
	});
	check("call this binding and construction", () => {
		return [
			Apply$1(allocate, void 0, [3]),
			Apply$1(allocate, null, [4]),
			Apply$1(allocate, { get size() {
				throw new ErrorCtor$2("this must not be read");
			} }, [5]),
			new allocate(6),
			Construct$1(allocate, [7], function Other() {})
		].map((bytes) => {
			must$1(BufferCtor.isBuffer(bytes), "new/call returns genuine Buffer");
			must$1(Proto(bytes) === BufferCtor.prototype, "new target cannot change returned Buffer prototype");
			return bytes.length;
		});
	});
	check("construction invalid inputs", () => [
		code(() => new allocate()),
		code(() => new allocate("1")),
		code(() => new allocate(-.25))
	]);
	check("bound call extra arguments and derived construction", () => {
		const bound = allocate.bind({ ignored: true });
		class Derived extends allocate {}
		const derived = new Derived(2);
		return {
			boundLength: bound(3, "ignored").length,
			extraLength: allocate(4, 255).length,
			boundConstruct: new bound(5).length,
			derivedBuffer: BufferCtor.isBuffer(derived),
			derivedInstance: derived instanceof Derived,
			returnedPrototype: Proto(derived) === BufferCtor.prototype
		};
	});
	check("independent visible allocations", () => {
		const a = allocate(4), b = allocate(4);
		a[0] = 11;
		b[0] = 22;
		return {
			distinct: a !== b,
			a: a[0],
			b: b[0],
			prototype: Proto(a) === BufferCtor.prototype
		};
	});
	check("shared subarray and backing view", () => {
		const bytes = allocate(6);
		for (let i = 0; i < bytes.length; i++) bytes[i] = i + 1;
		const slice = bytes.slice(1, 4), subarray = bytes.subarray(2, 5);
		slice[0] = 41;
		subarray[0] = 42;
		const view = new U8(bytes.buffer, bytes.byteOffset, bytes.byteLength);
		view[5] = 43;
		return {
			bytes: [...bytes],
			slice: [...slice],
			subarray: [...subarray],
			sliceBrand: BufferCtor.isBuffer(slice),
			subarrayBrand: BufferCtor.isBuffer(subarray),
			backing: slice.buffer === bytes.buffer && subarray.buffer === bytes.buffer,
			offsetDeltas: [slice.byteOffset - bytes.byteOffset, subarray.byteOffset - bytes.byteOffset]
		};
	});
	return cases;
}
// \0node-compat:installed-core-contract
var _node_compat_installed_core_contract_default = {
	"schema": 1,
	"coreVersion": "sm-node-22.14.0-m0.11",
	"allocUnsafePolicy": "zeroed-no-pool-direct-u8-v1",
	"unsupportedStatic": [
		"copyBytesFrom",
		"of",
		"allocUnsafeSlow",
		"compare",
		"concat"
	],
	"prototypeRefusals": 91,
	"bufferExports": [
		"Blob",
		"Buffer",
		"File",
		"INSPECT_MAX_BYTES",
		"SlowBuffer",
		"atob",
		"btoa",
		"constants",
		"default",
		"isAscii",
		"isUtf8",
		"kMaxLength",
		"kStringMaxLength",
		"resolveObjectURL",
		"transcode"
	],
	"importOnlyExports": [
		"Blob",
		"File",
		"SlowBuffer",
		"atob",
		"btoa",
		"isAscii",
		"isUtf8",
		"resolveObjectURL",
		"transcode"
	],
	"childExports": [
		"ChildProcess",
		"_forkChild",
		"exec",
		"execFile",
		"execFileSync",
		"execSync",
		"fork",
		"spawn",
		"spawnSync"
	]
};
// tests/node-compat/foundation-alloc-unsafe/installed/checks.mjs
const ErrorCtor$1 = Error;
const TypeErrorCtor = TypeError;
const RangeErrorCtor = RangeError;
const Apply = Reflect.apply;
const Construct = Reflect.construct;
const Define$1 = Object.defineProperty;
const Descriptor$1 = Object.getOwnPropertyDescriptor;
const OwnKeys = Reflect.ownKeys;
function must(value, message) {
	if (!value) throw new ErrorCtor$1("Installed allocator: " + message);
}
function equal(a, b, message) {
	must(JSON.stringify(a) === JSON.stringify(b), message);
}
function allocationProfile(Buffer) {
	const allocate = Buffer.allocUnsafe, cases = [];
	function group(name, run) {
		cases.push({
			name,
			result: run()
		});
	}
	group("fresh zeroed no-pool backing", () => [
		0,
		.5,
		1,
		17,
		1024
	].map((size) => {
		const a = allocate(size), b = allocate(size);
		must(Buffer.isBuffer(a) && Buffer.isBuffer(b), "brand");
		must(a.byteOffset === 0 && a.buffer.byteLength === a.length && a.buffer !== b.buffer, "exact distinct backing");
		for (const byte of a) must(byte === 0, "all small bytes zero");
		return {
			size,
			length: a.length,
			offset: 0,
			backingBytes: a.buffer.byteLength
		};
	}));
	group("maximum and raw fractional cap", () => {
		const a = allocate(16777216);
		must(a.length === 16777216 && a.byteOffset === 0 && a.buffer.byteLength === 16777216, "max backing");
		must(a[0] === 0 && a[8388608] === 0 && a[16777215] === 0, "max samples");
		let rejected = 0;
		for (const size of [
			16777216.25,
			16777217,
			Number.MAX_SAFE_INTEGER
		]) try {
			allocate(size);
		} catch (e) {
			must(e.name === "RangeError" && e.code === "ERR_OUT_OF_RANGE", "cap code");
			rejected++;
		}
		must(rejected === 3, "cap failures");
		return {
			maximum: a.length,
			zeroSamples: [
				0,
				0,
				0
			],
			rejected
		};
	});
	group("captured original producer and normalization", () => {
		const oldAlloc = Buffer.alloc, oldTrunc = Math.trunc, oldApply = Reflect.apply;
		let calls = 0, a;
		const poison = () => {
			calls++;
			throw new ErrorCtor$1("public producer called");
		};
		try {
			Buffer.alloc = poison;
			Math.trunc = poison;
			Reflect.apply = poison;
			a = allocate(3.75);
		} finally {
			Buffer.alloc = oldAlloc;
			Math.trunc = oldTrunc;
			Reflect.apply = oldApply;
		}
		must(calls === 0 && a.length === 3 && Buffer.isBuffer(a), "private capture");
		equal([...a], [
			0,
			0,
			0
		], "private zero");
		return {
			length: 3,
			publicCalls: calls
		};
	});
	group("captured validation constructors and own fields", () => {
		const oldType = globalThis.TypeError, oldRange = globalThis.RangeError, oldDefine = Object.defineProperty;
		const fields = Object.fromEntries([
			"code",
			"module",
			"operation"
		].map((name) => [name, Descriptor$1(ErrorCtor$1.prototype, name)]));
		const sentinel = new ErrorCtor$1("pure JS validation poison"), caught = [];
		let calls = 0;
		const poison = () => {
			calls++;
			throw sentinel;
		};
		try {
			for (const name of [
				"code",
				"module",
				"operation"
			]) Define$1(ErrorCtor$1.prototype, name, {
				get: poison,
				set: poison,
				configurable: true
			});
			globalThis.TypeError = poison;
			globalThis.RangeError = poison;
			Object.defineProperty = poison;
			for (const value of ["3", Infinity]) try {
				allocate(value);
			} catch (error) {
				caught.push(error);
			}
		} finally {
			globalThis.TypeError = oldType;
			globalThis.RangeError = oldRange;
			Object.defineProperty = oldDefine;
			for (const name of [
				"code",
				"module",
				"operation"
			]) if (fields[name]) Define$1(ErrorCtor$1.prototype, name, fields[name]);
			else delete ErrorCtor$1.prototype[name];
		}
		must(calls === 0 && caught.length === 2, "validation captures");
		must(caught[0] instanceof TypeErrorCtor && caught[1] instanceof RangeErrorCtor, "validation types");
		for (let i = 0; i < caught.length; i++) for (const [name, value] of Object.entries({
			code: i ? "ERR_OUT_OF_RANGE" : "ERR_INVALID_ARG_TYPE",
			module: "node:buffer",
			operation: "Buffer.allocUnsafe"
		})) equal(Descriptor$1(caught[i], name), {
			value,
			writable: true,
			enumerable: true,
			configurable: true
		}, "own validation fields");
		return {
			hookCalls: calls,
			codes: caught.map((e) => e.code)
		};
	});
	group("public pool setting has no effect", () => {
		const old = Buffer.poolSize;
		let a;
		try {
			Buffer.poolSize = 8192;
			a = allocate(3);
		} finally {
			Buffer.poolSize = old;
		}
		must(a.byteOffset === 0 && a.buffer.byteLength === 3 && a.parent === a.buffer && a.offset === 0, "no pool");
		return {
			offset: 0,
			backingBytes: 3
		};
	});
	return cases;
}
function stubPoisonChecks(buffer, child, contract) {
	const B = buffer.Buffer, receiver = B.alloc(1), operations = [];
	const entry = (fn, module, operation, thisValue) => {
		for (const construct of [false, true]) operations.push({
			fn,
			module,
			operation,
			thisValue,
			construct
		});
	};
	let prototypes = 0;
	for (const name of OwnKeys(B.prototype)) {
		const d = Descriptor$1(B.prototype, name);
		if (typeof d.value !== "function" || [
			"constructor",
			"toString",
			"slice",
			"subarray"
		].includes(name)) continue;
		entry(d.value, "node:buffer", typeof name === "symbol" ? "Buffer.prototype[util.inspect.custom]" : "Buffer.prototype." + name, receiver);
		prototypes++;
	}
	must(prototypes === 91, "own prototype count");
	for (const name of contract.unsupportedStatic) entry(B[name], "node:buffer", "Buffer." + name);
	entry(B, "node:buffer", "Buffer constructor");
	for (const name of contract.importOnlyExports) entry(buffer[name], "node:buffer", name);
	for (const name of contract.childExports) entry(child[name], "node:child_process", name);
	for (const name of [
		"spawn",
		"kill",
		"ref",
		"unref"
	]) entry(child.ChildProcess.prototype[name], "node:child_process", "ChildProcess.prototype." + name);
	entry(child.ChildProcess.prototype[Symbol.for("nodejs.dispose")], "node:child_process", "ChildProcess.prototype[Symbol.dispose]");
	const fields = [
		"code",
		"module",
		"operation",
		"profile"
	], old = Object.fromEntries(fields.map((name) => [name, Descriptor$1(ErrorCtor$1.prototype, name)]));
	const oldError = globalThis.Error, oldDefine = Object.defineProperty, sentinel = new ErrorCtor$1("pure JS refusal poison");
	const counts = {
		globalError: 0,
		publicDefineProperty: 0,
		inheritedGets: 0,
		inheritedSets: 0
	}, caught = [];
	try {
		for (const name of fields) Define$1(ErrorCtor$1.prototype, name, {
			get() {
				counts.inheritedGets++;
				throw sentinel;
			},
			set() {
				counts.inheritedSets++;
				throw sentinel;
			},
			configurable: true
		});
		globalThis.Error = function ReplacedError() {
			counts.globalError++;
			throw sentinel;
		};
		Object.defineProperty = function replacedDefine() {
			counts.publicDefineProperty++;
			throw sentinel;
		};
		for (const operation of operations) {
			let failure, threw = false;
			try {
				if (operation.construct) Construct(operation.fn, []);
				else Apply(operation.fn, operation.thisValue, []);
			} catch (error) {
				failure = error;
				threw = true;
			}
			caught.push({
				operation,
				failure,
				threw
			});
		}
	} finally {
		globalThis.Error = oldError;
		Object.defineProperty = oldDefine;
		for (const name of fields) if (old[name]) Define$1(ErrorCtor$1.prototype, name, old[name]);
		else delete ErrorCtor$1.prototype[name];
	}
	equal(counts, {
		globalError: 0,
		publicDefineProperty: 0,
		inheritedGets: 0,
		inheritedSets: 0
	}, "refusal hooks unused");
	must(caught.length === 240, "finite refusal count");
	for (const { operation, failure, threw } of caught) {
		must(threw && failure instanceof ErrorCtor$1 && failure !== sentinel, "identifiable original Error");
		for (const [name, value] of Object.entries({
			code: "ERR_SM_NODE_UNSUPPORTED",
			module: operation.module,
			operation: operation.operation,
			profile: contract.coreVersion
		})) equal(Descriptor$1(failure, name), {
			value,
			writable: true,
			enumerable: true,
			configurable: true
		}, "own refusal fields");
	}
	return {
		operations: caught.length,
		prototypeFunctions: prototypes,
		counts,
		ownFields: fields,
		restored: true,
		pureJsOnly: true
	};
}
// tests/node-compat/foundation-alloc-unsafe/installed/numeric-hooks-v11.mjs
const Define = Object.defineProperty;
const Descriptor = Object.getOwnPropertyDescriptor;
const ErrorCtor = Error;
function directNumericHooks(Buffer) {
	const rows = [];
	for (const name of ["isInteger", "isFinite"]) for (const behavior of [
		"throw-sentinel",
		"return-false",
		"return-true"
	]) {
		const old = Descriptor(Number, name), sentinel = new ErrorCtor("Ordinary mutable Number hook");
		let calls = 0, value, error;
		try {
			Define(Number, name, {
				...old,
				value() {
					calls++;
					if (behavior === "throw-sentinel") throw sentinel;
					return behavior === "return-true";
				}
			});
			try {
				value = Buffer.allocUnsafe(3.75);
			} catch (caught) {
				error = caught;
			}
		} finally {
			Define(Number, name, old);
		}
		if (calls !== 0 || error !== void 0 || value.length !== 3 || !Buffer.isBuffer(value) || ![...value].every((byte) => byte === 0)) throw new ErrorCtor("Direct allocation numeric-hook policy mismatch");
		rows.push({
			name,
			behavior,
			hookCalls: calls,
			result: "zeroed-length-3"
		});
	}
	return rows;
}
// \0node-compat:installed-buffer-list-demand
function createDemandList(Buffer) {
	const Uint8Array = globalThis.Uint8Array;
	const apply = Reflect.apply, set = Uint8Array.prototype.set;
	const TypedArrayPrototypeSet = (receiver, source, offset) => apply(set, receiver, [source, offset]);
	class BufferList {
		constructor() {
			this.head = null;
			this.tail = null;
			this.length = 0;
		}
		push(v) {
			const entry = {
				data: v,
				next: null
			};
			if (this.length > 0) this.tail.next = entry;
			else this.head = entry;
			this.tail = entry;
			++this.length;
		}
		concat(n) {
			if (this.length === 0) return Buffer.alloc(0);
			const ret = Buffer.allocUnsafe(n >>> 0);
			let p = this.head;
			let i = 0;
			while (p) {
				TypedArrayPrototypeSet(ret, p.data, i);
				i += p.data.length;
				p = p.next;
			}
			return ret;
		}
		_getBuffer(n) {
			const ret = Buffer.allocUnsafe(n);
			const retLen = n;
			let p = this.head;
			let c = 0;
			do {
				const buf = p.data;
				if (n > buf.length) {
					TypedArrayPrototypeSet(ret, buf, retLen - n);
					n -= buf.length;
				} else {
					if (n === buf.length) {
						TypedArrayPrototypeSet(ret, buf, retLen - n);
						++c;
						if (p.next) this.head = p.next;
						else this.head = this.tail = null;
					} else {
						TypedArrayPrototypeSet(ret, new Uint8Array(buf.buffer, buf.byteOffset, n), retLen - n);
						this.head = p;
						p.data = buf.slice(n);
					}
					break;
				}
				++c;
			} while ((p = p.next) !== null);
			this.length -= c;
			return ret;
		}
	}
	return BufferList;
}
// tests/node-compat/foundation-alloc-unsafe/demand-checks.mjs
function demandChecks(BufferCtor, List) {
	const make = (values) => BufferCtor.from(new Uint8Array(values));
	const list = new List();
	list.push(make([1, 2]));
	list.push(make([
		3,
		4,
		5
	]));
	const joined = list.concat(5);
	const second = new List();
	second.push(make([1, 2]));
	second.push(make([
		3,
		4,
		5
	]));
	const consumed = second._getBuffer(3);
	return {
		concat: [...joined],
		concatBrand: BufferCtor.isBuffer(joined),
		originalNodes: list.length,
		consumed: [...consumed],
		consumedBrand: BufferCtor.isBuffer(consumed),
		remainingNodes: second.length,
		remaining: [...second.head.data],
		outputVisibleRangeDisjoint: consumed.buffer !== second.head.data.buffer || consumed.byteOffset + consumed.byteLength <= second.head.data.byteOffset || second.head.data.byteOffset + second.head.data.byteLength <= consumed.byteOffset
	};
}
// tests/node-compat/foundation-alloc-unsafe/installed/component-v11.mjs
const { Buffer } = buffer, allocate = Buffer.allocUnsafe;
const snapshot = allocate(3);
const view = snapshot.subarray(1, 3);
const backing = snapshot.buffer;
snapshot[0] = 17;
let calls = 0;
let bareBuffer;
let bareChild;
function check(value, message) {
	if (!value) throw new Error("Installed allocator: " + message);
}
async function run() {
	try {
		const b = String.fromCharCode(98, 117, 102, 102, 101, 114), c = String.fromCharCode(99, 104, 105, 108, 100, 95, 112, 114, 111, 99, 101, 115, 115);
		const nextBuffer = await import(b), nextChild = await import(c);
		if (bareBuffer) check(bareBuffer === nextBuffer && bareChild === nextChild, "per-specifier module cache");
		bareBuffer = nextBuffer;
		bareChild = nextChild;
		check(await import("node:buffer") === buffer && await import("node:child_process") === child, "canonical module cache");
		check(bareBuffer.Buffer === Buffer && bareBuffer.default === __smBuiltin0 && bareChild.default === __smBuiltin1, "native bare aliases");
		check(static_require_cjs_native_profile_default.Buffer === Buffer && static_require_cjs_native_profile_default.buffer === __smBuiltin0 && static_require_cjs_native_profile_default.child === __smBuiltin1 && globalThis.Buffer === Buffer, "static CJS/global identity");
		check(Object.getPrototypeOf(buffer) === null && Object.getPrototypeOf(child) === null, "native namespace prototypes");
		check(Object.prototype.toString.call(buffer) === "[object Module]" && Object.prototype.toString.call(child) === "[object Module]", "native namespace tags");
		check(buffer.then === void 0 && child.then === void 0 && __smBuiltin0.then === void 0 && __smBuiltin1.then === void 0, "safe namespace inspection");
		check(await Promise.resolve(buffer) === buffer && await Promise.resolve(child) === child, "safe namespace await");
		for (const name of _node_compat_installed_core_contract_default.bufferExports.filter((n) => n !== "default")) check(buffer[name] === __smBuiltin0[name], "Buffer default binding");
		for (const name of _node_compat_installed_core_contract_default.childExports) check(child[name] === __smBuiltin1[name], "child default binding");
		check(Buffer.allocUnsafe === allocate && bareBuffer.Buffer.allocUnsafe === allocate && static_require_cjs_native_profile_default.Buffer.allocUnsafe === allocate, "actual allocator unchanged");
		const cases = allocationChecks(Buffer, allocate), profile = allocationProfile(Buffer), refusals = stubPoisonChecks(buffer, child, _node_compat_installed_core_contract_default);
		const demand = demandChecks(Buffer, createDemandList(Buffer)), numericHooks = directNumericHooks(Buffer);
		check(Buffer.allocUnsafe === allocate, "allocator never replaced");
		check(Buffer.isBuffer(snapshot) && snapshot.buffer === backing && backing.byteLength === 3 && snapshot.byteOffset === 0, "snapshot owned brand/backing");
		check(Buffer.isBuffer(view) && view.buffer === backing && view.byteOffset === 1, "snapshot shared view");
		view[0] = ++calls;
		snapshot[0]++;
		return JSON.stringify({
			calls,
			cases,
			profile,
			refusals,
			demand,
			numericHooks,
			snapshot: {
				first: snapshot[0],
				shared: view[0] === snapshot[1],
				viewValue: view[0],
				byteOffset: view.byteOffset,
				backingBytes: backing.byteLength
			},
			coreVersion: _node_compat_installed_core_contract_default.coreVersion,
			allocUnsafePolicy: _node_compat_installed_core_contract_default.allocUnsafePolicy,
			actualNativeModule: true,
			allocatorReplaced: false,
			namespaceAliases: true,
			staticCommonJS: true,
			globalIdentity: true
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
