import * as m from "node:buffer";
// \0rolldown/runtime.js
var __commonJSMin = (cb, mod) => () => (mod || (cb((mod = { exports: {} }).exports, mod, mod.exports), cb = null), mod.exports);
// builtin:esm-external-require-node:buffer
var require_builtin_esm_external_require_node_buffer = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = m.default;
}));
// tests/node-compat/frameworks/package-bundler-v1/virtual-source-evidence/entry.cjs
var require_entry = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = require_builtin_esm_external_require_node_buffer();
}));
export default require_entry();
