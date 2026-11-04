import __smBuiltin0, * as namespace from "node:stream/web";
// tests/node-compat/foundation-stream-web/production-candidate/native-require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	module.exports = {
		canonical: __smBuiltin0,
		bare: __smBuiltin0
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var native_require_cjs_native_profile_default = __smModule.exports;
// tests/node-compat/foundation-stream-web/candidate/codec-cases.mjs
function errorValue$2(error) {
	if (error === null || typeof error !== "object") return { primitive: error };
	const value = {
		name: error.name,
		sentinel: error.message === "sentinel"
	};
	if (error.code !== void 0) value.code = error.code;
	return value;
}
function outputValue(value) {
	if (typeof value === "string") return value.length > 256 ? {
		stringLength: value.length,
		first: value[0],
		last: value[value.length - 1]
	} : value;
	if (value.byteLength > 256) {
		let sum = 0;
		for (let i = 0; i < value.length; i++) sum = Math.imul(sum, 33) + value[i] >>> 0;
		return {
			byteLength: value.byteLength,
			hash: sum
		};
	}
	return [...value];
}
async function pipeline(codec, chunks) {
	const writer = codec.writable.getWriter(), reader = codec.readable.getReader(), outputs = [];
	const closed = writer.closed.then(() => ({ fulfilled: true }), (error) => ({ error: errorValue$2(error) }));
	const readerClosed = reader.closed.then(() => ({ fulfilled: true }), (error) => ({ error: errorValue$2(error) }));
	const draining = (async () => {
		try {
			while (true) {
				const item = await reader.read();
				if (item.done) return { fulfilled: true };
				outputs.push(outputValue(item.value));
			}
		} catch (error) {
			return { error: errorValue$2(error) };
		}
	})();
	const writes = [];
	let failed = false;
	for (const chunk of chunks) try {
		await writer.write(chunk);
		writes.push({ fulfilled: true });
	} catch (error) {
		writes.push({ error: errorValue$2(error) });
		failed = true;
		break;
	}
	let close = { skipped: true };
	if (!failed) try {
		await writer.close();
		close = { fulfilled: true };
	} catch (error) {
		close = { error: errorValue$2(error) };
	}
	const read = await draining, writerClosed = await closed, readClosed = await readerClosed;
	writer.releaseLock();
	reader.releaseLock();
	return {
		outputs,
		writes,
		close,
		read,
		writerClosed,
		readClosed
	};
}
function definitions() {
	const values = [];
	function encoder(name, make) {
		values.push({
			name: "encoder:" + name,
			kind: "encoder",
			make
		});
	}
	function decoder(name, chunks, options) {
		values.push({
			name: "decoder:" + name,
			kind: "decoder",
			make: () => ({
				chunks: chunks.map((bytes) => Uint8Array.from(bytes)),
				options
			})
		});
	}
	encoder("empty", () => ({ chunks: [] }));
	encoder("empty-writes", () => ({ chunks: [
		"",
		"",
		""
	] }));
	encoder("ascii", () => ({ chunks: ["a", "bc"] }));
	encoder("pair-split", () => ({ chunks: ["\ud83c", "\udf0d"] }));
	encoder("pair-whole", () => ({ chunks: ["🌍"] }));
	encoder("high-empty-low", () => ({ chunks: [
		"\ud83c",
		"",
		"\udf0d"
	] }));
	encoder("high-flush", () => ({ chunks: ["\ud800"] }));
	encoder("low", () => ({ chunks: ["\udfff"] }));
	encoder("high-high-low", () => ({ chunks: [
		"\ud800",
		"\ud800",
		"\udc00"
	] }));
	encoder("mixed", () => ({ chunks: [
		"a\ud800b\udc00c",
		"\udbff",
		"\udfffz"
	] }));
	encoder("scalars", () => ({ chunks: [
		void 0,
		null,
		true,
		42,
		2n,
		Symbol("s")
	] }));
	encoder("coercion", (trace) => ({ chunks: [{
		toString() {
			trace.push("toString");
			return "abc";
		},
		valueOf() {
			trace.push("valueOf");
			return 1;
		}
	}] }));
	encoder("throwing-coercion", (trace) => ({ chunks: ["\ud800", { toString() {
		trace.push("toString");
		throw Error("sentinel");
	} }] }));
	const seeds = [
		[],
		[97],
		[194, 162],
		[
			226,
			130,
			172
		],
		[
			240,
			159,
			140,
			141
		],
		[
			239,
			187,
			191,
			97
		],
		[192, 128],
		[
			237,
			160,
			128
		],
		[
			240,
			143,
			128,
			128
		],
		[
			244,
			144,
			128,
			128
		],
		[226, 130],
		[255, 97],
		[
			240,
			159,
			140,
			141,
			239,
			187,
			191
		]
	];
	for (let index = 0; index < seeds.length; index++) {
		const bytes = seeds[index];
		for (let mask = 0; mask < 2 ** Math.max(0, bytes.length - 1); mask++) {
			const chunks = [];
			let start = 0;
			for (let cursor = 1; cursor <= bytes.length; cursor++) if (cursor === bytes.length || mask & 2 ** (cursor - 1)) {
				chunks.push(bytes.slice(start, cursor));
				start = cursor;
			}
			for (const fatal of [false, true]) decoder("split-" + index + "-" + mask + "-" + fatal, chunks, { fatal });
		}
	}
	decoder("bom-preserved", [[239], [
		187,
		191,
		97
	]], { ignoreBOM: true });
	decoder("bom-removed", [[239], [
		187,
		191,
		97
	]], { ignoreBOM: false });
	values.push({
		name: "decoder:arraybuffer-offset",
		kind: "decoder",
		make: () => ({ chunks: [new DataView(Uint8Array.of(0, 97, 98, 0).buffer, 1, 2), Uint8Array.of(99).buffer] })
	});
	values.push({
		name: "decoder:shadowed-fields",
		kind: "decoder",
		make: () => {
			const input = Uint8Array.of(97);
			for (const key of [
				"buffer",
				"byteOffset",
				"byteLength"
			]) Object.defineProperty(input, key, { get() {
				throw Error("sentinel");
			} });
			return { chunks: [input] };
		}
	});
	for (const value of [
		void 0,
		null,
		1,
		"abc",
		{}
	]) values.push({
		name: "decoder:invalid-" + String(value),
		kind: "decoder",
		make: () => ({ chunks: [value] })
	});
	return values;
}
async function codecCases(web) {
	const cases = [];
	for (const definition of definitions()) {
		const trace = [], spec = definition.make(trace), Ctor = definition.kind === "encoder" ? web.TextEncoderStream : web.TextDecoderStream;
		try {
			const instance = definition.kind === "encoder" ? new Ctor() : new Ctor("utf-8", spec.options);
			cases.push({
				name: definition.name,
				trace,
				result: await pipeline(instance, spec.chunks)
			});
		} catch (error) {
			cases.push({
				name: definition.name,
				trace,
				error: errorValue$2(error)
			});
		}
	}
	return cases;
}
async function cancellationCases(web) {
	const cases = [];
	for (const name of ["TextEncoderStream", "TextDecoderStream"]) for (const operation of ["cancel-readable", "abort-writable"]) {
		const instance = new web[name](), reader = instance.readable.getReader(), writer = instance.writable.getWriter(), reason = { reason: operation };
		const closed = writer.closed.then(() => false, (error) => error === reason), readClosed = reader.closed.then(() => true, (error) => error === reason);
		if (operation === "cancel-readable") {
			const pending = writer.write(name === "TextEncoderStream" ? "a" : Uint8Array.of(97)).then(() => false, (error) => error === reason);
			await reader.cancel(reason);
			cases.push({
				name: name + ":" + operation,
				pendingRejected: await pending,
				writerRejected: await closed,
				readerClosed: await readClosed
			});
		} else {
			const pending = reader.read().then(() => false, (error) => error === reason);
			await writer.abort(reason);
			cases.push({
				name: name + ":" + operation,
				pendingRejected: await pending,
				writerRejected: await closed,
				readerClosed: await readClosed
			});
		}
		writer.releaseLock();
		reader.releaseLock();
	}
	return cases;
}
function constructorCases(web) {
	const cases = [];
	const probe = (name, callback) => {
		const trace = [];
		try {
			cases.push({
				name,
				trace,
				value: callback(trace)
			});
		} catch (error) {
			cases.push({
				name,
				trace,
				error: errorValue$2(error)
			});
		}
	};
	for (const name of ["TextEncoderStream", "TextDecoderStream"]) {
		const Ctor = web[name], value = new Ctor();
		cases.push({
			name: name + ":shape",
			value: {
				name: Ctor.name,
				length: Ctor.length,
				prototypeNames: Object.getOwnPropertyNames(Ctor.prototype),
				enumerable: Object.keys(Ctor.prototype),
				ownNames: Object.getOwnPropertyNames(value),
				tag: Object.prototype.toString.call(value),
				encoding: value.encoding
			}
		});
		probe(name + ":plain", () => Ctor());
		for (const key of Object.getOwnPropertyNames(Ctor.prototype)) if (key !== "constructor") {
			const getter = Object.getOwnPropertyDescriptor(Ctor.prototype, key).get;
			for (const receiver of [
				void 0,
				{},
				Object.create(Ctor.prototype)
			]) probe(name + ":brand:" + key + ":" + String(receiver), () => getter.call(receiver));
		}
	}
	for (const label of [
		"utf-8",
		"UTF8",
		" unicode-1-1-utf-8 ",
		"	utf-8\r",
		{},
		Symbol("s"),
		"rot13"
	]) probe("label:" + String(label), () => new web.TextDecoderStream(label).encoding);
	probe("label-coercion", (trace) => new web.TextDecoderStream({ toString() {
		trace.push("label");
		return "utf8";
	} }).encoding);
	probe("options-order", (trace) => {
		const value = new web.TextDecoderStream("utf8", {
			get fatal() {
				trace.push("fatal");
				return false;
			},
			get ignoreBOM() {
				trace.push("ignoreBOM");
				return true;
			}
		});
		return {
			encoding: value.encoding,
			fatal: value.fatal,
			ignoreBOM: value.ignoreBOM
		};
	});
	probe("flags-first-vs-public-second", (trace) => {
		let f = 0, b = 0;
		const value = new web.TextDecoderStream("utf8", {
			get fatal() {
				trace.push("fatal");
				return ++f === 1;
			},
			get ignoreBOM() {
				trace.push("ignoreBOM");
				return ++b === 1;
			}
		});
		return {
			fatal: value.fatal,
			ignoreBOM: value.ignoreBOM
		};
	});
	probe("unknown-label-before-options", (trace) => new web.TextDecoderStream("rot13", { get fatal() {
		trace.push("fatal");
		throw Error("sentinel");
	} }));
	probe("invalid-options-before-label", () => new web.TextDecoderStream("rot13", 1));
	probe("throwing-options", (trace) => new web.TextDecoderStream("utf8", { get fatal() {
		trace.push("fatal");
		throw Error("sentinel");
	} }));
	return cases;
}
// tests/node-compat/foundation-stream-web/candidate/guard-cases.mjs
async function guardCases(web, track = (reader) => reader) {
	const { ReadableStream, ReadableStreamBYOBReader } = web;
	const definitions = [
		["default", () => ({})],
		["null-options", () => ({ options: null })],
		["array-options", () => ({ options: [] })],
		["function-options", () => ({ options: function() {} })],
		["number-options", () => ({ options: 1 })],
		["min-one", () => ({ options: { min: 1 } })],
		["min-two", () => ({ options: { min: 2 } })],
		["min-null", () => ({ options: { min: null } })],
		["min-string", () => ({ options: { min: "1" } })],
		["min-fraction", () => ({ options: { min: 1.5 } })],
		["min-zero", () => ({ options: { min: 0 } })],
		["min-nan", () => ({ options: { min: NaN } })],
		["min-infinity", () => ({ options: { min: Infinity } })],
		["min-too-large", () => ({ options: { min: 5 } })],
		["min-getter", (trace) => ({ options: { get min() {
			trace.push("min");
			return 1;
		} } })],
		["throwing-min", (trace) => ({ options: { get min() {
			trace.push("min");
			throw Error("sentinel");
		} } })],
		["invalid-receiver-first", (trace) => ({
			receiver: {},
			view: {},
			options: { get min() {
				trace.push("min");
				throw Error("sentinel");
			} }
		})],
		["spoof-receiver-first", (trace) => ({
			receiver: Object.create(ReadableStreamBYOBReader.prototype),
			view: {},
			options: { get min() {
				trace.push("min");
				throw Error("sentinel");
			} }
		})],
		["proxy-genuine-receiver", (_trace, reader) => ({ receiver: new Proxy(reader, {}) })],
		["invalid-view-before-options", (trace) => ({
			view: {},
			options: { get min() {
				trace.push("min");
				throw Error("sentinel");
			} }
		})],
		["arraybuffer-view-rejected", () => ({ view: /* @__PURE__ */ new ArrayBuffer(4) })],
		["zero-view-before-min", (trace) => ({
			view: /* @__PURE__ */ new Uint8Array(0),
			options: { get min() {
				trace.push("min");
				throw Error("sentinel");
			} }
		})],
		["zero-view-invalid-options", () => ({
			view: /* @__PURE__ */ new Uint8Array(0),
			options: 1
		})],
		["shadowed-view-fields", (trace) => {
			const view = /* @__PURE__ */ new Uint8Array(4);
			for (const key of [
				"buffer",
				"byteLength",
				"length"
			]) Object.defineProperty(view, key, { get() {
				trace.push(key);
				throw Error("sentinel");
			} });
			return {
				view,
				options: { min: 1 }
			};
		}]
	];
	const cases = [];
	for (const [name, make] of definitions) {
		const trace = [], reader = track(new ReadableStream({
			type: "bytes",
			start(controller) {
				controller.enqueue(Uint8Array.of(9, 10));
				controller.close();
			}
		}).getReader({ mode: "byob" }));
		const state = make(trace, reader), view = state.view ?? /* @__PURE__ */ new Uint8Array(4), receiver = Object.hasOwn(state, "receiver") ? state.receiver : reader;
		const result = {
			name,
			trace
		};
		try {
			const value = await ReadableStreamBYOBReader.prototype.read.call(receiver, view, state.options);
			result.value = {
				done: value.done,
				bytes: [...value.value]
			};
		} catch (error) {
			result.error = { name: error.name };
			if (error.code !== void 0) result.error.code = error.code;
			result.error.sentinel = error.message === "sentinel";
		}
		await reader.cancel();
		await reader.closed;
		reader.releaseLock();
		cases.push(result);
	}
	return cases;
}
// tests/node-compat/foundation-stream-web/candidate/typed-view-cases.mjs
async function typedViewCases(web, track = (reader) => reader) {
	const results = [];
	for (const Type of [
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
		BigUint64Array,
		DataView
	]) {
		const source = new web.ReadableStream({
			type: "bytes",
			start(controller) {
				const bytes = /* @__PURE__ */ new Uint8Array(16);
				for (let i = 0; i < bytes.length; i++) bytes[i] = i;
				controller.enqueue(bytes);
				controller.close();
			}
		});
		const buffer = /* @__PURE__ */ new ArrayBuffer(32), view = Type === DataView ? new Type(buffer, 8, 16) : new Type(buffer, 8, 16 / Type.BYTES_PER_ELEMENT);
		const reader = track(source.getReader({ mode: "byob" }));
		const closed = reader.closed.catch(() => {});
		try {
			const result = await reader.read(view, { min: 1 }), value = result.value;
			results.push({
				name: Type.name,
				bytes: [...new Uint8Array(value.buffer, value.byteOffset, value.byteLength)],
				returnedType: value.constructor.name,
				prototypeIdentity: Object.getPrototypeOf(value) === Type.prototype,
				byteOffset: value.byteOffset,
				byteLength: value.byteLength,
				bufferLength: value.buffer.byteLength,
				oldBufferLength: buffer.byteLength,
				separateBuffer: value.buffer !== buffer,
				done: result.done
			});
		} catch (error) {
			const item = {
				name: Type.name,
				error: {
					name: error.name,
					code: error.code
				},
				oldBufferLength: buffer.byteLength
			};
			if (error.code === "ERR_SM_NODE_UNSUPPORTED") item.recovery = [...(await reader.read(/* @__PURE__ */ new Uint8Array(16))).value];
			results.push(item);
		}
		await reader.cancel();
		await closed;
		reader.releaseLock();
	}
	return results;
}
// tests/node-compat/foundation-stream-web/candidate/controller-cases.mjs
async function controllerCases(web) {
	const prototype = web.TransformStreamDefaultController.prototype, cases = [];
	for (const name of [
		"desiredSize",
		"enqueue",
		"error",
		"terminate"
	]) {
		const entry = Object.getOwnPropertyDescriptor(prototype, name), method = entry.get ?? entry.value;
		try {
			method.call(prototype);
			cases.push({
				name,
				returned: true
			});
		} catch (error) {
			cases.push({
				name,
				error: errorValue$2(error)
			});
		}
	}
	let closedController;
	const closed = new web.TransformStream({ start(controller) {
		closedController = controller;
	} });
	const cw = closed.writable.getWriter(), cr = closed.readable.getReader(), closing = cw.close();
	await cr.read();
	await closing;
	await cw.closed;
	await cr.closed;
	cases.push({
		name: "closed-controller",
		desiredSize: closedController.desiredSize
	});
	cw.releaseLock();
	cr.releaseLock();
	let erroredController;
	const errored = new web.TransformStream({ start(controller) {
		erroredController = controller;
	} });
	const ew = errored.writable.getWriter(), er = errored.readable.getReader(), reason = { reason: "error" };
	const wc = ew.closed.then(() => false, (error) => error === reason), rc = er.closed.then(() => false, (error) => error === reason);
	erroredController.error(reason);
	cases.push({
		name: "errored-controller",
		desiredSize: erroredController.desiredSize,
		writerReason: await wc,
		readerReason: await rc
	});
	ew.releaseLock();
	er.releaseLock();
	return cases;
}
// tests/node-compat/foundation-stream-web/production-candidate/native-policies.mjs
const MAX_SOURCE_UNITS = 1048576;
const MAX_INPUT_BYTES = 16777216;
function ensure$3(value, message) {
	if (!value) throw Error(message);
}
async function guardRejection(module, track, view, options) {
	const reader = track(new module.ReadableStream({
		type: "bytes",
		start(controller) {
			controller.enqueue(Uint8Array.of(9, 10));
			controller.close();
		}
	}).getReader({ mode: "byob" }));
	let error;
	try {
		await reader.read(view, options);
	} catch (caught) {
		error = caught;
	}
	await reader.cancel();
	await reader.closed;
	reader.releaseLock();
	return error;
}
async function policyCases$1(module, fixture) {
	const checks = [];
	for (const label of [
		"utf-16le",
		"utf-16be",
		"windows-1252",
		"shift_jis"
	]) {
		let error;
		try {
			new module.TextDecoderStream(label);
		} catch (caught) {
			error = caught;
		}
		ensure$3(error?.code === "ERR_SM_NODE_UNSUPPORTED", "known label must fail " + label);
		checks.push("deferred-label:" + label);
	}
	ensure$3((await pipeline(new module.TextEncoderStream(), ["a".repeat(1048577)])).writes[0]?.error?.code === "ERR_SM_NODE_LIMIT", "encoder source cap");
	checks.push("encoder-over-limit");
	const encoderEdge = await pipeline(new module.TextEncoderStream(), ["a".repeat(MAX_SOURCE_UNITS)]);
	ensure$3(encoderEdge.outputs[0]?.byteLength === MAX_SOURCE_UNITS && encoderEdge.close.fulfilled, "encoder accepted boundary");
	checks.push("encoder-at-limit");
	ensure$3((await pipeline(new module.TextDecoderStream(), [/* @__PURE__ */ new Uint8Array(16777217)])).writes[0]?.error?.code === "ERR_SM_NODE_LIMIT", "decoder byte cap");
	checks.push("decoder-over-limit");
	const decoderEdgeInput = new Uint8Array(MAX_INPUT_BYTES);
	decoderEdgeInput.fill(97);
	const decoderEdge = await pipeline(new module.TextDecoderStream(), [decoderEdgeInput]);
	ensure$3(decoderEdge.outputs[0]?.stringLength === MAX_INPUT_BYTES && decoderEdge.outputs[0].first === "a" && decoderEdge.outputs[0].last === "a" && decoderEdge.close.fulfilled, "decoder accepted boundary");
	checks.push("decoder-at-limit");
	const resizableDecoder = new ArrayBuffer(4, { maxByteLength: 8 });
	ensure$3((await pipeline(new module.TextDecoderStream(), [new Uint8Array(resizableDecoder)])).writes[0]?.error?.code === "ERR_SM_NODE_UNSUPPORTED", "decoder RAB policy");
	checks.push("decoder-resizable");
	const detachedDecoder = /* @__PURE__ */ new Uint8Array(4);
	detachedDecoder.buffer.transfer();
	ensure$3((await pipeline(new module.TextDecoderStream(), [detachedDecoder])).writes[0]?.error?.code === "ERR_SM_NODE_UNSUPPORTED", "decoder detached policy");
	checks.push("decoder-detached");
	ensure$3((await guardRejection(module, fixture.track, /* @__PURE__ */ new Uint8Array(16777217)))?.code === "ERR_SM_NODE_LIMIT", "BYOB byte cap");
	checks.push("byob-over-limit");
	const resizable = new ArrayBuffer(4, { maxByteLength: 8 });
	ensure$3((await guardRejection(module, fixture.track, new Uint8Array(resizable)))?.code === "ERR_SM_NODE_UNSUPPORTED", "BYOB RAB policy");
	checks.push("byob-resizable");
	class Subclass extends Uint8Array {}
	ensure$3((await guardRejection(module, fixture.track, new Subclass(4)))?.code === "ERR_SM_NODE_UNSUPPORTED", "BYOB subclass policy");
	checks.push("byob-subclass");
	const source = new module.ReadableStream({
		type: "bytes",
		start(controller) {
			controller.enqueue(Uint8Array.of(9, 10));
			controller.close();
		}
	});
	const reader = fixture.track(new module.ReadableStreamBYOBReader(source)), view = /* @__PURE__ */ new Uint8Array(4);
	let minError;
	try {
		await reader.read(view, { min: 2 });
	} catch (error) {
		minError = error;
	}
	ensure$3(minError?.code === "ERR_SM_NODE_UNSUPPORTED" && view.byteLength === 4, "unsupported min must not detach/consume");
	const recovery = await reader.read(/* @__PURE__ */ new Uint8Array(4));
	ensure$3(JSON.stringify([...recovery.value]) === "[9,10]", "unsupported min preserves source queue");
	await reader.closed;
	reader.releaseLock();
	checks.push("byob-minimum-no-operation-and-recovery");
	const shared = {
		available: typeof SharedArrayBuffer === "function",
		checks: 0
	};
	if (shared.available) for (const input of [new SharedArrayBuffer(1), new Uint8Array(new SharedArrayBuffer(1))]) {
		ensure$3((await pipeline(new module.TextDecoderStream(), [input])).writes[0]?.error?.code === "ERR_SM_NODE_UNSUPPORTED", "shared decoder policy");
		shared.checks++;
	}
	return {
		checks,
		shared,
		limits: {
			sourceUnits: MAX_SOURCE_UNITS,
			inputBytes: MAX_INPUT_BYTES
		},
		ordinaryNativeBrandProof: false
	};
}
async function primordialCases(module, record) {
	const saved = {
		String,
		Error,
		TypeError,
		RangeError,
		apply: Reflect.apply,
		integer: Number.isInteger,
		isView: ArrayBuffer.isView,
		get: WeakMap.prototype.get,
		set: WeakMap.prototype.set,
		charCodeAt: String.prototype.charCodeAt,
		slice: String.prototype.slice,
		encode: record.TextEncoder.prototype.encode,
		decode: record.TextDecoder.prototype.decode,
		enqueue: record.TransformStreamDefaultController.prototype.enqueue,
		terminate: record.TransformStreamDefaultController.prototype.terminate,
		readable: Object.getOwnPropertyDescriptor(record.TransformStream.prototype, "readable"),
		writable: Object.getOwnPropertyDescriptor(record.TransformStream.prototype, "writable")
	};
	let invoked = 0;
	function replaced() {
		invoked++;
		throw new saved.Error("replaced intrinsic");
	}
	let encoded, decoded, error;
	try {
		globalThis.String = globalThis.Error = globalThis.TypeError = globalThis.RangeError = replaced;
		Reflect.apply = Number.isInteger = ArrayBuffer.isView = replaced;
		WeakMap.prototype.get = WeakMap.prototype.set = replaced;
		saved.String.prototype.charCodeAt = saved.String.prototype.slice = replaced;
		record.TextEncoder.prototype.encode = record.TextDecoder.prototype.decode = replaced;
		record.TransformStreamDefaultController.prototype.enqueue = record.TransformStreamDefaultController.prototype.terminate = replaced;
		Object.defineProperty(record.TransformStream.prototype, "readable", {
			get: replaced,
			configurable: true
		});
		Object.defineProperty(record.TransformStream.prototype, "writable", {
			get: replaced,
			configurable: true
		});
		encoded = await pipeline(new module.TextEncoderStream(), ["\ud83c", "\udf0d"]);
		decoded = await pipeline(new module.TextDecoderStream(), [Uint8Array.of(226), Uint8Array.of(130, 172)]);
		try {
			new module.CompressionStream();
		} catch (caught) {
			error = caught;
		}
	} finally {
		globalThis.String = saved.String;
		globalThis.Error = saved.Error;
		globalThis.TypeError = saved.TypeError;
		globalThis.RangeError = saved.RangeError;
		Reflect.apply = saved.apply;
		Number.isInteger = saved.integer;
		ArrayBuffer.isView = saved.isView;
		WeakMap.prototype.get = saved.get;
		WeakMap.prototype.set = saved.set;
		saved.String.prototype.charCodeAt = saved.charCodeAt;
		saved.String.prototype.slice = saved.slice;
		record.TextEncoder.prototype.encode = saved.encode;
		record.TextDecoder.prototype.decode = saved.decode;
		record.TransformStreamDefaultController.prototype.enqueue = saved.enqueue;
		record.TransformStreamDefaultController.prototype.terminate = saved.terminate;
		Object.defineProperty(record.TransformStream.prototype, "readable", saved.readable);
		Object.defineProperty(record.TransformStream.prototype, "writable", saved.writable);
	}
	ensure$3(invoked === 0, "replaced producer/intrinsic executed");
	ensure$3(JSON.stringify(encoded.outputs) === "[[240,159,140,141]]" && encoded.close.fulfilled, "captured encoder");
	ensure$3(JSON.stringify(decoded.outputs) === "[\"€\"]" && decoded.close.fulfilled, "captured decoder");
	ensure$3(error?.code === "ERR_SM_NODE_UNSUPPORTED", "captured error constructor");
	return {
		replacementInvocations: invoked,
		encoder: true,
		decoder: true,
		error: errorValue$2(error)
	};
}
// tests/node-compat/foundation-stream-web/iteration/cases.mjs
function errorValue$1(error) {
	return {
		name: error?.name,
		...error?.code !== void 0 ? { code: error.code } : {}
	};
}
async function outcome$1(invoke) {
	try {
		return { value: await invoke() };
	} catch (error) {
		return { error: errorValue$1(error) };
	}
}
async function consume$1(stream) {
	const reader = stream.getReader(), values = [];
	try {
		for (;;) {
			const entry = await reader.read();
			if (entry.done) break;
			values.push(entry.value);
		}
	} finally {
		reader.releaseLock();
	}
	return values;
}
async function iterationCases(web) {
	const S = web.ReadableStream, cases = [];
	async function test(name, run) {
		cases.push({
			name,
			...await outcome$1(run)
		});
	}
	await test("from-array", () => consume$1(S.from([
		1,
		2,
		3
	])));
	await test("from-string-unicode", () => consume$1(S.from("A🌍é")));
	await test("from-sync-generator", () => consume$1(S.from((function* () {
		yield 1;
		yield 2;
		return 99;
	})())));
	await test("from-async-generator", () => consume$1(S.from((async function* () {
		yield 1;
		await 0;
		yield 2;
	})())));
	await test("from-sync-promised-value", () => consume$1(S.from([Promise.resolve(7)])));
	await test("from-async-promised-value", async () => {
		const reader = S.from({ [Symbol.asyncIterator]() {
			return { next() {
				return Promise.resolve({
					done: false,
					value: Promise.resolve(8)
				});
			} };
		} }).getReader(), entry = await reader.read();
		const promised = typeof entry.value?.then === "function";
		const value = await entry.value;
		await reader.cancel();
		reader.releaseLock();
		return {
			promised,
			value
		};
	});
	for (const [name, value] of [
		["null", null],
		["undefined", void 0],
		["plain", {}],
		["number", 1],
		["sync-null", { [Symbol.iterator]: null }],
		["async-number", { [Symbol.asyncIterator]: 1 }],
		["iterator-number", { [Symbol.iterator]() {
			return 1;
		} }],
		["iterator-function", { [Symbol.asyncIterator]() {
			return function f() {};
		} }]
	]) await test("from-invalid-" + name, () => S.from(value));
	await test("from-async-next-number", () => consume$1(S.from({ [Symbol.asyncIterator]() {
		return { next() {
			return 1;
		} };
	} })));
	await test("from-async-next-promised-number", () => consume$1(S.from({ [Symbol.asyncIterator]() {
		return { next() {
			return Promise.resolve(1);
		} };
	} })));
	await test("from-sync-next-number", () => consume$1(S.from({ [Symbol.iterator]() {
		return { next() {
			return 1;
		} };
	} })));
	await test("from-throwing-next", async () => {
		const reason = { tag: "next" }, source = S.from({ [Symbol.asyncIterator]() {
			return { next() {
				throw reason;
			} };
		} }), reader = source.getReader();
		const handled = reader.closed.catch((error) => error === reason);
		let same = false;
		try {
			await reader.read();
		} catch (error) {
			same = error === reason;
		}
		await handled;
		reader.releaseLock();
		return {
			same,
			locked: source.locked
		};
	});
	await test("from-no-eager-pull", async () => {
		const trace = [];
		let index = 0;
		const stream = S.from({ [Symbol.asyncIterator]() {
			trace.push("iterator");
			return {
				next() {
					trace.push("next");
					return Promise.resolve(index++ ? { done: true } : {
						value: 3,
						done: false
					});
				},
				return(reason) {
					trace.push("return:" + reason);
					return { done: true };
				}
			};
		} });
		await Promise.resolve();
		await Promise.resolve();
		const before = trace.slice(), reader = stream.getReader();
		const first = await reader.read();
		await Promise.resolve();
		const after = trace.slice();
		await reader.cancel("stop");
		reader.releaseLock();
		return {
			before,
			first,
			after,
			trace
		};
	});
	await test("from-next-captured", async () => {
		let gets = 0, index = 0;
		const iterator = { get next() {
			gets++;
			return function() {
				return index++ ? { done: true } : {
					value: 9,
					done: false
				};
			};
		} };
		const stream = S.from({ [Symbol.asyncIterator]() {
			return iterator;
		} });
		Object.defineProperty(iterator, "next", { value() {
			throw Error("changed");
		} });
		return {
			values: await consume$1(stream),
			gets
		};
	});
	await test("from-sync-next-get-order", async () => {
		let gets = 0, index = 0;
		const trace = [];
		const stream = S.from({ [Symbol.iterator]() {
			trace.push("iterator");
			return { get next() {
				trace.push("next-get");
				gets++;
				return function() {
					return index++ ? { done: true } : {
						value: 9,
						done: false
					};
				};
			} };
		} });
		const before = trace.slice(), values = await consume$1(stream);
		return {
			before,
			trace,
			gets,
			values
		};
	});
	for (const [name, result] of [
		["number", 1],
		["null", null],
		["undefined", void 0],
		["object", { done: true }],
		["promise-object", Promise.resolve({ done: true })]
	]) await test("from-cancel-return-" + name, async () => {
		const reason = { why: 1 };
		let same = false;
		const stream = S.from({ [Symbol.asyncIterator]() {
			return {
				next() {
					return {
						value: 1,
						done: false
					};
				},
				return(value) {
					same = value === reason;
					return result;
				}
			};
		} });
		const reader = stream.getReader();
		await reader.read();
		const cancelled = await outcome$1(() => reader.cancel(reason));
		reader.releaseLock();
		return {
			same,
			cancelled,
			locked: stream.locked
		};
	});
	await test("from-cancel-return-rejection", async () => {
		const reason = { why: 2 }, stream = S.from({ [Symbol.asyncIterator]() {
			return {
				next() {
					return {
						value: 1,
						done: false
					};
				},
				return() {
					return Promise.reject(reason);
				}
			};
		} });
		const reader = stream.getReader();
		await reader.read();
		let same = false;
		try {
			await reader.cancel();
		} catch (error) {
			same = error === reason;
		}
		reader.releaseLock();
		return {
			same,
			locked: stream.locked
		};
	});
	await test("from-static-this-ignored", () => consume$1(S.from.call(null, [4])));
	await test("from-async-method-precedence", async () => {
		const trace = [];
		let done = false;
		return {
			trace,
			values: await consume$1(S.from({
				get [Symbol.iterator]() {
					trace.push("sync");
					throw Error("wrong");
				},
				[Symbol.asyncIterator]() {
					trace.push("async");
					return { next() {
						if (done) return { done: true };
						done = true;
						return {
							value: 5,
							done: false
						};
					} };
				}
			}))
		};
	});
	await test("from-null-async-fallback", () => consume$1(S.from({
		[Symbol.asyncIterator]: null,
		*[Symbol.iterator]() {
			yield 6;
		}
	})));
	await test("from-sync-generator-cancel-finally", async () => {
		const trace = [];
		const reader = S.from((function* () {
			try {
				yield 1;
				yield 2;
			} finally {
				trace.push("finally");
			}
		})()).getReader(), first = await reader.read();
		await reader.cancel("done");
		reader.releaseLock();
		return {
			first,
			trace
		};
	});
	await test("from-serial-pulls", async () => {
		let finish, index = 0, active = 0, maxActive = 0;
		const trace = [];
		const reader = S.from({ [Symbol.asyncIterator]() {
			return { next() {
				active++;
				maxActive = Math.max(maxActive, active);
				trace.push("next:" + index);
				if (index++ === 0) return new Promise((resolve) => {
					finish = () => {
						active--;
						resolve({
							value: 1,
							done: false
						});
					};
				});
				active--;
				return { done: true };
			} };
		} }).getReader();
		const first = reader.read(), second = reader.read();
		await Promise.resolve();
		await Promise.resolve();
		const before = trace.slice();
		finish();
		const results = await Promise.all([first, second]);
		reader.releaseLock();
		return {
			before,
			trace,
			results,
			maxActive
		};
	});
	for (const field of ["done", "value"]) await test("from-throwing-result-" + field, async () => {
		const reason = {}, entry = {
			done: false,
			value: 1
		};
		Object.defineProperty(entry, field, { get() {
			throw reason;
		} });
		const stream = S.from({ [Symbol.asyncIterator]() {
			return { next() {
				return entry;
			} };
		} }), reader = stream.getReader();
		let same = false;
		try {
			await reader.read();
		} catch (error) {
			same = error === reason;
		}
		reader.releaseLock();
		return {
			same,
			locked: stream.locked
		};
	});
	await test("from-throwing-return-getter", async () => {
		const reason = {}, reader = S.from({ [Symbol.asyncIterator]() {
			return {
				next() {
					return { value: 1 };
				},
				get return() {
					throw reason;
				}
			};
		} }).getReader();
		await reader.read();
		let same = false;
		try {
			await reader.cancel();
		} catch (error) {
			same = error === reason;
		}
		reader.releaseLock();
		return { same };
	});
	await test("from-new-rejected", () => new S.from([]));
	for (const [name, options] of [
		["undefined", void 0],
		["null", null],
		["false", false],
		["zero", 0],
		["string", "x"],
		["array", []],
		["function", () => {}]
	]) await test("values-options-" + name, async () => {
		const stream = new S({ start(c) {
			c.close();
		} });
		return {
			first: await stream.values(options).next(),
			locked: stream.locked
		};
	});
	await test("values-invalid-receiver-before-options", () => {
		let reads = 0;
		try {
			S.prototype.values.call({}, { get preventCancel() {
				reads++;
				throw Error();
			} });
		} catch (error) {
			return {
				error: errorValue$1(error),
				reads
			};
		}
	});
	await test("values-prototype-rejected", () => S.prototype.values.call(S.prototype));
	await test("values-locked-after-getter", async () => {
		const stream = new S(), reader = stream.getReader(), trace = [];
		const result = await outcome$1(() => stream.values({ get preventCancel() {
			trace.push("get");
			return false;
		} }));
		reader.releaseLock();
		await stream.cancel();
		return {
			result,
			trace
		};
	});
	await test("values-throwing-options-unlocked", async () => {
		const reason = {}, stream = new S();
		let same = false;
		try {
			stream.values({ get preventCancel() {
				throw reason;
			} });
		} catch (error) {
			same = error === reason;
		}
		const locked = stream.locked;
		await stream.cancel();
		return {
			same,
			locked
		};
	});
	await test("values-close-and-next", async () => {
		const stream = new S({ start(c) {
			c.enqueue(1);
			c.close();
		} }), iterator = stream.values();
		const lockedBefore = stream.locked, one = await iterator.next(), two = await iterator.next();
		return {
			lockedBefore,
			one,
			two,
			three: await iterator.next(),
			closedKeys: Object.keys(two),
			lockedAfter: stream.locked,
			returned: await iterator.return("after")
		};
	});
	await test("values-three-concurrent-next", async () => {
		const stream = new S({ start(c) {
			c.enqueue(1);
			c.enqueue(2);
			c.close();
		} }), iterator = stream.values();
		return {
			results: await Promise.all([
				iterator.next(),
				iterator.next(),
				iterator.next()
			]),
			locked: stream.locked
		};
	});
	await test("values-pending-next-return-serialized", async () => {
		let control;
		const trace = [], stream = new S({
			start(c) {
				control = c;
			},
			cancel(reason) {
				trace.push("cancel:" + reason);
			}
		}), iterator = stream.values();
		const first = iterator.next().then((value) => {
			trace.push("next");
			return value;
		}), last = iterator.return("stop").then((value) => {
			trace.push("return");
			return value;
		});
		await Promise.resolve();
		await Promise.resolve();
		const before = trace.slice();
		control.enqueue(7);
		return {
			before,
			results: await Promise.all([first, last]),
			trace,
			locked: stream.locked
		};
	});
	for (const preventCancel of [
		false,
		true,
		"yes",
		0
	]) await test("values-return-prevent-" + String(preventCancel), async () => {
		const reasons = [], stream = new S({
			start(c) {
				c.enqueue(1);
				c.enqueue(2);
			},
			cancel(reason) {
				reasons.push(reason);
			}
		}), iterator = stream.values({ preventCancel });
		const first = await iterator.next(), returned = await iterator.return("stop"), again = await iterator.next();
		const locked = stream.locked, reader = stream.getReader(), remaining = preventCancel ? (await reader.read()).value : null;
		await reader.cancel();
		reader.releaseLock();
		return {
			first,
			returned,
			again,
			reasons: reasons.slice(0, preventCancel ? 0 : 1),
			locked,
			remaining
		};
	});
	await test("values-return-cancel-reject-unlocks", async () => {
		const reason = {}, stream = new S({ cancel() {
			return Promise.reject(reason);
		} }), iterator = stream.values();
		let same = false;
		try {
			await iterator.return("stop");
		} catch (error) {
			same = error === reason;
		}
		return {
			same,
			locked: stream.locked,
			next: await iterator.next(),
			again: await iterator.return("again")
		};
	});
	await test("values-error-unlocks-and-recovers-queue", async () => {
		const reason = {}, stream = new S({ start(c) {
			c.error(reason);
		} }), iterator = stream.values();
		let same = false;
		try {
			await iterator.next();
		} catch (error) {
			same = error === reason;
		}
		return {
			same,
			locked: stream.locked,
			next: await iterator.next(),
			returned: await iterator.return("after")
		};
	});
	await test("values-concurrent-rejection-next", async () => {
		const reason = {}, stream = new S({ start(c) {
			c.error(reason);
		} }), iterator = stream.values();
		const first = iterator.next().then(() => false, (error) => error === reason), second = iterator.next();
		return {
			first: await first,
			second: await second,
			locked: stream.locked
		};
	});
	await test("values-return-before-read", async () => {
		const trace = [], stream = new S({ cancel(reason) {
			trace.push(reason);
		} }), iterator = stream.values();
		return {
			returned: await iterator.return("early"),
			next: await iterator.next(),
			trace,
			locked: stream.locked
		};
	});
	await test("values-concurrent-returns", async () => {
		const reasons = [], stream = new S({ cancel(reason) {
			reasons.push(reason);
		} }), iterator = stream.values();
		return {
			returned: await Promise.all([
				iterator.return("first"),
				iterator.return("second"),
				iterator.next()
			]),
			reasons,
			locked: stream.locked
		};
	});
	await test("values-return-unlocks-before-cancel-fulfilled", async () => {
		let finish;
		const stream = new S({ cancel() {
			return new Promise((resolve) => {
				finish = resolve;
			});
		} }), iterator = stream.values();
		let fulfilled = false;
		const returned = iterator.return("stop").then((value) => {
			fulfilled = true;
			return value;
		});
		await Promise.resolve();
		await Promise.resolve();
		const before = {
			locked: stream.locked,
			fulfilled
		};
		finish();
		return {
			before,
			returned: await returned,
			after: fulfilled
		};
	});
	await test("values-option-read-once", async () => {
		let gets = 0;
		const stream = new S({ start(c) {
			c.close();
		} }), iterator = stream.values({ get preventCancel() {
			gets++;
			return true;
		} });
		await iterator.next();
		await iterator.return();
		return {
			gets,
			locked: stream.locked
		};
	});
	await test("values-for-await-break", async () => {
		const trace = [], stream = new S({
			start(c) {
				c.enqueue(1);
				c.enqueue(2);
			},
			cancel(reason) {
				trace.push(reason === void 0 ? "undefined" : reason);
			}
		});
		const values = [];
		for await (const value of stream) {
			values.push(value);
			break;
		}
		return {
			values,
			trace,
			locked: stream.locked
		};
	});
	await test("values-for-await-prevent-cancel", async () => {
		let cancels = 0;
		const stream = new S({
			start(c) {
				c.enqueue(1);
				c.enqueue(2);
				c.close();
			},
			cancel() {
				cancels++;
			}
		}), values = [];
		for await (const value of stream.values({ preventCancel: true })) {
			values.push(value);
			break;
		}
		return {
			values,
			rest: await consume$1(stream),
			cancels,
			locked: stream.locked
		};
	});
	await test("values-borrowed-next-return", async () => {
		const stream = new S({ start(c) {
			c.enqueue(3);
			c.close();
		} }), iterator = stream.values(), next = iterator.next, stop = iterator.return;
		return {
			first: await next.call(null),
			last: await stop.call({ x: 1 }, "stop"),
			locked: stream.locked
		};
	});
	await test("values-descriptors-and-protocol", async () => {
		const iterator = new S({ start(c) {
			c.close();
		} }).values(), proto = Object.getPrototypeOf(iterator);
		const result = {
			same: S.prototype.values === S.prototype[Symbol.asyncIterator],
			valuesLength: S.prototype.values.length,
			fromLength: S.from.length,
			nextLength: iterator.next.length,
			returnLength: iterator.return.length,
			self: iterator[Symbol.asyncIterator]() === iterator,
			throwType: typeof iterator.throw,
			protoNext: proto.next === void 0,
			protoReturn: proto.return === void 0,
			ownKeys: Object.keys(iterator),
			tag: Object.prototype.toString.call(iterator)
		};
		await iterator.return();
		return result;
	});
	await test("values-new-rejected", () => new S.prototype.values());
	await test("own-error-codes-ignore-inherited-setter", async () => {
		const define = Object.defineProperty, previous = Object.getOwnPropertyDescriptor(Error.prototype, "code");
		let gets = 0, sets = 0;
		const codes = [];
		let stream, reader;
		try {
			define(Error.prototype, "code", {
				configurable: true,
				get() {
					gets++;
					throw Error("inherited code getter");
				},
				set() {
					sets++;
					throw Error("inherited code setter");
				}
			});
			for (const invoke of [() => S.from({}), () => S.prototype.values.call({})]) try {
				invoke();
			} catch (error) {
				codes.push(Object.getOwnPropertyDescriptor(error, "code")?.value);
			}
			stream = new S();
			reader = stream.getReader();
			try {
				stream.values();
			} catch (error) {
				codes.push(Object.getOwnPropertyDescriptor(error, "code")?.value);
			}
		} finally {
			if (previous) define(Error.prototype, "code", previous);
			else delete Error.prototype.code;
			if (reader) reader.releaseLock();
			if (stream) await stream.cancel();
		}
		return {
			gets,
			sets,
			codes
		};
	});
	return cases;
}
// tests/node-compat/foundation-stream-web/iteration/intrinsics.mjs
async function capturedIntrinsicCases$1(record) {
	const P = Promise, then = P.prototype.then, resolve = P.resolve;
	const read = record.ReadableStreamDefaultReader.prototype.read, cancel = record.ReadableStreamDefaultReader.prototype.cancel;
	const release = record.ReadableStreamDefaultReader.prototype.releaseLock;
	const enqueue = record.ReadableStreamDefaultController.prototype.enqueue, close = record.ReadableStreamDefaultController.prototype.close;
	const apply = Reflect.apply, setPrototype = Object.setPrototypeOf;
	const savedGlobal = {
		Promise,
		TypeError
	};
	let replacements = 0, values = [], stopped, error;
	function replaced() {
		replacements++;
		throw Error("Replaced intrinsic invoked");
	}
	try {
		globalThis.Promise = globalThis.TypeError = replaced;
		P.resolve = replaced;
		Reflect.apply = Object.setPrototypeOf = replaced;
		record.ReadableStreamDefaultReader.prototype.read = record.ReadableStreamDefaultReader.prototype.cancel = record.ReadableStreamDefaultReader.prototype.releaseLock = replaced;
		record.ReadableStreamDefaultController.prototype.enqueue = record.ReadableStreamDefaultController.prototype.close = replaced;
		const iterator = record.ReadableStream.from([1, 2]).values();
		values.push((await iterator.next()).value);
		values.push((await iterator.next()).value);
		stopped = await iterator.return("stop");
		try {
			record.ReadableStream.prototype.values.call({});
		} catch (caught) {
			error = caught;
		}
	} finally {
		globalThis.Promise = savedGlobal.Promise;
		globalThis.TypeError = savedGlobal.TypeError;
		P.prototype.then = then;
		P.resolve = resolve;
		Reflect.apply = apply;
		Object.setPrototypeOf = setPrototype;
		record.ReadableStreamDefaultReader.prototype.read = read;
		record.ReadableStreamDefaultReader.prototype.cancel = cancel;
		record.ReadableStreamDefaultReader.prototype.releaseLock = release;
		record.ReadableStreamDefaultController.prototype.enqueue = enqueue;
		record.ReadableStreamDefaultController.prototype.close = close;
	}
	if (replacements !== 0 || JSON.stringify(values) !== "[1,2]" || !stopped?.done || stopped.value !== "stop" || error?.code !== "ERR_INVALID_THIS") throw {
		replacements,
		values,
		stopped,
		errorCode: error?.code
	};
	return {
		replacementInvocations: replacements,
		values,
		stopped,
		errorCode: error.code
	};
}
// tests/node-compat/foundation-stream-web/dataview/cases.mjs
function errorValue(error) {
	return {
		name: error?.name,
		...error?.code !== void 0 ? { code: error.code } : {}
	};
}
async function outcome(invoke) {
	try {
		return { value: await invoke() };
	} catch (error) {
		return { error: errorValue(error) };
	}
}
function describe(entry) {
	if (entry.value === void 0) return {
		done: entry.done,
		undefinedValue: true
	};
	const view = entry.value;
	return {
		done: entry.done,
		constructor: view.constructor.name,
		dataView: view instanceof DataView,
		offset: view.byteOffset,
		length: view.byteLength,
		bufferLength: view.buffer.byteLength,
		bytes: [...new Uint8Array(view.buffer, view.byteOffset, view.byteLength)]
	};
}
async function dataViewCases(web, track = (value) => value) {
	const S = web.ReadableStream, cases = [];
	async function test(name, run) {
		cases.push({
			name,
			...await outcome(run)
		});
	}
	for (const [offset, length] of [
		[0, 8],
		[4, 8],
		[8, 16]
	]) await test("queued-offset-" + offset, async () => {
		const stream = new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(2, 3, 4));
				c.close();
			}
		}), reader = track(stream.getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(32), view = new DataView(buffer, offset, length), result = await reader.read(view);
		const first = describe(result), oldBytes = buffer.byteLength, resultDistinct = result.value.buffer !== buffer;
		const last = describe(await reader.read(new DataView(/* @__PURE__ */ new ArrayBuffer(16), 2, 8)));
		await reader.closed;
		reader.releaseLock();
		return {
			first,
			last,
			oldBytes,
			resultDistinct,
			locked: stream.locked
		};
	});
	await test("closed-empty-view-result", async () => {
		const reader = track(new S({
			type: "bytes",
			start(c) {
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16);
		const result = {
			entry: describe(await reader.read(new DataView(buffer, 4, 8))),
			oldBytes: buffer.byteLength
		};
		await reader.closed;
		reader.releaseLock();
		return result;
	});
	await test("byob-request-respond", async () => {
		const trace = [];
		const reader = track(new S({
			type: "bytes",
			pull(c) {
				const request = c.byobRequest;
				trace.push({
					constructor: request.view.constructor.name,
					length: request.view.byteLength,
					offset: request.view.byteOffset
				});
				request.view.set([6, 7]);
				request.respond(2);
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(24), entry = await reader.read(new DataView(buffer, 5, 8));
		await reader.closed;
		reader.releaseLock();
		return {
			trace,
			entry: describe(entry),
			oldBytes: buffer.byteLength
		};
	});
	await test("partial-queue-remains", async () => {
		const reader = track(new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.from([
					0,
					1,
					2,
					3,
					4,
					5
				]));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const entries = [];
		for (const length of [
			2,
			8,
			8
		]) entries.push(describe(await reader.read(new DataView(/* @__PURE__ */ new ArrayBuffer(16), 3, length))));
		await reader.closed;
		reader.releaseLock();
		return entries;
	});
	await test("pending-cancel-undefined-result", async () => {
		let cancelReason;
		const reason = { tag: "cancel" }, stream = new S({
			type: "bytes",
			cancel(value) {
				cancelReason = value;
			}
		}), reader = track(stream.getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), pending = reader.read(new DataView(buffer, 4, 8));
		const detachedBeforeCancel = buffer.byteLength === 0;
		await reader.cancel(reason);
		const entry = describe(await pending);
		await reader.closed;
		reader.releaseLock();
		return {
			entry,
			detachedBeforeCancel,
			reasonSame: cancelReason === reason,
			locked: stream.locked
		};
	});
	await test("pending-error-identity", async () => {
		let control;
		const reason = {}, stream = new S({
			type: "bytes",
			start(c) {
				control = c;
			}
		}), reader = track(stream.getReader({ mode: "byob" }));
		const handled = reader.closed.catch((error) => error === reason), buffer = /* @__PURE__ */ new ArrayBuffer(16), pending = reader.read(new DataView(buffer, 2, 8));
		control.error(reason);
		let same = false;
		try {
			await pending;
		} catch (error) {
			same = error === reason;
		}
		const closedSame = await handled;
		reader.releaseLock();
		return {
			same,
			closedSame,
			oldBytes: buffer.byteLength,
			locked: stream.locked
		};
	});
	await test("already-errored-no-transfer", async () => {
		const reason = {}, stream = new S({
			type: "bytes",
			start(c) {
				c.error(reason);
			}
		}), reader = track(stream.getReader({ mode: "byob" }));
		const handled = reader.closed.catch(() => {}), buffer = /* @__PURE__ */ new ArrayBuffer(16);
		let same = false;
		try {
			await reader.read(new DataView(buffer, 3, 8));
		} catch (error) {
			same = error === reason;
		}
		await handled;
		reader.releaseLock();
		return {
			same,
			oldBytes: buffer.byteLength,
			locked: stream.locked
		};
	});
	await test("released-reader-rejects-before-transfer", async () => {
		const stream = new S({ type: "bytes" }), reader = track(stream.getReader({ mode: "byob" }));
		reader.closed.catch(() => {});
		reader.releaseLock();
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), result = await outcome(() => reader.read(new DataView(buffer, 2, 8)));
		await stream.cancel();
		return {
			result,
			oldBytes: buffer.byteLength
		};
	});
	await test("concurrent-reads", async () => {
		const reader = track(new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(1, 2, 3, 4));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffers = [
			/* @__PURE__ */ new ArrayBuffer(16),
			/* @__PURE__ */ new ArrayBuffer(16),
			/* @__PURE__ */ new ArrayBuffer(16)
		];
		const entries = await Promise.all(buffers.map((buffer) => reader.read(new DataView(buffer, 2, 2)).then(describe)));
		await reader.closed;
		reader.releaseLock();
		return {
			entries,
			oldBytes: buffers.map((buffer) => buffer.byteLength)
		};
	});
	for (const min of [
		void 0,
		null,
		1,
		0,
		-1,
		1.5,
		"1",
		9
	]) await test("min-" + String(min), async () => {
		const trace = [], reader = track(new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(1));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), result = await outcome(async () => describe(await reader.read(new DataView(buffer, 2, 8), { get min() {
			trace.push("min");
			return min;
		} })));
		await reader.cancel();
		await reader.closed;
		reader.releaseLock();
		return {
			result,
			trace,
			oldBytes: buffer.byteLength
		};
	});
	for (const length of [0]) await test("empty-view-before-min", async () => {
		let gets = 0;
		const reader = track(new S({ type: "bytes" }).getReader({ mode: "byob" })), buffer = /* @__PURE__ */ new ArrayBuffer(16);
		const result = await outcome(() => reader.read(new DataView(buffer, 2, length), { get min() {
			gets++;
			return 1;
		} }));
		await reader.cancel();
		reader.releaseLock();
		return {
			result,
			gets,
			oldBytes: buffer.byteLength
		};
	});
	await test("detached-by-min-getter", async () => {
		const reader = track(new S({ type: "bytes" }).getReader({ mode: "byob" })), buffer = /* @__PURE__ */ new ArrayBuffer(16), view = new DataView(buffer, 2, 8);
		const result = await outcome(() => reader.read(view, { get min() {
			buffer.transfer();
			return 1;
		} }));
		await reader.cancel();
		reader.releaseLock();
		return {
			result,
			oldBytes: buffer.byteLength
		};
	});
	await test("throwing-min-queue-preserved", async () => {
		const reason = {}, reader = track(new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(7, 8));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), view = new DataView(buffer, 2, 8);
		let same = false;
		try {
			await reader.read(view, { get min() {
				throw reason;
			} });
		} catch (error) {
			same = error === reason;
		}
		const before = buffer.byteLength, result = describe(await reader.read(view));
		await reader.closed;
		reader.releaseLock();
		return {
			same,
			before,
			result
		};
	});
	await test("untouched-backing-outside-view", async () => {
		const reader = track(new S({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(1, 2, 3));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(24);
		new Uint8Array(buffer).fill(165);
		const entry = await reader.read(new DataView(buffer, 5, 8));
		const result = {
			entry: describe(entry),
			allBytes: [...new Uint8Array(entry.value.buffer)],
			oldBytes: buffer.byteLength
		};
		await reader.closed;
		reader.releaseLock();
		return result;
	});
	await test("close-pending-with-zero-response", async () => {
		const reader = track(new S({
			type: "bytes",
			pull(c) {
				const request = c.byobRequest;
				c.close();
				request.respond(0);
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), entry = await reader.read(new DataView(buffer, 2, 8));
		await reader.closed;
		reader.releaseLock();
		return {
			entry: describe(entry),
			oldBytes: buffer.byteLength
		};
	});
	await test("source-type-error-identity", async () => {
		const reason = /* @__PURE__ */ new TypeError("application"), reader = track(new S({
			type: "bytes",
			start(c) {
				c.error(reason);
			}
		}).getReader({ mode: "byob" }));
		reader.closed.catch(() => {});
		let same = false;
		try {
			await reader.read(new DataView(/* @__PURE__ */ new ArrayBuffer(16), 2, 8));
		} catch (error) {
			same = error === reason;
		}
		reader.releaseLock();
		return { same };
	});
	await test("cancel-rejection-pending-result", async () => {
		const reason = {}, reader = track(new S({
			type: "bytes",
			cancel() {
				throw reason;
			}
		}).getReader({ mode: "byob" }));
		const buffer = /* @__PURE__ */ new ArrayBuffer(16), pending = reader.read(new DataView(buffer, 2, 8));
		let same = false;
		try {
			await reader.cancel();
		} catch (error) {
			same = error === reason;
		}
		const entry = describe(await pending);
		await reader.closed;
		reader.releaseLock();
		return {
			same,
			entry,
			oldBytes: buffer.byteLength
		};
	});
	return cases;
}
// tests/node-compat/foundation-stream-web/dataview/policy.mjs
function ensure$2(value, message) {
	if (!value) throw Error(message);
}
async function policyCases(web, track) {
	const checks = [];
	async function reject(name, view, options, wanted) {
		const reader = track(new web.ReadableStream({
			type: "bytes",
			start(c) {
				c.enqueue(Uint8Array.of(7, 8));
				c.close();
			}
		}).getReader({ mode: "byob" }));
		let error;
		const buffer = view.buffer, before = buffer.byteLength;
		try {
			await reader.read(view, options);
		} catch (caught) {
			error = caught;
		}
		ensure$2(error?.code === wanted, name + " error");
		ensure$2(buffer.byteLength === before, name + " input not transferred");
		const entry = await reader.read(new DataView(/* @__PURE__ */ new ArrayBuffer(8), 1, 4));
		ensure$2(JSON.stringify([...new Uint8Array(entry.value.buffer, entry.value.byteOffset, entry.value.byteLength)]) === "[7,8]", name + " queue preserved");
		await reader.closed;
		reader.releaseLock();
		checks.push(name);
	}
	await reject("min-two", new DataView(/* @__PURE__ */ new ArrayBuffer(16), 2, 8), { min: 2 }, "ERR_SM_NODE_UNSUPPORTED");
	await reject("over-limit", /* @__PURE__ */ new DataView(/* @__PURE__ */ new ArrayBuffer(16777217)), void 0, "ERR_SM_NODE_LIMIT");
	await reject("resizable", new DataView(new ArrayBuffer(8, { maxByteLength: 16 })), void 0, "ERR_SM_NODE_UNSUPPORTED");
	class Subclass extends DataView {}
	await reject("subclass", new Subclass(/* @__PURE__ */ new ArrayBuffer(8)), void 0, "ERR_SM_NODE_UNSUPPORTED");
	let layoutGets = 0;
	const shadowed = /* @__PURE__ */ new DataView(/* @__PURE__ */ new ArrayBuffer(8));
	Object.defineProperty(shadowed, "constructor", { get() {
		layoutGets++;
		throw Error();
	} });
	await reject("own-constructor", shadowed, void 0, "ERR_SM_NODE_UNSUPPORTED");
	ensure$2(layoutGets === 0, "no own layout callbacks");
	const define = Object.defineProperty, original = Object.getOwnPropertyDescriptor(Error.prototype, "code");
	let gets = 0, sets = 0;
	try {
		define(Error.prototype, "code", {
			configurable: true,
			get() {
				gets++;
				throw Error("getter");
			},
			set() {
				sets++;
				throw Error("setter");
			}
		});
		await reject("inherited-code-setter", /* @__PURE__ */ new DataView(/* @__PURE__ */ new ArrayBuffer(8)), { min: 0 }, "ERR_INVALID_ARG_VALUE");
	} finally {
		if (original) define(Error.prototype, "code", original);
		else delete Error.prototype.code;
	}
	ensure$2(gets === 0 && sets === 0, "own coded properties");
	return {
		checks,
		layoutGetterCalls: layoutGets,
		inheritedCodeGets: gets,
		inheritedCodeSets: sets
	};
}
async function capturedIntrinsicCases(web, track) {
	const DV = DataView, U8 = Uint8Array, apply = Reflect.apply, isView = ArrayBuffer.isView, isInteger = Number.isInteger;
	const oldRead = web.ReadableStreamBYOBReader.prototype.read;
	const reader = track(new web.ReadableStream({
		type: "bytes",
		start(c) {
			c.enqueue(U8.of(3, 4));
			c.close();
		}
	}).getReader({ mode: "byob" }));
	const view = new DV(/* @__PURE__ */ new ArrayBuffer(16), 3, 8);
	let replacements = 0, entry;
	function replaced() {
		replacements++;
		throw Error("replaced intrinsic");
	}
	try {
		globalThis.DataView = globalThis.Uint8Array = replaced;
		Reflect.apply = ArrayBuffer.isView = Number.isInteger = replaced;
		entry = await oldRead.call(reader, view);
	} finally {
		globalThis.DataView = DV;
		globalThis.Uint8Array = U8;
		Reflect.apply = apply;
		ArrayBuffer.isView = isView;
		Number.isInteger = isInteger;
	}
	await reader.closed;
	reader.releaseLock();
	ensure$2(replacements === 0 && entry.value instanceof DV && entry.value.byteOffset === 3 && entry.value.byteLength === 2, "captured adapter operations");
	return {
		replacementInvocations: replacements,
		bytes: [...new U8(entry.value.buffer, entry.value.byteOffset, entry.value.byteLength)]
	};
}
// tests/node-compat/foundation-stream-web/production-candidate/native-checks.mjs
function ensure$1(value, message) {
	if (!value) throw Error(message);
}
function equal(actual, wanted, name) {
	if (JSON.stringify(actual) !== JSON.stringify(wanted)) throw {
		name,
		actual,
		wanted
	};
}
async function ownErrorCases(web) {
	const define = Object.defineProperty, descriptor = Object.getOwnPropertyDescriptor, previous = {};
	let gets = 0, sets = 0;
	const fields = [
		"code",
		"module",
		"operation",
		"profile",
		"resource"
	];
	for (const field of fields) previous[field] = descriptor(Error.prototype, field);
	let count = 0;
	function check(error, code) {
		ensure$1(descriptor(error, "code")?.value === code, "own code " + code);
		count++;
	}
	try {
		for (const field of fields) define(Error.prototype, field, {
			configurable: true,
			get() {
				gets++;
				throw Error("inherited getter");
			},
			set() {
				sets++;
				throw Error("inherited setter");
			}
		});
		for (const invoke of [
			() => web.CompressionStream(),
			() => new web.CompressionStream("gzip"),
			() => web.DecompressionStream(),
			() => new web.DecompressionStream("gzip")
		]) {
			let caught;
			try {
				invoke();
			} catch (error) {
				caught = error;
			}
			check(caught, "ERR_SM_NODE_UNSUPPORTED");
			for (const field of [
				"module",
				"operation",
				"profile"
			]) ensure$1(typeof descriptor(caught, field)?.value === "string", "own metadata " + field);
		}
		for (const [label, code] of [["utf-16le", "ERR_SM_NODE_UNSUPPORTED"], ["invalid-label", "ERR_ENCODING_NOT_SUPPORTED"]]) {
			let caught;
			try {
				new web.TextDecoderStream(label);
			} catch (error) {
				caught = error;
			}
			check(caught, code);
		}
		let caught;
		try {
			web.ReadableStream.prototype.values.call({});
		} catch (error) {
			caught = error;
		}
		check(caught, "ERR_INVALID_THIS");
		ensure$1((await pipeline(new web.TextEncoderStream(), ["a".repeat(1048577)])).writes[0]?.error?.code === "ERR_SM_NODE_LIMIT", "own source-limit code");
		count++;
	} finally {
		for (const field of fields) if (previous[field]) define(Error.prototype, field, previous[field]);
		else delete Error.prototype[field];
	}
	ensure$1((await pipeline(new web.TextDecoderStream("utf-8", { fatal: true }), [Uint8Array.of(255)])).writes[0]?.error?.code === "ERR_ENCODING_INVALID_ENCODED_DATA", "normal native fatal code");
	count++;
	ensure$1(gets === 0 && sets === 0, "no inherited error metadata accessors");
	return {
		checks: count,
		inheritedGets: gets,
		inheritedSets: sets
	};
}
async function runNativeCorpus(web, expected) {
	const report = { passed: false };
	try {
		const track = (value) => value, record = {
			...web,
			TextEncoder: globalThis.TextEncoder,
			TextDecoder: globalThis.TextDecoder
		};
		const fixture = { track };
		for (const [name, invoke] of [
			["constructors", () => constructorCases(web)],
			["codecs", () => codecCases(web)],
			["cancellations", () => cancellationCases(web)]
		]) {
			const actual = await invoke();
			equal(actual, expected.codecs[name === "constructors" ? "constructorCases" : name === "codecs" ? "codecCases" : "cancellationCases"], name);
			report[name] = actual.length;
		}
		const guarded = await guardCases(web, track);
		report.guardDeviations = [];
		for (let index = 0; index < guarded.length; index++) {
			const actual = guarded[index], wanted = expected.guards.cases[index];
			const code = actual.name === "proxy-genuine-receiver" ? "ERR_INVALID_THIS" : ["min-two", "shadowed-view-fields"].includes(actual.name) ? "ERR_SM_NODE_UNSUPPORTED" : null;
			if (code) {
				ensure$1(actual.error?.code === code, "guard " + actual.name);
				report.guardDeviations.push(actual.name);
			} else equal(actual, wanted, actual.name);
		}
		report.guards = guarded.length;
		const views = await typedViewCases(web, track);
		equal(views, expected.views.cases, "all ordinary views");
		report.views = views.length;
		const controllers = await controllerCases(web);
		equal(controllers, expected.controllers.cases, "guarded controllers");
		report.controllers = controllers.length;
		const iterations = await iterationCases(web);
		equal(iterations, expected.iteration.cases, "readable iteration");
		report.iterations = iterations.length;
		const data = await dataViewCases(web, track);
		report.dataDeviations = [];
		for (let index = 0; index < data.length; index++) {
			const actual = data[index], wanted = JSON.parse(JSON.stringify(expected.data.cases[index]));
			if (actual.name === "released-reader-rejects-before-transfer" && actual.value?.result?.error?.code === void 0) {
				delete wanted.value.result.error.code;
				report.dataDeviations.push(actual.name);
			}
			equal(actual, wanted, "data " + actual.name);
		}
		report.data = data.length;
		report.policies = await policyCases$1(web, fixture);
		report.dataPolicies = await policyCases(web, track);
		report.codecIntrinsics = await primordialCases(web, record);
		report.iterationIntrinsics = await capturedIntrinsicCases$1(record);
		report.dataIntrinsics = await capturedIntrinsicCases(web, track);
		report.ownErrors = await ownErrorCases(web);
		report.privateFactoryRecordTests = "not application surface; preserved source-stage proof only (2 checks)";
		report.fixtureRegistryUsed = false;
		report.applicationFactoryUsed = false;
		report.passed = true;
	} catch (error) {
		report.failure = error?.actual !== void 0 ? error : {
			name: error?.name,
			message: error?.message,
			stack: error?.stack
		};
	}
	return report;
}
// \0node-compat:stream-web-installed-oracles
var _node_compat_stream_web_installed_oracles_default = {
	"names": [
		"ByteLengthQueuingStrategy",
		"CompressionStream",
		"CountQueuingStrategy",
		"DecompressionStream",
		"ReadableByteStreamController",
		"ReadableStream",
		"ReadableStreamBYOBReader",
		"ReadableStreamBYOBRequest",
		"ReadableStreamDefaultController",
		"ReadableStreamDefaultReader",
		"TextDecoderStream",
		"TextEncoderStream",
		"TransformStream",
		"TransformStreamDefaultController",
		"WritableStream",
		"WritableStreamDefaultController",
		"WritableStreamDefaultWriter",
		"default"
	],
	"codecs": {
		"node": "v22.14.0",
		"constructorCases": [
			{
				"name": "TextEncoderStream:shape",
				"value": {
					"name": "TextEncoderStream",
					"length": 0,
					"prototypeNames": [
						"constructor",
						"encoding",
						"readable",
						"writable"
					],
					"enumerable": [
						"encoding",
						"readable",
						"writable"
					],
					"ownNames": [],
					"tag": "[object Object]",
					"encoding": "utf-8"
				}
			},
			{
				"name": "TextEncoderStream:plain",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:encoding:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:encoding:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:encoding:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:readable:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:readable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:readable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:writable:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:writable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextEncoderStream:brand:writable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:shape",
				"value": {
					"name": "TextDecoderStream",
					"length": 0,
					"prototypeNames": [
						"constructor",
						"encoding",
						"fatal",
						"ignoreBOM",
						"readable",
						"writable"
					],
					"enumerable": [
						"encoding",
						"fatal",
						"ignoreBOM",
						"readable",
						"writable"
					],
					"ownNames": [],
					"tag": "[object Object]",
					"encoding": "utf-8"
				}
			},
			{
				"name": "TextDecoderStream:plain",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:encoding:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:encoding:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:encoding:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:fatal:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:fatal:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:fatal:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:ignoreBOM:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:ignoreBOM:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:ignoreBOM:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:readable:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:readable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:readable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:writable:undefined",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:writable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "TextDecoderStream:brand:writable:[object Object]",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "label:utf-8",
				"trace": [],
				"value": "utf-8"
			},
			{
				"name": "label:UTF8",
				"trace": [],
				"value": "utf-8"
			},
			{
				"name": "label: unicode-1-1-utf-8 ",
				"trace": [],
				"value": "utf-8"
			},
			{
				"name": "label:	utf-8\r",
				"trace": [],
				"value": "utf-8"
			},
			{
				"name": "label:[object Object]",
				"trace": [],
				"error": {
					"name": "RangeError",
					"sentinel": false,
					"code": "ERR_ENCODING_NOT_SUPPORTED"
				}
			},
			{
				"name": "label:Symbol(s)",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false
				}
			},
			{
				"name": "label:rot13",
				"trace": [],
				"error": {
					"name": "RangeError",
					"sentinel": false,
					"code": "ERR_ENCODING_NOT_SUPPORTED"
				}
			},
			{
				"name": "label-coercion",
				"trace": ["label"],
				"value": "utf-8"
			},
			{
				"name": "options-order",
				"trace": [
					"fatal",
					"ignoreBOM",
					"ignoreBOM",
					"fatal"
				],
				"value": {
					"encoding": "utf-8",
					"fatal": false,
					"ignoreBOM": true
				}
			},
			{
				"name": "flags-first-vs-public-second",
				"trace": [
					"fatal",
					"ignoreBOM",
					"ignoreBOM",
					"fatal"
				],
				"value": {
					"fatal": true,
					"ignoreBOM": true
				}
			},
			{
				"name": "unknown-label-before-options",
				"trace": [],
				"error": {
					"name": "RangeError",
					"sentinel": false,
					"code": "ERR_ENCODING_NOT_SUPPORTED"
				}
			},
			{
				"name": "invalid-options-before-label",
				"trace": [],
				"error": {
					"name": "TypeError",
					"sentinel": false,
					"code": "ERR_INVALID_ARG_TYPE"
				}
			},
			{
				"name": "throwing-options",
				"trace": ["fatal"],
				"error": {
					"name": "Error",
					"sentinel": true
				}
			}
		],
		"codecCases": [
			{
				"name": "encoder:empty",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:empty-writes",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:ascii",
				"trace": [],
				"result": {
					"outputs": [[97], [98, 99]],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:pair-split",
				"trace": [],
				"result": {
					"outputs": [[
						240,
						159,
						140,
						141
					]],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:pair-whole",
				"trace": [],
				"result": {
					"outputs": [[
						240,
						159,
						140,
						141
					]],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:high-empty-low",
				"trace": [],
				"result": {
					"outputs": [[
						240,
						159,
						140,
						141
					]],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:high-flush",
				"trace": [],
				"result": {
					"outputs": [[
						239,
						191,
						189
					]],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:low",
				"trace": [],
				"result": {
					"outputs": [[
						239,
						191,
						189
					]],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:high-high-low",
				"trace": [],
				"result": {
					"outputs": [[
						239,
						191,
						189
					], [
						240,
						144,
						128,
						128
					]],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:mixed",
				"trace": [],
				"result": {
					"outputs": [[
						97,
						239,
						191,
						189,
						98,
						239,
						191,
						189,
						99
					], [
						244,
						143,
						191,
						191,
						122
					]],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:scalars",
				"trace": [],
				"result": {
					"outputs": [
						[
							117,
							110,
							100,
							101,
							102,
							105,
							110,
							101,
							100
						],
						[
							110,
							117,
							108,
							108
						],
						[
							116,
							114,
							117,
							101
						],
						[52, 50],
						[50],
						[
							83,
							121,
							109,
							98,
							111,
							108,
							40,
							115,
							41
						]
					],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:coercion",
				"trace": ["toString"],
				"result": {
					"outputs": [[
						97,
						98,
						99
					]],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "encoder:throwing-coercion",
				"trace": ["toString"],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "Error",
						"sentinel": true
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "Error",
						"sentinel": true
					} },
					"writerClosed": { "error": {
						"name": "Error",
						"sentinel": true
					} },
					"readClosed": { "error": {
						"name": "Error",
						"sentinel": true
					} }
				}
			},
			{
				"name": "decoder:split-0-0-false",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-0-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-1-0-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-1-0-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-2-0-false",
				"trace": [],
				"result": {
					"outputs": ["¢"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-2-0-true",
				"trace": [],
				"result": {
					"outputs": ["¢"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-2-1-false",
				"trace": [],
				"result": {
					"outputs": ["¢"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-2-1-true",
				"trace": [],
				"result": {
					"outputs": ["¢"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-0-false",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-0-true",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-1-false",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-1-true",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-2-false",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-2-true",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-3-false",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-3-3-true",
				"trace": [],
				"result": {
					"outputs": ["€"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-0-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-0-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-1-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-1-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-2-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-2-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-3-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-3-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-4-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-4-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-5-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-5-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-6-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-6-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-7-false",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-4-7-true",
				"trace": [],
				"result": {
					"outputs": ["🌍"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-0-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-0-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-1-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-1-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-2-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-2-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-3-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-3-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-4-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-4-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-5-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-5-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-6-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-6-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-7-false",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-5-7-true",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-6-0-false",
				"trace": [],
				"result": {
					"outputs": ["��"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-6-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-6-1-false",
				"trace": [],
				"result": {
					"outputs": ["�", "�"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-6-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-7-0-false",
				"trace": [],
				"result": {
					"outputs": ["���"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-7-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-7-1-false",
				"trace": [],
				"result": {
					"outputs": ["���"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-7-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-7-2-false",
				"trace": [],
				"result": {
					"outputs": ["��", "�"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-7-2-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-7-3-false",
				"trace": [],
				"result": {
					"outputs": ["��", "�"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-7-3-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-0-false",
				"trace": [],
				"result": {
					"outputs": ["����"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-1-false",
				"trace": [],
				"result": {
					"outputs": ["����"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-2-false",
				"trace": [],
				"result": {
					"outputs": ["��", "��"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-2-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-3-false",
				"trace": [],
				"result": {
					"outputs": ["��", "��"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-3-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-4-false",
				"trace": [],
				"result": {
					"outputs": ["���", "�"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-4-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-5-false",
				"trace": [],
				"result": {
					"outputs": ["���", "�"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-5-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-6-false",
				"trace": [],
				"result": {
					"outputs": [
						"��",
						"�",
						"�"
					],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-6-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-8-7-false",
				"trace": [],
				"result": {
					"outputs": [
						"��",
						"�",
						"�"
					],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-8-7-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-0-false",
				"trace": [],
				"result": {
					"outputs": ["����"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-1-false",
				"trace": [],
				"result": {
					"outputs": ["����"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-2-false",
				"trace": [],
				"result": {
					"outputs": ["��", "��"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-2-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-3-false",
				"trace": [],
				"result": {
					"outputs": ["��", "��"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-3-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-4-false",
				"trace": [],
				"result": {
					"outputs": ["���", "�"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-4-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-5-false",
				"trace": [],
				"result": {
					"outputs": ["���", "�"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-5-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-6-false",
				"trace": [],
				"result": {
					"outputs": [
						"��",
						"�",
						"�"
					],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-6-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-9-7-false",
				"trace": [],
				"result": {
					"outputs": [
						"��",
						"�",
						"�"
					],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-9-7-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-10-0-false",
				"trace": [],
				"result": {
					"outputs": ["�"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-10-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }],
					"close": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-10-1-false",
				"trace": [],
				"result": {
					"outputs": ["�"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-10-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-11-0-false",
				"trace": [],
				"result": {
					"outputs": ["�a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-11-0-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-11-1-false",
				"trace": [],
				"result": {
					"outputs": ["�", "a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-11-1-true",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_ENCODING_INVALID_ENCODED_DATA"
					} }
				}
			},
			{
				"name": "decoder:split-12-0-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-0-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-1-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-1-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-2-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-2-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-3-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-3-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-4-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-4-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-5-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-5-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-6-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-6-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-7-false",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-7-true",
				"trace": [],
				"result": {
					"outputs": ["🌍﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-8-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-8-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-9-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-9-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-10-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-10-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-11-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-11-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-12-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-12-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-13-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-13-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-14-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-14-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-15-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-15-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-16-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-16-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-17-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-17-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-18-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-18-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-19-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-19-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-20-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-20-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-21-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-21-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-22-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-22-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-23-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-23-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-24-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-24-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-25-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-25-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-26-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-26-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-27-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-27-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-28-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-28-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-29-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-29-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-30-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-30-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-31-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-31-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-32-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-32-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-33-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-33-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-34-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-34-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-35-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-35-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-36-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-36-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-37-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-37-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-38-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-38-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-39-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-39-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-40-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-40-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-41-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-41-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-42-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-42-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-43-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-43-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-44-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-44-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-45-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-45-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-46-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-46-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-47-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-47-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-48-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-48-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-49-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-49-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-50-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-50-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-51-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-51-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-52-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-52-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-53-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-53-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-54-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-54-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-55-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-55-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-56-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-56-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-57-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-57-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-58-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-58-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-59-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-59-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-60-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-60-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-61-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-61-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-62-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-62-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-63-false",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:split-12-63-true",
				"trace": [],
				"result": {
					"outputs": ["🌍", "﻿"],
					"writes": [
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true },
						{ "fulfilled": true }
					],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:bom-preserved",
				"trace": [],
				"result": {
					"outputs": ["﻿a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:bom-removed",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:arraybuffer-offset",
				"trace": [],
				"result": {
					"outputs": ["ab", "c"],
					"writes": [{ "fulfilled": true }, { "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:shadowed-fields",
				"trace": [],
				"result": {
					"outputs": ["a"],
					"writes": [{ "fulfilled": true }],
					"close": { "fulfilled": true },
					"read": { "fulfilled": true },
					"writerClosed": { "fulfilled": true },
					"readClosed": { "fulfilled": true }
				}
			},
			{
				"name": "decoder:invalid-undefined",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }
				}
			},
			{
				"name": "decoder:invalid-null",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }
				}
			},
			{
				"name": "decoder:invalid-1",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }
				}
			},
			{
				"name": "decoder:invalid-abc",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }
				}
			},
			{
				"name": "decoder:invalid-[object Object]",
				"trace": [],
				"result": {
					"outputs": [],
					"writes": [{ "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }],
					"close": { "skipped": true },
					"read": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"writerClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"readClosed": { "error": {
						"name": "TypeError",
						"sentinel": false,
						"code": "ERR_INVALID_ARG_TYPE"
					} }
				}
			}
		],
		"cancellationCases": [
			{
				"name": "TextEncoderStream:cancel-readable",
				"pendingRejected": true,
				"writerRejected": true,
				"readerClosed": true
			},
			{
				"name": "TextEncoderStream:abort-writable",
				"pendingRejected": true,
				"writerRejected": true,
				"readerClosed": true
			},
			{
				"name": "TextDecoderStream:cancel-readable",
				"pendingRejected": true,
				"writerRejected": true,
				"readerClosed": true
			},
			{
				"name": "TextDecoderStream:abort-writable",
				"pendingRejected": true,
				"writerRejected": true,
				"readerClosed": true
			}
		]
	},
	"guards": {
		"node": "v22.14.0",
		"cases": [
			{
				"name": "default",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "null-options",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "array-options",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "function-options",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "number-options",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE",
					"sentinel": false
				}
			},
			{
				"name": "min-one",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "min-two",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "min-null",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "min-string",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE",
					"sentinel": false
				}
			},
			{
				"name": "min-fraction",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_VALUE",
					"sentinel": false
				}
			},
			{
				"name": "min-zero",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_VALUE",
					"sentinel": false
				}
			},
			{
				"name": "min-nan",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_VALUE",
					"sentinel": false
				}
			},
			{
				"name": "min-infinity",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_VALUE",
					"sentinel": false
				}
			},
			{
				"name": "min-too-large",
				"trace": [],
				"error": {
					"name": "RangeError",
					"code": "ERR_OUT_OF_RANGE",
					"sentinel": false
				}
			},
			{
				"name": "min-getter",
				"trace": ["min"],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "throwing-min",
				"trace": ["min"],
				"error": {
					"name": "Error",
					"sentinel": true
				}
			},
			{
				"name": "invalid-receiver-first",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_THIS",
					"sentinel": false
				}
			},
			{
				"name": "spoof-receiver-first",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_THIS",
					"sentinel": false
				}
			},
			{
				"name": "proxy-genuine-receiver",
				"trace": [],
				"value": {
					"done": false,
					"bytes": [9, 10]
				}
			},
			{
				"name": "invalid-view-before-options",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE",
					"sentinel": false
				}
			},
			{
				"name": "arraybuffer-view-rejected",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE",
					"sentinel": false
				}
			},
			{
				"name": "zero-view-before-min",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_STATE",
					"sentinel": false
				}
			},
			{
				"name": "zero-view-invalid-options",
				"trace": [],
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE",
					"sentinel": false
				}
			},
			{
				"name": "shadowed-view-fields",
				"trace": ["byteLength"],
				"error": {
					"name": "Error",
					"sentinel": true
				}
			}
		]
	},
	"views": {
		"node": "v22.14.0",
		"cases": [
			{
				"name": "Int8Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Int8Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Uint8Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Uint8Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Uint8ClampedArray",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Uint8ClampedArray",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Int16Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Int16Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Uint16Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Uint16Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Int32Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Int32Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Uint32Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Uint32Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Float32Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Float32Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "Float64Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "Float64Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "BigInt64Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "BigInt64Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "BigUint64Array",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "BigUint64Array",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			},
			{
				"name": "DataView",
				"bytes": [
					0,
					1,
					2,
					3,
					4,
					5,
					6,
					7,
					8,
					9,
					10,
					11,
					12,
					13,
					14,
					15
				],
				"returnedType": "DataView",
				"prototypeIdentity": true,
				"byteOffset": 8,
				"byteLength": 16,
				"bufferLength": 32,
				"oldBufferLength": 0,
				"separateBuffer": true,
				"done": false
			}
		]
	},
	"controllers": {
		"node": "v22.14.0",
		"cases": [
			{
				"name": "desiredSize",
				"error": {
					"name": "TypeError",
					"sentinel": false,
					"code": "ERR_INVALID_THIS"
				}
			},
			{
				"name": "enqueue",
				"error": {
					"name": "TypeError",
					"sentinel": false,
					"code": "ERR_INVALID_THIS"
				}
			},
			{
				"name": "error",
				"error": {
					"name": "TypeError",
					"sentinel": false,
					"code": "ERR_INVALID_THIS"
				}
			},
			{
				"name": "terminate",
				"error": {
					"name": "TypeError",
					"sentinel": false,
					"code": "ERR_INVALID_THIS"
				}
			},
			{
				"name": "closed-controller",
				"desiredSize": 0
			},
			{
				"name": "errored-controller",
				"desiredSize": null,
				"writerReason": true,
				"readerReason": true
			}
		]
	},
	"iteration": {
		"node": "v22.14.0",
		"cases": [
			{
				"name": "from-array",
				"value": [
					1,
					2,
					3
				]
			},
			{
				"name": "from-string-unicode",
				"value": [
					"A",
					"🌍",
					"é"
				]
			},
			{
				"name": "from-sync-generator",
				"value": [1, 2]
			},
			{
				"name": "from-async-generator",
				"value": [1, 2]
			},
			{
				"name": "from-sync-promised-value",
				"value": [7]
			},
			{
				"name": "from-async-promised-value",
				"value": {
					"promised": true,
					"value": 8
				}
			},
			{
				"name": "from-invalid-null",
				"error": { "name": "TypeError" }
			},
			{
				"name": "from-invalid-undefined",
				"error": { "name": "TypeError" }
			},
			{
				"name": "from-invalid-plain",
				"error": {
					"name": "TypeError",
					"code": "ERR_ARG_NOT_ITERABLE"
				}
			},
			{
				"name": "from-invalid-number",
				"error": {
					"name": "TypeError",
					"code": "ERR_ARG_NOT_ITERABLE"
				}
			},
			{
				"name": "from-invalid-sync-null",
				"error": { "name": "TypeError" }
			},
			{
				"name": "from-invalid-async-number",
				"error": { "name": "TypeError" }
			},
			{
				"name": "from-invalid-iterator-number",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_STATE"
				}
			},
			{
				"name": "from-invalid-iterator-function",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_STATE"
				}
			},
			{
				"name": "from-async-next-number",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_STATE"
				}
			},
			{
				"name": "from-async-next-promised-number",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_STATE"
				}
			},
			{
				"name": "from-sync-next-number",
				"error": { "name": "TypeError" }
			},
			{
				"name": "from-throwing-next",
				"value": {
					"same": true,
					"locked": false
				}
			},
			{
				"name": "from-no-eager-pull",
				"value": {
					"before": ["iterator"],
					"first": {
						"value": 3,
						"done": false
					},
					"after": ["iterator", "next"],
					"trace": [
						"iterator",
						"next",
						"return:stop"
					]
				}
			},
			{
				"name": "from-next-captured",
				"value": {
					"values": [9],
					"gets": 1
				}
			},
			{
				"name": "from-sync-next-get-order",
				"value": {
					"before": ["iterator", "next-get"],
					"trace": [
						"iterator",
						"next-get",
						"next-get"
					],
					"gets": 2,
					"values": [9]
				}
			},
			{
				"name": "from-cancel-return-number",
				"value": {
					"same": true,
					"cancelled": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"locked": false
				}
			},
			{
				"name": "from-cancel-return-null",
				"value": {
					"same": true,
					"cancelled": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"locked": false
				}
			},
			{
				"name": "from-cancel-return-undefined",
				"value": {
					"same": true,
					"cancelled": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"locked": false
				}
			},
			{
				"name": "from-cancel-return-object",
				"value": {
					"same": true,
					"cancelled": {},
					"locked": false
				}
			},
			{
				"name": "from-cancel-return-promise-object",
				"value": {
					"same": true,
					"cancelled": {},
					"locked": false
				}
			},
			{
				"name": "from-cancel-return-rejection",
				"value": {
					"same": true,
					"locked": false
				}
			},
			{
				"name": "from-static-this-ignored",
				"value": [4]
			},
			{
				"name": "from-async-method-precedence",
				"value": {
					"trace": ["async"],
					"values": [5]
				}
			},
			{
				"name": "from-null-async-fallback",
				"value": [6]
			},
			{
				"name": "from-sync-generator-cancel-finally",
				"value": {
					"first": {
						"value": 1,
						"done": false
					},
					"trace": ["finally"]
				}
			},
			{
				"name": "from-serial-pulls",
				"value": {
					"before": ["next:0"],
					"trace": ["next:0", "next:1"],
					"results": [{
						"value": 1,
						"done": false
					}, { "done": true }],
					"maxActive": 1
				}
			},
			{
				"name": "from-throwing-result-done",
				"value": {
					"same": true,
					"locked": false
				}
			},
			{
				"name": "from-throwing-result-value",
				"value": {
					"same": true,
					"locked": false
				}
			},
			{
				"name": "from-throwing-return-getter",
				"value": { "same": true }
			},
			{
				"name": "from-new-rejected",
				"error": { "name": "TypeError" }
			},
			{
				"name": "values-options-undefined",
				"value": {
					"first": { "done": true },
					"locked": false
				}
			},
			{
				"name": "values-options-null",
				"value": {
					"first": { "done": true },
					"locked": false
				}
			},
			{
				"name": "values-options-false",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE"
				}
			},
			{
				"name": "values-options-zero",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE"
				}
			},
			{
				"name": "values-options-string",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_ARG_TYPE"
				}
			},
			{
				"name": "values-options-array",
				"value": {
					"first": { "done": true },
					"locked": false
				}
			},
			{
				"name": "values-options-function",
				"value": {
					"first": { "done": true },
					"locked": false
				}
			},
			{
				"name": "values-invalid-receiver-before-options",
				"value": {
					"error": {
						"name": "TypeError",
						"code": "ERR_INVALID_THIS"
					},
					"reads": 0
				}
			},
			{
				"name": "values-prototype-rejected",
				"error": {
					"name": "TypeError",
					"code": "ERR_INVALID_THIS"
				}
			},
			{
				"name": "values-locked-after-getter",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"trace": ["get"]
				}
			},
			{
				"name": "values-throwing-options-unlocked",
				"value": {
					"same": true,
					"locked": false
				}
			},
			{
				"name": "values-close-and-next",
				"value": {
					"lockedBefore": true,
					"one": {
						"value": 1,
						"done": false
					},
					"two": { "done": true },
					"three": { "done": true },
					"closedKeys": ["done", "value"],
					"lockedAfter": false,
					"returned": {
						"done": true,
						"value": "after"
					}
				}
			},
			{
				"name": "values-three-concurrent-next",
				"value": {
					"results": [
						{
							"value": 1,
							"done": false
						},
						{
							"value": 2,
							"done": false
						},
						{ "done": true }
					],
					"locked": false
				}
			},
			{
				"name": "values-pending-next-return-serialized",
				"value": {
					"before": [],
					"results": [{
						"value": 7,
						"done": false
					}, {
						"done": true,
						"value": "stop"
					}],
					"trace": [
						"next",
						"cancel:stop",
						"return"
					],
					"locked": false
				}
			},
			{
				"name": "values-return-prevent-false",
				"value": {
					"first": {
						"value": 1,
						"done": false
					},
					"returned": {
						"done": true,
						"value": "stop"
					},
					"again": { "done": true },
					"reasons": ["stop"],
					"locked": false,
					"remaining": null
				}
			},
			{
				"name": "values-return-prevent-true",
				"value": {
					"first": {
						"value": 1,
						"done": false
					},
					"returned": {
						"done": true,
						"value": "stop"
					},
					"again": { "done": true },
					"reasons": [],
					"locked": false,
					"remaining": 2
				}
			},
			{
				"name": "values-return-prevent-yes",
				"value": {
					"first": {
						"value": 1,
						"done": false
					},
					"returned": {
						"done": true,
						"value": "stop"
					},
					"again": { "done": true },
					"reasons": [],
					"locked": false,
					"remaining": 2
				}
			},
			{
				"name": "values-return-prevent-0",
				"value": {
					"first": {
						"value": 1,
						"done": false
					},
					"returned": {
						"done": true,
						"value": "stop"
					},
					"again": { "done": true },
					"reasons": ["stop"],
					"locked": false,
					"remaining": null
				}
			},
			{
				"name": "values-return-cancel-reject-unlocks",
				"value": {
					"same": true,
					"locked": false,
					"next": { "done": true },
					"again": {
						"done": true,
						"value": "again"
					}
				}
			},
			{
				"name": "values-error-unlocks-and-recovers-queue",
				"value": {
					"same": true,
					"locked": false,
					"next": { "done": true },
					"returned": {
						"done": true,
						"value": "after"
					}
				}
			},
			{
				"name": "values-concurrent-rejection-next",
				"value": {
					"first": true,
					"second": { "done": true },
					"locked": false
				}
			},
			{
				"name": "values-return-before-read",
				"value": {
					"returned": {
						"done": true,
						"value": "early"
					},
					"next": { "done": true },
					"trace": ["early"],
					"locked": false
				}
			},
			{
				"name": "values-concurrent-returns",
				"value": {
					"returned": [
						{
							"done": true,
							"value": "first"
						},
						{
							"done": true,
							"value": "second"
						},
						{ "done": true }
					],
					"reasons": ["first"],
					"locked": false
				}
			},
			{
				"name": "values-return-unlocks-before-cancel-fulfilled",
				"value": {
					"before": {
						"locked": false,
						"fulfilled": false
					},
					"returned": {
						"done": true,
						"value": "stop"
					},
					"after": true
				}
			},
			{
				"name": "values-option-read-once",
				"value": {
					"gets": 1,
					"locked": false
				}
			},
			{
				"name": "values-for-await-break",
				"value": {
					"values": [1],
					"trace": ["undefined"],
					"locked": false
				}
			},
			{
				"name": "values-for-await-prevent-cancel",
				"value": {
					"values": [1],
					"rest": [2],
					"cancels": 0,
					"locked": false
				}
			},
			{
				"name": "values-borrowed-next-return",
				"value": {
					"first": {
						"value": 3,
						"done": false
					},
					"last": {
						"done": true,
						"value": "stop"
					},
					"locked": false
				}
			},
			{
				"name": "values-descriptors-and-protocol",
				"value": {
					"same": true,
					"valuesLength": 0,
					"fromLength": 1,
					"nextLength": 0,
					"returnLength": 1,
					"self": true,
					"throwType": "undefined",
					"protoNext": true,
					"protoReturn": true,
					"ownKeys": ["next", "return"],
					"tag": "[object Object]"
				}
			},
			{
				"name": "values-new-rejected",
				"error": { "name": "TypeError" }
			},
			{
				"name": "own-error-codes-ignore-inherited-setter",
				"value": {
					"gets": 0,
					"sets": 0,
					"codes": [
						"ERR_ARG_NOT_ITERABLE",
						"ERR_INVALID_THIS",
						"ERR_INVALID_STATE"
					]
				}
			}
		]
	},
	"data": {
		"node": "v22.14.0",
		"cases": [
			{
				"name": "queued-offset-0",
				"value": {
					"first": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 0,
						"length": 3,
						"bufferLength": 32,
						"bytes": [
							2,
							3,
							4
						]
					},
					"last": {
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					},
					"oldBytes": 0,
					"resultDistinct": true,
					"locked": false
				}
			},
			{
				"name": "queued-offset-4",
				"value": {
					"first": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 4,
						"length": 3,
						"bufferLength": 32,
						"bytes": [
							2,
							3,
							4
						]
					},
					"last": {
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					},
					"oldBytes": 0,
					"resultDistinct": true,
					"locked": false
				}
			},
			{
				"name": "queued-offset-8",
				"value": {
					"first": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 8,
						"length": 3,
						"bufferLength": 32,
						"bytes": [
							2,
							3,
							4
						]
					},
					"last": {
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					},
					"oldBytes": 0,
					"resultDistinct": true,
					"locked": false
				}
			},
			{
				"name": "closed-empty-view-result",
				"value": {
					"entry": {
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 4,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					},
					"oldBytes": 0
				}
			},
			{
				"name": "byob-request-respond",
				"value": {
					"trace": [{
						"constructor": "Uint8Array",
						"length": 8,
						"offset": 5
					}],
					"entry": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 5,
						"length": 2,
						"bufferLength": 24,
						"bytes": [6, 7]
					},
					"oldBytes": 0
				}
			},
			{
				"name": "partial-queue-remains",
				"value": [
					{
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 3,
						"length": 2,
						"bufferLength": 16,
						"bytes": [0, 1]
					},
					{
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 3,
						"length": 4,
						"bufferLength": 16,
						"bytes": [
							2,
							3,
							4,
							5
						]
					},
					{
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 3,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					}
				]
			},
			{
				"name": "pending-cancel-undefined-result",
				"value": {
					"entry": {
						"done": true,
						"undefinedValue": true
					},
					"detachedBeforeCancel": true,
					"reasonSame": true,
					"locked": false
				}
			},
			{
				"name": "pending-error-identity",
				"value": {
					"same": true,
					"closedSame": true,
					"oldBytes": 0,
					"locked": false
				}
			},
			{
				"name": "already-errored-no-transfer",
				"value": {
					"same": true,
					"oldBytes": 16,
					"locked": false
				}
			},
			{
				"name": "released-reader-rejects-before-transfer",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"oldBytes": 16
				}
			},
			{
				"name": "concurrent-reads",
				"value": {
					"entries": [
						{
							"done": false,
							"constructor": "DataView",
							"dataView": true,
							"offset": 2,
							"length": 2,
							"bufferLength": 16,
							"bytes": [1, 2]
						},
						{
							"done": false,
							"constructor": "DataView",
							"dataView": true,
							"offset": 2,
							"length": 2,
							"bufferLength": 16,
							"bytes": [3, 4]
						},
						{
							"done": true,
							"constructor": "DataView",
							"dataView": true,
							"offset": 2,
							"length": 0,
							"bufferLength": 16,
							"bytes": []
						}
					],
					"oldBytes": [
						0,
						0,
						0
					]
				}
			},
			{
				"name": "min-undefined",
				"value": {
					"result": { "value": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 1,
						"bufferLength": 16,
						"bytes": [1]
					} },
					"trace": ["min"],
					"oldBytes": 0
				}
			},
			{
				"name": "min-null",
				"value": {
					"result": { "value": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 1,
						"bufferLength": 16,
						"bytes": [1]
					} },
					"trace": ["min"],
					"oldBytes": 0
				}
			},
			{
				"name": "min-1",
				"value": {
					"result": { "value": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 1,
						"bufferLength": 16,
						"bytes": [1]
					} },
					"trace": ["min"],
					"oldBytes": 0
				}
			},
			{
				"name": "min-0",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_ARG_VALUE"
					} },
					"trace": ["min"],
					"oldBytes": 16
				}
			},
			{
				"name": "min--1",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_ARG_VALUE"
					} },
					"trace": ["min"],
					"oldBytes": 16
				}
			},
			{
				"name": "min-1.5",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_ARG_VALUE"
					} },
					"trace": ["min"],
					"oldBytes": 16
				}
			},
			{
				"name": "min-1",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_ARG_TYPE"
					} },
					"trace": ["min"],
					"oldBytes": 16
				}
			},
			{
				"name": "min-9",
				"value": {
					"result": { "error": {
						"name": "RangeError",
						"code": "ERR_OUT_OF_RANGE"
					} },
					"trace": ["min"],
					"oldBytes": 16
				}
			},
			{
				"name": "empty-view-before-min",
				"value": {
					"result": { "error": {
						"name": "TypeError",
						"code": "ERR_INVALID_STATE"
					} },
					"gets": 0,
					"oldBytes": 16
				}
			},
			{
				"name": "detached-by-min-getter",
				"value": {
					"result": { "error": { "name": "TypeError" } },
					"oldBytes": 0
				}
			},
			{
				"name": "throwing-min-queue-preserved",
				"value": {
					"same": true,
					"before": 16,
					"result": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 2,
						"bufferLength": 16,
						"bytes": [7, 8]
					}
				}
			},
			{
				"name": "untouched-backing-outside-view",
				"value": {
					"entry": {
						"done": false,
						"constructor": "DataView",
						"dataView": true,
						"offset": 5,
						"length": 3,
						"bufferLength": 24,
						"bytes": [
							1,
							2,
							3
						]
					},
					"allBytes": [
						165,
						165,
						165,
						165,
						165,
						1,
						2,
						3,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165,
						165
					],
					"oldBytes": 0
				}
			},
			{
				"name": "close-pending-with-zero-response",
				"value": {
					"entry": {
						"done": true,
						"constructor": "DataView",
						"dataView": true,
						"offset": 2,
						"length": 0,
						"bufferLength": 16,
						"bytes": []
					},
					"oldBytes": 0
				}
			},
			{
				"name": "source-type-error-identity",
				"value": { "same": true }
			},
			{
				"name": "cancel-rejection-pending-result",
				"value": {
					"same": true,
					"entry": {
						"done": true,
						"undefinedValue": true
					},
					"oldBytes": 0
				}
			}
		]
	}
};
// tests/node-compat/foundation-stream-web/production-candidate/native-component.mjs
const snapshotReadable = new namespace.ReadableStream({ start(controller) {
	controller.enqueue("snapshot");
	controller.close();
} });
const snapshotFrom = namespace.ReadableStream.from([3, 4]);
const snapshotEncoder = new namespace.TextEncoderStream();
const snapshotDecoder = new namespace.TextDecoderStream();
let calls = 0;
function ensure(value, message) {
	if (!value) throw Error(message);
}
async function consume(stream) {
	const reader = stream.getReader(), values = [];
	try {
		for (;;) {
			const entry = await reader.read();
			if (entry.done) break;
			values.push(entry.value);
		}
	} finally {
		reader.releaseLock();
	}
	return values;
}
async function nativeIdentities() {
	const globals = [
		"ReadableStream",
		"ReadableStreamDefaultReader",
		"ReadableStreamBYOBReader",
		"ReadableStreamBYOBRequest",
		"ReadableByteStreamController",
		"ReadableStreamDefaultController",
		"WritableStream",
		"ByteLengthQueuingStrategy",
		"CountQueuingStrategy",
		"TransformStream"
	];
	for (const name of globals) ensure(namespace[name] === globalThis[name], "global identity " + name);
	let writableController, transformController;
	const writer = new namespace.WritableStream({ start(controller) {
		writableController = controller;
	} }).getWriter();
	ensure(writer.constructor === namespace.WritableStreamDefaultWriter && writableController.constructor === namespace.WritableStreamDefaultController, "hidden writable identities");
	ensure(writer instanceof namespace.WritableStreamDefaultWriter && writableController instanceof namespace.WritableStreamDefaultController, "hidden writable brands");
	await writer.close();
	await writer.closed;
	writer.releaseLock();
	const transform = new namespace.TransformStream({ start(controller) {
		transformController = controller;
	} }), tw = transform.writable.getWriter(), tr = transform.readable.getReader(), closed = tw.close();
	ensure(transformController.constructor === namespace.TransformStreamDefaultController && transformController instanceof namespace.TransformStreamDefaultController, "hidden transform identity");
	await tr.read();
	await closed;
	await tw.closed;
	await tr.closed;
	tw.releaseLock();
	tr.releaseLock();
	ensure(typeof writableController.signal === "undefined", "Writable controller signal remains an explicit gap");
	ensure(typeof globalThis.TextEncoderStream === "undefined" && typeof globalThis.TextDecoderStream === "undefined", "No accidental global codec installation");
	ensure(namespace.CompressionStream !== globalThis.CompressionStream && namespace.DecompressionStream !== globalThis.DecompressionStream, "Compression bindings must remain explicit deferred functions");
	return {
		globalNativeConstructors: globals.length,
		hiddenNativeConstructors: 3,
		uninstalledGlobalCodecs: true,
		signalMissing: true
	};
}
async function run() {
	const report = { calls: ++calls };
	try {
		const names = Object.keys(namespace).sort();
		ensure(JSON.stringify(names) === JSON.stringify(_node_compat_stream_web_installed_oracles_default.names), "exact finite ESM namespace");
		for (const candidate of [namespace, namespace]) {
			ensure(Object.getPrototypeOf(candidate) === null && candidate.then === void 0 && candidate.missing === void 0, "safe native ESM namespace");
			ensure(await Promise.resolve(candidate) === candidate, "no accidental thenable");
			for (const name of names) if (name !== "default") ensure(candidate[name] === __smBuiltin0[name], "named/default identity " + name);
		}
		ensure(__smBuiltin0 === namespace.default && __smBuiltin0 === __smBuiltin0 && namespace.default === __smBuiltin0, "alias defaults");
		ensure(native_require_cjs_native_profile_default.canonical === __smBuiltin0 && native_require_cjs_native_profile_default.bare === __smBuiltin0, "literal CommonJS default lowering");
		ensure(JSON.stringify(Object.keys(__smBuiltin0).sort()) === JSON.stringify(names.filter((name) => name !== "default")), "finite default fields");
		const saved = __smBuiltin0.TextEncoderStream;
		try {
			__smBuiltin0.TextEncoderStream = null;
			ensure(namespace.TextEncoderStream === saved, "named binding snapshot");
		} finally {
			__smBuiltin0.TextEncoderStream = saved;
		}
		report.identities = await nativeIdentities();
		report.aliases = 2;
		report.commonJS = true;
		report.names = names;
		const full = await runNativeCorpus(namespace, _node_compat_stream_web_installed_oracles_default);
		if (full.failure) throw full.failure;
		Object.assign(report, full);
		if (calls === 1) {
			ensure(JSON.stringify(await consume(snapshotReadable)) === "[\"snapshot\"]", "snapshot queued readable");
			ensure(JSON.stringify(await consume(snapshotFrom)) === "[3,4]", "snapshot HWM0 from iterable");
			const encoded = await pipeline(snapshotEncoder, ["\ud83c", "\udf0d"]);
			ensure(JSON.stringify(encoded.outputs) === "[[240,159,140,141]]" && encoded.close.fulfilled, "snapshot codec state");
			const decoded = await pipeline(snapshotDecoder, [Uint8Array.of(226), Uint8Array.of(130, 172)]);
			ensure(JSON.stringify(decoded.outputs) === "[\"€\"]" && decoded.close.fulfilled, "snapshot decoder state");
		}
		report.snapshotResumption = true;
		report.passed = true;
	} catch (error) {
		report.failure = error?.actual !== void 0 ? error : {
			name: error?.name,
			message: error?.message,
			stack: error?.stack
		};
		report.passed = false;
	}
	return JSON.stringify(report);
}
export { run };
