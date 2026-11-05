// \0rolldown/runtime.js
var __commonJSMin = (cb, mod) => () => (mod || (cb((mod = { exports: {} }).exports, mod, mod.exports), cb = null), mod.exports);
// tests/node-compat/frameworks/package-bundler-v1/lifecycle-evidence/mutable-cjs-named-import/entry.mjs
var import_pkg = (/* @__PURE__ */ __commonJSMin(((exports) => {
	exports.number = 1;
	exports.change = function() {
		exports.number = 2;
	};
})))();
function observe() {
	const before = import_pkg.number;
	(0, import_pkg.change)();
	return {
		before,
		after: import_pkg.number
	};
}
export { observe };
