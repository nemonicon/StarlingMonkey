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
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/cyclic-partial-exports/b.cjs
var require_b = /* @__PURE__ */ __commonJSMin(((exports) => {
	exports.name = "b";
	exports.a = require_a().name;
}));
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/cyclic-partial-exports/a.cjs
var require_a = /* @__PURE__ */ __commonJSMin(((exports) => {
	exports.name = "a";
	exports.b = require_b().name;
}));
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/cyclic-partial-exports/entry.mjs
var import_a = /* @__PURE__ */ __toESM(require_a(), 1);
var import_b = /* @__PURE__ */ __toESM(require_b(), 1);
function observe() {
	return {
		a: import_a.default,
		b: import_b.default
	};
}
export { observe };
