// ../../../../private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01/provided-process-global/entry.mjs
function observe() {
	const process = { env: {
		NODE_ENV: "local",
		OTHER_ENV: "value"
	} };
	return [
		process.env.NODE_ENV,
		process.env.OTHER_ENV,
		{ value: 7 }.value
	];
}
export { observe };
