// \0rolldown/runtime.js
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __esmMin = (fn, res, err) => () => {
	if (err) throw err[0];
	try {
		return fn && (res = fn(fn = 0)), res;
	} catch (e) {
		throw err = [e], e;
	}
};
var __commonJSMin = (cb, mod) => () => (mod || (cb((mod = { exports: {} }).exports, mod, mod.exports), cb = null), mod.exports);
var __exportAll = (all, no_symbols) => {
	let target = {};
	for (var name in all) __defProp(target, name, {
		get: all[name],
		enumerable: true
	});
	if (!no_symbols) __defProp(target, Symbol.toStringTag, { value: "Module" });
	return target;
};
var __copyProps = (to, from, except, desc) => {
	if (from && typeof from === "object" || typeof from === "function") for (var keys = __getOwnPropNames(from), i = 0, n = keys.length, key; i < n; i++) {
		key = keys[i];
		if (!__hasOwnProp.call(to, key) && key !== except) __defProp(to, key, {
			get: ((k) => from[k]).bind(null, key),
			enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable
		});
	}
	return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(isNodeMode || !mod || !mod.__esModule || !__hasOwnProp.call(mod, "default") ? __defProp(target, "default", {
	value: mod,
	enumerable: true
}) : target, mod));
var __toCommonJS = (mod) => __hasOwnProp.call(mod, "module.exports") ? mod["module.exports"] : __copyProps(__defProp({}, "__esModule", { value: true }), mod);
// \0@oxc-project+runtime@0.156.0/helpers/esm/typeof.js
function _typeof(o) {
	"@babel/helpers - typeof";
	return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(o) {
		return typeof o;
	} : function(o) {
		return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o;
	}, _typeof(o);
}
var init_typeof = __esmMin(() => {});
// \0@oxc-project+runtime@0.156.0/helpers/esm/toPrimitive.js
function toPrimitive(t, r) {
	if ("object" != _typeof(t) || !t) return t;
	var e = t[Symbol.toPrimitive];
	if (void 0 !== e) {
		var i = e.call(t, r || "default");
		if ("object" != _typeof(i)) return i;
		throw new TypeError("@@toPrimitive must return a primitive value.");
	}
	return ("string" === r ? String : Number)(t);
}
var init_toPrimitive = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init_typeof();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/toPropertyKey.js
function toPropertyKey(t) {
	var i = toPrimitive(t, "string");
	return "symbol" == _typeof(i) ? i : i + "";
}
var init_toPropertyKey = __esmMin(() => {
	init_typeof();
	init_toPrimitive();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/defineProperty.js
function _defineProperty(e, r, t) {
	return (r = toPropertyKey(r)) in e ? Object.defineProperty(e, r, {
		value: t,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[r] = t, e;
}
var init_defineProperty = __esmMin(() => {
	init_toPropertyKey();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/errors/core.js
function inspectObject(value) {
	try {
		const constructor = Reflect.get(value, "constructor");
		if (typeof constructor === "function" && constructor.name) return `an instance of ${constructor.name}`;
	} catch (_unused) {}
	try {
		return Object.prototype.toString.call(value);
	} catch (_unused2) {
		return "an object";
	}
}
function inspectValue(value) {
	if (typeof value === "string") return value.includes("'") ? JSON.stringify(value) : `'${value}'`;
	if (typeof value === "bigint") return `${value}n`;
	if (typeof value === "number" && Object.is(value, -0)) return "-0";
	if (value === null || value === void 0 || typeof value === "number" || typeof value === "boolean" || typeof value === "symbol") return String(value);
	if (typeof value === "function") return `[Function: ${value.name || "anonymous"}]`;
	try {
		const serialized = JSON.stringify(value);
		if (serialized !== void 0) return serialized.length > 128 ? `${serialized.slice(0, 128)}...` : serialized;
	} catch (_unused3) {}
	return inspectObject(value);
}
/** Describe a value using the stable presentation used in Node type errors. */
function determineSpecificType(value) {
	if (value === null) return "null";
	if (value === void 0) return "undefined";
	switch (typeof value) {
		case "bigint": return `type bigint (${value}n)`;
		case "number":
			if (Object.is(value, -0)) return "type number (-0)";
			if (Number.isNaN(value)) return "type number (NaN)";
			return `type number (${String(value)})`;
		case "boolean": return `type boolean (${String(value)})`;
		case "symbol": return `type symbol (${String(value)})`;
		case "function": return `function ${value.name}`;
		case "object": return inspectObject(value);
		case "string": {
			const shortened = value.length > 28 ? `${value.slice(0, 25)}...` : value;
			return shortened.includes("'") ? `type string (${JSON.stringify(shortened)})` : `type string ('${shortened}')`;
		}
		default: return `type ${typeof value} (${String(value)})`;
	}
}
/** Format a list as `A and B` or `A, B, and C`, without depending on Intl. */
function formatList(values, conjunction = "and") {
	switch (values.length) {
		case 0: return "";
		case 1: return values[0];
		case 2: return `${values[0]} ${conjunction} ${values[1]}`;
		case 3: return `${values[0]}, ${values[1]}, ${conjunction} ${values[2]}`;
		default: return `${values.slice(0, -1).join(", ")}, ${conjunction} ${values.at(-1)}`;
	}
}
/** Attach Node's stable public `code` contract to a standard error instance. */
function codedError(error, code) {
	Object.defineProperty(error, "code", {
		value: code,
		enumerable: true,
		configurable: true,
		writable: true
	});
	Object.defineProperty(error, "name", {
		value: `${error.name} [${code}]`,
		enumerable: false,
		configurable: true,
		writable: true
	});
	error.stack;
	Reflect.deleteProperty(error, "name");
	Object.defineProperty(error, "toString", {
		value() {
			return `${this.name} [${code}]: ${this.message}`;
		},
		enumerable: false,
		configurable: true,
		writable: true
	});
	return error;
}
function expectedTypeDescription(expected) {
	const values = typeof expected === "string" ? [expected] : [...expected];
	const types = [];
	const instances = [];
	const other = [];
	for (const value of values) if (PRIMITIVE_TYPES.has(value)) types.push(value.toLowerCase());
	else if (CLASS_NAME.test(value)) instances.push(value);
	else other.push(value);
	if (instances.length > 0 && types.includes("object")) {
		types.splice(types.indexOf("object"), 1);
		instances.push("Object");
	}
	const sections = [];
	if (types.length > 0) sections.push(`${types.length > 1 ? "one of type" : "of type"} ${formatList(types, "or")}`);
	if (instances.length > 0) sections.push(`an instance of ${formatList(instances, "or")}`);
	if (other.length > 0) sections.push(other.length > 1 ? `one of ${formatList(other, "or")}` : other[0]);
	return formatList(sections, "or");
}
function invalidArgType$1(name, expected, actual) {
	const subject = name.endsWith(" argument") ? `${name} ` : `"${name}" ${name.includes(".") ? "property" : "argument"} `;
	return codedError(new NativeTypeError(`The ${subject}must be ${expectedTypeDescription(expected)}. Received ${determineSpecificType(actual)}`), "ERR_INVALID_ARG_TYPE");
}
function invalidArgValue(name, value, reason = "is invalid") {
	const subject = name.includes(".") ? "property" : "argument";
	return codedError(new NativeTypeError(`The ${subject} '${name}' ${reason}. Received ${inspectValue(value)}`), "ERR_INVALID_ARG_VALUE");
}
function illegalConstructor() {
	return codedError(new NativeTypeError("Illegal constructor"), "ERR_ILLEGAL_CONSTRUCTOR");
}
/** Node's receiver check failure, raised when a method runs against a forged `this`. */
function invalidThis(name) {
	return codedError(new NativeTypeError(`Value of "this" must be of type ${name}`), "ERR_INVALID_THIS");
}
function deprecatedNodeApi(name, replacement) {
	const suffix = replacement ? ` Use ${replacement} instead.` : "";
	return codedError(new NativeError(`The deprecated Node.js API ${name} is not supported by jco-std.${suffix}`), "ERR_JCO_UNSUPPORTED_DEPRECATED_NODE_API");
}
function unsupportedNodeApi(api, reason) {
	return codedError(new NativeError(`${api} is not supported in a WebAssembly component: ${reason}`), "ERR_JCO_UNSUPPORTED_NODE_API");
}
function outOfRange$1(name, range, value) {
	return codedError(new NativeRangeError(`The value of "${name}" is out of range. It must be ${range}. Received ${inspectValue(value)}`), "ERR_OUT_OF_RANGE");
}
var NativeError, NativeRangeError, NativeTypeError, AbortError$1, PRIMITIVE_TYPES, CLASS_NAME;
var init_core = __esmMin(() => {
	init_defineProperty();
	NativeError = globalThis.Error;
	NativeRangeError = globalThis.RangeError;
	NativeTypeError = globalThis.TypeError;
	AbortError$1 = class extends NativeError {
		constructor(message = "The operation was aborted", options) {
			if (options !== void 0 && (typeof options !== "object" || options === null)) throw invalidArgType$1("options", "Object", options);
			super(message, options);
			_defineProperty(this, "code", "ABORT_ERR");
			this.name = "AbortError";
		}
	};
	PRIMITIVE_TYPES = /* @__PURE__ */ new Set([
		"string",
		"function",
		"number",
		"object",
		"Function",
		"Object",
		"boolean",
		"bigint",
		"symbol"
	]);
	CLASS_NAME = /^[A-Z][a-zA-Z0-9]*$/;
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/internal/validation.js
function validateFunction(value, name) {
	if (typeof value !== "function") throw invalidArgType$1(name, "Function", value);
}
function validateObject(value, name, options = {}) {
	if (value === null || typeof value !== "object" || !options.allowArray && Array.isArray(value)) throw invalidArgType$1(name, "Object", value);
}
function validateBoolean(value, name) {
	if (typeof value !== "boolean") throw invalidArgType$1(name, "boolean", value);
}
var init_validation = __esmMin(() => {
	init_core();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/errors/call-site.js
function parseFrame(line) {
	var _SPIDERMONKEY_FRAME$e;
	const match = (_SPIDERMONKEY_FRAME$e = SPIDERMONKEY_FRAME.exec(line)) !== null && _SPIDERMONKEY_FRAME$e !== void 0 ? _SPIDERMONKEY_FRAME$e : V8_FRAME.exec(line);
	if (!(match === null || match === void 0 ? void 0 : match.groups)) return;
	const { name, location, line: lineNumber, column } = match.groups;
	const evalSeparator = location.lastIndexOf(" > eval");
	const isEval = evalSeparator !== -1 || location.startsWith("eval");
	return {
		functionName: name ? name : null,
		fileName: evalSeparator === -1 ? location || null : location.slice(evalSeparator + 7) || null,
		lineNumber: Number(lineNumber),
		columnNumber: Number(column),
		isEval,
		evalOrigin: evalSeparator === -1 ? null : location.slice(0, evalSeparator)
	};
}
function toCallSite(frame) {
	var _frame$fileName, _frame$lineNumber, _frame$columnNumber;
	const location = `${(_frame$fileName = frame.fileName) !== null && _frame$fileName !== void 0 ? _frame$fileName : "<anonymous>"}:${(_frame$lineNumber = frame.lineNumber) !== null && _frame$lineNumber !== void 0 ? _frame$lineNumber : 0}:${(_frame$columnNumber = frame.columnNumber) !== null && _frame$columnNumber !== void 0 ? _frame$columnNumber : 0}`;
	return {
		getFileName: () => frame.fileName,
		getLineNumber: () => frame.lineNumber,
		getColumnNumber: () => frame.columnNumber,
		getFunctionName: () => frame.functionName,
		getTypeName: () => null,
		getMethodName: () => null,
		getFunction: () => void 0,
		getEvalOrigin: () => frame.evalOrigin,
		isNative: () => frame.fileName === null,
		isEval: () => frame.isEval,
		isConstructor: () => false,
		isToplevel: () => frame.functionName === null,
		isAsync: () => false,
		isPromiseAll: () => false,
		toString: () => frame.functionName ? `${frame.functionName} (${location})` : location
	};
}
/**
* Parse an engine stack string into V8-shaped call sites.
*
* @param stack - the engine's stack string
* @param skipUntil - drop every frame up to and including the first one for this function,
*   which is how `Error.captureStackTrace()`'s `constructorOpt` hides its own frames
* @returns one call site per frame the string named
*/
function parseCallSites(stack, skipUntil) {
	const frames = [];
	for (const line of stack.split("\n")) {
		const trimmed = line.trim();
		if (!trimmed) continue;
		const frame = parseFrame(trimmed);
		if (frame) frames.push(frame);
	}
	if (skipUntil) {
		const index = frames.findIndex((frame) => frame.functionName === skipUntil);
		if (index >= 0) frames.splice(0, index + 1);
	}
	return frames.map(toCallSite);
}
var SPIDERMONKEY_FRAME, V8_FRAME;
var init_call_site = __esmMin(() => {
	SPIDERMONKEY_FRAME = new RegExp("^(?<name>.*?)@(?<location>.*?):(?<line>\\d+):(?<column>\\d+)$", "");
	V8_FRAME = new RegExp("^\\s*at\\s+(?:(?<name>.*?)\\s+\\()?(?<location>.*?):(?<line>\\d+):(?<column>\\d+)\\)?$", "");
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/errors.js
function captureStackTrace(targetObject, constructorOpt) {
	if (typeof targetObject !== "object" && typeof targetObject !== "function" || targetObject === null) throw invalidArgType$1("targetObject", "Object", targetObject);
	const target = targetObject;
	const constructor = globalThis.Error;
	const previousPrepare = constructor.prepareStackTrace;
	let raw;
	try {
		var _constructor$stack;
		Reflect.set(constructor, "prepareStackTrace", void 0);
		raw = String((_constructor$stack = new constructor().stack) !== null && _constructor$stack !== void 0 ? _constructor$stack : "Error");
	} finally {
		constructor.prepareStackTrace = previousPrepare;
	}
	let stack = raw;
	if (constructorOpt === null || constructorOpt === void 0 ? void 0 : constructorOpt.name) {
		const lines = stack.split("\n");
		const frame = lines.findIndex((line) => line.includes(constructorOpt.name));
		if (frame >= 0) stack = [lines[0], ...lines.slice(frame + 1)].join("\n");
	}
	const name = typeof target.name === "string" ? target.name : "Error";
	const message = typeof target.message === "string" ? target.message : "";
	const lines = stack.split("\n");
	lines[0] = message ? `${name}: ${message}` : name;
	const rendered = lines.join("\n");
	let value;
	let computed = false;
	Object.defineProperty(targetObject, "stack", {
		enumerable: false,
		configurable: true,
		get() {
			if (!computed) {
				computed = true;
				const prepare = globalThis.Error.prepareStackTrace;
				value = typeof prepare === "function" ? prepare(targetObject, parseCallSites(raw, constructorOpt === null || constructorOpt === void 0 ? void 0 : constructorOpt.name)) : rendered;
			}
			return value;
		},
		set(replacement) {
			computed = true;
			value = replacement;
		}
	});
}
function ensureNodeErrorConstructor() {
	const constructor = globalThis.Error;
	let compatibleCaptureStackTrace = false;
	if (typeof constructor.captureStackTrace === "function") try {
		const target = {
			name: "JcoErrorProbe",
			message: "probe"
		};
		constructor.captureStackTrace(target);
		compatibleCaptureStackTrace = typeof target.stack === "string" && target.stack.startsWith("JcoErrorProbe: probe");
	} catch (_unused) {}
	if (!compatibleCaptureStackTrace) Object.defineProperty(constructor, "captureStackTrace", {
		value: captureStackTrace,
		enumerable: false,
		configurable: true,
		writable: true
	});
	if (!("stackTraceLimit" in constructor)) Object.defineProperty(constructor, "stackTraceLimit", {
		value: 10,
		enumerable: true,
		configurable: true,
		writable: true
	});
	if (typeof constructor.isError !== "function") Object.defineProperty(constructor, "isError", {
		value(value) {
			return Object.prototype.toString.call(value) === "[object Error]";
		},
		enumerable: false,
		configurable: true,
		writable: true
	});
	return constructor;
}
var _optionalGlobals$DOME, Error$1, RangeError, TypeError, DOM_EXCEPTION_CODES, PortableDOMException, DOM_EXCEPTION_CONSTANTS, optionalGlobals, DOMException;
var init_errors$2 = __esmMin(() => {
	init_defineProperty();
	init_core();
	init_validation();
	init_core();
	init_call_site();
	Error$1 = ensureNodeErrorConstructor();
	globalThis.EvalError;
	RangeError = globalThis.RangeError;
	globalThis.ReferenceError;
	globalThis.SyntaxError;
	TypeError = globalThis.TypeError;
	globalThis.URIError;
	globalThis.Error;
	globalThis.Error;
	DOM_EXCEPTION_CODES = {
		IndexSizeError: 1,
		DOMStringSizeError: 2,
		HierarchyRequestError: 3,
		WrongDocumentError: 4,
		InvalidCharacterError: 5,
		NoDataAllowedError: 6,
		NoModificationAllowedError: 7,
		NotFoundError: 8,
		NotSupportedError: 9,
		InUseAttributeError: 10,
		InvalidStateError: 11,
		SyntaxError: 12,
		InvalidModificationError: 13,
		NamespaceError: 14,
		InvalidAccessError: 15,
		ValidationError: 16,
		TypeMismatchError: 17,
		SecurityError: 18,
		NetworkError: 19,
		AbortError: 20,
		URLMismatchError: 21,
		QuotaExceededError: 22,
		TimeoutError: 23,
		InvalidNodeTypeError: 24,
		DataCloneError: 25
	};
	PortableDOMException = class extends globalThis.Error {
		constructor(message = "", name = "Error") {
			var _DOM_EXCEPTION_CODES$;
			super(message);
			_defineProperty(this, "code", void 0);
			this.name = name;
			this.code = (_DOM_EXCEPTION_CODES$ = DOM_EXCEPTION_CODES[name]) !== null && _DOM_EXCEPTION_CODES$ !== void 0 ? _DOM_EXCEPTION_CODES$ : 0;
		}
	};
	DOM_EXCEPTION_CONSTANTS = {
		INDEX_SIZE_ERR: 1,
		DOMSTRING_SIZE_ERR: 2,
		HIERARCHY_REQUEST_ERR: 3,
		WRONG_DOCUMENT_ERR: 4,
		INVALID_CHARACTER_ERR: 5,
		NO_DATA_ALLOWED_ERR: 6,
		NO_MODIFICATION_ALLOWED_ERR: 7,
		NOT_FOUND_ERR: 8,
		NOT_SUPPORTED_ERR: 9,
		INUSE_ATTRIBUTE_ERR: 10,
		INVALID_STATE_ERR: 11,
		SYNTAX_ERR: 12,
		INVALID_MODIFICATION_ERR: 13,
		NAMESPACE_ERR: 14,
		INVALID_ACCESS_ERR: 15,
		VALIDATION_ERR: 16,
		TYPE_MISMATCH_ERR: 17,
		SECURITY_ERR: 18,
		NETWORK_ERR: 19,
		ABORT_ERR: 20,
		URL_MISMATCH_ERR: 21,
		QUOTA_EXCEEDED_ERR: 22,
		TIMEOUT_ERR: 23,
		INVALID_NODE_TYPE_ERR: 24,
		DATA_CLONE_ERR: 25
	};
	for (const [name, value] of Object.entries(DOM_EXCEPTION_CONSTANTS)) {
		const descriptor = {
			value,
			enumerable: true,
			configurable: false,
			writable: false
		};
		Object.defineProperty(PortableDOMException, name, descriptor);
		Object.defineProperty(PortableDOMException.prototype, name, descriptor);
	}
	optionalGlobals = globalThis;
	optionalGlobals.AggregateError;
	DOMException = (_optionalGlobals$DOME = optionalGlobals.DOMException) !== null && _optionalGlobals$DOME !== void 0 ? _optionalGlobals$DOME : PortableDOMException;
	optionalGlobals.SuppressedError;
});
// \0jco-node-builtin:error-globals
var init__jco_node_builtin_error_globals = __esmMin(() => {
	init_errors$2();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/checkPrivateRedeclaration.js
function _checkPrivateRedeclaration(e, t) {
	if (t.has(e)) throw new TypeError("Cannot initialize the same private elements twice on an object");
}
var init_checkPrivateRedeclaration = __esmMin(() => {
	init__jco_node_builtin_error_globals();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/classPrivateFieldInitSpec.js
function _classPrivateFieldInitSpec(e, t, a) {
	_checkPrivateRedeclaration(e, t), t.set(e, a);
}
var init_classPrivateFieldInitSpec = __esmMin(() => {
	init_checkPrivateRedeclaration();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/assertClassBrand.js
function _assertClassBrand(e, t, n) {
	if ("function" == typeof e ? e === t : e.has(t)) return arguments.length < 3 ? t : n;
	throw new TypeError("Private element is not present on this object");
}
var init_assertClassBrand = __esmMin(() => {
	init__jco_node_builtin_error_globals();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/classPrivateFieldGet2.js
function _classPrivateFieldGet2(s, a) {
	return s.get(_assertClassBrand(s, a));
}
var init_classPrivateFieldGet2 = __esmMin(() => {
	init_assertClassBrand();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/classPrivateFieldSet2.js
function _classPrivateFieldSet2(s, a, r) {
	return s.set(_assertClassBrand(s, a), r), r;
}
var init_classPrivateFieldSet2 = __esmMin(() => {
	init_assertClassBrand();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/text-encoding.js
var _globalThis$TextEncod, _globalThis$TextDecod, PortableTextEncoder, _pending, _atStart, PortableTextDecoder, TextEncoder, TextDecoder;
var init_text_encoding = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_node_buffer();
	init_defineProperty();
	init_classPrivateFieldInitSpec();
	init_classPrivateFieldGet2();
	init_classPrivateFieldSet2();
	PortableTextEncoder = class {
		constructor() {
			_defineProperty(this, "encoding", "utf-8");
		}
		encode(input = "") {
			return new Uint8Array(Buffer$1.from(String(input), "utf8"));
		}
		encodeInto(input, destination) {
			let read = 0, written = 0;
			for (const character of String(input)) {
				const bytes = this.encode(character);
				if (written + bytes.length > destination.length) break;
				destination.set(bytes, written);
				written += bytes.length;
				read += character.length;
			}
			return {
				read,
				written
			};
		}
	};
	_pending = /* @__PURE__ */ new WeakMap();
	_atStart = /* @__PURE__ */ new WeakMap();
	PortableTextDecoder = class {
		constructor(label = "utf-8", options = {}) {
			_defineProperty(this, "encoding", void 0);
			_defineProperty(this, "fatal", void 0);
			_defineProperty(this, "ignoreBOM", void 0);
			_classPrivateFieldInitSpec(this, _pending, Buffer$1.alloc(0));
			_classPrivateFieldInitSpec(this, _atStart, true);
			const normalized = String(label).trim().toLowerCase();
			if ([
				"utf-8",
				"utf8",
				"unicode-1-1-utf-8"
			].includes(normalized)) this.encoding = "utf-8";
			else if ([
				"latin1",
				"iso-8859-1",
				"iso8859-1",
				"windows-1252",
				"ascii",
				"us-ascii"
			].includes(normalized)) this.encoding = "windows-1252";
			else throw new RangeError(`The encoding label provided ('${label}') is invalid`);
			this.fatal = Boolean(options.fatal);
			this.ignoreBOM = Boolean(options.ignoreBOM);
		}
		decode(input, options = {}) {
			const view = input === void 0 ? /* @__PURE__ */ new Uint8Array() : ArrayBuffer.isView(input) ? new Uint8Array(input.buffer, input.byteOffset, input.byteLength) : new Uint8Array(input);
			if (this.encoding === "windows-1252") {
				const c1 = [
					8364,
					129,
					8218,
					402,
					8222,
					8230,
					8224,
					8225,
					710,
					8240,
					352,
					8249,
					338,
					141,
					381,
					143,
					144,
					8216,
					8217,
					8220,
					8221,
					8226,
					8211,
					8212,
					732,
					8482,
					353,
					8250,
					339,
					157,
					382,
					376
				];
				return Array.from(view, (byte) => String.fromCharCode(byte >= 128 && byte < 160 ? c1[byte - 128] : byte)).join("");
			}
			let bytes = Buffer$1.concat([_classPrivateFieldGet2(_pending, this), Buffer$1.from(view)]);
			_classPrivateFieldSet2(_pending, this, Buffer$1.alloc(0));
			if (options.stream && bytes.length) {
				let start = bytes.length - 1;
				while (start >= 0 && (bytes[start] & 192) === 128) start--;
				const lead = bytes[start];
				const expected = lead >= 194 && lead <= 223 ? 2 : lead >= 224 && lead <= 239 ? 3 : lead >= 240 && lead <= 244 ? 4 : 0;
				if (expected && bytes.length - start < expected) {
					_classPrivateFieldSet2(_pending, this, bytes.subarray(start));
					bytes = bytes.subarray(0, start);
				}
			}
			let value = bytes.toString("utf8");
			if (this.fatal && !Buffer$1.from(value, "utf8").equals(bytes)) {
				_classPrivateFieldSet2(_pending, this, Buffer$1.alloc(0));
				_classPrivateFieldSet2(_atStart, this, true);
				throw new TypeError("The encoded data was not valid for encoding utf-8");
			}
			if (_classPrivateFieldGet2(_atStart, this) && value.length) {
				_classPrivateFieldSet2(_atStart, this, false);
				if (!this.ignoreBOM && value.charCodeAt(0) === 65279) value = value.slice(1);
			}
			if (!options.stream) _classPrivateFieldSet2(_atStart, this, true);
			return value;
		}
	};
	TextEncoder = (_globalThis$TextEncod = globalThis.TextEncoder) !== null && _globalThis$TextEncod !== void 0 ? _globalThis$TextEncod : PortableTextEncoder;
	TextDecoder = (_globalThis$TextDecod = globalThis.TextDecoder) !== null && _globalThis$TextDecod !== void 0 ? _globalThis$TextDecod : PortableTextDecoder;
});
// \0jco-node-builtin:text-encoding
var init__jco_node_builtin_text_encoding = __esmMin(() => {
	init_text_encoding();
});
// \0jco-node-builtin:console-globals
var _jco_node_builtin_console_globals_default;
var init__jco_node_builtin_console_globals = __esmMin(() => {
	_jco_node_builtin_console_globals_default = globalThis.console;
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/unenv/dist/runtime/node/internal/buffer/base64.mjs
function getLens(b64) {
	const len = b64.length;
	if (len % 4 > 0) throw new Error$1("Invalid string. Length must be a multiple of 4");
	let validLen = b64.indexOf("=");
	if (validLen === -1) validLen = len;
	const placeHoldersLen = validLen === len ? 0 : 4 - validLen % 4;
	return [validLen, placeHoldersLen];
}
function _byteLength(b64, validLen, placeHoldersLen) {
	return (validLen + placeHoldersLen) * 3 / 4 - placeHoldersLen;
}
function toByteArray(b64) {
	let tmp;
	const lens = getLens(b64);
	const validLen = lens[0];
	const placeHoldersLen = lens[1];
	const arr = new Arr(_byteLength(b64, validLen, placeHoldersLen));
	let curByte = 0;
	const len = placeHoldersLen > 0 ? validLen - 4 : validLen;
	let i = 0;
	for (; i < len; i += 4) {
		tmp = revLookup[b64.charCodeAt(i)] << 18 | revLookup[b64.charCodeAt(i + 1)] << 12 | revLookup[b64.charCodeAt(i + 2)] << 6 | revLookup[b64.charCodeAt(i + 3)];
		arr[curByte++] = tmp >> 16 & 255;
		arr[curByte++] = tmp >> 8 & 255;
		arr[curByte++] = tmp & 255;
	}
	if (placeHoldersLen === 2) {
		tmp = revLookup[b64.charCodeAt(i)] << 2 | revLookup[b64.charCodeAt(i + 1)] >> 4;
		arr[curByte++] = tmp & 255;
	}
	if (placeHoldersLen === 1) {
		tmp = revLookup[b64.charCodeAt(i)] << 10 | revLookup[b64.charCodeAt(i + 1)] << 4 | revLookup[b64.charCodeAt(i + 2)] >> 2;
		arr[curByte++] = tmp >> 8 & 255;
		arr[curByte++] = tmp & 255;
	}
	return arr;
}
function tripletToBase64(num) {
	return lookup[num >> 18 & 63] + lookup[num >> 12 & 63] + lookup[num >> 6 & 63] + lookup[num & 63];
}
function encodeChunk(uint8, start, end) {
	let tmp;
	const output = [];
	for (let i = start; i < end; i += 3) {
		tmp = (uint8[i] << 16 & 16711680) + (uint8[i + 1] << 8 & 65280) + (uint8[i + 2] & 255);
		output.push(tripletToBase64(tmp));
	}
	return output.join("");
}
function fromByteArray(uint8) {
	let tmp;
	const len = uint8.length;
	const extraBytes = len % 3;
	const parts = [];
	const maxChunkLength = 16383;
	for (let i = 0, len2 = len - extraBytes; i < len2; i += maxChunkLength) parts.push(encodeChunk(uint8, i, i + maxChunkLength > len2 ? len2 : i + maxChunkLength));
	if (extraBytes === 1) {
		tmp = uint8[len - 1];
		parts.push(lookup[tmp >> 2] + lookup[tmp << 4 & 63] + "==");
	} else if (extraBytes === 2) {
		tmp = (uint8[len - 2] << 8) + uint8[len - 1];
		parts.push(lookup[tmp >> 10] + lookup[tmp >> 4 & 63] + lookup[tmp << 2 & 63] + "=");
	}
	return parts.join("");
}
var lookup, revLookup, Arr, code;
var init_base64 = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	lookup = [];
	revLookup = [];
	Arr = typeof Uint8Array === "undefined" ? Array : Uint8Array;
	code = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	for (let i = 0, len = code.length; i < len; ++i) {
		lookup[i] = code[i];
		revLookup[code.charCodeAt(i)] = i;
	}
	revLookup["-".charCodeAt(0)] = 62;
	revLookup["_".charCodeAt(0)] = 63;
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/unenv/dist/runtime/node/internal/buffer/ieee754.mjs
/*! ieee754. BSD-3-Clause License. Feross Aboukhadijeh <https://feross.org/opensource> */
function read(buffer, offset, isLE, mLen, nBytes) {
	let e, m;
	const eLen = nBytes * 8 - mLen - 1;
	const eMax = (1 << eLen) - 1;
	const eBias = eMax >> 1;
	let nBits = -7;
	let i = isLE ? nBytes - 1 : 0;
	const d = isLE ? -1 : 1;
	let s = buffer[offset + i];
	i += d;
	e = s & (1 << -nBits) - 1;
	s >>= -nBits;
	nBits += eLen;
	while (nBits > 0) {
		e = e * 256 + buffer[offset + i];
		i += d;
		nBits -= 8;
	}
	m = e & (1 << -nBits) - 1;
	e >>= -nBits;
	nBits += mLen;
	while (nBits > 0) {
		m = m * 256 + buffer[offset + i];
		i += d;
		nBits -= 8;
	}
	if (e === 0) e = 1 - eBias;
	else if (e === eMax) return m ? NaN : (s ? -1 : 1) * Number.POSITIVE_INFINITY;
	else {
		m = m + Math.pow(2, mLen);
		e = e - eBias;
	}
	return (s ? -1 : 1) * m * Math.pow(2, e - mLen);
}
function write$1(buffer, value, offset, isLE, mLen, nBytes) {
	let e, m, c;
	let eLen = nBytes * 8 - mLen - 1;
	const eMax = (1 << eLen) - 1;
	const eBias = eMax >> 1;
	const rt = mLen === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0;
	let i = isLE ? 0 : nBytes - 1;
	const d = isLE ? 1 : -1;
	const s = value < 0 || value === 0 && 1 / value < 0 ? 1 : 0;
	value = Math.abs(value);
	if (Number.isNaN(value) || value === Number.POSITIVE_INFINITY) {
		m = Number.isNaN(value) ? 1 : 0;
		e = eMax;
	} else {
		e = Math.floor(Math.log2(value));
		if (value * (c = Math.pow(2, -e)) < 1) {
			e--;
			c *= 2;
		}
		value += e + eBias >= 1 ? rt / c : rt * Math.pow(2, 1 - eBias);
		if (value * c >= 2) {
			e++;
			c /= 2;
		}
		if (e + eBias >= eMax) {
			m = 0;
			e = eMax;
		} else if (e + eBias >= 1) {
			m = (value * c - 1) * Math.pow(2, mLen);
			e = e + eBias;
		} else {
			m = value * Math.pow(2, eBias - 1) * Math.pow(2, mLen);
			e = 0;
		}
	}
	while (mLen >= 8) {
		buffer[offset + i] = m & 255;
		i += d;
		m /= 256;
		mLen -= 8;
	}
	e = e << mLen | m;
	eLen += mLen;
	while (eLen > 0) {
		buffer[offset + i] = e & 255;
		i += d;
		e /= 256;
		eLen -= 8;
	}
	buffer[offset + i - d] |= s * 128;
}
var init_ieee754 = __esmMin(() => {});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/unenv/dist/runtime/node/internal/buffer/buffer.mjs
/*!
* The buffer module from node.js, for the browser.
*
* @author   Feross Aboukhadijeh <https://feross.org>
* @license  MIT
*/
function typedArraySupport() {
	try {
		const arr = /* @__PURE__ */ new Uint8Array(1);
		const proto = { foo: function() {
			return 42;
		} };
		Object.setPrototypeOf(proto, Uint8Array.prototype);
		Object.setPrototypeOf(arr, proto);
		return arr.foo() === 42;
	} catch (_unused) {
		return false;
	}
}
function createBuffer(length) {
	if (length > K_MAX_LENGTH) throw new RangeError("The value \"" + length + "\" is invalid for option \"size\"");
	const buf = new Uint8Array(length);
	Object.setPrototypeOf(buf, Buffer$2.prototype);
	return buf;
}
/**
* The Buffer constructor returns instances of `Uint8Array` that have their
* prototype changed to `Buffer.prototype`. Furthermore, `Buffer` is a subclass of
* `Uint8Array`, so the returned instances will have all the node `Buffer` methods
* and the `Uint8Array` methods. Square bracket notation works as expected -- it
* returns a single octet.
*
* The `Uint8Array` prototype remains unmodified.
*/
function Buffer$2(arg, encodingOrOffset, length) {
	if (typeof arg === "number") {
		if (typeof encodingOrOffset === "string") throw new TypeError("The \"string\" argument must be of type string. Received type number");
		return allocUnsafe(arg);
	}
	return from$1(arg, encodingOrOffset, length);
}
function from$1(value, encodingOrOffset, length) {
	if (typeof value === "string") return fromString(value, encodingOrOffset);
	if (ArrayBuffer.isView(value)) return fromArrayView(value);
	if (value == null) throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof value);
	if (isInstance(value, ArrayBuffer) || value && isInstance(value.buffer, ArrayBuffer)) return fromArrayBuffer(value, encodingOrOffset, length);
	if (typeof SharedArrayBuffer !== "undefined" && (isInstance(value, SharedArrayBuffer) || value && isInstance(value.buffer, SharedArrayBuffer))) return fromArrayBuffer(value, encodingOrOffset, length);
	if (typeof value === "number") throw new TypeError("The \"value\" argument must not be of type number. Received type number");
	const valueOf = value.valueOf && value.valueOf();
	if (valueOf != null && valueOf !== value) return Buffer$2.from(valueOf, encodingOrOffset, length);
	const b = fromObject(value);
	if (b) return b;
	if (typeof Symbol !== "undefined" && Symbol.toPrimitive != null && typeof value[Symbol.toPrimitive] === "function") return Buffer$2.from(value[Symbol.toPrimitive]("string"), encodingOrOffset, length);
	throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof value);
}
function assertSize(size) {
	if (typeof size !== "number") throw new TypeError("\"size\" argument must be of type number");
	else if (size < 0) throw new RangeError("The value \"" + size + "\" is invalid for option \"size\"");
}
function alloc(size, fill, encoding) {
	assertSize(size);
	if (size <= 0) return createBuffer(size);
	if (fill !== void 0) return typeof encoding === "string" ? createBuffer(size).fill(fill, encoding) : createBuffer(size).fill(fill);
	return createBuffer(size);
}
function allocUnsafe(size) {
	assertSize(size);
	return createBuffer(size < 0 ? 0 : checked(size) | 0);
}
function fromString(string, encoding) {
	if (typeof encoding !== "string" || encoding === "") encoding = "utf8";
	if (!Buffer$2.isEncoding(encoding)) throw new TypeError("Unknown encoding: " + encoding);
	const length = byteLength(string, encoding) | 0;
	let buf = createBuffer(length);
	const actual = buf.write(string, encoding);
	if (actual !== length) buf = buf.slice(0, actual);
	return buf;
}
function fromArrayLike(array) {
	const length = array.length < 0 ? 0 : checked(array.length) | 0;
	const buf = createBuffer(length);
	for (let i = 0; i < length; i += 1) buf[i] = array[i] & 255;
	return buf;
}
function fromArrayView(arrayView) {
	if (isInstance(arrayView, Uint8Array)) {
		const copy = new Uint8Array(arrayView);
		return fromArrayBuffer(copy.buffer, copy.byteOffset, copy.byteLength);
	}
	return fromArrayLike(arrayView);
}
function fromArrayBuffer(array, byteOffset, length) {
	if (byteOffset < 0 || array.byteLength < byteOffset) throw new RangeError("\"offset\" is outside of buffer bounds");
	if (array.byteLength < byteOffset + (length || 0)) throw new RangeError("\"length\" is outside of buffer bounds");
	let buf;
	if (byteOffset === void 0 && length === void 0) buf = new Uint8Array(array);
	else if (length === void 0) buf = new Uint8Array(array, byteOffset);
	else buf = new Uint8Array(array, byteOffset, length);
	Object.setPrototypeOf(buf, Buffer$2.prototype);
	return buf;
}
function fromObject(obj) {
	if (Buffer$2.isBuffer(obj)) {
		const len = checked(obj.length) | 0;
		const buf = createBuffer(len);
		if (buf.length === 0) return buf;
		obj.copy(buf, 0, 0, len);
		return buf;
	}
	if (obj.length !== void 0) {
		if (typeof obj.length !== "number" || numberIsNaN(obj.length)) return createBuffer(0);
		return fromArrayLike(obj);
	}
	if (obj.type === "Buffer" && Array.isArray(obj.data)) return fromArrayLike(obj.data);
}
function checked(length) {
	if (length >= K_MAX_LENGTH) throw new RangeError("Attempt to allocate Buffer larger than maximum size: 0x" + K_MAX_LENGTH.toString(16) + " bytes");
	return length | 0;
}
function byteLength(string, encoding) {
	if (Buffer$2.isBuffer(string)) return string.length;
	if (ArrayBuffer.isView(string) || isInstance(string, ArrayBuffer)) return string.byteLength;
	if (typeof string !== "string") throw new TypeError("The \"string\" argument must be one of type string, Buffer, or ArrayBuffer. Received type " + typeof string);
	const len = string.length;
	const mustMatch = arguments.length > 2 && arguments[2] === true;
	if (!mustMatch && len === 0) return 0;
	let loweredCase = false;
	for (;;) switch (encoding) {
		case "ascii":
		case "latin1":
		case "binary": return len;
		case "utf8":
		case "utf-8": return utf8ToBytes(string).length;
		case "ucs2":
		case "ucs-2":
		case "utf16le":
		case "utf-16le": return len * 2;
		case "hex": return len >>> 1;
		case "base64": return base64ToBytes(string).length;
		default:
			if (loweredCase) return mustMatch ? -1 : utf8ToBytes(string).length;
			encoding = ("" + encoding).toLowerCase();
			loweredCase = true;
	}
}
function slowToString(encoding, start, end) {
	let loweredCase = false;
	if (start === void 0 || start < 0) start = 0;
	if (start > this.length) return "";
	if (end === void 0 || end > this.length) end = this.length;
	if (end <= 0) return "";
	end >>>= 0;
	start >>>= 0;
	if (end <= start) return "";
	if (!encoding) encoding = "utf8";
	while (true) switch (encoding) {
		case "hex": return hexSlice(this, start, end);
		case "utf8":
		case "utf-8": return utf8Slice(this, start, end);
		case "ascii": return asciiSlice(this, start, end);
		case "latin1":
		case "binary": return latin1Slice(this, start, end);
		case "base64": return base64Slice(this, start, end);
		case "ucs2":
		case "ucs-2":
		case "utf16le":
		case "utf-16le": return utf16leSlice(this, start, end);
		default:
			if (loweredCase) throw new TypeError("Unknown encoding: " + encoding);
			encoding = (encoding + "").toLowerCase();
			loweredCase = true;
	}
}
function swap(b, n, m) {
	const i = b[n];
	b[n] = b[m];
	b[m] = i;
}
function bidirectionalIndexOf(buffer, val, byteOffset, encoding, dir) {
	if (buffer.length === 0) return -1;
	if (typeof byteOffset === "string") {
		encoding = byteOffset;
		byteOffset = 0;
	} else if (byteOffset > 2147483647) byteOffset = 2147483647;
	else if (byteOffset < -2147483648) byteOffset = -2147483648;
	byteOffset = +byteOffset;
	if (numberIsNaN(byteOffset)) byteOffset = dir ? 0 : buffer.length - 1;
	if (byteOffset < 0) byteOffset = buffer.length + byteOffset;
	if (byteOffset >= buffer.length) {
		if (dir) return -1;
		else byteOffset = buffer.length - 1;
	} else if (byteOffset < 0) {
		if (dir) byteOffset = 0;
		else return -1;
	}
	if (typeof val === "string") val = Buffer$2.from(val, encoding);
	if (Buffer$2.isBuffer(val)) {
		if (val.length === 0) return -1;
		return arrayIndexOf(buffer, val, byteOffset, encoding, dir);
	} else if (typeof val === "number") {
		val = val & 255;
		if (typeof Uint8Array.prototype.indexOf === "function") return dir ? Uint8Array.prototype.indexOf.call(buffer, val, byteOffset) : Uint8Array.prototype.lastIndexOf.call(buffer, val, byteOffset);
		return arrayIndexOf(buffer, [val], byteOffset, encoding, dir);
	}
	throw new TypeError("val must be string, number or Buffer");
}
function arrayIndexOf(arr, val, byteOffset, encoding, dir) {
	let indexSize = 1;
	let arrLength = arr.length;
	let valLength = val.length;
	if (encoding !== void 0) {
		encoding = String(encoding).toLowerCase();
		if (encoding === "ucs2" || encoding === "ucs-2" || encoding === "utf16le" || encoding === "utf-16le") {
			if (arr.length < 2 || val.length < 2) return -1;
			indexSize = 2;
			arrLength /= 2;
			valLength /= 2;
			byteOffset /= 2;
		}
	}
	function read(buf, i) {
		return indexSize === 1 ? buf[i] : buf.readUInt16BE(i * indexSize);
	}
	let i;
	if (dir) {
		let foundIndex = -1;
		for (i = byteOffset; i < arrLength; i++) if (read(arr, i) === read(val, foundIndex === -1 ? 0 : i - foundIndex)) {
			if (foundIndex === -1) foundIndex = i;
			if (i - foundIndex + 1 === valLength) return foundIndex * indexSize;
		} else {
			if (foundIndex !== -1) i -= i - foundIndex;
			foundIndex = -1;
		}
	} else {
		if (byteOffset + valLength > arrLength) byteOffset = arrLength - valLength;
		for (i = byteOffset; i >= 0; i--) {
			let found = true;
			for (let j = 0; j < valLength; j++) if (read(arr, i + j) !== read(val, j)) {
				found = false;
				break;
			}
			if (found) return i;
		}
	}
	return -1;
}
function hexWrite(buf, string, offset, length) {
	offset = Number(offset) || 0;
	const remaining = buf.length - offset;
	if (length) {
		length = Number(length);
		if (length > remaining) length = remaining;
	} else length = remaining;
	const strLen = string.length;
	if (length > strLen / 2) length = strLen / 2;
	let i = 0;
	for (; i < length; ++i) {
		const parsed = Number.parseInt(string.slice(i * 2, i * 2 + 2), 16);
		if (numberIsNaN(parsed)) return i;
		buf[offset + i] = parsed;
	}
	return i;
}
function utf8Write$1(buf, string, offset, length) {
	return blitBuffer(utf8ToBytes(string, buf.length - offset), buf, offset, length);
}
function asciiWrite(buf, string, offset, length) {
	return blitBuffer(asciiToBytes(string), buf, offset, length);
}
function base64Write(buf, string, offset, length) {
	return blitBuffer(base64ToBytes(string), buf, offset, length);
}
function ucs2Write(buf, string, offset, length) {
	return blitBuffer(utf16leToBytes(string, buf.length - offset), buf, offset, length);
}
function base64Slice(buf, start, end) {
	return start === 0 && end === buf.length ? fromByteArray(buf) : fromByteArray(buf.slice(start, end));
}
function utf8Slice(buf, start, end) {
	end = Math.min(buf.length, end);
	const res = [];
	let i = start;
	while (i < end) {
		const firstByte = buf[i];
		let codePoint = null;
		let bytesPerSequence = firstByte > 239 ? 4 : firstByte > 223 ? 3 : firstByte > 191 ? 2 : 1;
		if (i + bytesPerSequence <= end) {
			let secondByte, thirdByte, fourthByte, tempCodePoint;
			switch (bytesPerSequence) {
				case 1:
					if (firstByte < 128) codePoint = firstByte;
					break;
				case 2:
					secondByte = buf[i + 1];
					if ((secondByte & 192) === 128) {
						tempCodePoint = (firstByte & 31) << 6 | secondByte & 63;
						if (tempCodePoint > 127) codePoint = tempCodePoint;
					}
					break;
				case 3:
					secondByte = buf[i + 1];
					thirdByte = buf[i + 2];
					if ((secondByte & 192) === 128 && (thirdByte & 192) === 128) {
						tempCodePoint = (firstByte & 15) << 12 | (secondByte & 63) << 6 | thirdByte & 63;
						if (tempCodePoint > 2047 && (tempCodePoint < 55296 || tempCodePoint > 57343)) codePoint = tempCodePoint;
					}
					break;
				case 4:
					secondByte = buf[i + 1];
					thirdByte = buf[i + 2];
					fourthByte = buf[i + 3];
					if ((secondByte & 192) === 128 && (thirdByte & 192) === 128 && (fourthByte & 192) === 128) {
						tempCodePoint = (firstByte & 15) << 18 | (secondByte & 63) << 12 | (thirdByte & 63) << 6 | fourthByte & 63;
						if (tempCodePoint > 65535 && tempCodePoint < 1114112) codePoint = tempCodePoint;
					}
			}
		}
		if (codePoint === null) {
			codePoint = 65533;
			bytesPerSequence = 1;
		} else if (codePoint > 65535) {
			codePoint -= 65536;
			res.push(codePoint >>> 10 & 1023 | 55296);
			codePoint = 56320 | codePoint & 1023;
		}
		res.push(codePoint);
		i += bytesPerSequence;
	}
	return decodeCodePointsArray(res);
}
function decodeCodePointsArray(codePoints) {
	const len = codePoints.length;
	if (len <= MAX_ARGUMENTS_LENGTH) return String.fromCharCode.apply(String, codePoints);
	let res = "";
	let i = 0;
	while (i < len) res += String.fromCharCode.apply(String, codePoints.slice(i, i += MAX_ARGUMENTS_LENGTH));
	return res;
}
function asciiSlice(buf, start, end) {
	let ret = "";
	end = Math.min(buf.length, end);
	for (let i = start; i < end; ++i) ret += String.fromCharCode(buf[i] & 127);
	return ret;
}
function latin1Slice(buf, start, end) {
	let ret = "";
	end = Math.min(buf.length, end);
	for (let i = start; i < end; ++i) ret += String.fromCharCode(buf[i]);
	return ret;
}
function hexSlice(buf, start, end) {
	const len = buf.length;
	if (!start || start < 0) start = 0;
	if (!end || end < 0 || end > len) end = len;
	let out = "";
	for (let i = start; i < end; ++i) out += hexSliceLookupTable[buf[i]];
	return out;
}
function utf16leSlice(buf, start, end) {
	const bytes = buf.slice(start, end);
	let res = "";
	for (let i = 0; i < bytes.length - 1; i += 2) res += String.fromCharCode(bytes[i] + bytes[i + 1] * 256);
	return res;
}
function checkOffset(offset, ext, length) {
	if (offset % 1 !== 0 || offset < 0) throw new RangeError("offset is not uint");
	if (offset + ext > length) throw new RangeError("Trying to access beyond buffer length");
}
function checkInt(buf, value, offset, ext, max, min) {
	if (!Buffer$2.isBuffer(buf)) throw new TypeError("\"buffer\" argument must be a Buffer instance");
	if (value > max || value < min) throw new RangeError("\"value\" argument is out of bounds");
	if (offset + ext > buf.length) throw new RangeError("Index out of range");
}
function wrtBigUInt64LE(buf, value, offset, min, max) {
	checkIntBI(value, min, max, buf, offset, 7);
	let lo = Number(value & BigInt(4294967295));
	buf[offset++] = lo;
	lo = lo >> 8;
	buf[offset++] = lo;
	lo = lo >> 8;
	buf[offset++] = lo;
	lo = lo >> 8;
	buf[offset++] = lo;
	let hi = Number(value >> BigInt(32) & BigInt(4294967295));
	buf[offset++] = hi;
	hi = hi >> 8;
	buf[offset++] = hi;
	hi = hi >> 8;
	buf[offset++] = hi;
	hi = hi >> 8;
	buf[offset++] = hi;
	return offset;
}
function wrtBigUInt64BE(buf, value, offset, min, max) {
	checkIntBI(value, min, max, buf, offset, 7);
	let lo = Number(value & BigInt(4294967295));
	buf[offset + 7] = lo;
	lo = lo >> 8;
	buf[offset + 6] = lo;
	lo = lo >> 8;
	buf[offset + 5] = lo;
	lo = lo >> 8;
	buf[offset + 4] = lo;
	let hi = Number(value >> BigInt(32) & BigInt(4294967295));
	buf[offset + 3] = hi;
	hi = hi >> 8;
	buf[offset + 2] = hi;
	hi = hi >> 8;
	buf[offset + 1] = hi;
	hi = hi >> 8;
	buf[offset] = hi;
	return offset + 8;
}
function checkIEEE754(buf, value, offset, ext, max, min) {
	if (offset + ext > buf.length) throw new RangeError("Index out of range");
	if (offset < 0) throw new RangeError("Index out of range");
}
function writeFloat(buf, value, offset, littleEndian, noAssert) {
	value = +value;
	offset = offset >>> 0;
	if (!noAssert) checkIEEE754(buf, value, offset, 4, 34028234663852886e22, -34028234663852886e22);
	write$1(buf, value, offset, littleEndian, 23, 4);
	return offset + 4;
}
function writeDouble(buf, value, offset, littleEndian, noAssert) {
	value = +value;
	offset = offset >>> 0;
	if (!noAssert) checkIEEE754(buf, value, offset, 8, 17976931348623157e292, -17976931348623157e292);
	write$1(buf, value, offset, littleEndian, 52, 8);
	return offset + 8;
}
function E(sym, getMessage, Base) {
	errors[sym] = class NodeError extends Base {
		constructor() {
			super();
			Object.defineProperty(this, "message", {
				value: Reflect.apply(getMessage, this, arguments),
				writable: true,
				configurable: true
			});
			this.name = `${this.name} [${sym}]`;
			this.stack;
			delete this.name;
		}
		get code() {
			return sym;
		}
		set code(value) {
			Object.defineProperty(this, "code", {
				configurable: true,
				enumerable: true,
				value,
				writable: true
			});
		}
		toString() {
			return `${this.name} [${sym}]: ${this.message}`;
		}
	};
}
function addNumericalSeparator(val) {
	let res = "";
	let i = val.length;
	const start = val[0] === "-" ? 1 : 0;
	for (; i >= start + 4; i -= 3) res = `_${val.slice(i - 3, i)}${res}`;
	return `${val.slice(0, i)}${res}`;
}
function checkBounds(buf, offset, byteLength) {
	validateNumber(offset, "offset");
	if (buf[offset] === void 0 || buf[offset + byteLength] === void 0) boundsError(offset, buf.length - (byteLength + 1));
}
function checkIntBI(value, min, max, buf, offset, byteLength) {
	if (value > max || value < min) {
		const n = typeof min === "bigint" ? "n" : "";
		let range;
		if (byteLength > 3) range = min === 0 || min === BigInt(0) ? `>= 0${n} and < 2${n} ** ${(byteLength + 1) * 8}${n}` : `>= -(2${n} ** ${(byteLength + 1) * 8 - 1}${n}) and < 2 ** ${(byteLength + 1) * 8 - 1}${n}`;
		else range = `>= ${min}${n} and <= ${max}${n}`;
		throw new errors.ERR_OUT_OF_RANGE("value", range, value);
	}
	checkBounds(buf, offset, byteLength);
}
function validateNumber(value, name) {
	if (typeof value !== "number") throw new errors.ERR_INVALID_ARG_TYPE(name, "number", value);
}
function boundsError(value, length, type) {
	if (Math.floor(value) !== value) {
		validateNumber(value, type);
		throw new errors.ERR_OUT_OF_RANGE(type || "offset", "an integer", value);
	}
	if (length < 0) throw new errors.ERR_BUFFER_OUT_OF_BOUNDS();
	throw new errors.ERR_OUT_OF_RANGE(type || "offset", `>= ${type ? 1 : 0} and <= ${length}`, value);
}
function base64clean(str) {
	str = str.split("=")[0];
	str = str.trim().replace(INVALID_BASE64_RE, "");
	if (str.length < 2) return "";
	while (str.length % 4 !== 0) str = str + "=";
	return str;
}
function utf8ToBytes(string, units) {
	units = units || Number.POSITIVE_INFINITY;
	let codePoint;
	const length = string.length;
	let leadSurrogate = null;
	const bytes = [];
	for (let i = 0; i < length; ++i) {
		codePoint = string.charCodeAt(i);
		if (codePoint > 55295 && codePoint < 57344) {
			if (!leadSurrogate) {
				if (codePoint > 56319) {
					if ((units -= 3) > -1) bytes.push(239, 191, 189);
					continue;
				} else if (i + 1 === length) {
					if ((units -= 3) > -1) bytes.push(239, 191, 189);
					continue;
				}
				leadSurrogate = codePoint;
				continue;
			}
			if (codePoint < 56320) {
				if ((units -= 3) > -1) bytes.push(239, 191, 189);
				leadSurrogate = codePoint;
				continue;
			}
			codePoint = (leadSurrogate - 55296 << 10 | codePoint - 56320) + 65536;
		} else if (leadSurrogate && (units -= 3) > -1) bytes.push(239, 191, 189);
		leadSurrogate = null;
		if (codePoint < 128) {
			if ((units -= 1) < 0) break;
			bytes.push(codePoint);
		} else if (codePoint < 2048) {
			if ((units -= 2) < 0) break;
			bytes.push(codePoint >> 6 | 192, codePoint & 63 | 128);
		} else if (codePoint < 65536) {
			if ((units -= 3) < 0) break;
			bytes.push(codePoint >> 12 | 224, codePoint >> 6 & 63 | 128, codePoint & 63 | 128);
		} else if (codePoint < 1114112) {
			if ((units -= 4) < 0) break;
			bytes.push(codePoint >> 18 | 240, codePoint >> 12 & 63 | 128, codePoint >> 6 & 63 | 128, codePoint & 63 | 128);
		} else throw new Error$1("Invalid code point");
	}
	return bytes;
}
function asciiToBytes(str) {
	const byteArray = [];
	for (let i = 0; i < str.length; ++i) byteArray.push(str.charCodeAt(i) & 255);
	return byteArray;
}
function utf16leToBytes(str, units) {
	let c, hi, lo;
	const byteArray = [];
	for (let i = 0; i < str.length; ++i) {
		if ((units -= 2) < 0) break;
		c = str.charCodeAt(i);
		hi = c >> 8;
		lo = c % 256;
		byteArray.push(lo, hi);
	}
	return byteArray;
}
function base64ToBytes(str) {
	return toByteArray(base64clean(str));
}
function blitBuffer(src, dst, offset, length) {
	let i = 0;
	for (; i < length; ++i) {
		if (i + offset >= dst.length || i >= src.length) break;
		dst[i + offset] = src[i];
	}
	return i;
}
function isInstance(obj, type) {
	return obj instanceof type || obj != null && obj.constructor != null && obj.constructor.name != null && obj.constructor.name === type.name;
}
function numberIsNaN(obj) {
	return obj !== obj;
}
function defineBigIntMethod(fn) {
	return typeof BigInt === "undefined" ? BufferBigIntNotDefined : fn;
}
function BufferBigIntNotDefined() {
	throw new Error$1("BigInt not supported");
}
var customInspectSymbol, K_MAX_LENGTH, kMaxLength, MAX_ARGUMENTS_LENGTH, errors, INVALID_BASE64_RE, hexSliceLookupTable;
var init_buffer = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_console_globals();
	init_base64();
	init_ieee754();
	customInspectSymbol = typeof Symbol === "function" && typeof Symbol["for"] === "function" ? Symbol["for"]("nodejs.util.inspect.custom") : null;
	K_MAX_LENGTH = 2147483647;
	kMaxLength = K_MAX_LENGTH;
	/**
	* If `Buffer.TYPED_ARRAY_SUPPORT`:
	*   === true    Use Uint8Array implementation (fastest)
	*   === false   Print warning and recommend using `buffer` v4.x which has an Object
	*               implementation (most compatible, even IE6)
	*
	* Browsers that support typed arrays are IE 10+, Firefox 4+, Chrome 7+, Safari 5.1+,
	* Opera 11.6+, iOS 4.2+.
	*
	* We report that the browser does not support typed arrays if the are not subclassable
	* using __proto__. Firefox 4-29 lacks support for adding new properties to `Uint8Array`
	* (See: https://bugzilla.mozilla.org/show_bug.cgi?id=695438). IE 10 lacks support
	* for __proto__ and has a buggy typed array implementation.
	*/
	Buffer$2.TYPED_ARRAY_SUPPORT = typedArraySupport();
	if (!Buffer$2.TYPED_ARRAY_SUPPORT && typeof _jco_node_builtin_console_globals_default !== "undefined" && typeof _jco_node_builtin_console_globals_default.error === "function") _jco_node_builtin_console_globals_default.error("This environment lacks typed array (Uint8Array) support which is required by `buffer` v5.x. Use `buffer` v4.x if you require old browser support.");
	Object.defineProperty(Buffer$2.prototype, "parent", {
		enumerable: true,
		get: function() {
			if (!Buffer$2.isBuffer(this)) return;
			return this.buffer;
		}
	});
	Object.defineProperty(Buffer$2.prototype, "offset", {
		enumerable: true,
		get: function() {
			if (!Buffer$2.isBuffer(this)) return;
			return this.byteOffset;
		}
	});
	Buffer$2.poolSize = 8192;
	/**
	* Functionally equivalent to Buffer(arg, encoding) but throws a TypeError
	* if value is a number.
	* Buffer.from(str[, encoding])
	* Buffer.from(array)
	* Buffer.from(buffer)
	* Buffer.from(arrayBuffer[, byteOffset[, length]])
	**/
	Buffer$2.from = function(value, encodingOrOffset, length) {
		return from$1(value, encodingOrOffset, length);
	};
	Object.setPrototypeOf(Buffer$2.prototype, Uint8Array.prototype);
	Object.setPrototypeOf(Buffer$2, Uint8Array);
	/**
	* Creates a new filled Buffer instance.
	* alloc(size[, fill[, encoding]])
	**/
	Buffer$2.alloc = function(size, fill, encoding) {
		return alloc(size, fill, encoding);
	};
	/**
	* Equivalent to Buffer(num), by default creates a non-zero-filled Buffer instance.
	* */
	Buffer$2.allocUnsafe = function(size) {
		return allocUnsafe(size);
	};
	/**
	* Equivalent to SlowBuffer(num), by default creates a non-zero-filled Buffer instance.
	*/
	Buffer$2.allocUnsafeSlow = function(size) {
		return allocUnsafe(size);
	};
	Buffer$2.isBuffer = function isBuffer(b) {
		return b != null && b._isBuffer === true && b !== Buffer$2.prototype;
	};
	Buffer$2.compare = function compare(a, b) {
		if (isInstance(a, Uint8Array)) a = Buffer$2.from(a, a.offset, a.byteLength);
		if (isInstance(b, Uint8Array)) b = Buffer$2.from(b, b.offset, b.byteLength);
		if (!Buffer$2.isBuffer(a) || !Buffer$2.isBuffer(b)) throw new TypeError("The \"buf1\", \"buf2\" arguments must be one of type Buffer or Uint8Array");
		if (a === b) return 0;
		let x = a.length;
		let y = b.length;
		for (let i = 0, len = Math.min(x, y); i < len; ++i) if (a[i] !== b[i]) {
			x = a[i];
			y = b[i];
			break;
		}
		if (x < y) return -1;
		if (y < x) return 1;
		return 0;
	};
	Buffer$2.isEncoding = function isEncoding(encoding) {
		switch (String(encoding).toLowerCase()) {
			case "hex":
			case "utf8":
			case "utf-8":
			case "ascii":
			case "latin1":
			case "binary":
			case "base64":
			case "ucs2":
			case "ucs-2":
			case "utf16le":
			case "utf-16le": return true;
			default: return false;
		}
	};
	Buffer$2.concat = function concat(list, length) {
		if (!Array.isArray(list)) throw new TypeError("\"list\" argument must be an Array of Buffers");
		if (list.length === 0) return Buffer$2.alloc(0);
		let i;
		if (length === void 0) {
			length = 0;
			for (i = 0; i < list.length; ++i) length += list[i].length;
		}
		const buffer = Buffer$2.allocUnsafe(length);
		let pos = 0;
		for (i = 0; i < list.length; ++i) {
			let buf = list[i];
			if (isInstance(buf, Uint8Array)) {
				if (pos + buf.length > buffer.length) {
					if (!Buffer$2.isBuffer(buf)) buf = Buffer$2.from(buf.buffer, buf.byteOffset, buf.byteLength);
					buf.copy(buffer, pos);
				} else Uint8Array.prototype.set.call(buffer, buf, pos);
			} else if (Buffer$2.isBuffer(buf)) buf.copy(buffer, pos);
			else throw new TypeError("\"list\" argument must be an Array of Buffers");
			pos += buf.length;
		}
		return buffer;
	};
	Buffer$2.byteLength = byteLength;
	Buffer$2.prototype._isBuffer = true;
	Buffer$2.prototype.swap16 = function swap16() {
		const len = this.length;
		if (len % 2 !== 0) throw new RangeError("Buffer size must be a multiple of 16-bits");
		for (let i = 0; i < len; i += 2) swap(this, i, i + 1);
		return this;
	};
	Buffer$2.prototype.swap32 = function swap32() {
		const len = this.length;
		if (len % 4 !== 0) throw new RangeError("Buffer size must be a multiple of 32-bits");
		for (let i = 0; i < len; i += 4) {
			swap(this, i, i + 3);
			swap(this, i + 1, i + 2);
		}
		return this;
	};
	Buffer$2.prototype.swap64 = function swap64() {
		const len = this.length;
		if (len % 8 !== 0) throw new RangeError("Buffer size must be a multiple of 64-bits");
		for (let i = 0; i < len; i += 8) {
			swap(this, i, i + 7);
			swap(this, i + 1, i + 6);
			swap(this, i + 2, i + 5);
			swap(this, i + 3, i + 4);
		}
		return this;
	};
	Buffer$2.prototype.toString = function toString() {
		const length = this.length;
		if (length === 0) return "";
		if (arguments.length === 0) return utf8Slice(this, 0, length);
		return Reflect.apply(slowToString, this, arguments);
	};
	Buffer$2.prototype.toLocaleString = Buffer$2.prototype.toString;
	Buffer$2.prototype.equals = function equals(b) {
		if (!Buffer$2.isBuffer(b)) throw new TypeError("Argument must be a Buffer");
		if (this === b) return true;
		return Buffer$2.compare(this, b) === 0;
	};
	Buffer$2.prototype.inspect = function inspect() {
		let str = "";
		const max = 50;
		str = this.toString("hex", 0, max).replace(/(.{2})/g, "$1 ").trim();
		if (this.length > max) str += " ... ";
		return "<Buffer " + str + ">";
	};
	if (customInspectSymbol) Buffer$2.prototype[customInspectSymbol] = Buffer$2.prototype.inspect;
	Buffer$2.prototype.compare = function compare(target, start, end, thisStart, thisEnd) {
		if (isInstance(target, Uint8Array)) target = Buffer$2.from(target, target.offset, target.byteLength);
		if (!Buffer$2.isBuffer(target)) throw new TypeError("The \"target\" argument must be one of type Buffer or Uint8Array. Received type " + typeof target);
		if (start === void 0) start = 0;
		if (end === void 0) end = target ? target.length : 0;
		if (thisStart === void 0) thisStart = 0;
		if (thisEnd === void 0) thisEnd = this.length;
		if (start < 0 || end > target.length || thisStart < 0 || thisEnd > this.length) throw new RangeError("out of range index");
		if (thisStart >= thisEnd && start >= end) return 0;
		if (thisStart >= thisEnd) return -1;
		if (start >= end) return 1;
		start >>>= 0;
		end >>>= 0;
		thisStart >>>= 0;
		thisEnd >>>= 0;
		if (this === target) return 0;
		let x = thisEnd - thisStart;
		let y = end - start;
		const len = Math.min(x, y);
		const thisCopy = this.slice(thisStart, thisEnd);
		const targetCopy = target.slice(start, end);
		for (let i = 0; i < len; ++i) if (thisCopy[i] !== targetCopy[i]) {
			x = thisCopy[i];
			y = targetCopy[i];
			break;
		}
		if (x < y) return -1;
		if (y < x) return 1;
		return 0;
	};
	Buffer$2.prototype.includes = function includes(val, byteOffset, encoding) {
		return this.indexOf(val, byteOffset, encoding) !== -1;
	};
	Buffer$2.prototype.indexOf = function indexOf(val, byteOffset, encoding) {
		return bidirectionalIndexOf(this, val, byteOffset, encoding, true);
	};
	Buffer$2.prototype.lastIndexOf = function lastIndexOf(val, byteOffset, encoding) {
		return bidirectionalIndexOf(this, val, byteOffset, encoding, false);
	};
	Buffer$2.prototype.write = function write(string, offset, length, encoding) {
		if (offset === void 0) {
			encoding = "utf8";
			length = this.length;
			offset = 0;
		} else if (length === void 0 && typeof offset === "string") {
			encoding = offset;
			length = this.length;
			offset = 0;
		} else if (Number.isFinite(offset)) {
			offset = offset >>> 0;
			if (Number.isFinite(length)) {
				length = length >>> 0;
				if (encoding === void 0) encoding = "utf8";
			} else {
				encoding = length;
				length = void 0;
			}
		} else throw new TypeError("Buffer.write(string, encoding, offset[, length]) is no longer supported");
		const remaining = this.length - offset;
		if (length === void 0 || length > remaining) length = remaining;
		if (string.length > 0 && (length < 0 || offset < 0) || offset > this.length) throw new RangeError("Attempt to write outside buffer bounds");
		if (!encoding) encoding = "utf8";
		let loweredCase = false;
		for (;;) switch (encoding) {
			case "hex": return hexWrite(this, string, offset, length);
			case "utf8":
			case "utf-8": return utf8Write$1(this, string, offset, length);
			case "ascii":
			case "latin1":
			case "binary": return asciiWrite(this, string, offset, length);
			case "base64": return base64Write(this, string, offset, length);
			case "ucs2":
			case "ucs-2":
			case "utf16le":
			case "utf-16le": return ucs2Write(this, string, offset, length);
			default:
				if (loweredCase) throw new TypeError("Unknown encoding: " + encoding);
				encoding = ("" + encoding).toLowerCase();
				loweredCase = true;
		}
	};
	Buffer$2.prototype.toJSON = function toJSON() {
		return {
			type: "Buffer",
			data: Array.prototype.slice.call(this._arr || this, 0)
		};
	};
	MAX_ARGUMENTS_LENGTH = 4096;
	Buffer$2.prototype.slice = function slice(start, end) {
		const len = this.length;
		start = Math.trunc(start);
		end = end === void 0 ? len : Math.trunc(end);
		if (start < 0) {
			start += len;
			if (start < 0) start = 0;
		} else if (start > len) start = len;
		if (end < 0) {
			end += len;
			if (end < 0) end = 0;
		} else if (end > len) end = len;
		if (end < start) end = start;
		const newBuf = this.subarray(start, end);
		Object.setPrototypeOf(newBuf, Buffer$2.prototype);
		return newBuf;
	};
	Buffer$2.prototype.readUintLE = Buffer$2.prototype.readUIntLE = function readUIntLE(offset, byteLength, noAssert) {
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) checkOffset(offset, byteLength, this.length);
		let val = this[offset];
		let mul = 1;
		let i = 0;
		while (++i < byteLength && (mul *= 256)) val += this[offset + i] * mul;
		return val;
	};
	Buffer$2.prototype.readUintBE = Buffer$2.prototype.readUIntBE = function readUIntBE(offset, byteLength, noAssert) {
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) checkOffset(offset, byteLength, this.length);
		let val = this[offset + --byteLength];
		let mul = 1;
		while (byteLength > 0 && (mul *= 256)) val += this[offset + --byteLength] * mul;
		return val;
	};
	Buffer$2.prototype.readUint8 = Buffer$2.prototype.readUInt8 = function readUInt8(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 1, this.length);
		return this[offset];
	};
	Buffer$2.prototype.readUint16LE = Buffer$2.prototype.readUInt16LE = function readUInt16LE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 2, this.length);
		return this[offset] | this[offset + 1] << 8;
	};
	Buffer$2.prototype.readUint16BE = Buffer$2.prototype.readUInt16BE = function readUInt16BE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 2, this.length);
		return this[offset] << 8 | this[offset + 1];
	};
	Buffer$2.prototype.readUint32LE = Buffer$2.prototype.readUInt32LE = function readUInt32LE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return (this[offset] | this[offset + 1] << 8 | this[offset + 2] << 16) + this[offset + 3] * 16777216;
	};
	Buffer$2.prototype.readUint32BE = Buffer$2.prototype.readUInt32BE = function readUInt32BE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return this[offset] * 16777216 + (this[offset + 1] << 16 | this[offset + 2] << 8 | this[offset + 3]);
	};
	Buffer$2.prototype.readBigUInt64LE = defineBigIntMethod(function readBigUInt64LE(offset) {
		offset = offset >>> 0;
		validateNumber(offset, "offset");
		const first = this[offset];
		const last = this[offset + 7];
		if (first === void 0 || last === void 0) boundsError(offset, this.length - 8);
		const lo = first + this[++offset] * 256 + this[++offset] * 2 ** 16 + this[++offset] * 2 ** 24;
		const hi = this[++offset] + this[++offset] * 256 + this[++offset] * 2 ** 16 + last * 2 ** 24;
		return BigInt(lo) + (BigInt(hi) << BigInt(32));
	});
	Buffer$2.prototype.readBigUInt64BE = defineBigIntMethod(function readBigUInt64BE(offset) {
		offset = offset >>> 0;
		validateNumber(offset, "offset");
		const first = this[offset];
		const last = this[offset + 7];
		if (first === void 0 || last === void 0) boundsError(offset, this.length - 8);
		const hi = first * 2 ** 24 + this[++offset] * 2 ** 16 + this[++offset] * 256 + this[++offset];
		const lo = this[++offset] * 2 ** 24 + this[++offset] * 2 ** 16 + this[++offset] * 256 + last;
		return (BigInt(hi) << BigInt(32)) + BigInt(lo);
	});
	Buffer$2.prototype.readIntLE = function readIntLE(offset, byteLength, noAssert) {
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) checkOffset(offset, byteLength, this.length);
		let val = this[offset];
		let mul = 1;
		let i = 0;
		while (++i < byteLength && (mul *= 256)) val += this[offset + i] * mul;
		mul *= 128;
		if (val >= mul) val -= Math.pow(2, 8 * byteLength);
		return val;
	};
	Buffer$2.prototype.readIntBE = function readIntBE(offset, byteLength, noAssert) {
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) checkOffset(offset, byteLength, this.length);
		let i = byteLength;
		let mul = 1;
		let val = this[offset + --i];
		while (i > 0 && (mul *= 256)) val += this[offset + --i] * mul;
		mul *= 128;
		if (val >= mul) val -= Math.pow(2, 8 * byteLength);
		return val;
	};
	Buffer$2.prototype.readInt8 = function readInt8(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 1, this.length);
		if (!(this[offset] & 128)) return this[offset];
		return (255 - this[offset] + 1) * -1;
	};
	Buffer$2.prototype.readInt16LE = function readInt16LE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 2, this.length);
		const val = this[offset] | this[offset + 1] << 8;
		return val & 32768 ? val | 4294901760 : val;
	};
	Buffer$2.prototype.readInt16BE = function readInt16BE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 2, this.length);
		const val = this[offset + 1] | this[offset] << 8;
		return val & 32768 ? val | 4294901760 : val;
	};
	Buffer$2.prototype.readInt32LE = function readInt32LE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return this[offset] | this[offset + 1] << 8 | this[offset + 2] << 16 | this[offset + 3] << 24;
	};
	Buffer$2.prototype.readInt32BE = function readInt32BE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return this[offset] << 24 | this[offset + 1] << 16 | this[offset + 2] << 8 | this[offset + 3];
	};
	Buffer$2.prototype.readBigInt64LE = defineBigIntMethod(function readBigInt64LE(offset) {
		offset = offset >>> 0;
		validateNumber(offset, "offset");
		const first = this[offset];
		const last = this[offset + 7];
		if (first === void 0 || last === void 0) boundsError(offset, this.length - 8);
		const val = this[offset + 4] + this[offset + 5] * 256 + this[offset + 6] * 2 ** 16 + (last << 24);
		return (BigInt(val) << BigInt(32)) + BigInt(first + this[++offset] * 256 + this[++offset] * 2 ** 16 + this[++offset] * 2 ** 24);
	});
	Buffer$2.prototype.readBigInt64BE = defineBigIntMethod(function readBigInt64BE(offset) {
		offset = offset >>> 0;
		validateNumber(offset, "offset");
		const first = this[offset];
		const last = this[offset + 7];
		if (first === void 0 || last === void 0) boundsError(offset, this.length - 8);
		const val = (first << 24) + this[++offset] * 2 ** 16 + this[++offset] * 256 + this[++offset];
		return (BigInt(val) << BigInt(32)) + BigInt(this[++offset] * 2 ** 24 + this[++offset] * 2 ** 16 + this[++offset] * 256 + last);
	});
	Buffer$2.prototype.readFloatLE = function readFloatLE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return read(this, offset, true, 23, 4);
	};
	Buffer$2.prototype.readFloatBE = function readFloatBE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 4, this.length);
		return read(this, offset, false, 23, 4);
	};
	Buffer$2.prototype.readDoubleLE = function readDoubleLE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 8, this.length);
		return read(this, offset, true, 52, 8);
	};
	Buffer$2.prototype.readDoubleBE = function readDoubleBE(offset, noAssert) {
		offset = offset >>> 0;
		if (!noAssert) checkOffset(offset, 8, this.length);
		return read(this, offset, false, 52, 8);
	};
	Buffer$2.prototype.writeUintLE = Buffer$2.prototype.writeUIntLE = function writeUIntLE(value, offset, byteLength, noAssert) {
		value = +value;
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) {
			const maxBytes = Math.pow(2, 8 * byteLength) - 1;
			checkInt(this, value, offset, byteLength, maxBytes, 0);
		}
		let mul = 1;
		let i = 0;
		this[offset] = value & 255;
		while (++i < byteLength && (mul *= 256)) this[offset + i] = value / mul & 255;
		return offset + byteLength;
	};
	Buffer$2.prototype.writeUintBE = Buffer$2.prototype.writeUIntBE = function writeUIntBE(value, offset, byteLength, noAssert) {
		value = +value;
		offset = offset >>> 0;
		byteLength = byteLength >>> 0;
		if (!noAssert) {
			const maxBytes = Math.pow(2, 8 * byteLength) - 1;
			checkInt(this, value, offset, byteLength, maxBytes, 0);
		}
		let i = byteLength - 1;
		let mul = 1;
		this[offset + i] = value & 255;
		while (--i >= 0 && (mul *= 256)) this[offset + i] = value / mul & 255;
		return offset + byteLength;
	};
	Buffer$2.prototype.writeUint8 = Buffer$2.prototype.writeUInt8 = function writeUInt8(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 1, 255, 0);
		this[offset] = value & 255;
		return offset + 1;
	};
	Buffer$2.prototype.writeUint16LE = Buffer$2.prototype.writeUInt16LE = function writeUInt16LE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 2, 65535, 0);
		this[offset] = value & 255;
		this[offset + 1] = value >>> 8;
		return offset + 2;
	};
	Buffer$2.prototype.writeUint16BE = Buffer$2.prototype.writeUInt16BE = function writeUInt16BE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 2, 65535, 0);
		this[offset] = value >>> 8;
		this[offset + 1] = value & 255;
		return offset + 2;
	};
	Buffer$2.prototype.writeUint32LE = Buffer$2.prototype.writeUInt32LE = function writeUInt32LE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 4, 4294967295, 0);
		this[offset + 3] = value >>> 24;
		this[offset + 2] = value >>> 16;
		this[offset + 1] = value >>> 8;
		this[offset] = value & 255;
		return offset + 4;
	};
	Buffer$2.prototype.writeUint32BE = Buffer$2.prototype.writeUInt32BE = function writeUInt32BE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 4, 4294967295, 0);
		this[offset] = value >>> 24;
		this[offset + 1] = value >>> 16;
		this[offset + 2] = value >>> 8;
		this[offset + 3] = value & 255;
		return offset + 4;
	};
	Buffer$2.prototype.writeBigUInt64LE = defineBigIntMethod(function writeBigUInt64LE(value, offset = 0) {
		return wrtBigUInt64LE(this, value, offset, BigInt(0), BigInt("0xffffffffffffffff"));
	});
	Buffer$2.prototype.writeBigUInt64BE = defineBigIntMethod(function writeBigUInt64BE(value, offset = 0) {
		return wrtBigUInt64BE(this, value, offset, BigInt(0), BigInt("0xffffffffffffffff"));
	});
	Buffer$2.prototype.writeIntLE = function writeIntLE(value, offset, byteLength, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) {
			const limit = Math.pow(2, 8 * byteLength - 1);
			checkInt(this, value, offset, byteLength, limit - 1, -limit);
		}
		let i = 0;
		let mul = 1;
		let sub = 0;
		this[offset] = value & 255;
		while (++i < byteLength && (mul *= 256)) {
			if (value < 0 && sub === 0 && this[offset + i - 1] !== 0) sub = 1;
			this[offset + i] = Math.trunc(value / mul) - sub & 255;
		}
		return offset + byteLength;
	};
	Buffer$2.prototype.writeIntBE = function writeIntBE(value, offset, byteLength, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) {
			const limit = Math.pow(2, 8 * byteLength - 1);
			checkInt(this, value, offset, byteLength, limit - 1, -limit);
		}
		let i = byteLength - 1;
		let mul = 1;
		let sub = 0;
		this[offset + i] = value & 255;
		while (--i >= 0 && (mul *= 256)) {
			if (value < 0 && sub === 0 && this[offset + i + 1] !== 0) sub = 1;
			this[offset + i] = Math.trunc(value / mul) - sub & 255;
		}
		return offset + byteLength;
	};
	Buffer$2.prototype.writeInt8 = function writeInt8(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 1, 127, -128);
		if (value < 0) value = 255 + value + 1;
		this[offset] = value & 255;
		return offset + 1;
	};
	Buffer$2.prototype.writeInt16LE = function writeInt16LE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 2, 32767, -32768);
		this[offset] = value & 255;
		this[offset + 1] = value >>> 8;
		return offset + 2;
	};
	Buffer$2.prototype.writeInt16BE = function writeInt16BE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 2, 32767, -32768);
		this[offset] = value >>> 8;
		this[offset + 1] = value & 255;
		return offset + 2;
	};
	Buffer$2.prototype.writeInt32LE = function writeInt32LE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 4, 2147483647, -2147483648);
		this[offset] = value & 255;
		this[offset + 1] = value >>> 8;
		this[offset + 2] = value >>> 16;
		this[offset + 3] = value >>> 24;
		return offset + 4;
	};
	Buffer$2.prototype.writeInt32BE = function writeInt32BE(value, offset, noAssert) {
		value = +value;
		offset = offset >>> 0;
		if (!noAssert) checkInt(this, value, offset, 4, 2147483647, -2147483648);
		if (value < 0) value = 4294967295 + value + 1;
		this[offset] = value >>> 24;
		this[offset + 1] = value >>> 16;
		this[offset + 2] = value >>> 8;
		this[offset + 3] = value & 255;
		return offset + 4;
	};
	Buffer$2.prototype.writeBigInt64LE = defineBigIntMethod(function writeBigInt64LE(value, offset = 0) {
		return wrtBigUInt64LE(this, value, offset, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
	});
	Buffer$2.prototype.writeBigInt64BE = defineBigIntMethod(function writeBigInt64BE(value, offset = 0) {
		return wrtBigUInt64BE(this, value, offset, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
	});
	Buffer$2.prototype.writeFloatLE = function writeFloatLE(value, offset, noAssert) {
		return writeFloat(this, value, offset, true, noAssert);
	};
	Buffer$2.prototype.writeFloatBE = function writeFloatBE(value, offset, noAssert) {
		return writeFloat(this, value, offset, false, noAssert);
	};
	Buffer$2.prototype.writeDoubleLE = function writeDoubleLE(value, offset, noAssert) {
		return writeDouble(this, value, offset, true, noAssert);
	};
	Buffer$2.prototype.writeDoubleBE = function writeDoubleBE(value, offset, noAssert) {
		return writeDouble(this, value, offset, false, noAssert);
	};
	Buffer$2.prototype.copy = function copy(target, targetStart, start, end) {
		if (!Buffer$2.isBuffer(target)) throw new TypeError("argument should be a Buffer");
		if (!start) start = 0;
		if (!end && end !== 0) end = this.length;
		if (targetStart >= target.length) targetStart = target.length;
		if (!targetStart) targetStart = 0;
		if (end > 0 && end < start) end = start;
		if (end === start) return 0;
		if (target.length === 0 || this.length === 0) return 0;
		if (targetStart < 0) throw new RangeError("targetStart out of bounds");
		if (start < 0 || start >= this.length) throw new RangeError("Index out of range");
		if (end < 0) throw new RangeError("sourceEnd out of bounds");
		if (end > this.length) end = this.length;
		if (target.length - targetStart < end - start) end = target.length - targetStart + start;
		const len = end - start;
		if (this === target && typeof Uint8Array.prototype.copyWithin === "function") this.copyWithin(targetStart, start, end);
		else Uint8Array.prototype.set.call(target, this.subarray(start, end), targetStart);
		return len;
	};
	Buffer$2.prototype.fill = function fill(val, start, end, encoding) {
		if (typeof val === "string") {
			if (typeof start === "string") {
				encoding = start;
				start = 0;
				end = this.length;
			} else if (typeof end === "string") {
				encoding = end;
				end = this.length;
			}
			if (encoding !== void 0 && typeof encoding !== "string") throw new TypeError("encoding must be a string");
			if (typeof encoding === "string" && !Buffer$2.isEncoding(encoding)) throw new TypeError("Unknown encoding: " + encoding);
			if (val.length === 1) {
				const code = val.charCodeAt(0);
				if (encoding === "utf8" && code < 128 || encoding === "latin1") val = code;
			}
		} else if (typeof val === "number") val = val & 255;
		else if (typeof val === "boolean") val = Number(val);
		if (start < 0 || this.length < start || this.length < end) throw new RangeError("Out of range index");
		if (end <= start) return this;
		start = start >>> 0;
		end = end === void 0 ? this.length : end >>> 0;
		if (!val) val = 0;
		let i;
		if (typeof val === "number") for (i = start; i < end; ++i) this[i] = val;
		else {
			const bytes = Buffer$2.isBuffer(val) ? val : Buffer$2.from(val, encoding);
			const len = bytes.length;
			if (len === 0) throw new TypeError("The value \"" + val + "\" is invalid for argument \"value\"");
			for (i = 0; i < end - start; ++i) this[i + start] = bytes[i % len];
		}
		return this;
	};
	errors = {};
	E("ERR_BUFFER_OUT_OF_BOUNDS", function(name) {
		if (name) return `${name} is outside of buffer bounds`;
		return "Attempt to access memory outside buffer bounds";
	}, RangeError);
	E("ERR_INVALID_ARG_TYPE", function(name, actual) {
		return `The "${name}" argument must be of type number. Received type ${typeof actual}`;
	}, TypeError);
	E("ERR_OUT_OF_RANGE", function(str, range, input) {
		let msg = `The value of "${str}" is out of range.`;
		let received = input;
		if (Number.isInteger(input) && Math.abs(input) > 2 ** 32) received = addNumericalSeparator(String(input));
		else if (typeof input === "bigint") {
			received = String(input);
			if (input > BigInt(2) ** BigInt(32) || input < -(BigInt(2) ** BigInt(32))) received = addNumericalSeparator(received);
			received += "n";
		}
		msg += ` It must be ${range}. Received ${received}`;
		return msg;
	}, RangeError);
	INVALID_BASE64_RE = /[^\w+/-]/g;
	hexSliceLookupTable = (function() {
		const alphabet = "0123456789abcdef";
		const table = Array.from({ length: 256 });
		for (let i = 0; i < 16; ++i) {
			const i16 = i * 16;
			for (let j = 0; j < 16; ++j) table[i16 + j] = alphabet[i] + alphabet[j];
		}
		return table;
	})();
});
// \0jco-node-builtin:unenv-buffer-core
function deprecatedBufferConstructor() {
	const error = new Error$1("The deprecated Buffer() constructor is not supported; use Buffer.alloc(), Buffer.allocUnsafe(), or Buffer.from() instead");
	error.code = "ERR_JCO_UNSUPPORTED_DEPRECATED_NODE_API";
	throw error;
}
function unsupported$1(api) {
	const error = new Error$1(api + " is not supported by the Jco component runtime");
	error.code = "ERR_JCO_UNSUPPORTED_NODE_API";
	throw error;
}
function byteView(value) {
	if (value instanceof ArrayBuffer) return new Uint8Array(value);
	if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
	const error = new TypeError("The \"input\" argument must be an ArrayBuffer, Buffer, TypedArray, or DataView");
	error.code = "ERR_INVALID_ARG_TYPE";
	throw error;
}
var _globalThis$Blob, _globalThis$File, _globalThis$atob$bind, _globalThis$atob, _globalThis$btoa$bind, _globalThis$btoa, Buffer$1, toString, from, isEncoding, SlowBuffer, Blob, File, kStringMaxLength, constants, atob, btoa, isAscii, isUtf8, resolveObjectURL, transcode, _jco_node_builtin_unenv_buffer_core_default;
var init__jco_node_builtin_unenv_buffer_core = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_text_encoding();
	init_buffer();
	Buffer$1 = new Proxy(Buffer$2, {
		apply: deprecatedBufferConstructor,
		construct: deprecatedBufferConstructor
	});
	Buffer$1.prototype.constructor = Buffer$1;
	Object.defineProperty(Buffer$1, Symbol.species, { value: Buffer$2 });
	toString = Buffer$2.prototype.toString;
	Buffer$2.prototype.toString = function(encoding, ...args) {
		const value = Reflect.apply(toString, this, [encoding === "base64url" ? "base64" : encoding, ...args]);
		return encoding === "base64url" ? value.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "") : value;
	};
	from = Buffer$2.from;
	Buffer$2.from = function(value, encoding, ...args) {
		return Reflect.apply(from, this, [
			value,
			encoding === "base64url" ? "base64" : encoding,
			...args
		]);
	};
	isEncoding = Buffer$2.isEncoding;
	Buffer$2.isEncoding = (encoding) => encoding === "base64url" || isEncoding(encoding);
	for (const name of ["write", "fill"]) {
		const original = Buffer$2.prototype[name];
		Buffer$2.prototype[name] = function(...args) {
			if (args.at(-1) === "base64url") args[args.length - 1] = "base64";
			return Reflect.apply(original, this, args);
		};
	}
	for (const name of ["byteLength", "alloc"]) {
		const original = Buffer$2[name];
		Buffer$2[name] = function(...args) {
			if (args.at(-1) === "base64url") args[args.length - 1] = "base64";
			return Reflect.apply(original, this, args);
		};
	}
	for (const [name, encoding] of Object.entries({
		latin1: "latin1",
		utf8: "utf8",
		ascii: "ascii",
		base64: "base64",
		base64url: "base64url",
		ucs2: "utf16le",
		hex: "hex"
	})) Buffer$2.prototype[name + "Slice"] = function(start, end) {
		return this.toString(encoding, start, end);
	};
	SlowBuffer = new Proxy(function SlowBuffer() {}, {
		apply: deprecatedBufferConstructor,
		construct: deprecatedBufferConstructor
	});
	Blob = (_globalThis$Blob = globalThis.Blob) !== null && _globalThis$Blob !== void 0 ? _globalThis$Blob : class Blob {
		constructor() {
			unsupported$1("buffer.Blob");
		}
	};
	File = (_globalThis$File = globalThis.File) !== null && _globalThis$File !== void 0 ? _globalThis$File : class File {
		constructor() {
			unsupported$1("buffer.File");
		}
	};
	kStringMaxLength = 536870888;
	constants = {
		MAX_LENGTH: Number.MAX_SAFE_INTEGER,
		MAX_STRING_LENGTH: kStringMaxLength
	};
	atob = (_globalThis$atob$bind = (_globalThis$atob = globalThis.atob) === null || _globalThis$atob === void 0 ? void 0 : _globalThis$atob.bind(globalThis)) !== null && _globalThis$atob$bind !== void 0 ? _globalThis$atob$bind : ((value) => Buffer$2.from(value, "base64").toString("latin1"));
	btoa = (_globalThis$btoa$bind = (_globalThis$btoa = globalThis.btoa) === null || _globalThis$btoa === void 0 ? void 0 : _globalThis$btoa.bind(globalThis)) !== null && _globalThis$btoa$bind !== void 0 ? _globalThis$btoa$bind : ((value) => Buffer$2.from(value, "latin1").toString("base64"));
	isAscii = (value) => byteView(value).every((byte) => byte < 128);
	isUtf8 = (value) => {
		const bytes = byteView(value);
		try {
			new TextDecoder("utf-8", { fatal: true }).decode(bytes);
			return true;
		} catch (_unused) {
			return false;
		}
	};
	resolveObjectURL = () => unsupported$1("buffer.resolveObjectURL");
	transcode = () => unsupported$1("buffer.transcode");
	globalThis.Buffer = Buffer$1;
	_jco_node_builtin_unenv_buffer_core_default = {
		atob,
		Blob,
		Buffer: Buffer$1,
		btoa,
		constants,
		File,
		INSPECT_MAX_BYTES: 50,
		isAscii,
		isUtf8,
		kMaxLength,
		kStringMaxLength,
		resolveObjectURL,
		SlowBuffer,
		transcode
	};
});
// \0jco-node-builtin:node:buffer
var _jco_node_builtin_node_buffer_exports = /* @__PURE__ */ __exportAll({
	Blob: () => Blob,
	Buffer: () => Buffer$1,
	File: () => File,
	INSPECT_MAX_BYTES: () => 50,
	SlowBuffer: () => SlowBuffer,
	atob: () => atob,
	btoa: () => btoa,
	constants: () => constants,
	default: () => _jco_node_builtin_unenv_buffer_core_default,
	isAscii: () => isAscii,
	isUtf8: () => isUtf8,
	kMaxLength: () => kMaxLength,
	kStringMaxLength: () => kStringMaxLength,
	resolveObjectURL: () => resolveObjectURL,
	transcode: () => transcode
});
var init__jco_node_builtin_node_buffer = __esmMin(() => {
	init__jco_node_builtin_unenv_buffer_core();
	init__jco_node_builtin_unenv_buffer_core();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/ours/primordials.js
var require_primordials = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init__jco_node_builtin_error_globals();
	var AggregateError = class extends Error$1 {
		constructor(errors) {
			if (!Array.isArray(errors)) throw new TypeError(`Expected input to be an Array, got ${typeof errors}`);
			let message = "";
			for (let i = 0; i < errors.length; i++) message += `    ${errors[i].stack}\n`;
			super(message);
			this.name = "AggregateError";
			this.errors = errors;
		}
	};
	module.exports = {
		AggregateError,
		ArrayIsArray(self) {
			return Array.isArray(self);
		},
		ArrayPrototypeIncludes(self, el) {
			return self.includes(el);
		},
		ArrayPrototypeIndexOf(self, el) {
			return self.indexOf(el);
		},
		ArrayPrototypeJoin(self, sep) {
			return self.join(sep);
		},
		ArrayPrototypeMap(self, fn) {
			return self.map(fn);
		},
		ArrayPrototypePop(self, el) {
			return self.pop(el);
		},
		ArrayPrototypePush(self, el) {
			return self.push(el);
		},
		ArrayPrototypeSlice(self, start, end) {
			return self.slice(start, end);
		},
		Error: Error$1,
		FunctionPrototypeCall(fn, thisArgs, ...args) {
			return fn.call(thisArgs, ...args);
		},
		FunctionPrototypeSymbolHasInstance(self, instance) {
			return Function.prototype[Symbol.hasInstance].call(self, instance);
		},
		MathFloor: Math.floor,
		Number,
		NumberIsInteger: Number.isInteger,
		NumberIsNaN: Number.isNaN,
		NumberMAX_SAFE_INTEGER: Number.MAX_SAFE_INTEGER,
		NumberMIN_SAFE_INTEGER: Number.MIN_SAFE_INTEGER,
		NumberParseInt: Number.parseInt,
		ObjectDefineProperties(self, props) {
			return Object.defineProperties(self, props);
		},
		ObjectDefineProperty(self, name, prop) {
			return Object.defineProperty(self, name, prop);
		},
		ObjectGetOwnPropertyDescriptor(self, name) {
			return Object.getOwnPropertyDescriptor(self, name);
		},
		ObjectKeys(obj) {
			return Object.keys(obj);
		},
		ObjectSetPrototypeOf(target, proto) {
			return Object.setPrototypeOf(target, proto);
		},
		Promise,
		PromisePrototypeCatch(self, fn) {
			return self.catch(fn);
		},
		PromisePrototypeThen(self, thenFn, catchFn) {
			return self.then(thenFn, catchFn);
		},
		PromiseReject(err) {
			return Promise.reject(err);
		},
		PromiseResolve(val) {
			return Promise.resolve(val);
		},
		ReflectApply: Reflect.apply,
		RegExpPrototypeTest(self, value) {
			return self.test(value);
		},
		SafeSet: Set,
		String,
		StringPrototypeSlice(self, start, end) {
			return self.slice(start, end);
		},
		StringPrototypeToLowerCase(self) {
			return self.toLowerCase();
		},
		StringPrototypeToUpperCase(self) {
			return self.toUpperCase();
		},
		StringPrototypeTrim(self) {
			return self.trim();
		},
		Symbol,
		SymbolFor: Symbol.for,
		SymbolAsyncIterator: Symbol.asyncIterator,
		SymbolHasInstance: Symbol.hasInstance,
		SymbolIterator: Symbol.iterator,
		SymbolDispose: Symbol.dispose || Symbol("Symbol.dispose"),
		SymbolAsyncDispose: Symbol.asyncDispose || Symbol("Symbol.asyncDispose"),
		TypedArrayPrototypeSet(self, buf, len) {
			return self.set(buf, len);
		},
		Boolean,
		Uint8Array
	};
}));
// \0jco-node-builtin:microtask-globals
var _globalThis$queueMicr, _globalThis$queueMicr2, queueMicrotask;
var init__jco_node_builtin_microtask_globals = __esmMin(() => {
	queueMicrotask = (_globalThis$queueMicr = (_globalThis$queueMicr2 = globalThis.queueMicrotask) === null || _globalThis$queueMicr2 === void 0 ? void 0 : _globalThis$queueMicr2.bind(globalThis)) !== null && _globalThis$queueMicr !== void 0 ? _globalThis$queueMicr : ((callback) => Promise.resolve().then(callback));
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/asyncToGenerator.js
function asyncGeneratorStep(n, t, e, r, o, a, c) {
	try {
		var i = n[a](c), u = i.value;
	} catch (n) {
		e(n);
		return;
	}
	i.done ? t(u) : Promise.resolve(u).then(r, o);
}
function _asyncToGenerator(n) {
	return function() {
		var t = this, e = arguments;
		return new Promise(function(r, o) {
			var a = n.apply(t, e);
			function _next(n) {
				asyncGeneratorStep(a, r, o, _next, _throw, "next", n);
			}
			function _throw(n) {
				asyncGeneratorStep(a, r, o, _next, _throw, "throw", n);
			}
			_next(void 0);
		});
	};
}
var init_asyncToGenerator = __esmMin(() => {});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/ours/util/inspect.js
var require_inspect = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = {
		format(format, ...args) {
			return format.replace(/%([sdifj])/g, function(...[_unused, type]) {
				const replacement = args.shift();
				if (type === "f") return replacement.toFixed(6);
				else if (type === "j") return JSON.stringify(replacement);
				else if (type === "s" && typeof replacement === "object") return `${replacement.constructor !== Object ? replacement.constructor.name : ""} {}`.trim();
				else return replacement.toString();
			});
		},
		inspect(value) {
			switch (typeof value) {
				case "string":
					if (value.includes("'")) {
						if (!value.includes("\"")) return `"${value}"`;
						else if (!value.includes("`") && !value.includes("${")) return `\`${value}\``;
					}
					return `'${value}'`;
				case "number":
					if (isNaN(value)) return "NaN";
					else if (Object.is(value, -0)) return String(value);
					return value;
				case "bigint": return `${String(value)}n`;
				case "boolean":
				case "undefined": return String(value);
				case "object": return "{}";
			}
		}
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/ours/errors.js
var require_errors = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init__jco_node_builtin_error_globals();
	const { format, inspect } = require_inspect();
	const { AggregateError: CustomAggregateError } = require_primordials();
	const AggregateError = globalThis.AggregateError || CustomAggregateError;
	const kIsNodeError = Symbol("kIsNodeError");
	const kTypes = [
		"string",
		"function",
		"number",
		"object",
		"Function",
		"Object",
		"boolean",
		"bigint",
		"symbol"
	];
	const classRegExp = /^([A-Z][a-z0-9]*)+$/;
	const nodeInternalPrefix = "__node_internal_";
	const codes = {};
	function assert(value, message) {
		if (!value) throw new codes.ERR_INTERNAL_ASSERTION(message);
	}
	function addNumericalSeparator(val) {
		let res = "";
		let i = val.length;
		const start = val[0] === "-" ? 1 : 0;
		for (; i >= start + 4; i -= 3) res = `_${val.slice(i - 3, i)}${res}`;
		return `${val.slice(0, i)}${res}`;
	}
	function getMessage(key, msg, args) {
		if (typeof msg === "function") {
			assert(msg.length <= args.length, `Code: ${key}; The provided arguments length (${args.length}) does not match the required ones (${msg.length}).`);
			return msg(...args);
		}
		const expectedLength = (msg.match(/%[dfijoOs]/g) || []).length;
		assert(expectedLength === args.length, `Code: ${key}; The provided arguments length (${args.length}) does not match the required ones (${expectedLength}).`);
		if (args.length === 0) return msg;
		return format(msg, ...args);
	}
	function E(code, message, Base) {
		if (!Base) Base = Error$1;
		class NodeError extends Base {
			constructor(...args) {
				super(getMessage(code, message, args));
			}
			toString() {
				return `${this.name} [${code}]: ${this.message}`;
			}
		}
		Object.defineProperties(NodeError.prototype, {
			name: {
				value: Base.name,
				writable: true,
				enumerable: false,
				configurable: true
			},
			toString: {
				value() {
					return `${this.name} [${code}]: ${this.message}`;
				},
				writable: true,
				enumerable: false,
				configurable: true
			}
		});
		NodeError.prototype.code = code;
		NodeError.prototype[kIsNodeError] = true;
		codes[code] = NodeError;
	}
	function hideStackFrames(fn) {
		const hidden = nodeInternalPrefix + fn.name;
		Object.defineProperty(fn, "name", { value: hidden });
		return fn;
	}
	function aggregateTwoErrors(innerError, outerError) {
		if (innerError && outerError && innerError !== outerError) {
			if (Array.isArray(outerError.errors)) {
				outerError.errors.push(innerError);
				return outerError;
			}
			const err = new AggregateError([outerError, innerError], outerError.message);
			err.code = outerError.code;
			return err;
		}
		return innerError || outerError;
	}
	var AbortError = class extends Error$1 {
		constructor(message = "The operation was aborted", options = void 0) {
			if (options !== void 0 && typeof options !== "object") throw new codes.ERR_INVALID_ARG_TYPE("options", "Object", options);
			super(message, options);
			this.code = "ABORT_ERR";
			this.name = "AbortError";
		}
	};
	E("ERR_ASSERTION", "%s", Error$1);
	E("ERR_INVALID_ARG_TYPE", (name, expected, actual) => {
		assert(typeof name === "string", "'name' must be a string");
		if (!Array.isArray(expected)) expected = [expected];
		let msg = "The ";
		if (name.endsWith(" argument")) msg += `${name} `;
		else msg += `"${name}" ${name.includes(".") ? "property" : "argument"} `;
		msg += "must be ";
		const types = [];
		const instances = [];
		const other = [];
		for (const value of expected) {
			assert(typeof value === "string", "All expected entries have to be of type string");
			if (kTypes.includes(value)) types.push(value.toLowerCase());
			else if (classRegExp.test(value)) instances.push(value);
			else {
				assert(value !== "object", "The value \"object\" should be written as \"Object\"");
				other.push(value);
			}
		}
		if (instances.length > 0) {
			const pos = types.indexOf("object");
			if (pos !== -1) {
				types.splice(types, pos, 1);
				instances.push("Object");
			}
		}
		if (types.length > 0) {
			switch (types.length) {
				case 1:
					msg += `of type ${types[0]}`;
					break;
				case 2:
					msg += `one of type ${types[0]} or ${types[1]}`;
					break;
				default: {
					const last = types.pop();
					msg += `one of type ${types.join(", ")}, or ${last}`;
				}
			}
			if (instances.length > 0 || other.length > 0) msg += " or ";
		}
		if (instances.length > 0) {
			switch (instances.length) {
				case 1:
					msg += `an instance of ${instances[0]}`;
					break;
				case 2:
					msg += `an instance of ${instances[0]} or ${instances[1]}`;
					break;
				default: {
					const last = instances.pop();
					msg += `an instance of ${instances.join(", ")}, or ${last}`;
				}
			}
			if (other.length > 0) msg += " or ";
		}
		switch (other.length) {
			case 0: break;
			case 1:
				if (other[0].toLowerCase() !== other[0]) msg += "an ";
				msg += `${other[0]}`;
				break;
			case 2:
				msg += `one of ${other[0]} or ${other[1]}`;
				break;
			default: {
				const last = other.pop();
				msg += `one of ${other.join(", ")}, or ${last}`;
			}
		}
		if (actual == null) msg += `. Received ${actual}`;
		else if (typeof actual === "function" && actual.name) msg += `. Received function ${actual.name}`;
		else if (typeof actual === "object") {
			var _actual$constructor;
			if ((_actual$constructor = actual.constructor) !== null && _actual$constructor !== void 0 && _actual$constructor.name) msg += `. Received an instance of ${actual.constructor.name}`;
			else {
				const inspected = inspect(actual, { depth: -1 });
				msg += `. Received ${inspected}`;
			}
		} else {
			let inspected = inspect(actual, { colors: false });
			if (inspected.length > 25) inspected = `${inspected.slice(0, 25)}...`;
			msg += `. Received type ${typeof actual} (${inspected})`;
		}
		return msg;
	}, TypeError);
	E("ERR_INVALID_ARG_VALUE", (name, value, reason = "is invalid") => {
		let inspected = inspect(value);
		if (inspected.length > 128) inspected = inspected.slice(0, 128) + "...";
		return `The ${name.includes(".") ? "property" : "argument"} '${name}' ${reason}. Received ${inspected}`;
	}, TypeError);
	E("ERR_INVALID_RETURN_VALUE", (input, name, value) => {
		var _value$constructor;
		return `Expected ${input} to be returned from the "${name}" function but got ${value !== null && value !== void 0 && (_value$constructor = value.constructor) !== null && _value$constructor !== void 0 && _value$constructor.name ? `instance of ${value.constructor.name}` : `type ${typeof value}`}.`;
	}, TypeError);
	E("ERR_MISSING_ARGS", (...args) => {
		assert(args.length > 0, "At least one arg needs to be specified");
		let msg;
		const len = args.length;
		args = (Array.isArray(args) ? args : [args]).map((a) => `"${a}"`).join(" or ");
		switch (len) {
			case 1:
				msg += `The ${args[0]} argument`;
				break;
			case 2:
				msg += `The ${args[0]} and ${args[1]} arguments`;
				break;
			default: {
				const last = args.pop();
				msg += `The ${args.join(", ")}, and ${last} arguments`;
			}
		}
		return `${msg} must be specified`;
	}, TypeError);
	E("ERR_OUT_OF_RANGE", (str, range, input) => {
		assert(range, "Missing \"range\" argument");
		let received;
		if (Number.isInteger(input) && Math.abs(input) > 2 ** 32) received = addNumericalSeparator(String(input));
		else if (typeof input === "bigint") {
			received = String(input);
			const limit = BigInt(2) ** BigInt(32);
			if (input > limit || input < -limit) received = addNumericalSeparator(received);
			received += "n";
		} else received = inspect(input);
		return `The value of "${str}" is out of range. It must be ${range}. Received ${received}`;
	}, RangeError);
	E("ERR_MULTIPLE_CALLBACK", "Callback called multiple times", Error$1);
	E("ERR_METHOD_NOT_IMPLEMENTED", "The %s method is not implemented", Error$1);
	E("ERR_STREAM_ALREADY_FINISHED", "Cannot call %s after a stream was finished", Error$1);
	E("ERR_STREAM_CANNOT_PIPE", "Cannot pipe, not readable", Error$1);
	E("ERR_STREAM_DESTROYED", "Cannot call %s after a stream was destroyed", Error$1);
	E("ERR_STREAM_NULL_VALUES", "May not write null values to stream", TypeError);
	E("ERR_STREAM_PREMATURE_CLOSE", "Premature close", Error$1);
	E("ERR_STREAM_PUSH_AFTER_EOF", "stream.push() after EOF", Error$1);
	E("ERR_STREAM_UNSHIFT_AFTER_END_EVENT", "stream.unshift() after end event", Error$1);
	E("ERR_STREAM_WRITE_AFTER_END", "write after end", Error$1);
	E("ERR_UNKNOWN_ENCODING", "Unknown encoding: %s", TypeError);
	module.exports = {
		AbortError,
		aggregateTwoErrors: hideStackFrames(aggregateTwoErrors),
		hideStackFrames,
		codes
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/event-target-shim/dist/event-target-shim.js
/**
* @author Toru Nagashima <https://github.com/mysticatea>
* @copyright 2015 Toru Nagashima. All rights reserved.
* See LICENSE file in root directory for full license.
*/
var require_event_target_shim = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_console_globals();
	Object.defineProperty(exports, "__esModule", { value: true });
	/**
	* @typedef {object} PrivateData
	* @property {EventTarget} eventTarget The event target.
	* @property {{type:string}} event The original event object.
	* @property {number} eventPhase The current event phase.
	* @property {EventTarget|null} currentTarget The current event target.
	* @property {boolean} canceled The flag to prevent default.
	* @property {boolean} stopped The flag to stop propagation.
	* @property {boolean} immediateStopped The flag to stop propagation immediately.
	* @property {Function|null} passiveListener The listener if the current listener is passive. Otherwise this is null.
	* @property {number} timeStamp The unix time.
	* @private
	*/
	/**
	* Private data for event wrappers.
	* @type {WeakMap<Event, PrivateData>}
	* @private
	*/
	const privateData = /* @__PURE__ */ new WeakMap();
	/**
	* Cache for wrapper classes.
	* @type {WeakMap<Object, Function>}
	* @private
	*/
	const wrappers = /* @__PURE__ */ new WeakMap();
	/**
	* Get private data.
	* @param {Event} event The event object to get private data.
	* @returns {PrivateData} The private data of the event.
	* @private
	*/
	function pd(event) {
		const retv = privateData.get(event);
		_jco_node_builtin_console_globals_default.assert(retv != null, "'this' is expected an Event object, but got", event);
		return retv;
	}
	/**
	* https://dom.spec.whatwg.org/#set-the-canceled-flag
	* @param data {PrivateData} private data.
	*/
	function setCancelFlag(data) {
		if (data.passiveListener != null) {
			if (typeof _jco_node_builtin_console_globals_default !== "undefined" && typeof _jco_node_builtin_console_globals_default.error === "function") _jco_node_builtin_console_globals_default.error("Unable to preventDefault inside passive event listener invocation.", data.passiveListener);
			return;
		}
		if (!data.event.cancelable) return;
		data.canceled = true;
		if (typeof data.event.preventDefault === "function") data.event.preventDefault();
	}
	/**
	* @see https://dom.spec.whatwg.org/#interface-event
	* @private
	*/
	/**
	* The event wrapper.
	* @constructor
	* @param {EventTarget} eventTarget The event target of this dispatching.
	* @param {Event|{type:string}} event The original event to wrap.
	*/
	function Event(eventTarget, event) {
		privateData.set(this, {
			eventTarget,
			event,
			eventPhase: 2,
			currentTarget: eventTarget,
			canceled: false,
			stopped: false,
			immediateStopped: false,
			passiveListener: null,
			timeStamp: event.timeStamp || Date.now()
		});
		Object.defineProperty(this, "isTrusted", {
			value: false,
			enumerable: true
		});
		const keys = Object.keys(event);
		for (let i = 0; i < keys.length; ++i) {
			const key = keys[i];
			if (!(key in this)) Object.defineProperty(this, key, defineRedirectDescriptor(key));
		}
	}
	Event.prototype = {
		/**
		* The type of this event.
		* @type {string}
		*/
		get type() {
			return pd(this).event.type;
		},
		/**
		* The target of this event.
		* @type {EventTarget}
		*/
		get target() {
			return pd(this).eventTarget;
		},
		/**
		* The target of this event.
		* @type {EventTarget}
		*/
		get currentTarget() {
			return pd(this).currentTarget;
		},
		/**
		* @returns {EventTarget[]} The composed path of this event.
		*/
		composedPath() {
			const currentTarget = pd(this).currentTarget;
			if (currentTarget == null) return [];
			return [currentTarget];
		},
		/**
		* Constant of NONE.
		* @type {number}
		*/
		get NONE() {
			return 0;
		},
		/**
		* Constant of CAPTURING_PHASE.
		* @type {number}
		*/
		get CAPTURING_PHASE() {
			return 1;
		},
		/**
		* Constant of AT_TARGET.
		* @type {number}
		*/
		get AT_TARGET() {
			return 2;
		},
		/**
		* Constant of BUBBLING_PHASE.
		* @type {number}
		*/
		get BUBBLING_PHASE() {
			return 3;
		},
		/**
		* The target of this event.
		* @type {number}
		*/
		get eventPhase() {
			return pd(this).eventPhase;
		},
		/**
		* Stop event bubbling.
		* @returns {void}
		*/
		stopPropagation() {
			const data = pd(this);
			data.stopped = true;
			if (typeof data.event.stopPropagation === "function") data.event.stopPropagation();
		},
		/**
		* Stop event bubbling.
		* @returns {void}
		*/
		stopImmediatePropagation() {
			const data = pd(this);
			data.stopped = true;
			data.immediateStopped = true;
			if (typeof data.event.stopImmediatePropagation === "function") data.event.stopImmediatePropagation();
		},
		/**
		* The flag to be bubbling.
		* @type {boolean}
		*/
		get bubbles() {
			return Boolean(pd(this).event.bubbles);
		},
		/**
		* The flag to be cancelable.
		* @type {boolean}
		*/
		get cancelable() {
			return Boolean(pd(this).event.cancelable);
		},
		/**
		* Cancel this event.
		* @returns {void}
		*/
		preventDefault() {
			setCancelFlag(pd(this));
		},
		/**
		* The flag to indicate cancellation state.
		* @type {boolean}
		*/
		get defaultPrevented() {
			return pd(this).canceled;
		},
		/**
		* The flag to be composed.
		* @type {boolean}
		*/
		get composed() {
			return Boolean(pd(this).event.composed);
		},
		/**
		* The unix time of this event.
		* @type {number}
		*/
		get timeStamp() {
			return pd(this).timeStamp;
		},
		/**
		* The target of this event.
		* @type {EventTarget}
		* @deprecated
		*/
		get srcElement() {
			return pd(this).eventTarget;
		},
		/**
		* The flag to stop event bubbling.
		* @type {boolean}
		* @deprecated
		*/
		get cancelBubble() {
			return pd(this).stopped;
		},
		set cancelBubble(value) {
			if (!value) return;
			const data = pd(this);
			data.stopped = true;
			if (typeof data.event.cancelBubble === "boolean") data.event.cancelBubble = true;
		},
		/**
		* The flag to indicate cancellation state.
		* @type {boolean}
		* @deprecated
		*/
		get returnValue() {
			return !pd(this).canceled;
		},
		set returnValue(value) {
			if (!value) setCancelFlag(pd(this));
		},
		/**
		* Initialize this event object. But do nothing under event dispatching.
		* @param {string} type The event type.
		* @param {boolean} [bubbles=false] The flag to be possible to bubble up.
		* @param {boolean} [cancelable=false] The flag to be possible to cancel.
		* @deprecated
		*/
		initEvent() {}
	};
	Object.defineProperty(Event.prototype, "constructor", {
		value: Event,
		configurable: true,
		writable: true
	});
	if (typeof window !== "undefined" && typeof window.Event !== "undefined") {
		Object.setPrototypeOf(Event.prototype, window.Event.prototype);
		wrappers.set(window.Event.prototype, Event);
	}
	/**
	* Get the property descriptor to redirect a given property.
	* @param {string} key Property name to define property descriptor.
	* @returns {PropertyDescriptor} The property descriptor to redirect the property.
	* @private
	*/
	function defineRedirectDescriptor(key) {
		return {
			get() {
				return pd(this).event[key];
			},
			set(value) {
				pd(this).event[key] = value;
			},
			configurable: true,
			enumerable: true
		};
	}
	/**
	* Get the property descriptor to call a given method property.
	* @param {string} key Property name to define property descriptor.
	* @returns {PropertyDescriptor} The property descriptor to call the method property.
	* @private
	*/
	function defineCallDescriptor(key) {
		return {
			value() {
				const event = pd(this).event;
				return event[key].apply(event, arguments);
			},
			configurable: true,
			enumerable: true
		};
	}
	/**
	* Define new wrapper class.
	* @param {Function} BaseEvent The base wrapper class.
	* @param {Object} proto The prototype of the original event.
	* @returns {Function} The defined wrapper class.
	* @private
	*/
	function defineWrapper(BaseEvent, proto) {
		const keys = Object.keys(proto);
		if (keys.length === 0) return BaseEvent;
		/** CustomEvent */
		function CustomEvent(eventTarget, event) {
			BaseEvent.call(this, eventTarget, event);
		}
		CustomEvent.prototype = Object.create(BaseEvent.prototype, { constructor: {
			value: CustomEvent,
			configurable: true,
			writable: true
		} });
		for (let i = 0; i < keys.length; ++i) {
			const key = keys[i];
			if (!(key in BaseEvent.prototype)) {
				const isFunc = typeof Object.getOwnPropertyDescriptor(proto, key).value === "function";
				Object.defineProperty(CustomEvent.prototype, key, isFunc ? defineCallDescriptor(key) : defineRedirectDescriptor(key));
			}
		}
		return CustomEvent;
	}
	/**
	* Get the wrapper class of a given prototype.
	* @param {Object} proto The prototype of the original event to get its wrapper.
	* @returns {Function} The wrapper class.
	* @private
	*/
	function getWrapper(proto) {
		if (proto == null || proto === Object.prototype) return Event;
		let wrapper = wrappers.get(proto);
		if (wrapper == null) {
			wrapper = defineWrapper(getWrapper(Object.getPrototypeOf(proto)), proto);
			wrappers.set(proto, wrapper);
		}
		return wrapper;
	}
	/**
	* Wrap a given event to management a dispatching.
	* @param {EventTarget} eventTarget The event target of this dispatching.
	* @param {Object} event The event to wrap.
	* @returns {Event} The wrapper instance.
	* @private
	*/
	function wrapEvent(eventTarget, event) {
		return new (getWrapper(Object.getPrototypeOf(event)))(eventTarget, event);
	}
	/**
	* Get the immediateStopped flag of a given event.
	* @param {Event} event The event to get.
	* @returns {boolean} The flag to stop propagation immediately.
	* @private
	*/
	function isStopped(event) {
		return pd(event).immediateStopped;
	}
	/**
	* Set the current event phase of a given event.
	* @param {Event} event The event to set current target.
	* @param {number} eventPhase New event phase.
	* @returns {void}
	* @private
	*/
	function setEventPhase(event, eventPhase) {
		pd(event).eventPhase = eventPhase;
	}
	/**
	* Set the current target of a given event.
	* @param {Event} event The event to set current target.
	* @param {EventTarget|null} currentTarget New current target.
	* @returns {void}
	* @private
	*/
	function setCurrentTarget(event, currentTarget) {
		pd(event).currentTarget = currentTarget;
	}
	/**
	* Set a passive listener of a given event.
	* @param {Event} event The event to set current target.
	* @param {Function|null} passiveListener New passive listener.
	* @returns {void}
	* @private
	*/
	function setPassiveListener(event, passiveListener) {
		pd(event).passiveListener = passiveListener;
	}
	/**
	* @typedef {object} ListenerNode
	* @property {Function} listener
	* @property {1|2|3} listenerType
	* @property {boolean} passive
	* @property {boolean} once
	* @property {ListenerNode|null} next
	* @private
	*/
	/**
	* @type {WeakMap<object, Map<string, ListenerNode>>}
	* @private
	*/
	const listenersMap = /* @__PURE__ */ new WeakMap();
	const CAPTURE = 1;
	const BUBBLE = 2;
	const ATTRIBUTE = 3;
	/**
	* Check whether a given value is an object or not.
	* @param {any} x The value to check.
	* @returns {boolean} `true` if the value is an object.
	*/
	function isObject(x) {
		return x !== null && typeof x === "object";
	}
	/**
	* Get listeners.
	* @param {EventTarget} eventTarget The event target to get.
	* @returns {Map<string, ListenerNode>} The listeners.
	* @private
	*/
	function getListeners(eventTarget) {
		const listeners = listenersMap.get(eventTarget);
		if (listeners == null) throw new TypeError("'this' is expected an EventTarget object, but got another value.");
		return listeners;
	}
	/**
	* Get the property descriptor for the event attribute of a given event.
	* @param {string} eventName The event name to get property descriptor.
	* @returns {PropertyDescriptor} The property descriptor.
	* @private
	*/
	function defineEventAttributeDescriptor(eventName) {
		return {
			get() {
				let node = getListeners(this).get(eventName);
				while (node != null) {
					if (node.listenerType === ATTRIBUTE) return node.listener;
					node = node.next;
				}
				return null;
			},
			set(listener) {
				if (typeof listener !== "function" && !isObject(listener)) listener = null;
				const listeners = getListeners(this);
				let prev = null;
				let node = listeners.get(eventName);
				while (node != null) {
					if (node.listenerType === ATTRIBUTE) {
						if (prev !== null) prev.next = node.next;
						else if (node.next !== null) listeners.set(eventName, node.next);
						else listeners.delete(eventName);
					} else prev = node;
					node = node.next;
				}
				if (listener !== null) {
					const newNode = {
						listener,
						listenerType: ATTRIBUTE,
						passive: false,
						once: false,
						next: null
					};
					if (prev === null) listeners.set(eventName, newNode);
					else prev.next = newNode;
				}
			},
			configurable: true,
			enumerable: true
		};
	}
	/**
	* Define an event attribute (e.g. `eventTarget.onclick`).
	* @param {Object} eventTargetPrototype The event target prototype to define an event attrbite.
	* @param {string} eventName The event name to define.
	* @returns {void}
	*/
	function defineEventAttribute(eventTargetPrototype, eventName) {
		Object.defineProperty(eventTargetPrototype, `on${eventName}`, defineEventAttributeDescriptor(eventName));
	}
	/**
	* Define a custom EventTarget with event attributes.
	* @param {string[]} eventNames Event names for event attributes.
	* @returns {EventTarget} The custom EventTarget.
	* @private
	*/
	function defineCustomEventTarget(eventNames) {
		/** CustomEventTarget */
		function CustomEventTarget() {
			EventTarget.call(this);
		}
		CustomEventTarget.prototype = Object.create(EventTarget.prototype, { constructor: {
			value: CustomEventTarget,
			configurable: true,
			writable: true
		} });
		for (let i = 0; i < eventNames.length; ++i) defineEventAttribute(CustomEventTarget.prototype, eventNames[i]);
		return CustomEventTarget;
	}
	/**
	* EventTarget.
	*
	* - This is constructor if no arguments.
	* - This is a function which returns a CustomEventTarget constructor if there are arguments.
	*
	* For example:
	*
	*     class A extends EventTarget {}
	*     class B extends EventTarget("message") {}
	*     class C extends EventTarget("message", "error") {}
	*     class D extends EventTarget(["message", "error"]) {}
	*/
	function EventTarget() {
		if (this instanceof EventTarget) {
			listenersMap.set(this, /* @__PURE__ */ new Map());
			return;
		}
		if (arguments.length === 1 && Array.isArray(arguments[0])) return defineCustomEventTarget(arguments[0]);
		if (arguments.length > 0) {
			const types = new Array(arguments.length);
			for (let i = 0; i < arguments.length; ++i) types[i] = arguments[i];
			return defineCustomEventTarget(types);
		}
		throw new TypeError("Cannot call a class as a function");
	}
	EventTarget.prototype = {
		/**
		* Add a given listener to this event target.
		* @param {string} eventName The event name to add.
		* @param {Function} listener The listener to add.
		* @param {boolean|{capture?:boolean,passive?:boolean,once?:boolean}} [options] The options for this listener.
		* @returns {void}
		*/
		addEventListener(eventName, listener, options) {
			if (listener == null) return;
			if (typeof listener !== "function" && !isObject(listener)) throw new TypeError("'listener' should be a function or an object.");
			const listeners = getListeners(this);
			const optionsIsObj = isObject(options);
			const listenerType = (optionsIsObj ? Boolean(options.capture) : Boolean(options)) ? CAPTURE : BUBBLE;
			const newNode = {
				listener,
				listenerType,
				passive: optionsIsObj && Boolean(options.passive),
				once: optionsIsObj && Boolean(options.once),
				next: null
			};
			let node = listeners.get(eventName);
			if (node === void 0) {
				listeners.set(eventName, newNode);
				return;
			}
			let prev = null;
			while (node != null) {
				if (node.listener === listener && node.listenerType === listenerType) return;
				prev = node;
				node = node.next;
			}
			prev.next = newNode;
		},
		/**
		* Remove a given listener from this event target.
		* @param {string} eventName The event name to remove.
		* @param {Function} listener The listener to remove.
		* @param {boolean|{capture?:boolean,passive?:boolean,once?:boolean}} [options] The options for this listener.
		* @returns {void}
		*/
		removeEventListener(eventName, listener, options) {
			if (listener == null) return;
			const listeners = getListeners(this);
			const listenerType = (isObject(options) ? Boolean(options.capture) : Boolean(options)) ? CAPTURE : BUBBLE;
			let prev = null;
			let node = listeners.get(eventName);
			while (node != null) {
				if (node.listener === listener && node.listenerType === listenerType) {
					if (prev !== null) prev.next = node.next;
					else if (node.next !== null) listeners.set(eventName, node.next);
					else listeners.delete(eventName);
					return;
				}
				prev = node;
				node = node.next;
			}
		},
		/**
		* Dispatch a given event.
		* @param {Event|{type:string}} event The event to dispatch.
		* @returns {boolean} `false` if canceled.
		*/
		dispatchEvent(event) {
			if (event == null || typeof event.type !== "string") throw new TypeError("\"event.type\" should be a string.");
			const listeners = getListeners(this);
			const eventName = event.type;
			let node = listeners.get(eventName);
			if (node == null) return true;
			const wrappedEvent = wrapEvent(this, event);
			let prev = null;
			while (node != null) {
				if (node.once) {
					if (prev !== null) prev.next = node.next;
					else if (node.next !== null) listeners.set(eventName, node.next);
					else listeners.delete(eventName);
				} else prev = node;
				setPassiveListener(wrappedEvent, node.passive ? node.listener : null);
				if (typeof node.listener === "function") try {
					node.listener.call(this, wrappedEvent);
				} catch (err) {
					if (typeof _jco_node_builtin_console_globals_default !== "undefined" && typeof _jco_node_builtin_console_globals_default.error === "function") _jco_node_builtin_console_globals_default.error(err);
				}
				else if (node.listenerType !== ATTRIBUTE && typeof node.listener.handleEvent === "function") node.listener.handleEvent(wrappedEvent);
				if (isStopped(wrappedEvent)) break;
				node = node.next;
			}
			setPassiveListener(wrappedEvent, null);
			setEventPhase(wrappedEvent, 0);
			setCurrentTarget(wrappedEvent, null);
			return !wrappedEvent.defaultPrevented;
		}
	};
	Object.defineProperty(EventTarget.prototype, "constructor", {
		value: EventTarget,
		configurable: true,
		writable: true
	});
	if (typeof window !== "undefined" && typeof window.EventTarget !== "undefined") Object.setPrototypeOf(EventTarget.prototype, window.EventTarget.prototype);
	exports.defineEventAttribute = defineEventAttribute;
	exports.EventTarget = EventTarget;
	exports.default = EventTarget;
	module.exports = EventTarget;
	module.exports.EventTarget = module.exports["default"] = EventTarget;
	module.exports.defineEventAttribute = defineEventAttribute;
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/abort-controller/dist/abort-controller.js
/**
* @author Toru Nagashima <https://github.com/mysticatea>
* See LICENSE file in root directory for full license.
*/
var require_abort_controller = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init__jco_node_builtin_error_globals();
	Object.defineProperty(exports, "__esModule", { value: true });
	var eventTargetShim = require_event_target_shim();
	/**
	* The signal class.
	* @see https://dom.spec.whatwg.org/#abortsignal
	*/
	var AbortSignal = class extends eventTargetShim.EventTarget {
		/**
		* AbortSignal cannot be constructed directly.
		*/
		constructor() {
			super();
			throw new TypeError("AbortSignal cannot be constructed directly");
		}
		/**
		* Returns `true` if this `AbortSignal`'s `AbortController` has signaled to abort, and `false` otherwise.
		*/
		get aborted() {
			const aborted = abortedFlags.get(this);
			if (typeof aborted !== "boolean") throw new TypeError(`Expected 'this' to be an 'AbortSignal' object, but got ${this === null ? "null" : typeof this}`);
			return aborted;
		}
	};
	eventTargetShim.defineEventAttribute(AbortSignal.prototype, "abort");
	/**
	* Create an AbortSignal object.
	*/
	function createAbortSignal() {
		const signal = Object.create(AbortSignal.prototype);
		eventTargetShim.EventTarget.call(signal);
		abortedFlags.set(signal, false);
		return signal;
	}
	/**
	* Abort a given signal.
	*/
	function abortSignal(signal) {
		if (abortedFlags.get(signal) !== false) return;
		abortedFlags.set(signal, true);
		signal.dispatchEvent({ type: "abort" });
	}
	/**
	* Aborted flag for each instances.
	*/
	const abortedFlags = /* @__PURE__ */ new WeakMap();
	Object.defineProperties(AbortSignal.prototype, { aborted: { enumerable: true } });
	if (typeof Symbol === "function" && typeof Symbol.toStringTag === "symbol") Object.defineProperty(AbortSignal.prototype, Symbol.toStringTag, {
		configurable: true,
		value: "AbortSignal"
	});
	/**
	* The AbortController.
	* @see https://dom.spec.whatwg.org/#abortcontroller
	*/
	var AbortController = class {
		/**
		* Initialize this controller.
		*/
		constructor() {
			signals.set(this, createAbortSignal());
		}
		/**
		* Returns the `AbortSignal` object associated with this object.
		*/
		get signal() {
			return getSignal(this);
		}
		/**
		* Abort and signal to any observers that the associated activity is to be aborted.
		*/
		abort() {
			abortSignal(getSignal(this));
		}
	};
	/**
	* Associated signals.
	*/
	const signals = /* @__PURE__ */ new WeakMap();
	/**
	* Get the associated signal of a given controller.
	*/
	function getSignal(controller) {
		const signal = signals.get(controller);
		if (signal == null) throw new TypeError(`Expected 'this' to be an 'AbortController' object, but got ${controller === null ? "null" : typeof controller}`);
		return signal;
	}
	Object.defineProperties(AbortController.prototype, {
		signal: { enumerable: true },
		abort: { enumerable: true }
	});
	if (typeof Symbol === "function" && typeof Symbol.toStringTag === "symbol") Object.defineProperty(AbortController.prototype, Symbol.toStringTag, {
		configurable: true,
		value: "AbortController"
	});
	exports.AbortController = AbortController;
	exports.AbortSignal = AbortSignal;
	exports.default = AbortController;
	module.exports = AbortController;
	module.exports.AbortController = module.exports["default"] = AbortController;
	module.exports.AbortSignal = AbortSignal;
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/events/listener-count.js
/**
* `events.listenerCount(emitter, eventName)`.
*
* Deprecated in Node in favour of `emitter.listenerCount()`, but still present and still used, so
* it is implemented rather than refused. unenv ships it as a `notImplemented` stub that throws.
*
* Follows Node: delegate to the emitter's own method when it has one, so subclasses that override
* counting are honoured, and otherwise apply the core implementation to the object.
*
* @param core - the emitter core to fall back to
*/
function createListenerCount(core) {
	return function listenerCount(emitter, eventName) {
		if (typeof (emitter === null || emitter === void 0 ? void 0 : emitter.listenerCount) === "function") return emitter.listenerCount.call(emitter, eventName);
		return core.EventEmitter.prototype.listenerCount.call(emitter, eventName);
	};
}
var init_listener_count = __esmMin(() => {});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/events/errors.js
/**
* Node's `ERR_INVALID_ARG_TYPE`, phrased for a primitive type.
*
* @param name - the parameter that was wrong, as Node names it
* @param expected - the type Node accepts
* @param actual - the value that was passed
*/
function invalidArgType(name, expected, actual) {
	return invalidArgType$1(name, expected, actual);
}
/**
* Node's `ERR_INVALID_ARG_TYPE`, phrased for a class.
*
* @param name - the parameter that was wrong, as Node names it
* @param expected - the classes Node accepts for it
* @param actual - the value that was passed
*/
function invalidArgInstance(name, expected, actual) {
	return codedError(new TypeError(`The "${name}" argument must be an instance of ${formatList(expected, "or")}. Received ${determineSpecificType(actual)}`), "ERR_INVALID_ARG_TYPE");
}
/**
* Node's `ERR_OUT_OF_RANGE`.
*
* @param name - the parameter that was out of range
* @param range - the range Node requires, phrased as Node phrases it
* @param actual - the value that was passed
*/
function outOfRange(name, range, actual) {
	return outOfRange$1(name, range, actual);
}
var init_errors$1 = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init_core();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/events/max-listeners.js
/** Node accepts anything with `addEventListener`/`removeEventListener` as an `EventTarget`. */
function isEventTarget$1(value) {
	return typeof value === "object" && value !== null && typeof value.addEventListener === "function" && typeof value.removeEventListener === "function";
}
/** Node's `validateNumber(n, name, 0)`: a number, and not negative or `NaN`. */
function validateLimit$1(n) {
	if (typeof n !== "number") throw invalidArgType("setMaxListeners", "number", n);
	if (Number.isNaN(n) || n < 0) throw outOfRange("setMaxListeners", ">= 0", n);
}
/**
* `events.setMaxListeners()` and `events.getMaxListeners()`.
*
* unenv ships `setMaxListeners` as a `notImplemented` stub, and its `getMaxListeners` throws on an
* `EventTarget` because it only handles emitters. Both are implemented here against Node's
* behavior; the emitter half delegates to the core rather than reimplementing it.
*
* @param core - the emitter core supplying `defaultMaxListeners`
*/
function createMaxListeners(core) {
	/**
	* `events.setMaxListeners(n[, ...eventTargets])`.
	*
	* With no targets this sets the default for emitters created afterwards; with targets it sets
	* the limit on each one, accepting both `EventEmitter`s and `EventTarget`s.
	*/
	function setMaxListeners(n = core.EventEmitter.defaultMaxListeners, ...eventTargets) {
		validateLimit$1(n);
		if (eventTargets.length === 0) {
			core.EventEmitter.defaultMaxListeners = n;
			return;
		}
		for (const target of eventTargets) if (isEventTarget$1(target)) eventTargetLimits.set(target, n);
		else if (typeof (target === null || target === void 0 ? void 0 : target.setMaxListeners) === "function") target.setMaxListeners(n);
		else throw invalidArgInstance("eventTargets", ["EventEmitter", "EventTarget"], target);
	}
	/** `events.getMaxListeners(emitterOrEventTarget)`. */
	function getMaxListeners(emitterOrEventTarget) {
		if (typeof (emitterOrEventTarget === null || emitterOrEventTarget === void 0 ? void 0 : emitterOrEventTarget.getMaxListeners) === "function") return emitterOrEventTarget.getMaxListeners();
		if (isEventTarget$1(emitterOrEventTarget)) {
			var _eventTargetLimits$ge;
			return (_eventTargetLimits$ge = eventTargetLimits.get(emitterOrEventTarget)) !== null && _eventTargetLimits$ge !== void 0 ? _eventTargetLimits$ge : core.EventEmitter.defaultMaxListeners;
		}
		throw invalidArgInstance("emitter", ["EventEmitter", "EventTarget"], emitterOrEventTarget);
	}
	return {
		getMaxListeners,
		setMaxListeners
	};
}
var eventTargetLimits;
var init_max_listeners = __esmMin(() => {
	init_errors$1();
	eventTargetLimits = /* @__PURE__ */ new WeakMap();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/objectSpread2.js
function ownKeys(e, r) {
	var t = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var o = Object.getOwnPropertySymbols(e);
		r && (o = o.filter(function(r) {
			return Object.getOwnPropertyDescriptor(e, r).enumerable;
		})), t.push.apply(t, o);
	}
	return t;
}
function _objectSpread2(e) {
	for (var r = 1; r < arguments.length; r++) {
		var t = null != arguments[r] ? arguments[r] : {};
		r % 2 ? ownKeys(Object(t), !0).forEach(function(r) {
			_defineProperty(e, r, t[r]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function(r) {
			Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
		});
	}
	return e;
}
var init_objectSpread2 = __esmMin(() => {
	init_defineProperty();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/events/index.js
/**
* Complete an emitter core with the module-level functions it is missing.
*
* Jco's `node:events` is unenv's `EventEmitter` plus these three. `EventEmitter` itself, `once`,
* `on`, `getEventListeners`, `addAbortListener` and `EventEmitterAsyncResource` all match Node
* already and are re-exported untouched.
*
* @param core - the emitter core to complete
* @returns the entry points to layer over it, each matching Node 24
*/
function completeEvents(core) {
	return _objectSpread2({ listenerCount: createListenerCount(core) }, createMaxListeners(core));
}
var init_events$3 = __esmMin(() => {
	init_listener_count();
	init_max_listeners();
	init_objectSpread2();
	init_errors$1();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/events.js
var init_events$2 = __esmMin(() => {
	init_events$3();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/async-hooks/context.js
function hasAsyncPropagation() {
	return propagation;
}
/** The bundler lowers await to Promise continuations before enabling this hook. */
function installAsyncPropagation() {
	if (propagation) return;
	propagation = true;
	const then = Promise.prototype.then;
	Promise.prototype.then = function(fulfilled, rejected) {
		const captured = captureAll();
		const bind = (callback) => typeof callback === "function" ? function(...args) {
			return withCaptured(captured, () => Reflect.apply(callback, this, args));
		} : callback;
		return Reflect.apply(then, this, [bind(fulfilled), bind(rejected)]);
	};
	const microtask = globalThis.queueMicrotask;
	if (microtask) globalThis.queueMicrotask = (callback) => {
		const captured = captureAll();
		microtask(() => withCaptured(captured, callback));
	};
}
/** Create a key with its own independent stack. */
function createKey() {
	const key = { id: nextId$1++ };
	stacks.set(key.id, []);
	return key;
}
/** The value currently in scope, or `undefined` outside any scope. */
function current(key) {
	const stack = stacks.get(key.id);
	return stack && stack.length > 0 ? stack[stack.length - 1] : void 0;
}
/** Run `fn` with `store` in scope, restoring the previous scope afterwards. */
function withStore(key, store, fn) {
	const stack = stacks.get(key.id);
	if (!stack) throw new Error$1("async context used after its storage was disabled");
	stack.push(store);
	try {
		return fn();
	} finally {
		stack.pop();
	}
}
/** Replace the value in the innermost scope, as `enterWith` does. */
function setCurrent(key, store) {
	const stack = stacks.get(key.id);
	if (!stack) return;
	if (stack.length === 0) stack.push(store);
	else stack[stack.length - 1] = store;
}
/** Drop every value, as `disable` does. */
function clear(key) {
	stacks.set(key.id, []);
}
/** Capture every storage's current value, for `snapshot`. */
function captureAll() {
	const captured = /* @__PURE__ */ new Map();
	for (const [id, stack] of stacks) if (stack.length > 0) captured.set(id, stack[stack.length - 1]);
	return captured;
}
/** Run `fn` with a previously captured set of values in scope. */
function withCaptured(captured, fn) {
	const entered = [];
	for (const [id, stack] of stacks) {
		stack.push(captured.get(id));
		entered.push(id);
	}
	try {
		return fn();
	} finally {
		for (const id of entered) {
			var _stacks$get;
			(_stacks$get = stacks.get(id)) === null || _stacks$get === void 0 || _stacks$get.pop();
		}
	}
}
var stacks, nextId$1, propagation;
var init_context = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	stacks = /* @__PURE__ */ new Map();
	nextId$1 = 1;
	propagation = false;
});
function schedule$1(callback, delay, kind) {
	const captured = captureAll();
	const original = callback;
	callback = () => withCaptured(captured, original);
	const immediate = kind === "immediate" && typeof globalThis.setImmediate === "function";
	const name = immediate ? "setImmediate" : kind === "interval" ? "setInterval" : "setTimeout";
	const clearName = immediate ? "clearImmediate" : kind === "interval" ? "clearInterval" : "clearTimeout";
	const start = globalThis[name];
	const clear = globalThis[clearName];
	if (typeof start !== "function" || typeof clear !== "function") {
		if (fallback) return fallback(callback, delay, kind);
		throw unsupportedNodeApi(`timers.${kind === "immediate" ? "setImmediate" : name}`, "the engine must supply task timers");
	}
	const handle = Reflect.apply(start, globalThis, immediate ? [callback] : [callback, delay]);
	return {
		cancel() {
			Reflect.apply(clear, globalThis, [handle]);
		},
		setRef(ref) {
			const method = ref ? "ref" : "unref";
			if (typeof handle === "object" && handle !== null) {
				const fn = Reflect.get(handle, method);
				if (typeof fn === "function") {
					Reflect.apply(fn, handle, []);
					return;
				}
			}
			if (!ref) throw unsupportedNodeApi("timers.unref", "the engine timer handle does not support event-loop reference control");
		}
	};
}
var fallback;
var init_runtime = __esmMin(() => {
	init_core();
	init_context();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/classPrivateMethodInitSpec.js
function _classPrivateMethodInitSpec(e, a) {
	_checkPrivateRedeclaration(e, a), a.add(e);
}
var init_classPrivateMethodInitSpec = __esmMin(() => {
	init_checkPrivateRedeclaration();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/timers/handles.js
/** Node delay coercion, with warning emission omitted (no implicit process capability). */
function normalizeDelay(after) {
	const value = after === void 0 ? 1 : after * 1;
	return value >= 1 && value <= 2 ** 31 - 1 ? Math.trunc(value) : 1;
}
function _start() {
	_classPrivateFieldSet2(_timer, this, schedule$1(() => {
		var _classPrivateFieldGet2$2;
		if (!_classPrivateFieldGet2(_repeat, this)) {
			_classPrivateFieldSet2(_timer, this, void 0);
			_classPrivateFieldSet2(_fired, this, true);
			knownTimersById.delete(_classPrivateFieldGet2(_id, this));
		}
		(_classPrivateFieldGet2$2 = _classPrivateFieldGet2(_callback, this)) === null || _classPrivateFieldGet2$2 === void 0 || _classPrivateFieldGet2$2.call(this);
	}, _classPrivateFieldGet2(_delay, this), _classPrivateFieldGet2(_repeat, this) ? "interval" : "timeout"));
	try {
		_classPrivateFieldGet2(_timer, this).setRef(_classPrivateFieldGet2(_refed, this));
	} catch (error) {
		_classPrivateFieldGet2(_timer, this).cancel();
		_classPrivateFieldSet2(_timer, this, void 0);
		throw error;
	}
}
function cancelTimeout(timer) {
	if (timer instanceof Timeout) timer.close();
	else if (typeof timer === "number" || typeof timer === "string") {
		var _knownTimersById$get;
		const id = typeof timer === "number" ? timer : Number(timer);
		if (typeof timer === "string" && String(id) !== timer) return;
		(_knownTimersById$get = knownTimersById.get(id)) === null || _knownTimersById$get === void 0 || _knownTimersById$get.close();
	}
}
var _Symbol$dispose, _Symbol$toPrimitive, _Symbol$dispose2, nextId, knownTimersById, _timer, _callback, _delay, _repeat, _refed, _id, _primitive, _fired, _Timeout_brand, Timeout, _timer2, _callback2, _refed2, Immediate;
var init_handles = __esmMin(() => {
	init_runtime();
	init_classPrivateMethodInitSpec();
	init_classPrivateFieldInitSpec();
	init_classPrivateFieldSet2();
	init_assertClassBrand();
	init_classPrivateFieldGet2();
	nextId = 1;
	knownTimersById = /* @__PURE__ */ new Map();
	_timer = /* @__PURE__ */ new WeakMap();
	_callback = /* @__PURE__ */ new WeakMap();
	_delay = /* @__PURE__ */ new WeakMap();
	_repeat = /* @__PURE__ */ new WeakMap();
	_refed = /* @__PURE__ */ new WeakMap();
	_id = /* @__PURE__ */ new WeakMap();
	_primitive = /* @__PURE__ */ new WeakMap();
	_fired = /* @__PURE__ */ new WeakMap();
	_Timeout_brand = /* @__PURE__ */ new WeakSet();
	_Symbol$dispose = Symbol.dispose;
	_Symbol$toPrimitive = Symbol.toPrimitive;
	Timeout = class {
		constructor(callback, delay, repeat) {
			_classPrivateMethodInitSpec(this, _Timeout_brand);
			_classPrivateFieldInitSpec(this, _timer, void 0);
			_classPrivateFieldInitSpec(this, _callback, void 0);
			_classPrivateFieldInitSpec(this, _delay, void 0);
			_classPrivateFieldInitSpec(this, _repeat, void 0);
			_classPrivateFieldInitSpec(this, _refed, true);
			_classPrivateFieldInitSpec(this, _id, nextId++);
			_classPrivateFieldInitSpec(this, _primitive, false);
			_classPrivateFieldInitSpec(this, _fired, false);
			_classPrivateFieldSet2(_callback, this, callback);
			_classPrivateFieldSet2(_delay, this, normalizeDelay(delay));
			_classPrivateFieldSet2(_repeat, this, repeat);
			_assertClassBrand(_Timeout_brand, this, _start).call(this);
		}
		refresh() {
			var _classPrivateFieldGet3;
			if (!_classPrivateFieldGet2(_callback, this)) return this;
			(_classPrivateFieldGet3 = _classPrivateFieldGet2(_timer, this)) === null || _classPrivateFieldGet3 === void 0 || _classPrivateFieldGet3.cancel();
			if (_classPrivateFieldGet2(_fired, this)) {
				_classPrivateFieldSet2(_id, this, nextId++);
				_classPrivateFieldSet2(_fired, this, false);
				if (_classPrivateFieldGet2(_primitive, this)) knownTimersById.set(_classPrivateFieldGet2(_id, this), this);
			}
			_assertClassBrand(_Timeout_brand, this, _start).call(this);
			return this;
		}
		unref() {
			var _classPrivateFieldGet4;
			(_classPrivateFieldGet4 = _classPrivateFieldGet2(_timer, this)) === null || _classPrivateFieldGet4 === void 0 || _classPrivateFieldGet4.setRef(false);
			_classPrivateFieldSet2(_refed, this, false);
			return this;
		}
		ref() {
			var _classPrivateFieldGet5;
			(_classPrivateFieldGet5 = _classPrivateFieldGet2(_timer, this)) === null || _classPrivateFieldGet5 === void 0 || _classPrivateFieldGet5.setRef(true);
			_classPrivateFieldSet2(_refed, this, true);
			return this;
		}
		hasRef() {
			return _classPrivateFieldGet2(_refed, this);
		}
		close() {
			var _classPrivateFieldGet6;
			(_classPrivateFieldGet6 = _classPrivateFieldGet2(_timer, this)) === null || _classPrivateFieldGet6 === void 0 || _classPrivateFieldGet6.cancel();
			_classPrivateFieldSet2(_timer, this, void 0);
			_classPrivateFieldSet2(_callback, this, void 0);
			knownTimersById.delete(_classPrivateFieldGet2(_id, this));
			return this;
		}
		[_Symbol$dispose]() {
			this.close();
		}
		[_Symbol$toPrimitive]() {
			if (!_classPrivateFieldGet2(_primitive, this) && _classPrivateFieldGet2(_callback, this) && !_classPrivateFieldGet2(_fired, this)) {
				_classPrivateFieldSet2(_primitive, this, true);
				knownTimersById.set(_classPrivateFieldGet2(_id, this), this);
			}
			return _classPrivateFieldGet2(_id, this);
		}
	};
	_timer2 = /* @__PURE__ */ new WeakMap();
	_callback2 = /* @__PURE__ */ new WeakMap();
	_refed2 = /* @__PURE__ */ new WeakMap();
	_Symbol$dispose2 = Symbol.dispose;
	Immediate = class {
		constructor(callback) {
			_classPrivateFieldInitSpec(this, _timer2, void 0);
			_classPrivateFieldInitSpec(this, _callback2, void 0);
			_classPrivateFieldInitSpec(this, _refed2, true);
			_classPrivateFieldSet2(_callback2, this, callback);
			_classPrivateFieldSet2(_timer2, this, schedule$1(() => {
				const fn = _classPrivateFieldGet2(_callback2, this);
				_classPrivateFieldSet2(_callback2, this, void 0);
				_classPrivateFieldSet2(_timer2, this, void 0);
				_classPrivateFieldSet2(_refed2, this, false);
				fn === null || fn === void 0 || fn.call(this);
			}, 0, "immediate"));
		}
		ref() {
			if (_classPrivateFieldGet2(_timer2, this)) {
				_classPrivateFieldGet2(_timer2, this).setRef(true);
				_classPrivateFieldSet2(_refed2, this, true);
			}
			return this;
		}
		unref() {
			if (_classPrivateFieldGet2(_timer2, this)) {
				_classPrivateFieldGet2(_timer2, this).setRef(false);
				_classPrivateFieldSet2(_refed2, this, false);
			}
			return this;
		}
		hasRef() {
			return _classPrivateFieldGet2(_refed2, this);
		}
		[_Symbol$dispose2]() {
			var _classPrivateFieldGet7;
			(_classPrivateFieldGet7 = _classPrivateFieldGet2(_timer2, this)) === null || _classPrivateFieldGet7 === void 0 || _classPrivateFieldGet7.cancel();
			_classPrivateFieldSet2(_timer2, this, void 0);
			_classPrivateFieldSet2(_callback2, this, void 0);
			_classPrivateFieldSet2(_refed2, this, false);
		}
	};
	for (const [prototype, keys] of [[Timeout.prototype, [
		"close",
		Symbol.dispose,
		Symbol.toPrimitive
	]], [Immediate.prototype, [Symbol.dispose]]]) for (const key of keys) Object.defineProperty(prototype, key, { enumerable: true });
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/timers/callbacks.js
function setTimeout$2(callback, delay, ...args) {
	validateFunction(callback, "callback");
	return new Timeout(function() {
		Reflect.apply(callback, this, args);
	}, delay, false);
}
function setInterval$2(callback, delay, ...args) {
	validateFunction(callback, "callback");
	return new Timeout(function() {
		Reflect.apply(callback, this, args);
	}, delay, true);
}
function setImmediate$1(callback, ...args) {
	validateFunction(callback, "callback");
	return new Immediate(function() {
		Reflect.apply(callback, this, args);
	});
}
function clearTimeout$1(timer) {
	cancelTimeout(timer);
}
function clearInterval$1(timer) {
	cancelTimeout(timer);
}
function clearImmediate(immediate) {
	if (immediate instanceof Immediate) immediate[Symbol.dispose]();
}
var init_callbacks = __esmMin(() => {
	init_validation();
	init_handles();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/OverloadYield.js
function _OverloadYield(e, d) {
	this.v = e, this.k = d;
}
var init_OverloadYield = __esmMin(() => {});
// \0@oxc-project+runtime@0.156.0/helpers/esm/awaitAsyncGenerator.js
function _awaitAsyncGenerator(e) {
	return new _OverloadYield(e, 0);
}
var init_awaitAsyncGenerator = __esmMin(() => {
	init_OverloadYield();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/wrapAsyncGenerator.js
function _wrapAsyncGenerator(e) {
	return function() {
		return new AsyncGenerator(e.apply(this, arguments));
	};
}
function AsyncGenerator(e) {
	var r, t;
	function resume(r, t) {
		try {
			var n = e[r](t), o = n.value, u = o instanceof _OverloadYield;
			Promise.resolve(u ? o.v : o).then(function(t) {
				if (u) {
					var i = "return" === r ? "return" : "next";
					if (!o.k || t.done) return resume(i, t);
					t = e[i](t).value;
				}
				settle(n.done ? "return" : "normal", t);
			}, function(e) {
				resume("throw", e);
			});
		} catch (e) {
			settle("throw", e);
		}
	}
	function settle(e, n) {
		switch (e) {
			case "return":
				r.resolve({
					value: n,
					done: !0
				});
				break;
			case "throw":
				r.reject(n);
				break;
			default: r.resolve({
				value: n,
				done: !1
			});
		}
		(r = r.next) ? resume(r.key, r.arg) : t = null;
	}
	this._invoke = function(e, n) {
		return new Promise(function(o, u) {
			var i = {
				key: e,
				arg: n,
				resolve: o,
				reject: u,
				next: null
			};
			t ? t = t.next = i : (r = t = i, resume(e, n));
		});
	}, "function" != typeof e["return"] && (this["return"] = void 0);
}
var init_wrapAsyncGenerator = __esmMin(() => {
	init_OverloadYield();
	AsyncGenerator.prototype["function" == typeof Symbol && Symbol.asyncIterator || "@@asyncIterator"] = function() {
		return this;
	}, AsyncGenerator.prototype.next = function(e) {
		return this._invoke("next", e);
	}, AsyncGenerator.prototype["throw"] = function(e) {
		return this._invoke("throw", e);
	}, AsyncGenerator.prototype["return"] = function(e) {
		return this._invoke("return", e);
	};
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/timers/promises.js
function validateOptions(options, delay) {
	if (delay !== void 0 && typeof delay !== "number") throw invalidArgType$1("delay", "number", delay);
	validateObject(options, "options");
	const signal = options.signal;
	if (signal !== void 0 && (signal === null || typeof signal !== "object" || !("aborted" in signal))) throw invalidArgType$1("options.signal", "AbortSignal", signal);
	if (options.ref !== void 0 && typeof options.ref !== "boolean") throw invalidArgType$1("options.ref", "boolean", options.ref);
}
function wait(_x, _x2, _x3, _x4) {
	return _wait.apply(this, arguments);
}
function _wait() {
	_wait = _asyncToGenerator(function* (kind, value, options, delay) {
		validateOptions(options, delay);
		const { signal, ref = true } = options;
		if (signal === null || signal === void 0 ? void 0 : signal.aborted) throw new AbortError$1(void 0, { cause: signal.reason });
		let timer;
		let oncancel;
		try {
			return yield new Promise((resolve, reject) => {
				timer = kind === "timeout" ? setTimeout$2(resolve, delay, value) : setImmediate$1(resolve, value);
				if (!ref) timer.unref();
				if (signal) {
					oncancel = () => {
						timer === null || timer === void 0 || timer[Symbol.dispose]();
						reject(new AbortError$1(void 0, { cause: signal.reason }));
					};
					signal.addEventListener("abort", oncancel);
				}
			});
		} finally {
			timer === null || timer === void 0 || timer[Symbol.dispose]();
			if (oncancel) signal.removeEventListener("abort", oncancel);
		}
	});
	return _wait.apply(this, arguments);
}
function setTimeout$1(delay, value, options = {}) {
	return wait("timeout", value, options, delay);
}
function setImmediate(value, options = {}) {
	return wait("immediate", value, options);
}
function setInterval$1(_x5, _x6) {
	return _setInterval.apply(this, arguments);
}
function _setInterval() {
	_setInterval = _wrapAsyncGenerator(function* (delay, value, options = {}) {
		validateOptions(options, delay);
		const { signal, ref = true } = options;
		if (signal === null || signal === void 0 ? void 0 : signal.aborted) throw new AbortError$1(void 0, { cause: signal.reason });
		let onCancel;
		let interval;
		try {
			let notYielded = 0;
			let callback;
			interval = setInterval$2(() => {
				notYielded++;
				if (callback) {
					callback();
					callback = void 0;
				}
			}, delay);
			if (!ref) interval.unref();
			if (signal) {
				onCancel = () => {
					clearInterval$1(interval);
					if (callback) {
						callback(Promise.reject(new AbortError$1(void 0, { cause: signal.reason })));
						callback = void 0;
					}
				};
				signal.addEventListener("abort", onCancel, { once: true });
			}
			while (!(signal === null || signal === void 0 ? void 0 : signal.aborted)) {
				if (notYielded === 0) yield _awaitAsyncGenerator(new Promise((resolve) => {
					callback = resolve;
				}));
				for (; notYielded > 0; notYielded--) yield value;
			}
			throw new AbortError$1(void 0, { cause: signal === null || signal === void 0 ? void 0 : signal.reason });
		} finally {
			clearInterval$1(interval);
			if (onCancel) signal.removeEventListener("abort", onCancel);
		}
	});
	return _setInterval.apply(this, arguments);
}
var kScheduler, Scheduler, scheduler$1, promises$1;
var init_promises = __esmMin(() => {
	init_core();
	init_validation();
	init_callbacks();
	init_asyncToGenerator();
	init_awaitAsyncGenerator();
	init_wrapAsyncGenerator();
	kScheduler = Symbol("kScheduler");
	Scheduler = class {
		constructor() {
			throw illegalConstructor();
		}
		yield() {
			if (!this[kScheduler]) throw invalidThis("Scheduler");
			return setImmediate();
		}
		wait(delay, options) {
			if (!this[kScheduler]) throw invalidThis("Scheduler");
			return setTimeout$1(delay, void 0, options);
		}
	};
	scheduler$1 = Object.assign(Object.create(Scheduler.prototype), { [kScheduler]: true });
	promises$1 = {
		setTimeout: setTimeout$1,
		setImmediate,
		setInterval: setInterval$1,
		scheduler: scheduler$1
	};
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/timers/index.js
var customPromisify, timers;
var init_timers$1 = __esmMin(() => {
	init_callbacks();
	init_promises();
	customPromisify = Symbol.for("nodejs.util.promisify.custom");
	Object.defineProperty(setTimeout$2, customPromisify, {
		enumerable: true,
		get: () => promises$1.setTimeout
	});
	Object.defineProperty(setImmediate$1, customPromisify, {
		enumerable: true,
		get: () => promises$1.setImmediate
	});
	timers = {
		setTimeout: setTimeout$2,
		clearTimeout: clearTimeout$1,
		setImmediate: setImmediate$1,
		clearImmediate,
		setInterval: setInterval$2,
		clearInterval: clearInterval$1,
		get promises() {
			return promises$1;
		}
	};
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/timers.js
var init_timers = __esmMin(() => {
	init_timers$1();
	init_timers$1();
});
// \0jco-node-builtin:node:timers
var _jco_node_builtin_node_timers_default;
var init__jco_node_builtin_node_timers = __esmMin(() => {
	init_timers();
	init_timers();
	_jco_node_builtin_node_timers_default = timers;
}), _globalThis$setTimeou, _globalThis$setTimeou2, _globalThis$clearTime, _globalThis$clearTime2, _globalThis$setInterv, _globalThis$setInterv2, _globalThis$clearInte, _globalThis$clearInte2, scoped, setTimeout;
var init__jco_node_builtin_timer_globals = __esmMin(() => {
	init__jco_node_builtin_node_timers();
	init_context();
	scoped = (timer) => function(callback, ...args) {
		const captured = captureAll();
		return timer(function(...values) {
			return withCaptured(captured, () => Reflect.apply(callback, this, values));
		}, ...args);
	};
	setTimeout = scoped((_globalThis$setTimeou = (_globalThis$setTimeou2 = globalThis.setTimeout) === null || _globalThis$setTimeou2 === void 0 ? void 0 : _globalThis$setTimeou2.bind(globalThis)) !== null && _globalThis$setTimeou !== void 0 ? _globalThis$setTimeou : _jco_node_builtin_node_timers_default.setTimeout);
	(_globalThis$clearTime = (_globalThis$clearTime2 = globalThis.clearTimeout) === null || _globalThis$clearTime2 === void 0 ? void 0 : _globalThis$clearTime2.bind(globalThis)) !== null && _globalThis$clearTime !== void 0 || _jco_node_builtin_node_timers_default.clearTimeout;
	scoped((_globalThis$setInterv = (_globalThis$setInterv2 = globalThis.setInterval) === null || _globalThis$setInterv2 === void 0 ? void 0 : _globalThis$setInterv2.bind(globalThis)) !== null && _globalThis$setInterv !== void 0 ? _globalThis$setInterv : _jco_node_builtin_node_timers_default.setInterval);
	(_globalThis$clearInte = (_globalThis$clearInte2 = globalThis.clearInterval) === null || _globalThis$clearInte2 === void 0 ? void 0 : _globalThis$clearInte2.bind(globalThis)) !== null && _globalThis$clearInte !== void 0 || _jco_node_builtin_node_timers_default.clearInterval;
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/async-hooks/errors.js
/**
* Thrown for `node:async_hooks` behavior that cannot work in a component.
*
* @param api - the public API being used, as a user would write it
* @param reason - why it cannot work here
*/
function unsupported(api, reason) {
	return unsupportedNodeApi(api, reason);
}
var ASYNC_REASON;
var init_errors = __esmMin(() => {
	init_core();
	ASYNC_REASON = "the store cannot survive an await. `await` resolves through the engine's internal PerformPromiseThen, which JavaScript cannot intercept, and this engine exposes no AsyncContext to carry the value instead. Rather than return an empty store later, Jco refuses here";
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/async-hooks/async-local-storage.js
/** Anything with a `then` is a continuation this module cannot follow. */
function isThenable(value) {
	return typeof value === "object" && value !== null && typeof value.then === "function" || typeof value === "function" && typeof value.then === "function";
}
/**
* Refuse work that would outlive the synchronous scope.
*
* Returning a thenable is the exact moment the store stops being reliable: the continuation runs
* after this scope has exited. Failing here points at the call site instead of surfacing later as
* an empty store somewhere unrelated.
*/
function rejectAsync(api, result) {
	if (!hasAsyncPropagation() && isThenable(result)) throw unsupported(api, ASYNC_REASON);
}
var _key, _disabled, AsyncLocalStorage;
var init_async_local_storage = __esmMin(() => {
	init_errors();
	init_context();
	init_classPrivateFieldInitSpec();
	init_classPrivateFieldGet2();
	init_classPrivateFieldSet2();
	_key = /* @__PURE__ */ new WeakMap();
	_disabled = /* @__PURE__ */ new WeakMap();
	AsyncLocalStorage = class AsyncLocalStorage {
		constructor() {
			_classPrivateFieldInitSpec(this, _key, createKey());
			_classPrivateFieldInitSpec(this, _disabled, false);
		}
		/** Optional label, matching Node's `name` accessor. */
		get name() {
			return "AsyncLocalStorage";
		}
		/** The store for the current synchronous scope, or `undefined` outside one. */
		getStore() {
			if (_classPrivateFieldGet2(_disabled, this)) return;
			return current(_classPrivateFieldGet2(_key, this));
		}
		/**
		* Run `callback` with `store` in scope.
		*
		* @throws when `callback` returns a thenable, which this engine cannot follow
		*/
		run(store, callback, ...args) {
			if (_classPrivateFieldGet2(_disabled, this)) return callback(...args);
			const result = withStore(_classPrivateFieldGet2(_key, this), store, () => callback(...args));
			rejectAsync("AsyncLocalStorage.run(store, callback)", result);
			return result;
		}
		/** Run `callback` with no store in scope. */
		exit(callback, ...args) {
			const result = withStore(_classPrivateFieldGet2(_key, this), void 0, () => callback(...args));
			rejectAsync("AsyncLocalStorage.exit(callback)", result);
			return result;
		}
		/**
		* Set the store for the remainder of the current synchronous scope.
		*
		* In Node this also reaches asynchronous continuations of the current context; here it does not,
		* and unlike `run` there is no return value to inspect, so the difference cannot be detected.
		*/
		enterWith(store) {
			if (_classPrivateFieldGet2(_disabled, this)) return;
			setCurrent(_classPrivateFieldGet2(_key, this), store);
		}
		/** Run `callback` with `store` in scope, matching Node's `withScope`. */
		withScope(callback, ...args) {
			const result = withStore(_classPrivateFieldGet2(_key, this), current(_classPrivateFieldGet2(_key, this)), () => callback(...args));
			rejectAsync("AsyncLocalStorage.withScope(callback)", result);
			return result;
		}
		/** Discard every store and make `getStore` return `undefined`. */
		disable() {
			_classPrivateFieldSet2(_disabled, this, true);
			clear(_classPrivateFieldGet2(_key, this));
		}
		/**
		* Capture the active stores so they can be restored inside another scope.
		*
		* Useful synchronously; it cannot restore context into an asynchronous continuation.
		*/
		static snapshot() {
			const captured = captureAll();
			return function runInSnapshot(callback, ...args) {
				const result = withCaptured(captured, () => callback(...args));
				rejectAsync("the callback given to AsyncLocalStorage.snapshot()", result);
				return result;
			};
		}
		/** Bind `fn` to the stores active now, so a later synchronous call sees them. */
		static bind(fn) {
			const runInSnapshot = AsyncLocalStorage.snapshot();
			return function bound(...args) {
				return runInSnapshot(() => Reflect.apply(fn, this, args));
			};
		}
	};
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/async-hooks/async-resource.js
var nextAsyncId, _type, _asyncId, _triggerAsyncId, _scope, AsyncResource, init_async_resource = __esmMin(() => {
	init_async_local_storage();
	init_errors();
	init_core();
	init_classPrivateFieldInitSpec();
	init_classPrivateFieldSet2();
	init_classPrivateFieldGet2();
	nextAsyncId = 1;
	_type = /* @__PURE__ */ new WeakMap();
	_asyncId = /* @__PURE__ */ new WeakMap();
	_triggerAsyncId = /* @__PURE__ */ new WeakMap();
	_scope = /* @__PURE__ */ new WeakMap();
	AsyncResource = class AsyncResource {
		constructor(type, options) {
			var _options$triggerAsync;
			_classPrivateFieldInitSpec(this, _type, void 0);
			_classPrivateFieldInitSpec(this, _asyncId, void 0);
			_classPrivateFieldInitSpec(this, _triggerAsyncId, void 0);
			_classPrivateFieldInitSpec(this, _scope, void 0);
			if (typeof type !== "string") throw invalidArgType$1("type", "string", type);
			_classPrivateFieldSet2(_type, this, type);
			_classPrivateFieldSet2(_asyncId, this, nextAsyncId++);
			_classPrivateFieldSet2(_triggerAsyncId, this, (_options$triggerAsync = options === null || options === void 0 ? void 0 : options.triggerAsyncId) !== null && _options$triggerAsync !== void 0 ? _options$triggerAsync : 0);
			_classPrivateFieldSet2(_scope, this, AsyncLocalStorage.snapshot());
		}
		/** The resource type given to the constructor. */
		get type() {
			return _classPrivateFieldGet2(_type, this);
		}
		/** Locally unique id. Stable, but not part of any runtime-tracked graph. */
		asyncId() {
			return _classPrivateFieldGet2(_asyncId, this);
		}
		/** The id this resource was created under, or `0` when none was supplied. */
		triggerAsyncId() {
			return _classPrivateFieldGet2(_triggerAsyncId, this);
		}
		/** Call `fn` with the stores that were active when this resource was constructed. */
		runInAsyncScope(fn, thisArg, ...args) {
			return _classPrivateFieldGet2(_scope, this).call(this, () => Reflect.apply(fn, thisArg, args));
		}
		/** Bind `fn` so a later synchronous call runs in this resource's scope. */
		bind(fn) {
			const scope = _classPrivateFieldGet2(_scope, this);
			return function bound(...args) {
				return scope(() => Reflect.apply(fn, this, args));
			};
		}
		/** Bind `fn` to the stores active now. */
		static bind(fn, type = "bound-anonymous-fn") {
			return new AsyncResource(type).bind(fn);
		}
		/**
		* Node emits a `destroy` hook here.
		*
		* There are no hooks to notify, so this would be a silent no-op; it throws instead, because a
		* caller emitting destroy is expecting an observer that does not exist.
		*/
		emitDestroy() {
			throw unsupported("asyncResource.emitDestroy()", "it notifies async hooks, and createHook is not supported in a component");
		}
	};
});
var init_async_hooks$1 = __esmMin(() => {
	init_errors();
	init_async_local_storage();
	init_async_resource();
	Object.freeze({});
});
var init_async_hooks = __esmMin(() => {
	init_async_hooks$1();
});
var init__jco_node_builtin_node_async_hooks = __esmMin(() => {
	init_context();
	init_async_hooks();
	installAsyncPropagation();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/unenv/dist/runtime/node/internal/events/events.mjs
function isEventTarget(emitter) {
	return typeof (emitter === null || emitter === void 0 ? void 0 : emitter.addEventListener) === "function";
}
function addCatch(that, promise, type, args) {
	if (!that[kCapture]) return;
	try {
		const then = promise.then;
		if (typeof then === "function") then.call(promise, void 0, function(err) {
			setTimeout(emitUnhandledRejectionOrErr, 0, that, err, type, args);
		});
	} catch (error_) {
		that.emit("error", error_);
	}
}
function emitUnhandledRejectionOrErr(ee, err, type, args) {
	if (typeof ee[kRejection] === "function") ee[kRejection](err, type, ...args);
	else {
		const prev = ee[kCapture];
		try {
			ee[kCapture] = false;
			ee.emit("error", err);
		} finally {
			ee[kCapture] = prev;
		}
	}
}
function _getMaxListeners(that) {
	if (that._maxListeners === void 0) return defaultMaxListeners$1;
	return that._maxListeners;
}
function enhanceStackTrace(err, own) {
	let ctorInfo = "";
	try {
		const { name } = this.constructor;
		if (name !== "EventEmitter") ctorInfo = ` on ${name} instance`;
	} catch (_unused3) {}
	const sep = `\nEmitted 'error' event${ctorInfo} at:\n`;
	const ownStack = (own.stack || "").split("\n").slice(1);
	return err.stack + sep + ownStack.join("\n");
}
function _addListener(target, type, listener, prepend) {
	let m;
	let events;
	let existing;
	events = target._events;
	if (events === void 0) {
		events = target._events = { __proto__: null };
		target._eventsCount = 0;
	} else {
		if (events.newListener !== void 0) {
			var _listener$listener;
			target.emit("newListener", type, (_listener$listener = listener.listener) !== null && _listener$listener !== void 0 ? _listener$listener : listener);
			events = target._events;
		}
		existing = events[type];
	}
	if (existing === void 0) {
		events[type] = listener;
		++target._eventsCount;
	} else {
		if (typeof existing === "function") existing = events[type] = prepend ? [listener, existing] : [existing, listener];
		else if (prepend) existing.unshift(listener);
		else existing.push(listener);
		m = _getMaxListeners(target);
		if (m > 0 && existing.length > m && !existing.warned) {
			existing.warned = true;
			const w = new genericNodeError(`Possible EventEmitter memory leak detected. ${existing.length} ${String(type)} listeners added to ${inspect$1(target, { depth: -1 })}. MaxListeners is ${m}. Use emitter.setMaxListeners() to increase limit`, {
				name: "MaxListenersExceededWarning",
				emitter: target,
				type,
				count: existing.length
			});
			_jco_node_builtin_console_globals_default.warn(w);
		}
	}
	return target;
}
function onceWrapper() {
	if (!this.fired) {
		this.target.removeListener(this.type, this.wrapFn);
		this.fired = true;
		if (arguments.length === 0) return this.listener.call(this.target);
		return this.listener.apply(this.target, arguments);
	}
}
function _onceWrap(target, type, listener) {
	const state = {
		fired: false,
		wrapFn: void 0,
		target,
		type,
		listener
	};
	const wrapped = onceWrapper.bind(state);
	wrapped.listener = listener;
	state.wrapFn = wrapped;
	return wrapped;
}
function _listeners$1(target, type, unwrap) {
	const events = target._events;
	if (events === void 0) return [];
	const evlistener = events[type];
	if (evlistener === void 0) return [];
	if (typeof evlistener === "function") return unwrap ? [evlistener.listener || evlistener] : [evlistener];
	return unwrap ? unwrapListeners(evlistener) : arrayClone(evlistener);
}
function arrayClone(arr) {
	switch (arr.length) {
		case 2: return [arr[0], arr[1]];
		case 3: return [
			arr[0],
			arr[1],
			arr[2]
		];
		case 4: return [
			arr[0],
			arr[1],
			arr[2],
			arr[3]
		];
		case 5: return [
			arr[0],
			arr[1],
			arr[2],
			arr[3],
			arr[4]
		];
		case 6: return [
			arr[0],
			arr[1],
			arr[2],
			arr[3],
			arr[4],
			arr[5]
		];
	}
	return Array.prototype.slice.call(arr);
}
function unwrapListeners(arr) {
	const ret = arrayClone(arr);
	for (let i = 0; i < ret.length; ++i) {
		const orig = ret[i].listener;
		if (typeof orig === "function") ret[i] = orig;
	}
	return ret;
}
function createIterResult(value, done) {
	return {
		value,
		done
	};
}
function eventTargetAgnosticRemoveListener(emitter, name, listener, flags) {
	if (typeof emitter.removeListener === "function") emitter.removeListener(name, listener);
	else if (typeof emitter.removeEventListener === "function") emitter.removeEventListener(name, listener, flags);
	else throw new ERR_INVALID_ARG_TYPE("emitter", "EventEmitter", emitter);
}
function eventTargetAgnosticAddListener(emitter, name, listener, flags) {
	if (typeof emitter.on === "function") {
		if (flags === null || flags === void 0 ? void 0 : flags.once) emitter.once(name, listener);
		else emitter.on(name, listener);
	} else if (typeof emitter.addEventListener === "function") emitter.addEventListener(name, listener, flags);
	else throw new ERR_INVALID_ARG_TYPE("emitter", "EventEmitter", emitter);
}
function listenersController() {
	const listeners = [];
	return {
		addEventListener(emitter, event, handler, flags) {
			eventTargetAgnosticAddListener(emitter, event, handler, flags);
			Array.prototype.push(listeners, [
				emitter,
				event,
				handler,
				flags
			]);
		},
		removeAll() {
			while (listeners.length > 0) Reflect.apply(eventTargetAgnosticRemoveListener, void 0, listeners.pop());
		}
	};
}
function spliceOne(list, index) {
	for (; index + 1 < list.length; index++) list[index] = list[index + 1];
	list.pop();
}
var defaultMaxListeners$1, AsyncIteratorPrototype, inspect$1, ERR_INVALID_THIS, ERR_UNHANDLED_ERROR, ERR_INVALID_ARG_TYPE, AbortError, genericNodeError, kRejection, kCapture, kErrorMonitor, kShapeMode, kMaxEventTargetListeners, kEnhanceStackBeforeInspector, kWatermarkData, kEventEmitter, kAsyncResource, kFirstEventParam, kResistStopPropagation, kMaxEventTargetListenersWarned, _EventEmitter, EventEmitterAsyncResource, EventEmitterReferencingAsyncResource, on, once, addAbortListener, getEventListeners, getMaxListeners$1, kSize, kMask, FixedCircularBuffer, FixedQueue;
var init_events$1 = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_console_globals();
	init__jco_node_builtin_microtask_globals();
	init__jco_node_builtin_timer_globals();
	init__jco_node_builtin_node_async_hooks();
	init_defineProperty();
	init_asyncToGenerator();
	defaultMaxListeners$1 = 10;
	AsyncIteratorPrototype = Function("return Object.getPrototypeOf(Object.getPrototypeOf(async function* () {}).prototype)")();
	inspect$1 = (value, _opts) => value;
	ERR_INVALID_THIS = Error$1;
	ERR_UNHANDLED_ERROR = Error$1;
	ERR_INVALID_ARG_TYPE = Error$1;
	AbortError = Error$1;
	genericNodeError = Error$1;
	kRejection = /* @__PURE__ */ Symbol.for("nodejs.rejection");
	kCapture = /* @__PURE__ */ Symbol.for("kCapture");
	kErrorMonitor = /* @__PURE__ */ Symbol.for("events.errorMonitor");
	kShapeMode = /* @__PURE__ */ Symbol.for("shapeMode");
	kMaxEventTargetListeners = /* @__PURE__ */ Symbol.for("events.maxEventTargetListeners");
	kEnhanceStackBeforeInspector = /* @__PURE__ */ Symbol.for("kEnhanceStackBeforeInspector");
	kWatermarkData = /* @__PURE__ */ Symbol.for("nodejs.watermarkData");
	kEventEmitter = /* @__PURE__ */ Symbol.for("kEventEmitter");
	kAsyncResource = /* @__PURE__ */ Symbol.for("kAsyncResource");
	kFirstEventParam = /* @__PURE__ */ Symbol.for("kFirstEventParam");
	kResistStopPropagation = /* @__PURE__ */ Symbol.for("kResistStopPropagation");
	kMaxEventTargetListenersWarned = /* @__PURE__ */ Symbol.for("events.maxEventTargetListenersWarned");
	_EventEmitter = class _EventEmitter {
		static get on() {
			return on;
		}
		static get once() {
			return once;
		}
		static get getEventListeners() {
			return getEventListeners;
		}
		static get getMaxListeners() {
			return getMaxListeners$1;
		}
		static get addAbortListener() {
			return addAbortListener;
		}
		static get EventEmitterAsyncResource() {
			return EventEmitterAsyncResource;
		}
		static get EventEmitter() {
			return _EventEmitter;
		}
		static setMaxListeners(n = defaultMaxListeners$1, ...eventTargets) {
			if (eventTargets.length === 0) defaultMaxListeners$1 = n;
			else for (const target of eventTargets) if (isEventTarget(target)) {
				target[kMaxEventTargetListeners] = n;
				target[kMaxEventTargetListenersWarned] = false;
			} else if (typeof target.setMaxListeners === "function") target.setMaxListeners(n);
			else throw new ERR_INVALID_ARG_TYPE("eventTargets", ["EventEmitter", "EventTarget"], target);
		}
		static listenerCount(emitter, type) {
			if (typeof emitter.listenerCount === "function") return emitter.listenerCount(type);
			_EventEmitter.prototype.listenerCount.call(emitter, type);
		}
		static init() {
			throw new Error$1("EventEmitter.init() is not implemented.");
		}
		static get captureRejections() {
			return this[kCapture];
		}
		static set captureRejections(value) {
			this[kCapture] = value;
		}
		static get defaultMaxListeners() {
			return defaultMaxListeners$1;
		}
		static set defaultMaxListeners(arg) {
			defaultMaxListeners$1 = arg;
		}
		constructor(opts) {
			_defineProperty(this, "_events", void 0);
			_defineProperty(this, "_eventsCount", 0);
			_defineProperty(this, "_maxListeners", defaultMaxListeners$1);
			_defineProperty(this, kCapture, false);
			_defineProperty(this, kShapeMode, false);
			if (this._events === void 0 || this._events === Object.getPrototypeOf(this)._events) {
				this._events = { __proto__: null };
				this._eventsCount = 0;
				this[kShapeMode] = false;
			} else this[kShapeMode] = true;
			this._maxListeners = this._maxListeners || void 0;
			if (opts === null || opts === void 0 ? void 0 : opts.captureRejections) this[kCapture] = Boolean(opts.captureRejections);
			else this[kCapture] = _EventEmitter.prototype[kCapture];
		}
		/**
		* Increases the max listeners of the event emitter.
		* @param {number} n
		* @returns {EventEmitter}
		*/
		setMaxListeners(n) {
			this._maxListeners = n;
			return this;
		}
		/**
		* Returns the current max listener value for the event emitter.
		* @returns {number}
		*/
		getMaxListeners() {
			return _getMaxListeners(this);
		}
		/**
		* Synchronously calls each of the listeners registered
		* for the event.
		* @param {...any} [args]
		* @returns {boolean}
		*/
		emit(type, ...args) {
			let doError = type === "error";
			const events = this._events;
			if (events !== void 0) {
				if (doError && events[kErrorMonitor] !== void 0) this.emit(kErrorMonitor, ...args);
				doError = doError && events.error === void 0;
			} else if (!doError) return false;
			if (doError) {
				let er;
				if (args.length > 0) er = args[0];
				if (er instanceof Error$1) {
					try {
						var _Error$captureStackTr, _Error;
						const capture = {};
						(_Error$captureStackTr = (_Error = Error$1).captureStackTrace) === null || _Error$captureStackTr === void 0 || _Error$captureStackTr.call(_Error, capture, _EventEmitter.prototype.emit);
						Object.defineProperty(er, kEnhanceStackBeforeInspector, {
							__proto__: null,
							value: Function.prototype.bind(enhanceStackTrace, this, er, capture),
							configurable: true
						});
					} catch (_unused) {}
					throw er;
				}
				let stringifiedEr;
				try {
					stringifiedEr = inspect$1(er);
				} catch (_unused2) {
					stringifiedEr = er;
				}
				const err = new ERR_UNHANDLED_ERROR(stringifiedEr);
				err.context = er;
				throw err;
			}
			const handler = events[type];
			if (handler === void 0) return false;
			if (typeof handler === "function") {
				const result = handler.apply(this, args);
				if (result !== void 0 && result !== null) addCatch(this, result, type, args);
			} else {
				const len = handler.length;
				const listeners = arrayClone(handler);
				for (let i = 0; i < len; ++i) {
					const result = listeners[i].apply(this, args);
					if (result !== void 0 && result !== null) addCatch(this, result, type, args);
				}
			}
			return true;
		}
		/**
		* Adds a listener to the event emitter.
		* @returns {EventEmitter}
		*/
		addListener(type, listener) {
			_addListener(this, type, listener, false);
			return this;
		}
		on(type, listener) {
			return this.addListener(type, listener);
		}
		/**
		* Adds the `listener` function to the beginning of
		* the listeners array.
		*/
		prependListener(type, listener) {
			_addListener(this, type, listener, true);
			return this;
		}
		/**
		* Adds a one-time `listener` function to the event emitter.
		*/
		once(type, listener) {
			this.on(type, _onceWrap(this, type, listener));
			return this;
		}
		/**
		* Adds a one-time `listener` function to the beginning of
		* the listeners array.
		*/
		prependOnceListener(type, listener) {
			this.prependListener(type, _onceWrap(this, type, listener));
			return this;
		}
		/**
		* Removes the specified `listener` from the listeners array.
		* @param {string | symbol} type
		* @param {Function} listener
		* @returns {EventEmitter}
		*/
		removeListener(type, listener) {
			const events = this._events;
			if (events === void 0) return this;
			const list = events[type];
			if (list === void 0) return this;
			if (list === listener || list.listener === listener) {
				this._eventsCount -= 1;
				if (this[kShapeMode]) events[type] = void 0;
				else if (this._eventsCount === 0) this._events = { __proto__: null };
				else {
					delete events[type];
					if (events.removeListener) this.emit("removeListener", type, list.listener || listener);
				}
			} else if (typeof list !== "function") {
				let position = -1;
				for (let i = list.length - 1; i >= 0; i--) if (list[i] === listener || list[i].listener === listener) {
					position = i;
					break;
				}
				if (position < 0) return this;
				if (position === 0) list.shift();
				else spliceOne(list, position);
				if (list.length === 1) events[type] = list[0];
				if (events.removeListener !== void 0) this.emit("removeListener", type, listener);
			}
			return this;
		}
		off(type, listener) {
			return this.removeListener(type, listener);
		}
		/**
		* Removes all listeners from the event emitter. (Only
		* removes listeners for a specific event name if specified
		* as `type`).
		*/
		removeAllListeners(type) {
			const events = this._events;
			if (events === void 0) return this;
			if (events.removeListener === void 0) {
				if (arguments.length === 0) {
					this._events = { __proto__: null };
					this._eventsCount = 0;
				} else if (events[type] !== void 0) {
					if (--this._eventsCount === 0) this._events = { __proto__: null };
					else delete events[type];
				}
				this[kShapeMode] = false;
				return this;
			}
			if (arguments.length === 0) {
				for (const key of Reflect.ownKeys(events)) {
					if (key === "removeListener") continue;
					this.removeAllListeners(key);
				}
				this.removeAllListeners("removeListener");
				this._events = { __proto__: null };
				this._eventsCount = 0;
				this[kShapeMode] = false;
				return this;
			}
			const listeners = events[type];
			if (typeof listeners === "function") this.removeListener(type, listeners);
			else if (listeners !== void 0) for (let i = listeners.length - 1; i >= 0; i--) this.removeListener(type, listeners[i]);
			return this;
		}
		/**
		* Returns a copy of the array of listeners for the event name
		* specified as `type`.
		* @param {string | symbol} type
		* @returns {Function[]}
		*/
		listeners(type) {
			return _listeners$1(this, type, true);
		}
		/**
		* Returns a copy of the array of listeners and wrappers for
		* the event name specified as `type`.
		* @returns {Function[]}
		*/
		rawListeners(type) {
			return _listeners$1(this, type, false);
		}
		/**
		* Returns an array listing the events for which
		* the emitter has registered listeners.
		* @returns {any[]}
		*/
		eventNames() {
			return this._eventsCount > 0 ? Reflect.ownKeys(this._events) : [];
		}
		/**
		* Returns the number of listeners listening to event name
		*/
		listenerCount(eventName, listener) {
			const events = this._events;
			if (events !== void 0) {
				const evlistener = events[eventName];
				if (typeof evlistener === "function") {
					if (listener != null) return listener === evlistener || listener === evlistener.listener ? 1 : 0;
					return 1;
				} else if (evlistener !== void 0) {
					if (listener != null) {
						let matching = 0;
						for (let i = 0, l = evlistener.length; i < l; i++) if (evlistener[i] === listener || evlistener[i].listener === listener) matching++;
						return matching;
					}
					return evlistener.length;
				}
			}
			return 0;
		}
	};
	_defineProperty(_EventEmitter, "captureRejectionSymbol", kRejection);
	_defineProperty(_EventEmitter, "errorMonitor", kErrorMonitor);
	_defineProperty(_EventEmitter, "kMaxEventTargetListeners", kMaxEventTargetListeners);
	_defineProperty(_EventEmitter, "kMaxEventTargetListenersWarned", kMaxEventTargetListenersWarned);
	_defineProperty(_EventEmitter, "usingDomains", false);
	EventEmitterAsyncResource = class extends _EventEmitter {
		/**
		* @param {{
		*   name?: string,
		*   triggerAsyncId?: number,
		*   requireManualDestroy?: boolean,
		* }} [options]
		*/
		constructor(options) {
			let name;
			if (typeof options === "string") {
				name = options;
				options = void 0;
			} else name = (options === null || options === void 0 ? void 0 : options.name) || new.target.name;
			super(options);
			this[kAsyncResource] = new EventEmitterReferencingAsyncResource(this, name, options);
		}
		/**
		* @param {symbol,string} event
		* @param  {...any} args
		* @returns {boolean}
		*/
		emit(event, ...args) {
			if (this[kAsyncResource] === void 0) throw new ERR_INVALID_THIS("EventEmitterAsyncResource");
			const { asyncResource } = this;
			Array.prototype.unshift(args, super.emit, this, event);
			return Reflect.apply(asyncResource.runInAsyncScope, asyncResource, args);
		}
		/**
		* @returns {void}
		*/
		emitDestroy() {
			if (this[kAsyncResource] === void 0) throw new ERR_INVALID_THIS("EventEmitterAsyncResource");
			this.asyncResource.emitDestroy();
		}
		/**
		* @type {number}
		*/
		get asyncId() {
			if (this[kAsyncResource] === void 0) throw new ERR_INVALID_THIS("EventEmitterAsyncResource");
			return this.asyncResource.asyncId();
		}
		/**
		* @type {number}
		*/
		get triggerAsyncId() {
			if (this[kAsyncResource] === void 0) throw new ERR_INVALID_THIS("EventEmitterAsyncResource");
			return this.asyncResource.triggerAsyncId();
		}
		/**
		* @type {EventEmitterReferencingAsyncResource}
		*/
		get asyncResource() {
			if (this[kAsyncResource] === void 0) throw new ERR_INVALID_THIS("EventEmitterAsyncResource");
			return this[kAsyncResource];
		}
	};
	EventEmitterReferencingAsyncResource = class extends AsyncResource {
		/**
		* @param {EventEmitter} ee
		* @param {string} [type]
		* @param {{
		*   triggerAsyncId?: number,
		*   requireManualDestroy?: boolean,
		* }} [options]
		*/
		constructor(ee, type, options) {
			super(type, options);
			this[kEventEmitter] = ee;
		}
		/**
		* @type {EventEmitter}
		*/
		get eventEmitter() {
			if (this[kEventEmitter] === void 0) throw new ERR_INVALID_THIS("EventEmitterReferencingAsyncResource");
			return this[kEventEmitter];
		}
	};
	on = function on(emitter, event, options = {}) {
		var _ref, _options$highWaterMar, _ref2, _options$lowWaterMark;
		const signal = options.signal;
		if (signal === null || signal === void 0 ? void 0 : signal.aborted) throw new AbortError(void 0, { cause: signal === null || signal === void 0 ? void 0 : signal.reason });
		const highWatermark = (_ref = (_options$highWaterMar = options.highWaterMark) !== null && _options$highWaterMar !== void 0 ? _options$highWaterMar : options.highWatermark) !== null && _ref !== void 0 ? _ref : Number.MAX_SAFE_INTEGER;
		const lowWatermark = (_ref2 = (_options$lowWaterMark = options.lowWaterMark) !== null && _options$lowWaterMark !== void 0 ? _options$lowWaterMark : options.lowWatermark) !== null && _ref2 !== void 0 ? _ref2 : 1;
		const unconsumedEvents = new FixedQueue();
		const unconsumedPromises = new FixedQueue();
		let paused = false;
		let error = null;
		let finished = false;
		let size = 0;
		const iterator = Object.setPrototypeOf({
			next() {
				if (size) {
					const value = unconsumedEvents.shift();
					size--;
					if (paused && size < lowWatermark) {
						var _emitter$resume;
						(_emitter$resume = emitter.resume) === null || _emitter$resume === void 0 || _emitter$resume.call(emitter);
						paused = false;
					}
					return Promise.resolve(createIterResult(value, false));
				}
				if (error) {
					const p = Promise.reject(error);
					error = null;
					return p;
				}
				if (finished) return closeHandler();
				return new Promise(function(resolve, reject) {
					unconsumedPromises.push({
						resolve,
						reject
					});
				});
			},
			return() {
				return closeHandler();
			},
			throw(err) {
				if (!err || !(err instanceof Error$1)) throw new ERR_INVALID_ARG_TYPE("EventEmitter.AsyncIterator", "Error", err);
				errorHandler(err);
			},
			[Symbol.asyncIterator]() {
				return this;
			},
			[kWatermarkData]: {
				get size() {
					return size;
				},
				get low() {
					return lowWatermark;
				},
				get high() {
					return highWatermark;
				},
				get isPaused() {
					return paused;
				}
			}
		}, AsyncIteratorPrototype);
		const { addEventListener, removeAll } = listenersController();
		addEventListener(emitter, event, options[kFirstEventParam] ? eventHandler : function(...args) {
			return eventHandler(args);
		});
		if (event !== "error" && typeof emitter.on === "function") addEventListener(emitter, "error", errorHandler);
		const closeEvents = options === null || options === void 0 ? void 0 : options.close;
		if (closeEvents === null || closeEvents === void 0 ? void 0 : closeEvents.length) for (const closeEvent of closeEvents) addEventListener(emitter, closeEvent, closeHandler);
		const abortListenerDisposable = signal ? addAbortListener(signal, abortListener) : null;
		return iterator;
		function abortListener() {
			errorHandler(new AbortError(void 0, { cause: signal === null || signal === void 0 ? void 0 : signal.reason }));
		}
		function eventHandler(value) {
			if (unconsumedPromises.isEmpty()) {
				size++;
				if (!paused && size > highWatermark) {
					var _emitter$pause;
					paused = true;
					(_emitter$pause = emitter.pause) === null || _emitter$pause === void 0 || _emitter$pause.call(emitter);
				}
				unconsumedEvents.push(value);
			} else unconsumedPromises.shift().resolve(createIterResult(value, false));
		}
		function errorHandler(err) {
			if (unconsumedPromises.isEmpty()) error = err;
			else unconsumedPromises.shift().reject(err);
			closeHandler();
		}
		function closeHandler() {
			abortListenerDisposable === null || abortListenerDisposable === void 0 || abortListenerDisposable[Symbol.dispose]();
			removeAll();
			finished = true;
			const doneResult = createIterResult(void 0, true);
			while (!unconsumedPromises.isEmpty()) unconsumedPromises.shift().resolve(doneResult);
			return Promise.resolve(doneResult);
		}
	};
	once = /* @__PURE__ */ function() {
		var _once = _asyncToGenerator(function* (emitter, name, options = {}) {
			const signal = options === null || options === void 0 ? void 0 : options.signal;
			if (signal === null || signal === void 0 ? void 0 : signal.aborted) throw new AbortError(void 0, { cause: signal === null || signal === void 0 ? void 0 : signal.reason });
			return new Promise((resolve, reject) => {
				const errorListener = (err) => {
					if (typeof emitter.removeListener === "function") emitter.removeListener(name, resolver);
					if (signal != null) eventTargetAgnosticRemoveListener(signal, "abort", abortListener);
					reject(err);
				};
				const resolver = (...args) => {
					if (typeof emitter.removeListener === "function") emitter.removeListener("error", errorListener);
					if (signal != null) eventTargetAgnosticRemoveListener(signal, "abort", abortListener);
					resolve(args);
				};
				eventTargetAgnosticAddListener(emitter, name, resolver, {
					__proto__: null,
					once: true,
					[kResistStopPropagation]: true
				});
				if (name !== "error" && typeof emitter.once === "function") emitter.once("error", errorListener);
				function abortListener() {
					eventTargetAgnosticRemoveListener(emitter, name, resolver);
					eventTargetAgnosticRemoveListener(emitter, "error", errorListener);
					reject(new AbortError(void 0, { cause: signal === null || signal === void 0 ? void 0 : signal.reason }));
				}
				if (signal != null) eventTargetAgnosticAddListener(signal, "abort", abortListener, {
					__proto__: null,
					once: true,
					[kResistStopPropagation]: true
				});
			});
		});
		function once(_x, _x2) {
			return _once.apply(this, arguments);
		}
		return once;
	}();
	addAbortListener = function addAbortListener(signal, listener) {
		if (signal === void 0) throw new ERR_INVALID_ARG_TYPE("signal", "AbortSignal", signal);
		let removeEventListener;
		if (signal.aborted) queueMicrotask(() => listener());
		else {
			signal.addEventListener("abort", listener, {
				__proto__: null,
				once: true,
				[kResistStopPropagation]: true
			});
			removeEventListener = () => {
				signal.removeEventListener("abort", listener);
			};
		}
		return {
			__proto__: null,
			[Symbol.dispose]() {
				removeEventListener === null || removeEventListener === void 0 || removeEventListener();
			}
		};
	};
	getEventListeners = function getEventListeners(emitterOrTarget, type) {
		if (typeof emitterOrTarget.listeners === "function") return emitterOrTarget.listeners(type);
		if (isEventTarget(emitterOrTarget)) {
			const root = emitterOrTarget[kEvents].get(type);
			const listeners = [];
			let handler = root === null || root === void 0 ? void 0 : root.next;
			while ((handler === null || handler === void 0 ? void 0 : handler.listener) !== void 0) {
				var _handler$listener;
				const listener = ((_handler$listener = handler.listener) === null || _handler$listener === void 0 ? void 0 : _handler$listener.deref) ? handler.listener.deref() : handler.listener;
				listeners.push(listener);
				handler = handler.next;
			}
			return listeners;
		}
		throw new ERR_INVALID_ARG_TYPE("emitter", ["EventEmitter", "EventTarget"], emitterOrTarget);
	};
	getMaxListeners$1 = function getMaxListeners(emitterOrTarget) {
		if (typeof (emitterOrTarget === null || emitterOrTarget === void 0 ? void 0 : emitterOrTarget.getMaxListeners) === "function") return _getMaxListeners(emitterOrTarget);
		else if (emitterOrTarget === null || emitterOrTarget === void 0 ? void 0 : emitterOrTarget[kMaxEventTargetListeners]) return emitterOrTarget[kMaxEventTargetListeners];
		throw new ERR_INVALID_ARG_TYPE("emitter", ["EventEmitter", "EventTarget"], emitterOrTarget);
	};
	kSize = 2048;
	kMask = kSize - 1;
	FixedCircularBuffer = class {
		constructor() {
			_defineProperty(this, "bottom", void 0);
			_defineProperty(this, "top", void 0);
			_defineProperty(this, "list", void 0);
			_defineProperty(this, "next", void 0);
			this.bottom = 0;
			this.top = 0;
			this.list = new Array(kSize);
			this.next = null;
		}
		isEmpty() {
			return this.top === this.bottom;
		}
		isFull() {
			return (this.top + 1 & kMask) === this.bottom;
		}
		push(data) {
			this.list[this.top] = data;
			this.top = this.top + 1 & kMask;
		}
		shift() {
			const nextItem = this.list[this.bottom];
			if (nextItem === void 0) return null;
			this.list[this.bottom] = void 0;
			this.bottom = this.bottom + 1 & kMask;
			return nextItem;
		}
	};
	FixedQueue = class {
		constructor() {
			_defineProperty(this, "head", void 0);
			_defineProperty(this, "tail", void 0);
			this.head = this.tail = new FixedCircularBuffer();
		}
		isEmpty() {
			return this.head.isEmpty();
		}
		push(data) {
			if (this.head.isFull()) this.head = this.head.next = new FixedCircularBuffer();
			this.head.push(data);
		}
		shift() {
			const tail = this.tail;
			const next = tail.shift();
			if (tail.isEmpty() && tail.next !== null) {
				this.tail = tail.next;
				tail.next = null;
			}
			return next;
		}
	};
});
/* @__NO_SIDE_EFFECTS__ */
function createNotImplementedError(name) {
	return new Error$1(`[unenv] ${name} is not implemented yet!`);
}
/* @__NO_SIDE_EFFECTS__ */
function notImplemented(name) {
	const fn = () => {
		throw /* @__PURE__ */ createNotImplementedError(name);
	};
	return Object.assign(fn, { __unenv__: true });
}
var init_utils = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init_defineProperty();
}), captureRejectionSymbol, errorMonitor, init, events_default;
var init_events = __esmMin(() => {
	init_events$1();
	init_utils();
	captureRejectionSymbol = /* @__PURE__ */ Symbol.for("nodejs.rejection");
	errorMonitor = /* @__PURE__ */ Symbol.for("events.errorMonitor");
	init = /* @__PURE__ */ notImplemented("node:events.init");
	events_default = _EventEmitter;
});
// \0jco-node-builtin:node:events
var _jco_node_builtin_node_events_exports = /* @__PURE__ */ __exportAll({
	EventEmitter: () => EventEmitter$1,
	EventEmitterAsyncResource: () => EventEmitterAsyncResource,
	addAbortListener: () => addAbortListener,
	captureRejectionSymbol: () => captureRejectionSymbol,
	captureRejections: () => false,
	default: () => events,
	defaultMaxListeners: () => 10,
	errorMonitor: () => errorMonitor,
	getEventListeners: () => getEventListeners,
	getMaxListeners: () => getMaxListeners,
	init: () => init,
	listenerCount: () => listenerCount,
	on: () => on,
	once: () => once,
	setMaxListeners: () => setMaxListeners,
	usingDomains: () => false
});
function EventEmitter$1(options) {
	const initialized = new events_default(options);
	return this === void 0 ? initialized : Object.assign(this, initialized);
}
var events, completed, getMaxListeners, listenerCount, setMaxListeners;
var init__jco_node_builtin_node_events = __esmMin(() => {
	init_events$2();
	init_events();
	init_events();
	Object.setPrototypeOf(EventEmitter$1, events_default);
	EventEmitter$1.prototype = events_default.prototype;
	Object.defineProperty(EventEmitter$1.prototype, "constructor", {
		configurable: true,
		writable: true,
		value: EventEmitter$1
	});
	events = EventEmitter$1;
	completed = completeEvents(events);
	getMaxListeners = completed.getMaxListeners;
	listenerCount = completed.listenerCount;
	setMaxListeners = completed.setMaxListeners;
	for (const [name, value] of Object.entries(completed)) Object.defineProperty(events, name, {
		configurable: true,
		value,
		writable: true
	});
	Object.defineProperty(events, "EventEmitter", {
		configurable: true,
		writable: true,
		value: EventEmitter$1
	});
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/emitter.js
/**
* readable-stream initializes its EventEmitter base with EventEmitter.call(this).
* Jco's audited unenv emitter is an ES class with public instance state. Adapt
* that constructor call while keeping its prototype and instanceof identity.
*/
function callableEmitter(Emitter) {
	for (const [name, target] of [["on", "addListener"], ["off", "removeListener"]]) Object.defineProperty(Emitter.prototype, name, _objectSpread2(_objectSpread2({}, Object.getOwnPropertyDescriptor(Emitter.prototype, name)), {}, { value: Reflect.get(Emitter.prototype, target) }));
	return new Proxy(Emitter, { apply(target, receiver, args) {
		const initial = Reflect.construct(target, args);
		for (const key of Reflect.ownKeys(initial)) if (!Object.prototype.hasOwnProperty.call(receiver, key)) Object.defineProperty(receiver, key, Object.getOwnPropertyDescriptor(initial, key));
		return receiver;
	} });
}
var init_emitter = __esmMin(() => {
	init_objectSpread2();
});
// \0jco-node-builtin:stream-events
var _jco_node_builtin_stream_events_exports = /* @__PURE__ */ __exportAll({
	EventEmitter: () => EventEmitter,
	EventEmitterAsyncResource: () => EventEmitterAsyncResource,
	addAbortListener: () => addAbortListener,
	captureRejectionSymbol: () => captureRejectionSymbol,
	captureRejections: () => false,
	default: () => _jco_node_builtin_stream_events_default,
	defaultMaxListeners: () => 10,
	errorMonitor: () => errorMonitor,
	getEventListeners: () => getEventListeners,
	getMaxListeners: () => getMaxListeners,
	init: () => init,
	listenerCount: () => listenerCount,
	on: () => on,
	once: () => once,
	setMaxListeners: () => setMaxListeners,
	usingDomains: () => false
});
var EventEmitter, _jco_node_builtin_stream_events_default;
var init__jco_node_builtin_stream_events = __esmMin(() => {
	init__jco_node_builtin_node_events();
	init_emitter();
	init_objectSpread2();
	init__jco_node_builtin_node_events();
	EventEmitter = callableEmitter(EventEmitter$1);
	_jco_node_builtin_stream_events_default = _objectSpread2(_objectSpread2({}, _jco_node_builtin_node_events_exports), {}, { EventEmitter });
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/ours/util.js
var require_util = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init__jco_node_builtin_microtask_globals();
	init_asyncToGenerator();
	const bufferModule = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { format, inspect } = require_inspect();
	const { codes: { ERR_INVALID_ARG_TYPE } } = require_errors();
	const { kResistStopPropagation, AggregateError, SymbolDispose } = require_primordials();
	const AbortSignal = globalThis.AbortSignal || require_abort_controller().AbortSignal;
	const AbortController = globalThis.AbortController || require_abort_controller().AbortController;
	const AsyncFunction = Object.getPrototypeOf(_asyncToGenerator(function* () {})).constructor;
	const Blob = globalThis.Blob || bufferModule.Blob;
	const isBlob = typeof Blob !== "undefined" ? function isBlob(b) {
		return b instanceof Blob;
	} : function isBlob(b) {
		return false;
	};
	const validateAbortSignal = (signal, name) => {
		if (signal !== void 0 && (signal === null || typeof signal !== "object" || !("aborted" in signal))) throw new ERR_INVALID_ARG_TYPE(name, "AbortSignal", signal);
	};
	const validateFunction = (value, name) => {
		if (typeof value !== "function") throw new ERR_INVALID_ARG_TYPE(name, "Function", value);
	};
	module.exports = {
		AggregateError,
		kEmptyObject: Object.freeze({}),
		once(callback) {
			let called = false;
			return function(...args) {
				if (called) return;
				called = true;
				callback.apply(this, args);
			};
		},
		createDeferredPromise: function() {
			let resolve;
			let reject;
			return {
				promise: new Promise((res, rej) => {
					resolve = res;
					reject = rej;
				}),
				resolve,
				reject
			};
		},
		promisify(fn) {
			return new Promise((resolve, reject) => {
				fn((err, ...args) => {
					if (err) return reject(err);
					return resolve(...args);
				});
			});
		},
		debuglog() {
			return function() {};
		},
		format,
		inspect,
		types: {
			isAsyncFunction(fn) {
				return fn instanceof AsyncFunction;
			},
			isArrayBufferView(arr) {
				return ArrayBuffer.isView(arr);
			}
		},
		isBlob,
		deprecate(fn, message) {
			return fn;
		},
		addAbortListener: (init__jco_node_builtin_stream_events(), __toCommonJS(_jco_node_builtin_stream_events_exports)).addAbortListener || function addAbortListener(signal, listener) {
			if (signal === void 0) throw new ERR_INVALID_ARG_TYPE("signal", "AbortSignal", signal);
			validateAbortSignal(signal, "signal");
			validateFunction(listener, "listener");
			let removeEventListener;
			if (signal.aborted) queueMicrotask(() => listener());
			else {
				signal.addEventListener("abort", listener, {
					__proto__: null,
					once: true,
					[kResistStopPropagation]: true
				});
				removeEventListener = () => {
					signal.removeEventListener("abort", listener);
				};
			}
			return {
				__proto__: null,
				[SymbolDispose]() {
					var _removeEventListener;
					(_removeEventListener = removeEventListener) === null || _removeEventListener === void 0 || _removeEventListener();
				}
			};
		},
		AbortSignalAny: AbortSignal.any || function AbortSignalAny(signals) {
			if (signals.length === 1) return signals[0];
			const ac = new AbortController();
			const abort = () => ac.abort();
			signals.forEach((signal) => {
				validateAbortSignal(signal, "signals");
				signal.addEventListener("abort", abort, { once: true });
			});
			ac.signal.addEventListener("abort", () => {
				signals.forEach((signal) => signal.removeEventListener("abort", abort));
			}, { once: true });
			return ac.signal;
		}
	};
	module.exports.promisify.custom = Symbol.for("nodejs.util.promisify.custom");
}));
// \0@oxc-project+runtime@0.156.0/helpers/esm/asyncIterator.js
function _asyncIterator(r) {
	var n, t, o, e = 2;
	for ("undefined" != typeof Symbol && (t = Symbol.asyncIterator, o = Symbol.iterator); e--;) {
		if (t && null != (n = r[t])) return n.call(r);
		if (o && null != (n = r[o])) return new AsyncFromSyncIterator(n.call(r));
		t = "@@asyncIterator", o = "@@iterator";
	}
	throw new TypeError("Object is not async iterable");
}
function AsyncFromSyncIterator(r) {
	function AsyncFromSyncIteratorContinuation(r) {
		if (Object(r) !== r) return Promise.reject(new TypeError(r + " is not an object."));
		var n = r.done;
		return Promise.resolve(r.value).then(function(r) {
			return {
				value: r,
				done: n
			};
		});
	}
	return AsyncFromSyncIterator = function AsyncFromSyncIterator(r) {
		this.s = r, this.n = r.next;
	}, AsyncFromSyncIterator.prototype = {
		s: null,
		n: null,
		next: function next() {
			return AsyncFromSyncIteratorContinuation(this.n.apply(this.s, arguments));
		},
		"return": function _return(r) {
			var n = this.s["return"];
			return void 0 === n ? Promise.resolve({
				value: r,
				done: !0
			}) : AsyncFromSyncIteratorContinuation(n.apply(this.s, arguments));
		},
		"throw": function _throw(r) {
			var n = this.s["throw"];
			return void 0 === n ? Promise.reject(r) : AsyncFromSyncIteratorContinuation(n.apply(this.s, arguments));
		}
	}, new AsyncFromSyncIterator(r);
}
var init_asyncIterator = __esmMin(() => {
	init__jco_node_builtin_error_globals();
});
// \0@oxc-project+runtime@0.156.0/helpers/esm/asyncGeneratorDelegate.js
function _asyncGeneratorDelegate(t) {
	var e = {}, n = !1;
	function pump(e, r) {
		return n = !0, r = new Promise(function(n) {
			n(t[e](r));
		}), {
			done: !1,
			value: new _OverloadYield(r, 1)
		};
	}
	return e["undefined" != typeof Symbol && Symbol.iterator || "@@iterator"] = function() {
		return this;
	}, e.next = function(t) {
		return n ? (n = !1, t) : pump("next", t);
	}, "function" == typeof t["throw"] && (e["throw"] = function(t) {
		if (n) throw n = !1, t;
		return pump("throw", t);
	}), "function" == typeof t["return"] && (e["return"] = function(t) {
		return n ? (n = !1, t) : pump("return", t);
	}), e;
}
var init_asyncGeneratorDelegate = __esmMin(() => {
	init_OverloadYield();
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/validators.js
var require_validators = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { ArrayIsArray, ArrayPrototypeIncludes, ArrayPrototypeJoin, ArrayPrototypeMap, NumberIsInteger, NumberIsNaN, NumberMAX_SAFE_INTEGER, NumberMIN_SAFE_INTEGER, NumberParseInt, ObjectPrototypeHasOwnProperty, RegExpPrototypeExec, String, StringPrototypeToUpperCase, StringPrototypeTrim } = require_primordials();
	const { hideStackFrames, codes: { ERR_SOCKET_BAD_PORT, ERR_INVALID_ARG_TYPE, ERR_INVALID_ARG_VALUE, ERR_OUT_OF_RANGE, ERR_UNKNOWN_SIGNAL } } = require_errors();
	const { normalizeEncoding } = require_util();
	const { isAsyncFunction, isArrayBufferView } = require_util().types;
	const signals = {};
	/**
	* @param {*} value
	* @returns {boolean}
	*/
	function isInt32(value) {
		return value === (value | 0);
	}
	/**
	* @param {*} value
	* @returns {boolean}
	*/
	function isUint32(value) {
		return value === value >>> 0;
	}
	const octalReg = /^[0-7]+$/;
	const modeDesc = "must be a 32-bit unsigned integer or an octal string";
	/**
	* Parse and validate values that will be converted into mode_t (the S_*
	* constants). Only valid numbers and octal strings are allowed. They could be
	* converted to 32-bit unsigned integers or non-negative signed integers in the
	* C++ land, but any value higher than 0o777 will result in platform-specific
	* behaviors.
	* @param {*} value Values to be validated
	* @param {string} name Name of the argument
	* @param {number} [def] If specified, will be returned for invalid values
	* @returns {number}
	*/
	function parseFileMode(value, name, def) {
		if (typeof value === "undefined") value = def;
		if (typeof value === "string") {
			if (RegExpPrototypeExec(octalReg, value) === null) throw new ERR_INVALID_ARG_VALUE(name, value, modeDesc);
			value = NumberParseInt(value, 8);
		}
		validateUint32(value, name);
		return value;
	}
	/**
	* @callback validateInteger
	* @param {*} value
	* @param {string} name
	* @param {number} [min]
	* @param {number} [max]
	* @returns {asserts value is number}
	*/
	/** @type {validateInteger} */
	const validateInteger = hideStackFrames((value, name, min = NumberMIN_SAFE_INTEGER, max = NumberMAX_SAFE_INTEGER) => {
		if (typeof value !== "number") throw new ERR_INVALID_ARG_TYPE(name, "number", value);
		if (!NumberIsInteger(value)) throw new ERR_OUT_OF_RANGE(name, "an integer", value);
		if (value < min || value > max) throw new ERR_OUT_OF_RANGE(name, `>= ${min} && <= ${max}`, value);
	});
	/**
	* @callback validateInt32
	* @param {*} value
	* @param {string} name
	* @param {number} [min]
	* @param {number} [max]
	* @returns {asserts value is number}
	*/
	/** @type {validateInt32} */
	const validateInt32 = hideStackFrames((value, name, min = -2147483648, max = 2147483647) => {
		if (typeof value !== "number") throw new ERR_INVALID_ARG_TYPE(name, "number", value);
		if (!NumberIsInteger(value)) throw new ERR_OUT_OF_RANGE(name, "an integer", value);
		if (value < min || value > max) throw new ERR_OUT_OF_RANGE(name, `>= ${min} && <= ${max}`, value);
	});
	/**
	* @callback validateUint32
	* @param {*} value
	* @param {string} name
	* @param {number|boolean} [positive=false]
	* @returns {asserts value is number}
	*/
	/** @type {validateUint32} */
	const validateUint32 = hideStackFrames((value, name, positive = false) => {
		if (typeof value !== "number") throw new ERR_INVALID_ARG_TYPE(name, "number", value);
		if (!NumberIsInteger(value)) throw new ERR_OUT_OF_RANGE(name, "an integer", value);
		const min = positive ? 1 : 0;
		const max = 4294967295;
		if (value < min || value > max) throw new ERR_OUT_OF_RANGE(name, `>= ${min} && <= ${max}`, value);
	});
	/**
	* @callback validateString
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is string}
	*/
	/** @type {validateString} */
	function validateString(value, name) {
		if (typeof value !== "string") throw new ERR_INVALID_ARG_TYPE(name, "string", value);
	}
	/**
	* @callback validateNumber
	* @param {*} value
	* @param {string} name
	* @param {number} [min]
	* @param {number} [max]
	* @returns {asserts value is number}
	*/
	/** @type {validateNumber} */
	function validateNumber(value, name, min = void 0, max) {
		if (typeof value !== "number") throw new ERR_INVALID_ARG_TYPE(name, "number", value);
		if (min != null && value < min || max != null && value > max || (min != null || max != null) && NumberIsNaN(value)) throw new ERR_OUT_OF_RANGE(name, `${min != null ? `>= ${min}` : ""}${min != null && max != null ? " && " : ""}${max != null ? `<= ${max}` : ""}`, value);
	}
	/**
	* @callback validateOneOf
	* @template T
	* @param {T} value
	* @param {string} name
	* @param {T[]} oneOf
	*/
	/** @type {validateOneOf} */
	const validateOneOf = hideStackFrames((value, name, oneOf) => {
		if (!ArrayPrototypeIncludes(oneOf, value)) {
			const reason = "must be one of: " + ArrayPrototypeJoin(ArrayPrototypeMap(oneOf, (v) => typeof v === "string" ? `'${v}'` : String(v)), ", ");
			throw new ERR_INVALID_ARG_VALUE(name, value, reason);
		}
	});
	/**
	* @callback validateBoolean
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is boolean}
	*/
	/** @type {validateBoolean} */
	function validateBoolean(value, name) {
		if (typeof value !== "boolean") throw new ERR_INVALID_ARG_TYPE(name, "boolean", value);
	}
	/**
	* @param {any} options
	* @param {string} key
	* @param {boolean} defaultValue
	* @returns {boolean}
	*/
	function getOwnPropertyValueOrDefault(options, key, defaultValue) {
		return options == null || !ObjectPrototypeHasOwnProperty(options, key) ? defaultValue : options[key];
	}
	/**
	* @callback validateObject
	* @param {*} value
	* @param {string} name
	* @param {{
	*   allowArray?: boolean,
	*   allowFunction?: boolean,
	*   nullable?: boolean
	* }} [options]
	*/
	/** @type {validateObject} */
	const validateObject = hideStackFrames((value, name, options = null) => {
		const allowArray = getOwnPropertyValueOrDefault(options, "allowArray", false);
		const allowFunction = getOwnPropertyValueOrDefault(options, "allowFunction", false);
		if (!getOwnPropertyValueOrDefault(options, "nullable", false) && value === null || !allowArray && ArrayIsArray(value) || typeof value !== "object" && (!allowFunction || typeof value !== "function")) throw new ERR_INVALID_ARG_TYPE(name, "Object", value);
	});
	/**
	* @callback validateDictionary - We are using the Web IDL Standard definition
	*                                of "dictionary" here, which means any value
	*                                whose Type is either Undefined, Null, or
	*                                Object (which includes functions).
	* @param {*} value
	* @param {string} name
	* @see https://webidl.spec.whatwg.org/#es-dictionary
	* @see https://tc39.es/ecma262/#table-typeof-operator-results
	*/
	/** @type {validateDictionary} */
	const validateDictionary = hideStackFrames((value, name) => {
		if (value != null && typeof value !== "object" && typeof value !== "function") throw new ERR_INVALID_ARG_TYPE(name, "a dictionary", value);
	});
	/**
	* @callback validateArray
	* @param {*} value
	* @param {string} name
	* @param {number} [minLength]
	* @returns {asserts value is any[]}
	*/
	/** @type {validateArray} */
	const validateArray = hideStackFrames((value, name, minLength = 0) => {
		if (!ArrayIsArray(value)) throw new ERR_INVALID_ARG_TYPE(name, "Array", value);
		if (value.length < minLength) {
			const reason = `must be longer than ${minLength}`;
			throw new ERR_INVALID_ARG_VALUE(name, value, reason);
		}
	});
	/**
	* @callback validateStringArray
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is string[]}
	*/
	/** @type {validateStringArray} */
	function validateStringArray(value, name) {
		validateArray(value, name);
		for (let i = 0; i < value.length; i++) validateString(value[i], `${name}[${i}]`);
	}
	/**
	* @callback validateBooleanArray
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is boolean[]}
	*/
	/** @type {validateBooleanArray} */
	function validateBooleanArray(value, name) {
		validateArray(value, name);
		for (let i = 0; i < value.length; i++) validateBoolean(value[i], `${name}[${i}]`);
	}
	/**
	* @callback validateAbortSignalArray
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is AbortSignal[]}
	*/
	/** @type {validateAbortSignalArray} */
	function validateAbortSignalArray(value, name) {
		validateArray(value, name);
		for (let i = 0; i < value.length; i++) {
			const signal = value[i];
			const indexedName = `${name}[${i}]`;
			if (signal == null) throw new ERR_INVALID_ARG_TYPE(indexedName, "AbortSignal", signal);
			validateAbortSignal(signal, indexedName);
		}
	}
	/**
	* @param {*} signal
	* @param {string} [name='signal']
	* @returns {asserts signal is keyof signals}
	*/
	function validateSignalName(signal, name = "signal") {
		validateString(signal, name);
		if (signals[signal] === void 0) {
			if (signals[StringPrototypeToUpperCase(signal)] !== void 0) throw new ERR_UNKNOWN_SIGNAL(signal + " (signals must use all capital letters)");
			throw new ERR_UNKNOWN_SIGNAL(signal);
		}
	}
	/**
	* @callback validateBuffer
	* @param {*} buffer
	* @param {string} [name='buffer']
	* @returns {asserts buffer is ArrayBufferView}
	*/
	/** @type {validateBuffer} */
	const validateBuffer = hideStackFrames((buffer, name = "buffer") => {
		if (!isArrayBufferView(buffer)) throw new ERR_INVALID_ARG_TYPE(name, [
			"Buffer",
			"TypedArray",
			"DataView"
		], buffer);
	});
	/**
	* @param {string} data
	* @param {string} encoding
	*/
	function validateEncoding(data, encoding) {
		const normalizedEncoding = normalizeEncoding(encoding);
		const length = data.length;
		if (normalizedEncoding === "hex" && length % 2 !== 0) throw new ERR_INVALID_ARG_VALUE("encoding", encoding, `is invalid for data of length ${length}`);
	}
	/**
	* Check that the port number is not NaN when coerced to a number,
	* is an integer and that it falls within the legal range of port numbers.
	* @param {*} port
	* @param {string} [name='Port']
	* @param {boolean} [allowZero=true]
	* @returns {number}
	*/
	function validatePort(port, name = "Port", allowZero = true) {
		if (typeof port !== "number" && typeof port !== "string" || typeof port === "string" && StringPrototypeTrim(port).length === 0 || +port !== +port >>> 0 || port > 65535 || port === 0 && !allowZero) throw new ERR_SOCKET_BAD_PORT(name, port, allowZero);
		return port | 0;
	}
	/**
	* @callback validateAbortSignal
	* @param {*} signal
	* @param {string} name
	*/
	/** @type {validateAbortSignal} */
	const validateAbortSignal = hideStackFrames((signal, name) => {
		if (signal !== void 0 && (signal === null || typeof signal !== "object" || !("aborted" in signal))) throw new ERR_INVALID_ARG_TYPE(name, "AbortSignal", signal);
	});
	/**
	* @callback validateFunction
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is Function}
	*/
	/** @type {validateFunction} */
	const validateFunction = hideStackFrames((value, name) => {
		if (typeof value !== "function") throw new ERR_INVALID_ARG_TYPE(name, "Function", value);
	});
	/**
	* @callback validatePlainFunction
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is Function}
	*/
	/** @type {validatePlainFunction} */
	const validatePlainFunction = hideStackFrames((value, name) => {
		if (typeof value !== "function" || isAsyncFunction(value)) throw new ERR_INVALID_ARG_TYPE(name, "Function", value);
	});
	/**
	* @callback validateUndefined
	* @param {*} value
	* @param {string} name
	* @returns {asserts value is undefined}
	*/
	/** @type {validateUndefined} */
	const validateUndefined = hideStackFrames((value, name) => {
		if (value !== void 0) throw new ERR_INVALID_ARG_TYPE(name, "undefined", value);
	});
	/**
	* @template T
	* @param {T} value
	* @param {string} name
	* @param {T[]} union
	*/
	function validateUnion(value, name, union) {
		if (!ArrayPrototypeIncludes(union, value)) throw new ERR_INVALID_ARG_TYPE(name, `('${ArrayPrototypeJoin(union, "|")}')`, value);
	}
	const linkValueRegExp = /^(?:<[^>]*>)(?:\s*;\s*[^;"\s]+(?:=(")?[^;"\s]*\1)?)*$/;
	/**
	* @param {any} value
	* @param {string} name
	*/
	function validateLinkHeaderFormat(value, name) {
		if (typeof value === "undefined" || !RegExpPrototypeExec(linkValueRegExp, value)) throw new ERR_INVALID_ARG_VALUE(name, value, "must be an array or string of format \"</styles.css>; rel=preload; as=style\"");
	}
	/**
	* @param {any} hints
	* @return {string}
	*/
	function validateLinkHeaderValue(hints) {
		if (typeof hints === "string") {
			validateLinkHeaderFormat(hints, "hints");
			return hints;
		} else if (ArrayIsArray(hints)) {
			const hintsLength = hints.length;
			let result = "";
			if (hintsLength === 0) return result;
			for (let i = 0; i < hintsLength; i++) {
				const link = hints[i];
				validateLinkHeaderFormat(link, "hints");
				result += link;
				if (i !== hintsLength - 1) result += ", ";
			}
			return result;
		}
		throw new ERR_INVALID_ARG_VALUE("hints", hints, "must be an array or string of format \"</styles.css>; rel=preload; as=style\"");
	}
	module.exports = {
		isInt32,
		isUint32,
		parseFileMode,
		validateArray,
		validateStringArray,
		validateBooleanArray,
		validateAbortSignalArray,
		validateBoolean,
		validateBuffer,
		validateDictionary,
		validateEncoding,
		validateFunction,
		validateInt32,
		validateInteger,
		validateNumber,
		validateObject,
		validateOneOf,
		validatePlainFunction,
		validatePort,
		validateSignalName,
		validateString,
		validateUint32,
		validateUndefined,
		validateUnion,
		validateAbortSignal,
		validateLinkHeaderValue
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/scheduler.js
var scheduler_exports = /* @__PURE__ */ __exportAll({
	default: () => scheduler,
	nextTick: () => nextTick
});
function flush() {
	try {
		while (queue.length) queue.shift()();
	} finally {
		scheduled = false;
		if (queue.length) schedule();
	}
}
function schedule() {
	if (scheduled) return;
	scheduled = true;
	queueMicrotask(flush);
}
function nextTick(callback, ...args) {
	queue.push(() => callback(...args));
	schedule();
}
var queue, scheduled, scheduler;
var init_scheduler = __esmMin(() => {
	init__jco_node_builtin_microtask_globals();
	queue = [];
	scheduled = false;
	scheduler = {
		nextTick,
		stdout: void 0,
		stderr: void 0
	};
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/utils.js
var require_utils = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { SymbolAsyncIterator, SymbolIterator, SymbolFor } = require_primordials();
	const kIsDestroyed = SymbolFor("nodejs.stream.destroyed");
	const kIsErrored = SymbolFor("nodejs.stream.errored");
	const kIsReadable = SymbolFor("nodejs.stream.readable");
	const kIsWritable = SymbolFor("nodejs.stream.writable");
	const kIsDisturbed = SymbolFor("nodejs.stream.disturbed");
	const kIsClosedPromise = SymbolFor("nodejs.webstream.isClosedPromise");
	const kControllerErrorFunction = SymbolFor("nodejs.webstream.controllerErrorFunction");
	function isReadableNodeStream(obj, strict = false) {
		var _obj$_readableState;
		return !!(obj && typeof obj.pipe === "function" && typeof obj.on === "function" && (!strict || typeof obj.pause === "function" && typeof obj.resume === "function") && (!obj._writableState || ((_obj$_readableState = obj._readableState) === null || _obj$_readableState === void 0 ? void 0 : _obj$_readableState.readable) !== false) && (!obj._writableState || obj._readableState));
	}
	function isWritableNodeStream(obj) {
		var _obj$_writableState;
		return !!(obj && typeof obj.write === "function" && typeof obj.on === "function" && (!obj._readableState || ((_obj$_writableState = obj._writableState) === null || _obj$_writableState === void 0 ? void 0 : _obj$_writableState.writable) !== false));
	}
	function isDuplexNodeStream(obj) {
		return !!(obj && typeof obj.pipe === "function" && obj._readableState && typeof obj.on === "function" && typeof obj.write === "function");
	}
	function isNodeStream(obj) {
		return obj && (obj._readableState || obj._writableState || typeof obj.write === "function" && typeof obj.on === "function" || typeof obj.pipe === "function" && typeof obj.on === "function");
	}
	function isReadableStream(obj) {
		return !!(obj && !isNodeStream(obj) && typeof obj.pipeThrough === "function" && typeof obj.getReader === "function" && typeof obj.cancel === "function");
	}
	function isWritableStream(obj) {
		return !!(obj && !isNodeStream(obj) && typeof obj.getWriter === "function" && typeof obj.abort === "function");
	}
	function isTransformStream(obj) {
		return !!(obj && !isNodeStream(obj) && typeof obj.readable === "object" && typeof obj.writable === "object");
	}
	function isWebStream(obj) {
		return isReadableStream(obj) || isWritableStream(obj) || isTransformStream(obj);
	}
	function isIterable(obj, isAsync) {
		if (obj == null) return false;
		if (isAsync === true) return typeof obj[SymbolAsyncIterator] === "function";
		if (isAsync === false) return typeof obj[SymbolIterator] === "function";
		return typeof obj[SymbolAsyncIterator] === "function" || typeof obj[SymbolIterator] === "function";
	}
	function isDestroyed(stream) {
		if (!isNodeStream(stream)) return null;
		const wState = stream._writableState;
		const rState = stream._readableState;
		const state = wState || rState;
		return !!(stream.destroyed || stream[kIsDestroyed] || state !== null && state !== void 0 && state.destroyed);
	}
	function isWritableEnded(stream) {
		if (!isWritableNodeStream(stream)) return null;
		if (stream.writableEnded === true) return true;
		const wState = stream._writableState;
		if (wState !== null && wState !== void 0 && wState.errored) return false;
		if (typeof (wState === null || wState === void 0 ? void 0 : wState.ended) !== "boolean") return null;
		return wState.ended;
	}
	function isWritableFinished(stream, strict) {
		if (!isWritableNodeStream(stream)) return null;
		if (stream.writableFinished === true) return true;
		const wState = stream._writableState;
		if (wState !== null && wState !== void 0 && wState.errored) return false;
		if (typeof (wState === null || wState === void 0 ? void 0 : wState.finished) !== "boolean") return null;
		return !!(wState.finished || strict === false && wState.ended === true && wState.length === 0);
	}
	function isReadableEnded(stream) {
		if (!isReadableNodeStream(stream)) return null;
		if (stream.readableEnded === true) return true;
		const rState = stream._readableState;
		if (!rState || rState.errored) return false;
		if (typeof (rState === null || rState === void 0 ? void 0 : rState.ended) !== "boolean") return null;
		return rState.ended;
	}
	function isReadableFinished(stream, strict) {
		if (!isReadableNodeStream(stream)) return null;
		const rState = stream._readableState;
		if (rState !== null && rState !== void 0 && rState.errored) return false;
		if (typeof (rState === null || rState === void 0 ? void 0 : rState.endEmitted) !== "boolean") return null;
		return !!(rState.endEmitted || strict === false && rState.ended === true && rState.length === 0);
	}
	function isReadable(stream) {
		if (stream && stream[kIsReadable] != null) return stream[kIsReadable];
		if (typeof (stream === null || stream === void 0 ? void 0 : stream.readable) !== "boolean") return null;
		if (isDestroyed(stream)) return false;
		return isReadableNodeStream(stream) && stream.readable && !isReadableFinished(stream);
	}
	function isWritable(stream) {
		if (stream && stream[kIsWritable] != null) return stream[kIsWritable];
		if (typeof (stream === null || stream === void 0 ? void 0 : stream.writable) !== "boolean") return null;
		if (isDestroyed(stream)) return false;
		return isWritableNodeStream(stream) && stream.writable && !isWritableEnded(stream);
	}
	function isFinished(stream, opts) {
		if (!isNodeStream(stream)) return null;
		if (isDestroyed(stream)) return true;
		if ((opts === null || opts === void 0 ? void 0 : opts.readable) !== false && isReadable(stream)) return false;
		if ((opts === null || opts === void 0 ? void 0 : opts.writable) !== false && isWritable(stream)) return false;
		return true;
	}
	function isWritableErrored(stream) {
		var _stream$_writableStat, _stream$_writableStat2;
		if (!isNodeStream(stream)) return null;
		if (stream.writableErrored) return stream.writableErrored;
		return (_stream$_writableStat = (_stream$_writableStat2 = stream._writableState) === null || _stream$_writableStat2 === void 0 ? void 0 : _stream$_writableStat2.errored) !== null && _stream$_writableStat !== void 0 ? _stream$_writableStat : null;
	}
	function isReadableErrored(stream) {
		var _stream$_readableStat, _stream$_readableStat2;
		if (!isNodeStream(stream)) return null;
		if (stream.readableErrored) return stream.readableErrored;
		return (_stream$_readableStat = (_stream$_readableStat2 = stream._readableState) === null || _stream$_readableStat2 === void 0 ? void 0 : _stream$_readableStat2.errored) !== null && _stream$_readableStat !== void 0 ? _stream$_readableStat : null;
	}
	function isClosed(stream) {
		if (!isNodeStream(stream)) return null;
		if (typeof stream.closed === "boolean") return stream.closed;
		const wState = stream._writableState;
		const rState = stream._readableState;
		if (typeof (wState === null || wState === void 0 ? void 0 : wState.closed) === "boolean" || typeof (rState === null || rState === void 0 ? void 0 : rState.closed) === "boolean") return (wState === null || wState === void 0 ? void 0 : wState.closed) || (rState === null || rState === void 0 ? void 0 : rState.closed);
		if (typeof stream._closed === "boolean" && isOutgoingMessage(stream)) return stream._closed;
		return null;
	}
	function isOutgoingMessage(stream) {
		return typeof stream._closed === "boolean" && typeof stream._defaultKeepAlive === "boolean" && typeof stream._removedConnection === "boolean" && typeof stream._removedContLen === "boolean";
	}
	function isServerResponse(stream) {
		return typeof stream._sent100 === "boolean" && isOutgoingMessage(stream);
	}
	function isServerRequest(stream) {
		var _stream$req;
		return typeof stream._consuming === "boolean" && typeof stream._dumped === "boolean" && ((_stream$req = stream.req) === null || _stream$req === void 0 ? void 0 : _stream$req.upgradeOrConnect) === void 0;
	}
	function willEmitClose(stream) {
		if (!isNodeStream(stream)) return null;
		const wState = stream._writableState;
		const rState = stream._readableState;
		const state = wState || rState;
		return !state && isServerResponse(stream) || !!(state && state.autoDestroy && state.emitClose && state.closed === false);
	}
	function isDisturbed(stream) {
		var _stream$kIsDisturbed;
		return !!(stream && ((_stream$kIsDisturbed = stream[kIsDisturbed]) !== null && _stream$kIsDisturbed !== void 0 ? _stream$kIsDisturbed : stream.readableDidRead || stream.readableAborted));
	}
	function isErrored(stream) {
		var _ref, _ref2, _ref3, _ref4, _ref5, _stream$kIsErrored, _stream$_readableStat3, _stream$_writableStat3, _stream$_readableStat4, _stream$_writableStat4;
		return !!(stream && ((_ref = (_ref2 = (_ref3 = (_ref4 = (_ref5 = (_stream$kIsErrored = stream[kIsErrored]) !== null && _stream$kIsErrored !== void 0 ? _stream$kIsErrored : stream.readableErrored) !== null && _ref5 !== void 0 ? _ref5 : stream.writableErrored) !== null && _ref4 !== void 0 ? _ref4 : (_stream$_readableStat3 = stream._readableState) === null || _stream$_readableStat3 === void 0 ? void 0 : _stream$_readableStat3.errorEmitted) !== null && _ref3 !== void 0 ? _ref3 : (_stream$_writableStat3 = stream._writableState) === null || _stream$_writableStat3 === void 0 ? void 0 : _stream$_writableStat3.errorEmitted) !== null && _ref2 !== void 0 ? _ref2 : (_stream$_readableStat4 = stream._readableState) === null || _stream$_readableStat4 === void 0 ? void 0 : _stream$_readableStat4.errored) !== null && _ref !== void 0 ? _ref : (_stream$_writableStat4 = stream._writableState) === null || _stream$_writableStat4 === void 0 ? void 0 : _stream$_writableStat4.errored));
	}
	module.exports = {
		isDestroyed,
		kIsDestroyed,
		isDisturbed,
		kIsDisturbed,
		isErrored,
		kIsErrored,
		isReadable,
		kIsReadable,
		kIsClosedPromise,
		kControllerErrorFunction,
		kIsWritable,
		isClosed,
		isDuplexNodeStream,
		isFinished,
		isIterable,
		isReadableNodeStream,
		isReadableStream,
		isReadableEnded,
		isReadableFinished,
		isReadableErrored,
		isNodeStream,
		isWebStream,
		isWritable,
		isWritableNodeStream,
		isWritableStream,
		isWritableEnded,
		isWritableFinished,
		isWritableErrored,
		isServerRequest,
		isServerResponse,
		willEmitClose,
		isTransformStream
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/end-of-stream.js
var require_end_of_stream = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { AbortError, codes } = require_errors();
	const { ERR_INVALID_ARG_TYPE, ERR_STREAM_PREMATURE_CLOSE } = codes;
	const { kEmptyObject, once } = require_util();
	const { validateAbortSignal, validateFunction, validateObject, validateBoolean } = require_validators();
	const { Promise, PromisePrototypeThen, SymbolDispose } = require_primordials();
	const { isClosed, isReadable, isReadableNodeStream, isReadableStream, isReadableFinished, isReadableErrored, isWritable, isWritableNodeStream, isWritableStream, isWritableFinished, isWritableErrored, isNodeStream, willEmitClose: _willEmitClose, kIsClosedPromise } = require_utils();
	let addAbortListener;
	function isRequest(stream) {
		return stream.setHeader && typeof stream.abort === "function";
	}
	const nop = () => {};
	function eos(stream, options, callback) {
		var _options$readable, _options$writable;
		if (arguments.length === 2) {
			callback = options;
			options = kEmptyObject;
		} else if (options == null) options = kEmptyObject;
		else validateObject(options, "options");
		validateFunction(callback, "callback");
		validateAbortSignal(options.signal, "options.signal");
		callback = once(callback);
		if (isReadableStream(stream) || isWritableStream(stream)) return eosWeb(stream, options, callback);
		if (!isNodeStream(stream)) throw new ERR_INVALID_ARG_TYPE("stream", [
			"ReadableStream",
			"WritableStream",
			"Stream"
		], stream);
		const readable = (_options$readable = options.readable) !== null && _options$readable !== void 0 ? _options$readable : isReadableNodeStream(stream);
		const writable = (_options$writable = options.writable) !== null && _options$writable !== void 0 ? _options$writable : isWritableNodeStream(stream);
		const wState = stream._writableState;
		const rState = stream._readableState;
		const onlegacyfinish = () => {
			if (!stream.writable) onfinish();
		};
		let willEmitClose = _willEmitClose(stream) && isReadableNodeStream(stream) === readable && isWritableNodeStream(stream) === writable;
		let writableFinished = isWritableFinished(stream, false);
		const onfinish = () => {
			writableFinished = true;
			if (stream.destroyed) willEmitClose = false;
			if (willEmitClose && (!stream.readable || readable)) return;
			if (!readable || readableFinished) callback.call(stream);
		};
		let readableFinished = isReadableFinished(stream, false);
		const onend = () => {
			readableFinished = true;
			if (stream.destroyed) willEmitClose = false;
			if (willEmitClose && (!stream.writable || writable)) return;
			if (!writable || writableFinished) callback.call(stream);
		};
		const onerror = (err) => {
			callback.call(stream, err);
		};
		let closed = isClosed(stream);
		const onclose = () => {
			closed = true;
			const errored = isWritableErrored(stream) || isReadableErrored(stream);
			if (errored && typeof errored !== "boolean") return callback.call(stream, errored);
			if (readable && !readableFinished && isReadableNodeStream(stream, true)) {
				if (!isReadableFinished(stream, false)) return callback.call(stream, new ERR_STREAM_PREMATURE_CLOSE());
			}
			if (writable && !writableFinished) {
				if (!isWritableFinished(stream, false)) return callback.call(stream, new ERR_STREAM_PREMATURE_CLOSE());
			}
			callback.call(stream);
		};
		const onclosed = () => {
			closed = true;
			const errored = isWritableErrored(stream) || isReadableErrored(stream);
			if (errored && typeof errored !== "boolean") return callback.call(stream, errored);
			callback.call(stream);
		};
		const onrequest = () => {
			stream.req.on("finish", onfinish);
		};
		if (isRequest(stream)) {
			stream.on("complete", onfinish);
			if (!willEmitClose) stream.on("abort", onclose);
			if (stream.req) onrequest();
			else stream.on("request", onrequest);
		} else if (writable && !wState) {
			stream.on("end", onlegacyfinish);
			stream.on("close", onlegacyfinish);
		}
		if (!willEmitClose && typeof stream.aborted === "boolean") stream.on("aborted", onclose);
		stream.on("end", onend);
		stream.on("finish", onfinish);
		if (options.error !== false) stream.on("error", onerror);
		stream.on("close", onclose);
		if (closed) process.nextTick(onclose);
		else if (wState !== null && wState !== void 0 && wState.errorEmitted || rState !== null && rState !== void 0 && rState.errorEmitted) {
			if (!willEmitClose) process.nextTick(onclosed);
		} else if (!readable && (!willEmitClose || isReadable(stream)) && (writableFinished || isWritable(stream) === false)) process.nextTick(onclosed);
		else if (!writable && (!willEmitClose || isWritable(stream)) && (readableFinished || isReadable(stream) === false)) process.nextTick(onclosed);
		else if (rState && stream.req && stream.aborted) process.nextTick(onclosed);
		const cleanup = () => {
			callback = nop;
			stream.removeListener("aborted", onclose);
			stream.removeListener("complete", onfinish);
			stream.removeListener("abort", onclose);
			stream.removeListener("request", onrequest);
			if (stream.req) stream.req.removeListener("finish", onfinish);
			stream.removeListener("end", onlegacyfinish);
			stream.removeListener("close", onlegacyfinish);
			stream.removeListener("finish", onfinish);
			stream.removeListener("end", onend);
			stream.removeListener("error", onerror);
			stream.removeListener("close", onclose);
		};
		if (options.signal && !closed) {
			const abort = () => {
				const endCallback = callback;
				cleanup();
				endCallback.call(stream, new AbortError(void 0, { cause: options.signal.reason }));
			};
			if (options.signal.aborted) process.nextTick(abort);
			else {
				addAbortListener = addAbortListener || require_util().addAbortListener;
				const disposable = addAbortListener(options.signal, abort);
				const originalCallback = callback;
				callback = once((...args) => {
					disposable[SymbolDispose]();
					originalCallback.apply(stream, args);
				});
			}
		}
		return cleanup;
	}
	function eosWeb(stream, options, callback) {
		let isAborted = false;
		let abort = nop;
		if (options.signal) {
			abort = () => {
				isAborted = true;
				callback.call(stream, new AbortError(void 0, { cause: options.signal.reason }));
			};
			if (options.signal.aborted) process.nextTick(abort);
			else {
				addAbortListener = addAbortListener || require_util().addAbortListener;
				const disposable = addAbortListener(options.signal, abort);
				const originalCallback = callback;
				callback = once((...args) => {
					disposable[SymbolDispose]();
					originalCallback.apply(stream, args);
				});
			}
		}
		const resolverFn = (...args) => {
			if (!isAborted) process.nextTick(() => callback.apply(stream, args));
		};
		PromisePrototypeThen(stream[kIsClosedPromise].promise, resolverFn, resolverFn);
		return nop;
	}
	function finished(stream, opts) {
		var _opts;
		let autoCleanup = false;
		if (opts === null) opts = kEmptyObject;
		if ((_opts = opts) !== null && _opts !== void 0 && _opts.cleanup) {
			validateBoolean(opts.cleanup, "cleanup");
			autoCleanup = opts.cleanup;
		}
		return new Promise((resolve, reject) => {
			const cleanup = eos(stream, opts, (err) => {
				if (autoCleanup) cleanup();
				if (err) reject(err);
				else resolve();
			});
		});
	}
	module.exports = eos;
	module.exports.finished = finished;
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/destroy.js
var require_destroy = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { aggregateTwoErrors, codes: { ERR_MULTIPLE_CALLBACK }, AbortError } = require_errors();
	const { Symbol } = require_primordials();
	const { kIsDestroyed, isDestroyed, isFinished, isServerRequest } = require_utils();
	const kDestroy = Symbol("kDestroy");
	const kConstruct = Symbol("kConstruct");
	function checkError(err, w, r) {
		if (err) {
			err.stack;
			if (w && !w.errored) w.errored = err;
			if (r && !r.errored) r.errored = err;
		}
	}
	function destroy(err, cb) {
		const r = this._readableState;
		const w = this._writableState;
		const s = w || r;
		if (w !== null && w !== void 0 && w.destroyed || r !== null && r !== void 0 && r.destroyed) {
			if (typeof cb === "function") cb();
			return this;
		}
		checkError(err, w, r);
		if (w) w.destroyed = true;
		if (r) r.destroyed = true;
		if (!s.constructed) this.once(kDestroy, function(er) {
			_destroy(this, aggregateTwoErrors(er, err), cb);
		});
		else _destroy(this, err, cb);
		return this;
	}
	function _destroy(self, err, cb) {
		let called = false;
		function onDestroy(err) {
			if (called) return;
			called = true;
			const r = self._readableState;
			const w = self._writableState;
			checkError(err, w, r);
			if (w) w.closed = true;
			if (r) r.closed = true;
			if (typeof cb === "function") cb(err);
			if (err) process.nextTick(emitErrorCloseNT, self, err);
			else process.nextTick(emitCloseNT, self);
		}
		try {
			self._destroy(err || null, onDestroy);
		} catch (err) {
			onDestroy(err);
		}
	}
	function emitErrorCloseNT(self, err) {
		emitErrorNT(self, err);
		emitCloseNT(self);
	}
	function emitCloseNT(self) {
		const r = self._readableState;
		const w = self._writableState;
		if (w) w.closeEmitted = true;
		if (r) r.closeEmitted = true;
		if (w !== null && w !== void 0 && w.emitClose || r !== null && r !== void 0 && r.emitClose) self.emit("close");
	}
	function emitErrorNT(self, err) {
		const r = self._readableState;
		const w = self._writableState;
		if (w !== null && w !== void 0 && w.errorEmitted || r !== null && r !== void 0 && r.errorEmitted) return;
		if (w) w.errorEmitted = true;
		if (r) r.errorEmitted = true;
		self.emit("error", err);
	}
	function undestroy() {
		const r = this._readableState;
		const w = this._writableState;
		if (r) {
			r.constructed = true;
			r.closed = false;
			r.closeEmitted = false;
			r.destroyed = false;
			r.errored = null;
			r.errorEmitted = false;
			r.reading = false;
			r.ended = r.readable === false;
			r.endEmitted = r.readable === false;
		}
		if (w) {
			w.constructed = true;
			w.destroyed = false;
			w.closed = false;
			w.closeEmitted = false;
			w.errored = null;
			w.errorEmitted = false;
			w.finalCalled = false;
			w.prefinished = false;
			w.ended = w.writable === false;
			w.ending = w.writable === false;
			w.finished = w.writable === false;
		}
	}
	function errorOrDestroy(stream, err, sync) {
		const r = stream._readableState;
		const w = stream._writableState;
		if (w !== null && w !== void 0 && w.destroyed || r !== null && r !== void 0 && r.destroyed) return this;
		if (r !== null && r !== void 0 && r.autoDestroy || w !== null && w !== void 0 && w.autoDestroy) stream.destroy(err);
		else if (err) {
			err.stack;
			if (w && !w.errored) w.errored = err;
			if (r && !r.errored) r.errored = err;
			if (sync) process.nextTick(emitErrorNT, stream, err);
			else emitErrorNT(stream, err);
		}
	}
	function construct(stream, cb) {
		if (typeof stream._construct !== "function") return;
		const r = stream._readableState;
		const w = stream._writableState;
		if (r) r.constructed = false;
		if (w) w.constructed = false;
		stream.once(kConstruct, cb);
		if (stream.listenerCount(kConstruct) > 1) return;
		process.nextTick(constructNT, stream);
	}
	function constructNT(stream) {
		let called = false;
		function onConstruct(err) {
			if (called) {
				errorOrDestroy(stream, err !== null && err !== void 0 ? err : new ERR_MULTIPLE_CALLBACK());
				return;
			}
			called = true;
			const r = stream._readableState;
			const w = stream._writableState;
			const s = w || r;
			if (r) r.constructed = true;
			if (w) w.constructed = true;
			if (s.destroyed) stream.emit(kDestroy, err);
			else if (err) errorOrDestroy(stream, err, true);
			else process.nextTick(emitConstructNT, stream);
		}
		try {
			stream._construct((err) => {
				process.nextTick(onConstruct, err);
			});
		} catch (err) {
			process.nextTick(onConstruct, err);
		}
	}
	function emitConstructNT(stream) {
		stream.emit(kConstruct);
	}
	function isRequest(stream) {
		return (stream === null || stream === void 0 ? void 0 : stream.setHeader) && typeof stream.abort === "function";
	}
	function emitCloseLegacy(stream) {
		stream.emit("close");
	}
	function emitErrorCloseLegacy(stream, err) {
		stream.emit("error", err);
		process.nextTick(emitCloseLegacy, stream);
	}
	function destroyer(stream, err) {
		if (!stream || isDestroyed(stream)) return;
		if (!err && !isFinished(stream)) err = new AbortError();
		if (isServerRequest(stream)) {
			stream.socket = null;
			stream.destroy(err);
		} else if (isRequest(stream)) stream.abort();
		else if (isRequest(stream.req)) stream.req.abort();
		else if (typeof stream.destroy === "function") stream.destroy(err);
		else if (typeof stream.close === "function") stream.close();
		else if (err) process.nextTick(emitErrorCloseLegacy, stream, err);
		else process.nextTick(emitCloseLegacy, stream);
		if (!stream.destroyed) stream[kIsDestroyed] = true;
	}
	module.exports = {
		construct,
		destroyer,
		destroy,
		undestroy,
		errorOrDestroy
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/legacy.js
var require_legacy = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { ArrayIsArray, ObjectSetPrototypeOf } = require_primordials();
	const { EventEmitter: EE } = (init__jco_node_builtin_stream_events(), __toCommonJS(_jco_node_builtin_stream_events_exports));
	function Stream(opts) {
		EE.call(this, opts);
	}
	ObjectSetPrototypeOf(Stream.prototype, EE.prototype);
	ObjectSetPrototypeOf(Stream, EE);
	Stream.prototype.pipe = function(dest, options) {
		const source = this;
		function ondata(chunk) {
			if (dest.writable && dest.write(chunk) === false && source.pause) source.pause();
		}
		source.on("data", ondata);
		function ondrain() {
			if (source.readable && source.resume) source.resume();
		}
		dest.on("drain", ondrain);
		if (!dest._isStdio && (!options || options.end !== false)) {
			source.on("end", onend);
			source.on("close", onclose);
		}
		let didOnEnd = false;
		function onend() {
			if (didOnEnd) return;
			didOnEnd = true;
			dest.end();
		}
		function onclose() {
			if (didOnEnd) return;
			didOnEnd = true;
			if (typeof dest.destroy === "function") dest.destroy();
		}
		function onerror(er) {
			cleanup();
			if (EE.listenerCount(this, "error") === 0) this.emit("error", er);
		}
		prependListener(source, "error", onerror);
		prependListener(dest, "error", onerror);
		function cleanup() {
			source.removeListener("data", ondata);
			dest.removeListener("drain", ondrain);
			source.removeListener("end", onend);
			source.removeListener("close", onclose);
			source.removeListener("error", onerror);
			dest.removeListener("error", onerror);
			source.removeListener("end", cleanup);
			source.removeListener("close", cleanup);
			dest.removeListener("close", cleanup);
		}
		source.on("end", cleanup);
		source.on("close", cleanup);
		dest.on("close", cleanup);
		dest.emit("pipe", source);
		return dest;
	};
	function prependListener(emitter, event, fn) {
		if (typeof emitter.prependListener === "function") return emitter.prependListener(event, fn);
		if (!emitter._events || !emitter._events[event]) emitter.on(event, fn);
		else if (ArrayIsArray(emitter._events[event])) emitter._events[event].unshift(fn);
		else emitter._events[event] = [fn, emitter._events[event]];
	}
	module.exports = {
		Stream,
		prependListener
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/add-abort-signal.js
var require_add_abort_signal = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { SymbolDispose } = require_primordials();
	const { AbortError, codes } = require_errors();
	const { isNodeStream, isWebStream, kControllerErrorFunction } = require_utils();
	const eos = require_end_of_stream();
	const { ERR_INVALID_ARG_TYPE } = codes;
	let addAbortListener;
	const validateAbortSignal = (signal, name) => {
		if (typeof signal !== "object" || !("aborted" in signal)) throw new ERR_INVALID_ARG_TYPE(name, "AbortSignal", signal);
	};
	module.exports.addAbortSignal = function addAbortSignal(signal, stream) {
		validateAbortSignal(signal, "signal");
		if (!isNodeStream(stream) && !isWebStream(stream)) throw new ERR_INVALID_ARG_TYPE("stream", [
			"ReadableStream",
			"WritableStream",
			"Stream"
		], stream);
		return module.exports.addAbortSignalNoValidate(signal, stream);
	};
	module.exports.addAbortSignalNoValidate = function(signal, stream) {
		if (typeof signal !== "object" || !("aborted" in signal)) return stream;
		const onAbort = isNodeStream(stream) ? () => {
			stream.destroy(new AbortError(void 0, { cause: signal.reason }));
		} : () => {
			stream[kControllerErrorFunction](new AbortError(void 0, { cause: signal.reason }));
		};
		if (signal.aborted) onAbort();
		else {
			addAbortListener = addAbortListener || require_util().addAbortListener;
			const disposable = addAbortListener(signal, onAbort);
			eos(stream, disposable[SymbolDispose]);
		}
		return stream;
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/buffer_list.js
var require_buffer_list = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_objectSpread2();
	const { StringPrototypeSlice, SymbolIterator, TypedArrayPrototypeSet, Uint8Array } = require_primordials();
	const { Buffer } = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { inspect } = require_util();
	module.exports = class BufferList {
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
		unshift(v) {
			const entry = {
				data: v,
				next: this.head
			};
			if (this.length === 0) this.tail = entry;
			this.head = entry;
			++this.length;
		}
		shift() {
			if (this.length === 0) return;
			const ret = this.head.data;
			if (this.length === 1) this.head = this.tail = null;
			else this.head = this.head.next;
			--this.length;
			return ret;
		}
		clear() {
			this.head = this.tail = null;
			this.length = 0;
		}
		join(s) {
			if (this.length === 0) return "";
			let p = this.head;
			let ret = "" + p.data;
			while ((p = p.next) !== null) ret += s + p.data;
			return ret;
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
		consume(n, hasStrings) {
			const data = this.head.data;
			if (n < data.length) {
				const slice = data.slice(0, n);
				this.head.data = data.slice(n);
				return slice;
			}
			if (n === data.length) return this.shift();
			return hasStrings ? this._getString(n) : this._getBuffer(n);
		}
		first() {
			return this.head.data;
		}
		*[SymbolIterator]() {
			for (let p = this.head; p; p = p.next) yield p.data;
		}
		_getString(n) {
			let ret = "";
			let p = this.head;
			let c = 0;
			do {
				const str = p.data;
				if (n > str.length) {
					ret += str;
					n -= str.length;
				} else {
					if (n === str.length) {
						ret += str;
						++c;
						if (p.next) this.head = p.next;
						else this.head = this.tail = null;
					} else {
						ret += StringPrototypeSlice(str, 0, n);
						this.head = p;
						p.data = StringPrototypeSlice(str, n);
					}
					break;
				}
				++c;
			} while ((p = p.next) !== null);
			this.length -= c;
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
		[Symbol.for("nodejs.util.inspect.custom")](_, options) {
			return inspect(this, _objectSpread2(_objectSpread2({}, options), {}, {
				depth: 0,
				customInspect: false
			}));
		}
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/state.js
var require_state = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { MathFloor, NumberIsInteger } = require_primordials();
	const { validateInteger } = require_validators();
	const { ERR_INVALID_ARG_VALUE } = require_errors().codes;
	let defaultHighWaterMarkBytes = 16384;
	let defaultHighWaterMarkObjectMode = 16;
	function highWaterMarkFrom(options, isDuplex, duplexKey) {
		return options.highWaterMark != null ? options.highWaterMark : isDuplex ? options[duplexKey] : null;
	}
	function getDefaultHighWaterMark(objectMode) {
		return objectMode ? defaultHighWaterMarkObjectMode : defaultHighWaterMarkBytes;
	}
	function setDefaultHighWaterMark(objectMode, value) {
		validateInteger(value, "value", 0);
		if (objectMode) defaultHighWaterMarkObjectMode = value;
		else defaultHighWaterMarkBytes = value;
	}
	function getHighWaterMark(state, options, duplexKey, isDuplex) {
		const hwm = highWaterMarkFrom(options, isDuplex, duplexKey);
		if (hwm != null) {
			if (!NumberIsInteger(hwm) || hwm < 0) {
				const name = isDuplex ? `options.${duplexKey}` : "options.highWaterMark";
				throw new ERR_INVALID_ARG_VALUE(name, hwm);
			}
			return MathFloor(hwm);
		}
		return getDefaultHighWaterMark(state.objectMode);
	}
	module.exports = {
		getHighWaterMark,
		getDefaultHighWaterMark,
		setDefaultHighWaterMark
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/string-decoder.js
function lower(value) {
	return String.prototype.toLowerCase.call(value);
}
function normalizeEncoding(encoding) {
	if (encoding == null || encoding === "utf8" || encoding === "utf-8") return "utf8";
	switch (encoding.length) {
		case 4:
			if (encoding === "UTF8") return "utf8";
			if (encoding === "ucs2" || encoding === "UCS2") return "utf16le";
			if (lower(encoding) === "utf8") return "utf8";
			if (lower(encoding) === "ucs2") return "utf16le";
			break;
		case 3:
			if (encoding === "hex" || encoding === "HEX" || lower(encoding) === "hex") return "hex";
			break;
		case 5:
			if (encoding === "ascii" || encoding === "ASCII") return "ascii";
			if (encoding === "ucs-2" || encoding === "UCS-2") return "utf16le";
			if (encoding === "UTF-8") return "utf8";
			if (lower(encoding) === "utf-8") return "utf8";
			if (lower(encoding) === "ascii") return "ascii";
			if (lower(encoding) === "ucs-2") return "utf16le";
			break;
		case 6:
			if (encoding === "base64" || encoding === "BASE64") return "base64";
			if (encoding === "latin1" || encoding === "LATIN1") return "latin1";
			if (encoding === "binary" || encoding === "BINARY") return "latin1";
			if (lower(encoding) === "base64") return "base64";
			if (lower(encoding) === "latin1" || lower(encoding) === "binary") return "latin1";
			break;
		case 7:
			if (encoding === "utf16le" || encoding === "UTF16LE" || lower(encoding) === "utf16le") return "utf16le";
			break;
		case 8:
			if (encoding === "utf-16le" || encoding === "UTF-16LE" || lower(encoding) === "utf-16le") return "utf16le";
			break;
		case 9:
			if (encoding === "base64url" || encoding === "BASE64URL" || lower(encoding) === "base64url") return "base64url";
			break;
		default: if (encoding === "") return "utf8";
	}
}
function unknownEncoding(encoding) {
	return codedError(new TypeError(`Unknown encoding: ${String(encoding)}`), "ERR_UNKNOWN_ENCODING");
}
function inputBytes(input) {
	return Buffer$1.from(new Uint8Array(input.buffer, input.byteOffset, input.byteLength));
}
function encodeBytes(input, encoding, start = 0, end = input.length) {
	if (encoding === "base64url") return input.toString("base64", start, end).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
	return input.toString(encoding, start, end);
}
function utf8CheckByte(byte) {
	if (byte <= 127) return 0;
	if (byte >> 5 === 6) return 2;
	if (byte >> 4 === 14) return 3;
	if (byte >> 3 === 30) return 4;
	return byte >> 6 === 2 ? -1 : -2;
}
function utf8CheckIncomplete(state, input, start) {
	let index = input.length - 1;
	if (index < start) return 0;
	let bytes = utf8CheckByte(input[index]);
	if (bytes >= 0) {
		if (bytes > 0) state.lastNeed = bytes - 1;
		return bytes;
	}
	if (--index < start || bytes === -2) return 0;
	bytes = utf8CheckByte(input[index]);
	if (bytes >= 0) {
		if (bytes > 0) state.lastNeed = bytes - 2;
		return bytes;
	}
	if (--index < start || bytes === -2) return 0;
	bytes = utf8CheckByte(input[index]);
	if (bytes >= 0) {
		if (bytes > 0) {
			if (bytes === 2) bytes = 0;
			else state.lastNeed = bytes - 3;
		}
		return bytes;
	}
	return 0;
}
function fillLast(state, input, encoding) {
	if (state.lastNeed <= input.length) {
		input.copy(state.lastChar, state.lastTotal - state.lastNeed, 0, state.lastNeed);
		return encodeBytes(state.lastChar, encoding, 0, state.lastTotal);
	}
	input.copy(state.lastChar, state.lastTotal - state.lastNeed, 0, input.length);
	state.lastNeed -= input.length;
}
function utf8Text(state, input, start) {
	const total = utf8CheckIncomplete(state, input, start);
	if (state.lastNeed === 0) return input.toString("utf8", start);
	state.lastTotal = total;
	const end = input.length - (total - state.lastNeed);
	input.copy(state.lastChar, 0, end);
	return input.toString("utf8", start, end);
}
function utf8Write(state, input) {
	const buffered = state.lastTotal - state.lastNeed;
	const bytes = buffered > 0 ? Buffer$1.concat([state.lastChar.subarray(0, buffered), input]) : input;
	state.lastNeed = 0;
	state.lastTotal = 0;
	return utf8Text(state, bytes, 0);
}
function utf16Text(state, input, start) {
	if ((input.length - start) % 2 === 0) {
		const result = input.toString("utf16le", start);
		if (result) {
			const code = result.charCodeAt(result.length - 1);
			if (code >= 55296 && code <= 56319) {
				state.lastNeed = 2;
				state.lastTotal = 4;
				state.lastChar[0] = input[input.length - 2];
				state.lastChar[1] = input[input.length - 1];
				return result.slice(0, -1);
			}
		}
		return result;
	}
	state.lastNeed = 1;
	state.lastTotal = 2;
	state.lastChar[0] = input[input.length - 1];
	return input.toString("utf16le", start, input.length - 1);
}
function base64Text(state, input, start, encoding) {
	const remainder = (input.length - start) % 3;
	if (remainder === 0) return encodeBytes(input, encoding, start);
	state.lastNeed = 3 - remainder;
	state.lastTotal = 3;
	if (remainder === 1) state.lastChar[0] = input[input.length - 1];
	else {
		state.lastChar[0] = input[input.length - 2];
		state.lastChar[1] = input[input.length - 1];
	}
	return encodeBytes(input, encoding, start, input.length - remainder);
}
var kNativeDecoder, StringDecoderImplementation, StringDecoder, stringDecoder;
var init_string_decoder = __esmMin(() => {
	init__jco_node_builtin_error_globals();
	init__jco_node_builtin_node_buffer();
	init_errors$2();
	init_defineProperty();
	init_objectSpread2();
	kNativeDecoder = Symbol("kNativeDecoder");
	StringDecoderImplementation = class {
		constructor(encoding) {
			_defineProperty(this, "encoding", void 0);
			_defineProperty(this, kNativeDecoder, void 0);
			const normalized = normalizeEncoding(encoding);
			if (normalized === void 0) throw unknownEncoding(encoding);
			this.encoding = normalized;
			this[kNativeDecoder] = {
				lastChar: Buffer$1.alloc(4),
				lastNeed: 0,
				lastTotal: 0
			};
		}
		write(input) {
			var _this;
			if (typeof input === "string") return input;
			if (!ArrayBuffer.isView(input)) throw invalidArgType$1("buf", [
				"Buffer",
				"TypedArray",
				"DataView"
			], input);
			const state = (_this = this) === null || _this === void 0 ? void 0 : _this[kNativeDecoder];
			if (!state) throw invalidThis("StringDecoder");
			const bytes = inputBytes(input);
			if (bytes.length === 0) return "";
			if (this.encoding === "utf8") return utf8Write(state, bytes);
			let prefix;
			let start = 0;
			if (state.lastNeed > 0) {
				prefix = fillLast(state, bytes, this.encoding);
				if (prefix === void 0) return "";
				start = state.lastNeed;
				state.lastNeed = 0;
				state.lastTotal = 0;
			}
			let decoded = "";
			if (start < bytes.length) switch (this.encoding) {
				case "utf16le":
					decoded = utf16Text(state, bytes, start);
					break;
				case "base64":
				case "base64url":
					decoded = base64Text(state, bytes, start, this.encoding);
					break;
				default: decoded = encodeBytes(bytes, this.encoding, start);
			}
			return prefix ? prefix + decoded : decoded;
		}
		end(input) {
			const result = input === void 0 ? "" : this.write(input);
			const state = this[kNativeDecoder];
			if (state.lastNeed === 0) return result;
			let trailing = "";
			switch (this.encoding) {
				case "utf8":
					trailing = state.lastChar.toString("utf8", 0, state.lastTotal - state.lastNeed);
					break;
				case "utf16le":
					trailing = state.lastChar.toString("utf16le", 0, state.lastTotal - state.lastNeed);
					break;
				case "base64":
				case "base64url": trailing = encodeBytes(state.lastChar, this.encoding, 0, state.lastTotal - state.lastNeed);
			}
			state.lastNeed = 0;
			state.lastTotal = 0;
			return result + trailing;
		}
		/** Undocumented legacy method retained by Node 24. */
		text(input, offset) {
			const state = this[kNativeDecoder];
			state.lastNeed = 0;
			state.lastTotal = 0;
			if (typeof input === "string") return this.write(input.slice(offset));
			if (!ArrayBuffer.isView(input)) throw invalidArgType$1("buf", [
				"Buffer",
				"TypedArray",
				"DataView"
			], input);
			const bytes = new Uint8Array(input.buffer, input.byteOffset, input.byteLength).subarray(offset);
			return this.write(bytes);
		}
		/** Undocumented legacy buffered-byte view retained by Node 24. */
		get lastChar() {
			var _this2;
			const state = (_this2 = this) === null || _this2 === void 0 ? void 0 : _this2[kNativeDecoder];
			if (!state) throw invalidThis("StringDecoder");
			return state.lastChar.subarray(0, 4);
		}
		/** Undocumented legacy count retained by Node 24. */
		get lastNeed() {
			var _this3;
			const state = (_this3 = this) === null || _this3 === void 0 ? void 0 : _this3[kNativeDecoder];
			if (!state) throw invalidThis("StringDecoder");
			return state.lastNeed;
		}
		/** Undocumented legacy count retained by Node 24. */
		get lastTotal() {
			var _this4;
			const state = (_this4 = this) === null || _this4 === void 0 ? void 0 : _this4[kNativeDecoder];
			if (!state) throw invalidThis("StringDecoder");
			return state.lastTotal;
		}
	};
	StringDecoder = function StringDecoder(encoding) {
		const initialized = new StringDecoderImplementation(encoding);
		return this === void 0 ? initialized : Object.assign(this, initialized);
	};
	StringDecoder.prototype = StringDecoderImplementation.prototype;
	Object.defineProperty(StringDecoder.prototype, "constructor", {
		configurable: true,
		writable: true,
		value: StringDecoder
	});
	for (const name of [
		"write",
		"end",
		"text",
		"lastChar",
		"lastNeed",
		"lastTotal"
	]) {
		const descriptor = Object.getOwnPropertyDescriptor(StringDecoder.prototype, name);
		if (descriptor) Object.defineProperty(StringDecoder.prototype, name, _objectSpread2(_objectSpread2({}, descriptor), {}, { enumerable: true }));
	}
	stringDecoder = { StringDecoder };
});
// \0jco-node-builtin:node:string_decoder
var _jco_node_builtin_node_string_decoder_exports = /* @__PURE__ */ __exportAll({
	StringDecoder: () => StringDecoder,
	default: () => _jco_node_builtin_node_string_decoder_default
});
var _jco_node_builtin_node_string_decoder_default;
var init__jco_node_builtin_node_string_decoder = __esmMin(() => {
	init_string_decoder();
	_jco_node_builtin_node_string_decoder_default = stringDecoder;
});
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/from.js
var require_from = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_objectSpread2();
	init_asyncToGenerator();
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { PromisePrototypeThen, SymbolAsyncIterator, SymbolIterator } = require_primordials();
	const { Buffer } = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { ERR_INVALID_ARG_TYPE, ERR_STREAM_NULL_VALUES } = require_errors().codes;
	function from(Readable, iterable, opts) {
		let iterator;
		if (typeof iterable === "string" || iterable instanceof Buffer) return new Readable(_objectSpread2(_objectSpread2({ objectMode: true }, opts), {}, { read() {
			this.push(iterable);
			this.push(null);
		} }));
		let isAsync;
		if (iterable && iterable[SymbolAsyncIterator]) {
			isAsync = true;
			iterator = iterable[SymbolAsyncIterator]();
		} else if (iterable && iterable[SymbolIterator]) {
			isAsync = false;
			iterator = iterable[SymbolIterator]();
		} else throw new ERR_INVALID_ARG_TYPE("iterable", ["Iterable"], iterable);
		const readable = new Readable(_objectSpread2({
			objectMode: true,
			highWaterMark: 1
		}, opts));
		let reading = false;
		readable._read = function() {
			if (!reading) {
				reading = true;
				next();
			}
		};
		readable._destroy = function(error, cb) {
			PromisePrototypeThen(close(error), () => process.nextTick(cb, error), (e) => process.nextTick(cb, e || error));
		};
		function close(_x) {
			return _close.apply(this, arguments);
		}
		function _close() {
			_close = _asyncToGenerator(function* (error) {
				const hadError = error !== void 0 && error !== null;
				const hasThrow = typeof iterator.throw === "function";
				if (hadError && hasThrow) {
					const { value, done } = yield iterator.throw(error);
					yield value;
					if (done) return;
				}
				if (typeof iterator.return === "function") {
					const { value } = yield iterator.return();
					yield value;
				}
			});
			return _close.apply(this, arguments);
		}
		function next() {
			return _next.apply(this, arguments);
		}
		function _next() {
			_next = _asyncToGenerator(function* () {
				for (;;) {
					try {
						const { value, done } = isAsync ? yield iterator.next() : iterator.next();
						if (done) readable.push(null);
						else {
							const res = value && typeof value.then === "function" ? yield value : value;
							if (res === null) {
								reading = false;
								throw new ERR_STREAM_NULL_VALUES();
							} else if (readable.push(res)) continue;
							else reading = false;
						}
					} catch (err) {
						readable.destroy(err);
					}
					break;
				}
			});
			return _next.apply(this, arguments);
		}
		return readable;
	}
	module.exports = from;
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/readable.js
var require_readable = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_awaitAsyncGenerator();
	init_wrapAsyncGenerator();
	init_objectSpread2();
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { ArrayPrototypeIndexOf, NumberIsInteger, NumberIsNaN, NumberParseInt, ObjectDefineProperties, ObjectKeys, ObjectSetPrototypeOf, Promise, SafeSet, SymbolAsyncDispose, SymbolAsyncIterator, Symbol } = require_primordials();
	module.exports = Readable;
	Readable.ReadableState = ReadableState;
	const { EventEmitter: EE } = (init__jco_node_builtin_stream_events(), __toCommonJS(_jco_node_builtin_stream_events_exports));
	const { Stream, prependListener } = require_legacy();
	const { Buffer } = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { addAbortSignal } = require_add_abort_signal();
	const eos = require_end_of_stream();
	let debug = require_util().debuglog("stream", (fn) => {
		debug = fn;
	});
	const BufferList = require_buffer_list();
	const destroyImpl = require_destroy();
	const { getHighWaterMark, getDefaultHighWaterMark } = require_state();
	const { aggregateTwoErrors, codes: { ERR_INVALID_ARG_TYPE, ERR_METHOD_NOT_IMPLEMENTED, ERR_OUT_OF_RANGE, ERR_STREAM_PUSH_AFTER_EOF, ERR_STREAM_UNSHIFT_AFTER_END_EVENT }, AbortError } = require_errors();
	const { validateObject } = require_validators();
	const kPaused = Symbol("kPaused");
	const { StringDecoder } = (init__jco_node_builtin_node_string_decoder(), __toCommonJS(_jco_node_builtin_node_string_decoder_exports));
	const from = require_from();
	ObjectSetPrototypeOf(Readable.prototype, Stream.prototype);
	ObjectSetPrototypeOf(Readable, Stream);
	const nop = () => {};
	const { errorOrDestroy } = destroyImpl;
	const kObjectMode = 1;
	const kEnded = 2;
	const kEndEmitted = 4;
	const kReading = 8;
	const kConstructed = 16;
	const kSync = 32;
	const kNeedReadable = 64;
	const kEmittedReadable = 128;
	const kReadableListening = 256;
	const kResumeScheduled = 512;
	const kErrorEmitted = 1024;
	const kEmitClose = 2048;
	const kAutoDestroy = 4096;
	const kDestroyed = 8192;
	const kClosed = 16384;
	const kCloseEmitted = 32768;
	const kMultiAwaitDrain = 65536;
	const kReadingMore = 1 << 17;
	const kDataEmitted = 1 << 18;
	function makeBitMapDescriptor(bit) {
		return {
			enumerable: false,
			get() {
				return (this.state & bit) !== 0;
			},
			set(value) {
				if (value) this.state |= bit;
				else this.state &= ~bit;
			}
		};
	}
	ObjectDefineProperties(ReadableState.prototype, {
		objectMode: makeBitMapDescriptor(kObjectMode),
		ended: makeBitMapDescriptor(kEnded),
		endEmitted: makeBitMapDescriptor(kEndEmitted),
		reading: makeBitMapDescriptor(kReading),
		constructed: makeBitMapDescriptor(kConstructed),
		sync: makeBitMapDescriptor(kSync),
		needReadable: makeBitMapDescriptor(kNeedReadable),
		emittedReadable: makeBitMapDescriptor(kEmittedReadable),
		readableListening: makeBitMapDescriptor(kReadableListening),
		resumeScheduled: makeBitMapDescriptor(kResumeScheduled),
		errorEmitted: makeBitMapDescriptor(kErrorEmitted),
		emitClose: makeBitMapDescriptor(kEmitClose),
		autoDestroy: makeBitMapDescriptor(kAutoDestroy),
		destroyed: makeBitMapDescriptor(kDestroyed),
		closed: makeBitMapDescriptor(kClosed),
		closeEmitted: makeBitMapDescriptor(kCloseEmitted),
		multiAwaitDrain: makeBitMapDescriptor(kMultiAwaitDrain),
		readingMore: makeBitMapDescriptor(kReadingMore),
		dataEmitted: makeBitMapDescriptor(kDataEmitted)
	});
	function ReadableState(options, stream, isDuplex) {
		if (typeof isDuplex !== "boolean") isDuplex = stream instanceof require_duplex();
		this.state = 6192;
		if (options && options.objectMode) this.state |= kObjectMode;
		if (isDuplex && options && options.readableObjectMode) this.state |= kObjectMode;
		this.highWaterMark = options ? getHighWaterMark(this, options, "readableHighWaterMark", isDuplex) : getDefaultHighWaterMark(false);
		this.buffer = new BufferList();
		this.length = 0;
		this.pipes = [];
		this.flowing = null;
		this[kPaused] = null;
		if (options && options.emitClose === false) this.state &= -2049;
		if (options && options.autoDestroy === false) this.state &= -4097;
		this.errored = null;
		this.defaultEncoding = options && options.defaultEncoding || "utf8";
		this.awaitDrainWriters = null;
		this.decoder = null;
		this.encoding = null;
		if (options && options.encoding) {
			this.decoder = new StringDecoder(options.encoding);
			this.encoding = options.encoding;
		}
	}
	function Readable(options) {
		if (!(this instanceof Readable)) return new Readable(options);
		const isDuplex = this instanceof require_duplex();
		this._readableState = new ReadableState(options, this, isDuplex);
		if (options) {
			if (typeof options.read === "function") this._read = options.read;
			if (typeof options.destroy === "function") this._destroy = options.destroy;
			if (typeof options.construct === "function") this._construct = options.construct;
			if (options.signal && !isDuplex) addAbortSignal(options.signal, this);
		}
		Stream.call(this, options);
		destroyImpl.construct(this, () => {
			if (this._readableState.needReadable) maybeReadMore(this, this._readableState);
		});
	}
	Readable.prototype.destroy = destroyImpl.destroy;
	Readable.prototype._undestroy = destroyImpl.undestroy;
	Readable.prototype._destroy = function(err, cb) {
		cb(err);
	};
	Readable.prototype[EE.captureRejectionSymbol] = function(err) {
		this.destroy(err);
	};
	Readable.prototype[SymbolAsyncDispose] = function() {
		let error;
		if (!this.destroyed) {
			error = this.readableEnded ? null : new AbortError();
			this.destroy(error);
		}
		return new Promise((resolve, reject) => eos(this, (err) => err && err !== error ? reject(err) : resolve(null)));
	};
	Readable.prototype.push = function(chunk, encoding) {
		return readableAddChunk(this, chunk, encoding, false);
	};
	Readable.prototype.unshift = function(chunk, encoding) {
		return readableAddChunk(this, chunk, encoding, true);
	};
	function readableAddChunk(stream, chunk, encoding, addToFront) {
		debug("readableAddChunk", chunk);
		const state = stream._readableState;
		let err;
		if ((state.state & kObjectMode) === 0) {
			if (typeof chunk === "string") {
				encoding = encoding || state.defaultEncoding;
				if (state.encoding !== encoding) {
					if (addToFront && state.encoding) chunk = Buffer.from(chunk, encoding).toString(state.encoding);
					else {
						chunk = Buffer.from(chunk, encoding);
						encoding = "";
					}
				}
			} else if (chunk instanceof Buffer) encoding = "";
			else if (Stream._isUint8Array(chunk)) {
				chunk = Stream._uint8ArrayToBuffer(chunk);
				encoding = "";
			} else if (chunk != null) err = new ERR_INVALID_ARG_TYPE("chunk", [
				"string",
				"Buffer",
				"Uint8Array"
			], chunk);
		}
		if (err) errorOrDestroy(stream, err);
		else if (chunk === null) {
			state.state &= -9;
			onEofChunk(stream, state);
		} else if ((state.state & kObjectMode) !== 0 || chunk && chunk.length > 0) {
			if (addToFront) {
				if ((state.state & kEndEmitted) !== 0) errorOrDestroy(stream, new ERR_STREAM_UNSHIFT_AFTER_END_EVENT());
				else if (state.destroyed || state.errored) return false;
				else addChunk(stream, state, chunk, true);
			} else if (state.ended) errorOrDestroy(stream, new ERR_STREAM_PUSH_AFTER_EOF());
			else if (state.destroyed || state.errored) return false;
			else {
				state.state &= -9;
				if (state.decoder && !encoding) {
					chunk = state.decoder.write(chunk);
					if (state.objectMode || chunk.length !== 0) addChunk(stream, state, chunk, false);
					else maybeReadMore(stream, state);
				} else addChunk(stream, state, chunk, false);
			}
		} else if (!addToFront) {
			state.state &= -9;
			maybeReadMore(stream, state);
		}
		return !state.ended && (state.length < state.highWaterMark || state.length === 0);
	}
	function addChunk(stream, state, chunk, addToFront) {
		if (state.flowing && state.length === 0 && !state.sync && stream.listenerCount("data") > 0) {
			if ((state.state & kMultiAwaitDrain) !== 0) state.awaitDrainWriters.clear();
			else state.awaitDrainWriters = null;
			state.dataEmitted = true;
			stream.emit("data", chunk);
		} else {
			state.length += state.objectMode ? 1 : chunk.length;
			if (addToFront) state.buffer.unshift(chunk);
			else state.buffer.push(chunk);
			if ((state.state & kNeedReadable) !== 0) emitReadable(stream);
		}
		maybeReadMore(stream, state);
	}
	Readable.prototype.isPaused = function() {
		const state = this._readableState;
		return state[kPaused] === true || state.flowing === false;
	};
	Readable.prototype.setEncoding = function(enc) {
		const decoder = new StringDecoder(enc);
		this._readableState.decoder = decoder;
		this._readableState.encoding = this._readableState.decoder.encoding;
		const buffer = this._readableState.buffer;
		let content = "";
		for (const data of buffer) content += decoder.write(data);
		buffer.clear();
		if (content !== "") buffer.push(content);
		this._readableState.length = content.length;
		return this;
	};
	const MAX_HWM = 1073741824;
	function computeNewHighWaterMark(n) {
		if (n > MAX_HWM) throw new ERR_OUT_OF_RANGE("size", "<= 1GiB", n);
		else {
			n--;
			n |= n >>> 1;
			n |= n >>> 2;
			n |= n >>> 4;
			n |= n >>> 8;
			n |= n >>> 16;
			n++;
		}
		return n;
	}
	function howMuchToRead(n, state) {
		if (n <= 0 || state.length === 0 && state.ended) return 0;
		if ((state.state & kObjectMode) !== 0) return 1;
		if (NumberIsNaN(n)) {
			if (state.flowing && state.length) return state.buffer.first().length;
			return state.length;
		}
		if (n <= state.length) return n;
		return state.ended ? state.length : 0;
	}
	Readable.prototype.read = function(n) {
		debug("read", n);
		if (n === void 0) n = NaN;
		else if (!NumberIsInteger(n)) n = NumberParseInt(n, 10);
		const state = this._readableState;
		const nOrig = n;
		if (n > state.highWaterMark) state.highWaterMark = computeNewHighWaterMark(n);
		if (n !== 0) state.state &= -129;
		if (n === 0 && state.needReadable && ((state.highWaterMark !== 0 ? state.length >= state.highWaterMark : state.length > 0) || state.ended)) {
			debug("read: emitReadable", state.length, state.ended);
			if (state.length === 0 && state.ended) endReadable(this);
			else emitReadable(this);
			return null;
		}
		n = howMuchToRead(n, state);
		if (n === 0 && state.ended) {
			if (state.length === 0) endReadable(this);
			return null;
		}
		let doRead = (state.state & kNeedReadable) !== 0;
		debug("need readable", doRead);
		if (state.length === 0 || state.length - n < state.highWaterMark) {
			doRead = true;
			debug("length less than watermark", doRead);
		}
		if (state.ended || state.reading || state.destroyed || state.errored || !state.constructed) {
			doRead = false;
			debug("reading, ended or constructing", doRead);
		} else if (doRead) {
			debug("do read");
			state.state |= 40;
			if (state.length === 0) state.state |= kNeedReadable;
			try {
				this._read(state.highWaterMark);
			} catch (err) {
				errorOrDestroy(this, err);
			}
			state.state &= -33;
			if (!state.reading) n = howMuchToRead(nOrig, state);
		}
		let ret;
		if (n > 0) ret = fromList(n, state);
		else ret = null;
		if (ret === null) {
			state.needReadable = state.length <= state.highWaterMark;
			n = 0;
		} else {
			state.length -= n;
			if (state.multiAwaitDrain) state.awaitDrainWriters.clear();
			else state.awaitDrainWriters = null;
		}
		if (state.length === 0) {
			if (!state.ended) state.needReadable = true;
			if (nOrig !== n && state.ended) endReadable(this);
		}
		if (ret !== null && !state.errorEmitted && !state.closeEmitted) {
			state.dataEmitted = true;
			this.emit("data", ret);
		}
		return ret;
	};
	function onEofChunk(stream, state) {
		debug("onEofChunk");
		if (state.ended) return;
		if (state.decoder) {
			const chunk = state.decoder.end();
			if (chunk && chunk.length) {
				state.buffer.push(chunk);
				state.length += state.objectMode ? 1 : chunk.length;
			}
		}
		state.ended = true;
		if (state.sync) emitReadable(stream);
		else {
			state.needReadable = false;
			state.emittedReadable = true;
			emitReadable_(stream);
		}
	}
	function emitReadable(stream) {
		const state = stream._readableState;
		debug("emitReadable", state.needReadable, state.emittedReadable);
		state.needReadable = false;
		if (!state.emittedReadable) {
			debug("emitReadable", state.flowing);
			state.emittedReadable = true;
			process.nextTick(emitReadable_, stream);
		}
	}
	function emitReadable_(stream) {
		const state = stream._readableState;
		debug("emitReadable_", state.destroyed, state.length, state.ended);
		if (!state.destroyed && !state.errored && (state.length || state.ended)) {
			stream.emit("readable");
			state.emittedReadable = false;
		}
		state.needReadable = !state.flowing && !state.ended && state.length <= state.highWaterMark;
		flow(stream);
	}
	function maybeReadMore(stream, state) {
		if (!state.readingMore && state.constructed) {
			state.readingMore = true;
			process.nextTick(maybeReadMore_, stream, state);
		}
	}
	function maybeReadMore_(stream, state) {
		while (!state.reading && !state.ended && (state.length < state.highWaterMark || state.flowing && state.length === 0)) {
			const len = state.length;
			debug("maybeReadMore read 0");
			stream.read(0);
			if (len === state.length) break;
		}
		state.readingMore = false;
	}
	Readable.prototype._read = function(n) {
		throw new ERR_METHOD_NOT_IMPLEMENTED("_read()");
	};
	Readable.prototype.pipe = function(dest, pipeOpts) {
		const src = this;
		const state = this._readableState;
		if (state.pipes.length === 1) {
			if (!state.multiAwaitDrain) {
				state.multiAwaitDrain = true;
				state.awaitDrainWriters = new SafeSet(state.awaitDrainWriters ? [state.awaitDrainWriters] : []);
			}
		}
		state.pipes.push(dest);
		debug("pipe count=%d opts=%j", state.pipes.length, pipeOpts);
		const endFn = (!pipeOpts || pipeOpts.end !== false) && dest !== process.stdout && dest !== process.stderr ? onend : unpipe;
		if (state.endEmitted) process.nextTick(endFn);
		else src.once("end", endFn);
		dest.on("unpipe", onunpipe);
		function onunpipe(readable, unpipeInfo) {
			debug("onunpipe");
			if (readable === src) {
				if (unpipeInfo && unpipeInfo.hasUnpiped === false) {
					unpipeInfo.hasUnpiped = true;
					cleanup();
				}
			}
		}
		function onend() {
			debug("onend");
			dest.end();
		}
		let ondrain;
		let cleanedUp = false;
		function cleanup() {
			debug("cleanup");
			dest.removeListener("close", onclose);
			dest.removeListener("finish", onfinish);
			if (ondrain) dest.removeListener("drain", ondrain);
			dest.removeListener("error", onerror);
			dest.removeListener("unpipe", onunpipe);
			src.removeListener("end", onend);
			src.removeListener("end", unpipe);
			src.removeListener("data", ondata);
			cleanedUp = true;
			if (ondrain && state.awaitDrainWriters && (!dest._writableState || dest._writableState.needDrain)) ondrain();
		}
		function pause() {
			if (!cleanedUp) {
				if (state.pipes.length === 1 && state.pipes[0] === dest) {
					debug("false write response, pause", 0);
					state.awaitDrainWriters = dest;
					state.multiAwaitDrain = false;
				} else if (state.pipes.length > 1 && state.pipes.includes(dest)) {
					debug("false write response, pause", state.awaitDrainWriters.size);
					state.awaitDrainWriters.add(dest);
				}
				src.pause();
			}
			if (!ondrain) {
				ondrain = pipeOnDrain(src, dest);
				dest.on("drain", ondrain);
			}
		}
		src.on("data", ondata);
		function ondata(chunk) {
			debug("ondata");
			const ret = dest.write(chunk);
			debug("dest.write", ret);
			if (ret === false) pause();
		}
		function onerror(er) {
			debug("onerror", er);
			unpipe();
			dest.removeListener("error", onerror);
			if (dest.listenerCount("error") === 0) {
				const s = dest._writableState || dest._readableState;
				if (s && !s.errorEmitted) errorOrDestroy(dest, er);
				else dest.emit("error", er);
			}
		}
		prependListener(dest, "error", onerror);
		function onclose() {
			dest.removeListener("finish", onfinish);
			unpipe();
		}
		dest.once("close", onclose);
		function onfinish() {
			debug("onfinish");
			dest.removeListener("close", onclose);
			unpipe();
		}
		dest.once("finish", onfinish);
		function unpipe() {
			debug("unpipe");
			src.unpipe(dest);
		}
		dest.emit("pipe", src);
		if (dest.writableNeedDrain === true) pause();
		else if (!state.flowing) {
			debug("pipe resume");
			src.resume();
		}
		return dest;
	};
	function pipeOnDrain(src, dest) {
		return function pipeOnDrainFunctionResult() {
			const state = src._readableState;
			if (state.awaitDrainWriters === dest) {
				debug("pipeOnDrain", 1);
				state.awaitDrainWriters = null;
			} else if (state.multiAwaitDrain) {
				debug("pipeOnDrain", state.awaitDrainWriters.size);
				state.awaitDrainWriters.delete(dest);
			}
			if ((!state.awaitDrainWriters || state.awaitDrainWriters.size === 0) && src.listenerCount("data")) src.resume();
		};
	}
	Readable.prototype.unpipe = function(dest) {
		const state = this._readableState;
		const unpipeInfo = { hasUnpiped: false };
		if (state.pipes.length === 0) return this;
		if (!dest) {
			const dests = state.pipes;
			state.pipes = [];
			this.pause();
			for (let i = 0; i < dests.length; i++) dests[i].emit("unpipe", this, { hasUnpiped: false });
			return this;
		}
		const index = ArrayPrototypeIndexOf(state.pipes, dest);
		if (index === -1) return this;
		state.pipes.splice(index, 1);
		if (state.pipes.length === 0) this.pause();
		dest.emit("unpipe", this, unpipeInfo);
		return this;
	};
	Readable.prototype.on = function(ev, fn) {
		const res = Stream.prototype.on.call(this, ev, fn);
		const state = this._readableState;
		if (ev === "data") {
			state.readableListening = this.listenerCount("readable") > 0;
			if (state.flowing !== false) this.resume();
		} else if (ev === "readable") {
			if (!state.endEmitted && !state.readableListening) {
				state.readableListening = state.needReadable = true;
				state.flowing = false;
				state.emittedReadable = false;
				debug("on readable", state.length, state.reading);
				if (state.length) emitReadable(this);
				else if (!state.reading) process.nextTick(nReadingNextTick, this);
			}
		}
		return res;
	};
	Readable.prototype.addListener = Readable.prototype.on;
	Readable.prototype.removeListener = function(ev, fn) {
		const res = Stream.prototype.removeListener.call(this, ev, fn);
		if (ev === "readable") process.nextTick(updateReadableListening, this);
		return res;
	};
	Readable.prototype.off = Readable.prototype.removeListener;
	Readable.prototype.removeAllListeners = function(ev) {
		const res = Stream.prototype.removeAllListeners.apply(this, arguments);
		if (ev === "readable" || ev === void 0) process.nextTick(updateReadableListening, this);
		return res;
	};
	function updateReadableListening(self) {
		const state = self._readableState;
		state.readableListening = self.listenerCount("readable") > 0;
		if (state.resumeScheduled && state[kPaused] === false) state.flowing = true;
		else if (self.listenerCount("data") > 0) self.resume();
		else if (!state.readableListening) state.flowing = null;
	}
	function nReadingNextTick(self) {
		debug("readable nexttick read 0");
		self.read(0);
	}
	Readable.prototype.resume = function() {
		const state = this._readableState;
		if (!state.flowing) {
			debug("resume");
			state.flowing = !state.readableListening;
			resume(this, state);
		}
		state[kPaused] = false;
		return this;
	};
	function resume(stream, state) {
		if (!state.resumeScheduled) {
			state.resumeScheduled = true;
			process.nextTick(resume_, stream, state);
		}
	}
	function resume_(stream, state) {
		debug("resume", state.reading);
		if (!state.reading) stream.read(0);
		state.resumeScheduled = false;
		stream.emit("resume");
		flow(stream);
		if (state.flowing && !state.reading) stream.read(0);
	}
	Readable.prototype.pause = function() {
		debug("call pause flowing=%j", this._readableState.flowing);
		if (this._readableState.flowing !== false) {
			debug("pause");
			this._readableState.flowing = false;
			this.emit("pause");
		}
		this._readableState[kPaused] = true;
		return this;
	};
	function flow(stream) {
		const state = stream._readableState;
		debug("flow", state.flowing);
		while (state.flowing && stream.read() !== null);
	}
	Readable.prototype.wrap = function(stream) {
		let paused = false;
		stream.on("data", (chunk) => {
			if (!this.push(chunk) && stream.pause) {
				paused = true;
				stream.pause();
			}
		});
		stream.on("end", () => {
			this.push(null);
		});
		stream.on("error", (err) => {
			errorOrDestroy(this, err);
		});
		stream.on("close", () => {
			this.destroy();
		});
		stream.on("destroy", () => {
			this.destroy();
		});
		this._read = () => {
			if (paused && stream.resume) {
				paused = false;
				stream.resume();
			}
		};
		const streamKeys = ObjectKeys(stream);
		for (let j = 1; j < streamKeys.length; j++) {
			const i = streamKeys[j];
			if (this[i] === void 0 && typeof stream[i] === "function") this[i] = stream[i].bind(stream);
		}
		return this;
	};
	Readable.prototype[SymbolAsyncIterator] = function() {
		return streamToAsyncIterator(this);
	};
	Readable.prototype.iterator = function(options) {
		if (options !== void 0) validateObject(options, "options");
		return streamToAsyncIterator(this, options);
	};
	function streamToAsyncIterator(stream, options) {
		if (typeof stream.read !== "function") stream = Readable.wrap(stream, { objectMode: true });
		const iter = createAsyncIterator(stream, options);
		iter.stream = stream;
		return iter;
	}
	function createAsyncIterator(_x, _x2) {
		return _createAsyncIterator.apply(this, arguments);
	}
	function _createAsyncIterator() {
		_createAsyncIterator = _wrapAsyncGenerator(function* (stream, options) {
			let callback = nop;
			function next(resolve) {
				if (this === stream) {
					callback();
					callback = nop;
				} else callback = resolve;
			}
			stream.on("readable", next);
			let error;
			const cleanup = eos(stream, { writable: false }, (err) => {
				error = err ? aggregateTwoErrors(error, err) : null;
				callback();
				callback = nop;
			});
			try {
				while (true) {
					const chunk = stream.destroyed ? null : stream.read();
					if (chunk !== null) yield chunk;
					else if (error) throw error;
					else if (error === null) return;
					else yield _awaitAsyncGenerator(new Promise(next));
				}
			} catch (err) {
				error = aggregateTwoErrors(error, err);
				throw error;
			} finally {
				if ((error || (options === null || options === void 0 ? void 0 : options.destroyOnReturn) !== false) && (error === void 0 || stream._readableState.autoDestroy)) destroyImpl.destroyer(stream, null);
				else {
					stream.off("readable", next);
					cleanup();
				}
			}
		});
		return _createAsyncIterator.apply(this, arguments);
	}
	ObjectDefineProperties(Readable.prototype, {
		readable: {
			__proto__: null,
			get() {
				const r = this._readableState;
				return !!r && r.readable !== false && !r.destroyed && !r.errorEmitted && !r.endEmitted;
			},
			set(val) {
				if (this._readableState) this._readableState.readable = !!val;
			}
		},
		readableDidRead: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return this._readableState.dataEmitted;
			}
		},
		readableAborted: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return !!(this._readableState.readable !== false && (this._readableState.destroyed || this._readableState.errored) && !this._readableState.endEmitted);
			}
		},
		readableHighWaterMark: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return this._readableState.highWaterMark;
			}
		},
		readableBuffer: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return this._readableState && this._readableState.buffer;
			}
		},
		readableFlowing: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return this._readableState.flowing;
			},
			set: function(state) {
				if (this._readableState) this._readableState.flowing = state;
			}
		},
		readableLength: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState.length;
			}
		},
		readableObjectMode: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState ? this._readableState.objectMode : false;
			}
		},
		readableEncoding: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState ? this._readableState.encoding : null;
			}
		},
		errored: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState ? this._readableState.errored : null;
			}
		},
		closed: {
			__proto__: null,
			get() {
				return this._readableState ? this._readableState.closed : false;
			}
		},
		destroyed: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState ? this._readableState.destroyed : false;
			},
			set(value) {
				if (!this._readableState) return;
				this._readableState.destroyed = value;
			}
		},
		readableEnded: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._readableState ? this._readableState.endEmitted : false;
			}
		}
	});
	ObjectDefineProperties(ReadableState.prototype, {
		pipesCount: {
			__proto__: null,
			get() {
				return this.pipes.length;
			}
		},
		paused: {
			__proto__: null,
			get() {
				return this[kPaused] !== false;
			},
			set(value) {
				this[kPaused] = !!value;
			}
		}
	});
	Readable._fromList = fromList;
	function fromList(n, state) {
		if (state.length === 0) return null;
		let ret;
		if (state.objectMode) ret = state.buffer.shift();
		else if (!n || n >= state.length) {
			if (state.decoder) ret = state.buffer.join("");
			else if (state.buffer.length === 1) ret = state.buffer.first();
			else ret = state.buffer.concat(state.length);
			state.buffer.clear();
		} else ret = state.buffer.consume(n, state.decoder);
		return ret;
	}
	function endReadable(stream) {
		const state = stream._readableState;
		debug("endReadable", state.endEmitted);
		if (!state.endEmitted) {
			state.ended = true;
			process.nextTick(endReadableNT, state, stream);
		}
	}
	function endReadableNT(state, stream) {
		debug("endReadableNT", state.endEmitted, state.length);
		if (!state.errored && !state.closeEmitted && !state.endEmitted && state.length === 0) {
			state.endEmitted = true;
			stream.emit("end");
			if (stream.writable && stream.allowHalfOpen === false) process.nextTick(endWritableNT, stream);
			else if (state.autoDestroy) {
				const wState = stream._writableState;
				if (!wState || wState.autoDestroy && (wState.finished || wState.writable === false)) stream.destroy();
			}
		}
	}
	function endWritableNT(stream) {
		if (stream.writable && !stream.writableEnded && !stream.destroyed) stream.end();
	}
	Readable.from = function(iterable, opts) {
		return from(Readable, iterable, opts);
	};
	let webStreamsAdapters;
	function lazyWebStreams() {
		if (webStreamsAdapters === void 0) webStreamsAdapters = {};
		return webStreamsAdapters;
	}
	Readable.fromWeb = function(readableStream, options) {
		return lazyWebStreams().newStreamReadableFromReadableStream(readableStream, options);
	};
	Readable.toWeb = function(streamReadable, options) {
		return lazyWebStreams().newReadableStreamFromStreamReadable(streamReadable, options);
	};
	Readable.wrap = function(src, options) {
		var _ref, _src$readableObjectMo;
		return new Readable(_objectSpread2(_objectSpread2({ objectMode: (_ref = (_src$readableObjectMo = src.readableObjectMode) !== null && _src$readableObjectMo !== void 0 ? _src$readableObjectMo : src.objectMode) !== null && _ref !== void 0 ? _ref : true }, options), {}, { destroy(err, callback) {
			destroyImpl.destroyer(src, err);
			callback(err);
		} })).wrap(src);
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/writable.js
var require_writable = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { ArrayPrototypeSlice, Error, FunctionPrototypeSymbolHasInstance, ObjectDefineProperty, ObjectDefineProperties, ObjectSetPrototypeOf, StringPrototypeToLowerCase, Symbol, SymbolHasInstance } = require_primordials();
	module.exports = Writable;
	Writable.WritableState = WritableState;
	const { EventEmitter: EE } = (init__jco_node_builtin_stream_events(), __toCommonJS(_jco_node_builtin_stream_events_exports));
	const Stream = require_legacy().Stream;
	const { Buffer } = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const destroyImpl = require_destroy();
	const { addAbortSignal } = require_add_abort_signal();
	const { getHighWaterMark, getDefaultHighWaterMark } = require_state();
	const { ERR_INVALID_ARG_TYPE, ERR_METHOD_NOT_IMPLEMENTED, ERR_MULTIPLE_CALLBACK, ERR_STREAM_CANNOT_PIPE, ERR_STREAM_DESTROYED, ERR_STREAM_ALREADY_FINISHED, ERR_STREAM_NULL_VALUES, ERR_STREAM_WRITE_AFTER_END, ERR_UNKNOWN_ENCODING } = require_errors().codes;
	const { errorOrDestroy } = destroyImpl;
	ObjectSetPrototypeOf(Writable.prototype, Stream.prototype);
	ObjectSetPrototypeOf(Writable, Stream);
	function nop() {}
	const kOnFinished = Symbol("kOnFinished");
	function WritableState(options, stream, isDuplex) {
		if (typeof isDuplex !== "boolean") isDuplex = stream instanceof require_duplex();
		this.objectMode = !!(options && options.objectMode);
		if (isDuplex) this.objectMode = this.objectMode || !!(options && options.writableObjectMode);
		this.highWaterMark = options ? getHighWaterMark(this, options, "writableHighWaterMark", isDuplex) : getDefaultHighWaterMark(false);
		this.finalCalled = false;
		this.needDrain = false;
		this.ending = false;
		this.ended = false;
		this.finished = false;
		this.destroyed = false;
		const noDecode = !!(options && options.decodeStrings === false);
		this.decodeStrings = !noDecode;
		this.defaultEncoding = options && options.defaultEncoding || "utf8";
		this.length = 0;
		this.writing = false;
		this.corked = 0;
		this.sync = true;
		this.bufferProcessing = false;
		this.onwrite = onwrite.bind(void 0, stream);
		this.writecb = null;
		this.writelen = 0;
		this.afterWriteTickInfo = null;
		resetBuffer(this);
		this.pendingcb = 0;
		this.constructed = true;
		this.prefinished = false;
		this.errorEmitted = false;
		this.emitClose = !options || options.emitClose !== false;
		this.autoDestroy = !options || options.autoDestroy !== false;
		this.errored = null;
		this.closed = false;
		this.closeEmitted = false;
		this[kOnFinished] = [];
	}
	function resetBuffer(state) {
		state.buffered = [];
		state.bufferedIndex = 0;
		state.allBuffers = true;
		state.allNoop = true;
	}
	WritableState.prototype.getBuffer = function getBuffer() {
		return ArrayPrototypeSlice(this.buffered, this.bufferedIndex);
	};
	ObjectDefineProperty(WritableState.prototype, "bufferedRequestCount", {
		__proto__: null,
		get() {
			return this.buffered.length - this.bufferedIndex;
		}
	});
	function Writable(options) {
		const isDuplex = this instanceof require_duplex();
		if (!isDuplex && !FunctionPrototypeSymbolHasInstance(Writable, this)) return new Writable(options);
		this._writableState = new WritableState(options, this, isDuplex);
		if (options) {
			if (typeof options.write === "function") this._write = options.write;
			if (typeof options.writev === "function") this._writev = options.writev;
			if (typeof options.destroy === "function") this._destroy = options.destroy;
			if (typeof options.final === "function") this._final = options.final;
			if (typeof options.construct === "function") this._construct = options.construct;
			if (options.signal) addAbortSignal(options.signal, this);
		}
		Stream.call(this, options);
		destroyImpl.construct(this, () => {
			const state = this._writableState;
			if (!state.writing) clearBuffer(this, state);
			finishMaybe(this, state);
		});
	}
	ObjectDefineProperty(Writable, SymbolHasInstance, {
		__proto__: null,
		value: function(object) {
			if (FunctionPrototypeSymbolHasInstance(this, object)) return true;
			if (this !== Writable) return false;
			return object && object._writableState instanceof WritableState;
		}
	});
	Writable.prototype.pipe = function() {
		errorOrDestroy(this, new ERR_STREAM_CANNOT_PIPE());
	};
	function _write(stream, chunk, encoding, cb) {
		const state = stream._writableState;
		if (typeof encoding === "function") {
			cb = encoding;
			encoding = state.defaultEncoding;
		} else {
			if (!encoding) encoding = state.defaultEncoding;
			else if (encoding !== "buffer" && !Buffer.isEncoding(encoding)) throw new ERR_UNKNOWN_ENCODING(encoding);
			if (typeof cb !== "function") cb = nop;
		}
		if (chunk === null) throw new ERR_STREAM_NULL_VALUES();
		else if (!state.objectMode) {
			if (typeof chunk === "string") {
				if (state.decodeStrings !== false) {
					chunk = Buffer.from(chunk, encoding);
					encoding = "buffer";
				}
			} else if (chunk instanceof Buffer) encoding = "buffer";
			else if (Stream._isUint8Array(chunk)) {
				chunk = Stream._uint8ArrayToBuffer(chunk);
				encoding = "buffer";
			} else throw new ERR_INVALID_ARG_TYPE("chunk", [
				"string",
				"Buffer",
				"Uint8Array"
			], chunk);
		}
		let err;
		if (state.ending) err = new ERR_STREAM_WRITE_AFTER_END();
		else if (state.destroyed) err = new ERR_STREAM_DESTROYED("write");
		if (err) {
			process.nextTick(cb, err);
			errorOrDestroy(stream, err, true);
			return err;
		}
		state.pendingcb++;
		return writeOrBuffer(stream, state, chunk, encoding, cb);
	}
	Writable.prototype.write = function(chunk, encoding, cb) {
		return _write(this, chunk, encoding, cb) === true;
	};
	Writable.prototype.cork = function() {
		this._writableState.corked++;
	};
	Writable.prototype.uncork = function() {
		const state = this._writableState;
		if (state.corked) {
			state.corked--;
			if (!state.writing) clearBuffer(this, state);
		}
	};
	Writable.prototype.setDefaultEncoding = function setDefaultEncoding(encoding) {
		if (typeof encoding === "string") encoding = StringPrototypeToLowerCase(encoding);
		if (!Buffer.isEncoding(encoding)) throw new ERR_UNKNOWN_ENCODING(encoding);
		this._writableState.defaultEncoding = encoding;
		return this;
	};
	function writeOrBuffer(stream, state, chunk, encoding, callback) {
		const len = state.objectMode ? 1 : chunk.length;
		state.length += len;
		const ret = state.length < state.highWaterMark;
		if (!ret) state.needDrain = true;
		if (state.writing || state.corked || state.errored || !state.constructed) {
			state.buffered.push({
				chunk,
				encoding,
				callback
			});
			if (state.allBuffers && encoding !== "buffer") state.allBuffers = false;
			if (state.allNoop && callback !== nop) state.allNoop = false;
		} else {
			state.writelen = len;
			state.writecb = callback;
			state.writing = true;
			state.sync = true;
			stream._write(chunk, encoding, state.onwrite);
			state.sync = false;
		}
		return ret && !state.errored && !state.destroyed;
	}
	function doWrite(stream, state, writev, len, chunk, encoding, cb) {
		state.writelen = len;
		state.writecb = cb;
		state.writing = true;
		state.sync = true;
		if (state.destroyed) state.onwrite(new ERR_STREAM_DESTROYED("write"));
		else if (writev) stream._writev(chunk, state.onwrite);
		else stream._write(chunk, encoding, state.onwrite);
		state.sync = false;
	}
	function onwriteError(stream, state, er, cb) {
		--state.pendingcb;
		cb(er);
		errorBuffer(state);
		errorOrDestroy(stream, er);
	}
	function onwrite(stream, er) {
		const state = stream._writableState;
		const sync = state.sync;
		const cb = state.writecb;
		if (typeof cb !== "function") {
			errorOrDestroy(stream, new ERR_MULTIPLE_CALLBACK());
			return;
		}
		state.writing = false;
		state.writecb = null;
		state.length -= state.writelen;
		state.writelen = 0;
		if (er) {
			er.stack;
			if (!state.errored) state.errored = er;
			if (stream._readableState && !stream._readableState.errored) stream._readableState.errored = er;
			if (sync) process.nextTick(onwriteError, stream, state, er, cb);
			else onwriteError(stream, state, er, cb);
		} else {
			if (state.buffered.length > state.bufferedIndex) clearBuffer(stream, state);
			if (sync) {
				if (state.afterWriteTickInfo !== null && state.afterWriteTickInfo.cb === cb) state.afterWriteTickInfo.count++;
				else {
					state.afterWriteTickInfo = {
						count: 1,
						cb,
						stream,
						state
					};
					process.nextTick(afterWriteTick, state.afterWriteTickInfo);
				}
			} else afterWrite(stream, state, 1, cb);
		}
	}
	function afterWriteTick({ stream, state, count, cb }) {
		state.afterWriteTickInfo = null;
		return afterWrite(stream, state, count, cb);
	}
	function afterWrite(stream, state, count, cb) {
		if (!state.ending && !stream.destroyed && state.length === 0 && state.needDrain) {
			state.needDrain = false;
			stream.emit("drain");
		}
		while (count-- > 0) {
			state.pendingcb--;
			cb();
		}
		if (state.destroyed) errorBuffer(state);
		finishMaybe(stream, state);
	}
	function errorBuffer(state) {
		if (state.writing) return;
		for (let n = state.bufferedIndex; n < state.buffered.length; ++n) {
			var _state$errored;
			const { chunk, callback } = state.buffered[n];
			const len = state.objectMode ? 1 : chunk.length;
			state.length -= len;
			callback((_state$errored = state.errored) !== null && _state$errored !== void 0 ? _state$errored : new ERR_STREAM_DESTROYED("write"));
		}
		const onfinishCallbacks = state[kOnFinished].splice(0);
		for (let i = 0; i < onfinishCallbacks.length; i++) {
			var _state$errored2;
			onfinishCallbacks[i]((_state$errored2 = state.errored) !== null && _state$errored2 !== void 0 ? _state$errored2 : new ERR_STREAM_DESTROYED("end"));
		}
		resetBuffer(state);
	}
	function clearBuffer(stream, state) {
		if (state.corked || state.bufferProcessing || state.destroyed || !state.constructed) return;
		const { buffered, bufferedIndex, objectMode } = state;
		const bufferedLength = buffered.length - bufferedIndex;
		if (!bufferedLength) return;
		let i = bufferedIndex;
		state.bufferProcessing = true;
		if (bufferedLength > 1 && stream._writev) {
			state.pendingcb -= bufferedLength - 1;
			const callback = state.allNoop ? nop : (err) => {
				for (let n = i; n < buffered.length; ++n) buffered[n].callback(err);
			};
			const chunks = state.allNoop && i === 0 ? buffered : ArrayPrototypeSlice(buffered, i);
			chunks.allBuffers = state.allBuffers;
			doWrite(stream, state, true, state.length, chunks, "", callback);
			resetBuffer(state);
		} else {
			do {
				const { chunk, encoding, callback } = buffered[i];
				buffered[i++] = null;
				doWrite(stream, state, false, objectMode ? 1 : chunk.length, chunk, encoding, callback);
			} while (i < buffered.length && !state.writing);
			if (i === buffered.length) resetBuffer(state);
			else if (i > 256) {
				buffered.splice(0, i);
				state.bufferedIndex = 0;
			} else state.bufferedIndex = i;
		}
		state.bufferProcessing = false;
	}
	Writable.prototype._write = function(chunk, encoding, cb) {
		if (this._writev) this._writev([{
			chunk,
			encoding
		}], cb);
		else throw new ERR_METHOD_NOT_IMPLEMENTED("_write()");
	};
	Writable.prototype._writev = null;
	Writable.prototype.end = function(chunk, encoding, cb) {
		const state = this._writableState;
		if (typeof chunk === "function") {
			cb = chunk;
			chunk = null;
			encoding = null;
		} else if (typeof encoding === "function") {
			cb = encoding;
			encoding = null;
		}
		let err;
		if (chunk !== null && chunk !== void 0) {
			const ret = _write(this, chunk, encoding);
			if (ret instanceof Error) err = ret;
		}
		if (state.corked) {
			state.corked = 1;
			this.uncork();
		}
		if (err) {} else if (!state.errored && !state.ending) {
			state.ending = true;
			finishMaybe(this, state, true);
			state.ended = true;
		} else if (state.finished) err = new ERR_STREAM_ALREADY_FINISHED("end");
		else if (state.destroyed) err = new ERR_STREAM_DESTROYED("end");
		if (typeof cb === "function") {
			if (err || state.finished) process.nextTick(cb, err);
			else state[kOnFinished].push(cb);
		}
		return this;
	};
	function needFinish(state) {
		return state.ending && !state.destroyed && state.constructed && state.length === 0 && !state.errored && state.buffered.length === 0 && !state.finished && !state.writing && !state.errorEmitted && !state.closeEmitted;
	}
	function callFinal(stream, state) {
		let called = false;
		function onFinish(err) {
			if (called) {
				errorOrDestroy(stream, err !== null && err !== void 0 ? err : ERR_MULTIPLE_CALLBACK());
				return;
			}
			called = true;
			state.pendingcb--;
			if (err) {
				const onfinishCallbacks = state[kOnFinished].splice(0);
				for (let i = 0; i < onfinishCallbacks.length; i++) onfinishCallbacks[i](err);
				errorOrDestroy(stream, err, state.sync);
			} else if (needFinish(state)) {
				state.prefinished = true;
				stream.emit("prefinish");
				state.pendingcb++;
				process.nextTick(finish, stream, state);
			}
		}
		state.sync = true;
		state.pendingcb++;
		try {
			stream._final(onFinish);
		} catch (err) {
			onFinish(err);
		}
		state.sync = false;
	}
	function prefinish(stream, state) {
		if (!state.prefinished && !state.finalCalled) {
			if (typeof stream._final === "function" && !state.destroyed) {
				state.finalCalled = true;
				callFinal(stream, state);
			} else {
				state.prefinished = true;
				stream.emit("prefinish");
			}
		}
	}
	function finishMaybe(stream, state, sync) {
		if (needFinish(state)) {
			prefinish(stream, state);
			if (state.pendingcb === 0) {
				if (sync) {
					state.pendingcb++;
					process.nextTick((stream, state) => {
						if (needFinish(state)) finish(stream, state);
						else state.pendingcb--;
					}, stream, state);
				} else if (needFinish(state)) {
					state.pendingcb++;
					finish(stream, state);
				}
			}
		}
	}
	function finish(stream, state) {
		state.pendingcb--;
		state.finished = true;
		const onfinishCallbacks = state[kOnFinished].splice(0);
		for (let i = 0; i < onfinishCallbacks.length; i++) onfinishCallbacks[i]();
		stream.emit("finish");
		if (state.autoDestroy) {
			const rState = stream._readableState;
			if (!rState || rState.autoDestroy && (rState.endEmitted || rState.readable === false)) stream.destroy();
		}
	}
	ObjectDefineProperties(Writable.prototype, {
		closed: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.closed : false;
			}
		},
		destroyed: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.destroyed : false;
			},
			set(value) {
				if (this._writableState) this._writableState.destroyed = value;
			}
		},
		writable: {
			__proto__: null,
			get() {
				const w = this._writableState;
				return !!w && w.writable !== false && !w.destroyed && !w.errored && !w.ending && !w.ended;
			},
			set(val) {
				if (this._writableState) this._writableState.writable = !!val;
			}
		},
		writableFinished: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.finished : false;
			}
		},
		writableObjectMode: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.objectMode : false;
			}
		},
		writableBuffer: {
			__proto__: null,
			get() {
				return this._writableState && this._writableState.getBuffer();
			}
		},
		writableEnded: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.ending : false;
			}
		},
		writableNeedDrain: {
			__proto__: null,
			get() {
				const wState = this._writableState;
				if (!wState) return false;
				return !wState.destroyed && !wState.ending && wState.needDrain;
			}
		},
		writableHighWaterMark: {
			__proto__: null,
			get() {
				return this._writableState && this._writableState.highWaterMark;
			}
		},
		writableCorked: {
			__proto__: null,
			get() {
				return this._writableState ? this._writableState.corked : 0;
			}
		},
		writableLength: {
			__proto__: null,
			get() {
				return this._writableState && this._writableState.length;
			}
		},
		errored: {
			__proto__: null,
			enumerable: false,
			get() {
				return this._writableState ? this._writableState.errored : null;
			}
		},
		writableAborted: {
			__proto__: null,
			enumerable: false,
			get: function() {
				return !!(this._writableState.writable !== false && (this._writableState.destroyed || this._writableState.errored) && !this._writableState.finished);
			}
		}
	});
	const destroy = destroyImpl.destroy;
	Writable.prototype.destroy = function(err, cb) {
		const state = this._writableState;
		if (!state.destroyed && (state.bufferedIndex < state.buffered.length || state[kOnFinished].length)) process.nextTick(errorBuffer, state);
		destroy.call(this, err, cb);
		return this;
	};
	Writable.prototype._undestroy = destroyImpl.undestroy;
	Writable.prototype._destroy = function(err, cb) {
		cb(err);
	};
	Writable.prototype[EE.captureRejectionSymbol] = function(err) {
		this.destroy(err);
	};
	let webStreamsAdapters;
	function lazyWebStreams() {
		if (webStreamsAdapters === void 0) webStreamsAdapters = {};
		return webStreamsAdapters;
	}
	Writable.fromWeb = function(writableStream, options) {
		return lazyWebStreams().newStreamWritableFromWritableStream(writableStream, options);
	};
	Writable.toWeb = function(streamWritable) {
		return lazyWebStreams().newWritableStreamFromStreamWritable(streamWritable);
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/duplexify.js
var require_duplexify = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_asyncToGenerator();
	init_awaitAsyncGenerator();
	init_wrapAsyncGenerator();
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const bufferModule = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { isReadable, isWritable, isIterable, isNodeStream, isReadableNodeStream, isWritableNodeStream, isDuplexNodeStream, isReadableStream, isWritableStream } = require_utils();
	const eos = require_end_of_stream();
	const { AbortError, codes: { ERR_INVALID_ARG_TYPE, ERR_INVALID_RETURN_VALUE } } = require_errors();
	const { destroyer } = require_destroy();
	const Duplex = require_duplex();
	const Readable = require_readable();
	const Writable = require_writable();
	const { createDeferredPromise } = require_util();
	const from = require_from();
	const Blob = globalThis.Blob || bufferModule.Blob;
	const isBlob = typeof Blob !== "undefined" ? function isBlob(b) {
		return b instanceof Blob;
	} : function isBlob(b) {
		return false;
	};
	const AbortController = globalThis.AbortController || require_abort_controller().AbortController;
	const { FunctionPrototypeCall } = require_primordials();
	var Duplexify = class extends Duplex {
		constructor(options) {
			super(options);
			if ((options === null || options === void 0 ? void 0 : options.readable) === false) {
				this._readableState.readable = false;
				this._readableState.ended = true;
				this._readableState.endEmitted = true;
			}
			if ((options === null || options === void 0 ? void 0 : options.writable) === false) {
				this._writableState.writable = false;
				this._writableState.ending = true;
				this._writableState.ended = true;
				this._writableState.finished = true;
			}
		}
	};
	module.exports = function duplexify(body, name) {
		if (isDuplexNodeStream(body)) return body;
		if (isReadableNodeStream(body)) return _duplexify({ readable: body });
		if (isWritableNodeStream(body)) return _duplexify({ writable: body });
		if (isNodeStream(body)) return _duplexify({
			writable: false,
			readable: false
		});
		if (isReadableStream(body)) return _duplexify({ readable: Readable.fromWeb(body) });
		if (isWritableStream(body)) return _duplexify({ writable: Writable.fromWeb(body) });
		if (typeof body === "function") {
			const { value, write, final, destroy } = fromAsyncGen(body);
			if (isIterable(value)) return from(Duplexify, value, {
				objectMode: true,
				write,
				final,
				destroy
			});
			const then = value === null || value === void 0 ? void 0 : value.then;
			if (typeof then === "function") {
				let d;
				const promise = FunctionPrototypeCall(then, value, (val) => {
					if (val != null) throw new ERR_INVALID_RETURN_VALUE("nully", "body", val);
				}, (err) => {
					destroyer(d, err);
				});
				return d = new Duplexify({
					objectMode: true,
					readable: false,
					write,
					final(cb) {
						final(_asyncToGenerator(function* () {
							try {
								yield promise;
								process.nextTick(cb, null);
							} catch (err) {
								process.nextTick(cb, err);
							}
						}));
					},
					destroy
				});
			}
			throw new ERR_INVALID_RETURN_VALUE("Iterable, AsyncIterable or AsyncFunction", name, value);
		}
		if (isBlob(body)) return duplexify(body.arrayBuffer());
		if (isIterable(body)) return from(Duplexify, body, {
			objectMode: true,
			writable: false
		});
		if (isReadableStream(body === null || body === void 0 ? void 0 : body.readable) && isWritableStream(body === null || body === void 0 ? void 0 : body.writable)) return Duplexify.fromWeb(body);
		if (typeof (body === null || body === void 0 ? void 0 : body.writable) === "object" || typeof (body === null || body === void 0 ? void 0 : body.readable) === "object") return _duplexify({
			readable: body !== null && body !== void 0 && body.readable ? isReadableNodeStream(body === null || body === void 0 ? void 0 : body.readable) ? body === null || body === void 0 ? void 0 : body.readable : duplexify(body.readable) : void 0,
			writable: body !== null && body !== void 0 && body.writable ? isWritableNodeStream(body === null || body === void 0 ? void 0 : body.writable) ? body === null || body === void 0 ? void 0 : body.writable : duplexify(body.writable) : void 0
		});
		const then = body === null || body === void 0 ? void 0 : body.then;
		if (typeof then === "function") {
			let d;
			FunctionPrototypeCall(then, body, (val) => {
				if (val != null) d.push(val);
				d.push(null);
			}, (err) => {
				destroyer(d, err);
			});
			return d = new Duplexify({
				objectMode: true,
				writable: false,
				read() {}
			});
		}
		throw new ERR_INVALID_ARG_TYPE(name, [
			"Blob",
			"ReadableStream",
			"WritableStream",
			"Stream",
			"Iterable",
			"AsyncIterable",
			"Function",
			"{ readable, writable } pair",
			"Promise"
		], body);
	};
	function fromAsyncGen(fn) {
		let { promise, resolve } = createDeferredPromise();
		const ac = new AbortController();
		const signal = ac.signal;
		return {
			value: fn(_wrapAsyncGenerator(function* () {
				while (true) {
					const _promise = promise;
					promise = null;
					const { chunk, done, cb } = yield _awaitAsyncGenerator(_promise);
					process.nextTick(cb);
					if (done) return;
					if (signal.aborted) throw new AbortError(void 0, { cause: signal.reason });
					({promise, resolve} = createDeferredPromise());
					yield chunk;
				}
			})(), { signal }),
			write(chunk, encoding, cb) {
				const _resolve = resolve;
				resolve = null;
				_resolve({
					chunk,
					done: false,
					cb
				});
			},
			final(cb) {
				const _resolve = resolve;
				resolve = null;
				_resolve({
					done: true,
					cb
				});
			},
			destroy(err, cb) {
				ac.abort();
				cb(err);
			}
		};
	}
	function _duplexify(pair) {
		const r = pair.readable && typeof pair.readable.read !== "function" ? Readable.wrap(pair.readable) : pair.readable;
		const w = pair.writable;
		let readable = !!isReadable(r);
		let writable = !!isWritable(w);
		let ondrain;
		let onfinish;
		let onreadable;
		let onclose;
		let d;
		function onfinished(err) {
			const cb = onclose;
			onclose = null;
			if (cb) cb(err);
			else if (err) d.destroy(err);
		}
		d = new Duplexify({
			readableObjectMode: !!(r !== null && r !== void 0 && r.readableObjectMode),
			writableObjectMode: !!(w !== null && w !== void 0 && w.writableObjectMode),
			readable,
			writable
		});
		if (writable) {
			eos(w, (err) => {
				writable = false;
				if (err) destroyer(r, err);
				onfinished(err);
			});
			d._write = function(chunk, encoding, callback) {
				if (w.write(chunk, encoding)) callback();
				else ondrain = callback;
			};
			d._final = function(callback) {
				w.end();
				onfinish = callback;
			};
			w.on("drain", function() {
				if (ondrain) {
					const cb = ondrain;
					ondrain = null;
					cb();
				}
			});
			w.on("finish", function() {
				if (onfinish) {
					const cb = onfinish;
					onfinish = null;
					cb();
				}
			});
		}
		if (readable) {
			eos(r, (err) => {
				readable = false;
				if (err) destroyer(r, err);
				onfinished(err);
			});
			r.on("readable", function() {
				if (onreadable) {
					const cb = onreadable;
					onreadable = null;
					cb();
				}
			});
			r.on("end", function() {
				d.push(null);
			});
			d._read = function() {
				while (true) {
					const buf = r.read();
					if (buf === null) {
						onreadable = d._read;
						return;
					}
					if (!d.push(buf)) return;
				}
			};
		}
		d._destroy = function(err, callback) {
			if (!err && onclose !== null) err = new AbortError();
			onreadable = null;
			ondrain = null;
			onfinish = null;
			if (onclose === null) callback(err);
			else {
				onclose = callback;
				destroyer(w, err);
				destroyer(r, err);
			}
		};
		return d;
	}
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/duplex.js
var require_duplex = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_objectSpread2();
	const { ObjectDefineProperties, ObjectGetOwnPropertyDescriptor, ObjectKeys, ObjectSetPrototypeOf } = require_primordials();
	module.exports = Duplex;
	const Readable = require_readable();
	const Writable = require_writable();
	ObjectSetPrototypeOf(Duplex.prototype, Readable.prototype);
	ObjectSetPrototypeOf(Duplex, Readable);
	{
		const keys = ObjectKeys(Writable.prototype);
		for (let i = 0; i < keys.length; i++) {
			const method = keys[i];
			if (!Duplex.prototype[method]) Duplex.prototype[method] = Writable.prototype[method];
		}
	}
	function Duplex(options) {
		if (!(this instanceof Duplex)) return new Duplex(options);
		Readable.call(this, options);
		Writable.call(this, options);
		if (options) {
			this.allowHalfOpen = options.allowHalfOpen !== false;
			if (options.readable === false) {
				this._readableState.readable = false;
				this._readableState.ended = true;
				this._readableState.endEmitted = true;
			}
			if (options.writable === false) {
				this._writableState.writable = false;
				this._writableState.ending = true;
				this._writableState.ended = true;
				this._writableState.finished = true;
			}
		} else this.allowHalfOpen = true;
	}
	ObjectDefineProperties(Duplex.prototype, {
		writable: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writable")),
		writableHighWaterMark: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableHighWaterMark")),
		writableObjectMode: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableObjectMode")),
		writableBuffer: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableBuffer")),
		writableLength: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableLength")),
		writableFinished: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableFinished")),
		writableCorked: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableCorked")),
		writableEnded: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableEnded")),
		writableNeedDrain: _objectSpread2({ __proto__: null }, ObjectGetOwnPropertyDescriptor(Writable.prototype, "writableNeedDrain")),
		destroyed: {
			__proto__: null,
			get() {
				if (this._readableState === void 0 || this._writableState === void 0) return false;
				return this._readableState.destroyed && this._writableState.destroyed;
			},
			set(value) {
				if (this._readableState && this._writableState) {
					this._readableState.destroyed = value;
					this._writableState.destroyed = value;
				}
			}
		}
	});
	let webStreamsAdapters;
	function lazyWebStreams() {
		if (webStreamsAdapters === void 0) webStreamsAdapters = {};
		return webStreamsAdapters;
	}
	Duplex.fromWeb = function(pair, options) {
		return lazyWebStreams().newStreamDuplexFromReadableWritablePair(pair, options);
	};
	Duplex.toWeb = function(duplex) {
		return lazyWebStreams().newReadableWritablePairFromDuplex(duplex);
	};
	let duplexify;
	Duplex.from = function(body) {
		if (!duplexify) duplexify = require_duplexify();
		return duplexify(body, "body");
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/transform.js
var require_transform = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_objectSpread2();
	const { ObjectSetPrototypeOf, Symbol } = require_primordials();
	module.exports = Transform;
	const { ERR_METHOD_NOT_IMPLEMENTED } = require_errors().codes;
	const Duplex = require_duplex();
	const { getHighWaterMark } = require_state();
	ObjectSetPrototypeOf(Transform.prototype, Duplex.prototype);
	ObjectSetPrototypeOf(Transform, Duplex);
	const kCallback = Symbol("kCallback");
	function Transform(options) {
		if (!(this instanceof Transform)) return new Transform(options);
		const readableHighWaterMark = options ? getHighWaterMark(this, options, "readableHighWaterMark", true) : null;
		if (readableHighWaterMark === 0) options = _objectSpread2(_objectSpread2({}, options), {}, {
			highWaterMark: null,
			readableHighWaterMark,
			writableHighWaterMark: options.writableHighWaterMark || 0
		});
		Duplex.call(this, options);
		this._readableState.sync = false;
		this[kCallback] = null;
		if (options) {
			if (typeof options.transform === "function") this._transform = options.transform;
			if (typeof options.flush === "function") this._flush = options.flush;
		}
		this.on("prefinish", prefinish);
	}
	function final(cb) {
		if (typeof this._flush === "function" && !this.destroyed) this._flush((er, data) => {
			if (er) {
				if (cb) cb(er);
				else this.destroy(er);
				return;
			}
			if (data != null) this.push(data);
			this.push(null);
			if (cb) cb();
		});
		else {
			this.push(null);
			if (cb) cb();
		}
	}
	function prefinish() {
		if (this._final !== final) final.call(this);
	}
	Transform.prototype._final = final;
	Transform.prototype._transform = function(chunk, encoding, callback) {
		throw new ERR_METHOD_NOT_IMPLEMENTED("_transform()");
	};
	Transform.prototype._write = function(chunk, encoding, callback) {
		const rState = this._readableState;
		const wState = this._writableState;
		const length = rState.length;
		this._transform(chunk, encoding, (err, val) => {
			if (err) {
				callback(err);
				return;
			}
			if (val != null) this.push(val);
			if (wState.ended || length === rState.length || rState.length < rState.highWaterMark) callback();
			else this[kCallback] = callback;
		});
	};
	Transform.prototype._read = function() {
		if (this[kCallback]) {
			const callback = this[kCallback];
			this[kCallback] = null;
			callback();
		}
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/passthrough.js
var require_passthrough = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { ObjectSetPrototypeOf } = require_primordials();
	module.exports = PassThrough;
	const Transform = require_transform();
	ObjectSetPrototypeOf(PassThrough.prototype, Transform.prototype);
	ObjectSetPrototypeOf(PassThrough, Transform);
	function PassThrough(options) {
		if (!(this instanceof PassThrough)) return new PassThrough(options);
		Transform.call(this, options);
	}
	PassThrough.prototype._transform = function(chunk, encoding, cb) {
		cb(null, chunk);
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/pipeline.js
var require_pipeline = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_asyncIterator();
	init_asyncGeneratorDelegate();
	init_wrapAsyncGenerator();
	init_asyncToGenerator();
	const process = (init_scheduler(), __toCommonJS(scheduler_exports));
	const { ArrayIsArray, Promise, SymbolAsyncIterator, SymbolDispose } = require_primordials();
	const eos = require_end_of_stream();
	const { once } = require_util();
	const destroyImpl = require_destroy();
	const Duplex = require_duplex();
	const { aggregateTwoErrors, codes: { ERR_INVALID_ARG_TYPE, ERR_INVALID_RETURN_VALUE, ERR_MISSING_ARGS, ERR_STREAM_DESTROYED, ERR_STREAM_PREMATURE_CLOSE }, AbortError } = require_errors();
	const { validateFunction, validateAbortSignal } = require_validators();
	const { isIterable, isReadable, isReadableNodeStream, isNodeStream, isTransformStream, isWebStream, isReadableStream, isReadableFinished } = require_utils();
	const AbortController = globalThis.AbortController || require_abort_controller().AbortController;
	let PassThrough;
	let Readable;
	let addAbortListener;
	function destroyer(stream, reading, writing) {
		let finished = false;
		stream.on("close", () => {
			finished = true;
		});
		return {
			destroy: (err) => {
				if (finished) return;
				finished = true;
				destroyImpl.destroyer(stream, err || new ERR_STREAM_DESTROYED("pipe"));
			},
			cleanup: eos(stream, {
				readable: reading,
				writable: writing
			}, (err) => {
				finished = !err;
			})
		};
	}
	function popCallback(streams) {
		validateFunction(streams[streams.length - 1], "streams[stream.length - 1]");
		return streams.pop();
	}
	function makeAsyncIterable(val) {
		if (isIterable(val)) return val;
		else if (isReadableNodeStream(val)) return fromReadable(val);
		throw new ERR_INVALID_ARG_TYPE("val", [
			"Readable",
			"Iterable",
			"AsyncIterable"
		], val);
	}
	function fromReadable(_x) {
		return _fromReadable.apply(this, arguments);
	}
	function _fromReadable() {
		_fromReadable = _wrapAsyncGenerator(function* (val) {
			if (!Readable) Readable = require_readable();
			yield* _asyncGeneratorDelegate(_asyncIterator(Readable.prototype[SymbolAsyncIterator].call(val)));
		});
		return _fromReadable.apply(this, arguments);
	}
	function pumpToNode(_x2, _x3, _x4, _x5) {
		return _pumpToNode.apply(this, arguments);
	}
	function _pumpToNode() {
		_pumpToNode = _asyncToGenerator(function* (iterable, writable, finish, { end }) {
			let error;
			let onresolve = null;
			const resume = (err) => {
				if (err) error = err;
				if (onresolve) {
					const callback = onresolve;
					onresolve = null;
					callback();
				}
			};
			const wait = () => new Promise((resolve, reject) => {
				if (error) reject(error);
				else onresolve = () => {
					if (error) reject(error);
					else resolve();
				};
			});
			writable.on("drain", resume);
			const cleanup = eos(writable, { readable: false }, resume);
			try {
				if (writable.writableNeedDrain) yield wait();
				var _iteratorAbruptCompletion = false;
				var _didIteratorError = false;
				var _iteratorError;
				try {
					for (var _iterator = _asyncIterator(iterable), _step; _iteratorAbruptCompletion = !(_step = yield _iterator.next()).done; _iteratorAbruptCompletion = false) {
						const chunk = _step.value;
						if (!writable.write(chunk)) yield wait();
					}
				} catch (err) {
					_didIteratorError = true;
					_iteratorError = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion && _iterator.return != null) yield _iterator.return();
					} finally {
						if (_didIteratorError) throw _iteratorError;
					}
				}
				if (end) {
					writable.end();
					yield wait();
				}
				finish();
			} catch (err) {
				finish(error !== err ? aggregateTwoErrors(error, err) : err);
			} finally {
				cleanup();
				writable.off("drain", resume);
			}
		});
		return _pumpToNode.apply(this, arguments);
	}
	function pumpToWeb(_x6, _x7, _x8, _x9) {
		return _pumpToWeb.apply(this, arguments);
	}
	function _pumpToWeb() {
		_pumpToWeb = _asyncToGenerator(function* (readable, writable, finish, { end }) {
			if (isTransformStream(writable)) writable = writable.writable;
			const writer = writable.getWriter();
			try {
				var _iteratorAbruptCompletion2 = false;
				var _didIteratorError2 = false;
				var _iteratorError2;
				try {
					for (var _iterator2 = _asyncIterator(readable), _step2; _iteratorAbruptCompletion2 = !(_step2 = yield _iterator2.next()).done; _iteratorAbruptCompletion2 = false) {
						const chunk = _step2.value;
						yield writer.ready;
						writer.write(chunk).catch(() => {});
					}
				} catch (err) {
					_didIteratorError2 = true;
					_iteratorError2 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion2 && _iterator2.return != null) yield _iterator2.return();
					} finally {
						if (_didIteratorError2) throw _iteratorError2;
					}
				}
				yield writer.ready;
				if (end) yield writer.close();
				finish();
			} catch (err) {
				try {
					yield writer.abort(err);
					finish(err);
				} catch (err) {
					finish(err);
				}
			}
		});
		return _pumpToWeb.apply(this, arguments);
	}
	function pipeline(...streams) {
		return pipelineImpl(streams, once(popCallback(streams)));
	}
	function pipelineImpl(streams, callback, opts) {
		if (streams.length === 1 && ArrayIsArray(streams[0])) streams = streams[0];
		if (streams.length < 2) throw new ERR_MISSING_ARGS("streams");
		const ac = new AbortController();
		const signal = ac.signal;
		const outerSignal = opts === null || opts === void 0 ? void 0 : opts.signal;
		const lastStreamCleanup = [];
		validateAbortSignal(outerSignal, "options.signal");
		function abort() {
			finishImpl(new AbortError());
		}
		addAbortListener = addAbortListener || require_util().addAbortListener;
		let disposable;
		if (outerSignal) disposable = addAbortListener(outerSignal, abort);
		let error;
		let value;
		const destroys = [];
		let finishCount = 0;
		function finish(err) {
			finishImpl(err, --finishCount === 0);
		}
		function finishImpl(err, final) {
			var _disposable;
			if (err && (!error || error.code === "ERR_STREAM_PREMATURE_CLOSE")) error = err;
			if (!error && !final) return;
			while (destroys.length) destroys.shift()(error);
			(_disposable = disposable) === null || _disposable === void 0 || _disposable[SymbolDispose]();
			ac.abort();
			if (final) {
				if (!error) lastStreamCleanup.forEach((fn) => fn());
				process.nextTick(callback, error, value);
			}
		}
		let ret;
		for (let i = 0; i < streams.length; i++) {
			const stream = streams[i];
			const reading = i < streams.length - 1;
			const writing = i > 0;
			const end = reading || (opts === null || opts === void 0 ? void 0 : opts.end) !== false;
			const isLastStream = i === streams.length - 1;
			if (isNodeStream(stream)) {
				if (end) {
					const { destroy, cleanup } = destroyer(stream, reading, writing);
					destroys.push(destroy);
					if (isReadable(stream) && isLastStream) lastStreamCleanup.push(cleanup);
				}
				function onError(err) {
					if (err && err.name !== "AbortError" && err.code !== "ERR_STREAM_PREMATURE_CLOSE") finish(err);
				}
				stream.on("error", onError);
				if (isReadable(stream) && isLastStream) lastStreamCleanup.push(() => {
					stream.removeListener("error", onError);
				});
			}
			if (i === 0) {
				if (typeof stream === "function") {
					ret = stream({ signal });
					if (!isIterable(ret)) throw new ERR_INVALID_RETURN_VALUE("Iterable, AsyncIterable or Stream", "source", ret);
				} else if (isIterable(stream) || isReadableNodeStream(stream) || isTransformStream(stream)) ret = stream;
				else ret = Duplex.from(stream);
			} else if (typeof stream === "function") {
				if (isTransformStream(ret)) {
					var _ret;
					ret = makeAsyncIterable((_ret = ret) === null || _ret === void 0 ? void 0 : _ret.readable);
				} else ret = makeAsyncIterable(ret);
				ret = stream(ret, { signal });
				if (reading) {
					if (!isIterable(ret, true)) throw new ERR_INVALID_RETURN_VALUE("AsyncIterable", `transform[${i - 1}]`, ret);
				} else {
					var _ret2;
					if (!PassThrough) PassThrough = require_passthrough();
					const pt = new PassThrough({ objectMode: true });
					const then = (_ret2 = ret) === null || _ret2 === void 0 ? void 0 : _ret2.then;
					if (typeof then === "function") {
						finishCount++;
						then.call(ret, (val) => {
							value = val;
							if (val != null) pt.write(val);
							if (end) pt.end();
							process.nextTick(finish);
						}, (err) => {
							pt.destroy(err);
							process.nextTick(finish, err);
						});
					} else if (isIterable(ret, true)) {
						finishCount++;
						pumpToNode(ret, pt, finish, { end });
					} else if (isReadableStream(ret) || isTransformStream(ret)) {
						const toRead = ret.readable || ret;
						finishCount++;
						pumpToNode(toRead, pt, finish, { end });
					} else throw new ERR_INVALID_RETURN_VALUE("AsyncIterable or Promise", "destination", ret);
					ret = pt;
					const { destroy, cleanup } = destroyer(ret, false, true);
					destroys.push(destroy);
					if (isLastStream) lastStreamCleanup.push(cleanup);
				}
			} else if (isNodeStream(stream)) {
				if (isReadableNodeStream(ret)) {
					finishCount += 2;
					const cleanup = pipe(ret, stream, finish, { end });
					if (isReadable(stream) && isLastStream) lastStreamCleanup.push(cleanup);
				} else if (isTransformStream(ret) || isReadableStream(ret)) {
					const toRead = ret.readable || ret;
					finishCount++;
					pumpToNode(toRead, stream, finish, { end });
				} else if (isIterable(ret)) {
					finishCount++;
					pumpToNode(ret, stream, finish, { end });
				} else throw new ERR_INVALID_ARG_TYPE("val", [
					"Readable",
					"Iterable",
					"AsyncIterable",
					"ReadableStream",
					"TransformStream"
				], ret);
				ret = stream;
			} else if (isWebStream(stream)) {
				if (isReadableNodeStream(ret)) {
					finishCount++;
					pumpToWeb(makeAsyncIterable(ret), stream, finish, { end });
				} else if (isReadableStream(ret) || isIterable(ret)) {
					finishCount++;
					pumpToWeb(ret, stream, finish, { end });
				} else if (isTransformStream(ret)) {
					finishCount++;
					pumpToWeb(ret.readable, stream, finish, { end });
				} else throw new ERR_INVALID_ARG_TYPE("val", [
					"Readable",
					"Iterable",
					"AsyncIterable",
					"ReadableStream",
					"TransformStream"
				], ret);
				ret = stream;
			} else ret = Duplex.from(stream);
		}
		if (signal !== null && signal !== void 0 && signal.aborted || outerSignal !== null && outerSignal !== void 0 && outerSignal.aborted) process.nextTick(abort);
		return ret;
	}
	function pipe(src, dst, finish, { end }) {
		let ended = false;
		dst.on("close", () => {
			if (!ended) finish(new ERR_STREAM_PREMATURE_CLOSE());
		});
		src.pipe(dst, { end: false });
		if (end) {
			function endFn() {
				ended = true;
				dst.end();
			}
			if (isReadableFinished(src)) process.nextTick(endFn);
			else src.once("end", endFn);
		} else finish();
		eos(src, {
			readable: true,
			writable: false
		}, (err) => {
			const rState = src._readableState;
			if (err && err.code === "ERR_STREAM_PREMATURE_CLOSE" && rState && rState.ended && !rState.errored && !rState.errorEmitted) src.once("end", finish).once("error", finish);
			else finish(err);
		});
		return eos(dst, {
			readable: false,
			writable: true
		}, finish);
	}
	module.exports = {
		pipelineImpl,
		pipeline
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/compose.js
var require_compose = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_asyncToGenerator();
	const { pipeline } = require_pipeline();
	const Duplex = require_duplex();
	const { destroyer } = require_destroy();
	const { isNodeStream, isReadable, isWritable, isWebStream, isTransformStream, isWritableStream, isReadableStream } = require_utils();
	const { AbortError, codes: { ERR_INVALID_ARG_VALUE, ERR_MISSING_ARGS } } = require_errors();
	const eos = require_end_of_stream();
	module.exports = function compose(...streams) {
		if (streams.length === 0) throw new ERR_MISSING_ARGS("streams");
		if (streams.length === 1) return Duplex.from(streams[0]);
		const orgStreams = [...streams];
		if (typeof streams[0] === "function") streams[0] = Duplex.from(streams[0]);
		if (typeof streams[streams.length - 1] === "function") {
			const idx = streams.length - 1;
			streams[idx] = Duplex.from(streams[idx]);
		}
		for (let n = 0; n < streams.length; ++n) {
			if (!isNodeStream(streams[n]) && !isWebStream(streams[n])) continue;
			if (n < streams.length - 1 && !(isReadable(streams[n]) || isReadableStream(streams[n]) || isTransformStream(streams[n]))) throw new ERR_INVALID_ARG_VALUE(`streams[${n}]`, orgStreams[n], "must be readable");
			if (n > 0 && !(isWritable(streams[n]) || isWritableStream(streams[n]) || isTransformStream(streams[n]))) throw new ERR_INVALID_ARG_VALUE(`streams[${n}]`, orgStreams[n], "must be writable");
		}
		let ondrain;
		let onfinish;
		let onreadable;
		let onclose;
		let d;
		function onfinished(err) {
			const cb = onclose;
			onclose = null;
			if (cb) cb(err);
			else if (err) d.destroy(err);
			else if (!readable && !writable) d.destroy();
		}
		const head = streams[0];
		const tail = pipeline(streams, onfinished);
		const writable = !!(isWritable(head) || isWritableStream(head) || isTransformStream(head));
		const readable = !!(isReadable(tail) || isReadableStream(tail) || isTransformStream(tail));
		d = new Duplex({
			writableObjectMode: !!(head !== null && head !== void 0 && head.writableObjectMode),
			readableObjectMode: !!(tail !== null && tail !== void 0 && tail.readableObjectMode),
			writable,
			readable
		});
		if (writable) {
			if (isNodeStream(head)) {
				d._write = function(chunk, encoding, callback) {
					if (head.write(chunk, encoding)) callback();
					else ondrain = callback;
				};
				d._final = function(callback) {
					head.end();
					onfinish = callback;
				};
				head.on("drain", function() {
					if (ondrain) {
						const cb = ondrain;
						ondrain = null;
						cb();
					}
				});
			} else if (isWebStream(head)) {
				const writer = (isTransformStream(head) ? head.writable : head).getWriter();
				d._write = /* @__PURE__ */ function() {
					var _ref = _asyncToGenerator(function* (chunk, encoding, callback) {
						try {
							yield writer.ready;
							writer.write(chunk).catch(() => {});
							callback();
						} catch (err) {
							callback(err);
						}
					});
					return function(_x, _x2, _x3) {
						return _ref.apply(this, arguments);
					};
				}();
				d._final = /* @__PURE__ */ function() {
					var _ref2 = _asyncToGenerator(function* (callback) {
						try {
							yield writer.ready;
							writer.close().catch(() => {});
							onfinish = callback;
						} catch (err) {
							callback(err);
						}
					});
					return function(_x4) {
						return _ref2.apply(this, arguments);
					};
				}();
			}
			const toRead = isTransformStream(tail) ? tail.readable : tail;
			eos(toRead, () => {
				if (onfinish) {
					const cb = onfinish;
					onfinish = null;
					cb();
				}
			});
		}
		if (readable) {
			if (isNodeStream(tail)) {
				tail.on("readable", function() {
					if (onreadable) {
						const cb = onreadable;
						onreadable = null;
						cb();
					}
				});
				tail.on("end", function() {
					d.push(null);
				});
				d._read = function() {
					while (true) {
						const buf = tail.read();
						if (buf === null) {
							onreadable = d._read;
							return;
						}
						if (!d.push(buf)) return;
					}
				};
			} else if (isWebStream(tail)) {
				const reader = (isTransformStream(tail) ? tail.readable : tail).getReader();
				d._read = _asyncToGenerator(function* () {
					while (true) try {
						const { value, done } = yield reader.read();
						if (!d.push(value)) return;
						if (done) {
							d.push(null);
							return;
						}
					} catch (_unused) {
						return;
					}
				});
			}
		}
		d._destroy = function(err, callback) {
			if (!err && onclose !== null) err = new AbortError();
			onreadable = null;
			ondrain = null;
			onfinish = null;
			if (onclose === null) callback(err);
			else {
				onclose = callback;
				if (isNodeStream(tail)) destroyer(tail, err);
			}
		};
		return d;
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/operators.js
var require_operators = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	init_asyncIterator();
	init_asyncToGenerator();
	init_awaitAsyncGenerator();
	init_wrapAsyncGenerator();
	init_asyncGeneratorDelegate();
	const AbortController = globalThis.AbortController || require_abort_controller().AbortController;
	const { codes: { ERR_INVALID_ARG_VALUE, ERR_INVALID_ARG_TYPE, ERR_MISSING_ARGS, ERR_OUT_OF_RANGE }, AbortError } = require_errors();
	const { validateAbortSignal, validateInteger, validateObject } = require_validators();
	const kWeakHandler = require_primordials().Symbol("kWeak");
	const kResistStopPropagation = require_primordials().Symbol("kResistStopPropagation");
	const { finished } = require_end_of_stream();
	const staticCompose = require_compose();
	const { addAbortSignalNoValidate } = require_add_abort_signal();
	const { isWritable, isNodeStream } = require_utils();
	const { deprecate } = require_util();
	const { ArrayPrototypePush, Boolean, MathFloor, Number, NumberIsNaN, Promise, PromiseReject, PromiseResolve, PromisePrototypeThen, Symbol } = require_primordials();
	const kEmpty = Symbol("kEmpty");
	const kEof = Symbol("kEof");
	function compose(stream, options) {
		if (options != null) validateObject(options, "options");
		if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
		if (isNodeStream(stream) && !isWritable(stream)) throw new ERR_INVALID_ARG_VALUE("stream", stream, "must be writable");
		const composedStream = staticCompose(this, stream);
		if (options !== null && options !== void 0 && options.signal) addAbortSignalNoValidate(options.signal, composedStream);
		return composedStream;
	}
	function map(fn, options) {
		if (typeof fn !== "function") throw new ERR_INVALID_ARG_TYPE("fn", ["Function", "AsyncFunction"], fn);
		if (options != null) validateObject(options, "options");
		if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
		let concurrency = 1;
		if ((options === null || options === void 0 ? void 0 : options.concurrency) != null) concurrency = MathFloor(options.concurrency);
		let highWaterMark = concurrency - 1;
		if ((options === null || options === void 0 ? void 0 : options.highWaterMark) != null) highWaterMark = MathFloor(options.highWaterMark);
		validateInteger(concurrency, "options.concurrency", 1);
		validateInteger(highWaterMark, "options.highWaterMark", 0);
		highWaterMark += concurrency;
		return (/* @__PURE__ */ function() {
			var _map = _wrapAsyncGenerator(function* () {
				const signal = require_util().AbortSignalAny([options === null || options === void 0 ? void 0 : options.signal].filter(Boolean));
				const stream = this;
				const queue = [];
				const signalOpt = { signal };
				let next;
				let resume;
				let done = false;
				let cnt = 0;
				function onCatch() {
					done = true;
					afterItemProcessed();
				}
				function afterItemProcessed() {
					cnt -= 1;
					maybeResume();
				}
				function maybeResume() {
					if (resume && !done && cnt < concurrency && queue.length < highWaterMark) {
						resume();
						resume = null;
					}
				}
				function pump() {
					return _pump.apply(this, arguments);
				}
				function _pump() {
					_pump = _asyncToGenerator(function* () {
						try {
							var _iteratorAbruptCompletion = false;
							var _didIteratorError = false;
							var _iteratorError;
							try {
								for (var _iterator = _asyncIterator(stream), _step; _iteratorAbruptCompletion = !(_step = yield _iterator.next()).done; _iteratorAbruptCompletion = false) {
									let val = _step.value;
									if (done) return;
									if (signal.aborted) throw new AbortError();
									try {
										val = fn(val, signalOpt);
										if (val === kEmpty) continue;
										val = PromiseResolve(val);
									} catch (err) {
										val = PromiseReject(err);
									}
									cnt += 1;
									PromisePrototypeThen(val, afterItemProcessed, onCatch);
									queue.push(val);
									if (next) {
										next();
										next = null;
									}
									if (!done && (queue.length >= highWaterMark || cnt >= concurrency)) yield new Promise((resolve) => {
										resume = resolve;
									});
								}
							} catch (err) {
								_didIteratorError = true;
								_iteratorError = err;
							} finally {
								try {
									if (_iteratorAbruptCompletion && _iterator.return != null) yield _iterator.return();
								} finally {
									if (_didIteratorError) throw _iteratorError;
								}
							}
							queue.push(kEof);
						} catch (err) {
							const val = PromiseReject(err);
							PromisePrototypeThen(val, afterItemProcessed, onCatch);
							queue.push(val);
						} finally {
							done = true;
							if (next) {
								next();
								next = null;
							}
						}
					});
					return _pump.apply(this, arguments);
				}
				pump();
				try {
					while (true) {
						while (queue.length > 0) {
							const val = yield _awaitAsyncGenerator(queue[0]);
							if (val === kEof) return;
							if (signal.aborted) throw new AbortError();
							if (val !== kEmpty) yield val;
							queue.shift();
							maybeResume();
						}
						yield _awaitAsyncGenerator(new Promise((resolve) => {
							next = resolve;
						}));
					}
				} finally {
					done = true;
					if (resume) {
						resume();
						resume = null;
					}
				}
			});
			function map() {
				return _map.apply(this, arguments);
			}
			return map;
		}()).call(this);
	}
	function asIndexedPairs(options = void 0) {
		if (options != null) validateObject(options, "options");
		if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
		return (/* @__PURE__ */ function() {
			var _asIndexedPairs = _wrapAsyncGenerator(function* () {
				let index = 0;
				var _iteratorAbruptCompletion2 = false;
				var _didIteratorError2 = false;
				var _iteratorError2;
				try {
					for (var _iterator2 = _asyncIterator(this), _step2; _iteratorAbruptCompletion2 = !(_step2 = yield _awaitAsyncGenerator(_iterator2.next())).done; _iteratorAbruptCompletion2 = false) {
						const val = _step2.value;
						var _options$signal;
						if (options !== null && options !== void 0 && (_options$signal = options.signal) !== null && _options$signal !== void 0 && _options$signal.aborted) throw new AbortError({ cause: options.signal.reason });
						yield [index++, val];
					}
				} catch (err) {
					_didIteratorError2 = true;
					_iteratorError2 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion2 && _iterator2.return != null) yield _awaitAsyncGenerator(_iterator2.return());
					} finally {
						if (_didIteratorError2) throw _iteratorError2;
					}
				}
			});
			function asIndexedPairs() {
				return _asIndexedPairs.apply(this, arguments);
			}
			return asIndexedPairs;
		}()).call(this);
	}
	function some(_x) {
		return _some.apply(this, arguments);
	}
	function _some() {
		_some = _asyncToGenerator(function* (fn, options = void 0) {
			var _iteratorAbruptCompletion3 = false;
			var _didIteratorError3 = false;
			var _iteratorError3;
			try {
				for (var _iterator3 = _asyncIterator(filter.call(this, fn, options)), _step3; _iteratorAbruptCompletion3 = !(_step3 = yield _iterator3.next()).done; _iteratorAbruptCompletion3 = false) {
					_step3.value;
					return true;
				}
			} catch (err) {
				_didIteratorError3 = true;
				_iteratorError3 = err;
			} finally {
				try {
					if (_iteratorAbruptCompletion3 && _iterator3.return != null) yield _iterator3.return();
				} finally {
					if (_didIteratorError3) throw _iteratorError3;
				}
			}
			return false;
		});
		return _some.apply(this, arguments);
	}
	function every(_x2) {
		return _every.apply(this, arguments);
	}
	function _every() {
		_every = _asyncToGenerator(function* (fn, options = void 0) {
			if (typeof fn !== "function") throw new ERR_INVALID_ARG_TYPE("fn", ["Function", "AsyncFunction"], fn);
			return !(yield some.call(this, _asyncToGenerator(function* (...args) {
				return !(yield fn(...args));
			}), options));
		});
		return _every.apply(this, arguments);
	}
	function find(_x3, _x4) {
		return _find.apply(this, arguments);
	}
	function _find() {
		_find = _asyncToGenerator(function* (fn, options) {
			var _iteratorAbruptCompletion4 = false;
			var _didIteratorError4 = false;
			var _iteratorError4;
			try {
				for (var _iterator4 = _asyncIterator(filter.call(this, fn, options)), _step4; _iteratorAbruptCompletion4 = !(_step4 = yield _iterator4.next()).done; _iteratorAbruptCompletion4 = false) return _step4.value;
			} catch (err) {
				_didIteratorError4 = true;
				_iteratorError4 = err;
			} finally {
				try {
					if (_iteratorAbruptCompletion4 && _iterator4.return != null) yield _iterator4.return();
				} finally {
					if (_didIteratorError4) throw _iteratorError4;
				}
			}
		});
		return _find.apply(this, arguments);
	}
	function forEach(_x7, _x8) {
		return _forEach.apply(this, arguments);
	}
	function _forEach() {
		_forEach = _asyncToGenerator(function* (fn, options) {
			if (typeof fn !== "function") throw new ERR_INVALID_ARG_TYPE("fn", ["Function", "AsyncFunction"], fn);
			function forEachFn(_x5, _x6) {
				return _forEachFn.apply(this, arguments);
			}
			function _forEachFn() {
				_forEachFn = _asyncToGenerator(function* (value, options) {
					yield fn(value, options);
					return kEmpty;
				});
				return _forEachFn.apply(this, arguments);
			}
			var _iteratorAbruptCompletion5 = false;
			var _didIteratorError5 = false;
			var _iteratorError5;
			try {
				for (var _iterator5 = _asyncIterator(map.call(this, forEachFn, options)), _step5; _iteratorAbruptCompletion5 = !(_step5 = yield _iterator5.next()).done; _iteratorAbruptCompletion5 = false) _step5.value;
			} catch (err) {
				_didIteratorError5 = true;
				_iteratorError5 = err;
			} finally {
				try {
					if (_iteratorAbruptCompletion5 && _iterator5.return != null) yield _iterator5.return();
				} finally {
					if (_didIteratorError5) throw _iteratorError5;
				}
			}
		});
		return _forEach.apply(this, arguments);
	}
	function filter(fn, options) {
		if (typeof fn !== "function") throw new ERR_INVALID_ARG_TYPE("fn", ["Function", "AsyncFunction"], fn);
		function filterFn(_x9, _x10) {
			return _filterFn.apply(this, arguments);
		}
		function _filterFn() {
			_filterFn = _asyncToGenerator(function* (value, options) {
				if (yield fn(value, options)) return value;
				return kEmpty;
			});
			return _filterFn.apply(this, arguments);
		}
		return map.call(this, filterFn, options);
	}
	var ReduceAwareErrMissingArgs = class extends ERR_MISSING_ARGS {
		constructor() {
			super("reduce");
			this.message = "Reduce of an empty stream requires an initial value";
		}
	};
	function reduce(_x11, _x12, _x13) {
		return _reduce.apply(this, arguments);
	}
	function _reduce() {
		_reduce = _asyncToGenerator(function* (reducer, initialValue, options) {
			var _options$signal2;
			if (typeof reducer !== "function") throw new ERR_INVALID_ARG_TYPE("reducer", ["Function", "AsyncFunction"], reducer);
			if (options != null) validateObject(options, "options");
			if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
			let hasInitialValue = arguments.length > 1;
			if (options !== null && options !== void 0 && (_options$signal2 = options.signal) !== null && _options$signal2 !== void 0 && _options$signal2.aborted) {
				const err = new AbortError(void 0, { cause: options.signal.reason });
				this.once("error", () => {});
				yield finished(this.destroy(err));
				throw err;
			}
			const ac = new AbortController();
			const signal = ac.signal;
			if (options !== null && options !== void 0 && options.signal) {
				const opts = {
					once: true,
					[kWeakHandler]: this,
					[kResistStopPropagation]: true
				};
				options.signal.addEventListener("abort", () => ac.abort(), opts);
			}
			let gotAnyItemFromStream = false;
			try {
				var _iteratorAbruptCompletion6 = false;
				var _didIteratorError6 = false;
				var _iteratorError6;
				try {
					for (var _iterator6 = _asyncIterator(this), _step6; _iteratorAbruptCompletion6 = !(_step6 = yield _iterator6.next()).done; _iteratorAbruptCompletion6 = false) {
						const value = _step6.value;
						var _options$signal3;
						gotAnyItemFromStream = true;
						if (options !== null && options !== void 0 && (_options$signal3 = options.signal) !== null && _options$signal3 !== void 0 && _options$signal3.aborted) throw new AbortError();
						if (!hasInitialValue) {
							initialValue = value;
							hasInitialValue = true;
						} else initialValue = yield reducer(initialValue, value, { signal });
					}
				} catch (err) {
					_didIteratorError6 = true;
					_iteratorError6 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion6 && _iterator6.return != null) yield _iterator6.return();
					} finally {
						if (_didIteratorError6) throw _iteratorError6;
					}
				}
				if (!gotAnyItemFromStream && !hasInitialValue) throw new ReduceAwareErrMissingArgs();
			} finally {
				ac.abort();
			}
			return initialValue;
		});
		return _reduce.apply(this, arguments);
	}
	function toArray(_x14) {
		return _toArray.apply(this, arguments);
	}
	function _toArray() {
		_toArray = _asyncToGenerator(function* (options) {
			if (options != null) validateObject(options, "options");
			if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
			const result = [];
			var _iteratorAbruptCompletion7 = false;
			var _didIteratorError7 = false;
			var _iteratorError7;
			try {
				for (var _iterator7 = _asyncIterator(this), _step7; _iteratorAbruptCompletion7 = !(_step7 = yield _iterator7.next()).done; _iteratorAbruptCompletion7 = false) {
					const val = _step7.value;
					var _options$signal4;
					if (options !== null && options !== void 0 && (_options$signal4 = options.signal) !== null && _options$signal4 !== void 0 && _options$signal4.aborted) throw new AbortError(void 0, { cause: options.signal.reason });
					ArrayPrototypePush(result, val);
				}
			} catch (err) {
				_didIteratorError7 = true;
				_iteratorError7 = err;
			} finally {
				try {
					if (_iteratorAbruptCompletion7 && _iterator7.return != null) yield _iterator7.return();
				} finally {
					if (_didIteratorError7) throw _iteratorError7;
				}
			}
			return result;
		});
		return _toArray.apply(this, arguments);
	}
	function flatMap(fn, options) {
		const values = map.call(this, fn, options);
		return (/* @__PURE__ */ function() {
			var _flatMap = _wrapAsyncGenerator(function* () {
				var _iteratorAbruptCompletion8 = false;
				var _didIteratorError8 = false;
				var _iteratorError8;
				try {
					for (var _iterator8 = _asyncIterator(values), _step8; _iteratorAbruptCompletion8 = !(_step8 = yield _awaitAsyncGenerator(_iterator8.next())).done; _iteratorAbruptCompletion8 = false) {
						const val = _step8.value;
						yield* _asyncGeneratorDelegate(_asyncIterator(val));
					}
				} catch (err) {
					_didIteratorError8 = true;
					_iteratorError8 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion8 && _iterator8.return != null) yield _awaitAsyncGenerator(_iterator8.return());
					} finally {
						if (_didIteratorError8) throw _iteratorError8;
					}
				}
			});
			function flatMap() {
				return _flatMap.apply(this, arguments);
			}
			return flatMap;
		}()).call(this);
	}
	function toIntegerOrInfinity(number) {
		number = Number(number);
		if (NumberIsNaN(number)) return 0;
		if (number < 0) throw new ERR_OUT_OF_RANGE("number", ">= 0", number);
		return number;
	}
	function drop(number, options = void 0) {
		if (options != null) validateObject(options, "options");
		if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
		number = toIntegerOrInfinity(number);
		return (/* @__PURE__ */ function() {
			var _drop = _wrapAsyncGenerator(function* () {
				var _options$signal5;
				if (options !== null && options !== void 0 && (_options$signal5 = options.signal) !== null && _options$signal5 !== void 0 && _options$signal5.aborted) throw new AbortError();
				var _iteratorAbruptCompletion9 = false;
				var _didIteratorError9 = false;
				var _iteratorError9;
				try {
					for (var _iterator9 = _asyncIterator(this), _step9; _iteratorAbruptCompletion9 = !(_step9 = yield _awaitAsyncGenerator(_iterator9.next())).done; _iteratorAbruptCompletion9 = false) {
						const val = _step9.value;
						var _options$signal6;
						if (options !== null && options !== void 0 && (_options$signal6 = options.signal) !== null && _options$signal6 !== void 0 && _options$signal6.aborted) throw new AbortError();
						if (number-- <= 0) yield val;
					}
				} catch (err) {
					_didIteratorError9 = true;
					_iteratorError9 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion9 && _iterator9.return != null) yield _awaitAsyncGenerator(_iterator9.return());
					} finally {
						if (_didIteratorError9) throw _iteratorError9;
					}
				}
			});
			function drop() {
				return _drop.apply(this, arguments);
			}
			return drop;
		}()).call(this);
	}
	function take(number, options = void 0) {
		if (options != null) validateObject(options, "options");
		if ((options === null || options === void 0 ? void 0 : options.signal) != null) validateAbortSignal(options.signal, "options.signal");
		number = toIntegerOrInfinity(number);
		return (/* @__PURE__ */ function() {
			var _take = _wrapAsyncGenerator(function* () {
				var _options$signal7;
				if (options !== null && options !== void 0 && (_options$signal7 = options.signal) !== null && _options$signal7 !== void 0 && _options$signal7.aborted) throw new AbortError();
				var _iteratorAbruptCompletion10 = false;
				var _didIteratorError10 = false;
				var _iteratorError10;
				try {
					for (var _iterator10 = _asyncIterator(this), _step10; _iteratorAbruptCompletion10 = !(_step10 = yield _awaitAsyncGenerator(_iterator10.next())).done; _iteratorAbruptCompletion10 = false) {
						const val = _step10.value;
						var _options$signal8;
						if (options !== null && options !== void 0 && (_options$signal8 = options.signal) !== null && _options$signal8 !== void 0 && _options$signal8.aborted) throw new AbortError();
						if (number-- > 0) yield val;
						if (number <= 0) return;
					}
				} catch (err) {
					_didIteratorError10 = true;
					_iteratorError10 = err;
				} finally {
					try {
						if (_iteratorAbruptCompletion10 && _iterator10.return != null) yield _awaitAsyncGenerator(_iterator10.return());
					} finally {
						if (_didIteratorError10) throw _iteratorError10;
					}
				}
			});
			function take() {
				return _take.apply(this, arguments);
			}
			return take;
		}()).call(this);
	}
	module.exports.streamReturningOperators = {
		asIndexedPairs: deprecate(asIndexedPairs, "readable.asIndexedPairs will be removed in a future version."),
		drop,
		filter,
		flatMap,
		map,
		take,
		compose
	};
	module.exports.promiseReturningOperators = {
		every,
		forEach,
		reduce,
		toArray,
		some,
		find
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/stream/promises.js
var require_promises = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { ArrayPrototypePop, Promise } = require_primordials();
	const { isIterable, isNodeStream, isWebStream } = require_utils();
	const { pipelineImpl: pl } = require_pipeline();
	const { finished } = require_end_of_stream();
	require_stream();
	function pipeline(...streams) {
		return new Promise((resolve, reject) => {
			let signal;
			let end;
			const lastArg = streams[streams.length - 1];
			if (lastArg && typeof lastArg === "object" && !isNodeStream(lastArg) && !isIterable(lastArg) && !isWebStream(lastArg)) {
				const options = ArrayPrototypePop(streams);
				signal = options.signal;
				end = options.end;
			}
			pl(streams, (err, value) => {
				if (err) reject(err);
				else resolve(value);
			}, {
				signal,
				end
			});
		});
	}
	module.exports = {
		finished,
		pipeline
	};
}));
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/readable-stream/lib/stream.js
var require_stream = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	const { Buffer } = (init__jco_node_builtin_node_buffer(), __toCommonJS(_jco_node_builtin_node_buffer_exports));
	const { ObjectDefineProperty, ObjectKeys, ReflectApply } = require_primordials();
	const { promisify: { custom: customPromisify } } = require_util();
	const { streamReturningOperators, promiseReturningOperators } = require_operators();
	const { codes: { ERR_ILLEGAL_CONSTRUCTOR } } = require_errors();
	const compose = require_compose();
	const { setDefaultHighWaterMark, getDefaultHighWaterMark } = require_state();
	const { pipeline } = require_pipeline();
	const { destroyer } = require_destroy();
	const eos = require_end_of_stream();
	const promises = require_promises();
	const utils = require_utils();
	const Stream = module.exports = require_legacy().Stream;
	Stream.isDestroyed = utils.isDestroyed;
	Stream.isDisturbed = utils.isDisturbed;
	Stream.isErrored = utils.isErrored;
	Stream.isReadable = utils.isReadable;
	Stream.isWritable = utils.isWritable;
	Stream.Readable = require_readable();
	for (const key of ObjectKeys(streamReturningOperators)) {
		const op = streamReturningOperators[key];
		function fn(...args) {
			if (new.target) throw ERR_ILLEGAL_CONSTRUCTOR();
			return Stream.Readable.from(ReflectApply(op, this, args));
		}
		ObjectDefineProperty(fn, "name", {
			__proto__: null,
			value: op.name
		});
		ObjectDefineProperty(fn, "length", {
			__proto__: null,
			value: op.length
		});
		ObjectDefineProperty(Stream.Readable.prototype, key, {
			__proto__: null,
			value: fn,
			enumerable: false,
			configurable: true,
			writable: true
		});
	}
	for (const key of ObjectKeys(promiseReturningOperators)) {
		const op = promiseReturningOperators[key];
		function fn(...args) {
			if (new.target) throw ERR_ILLEGAL_CONSTRUCTOR();
			return ReflectApply(op, this, args);
		}
		ObjectDefineProperty(fn, "name", {
			__proto__: null,
			value: op.name
		});
		ObjectDefineProperty(fn, "length", {
			__proto__: null,
			value: op.length
		});
		ObjectDefineProperty(Stream.Readable.prototype, key, {
			__proto__: null,
			value: fn,
			enumerable: false,
			configurable: true,
			writable: true
		});
	}
	Stream.Writable = require_writable();
	Stream.Duplex = require_duplex();
	Stream.Transform = require_transform();
	Stream.PassThrough = require_passthrough();
	Stream.pipeline = pipeline;
	const { addAbortSignal } = require_add_abort_signal();
	Stream.addAbortSignal = addAbortSignal;
	Stream.finished = eos;
	Stream.destroy = destroyer;
	Stream.compose = compose;
	Stream.setDefaultHighWaterMark = setDefaultHighWaterMark;
	Stream.getDefaultHighWaterMark = getDefaultHighWaterMark;
	ObjectDefineProperty(Stream, "promises", {
		__proto__: null,
		configurable: true,
		enumerable: true,
		get() {
			return promises;
		}
	});
	ObjectDefineProperty(pipeline, customPromisify, {
		__proto__: null,
		enumerable: true,
		get() {
			return promises.pipeline;
		}
	});
	ObjectDefineProperty(eos, customPromisify, {
		__proto__: null,
		enumerable: true,
		get() {
			return promises.finished;
		}
	});
	Stream.Stream = Stream;
	Stream._isUint8Array = function isUint8Array(value) {
		return value instanceof Uint8Array;
	};
	Stream._uint8ArrayToBuffer = function _uint8ArrayToBuffer(chunk) {
		return Buffer.from(chunk.buffer, chunk.byteOffset, chunk.byteLength);
	};
}));
const core = (/* @__PURE__ */ __toESM(require_stream(), 1)).default;
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/duplex-pair.js
/**
* Adapted from nodejs/node v24.20.0, commit
* 71b8b174857e25106d39b61a9e6f30d927da8b01,
* lib/internal/streams/duplexpair.js (MIT).
* Local changes add types and use the portable core and guest scheduler.
*/
init_scheduler();
init_defineProperty();
var DuplexSide = class extends core.Duplex {
	constructor(..._args) {
		super(..._args);
		_defineProperty(this, "otherSide", void 0);
		_defineProperty(this, "pendingRead", null);
	}
	_read() {
		const callback = this.pendingRead;
		if (callback) {
			this.pendingRead = null;
			callback();
		}
	}
	_write(chunk, _encoding, callback) {
		if (ArrayBuffer.isView(chunk) && chunk.byteLength === 0) nextTick(callback);
		else {
			this.otherSide.push(chunk);
			this.otherSide.pendingRead = callback;
		}
	}
	_final(callback) {
		this.otherSide.on("end", callback);
		this.otherSide.push(null);
	}
	_destroy(error, callback) {
		const other = this.otherSide;
		if (other && !other.destroyed) nextTick(() => {
			if (other.destroyed) return;
			if (error) other.destroy();
			else other.push(null);
		});
		callback(error);
	}
};
function duplexPair(options) {
	const first = new DuplexSide(options);
	const second = new DuplexSide(options);
	first.otherSide = second;
	second.otherSide = first;
	return [first, second];
}
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/lifecycle.js
init_core();
init_asyncToGenerator();
function isWebStream(value) {
	return typeof value === "object" && value !== null && ("getReader" in value && typeof value.getReader === "function" || "getWriter" in value && typeof value.getWriter === "function");
}
function requireClassic(value, api) {
	if (isWebStream(value)) throw unsupportedNodeApi(api, "Web Stream internal state is not exposed by the engine; convert it with Readable.fromWeb() or Writable.fromWeb() first");
}
function stage(value) {
	if (isWebStream(value)) return "getReader" in value ? core.Readable.fromWeb(value) : value;
	if (typeof value === "object" && value !== null && "readable" in value && "writable" in value && isWebStream(value.readable) && isWebStream(value.writable)) return core.Duplex.fromWeb(value);
	return value;
}
function stages(args) {
	return Array.isArray(args[0]) ? [args[0].map(stage), ...args.slice(1)] : args.map(stage);
}
function installLifecycle() {
	const originalFinished = core.finished;
	const finished = (stream, options, callback) => {
		requireClassic(stream, "stream.finished(Web Stream)");
		return typeof options === "function" ? originalFinished(stream, options) : originalFinished(stream, options, callback);
	};
	const originalPromiseFinished = core.promises.finished;
	core.promises.finished = function() {
		var _ref = _asyncToGenerator(function* (stream, options) {
			requireClassic(stream, "stream/promises.finished(Web Stream)");
			return originalPromiseFinished(stream, options);
		});
		return function(_x, _x2) {
			return _ref.apply(this, arguments);
		};
	}();
	const originalPipeline = core.pipeline;
	const pipeline = (...args) => Reflect.apply(originalPipeline, void 0, stages(args));
	const originalPromisePipeline = core.promises.pipeline;
	const promisePipeline = (...args) => {
		try {
			return Reflect.apply(originalPromisePipeline, void 0, stages(args));
		} catch (error) {
			return Promise.reject(error);
		}
	};
	core.promises.pipeline = promisePipeline;
	core.pipeline = pipeline;
	core.finished = finished;
	for (const [fn, promiseFn] of [[pipeline, promisePipeline], [finished, core.promises.finished]]) Object.defineProperty(fn, Symbol.for("nodejs.util.promisify.custom"), {
		configurable: true,
		enumerable: true,
		get: () => promiseFn
	});
	const originalCompose = core.compose;
	core.compose = (...streams) => Reflect.apply(originalCompose, void 0, streams.map(stage));
	const originalAbort = core.addAbortSignal;
	core.addAbortSignal = (signal, stream) => {
		requireClassic(stream, "stream.addAbortSignal(Web Stream)");
		return originalAbort(signal, stream);
	};
	function guarded(name, original) {
		return (stream) => {
			requireClassic(stream, `stream.${name}(Web Stream)`);
			return original(stream);
		};
	}
	core.isReadable = guarded("isReadable", core.isReadable);
	core.isWritable = guarded("isWritable", core.isWritable);
	core.isErrored = guarded("isErrored", core.isErrored);
	core.isDisturbed = guarded("isDisturbed", core.isDisturbed);
	core.Readable.isDisturbed = core.isDisturbed;
}
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/web.js
init__jco_node_builtin_error_globals();
init_validation();
init_core();
init_scheduler();
init_objectSpread2();
function booleanOption(value, name) {
	if (value !== void 0) validateBoolean(value, name);
}
function validateSignal(signal) {
	if (signal !== void 0 && (!signal || typeof signal.aborted !== "boolean" || typeof signal.addEventListener !== "function")) throw invalidArgType$1("options.signal", "AbortSignal", signal);
}
function streamError(value) {
	return value instanceof Error$1 ? value : new Error$1(String(value));
}
function abortError() {
	return new AbortError$1();
}
function done(callback, error) {
	try {
		callback(error == null ? void 0 : streamError(error));
	} catch (failure) {
		nextTick(() => {
			throw failure;
		});
	}
}
function fromReadableWeb(source, options = {}) {
	if (!source || typeof source.getReader !== "function") throw invalidArgType$1("readableStream", "ReadableStream", source);
	validateObject(options, "options", { allowArray: true });
	booleanOption(options.objectMode, "options.objectMode");
	validateSignal(options.signal);
	let reader = void 0;
	let closed = false;
	const readable = new core.Readable({
		objectMode: options.objectMode,
		highWaterMark: options.highWaterMark,
		encoding: options.encoding,
		read() {
			reader.read().then((chunk) => {
				readable.push(chunk.done ? null : chunk.value);
			}, (error) => {
				readable.destroy(streamError(error));
			});
		},
		destroy(error, callback) {
			if (!reader || closed) {
				done(callback, error);
				return;
			}
			reader.cancel(error).then(() => done(callback, error), () => done(callback, error));
		}
	});
	reader = source.getReader();
	reader.closed.then(() => {
		closed = true;
	}, (error) => {
		closed = true;
		readable.destroy(streamError(error));
	});
	if (options.signal) core.addAbortSignal(options.signal, readable);
	return readable;
}
function fromWritableWeb(source, options = {}) {
	if (!source || typeof source.getWriter !== "function") throw invalidArgType$1("writableStream", "WritableStream", source);
	validateObject(options, "options", { allowArray: true });
	booleanOption(options.objectMode, "options.objectMode");
	booleanOption(options.decodeStrings, "options.decodeStrings");
	validateSignal(options.signal);
	let writer = void 0;
	let closed = false;
	const writable = new core.Writable({
		objectMode: options.objectMode,
		highWaterMark: options.highWaterMark,
		decodeStrings: options.decodeStrings,
		write(chunk, _encoding, callback) {
			writer.ready.then(() => writer.write(chunk)).then(() => done(callback), (error) => done(callback, error));
		},
		writev(chunks, callback) {
			writer.ready.then(() => Promise.all(chunks.map((entry) => writer.write(entry.chunk)))).then(() => done(callback), (error) => done(callback, error));
		},
		final(callback) {
			if (closed) {
				done(callback);
				return;
			}
			writer.close().then(() => done(callback), (error) => done(callback, error));
		},
		destroy(error, callback) {
			if (!writer || closed) {
				done(callback, error);
				return;
			}
			(error ? writer.abort(error) : writer.close()).then(() => done(callback, error), () => done(callback, error));
		}
	});
	writer = source.getWriter();
	writer.closed.then(() => {
		closed = true;
		if (!writable.writableEnded) writable.destroy(codedError(new Error$1("Premature close"), "ERR_STREAM_PREMATURE_CLOSE"));
	}, (error) => {
		closed = true;
		writable.destroy(streamError(error));
	});
	if (options.signal) core.addAbortSignal(options.signal, writable);
	return writable;
}
function toReadableWeb(source, options = {}) {
	var _options$strategy;
	if (!source || typeof source.read !== "function" || typeof source.on !== "function") throw invalidArgType$1("streamReadable", "stream.Readable", source);
	validateObject(options, "options", { allowArray: true });
	if (options.type !== void 0 && options.type !== "bytes") throw invalidArgValue("options.type", options.type);
	const bytes = options.type === "bytes";
	let controller;
	let canceled = false;
	const onData = (value) => {
		var _controller$desiredSi;
		const chunk = !source.readableObjectMode && value instanceof Uint8Array ? new Uint8Array(value) : value;
		if (bytes) controller.enqueue(chunk);
		else controller.enqueue(chunk);
		if (((_controller$desiredSi = controller.desiredSize) !== null && _controller$desiredSi !== void 0 ? _controller$desiredSi : 0) <= 0) source.pause();
	};
	const underlying = {
		start(value) {
			controller = value;
		},
		pull() {
			source.resume();
		},
		cancel(reason) {
			canceled = true;
			source.destroy(reason == null ? void 0 : streamError(reason));
		}
	};
	const highWaterMark = source.readableHighWaterMark;
	const readable = bytes ? new ReadableStream(_objectSpread2(_objectSpread2({}, underlying), {}, { type: "bytes" }), { highWaterMark }) : new ReadableStream(underlying, (_options$strategy = options.strategy) !== null && _options$strategy !== void 0 ? _options$strategy : {
		highWaterMark,
		size(chunk) {
			return !source.readableObjectMode && ArrayBuffer.isView(chunk) ? chunk.byteLength : 1;
		}
	});
	let cleanup = () => {};
	cleanup = core.finished(source, { writable: false }, (error) => {
		cleanup();
		source.off("data", onData);
		if (canceled) return;
		canceled = true;
		if (error) controller.error(error);
		else {
			controller.close();
			if (bytes) {
				var _controller$byobReque;
				(_controller$byobReque = controller.byobRequest) === null || _controller$byobReque === void 0 || _controller$byobReque.respond(0);
			}
		}
	});
	source.pause();
	source.on("data", onData);
	return readable;
}
function deferred() {
	let resolve;
	let reject;
	return {
		promise: new Promise((res, rej) => {
			resolve = res;
			reject = rej;
		}),
		resolve,
		reject
	};
}
function toWritableWeb(source) {
	if (!source || typeof source.write !== "function" || typeof source.on !== "function") throw invalidArgType$1("streamWritable", "stream.Writable", source);
	if (source.destroyed || !source.writable) {
		const closed = new WritableStream();
		closed.close();
		return closed;
	}
	let controller;
	let draining;
	let closing;
	const onDrain = () => draining === null || draining === void 0 ? void 0 : draining.resolve();
	let cleanup = () => {};
	cleanup = core.finished(source, { readable: false }, (error) => {
		cleanup();
		source.off("drain", onDrain);
		if (error) {
			draining === null || draining === void 0 || draining.reject(error);
			closing === null || closing === void 0 || closing.reject(error);
			controller.error(error);
		} else if (closing) closing.resolve();
		else controller.error(abortError());
	});
	source.on("drain", onDrain);
	return new WritableStream({
		start(value) {
			controller = value;
		},
		write(chunk) {
			if (!source.writableObjectMode && chunk instanceof ArrayBuffer) chunk = new Uint8Array(chunk);
			if (!source.write(chunk)) {
				draining = deferred();
				if (!source.writableNeedDrain) draining.resolve();
				return draining.promise.finally(() => {
					draining = void 0;
				});
			}
		},
		close() {
			closing = deferred();
			source.end();
			return closing.promise;
		},
		abort(reason) {
			source.destroy(reason == null ? void 0 : streamError(reason));
		}
	}, {
		highWaterMark: source.writableHighWaterMark,
		size(chunk) {
			return !source.writableObjectMode && ArrayBuffer.isView(chunk) ? chunk.byteLength : 1;
		}
	});
}
function fromDuplexWeb(pair, options = {}) {
	var _options$allowHalfOpe;
	if (!pair || typeof pair !== "object") throw invalidArgType$1("pair", "Object", pair);
	if (!pair.readable || typeof pair.readable.getReader !== "function") throw invalidArgType$1("pair.readable", "ReadableStream", pair.readable);
	if (!pair.writable || typeof pair.writable.getWriter !== "function") throw invalidArgType$1("pair.writable", "WritableStream", pair.writable);
	validateObject(options, "options", { allowArray: true });
	if (pair.readable.locked || pair.writable.locked) throw invalidArgValue("pair", pair, "must contain unlocked streams");
	booleanOption(options.objectMode, "options.objectMode");
	booleanOption(options.decodeStrings, "options.decodeStrings");
	validateSignal(options.signal);
	booleanOption(options.allowHalfOpen, "options.allowHalfOpen");
	let reader = void 0;
	let writer = void 0;
	let readableClosed = false;
	let writableClosed = false;
	const duplex = new core.Duplex({
		objectMode: options.objectMode,
		highWaterMark: options.highWaterMark,
		encoding: options.encoding,
		decodeStrings: options.decodeStrings,
		allowHalfOpen: (_options$allowHalfOpe = options.allowHalfOpen) !== null && _options$allowHalfOpe !== void 0 ? _options$allowHalfOpe : false,
		read() {
			reader.read().then((chunk) => {
				duplex.push(chunk.done ? null : chunk.value);
			}, (error) => {
				duplex.destroy(streamError(error));
			});
		},
		write(chunk, _encoding, callback) {
			writer.ready.then(() => writer.write(chunk)).then(() => done(callback), (error) => done(callback, error));
		},
		writev(chunks, callback) {
			writer.ready.then(() => Promise.all(chunks.map((entry) => writer.write(entry.chunk)))).then(() => done(callback), (error) => done(callback, error));
		},
		final(callback) {
			if (writableClosed) {
				done(callback);
				return;
			}
			writer.close().then(() => done(callback), (error) => done(callback, error));
		},
		destroy(error, callback) {
			const tasks = [];
			if (reader && !readableClosed) tasks.push(reader.cancel(error));
			if (writer && !writableClosed) tasks.push(error ? writer.abort(error) : writer.close());
			Promise.allSettled(tasks).then(() => done(callback, error));
		}
	});
	reader = pair.readable.getReader();
	try {
		writer = pair.writable.getWriter();
	} catch (error) {
		reader.releaseLock();
		throw error;
	}
	reader.closed.then(() => {
		readableClosed = true;
	}, (error) => {
		readableClosed = true;
		duplex.destroy(streamError(error));
	});
	writer.closed.then(() => {
		writableClosed = true;
		if (!duplex.writableEnded) duplex.destroy(codedError(new Error$1("Premature close"), "ERR_STREAM_PREMATURE_CLOSE"));
	}, (error) => {
		writableClosed = true;
		duplex.destroy(streamError(error));
	});
	if (options.signal) core.addAbortSignal(options.signal, duplex);
	return duplex;
}
function toDuplexWeb(source, options = {}) {
	if (options && Object.prototype.hasOwnProperty.call(options, "type")) throw deprecatedNodeApi("Duplex.toWeb({ type })", "options.readableType");
	validateObject(options, "options", { allowArray: true });
	return {
		readable: toReadableWeb(source, { type: options.readableType }),
		writable: toWritableWeb(source)
	};
}
const toAsyncStreamable = Symbol.for("Stream.toAsyncStreamable");
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/shared.js
init__jco_node_builtin_text_encoding();
init_validation();
init_core();
init_asyncToGenerator();
let encoder;
function isArrayBufferLike(value) {
	return value instanceof ArrayBuffer || typeof SharedArrayBuffer !== "undefined" && value instanceof SharedArrayBuffer;
}
function isPrimitiveChunk(value) {
	return typeof value === "string" || isArrayBufferLike(value) || ArrayBuffer.isView(value);
}
function primitiveToUint8Array(value) {
	if (typeof value === "string") {
		var _encoder;
		return ((_encoder = encoder) !== null && _encoder !== void 0 ? _encoder : encoder = new TextEncoder()).encode(value);
	}
	if (isArrayBufferLike(value)) return new Uint8Array(value);
	return new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
}
function toUint8Array(value, name = "chunk") {
	if (!isPrimitiveChunk(value)) throw invalidArgType$1(name, [
		"string",
		"ArrayBuffer",
		"ArrayBufferView"
	], value);
	return primitiveToUint8Array(value);
}
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/index.js
/**
* Classic Node streams over readable-stream 4.7.0's MIT-licensed Node 18.19 core.
* Node 24 additions below are adapted from nodejs/node v24.20.0,
* 71b8b174857e25106d39b61a9e6f30d927da8b01, lib/stream.js and
* lib/internal/streams/{readable,writable,state}.js (MIT).
* Local changes use public Web APIs and a portable scheduling queue.
*/
init_asyncToGenerator();
init_asyncIterator();
init_awaitAsyncGenerator();
init_wrapAsyncGenerator();
core.setDefaultHighWaterMark(false, 65536);
core.Readable.fromWeb = fromReadableWeb;
core.Readable.toWeb = toReadableWeb;
core.Readable.isDisturbed = core.isDisturbed;
core.Writable.fromWeb = fromWritableWeb;
core.Writable.toWeb = toWritableWeb;
core.Duplex.fromWeb = fromDuplexWeb;
core.Duplex.toWeb = toDuplexWeb;
core.duplexPair = duplexPair;
core._isArrayBufferView = ArrayBuffer.isView;
installLifecycle();
function byteChunk(chunk, objectMode) {
	return !objectMode && ArrayBuffer.isView(chunk) && !(chunk instanceof Uint8Array) ? new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength) : chunk;
}
const push = core.Readable.prototype.push;
core.Readable.prototype.push = function(chunk, encoding) {
	return push.call(this, byteChunk(chunk, this.readableObjectMode), encoding);
};
const unshift = core.Readable.prototype.unshift;
core.Readable.prototype.unshift = function(chunk, encoding) {
	unshift.call(this, byteChunk(chunk, this.readableObjectMode), encoding);
};
const write = core.Writable.prototype.write;
const end = core.Writable.prototype.end;
for (const prototype of [core.Writable.prototype, core.Duplex.prototype]) {
	prototype.write = function(chunk, ...args) {
		return Reflect.apply(write, this, [byteChunk(chunk, this.writableObjectMode), ...args]);
	};
	prototype.end = function(chunk, ...args) {
		return Reflect.apply(end, this, [byteChunk(chunk, this.writableObjectMode), ...args]);
	};
}
core.Readable.prototype[Symbol.asyncDispose] = _asyncToGenerator(function* () {
	let expected;
	if (!this.destroyed) {
		expected = this.readableEnded ? void 0 : abortError();
		this.destroy(expected);
	}
	yield new Promise((resolve, reject) => {
		core.finished(this, (error) => {
			if (error && error !== expected) reject(error);
			else resolve();
		});
	});
});
core.Writable.prototype[Symbol.asyncDispose] = _asyncToGenerator(function* () {
	if (!this.destroyed) this.destroy(this.writableFinished ? void 0 : abortError());
	yield new Promise((resolve, reject) => {
		core.finished(this, (error) => {
			if (error && error.name !== "AbortError") reject(error);
			else resolve();
		});
	});
});
Object.defineProperty(core.Readable.prototype, toAsyncStreamable, {
	configurable: true,
	writable: true,
	value: _wrapAsyncGenerator(function* () {
		var _iteratorAbruptCompletion = false;
		var _didIteratorError = false;
		var _iteratorError;
		try {
			for (var _iterator = _asyncIterator(this), _step; _iteratorAbruptCompletion = !(_step = yield _awaitAsyncGenerator(_iterator.next())).done; _iteratorAbruptCompletion = false) {
				const chunk = _step.value;
				yield [toUint8Array(chunk)];
			}
		} catch (err) {
			_didIteratorError = true;
			_iteratorError = err;
		} finally {
			try {
				if (_iteratorAbruptCompletion && _iterator.return != null) yield _awaitAsyncGenerator(_iterator.return());
			} finally {
				if (_didIteratorError) throw _iteratorError;
			}
		}
	})
});
const Stream = core;
const Readable = core.Readable;
const Writable = core.Writable;
const Duplex = core.Duplex;
const Transform = core.Transform;
const PassThrough = core.PassThrough;
const pipeline$1 = core.pipeline;
const finished$1 = core.finished;
const promises = core.promises;
const compose = core.compose;
const addAbortSignal = core.addAbortSignal;
const destroy = core.destroy;
const isDestroyed = core.isDestroyed;
const isDisturbed = core.isDisturbed;
const isErrored = core.isErrored;
const isReadable = core.isReadable;
const isWritable = core.isWritable;
const getDefaultHighWaterMark = core.getDefaultHighWaterMark;
const setDefaultHighWaterMark = core.setDefaultHighWaterMark;
const _isUint8Array = core._isUint8Array;
const _isArrayBufferView = core._isArrayBufferView;
const _uint8ArrayToBuffer = core._uint8ArrayToBuffer;
// \0jco-node-builtin:node:stream
var _jco_node_builtin_node_stream_exports = /* @__PURE__ */ __exportAll({
	Duplex: () => Duplex,
	PassThrough: () => PassThrough,
	Readable: () => Readable,
	Stream: () => Stream,
	Transform: () => Transform,
	Writable: () => Writable,
	_isArrayBufferView: () => _isArrayBufferView,
	_isUint8Array: () => _isUint8Array,
	_uint8ArrayToBuffer: () => _uint8ArrayToBuffer,
	addAbortSignal: () => addAbortSignal,
	compose: () => compose,
	default: () => _jco_node_builtin_node_stream_default,
	destroy: () => destroy,
	duplexPair: () => duplexPair,
	finished: () => finished$1,
	getDefaultHighWaterMark: () => getDefaultHighWaterMark,
	isDestroyed: () => isDestroyed,
	isDisturbed: () => isDisturbed,
	isErrored: () => isErrored,
	isReadable: () => isReadable,
	isWritable: () => isWritable,
	pipeline: () => pipeline$1,
	promises: () => promises,
	setDefaultHighWaterMark: () => setDefaultHighWaterMark
});
var _jco_node_builtin_node_stream_default = Stream;
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/promises.js
const finished = promises.finished;
const pipeline = promises.pipeline;
var promises_default$1 = promises;
// \0jco-node-builtin:node:stream/promises
var promises_exports = /* @__PURE__ */ __exportAll({
	default: () => promises_default,
	finished: () => finished,
	pipeline: () => pipeline
});
var promises_default = promises_default$1;
// stock-provider.mjs
var stock_provider_exports = /* @__PURE__ */ __exportAll({
	default: () => stock_provider_default,
	dependencies: () => dependencies,
	promises: () => promises_exports,
	stream: () => _jco_node_builtin_node_stream_exports
});
init__jco_node_builtin_node_buffer();
init__jco_node_builtin_node_events();
init__jco_node_builtin_node_string_decoder();
init_scheduler();
const dependencies = {
	Buffer: Buffer$1,
	EventEmitter: EventEmitter$1,
	StringDecoder,
	nextTick
};
var stock_provider_default = _jco_node_builtin_node_stream_default;
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/abort-fallback.js
init__jco_node_builtin_error_globals();
init__jco_node_builtin_timer_globals();
init_classPrivateFieldInitSpec();
init_classPrivateFieldGet2();
init_defineProperty();
init_classPrivateFieldSet2();
var _globalThis$EventTarg;
var _globalThis$AbortCont;
var _globalThis$AbortSign;
var _globalThis;
var _globalThis$AbortCont2;
var _globalThis2;
var _globalThis2$AbortSig;
var _listeners = /* @__PURE__ */ new WeakMap();
var PortableEventTarget = class {
	constructor() {
		_classPrivateFieldInitSpec(this, _listeners, /* @__PURE__ */ new Map());
	}
	addEventListener(type, callback, options) {
		var _this$listeners$get;
		if (callback === null) return;
		const listeners = (_this$listeners$get = _classPrivateFieldGet2(_listeners, this).get(type)) !== null && _this$listeners$get !== void 0 ? _this$listeners$get : /* @__PURE__ */ new Map();
		if (!listeners.has(callback)) listeners.set(callback, typeof options === "object" && options.once === true);
		_classPrivateFieldGet2(_listeners, this).set(type, listeners);
	}
	removeEventListener(type, callback) {
		if (callback) {
			var _classPrivateFieldGet2$1;
			(_classPrivateFieldGet2$1 = _classPrivateFieldGet2(_listeners, this).get(type)) === null || _classPrivateFieldGet2$1 === void 0 || _classPrivateFieldGet2$1.delete(callback);
		}
	}
	dispatchEvent(event) {
		const listeners = _classPrivateFieldGet2(_listeners, this).get(event.type);
		for (const [callback, once] of [...listeners !== null && listeners !== void 0 ? listeners : []]) {
			if (!(listeners === null || listeners === void 0 ? void 0 : listeners.has(callback))) continue;
			if (once) listeners.delete(callback);
			if (typeof callback === "function") Reflect.apply(callback, this, [event]);
			else callback.handleEvent(event);
		}
		return !event.defaultPrevented;
	}
};
const Target = (_globalThis$EventTarg = globalThis.EventTarget) !== null && _globalThis$EventTarg !== void 0 ? _globalThis$EventTarg : PortableEventTarget;
function reason(name = "AbortError", message = "This operation was aborted") {
	return globalThis.DOMException ? new DOMException(message, name) : Object.assign(new Error$1(message), { name });
}
const token = {};
var _aborted = /* @__PURE__ */ new WeakMap();
var _reason = /* @__PURE__ */ new WeakMap();
var PortableAbortSignal = class PortableAbortSignal extends Target {
	constructor(key) {
		super();
		_classPrivateFieldInitSpec(this, _aborted, false);
		_classPrivateFieldInitSpec(this, _reason, void 0);
		_defineProperty(this, "onabort", null);
		if (key !== token) throw new TypeError("Illegal constructor");
	}
	get aborted() {
		return _classPrivateFieldGet2(_aborted, this);
	}
	get reason() {
		return _classPrivateFieldGet2(_reason, this);
	}
	throwIfAborted() {
		if (_classPrivateFieldGet2(_aborted, this)) throw _classPrivateFieldGet2(_reason, this);
	}
	abort(value = reason()) {
		var _this$onabort;
		if (_classPrivateFieldGet2(_aborted, this)) return;
		_classPrivateFieldSet2(_aborted, this, true);
		_classPrivateFieldSet2(_reason, this, value);
		const event = globalThis.Event ? new Event("abort") : {
			type: "abort",
			target: this,
			defaultPrevented: false
		};
		this.dispatchEvent(event);
		(_this$onabort = this.onabort) === null || _this$onabort === void 0 || _this$onabort.call(this, event);
	}
	static abort(value) {
		const signal = new PortableAbortSignal(token);
		signal.abort(value);
		return signal;
	}
	static timeout(milliseconds) {
		var _timer$unref;
		const signal = new PortableAbortSignal(token);
		const timer = setTimeout(() => signal.abort(reason("TimeoutError", "The operation was aborted due to timeout")), milliseconds);
		(_timer$unref = timer.unref) === null || _timer$unref === void 0 || _timer$unref.call(timer);
		return signal;
	}
	static any(signals) {
		const result = new PortableAbortSignal(token);
		const cleanups = [];
		for (const signal of signals) {
			if (signal.aborted) {
				result.abort(signal.reason);
				break;
			}
			const abort = () => result.abort(signal.reason);
			signal.addEventListener("abort", abort, { once: true });
			cleanups.push(() => signal.removeEventListener("abort", abort));
		}
		const cleanup = () => {
			for (const fn of cleanups) fn();
		};
		if (result.aborted) cleanup();
		else result.addEventListener("abort", cleanup, { once: true });
		return result;
	}
};
var PortableAbortController = class {
	constructor() {
		_defineProperty(this, "signal", new PortableAbortSignal(token));
	}
	abort(value) {
		this.signal.abort(value);
	}
};
const AbortController = (_globalThis$AbortCont = globalThis.AbortController) !== null && _globalThis$AbortCont !== void 0 ? _globalThis$AbortCont : PortableAbortController;
const AbortSignal = (_globalThis$AbortSign = globalThis.AbortSignal) !== null && _globalThis$AbortSign !== void 0 ? _globalThis$AbortSign : PortableAbortSignal;
(_globalThis$AbortCont2 = (_globalThis = globalThis).AbortController) !== null && _globalThis$AbortCont2 !== void 0 || (_globalThis.AbortController = AbortController);
(_globalThis2$AbortSig = (_globalThis2 = globalThis).AbortSignal) !== null && _globalThis2$AbortSig !== void 0 || (_globalThis2.AbortSignal = AbortSignal);
// ../../../../../../../../private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/abort-globals.js
init_core();
init_objectSpread2();
/**
* Adapt the legacy AbortSignal implementation embedded in ComponentizeJS 0.22.
* Keep native signal identities and dependency tracking. Engines with the
* standard sequence-taking any() implementation need no changes.
* Upstream fixes: bytecodealliance/StarlingMonkey#310.
*/
function installAbortCompatibility() {
	const Controller = globalThis.AbortController;
	const Signal = globalThis.AbortSignal;
	if (!Controller || !Signal || typeof Signal.any !== "function") return;
	const nativeAny = Signal.any;
	const aborted = Object.getOwnPropertyDescriptor(Signal.prototype, "aborted").get;
	const reason = Object.getOwnPropertyDescriptor(Signal.prototype, "reason").get;
	try {
		const probe = Reflect.apply(nativeAny, Signal, [new Controller().signal]);
		if (Reflect.apply(aborted, probe, []) !== false) return;
	} catch (_unused) {
		return;
	}
	const nativeAbort = Signal.abort;
	const nativeControllerAbort = Controller.prototype.abort;
	const methods = {
		any(signals) {
			if (!Array.isArray(signals)) throw invalidArgType$1("signals", "Array", signals);
			const inputs = Array.from(signals);
			for (let index = 0; index < inputs.length; index++) try {
				Reflect.apply(aborted, inputs[index], []);
			} catch (_unused2) {
				throw invalidArgType$1(`signals[${index}]`, "AbortSignal", inputs[index]);
			}
			return inputs.length ? Reflect.apply(nativeAny, Signal, inputs) : new Controller().signal;
		},
		abort(value) {
			return Reflect.apply(nativeAbort, Signal, [value]);
		},
		throwIfAborted() {
			if (Reflect.apply(aborted, this, [])) throw Reflect.apply(reason, this, []);
		}
	};
	const controllerMethods = { abort(value) {
		if (value === void 0) {
			const defaults = new Controller();
			Reflect.apply(nativeControllerAbort, defaults, []);
			value = Reflect.apply(reason, defaults.signal, []);
		}
		Reflect.apply(nativeControllerAbort, this, [value]);
	} };
	Object.defineProperties(Signal, {
		any: _objectSpread2(_objectSpread2({}, Object.getOwnPropertyDescriptor(Signal, "any")), {}, { value: methods.any }),
		abort: _objectSpread2(_objectSpread2({}, Object.getOwnPropertyDescriptor(Signal, "abort")), {}, { value: methods.abort })
	});
	Object.defineProperty(Signal.prototype, "throwIfAborted", _objectSpread2(_objectSpread2({}, Object.getOwnPropertyDescriptor(Signal.prototype, "throwIfAborted")), {}, { value: methods.throwIfAborted }));
	Object.defineProperty(Controller.prototype, "abort", _objectSpread2(_objectSpread2({}, Object.getOwnPropertyDescriptor(Controller.prototype, "abort")), {}, { value: controllerMethods.abort }));
}
installAbortCompatibility();
// workload.mjs
init__jco_node_builtin_error_globals();
init_asyncToGenerator();
const scenarioIds = Object.freeze([
	"pipeline-view-64",
	"pipeline-copy-64",
	"pipeline-view-524288",
	"pipeline-copy-524288",
	"fragmented-utf8",
	"object-backpressure",
	"handled-cancellation",
	"checksum-input-only",
	"byte-input-and-copy-construction-only",
	"stream-construction-and-clean-close-only"
]);
const seed = 2166136261;
const step = (hash, value) => Math.imul(hash ^ value >>> 0, 16777619) >>> 0;
function requireValue(value, message) {
	if (!value) throw new Error$1(message);
}
function bytesHash(hash, bytes) {
	for (let i = 0; i < bytes.length; i++) hash = step(hash, bytes[i]);
	return hash;
}
function stringHash(hash, value) {
	for (let i = 0; i < value.length; i++) hash = step(hash, value.charCodeAt(i));
	return hash;
}
function createWorkload(provider) {
	const { stream, promises, dependencies } = provider, { Buffer, StringDecoder, nextTick } = dependencies;
	requireValue(typeof Buffer.from === "function" && typeof nextTick === "function" && typeof promises.pipeline === "function", "Finite provider contract missing");
	let input;
	function setup(id) {
		requireValue(scenarioIds.includes(id), "Unknown finite scenario");
		const size = id.includes("524288") || id === "byte-input-and-copy-construction-only" ? 524288 : 64;
		const backing = new ArrayBuffer(size + 16), view = new Uint8Array(backing, 8, size);
		for (let i = 0; i < size; i++) view[i] = i * 17 + 3 & 255;
		const buffer = Buffer.from(backing, 8, size);
		requireValue(buffer.byteOffset === 8 && buffer.byteLength === size && buffer.buffer === backing, "Expected fixed attached unshared offset window");
		const text = Buffer.from("A¢€😀Z".repeat(8), "utf8"), fragments = [];
		let offset = 0;
		for (let i = 0; i < 64; i++) {
			const length = i < 24 ? 2 : 1;
			fragments.push(new Uint8Array(text.buffer, text.byteOffset + offset, length));
			offset += length;
		}
		requireValue(offset === text.byteLength, "Complete valid fragmented input");
		input = {
			id,
			view,
			buffer,
			fragments,
			objects: Array.from({ length: 64 }, (_, i) => ({ value: i })),
			size
		};
		return bytesHash(seed, view) | 0;
	}
	function run(_x) {
		return _run.apply(this, arguments);
	}
	function _run() {
		_run = _asyncToGenerator(function* (iterations, { trace = false } = {}) {
			requireValue(input && Number.isInteger(iterations) && iterations >= 1 && iterations <= 16, "Use setup plus finite1..16 iterations");
			const records = [];
			let aggregate = seed, totalUnits = 0, scheduledCallbacks = 0;
			for (let iteration = 0; iteration < iterations; iteration++) {
				const events = [], counts = {
					finish: 0,
					end: 0,
					error: 0,
					close: 0
				}, returns = [];
				let checksum = seed, units = 0, callbacks = 0, receiver;
				const emit = (...args) => {
					if (trace) {
						requireValue(events.length < 4096, "Ordinary per-iteration trace exceeded4096 records");
						events.push(args);
					}
				};
				const tick = (callback) => {
					scheduledCallbacks++;
					nextTick(callback);
				};
				function observe(target, name) {
					for (const event of [
						"finish",
						"end",
						"error",
						"close"
					]) target.on(event, function(...args) {
						var _args$0$code, _args$, _args$2;
						counts[event]++;
						emit("event", name, event, this === target, args.length, event === "error" ? (_args$0$code = (_args$ = args[0]) === null || _args$ === void 0 ? void 0 : _args$.code) !== null && _args$0$code !== void 0 ? _args$0$code : (_args$2 = args[0]) === null || _args$2 === void 0 ? void 0 : _args$2.name : null);
					});
				}
				function consume(chunk) {
					if (typeof chunk === "string") {
						requireValue(chunk === "A¢€😀Z".repeat(8).slice(units, units + chunk.length), "Exact decoded text mismatch");
						checksum = stringHash(checksum, chunk);
						units += chunk.length;
						emit("output-string", chunk);
					} else if (typeof chunk === "object" && chunk !== null && "value" in chunk) {
						requireValue(chunk.value === units, "Exact object value/order mismatch");
						checksum = step(checksum, chunk.value);
						units++;
						emit("output-object", chunk.value);
					} else {
						for (let i = 0; i < chunk.byteLength; i++) requireValue(chunk[i] === ((units + i) % input.size * 17 + 3 & 255), "Exact output byte mismatch");
						checksum = bytesHash(checksum, chunk);
						units += chunk.byteLength;
						emit("output-bytes", chunk.byteLength, bytesHash(seed, chunk));
					}
				}
				const encodingValue = (value) => value === void 0 ? { type: "undefined" } : {
					type: typeof value,
					value
				};
				function write(chunk, encoding, callback) {
					callbacks++;
					emit("write-callback", this === receiver, arguments.length, encodingValue(encoding), typeof chunk);
					consume(chunk);
					callback();
				}
				const id = input.id;
				if (id.startsWith("pipeline-") || id === "fragmented-utf8") {
					const fragmented = id === "fragmented-utf8", chunks = fragmented ? 64 : input.size === 64 ? 128 : 8;
					let index = 0, eof = false;
					const source = new stream.Readable({
						highWaterMark: fragmented ? 8 : input.size,
						read() {
							if (eof) return;
							while (index < chunks) {
								const chunk = fragmented ? input.fragments[index] : id.includes("-copy-") ? Buffer.from(input.buffer) : input.view;
								index++;
								const accepted = this.push(chunk);
								emit("push", index, accepted);
								if (!accepted) return;
							}
							eof = true;
							emit("push-eof");
							this.push(null);
						}
					});
					const decoder = fragmented ? new StringDecoder("utf8") : null;
					const pass = fragmented ? new stream.Transform({
						readableObjectMode: true,
						transform(chunk, encoding, callback) {
							emit("decode", chunk.byteLength);
							callback(null, decoder.write(chunk));
						},
						flush(callback) {
							const tail = decoder.end();
							emit("flush", tail);
							if (tail) this.push(tail);
							callback();
						}
					}) : new stream.PassThrough({ highWaterMark: input.size });
					const sink = new stream.Writable({
						objectMode: fragmented,
						highWaterMark: fragmented ? 2 : input.size,
						write
					});
					receiver = sink;
					observe(source, "source");
					observe(pass, "pass");
					observe(sink, "sink");
					const originalWrite = sink.write;
					sink.write = function(...args) {
						const accepted = Reflect.apply(originalWrite, this, args);
						returns.push(accepted);
						emit("write-return", accepted);
						return accepted;
					};
					emit("pipeline-before");
					const completion = promises.pipeline(source, pass, sink);
					emit("pipeline-registered");
					yield completion;
					emit("pipeline-resolved");
					yield new Promise((resolve) => tick(resolve));
					emit("selected-tick-checkpoint");
					requireValue(source.readableEnded && sink.writableFinished, "EOF/finish required");
					emit("terminal", source.readableEnded, sink.writableFinished, source.destroyed, pass.destroyed, sink.destroyed);
				} else if (id === "object-backpressure") {
					const sink = new stream.Writable({
						objectMode: true,
						highWaterMark: 2,
						write(chunk, encoding, callback) {
							callbacks++;
							consume(chunk);
							emit("write-callback", this === sink, arguments.length, encodingValue(encoding));
							tick(callback);
						}
					});
					observe(sink, "sink");
					for (const value of input.objects) {
						const accepted = sink.write(value);
						returns.push(accepted);
						emit("write-return", accepted);
						if (!accepted) yield new Promise((resolve) => sink.once("drain", function(...args) {
							emit("drain", this === sink, args.length);
							resolve();
						}));
					}
					const completion = promises.finished(sink);
					emit("finished-pending");
					sink.end();
					yield completion;
					emit("finished-resolved");
					yield new Promise((resolve) => tick(resolve));
					requireValue(sink.writableFinished && sink.destroyed, "Clean object writer required");
				} else if (id === "handled-cancellation") {
					const controller = new AbortController(), reason = new Error$1("ordinary benchmark cancellation");
					let next = 0;
					const source = new stream.Readable({
						objectMode: true,
						highWaterMark: 1,
						read() {
							if (next < 16) this.push({ value: next++ });
							else this.push(null);
						}
					});
					const sink = new stream.Writable({
						objectMode: true,
						highWaterMark: 1,
						write(chunk, encoding, callback) {
							callbacks++;
							consume(chunk);
							emit("write-callback", this === sink, arguments.length, encodingValue(encoding));
							tick(() => {
								if (callbacks === 4) {
									emit("abort");
									controller.abort(reason);
								}
								callback();
							});
						}
					});
					observe(source, "source");
					observe(sink, "sink");
					emit("pipeline-before");
					const completion = promises.pipeline(source, sink, { signal: controller.signal }).then(() => ({ resolved: true }), (error) => ({
						name: error.name,
						code: error.code,
						cause: error.cause === reason
					}));
					emit("pipeline-registered");
					const result = yield completion;
					emit("handled-rejection", result);
					yield new Promise((resolve) => tick(resolve));
					requireValue(result.name === "AbortError" && result.code === "ABORT_ERR" && source.destroyed && sink.destroyed && callbacks === 4, "Bounded handled cancellation required");
					emit("terminal", source.destroyed, sink.destroyed, controller.signal.aborted);
				} else if (id === "checksum-input-only" || id === "byte-input-and-copy-construction-only") {
					const count = id === "checksum-input-only" ? 128 : 8;
					for (let i = 0; i < count; i++) consume(id === "checksum-input-only" ? input.view : Buffer.from(input.buffer));
					emit("raw-control", id, count);
				} else {
					const source = new stream.Readable({ read() {
						this.push(null);
					} }), pass = new stream.PassThrough(), sink = new stream.Writable({ write });
					receiver = sink;
					observe(source, "source");
					observe(pass, "pass");
					observe(sink, "sink");
					emit("pipeline-before");
					const completion = promises.pipeline(source, pass, sink);
					emit("pipeline-registered");
					yield completion;
					emit("pipeline-resolved");
					yield new Promise((resolve) => tick(resolve));
					requireValue(source.readableEnded && sink.writableFinished, "Clean constructor-only pipeline required");
					emit("terminal", source.destroyed, pass.destroyed, sink.destroyed);
				}
				requireValue(callbacks <= 128, "Bounded callbacks per iteration");
				aggregate = step(aggregate, checksum);
				aggregate = step(aggregate, units);
				totalUnits += units;
				if (trace) records.push({
					iteration,
					checksum,
					units,
					callbacks,
					returns,
					counts,
					events
				});
			}
			return {
				scenario: input.id,
				iterations,
				checksum: aggregate | 0,
				unsignedChecksum: aggregate >>> 0,
				totalUnits,
				scheduledCallbacks,
				records
			};
		});
		return _run.apply(this, arguments);
	}
	return Object.freeze({
		setup,
		run
	});
}
// entry.mjs
init_asyncToGenerator();
const workload = createWorkload(stock_provider_exports);
const setup = workload.setup;
function run(_x) {
	return _run.apply(this, arguments);
}
function _run() {
	_run = _asyncToGenerator(function* (iterations) {
		return (yield workload.run(iterations)).checksum;
	});
	return _run.apply(this, arguments);
}
function inspect(_x2) {
	return _inspect.apply(this, arguments);
}
function _inspect() {
	_inspect = _asyncToGenerator(function* (iterations) {
		return JSON.stringify(yield workload.run(iterations, { trace: true }));
	});
	return _inspect.apply(this, arguments);
}
export { inspect, run, setup };
