# Source-only disabled CommonJS correction

The preceding twelve-file revision and receipt are preserved byte-for-byte under
`history/v3/`. Its receipt is SHA-256
`5a66b24bd02ce1217e11cd20a290e2f40639fd138083198d73749157ad897570`.
No bundler, componentizer, compiler, guest, or target host was executed.

The disabled module selection control previously gave both ESM and CommonJS
inputs an `.mjs` suffix. The profile bundler can refuse require calls outside
`.cjs` before evaluating whether the module is admitted, yielding the wrong
failure reason. The corrected controls use `.mjs` for ESM and `.cjs` for literal
CommonJS. The latter source uses `module.exports = require(...)`, without an ESM
export declaration inside the CommonJS wrapper. All eight expected failures
remain module-not-admitted errors, before componentizer selection.

Only the driver, current README, this note, and current receipt change. The
ordinary checks, existing Node oracle source/results, guest, deployed fixtures,
and GC owner-retention control remain unchanged. No oracle rerun is required
to describe this file-format-only source correction. All future engine pins
remain null and all component/runtime tests remain unexecuted.
