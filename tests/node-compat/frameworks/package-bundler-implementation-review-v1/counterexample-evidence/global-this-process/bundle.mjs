// tests/node-compat/frameworks/package-bundler-implementation-review-v1/counterexample-evidence/global-this-process/entry.mjs
function value() {
	return globalThis.process.env.OTHER_ENV;
}
export { value };
