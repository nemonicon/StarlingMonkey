// tests/node-compat/frameworks/package-bundler-v1/additional-evidence/dynamic-import-expression/entry.mjs
async function value(x) {
	return import(x);
}
export { value };
