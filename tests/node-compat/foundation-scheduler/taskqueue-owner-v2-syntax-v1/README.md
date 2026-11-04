# Isolated scheduler v2 Release SDK syntax

**All five staged translation units pass syntax checking, with no diagnostics.**
This is not an engine build, linkage test or guest execution. The source-only
[v2 packet](../taskqueue-owner-v2/index.json) and all its 17 indexed files remain
byte-identical; its original uncompiled labels describe that frozen proposal.
This separate receipt records the later actual syntax step.

[results.json](results.json) records the complete commands, compiler digest,
frozen input receipts and pre/post checks. The immutable v11 OFF receipt is
`/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json`,
referencing engine `1eb2b55a391e2bc83478fefee124a6f282cfed148cc0623754125f6c5e9b0458`.
All 304 frozen native input digests match v2's approved m11 ancestry. Only a few
necessary source/header files were copied to the separate
`/tmp/starling-node-compat/scheduler-taskqueue-v2-syntax-v1/stage`; SDK, library,
full native sources and engine binaries were not duplicated.

The exact frozen runtime/embedding commands supply Release, wasm32-wasi,
`-DNDEBUG`, `-Werror`, normal SM147 configuration and include flags. Changes are:
remove output/dependency-file flags and `-c`, add `-fsyntax-only` and
`-DNODE_COMPAT_INTERNAL_TICKS=1`, put staged changed headers first, and rewrite
unchanged repository include roots to the immutable v11 source freeze. The
runtime wrapper is replaced by the identical SDK clang++ it invokes; the wrapper
only adjusts PATH for linker wasm-opt. No linking occurs here. Diagnostic flags
are derived from the actual existing embedding-builtin command; they are **not**
claimed as an observed future diagnostic CMake command.

The new queue, patched event loop, Engine, embedding, and unchanged v2 diagnostic
all return status zero. [diagnostics](diagnostics/queue.command.json) retains all
five command lists and ten empty stdout/stderr logs. The reproducible
[runner](run-syntax.py) refuses to overwrite an existing stage. No DEBUG, OOM,
fault, raw-memory or cross-realm guest probe was run.

Source review identified a diagnostic-only gap: v2 `scheduleTask` does not reject
foreign callback objects before entering their realm. This syntax result does
not establish that domain's safety. The separate
[v3 diagnostic guard](../taskqueue-owner-v3/README.md) must be reviewed and syntax
checked before any guest test. Reset/cancellation safety remains explicitly
OPEN; this result does not establish safe reset or component reuse.
