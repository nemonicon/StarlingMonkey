// tests/node-compat/frameworks/package-bundler-implementation-review-v1/counterexample-evidence/global-this-filename/entry.mjs
function value() {
	return globalThis.__dirname;
}
export { value };
