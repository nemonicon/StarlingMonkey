import expected, * as m from "stream";
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
// builtin:esm-external-require-stream
var require_builtin_esm_external_require_stream = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = m.default;
}));
// tests/node-compat/frameworks/package-bundler-v1/evidence/official-bare-stream/entry.mjs
var import_pkg = /* @__PURE__ */ __toESM((/* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = require_builtin_esm_external_require_stream();
})))(), 1);
function observe() {
	return {
		sameDefault: import_pkg.default === expected,
		hasOwnDefault: Object.hasOwn(import_pkg.default, "default"),
		type: typeof import_pkg.default,
		keys: Object.keys(import_pkg.default).sort(),
		streamSelf: import_pkg.default.Stream === import_pkg.default
	};
}
export { observe };
