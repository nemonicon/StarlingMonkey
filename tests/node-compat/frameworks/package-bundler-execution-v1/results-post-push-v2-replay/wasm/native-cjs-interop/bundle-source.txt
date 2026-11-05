import * as m$2 from "node:buffer";
import buffer, { Buffer as Buffer$1 } from "node:buffer";
import stream, * as m$1 from "node:stream";
import events, * as m from "node:events";
// \0rolldown/runtime.js
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJSMin = (cb, mod) => () => (mod || (cb((mod = { exports: {} }).exports, mod, mod.exports), cb = null), mod.exports);
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
// builtin:esm-external-require-node:buffer
var require_builtin_esm_external_require_node_buffer = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = m$2.default;
}));
// tests/node-compat/frameworks/nextjs/probes/native-cjs-state.cjs
var require_native_cjs_state = /* @__PURE__ */ __commonJSMin(((exports) => {
	exports.marker = "real relative CommonJS dependency";
	exports.buffer = require_builtin_esm_external_require_node_buffer();
}));
// builtin:esm-external-require-node:stream
var require_builtin_esm_external_require_node_stream = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = m$1.default;
}));
// builtin:esm-external-require-node:events
var require_builtin_esm_external_require_node_events = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = m.default;
}));
// tests/node-compat/frameworks/nextjs/probes/native-cjs-interop.mjs
var import_native_cjs_interop = /* @__PURE__ */ __toESM((/* @__PURE__ */ __commonJSMin(((exports, module) => {
	const state = require_native_cjs_state();
	module.exports = {
		bare: require_builtin_esm_external_require_node_buffer(),
		canonical: require_builtin_esm_external_require_node_buffer(),
		stream: require_builtin_esm_external_require_node_stream(),
		events: require_builtin_esm_external_require_node_events(),
		state
	};
})))(), 1);
function run() {
	const bytes = import_native_cjs_interop.default.bare.Buffer.from(new Uint8Array([104, 105]));
	return JSON.stringify({
		marker: import_native_cjs_interop.default.state.marker,
		canonicalDefault: import_native_cjs_interop.default.canonical === buffer,
		bareDefault: import_native_cjs_interop.default.bare === buffer,
		nestedDefault: import_native_cjs_interop.default.state.buffer === buffer,
		constructorIdentity: import_native_cjs_interop.default.bare.Buffer === Buffer$1 && Buffer$1 === globalThis.Buffer,
		streamDefault: import_native_cjs_interop.default.stream === stream,
		streamCallable: typeof import_native_cjs_interop.default.stream === "function",
		streamSelf: import_native_cjs_interop.default.stream.Stream === import_native_cjs_interop.default.stream,
		eventDefault: import_native_cjs_interop.default.events === events,
		noNamespaceDefault: Object.hasOwn(import_native_cjs_interop.default.bare, "default") === false,
		text: bytes.toString("utf8"),
		hex: bytes.toString("hex")
	});
}
export { run };
