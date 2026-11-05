import { Buffer } from "node:buffer";
import path from "node:path";
import { EventEmitter } from "node:events";
import { StringDecoder } from "node:string_decoder";
import assert from "node:assert/strict";
import querystring from "node:querystring";
import { isArrayBuffer, isArrayBufferView, isDataView, isUint8Array } from "node:util/types";
import { ReadableStream, TransformStream } from "node:stream/web";
import { Readable, Transform, Writable } from "node:stream";
import { pipeline } from "node:stream/promises";
// ../../../../private/tmp/starling-node-compat/nextjs-16.4.5-v13-run-20261105-02/application/.sm-wasm-native-modules-a589e6ea5d31.mjs
async function run() {
	const input = new Uint8Array([
		0,
		104,
		101,
		108,
		108,
		111,
		255
	]);
	const copied = Buffer.from(input.subarray(1, 6));
	input[1] = 120;
	assert.equal(copied.toString("utf8"), "hello");
	const backing = /* @__PURE__ */ new ArrayBuffer(6), bytes = new Uint8Array(backing);
	bytes.set([
		10,
		20,
		30,
		40,
		50,
		60
	]);
	const shared = Buffer.from(backing, 1, 3);
	shared[0] = 91;
	assert.equal(bytes[1], 91);
	const sliced = shared.slice(1, 3);
	sliced[0] = 92;
	assert.equal(bytes[2], 92);
	const zeroed = Buffer.alloc(4);
	for (const byte of zeroed) assert.equal(byte, 0);
	const hex = Buffer.from("6869", "hex");
	assert.equal(hex.toString("utf8"), "hi");
	const emitter = new EventEmitter(), events = [];
	const listener = (value) => events.push("on:" + value);
	emitter.on("value", listener);
	emitter.once("value", (value) => events.push("once:" + value));
	emitter.emit("value", 7);
	emitter.off("value", listener);
	assert.equal(emitter.emit("value", 9), false);
	assert.equal(events.length, 2);
	assert.equal(events[0], "on:7");
	assert.equal(events[1], "once:7");
	const decoder = new StringDecoder("utf8");
	const first = decoder.write(Buffer.from(new Uint8Array([226, 130])));
	const last = decoder.end(Buffer.from(new Uint8Array([172])));
	assert.equal(first, "");
	assert.equal(last, "€");
	const parsed = querystring.parse("q=a%20b&tag=one&tag=two");
	assert.equal(parsed.q, "a b");
	assert.equal(parsed.tag.length, 2);
	const webSource = new ReadableStream({ start(controller) {
		controller.enqueue("x");
		controller.enqueue("y");
		controller.close();
	} });
	const webUpper = new TransformStream({ transform(chunk, controller) {
		controller.enqueue(chunk.toUpperCase());
	} });
	const webReader = webSource.pipeThrough(webUpper).getReader(), webChunks = [];
	try {
		for (;;) {
			const { done, value } = await webReader.read();
			if (done) break;
			webChunks.push(value);
			assert.equal(webChunks.length <= 2, true);
		}
	} finally {
		webReader.releaseLock();
	}
	assert.equal(webChunks.length, 2);
	assert.equal(webChunks[0], "X");
	assert.equal(webChunks[1], "Y");
	const classicChunks = [];
	const upper = new Transform({ transform(chunk, encoding, callback) {
		callback(null, chunk.toString("utf8").toUpperCase());
	} });
	const sink = new Writable({ write(chunk, encoding, callback) {
		classicChunks.push(chunk.toString("utf8"));
		callback();
	} });
	await pipeline(Readable.from(["a", "b"]), upper, sink);
	assert.equal(classicChunks.length, 2);
	assert.equal(classicChunks[0], "A");
	assert.equal(classicChunks[1], "B");
	return JSON.stringify({
		marker: "NATIVE_MODULES_SUPPORTED_DIFFERENTIAL",
		buffer: {
			utf8: copied.toString("utf8"),
			hex: copied.toString("hex"),
			copiesView: copied[0] === 104 && input[1] === 120,
			sharedHex: shared.toString("hex"),
			sliceHex: sliced.toString("hex"),
			sharesArrayBuffer: shared.buffer === backing,
			sliceSharesArrayBuffer: sliced.buffer === backing,
			zeroed: Array.from(zeroed),
			hexDecode: hex.toString("utf8")
		},
		path: {
			normalized: path.posix.normalize("/a/../b/./c"),
			basename: path.posix.basename("/b/c.txt", ".txt")
		},
		events,
		decoder: {
			first,
			last
		},
		query: {
			q: parsed.q,
			tag: parsed.tag,
			encoded: querystring.stringify({
				q: "a b",
				count: "2"
			})
		},
		types: {
			uint8Array: isUint8Array(input),
			arrayBuffer: isArrayBuffer(backing),
			arrayBufferView: isArrayBufferView(input),
			dataView: isDataView(new DataView(backing)),
			arrayIsUint8Array: isUint8Array([])
		},
		webStream: {
			chunks: webChunks,
			text: webChunks.join("")
		},
		classicStream: {
			chunks: classicChunks,
			text: classicChunks.join("")
		},
		assertions: true
	});
}
export { run };
