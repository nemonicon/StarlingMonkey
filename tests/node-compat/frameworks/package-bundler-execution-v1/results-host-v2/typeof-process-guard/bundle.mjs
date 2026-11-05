// ../../../../private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01/typeof-process-guard/entry.mjs
function observe() {
	if ("object" === typeof process && "function" === typeof process.emit) return typeof process.emit;
	return "absent";
}
export { observe };
