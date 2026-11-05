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
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/conditional-lazy-once/lazy.cjs
var require_lazy = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	globalThis.__auditCount = (globalThis.__auditCount ?? 0) + 1;
	module.exports = { id: globalThis.__auditCount };
}));
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/conditional-lazy-once/entry.mjs
var import_pkg = /* @__PURE__ */ __toESM((/* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = function(flag) {
		if (flag) return require_lazy();
		return "skip";
	};
})))(), 1);
function observe() {
	const before = globalThis.__auditCount ?? 0;
	const skipped = (0, import_pkg.default)(false);
	const afterSkip = globalThis.__auditCount ?? 0;
	const a = (0, import_pkg.default)(true);
	const afterLoad = globalThis.__auditCount;
	const b = (0, import_pkg.default)(true);
	return {
		before,
		skipped,
		afterSkip,
		afterLoad,
		afterAgain: globalThis.__auditCount,
		same: a === b
	};
}
export { observe };
