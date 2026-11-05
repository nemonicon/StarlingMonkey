import * as m from "./external.mjs";
import original, { change, number } from "./external.mjs";
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
// builtin:esm-external-require-./external.mjs
var require_external = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = Object.prototype.hasOwnProperty.call(m, "module.exports") ? m["module.exports"] : { ...m };
}));
// tests/node-compat/frameworks/package-bundler-v1/evidence/external-esm-live/entry.mjs
var import_pkg = /* @__PURE__ */ __toESM((/* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = require_external();
})))(), 1);
function observe() {
	const before = import_pkg.default.number;
	change(2);
	return {
		sameDefault: import_pkg.default === original,
		extraDefault: Object.hasOwn(import_pkg.default, "default"),
		before,
		requiredAfter: import_pkg.default.number,
		esmAfter: number
	};
}
export { observe };
