// tests/node-compat/frameworks/package-bundler-v2-source-review/cases/optional-process/entry.mjs
function o() {
	return typeof process === "undefined" ? null : process.emit;
}
export { o };
