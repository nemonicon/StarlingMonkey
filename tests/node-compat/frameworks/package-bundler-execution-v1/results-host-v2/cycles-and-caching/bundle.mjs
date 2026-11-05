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
// ../../../../private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01/cycles-and-caching/b.cjs
var require_b = /* @__PURE__ */ __commonJSMin(((exports) => {
	exports.name = "b";
	exports.partial = require_a().name;
}));
// ../../../../private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01/cycles-and-caching/a.cjs
var require_a = /* @__PURE__ */ __commonJSMin(((exports) => {
	exports.name = "a";
	exports.count = (exports.count || 0) + 1;
	exports.b = require_b();
}));
// ../../../../private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01/cycles-and-caching/entry.mjs
var import_a = /* @__PURE__ */ __toESM(require_a(), 1);
var import_b = /* @__PURE__ */ __toESM(require_b(), 1);
function observe() {
	return {
		a: "a",
		b: "b",
		partial: import_b.partial,
		once: import_a.count,
		same: import_a.b === import_b.default
	};
}
export { observe };
