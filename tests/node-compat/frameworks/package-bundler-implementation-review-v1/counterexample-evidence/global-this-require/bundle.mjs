// tests/node-compat/frameworks/package-bundler-implementation-review-v1/counterexample-evidence/global-this-require/entry.mjs
function value(name) {
	return globalThis.require(name);
}
export { value };
