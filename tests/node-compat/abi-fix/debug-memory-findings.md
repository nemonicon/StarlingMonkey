# DEBUG canonical-memory diagnosis and bounded allocator gate

The pinned ComponentizeJS DEBUG embedding exposes its canonical memory buffer at guest address **64**, while generated JavaScript bindings use absolute canonical addresses. This shifts indirect reads and writes by 64 bytes. It is independent of Buffer, allocator fault injection and the new native ABI conversions.

[debug-controls-results.json](debug-controls-results.json) records the same source, WIT world and v2 packager with three real engines. No fixture operation calls Buffer or a fault hook; final components import nothing. Every operation runs in a fresh process/instance. The observer reads only bounded prefixes before the original fatal UTF-8 decoder; it does not make malformed output acceptable.

| Engine | Scalar/control checks | Indirect checks |
| --- | --- | --- |
| Release allocation-r2 `99fdaa97…b65c` | 5/5 | 3/3 |
| Prior DEBUG `7d8c589c…2922` | 5/5 | 0/3 |
| DEBUG allocation-r2 `0d63dd0c…b6e5` | 5/5 | 0/3 |

The scalar checks are s32, high u32, f64, and the length/digest of the original guest string. Indirect checks are `list<u8>`, a constant string and a JSON string. The DEBUG list is malformed and much longer than its seven expected bytes; diagnostics cap its reported prefix.

For the DEBUG allocation-r2 constant string, the returned tuple at `ret` contains unrelated heap values. Reading the tuple at **ret + 64** yields pointer 8,014,656 and length 26. The exact expected UTF-8 text appears at **pointer + 64**. The prior DEBUG engine has the same displacement. Release's tuple and bytes are correct at offset zero.

The source cause is [ComponentizeJS GetMemBuffer](https://github.com/bytecodealliance/ComponentizeJS/blob/4d812f5a7b524cea5bcfd565cac55f3fab876a57/embedding/embedding.cpp#L542): its DEBUG branch chooses address 64, its release branch chooses zero, and both expose the same `sbrk(0)` length. The pinned [SpiderMonkey API implementation](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/vm/ArrayBufferObject.cpp#L3456) requires non-null user-owned contents. Simply selecting zero in DEBUG would violate that invariant. No assertion was disabled and no SpiderMonkey API or host was changed.

This finding invalidates DEBUG indirect-transport acceptance. It does not establish that every earlier allocator/SavedFrame failure had the same cause. Malformed indirect results and their post-return cleanup are no longer executed as an acceptance path.

## Implemented safe diagnostic exception

The shared [componentizer loader](../componentizer.mjs) rejects unrebased DEBUG engines before packaging by default, with `ERR_SM_NODE_UNREBASED_DEBUG_MEMORY`. Stock/legacy selection and the old environment override cannot bypass this guard. Normal calls require byte-matching engine metadata and an observed Release/Debug configuration; exact old release controls require a separate explicit diagnostic exception.

The sole admitted exception is explicit `loadComponentizer(toolchain, { debugScalarOOMDiagnostic: true })`, using:

- Exact WIT SHA `2384f23573d9f9264940b5f2e574ca06d43ad3a43587beb53f2fc308cd3ebb84`, world `profile`, no `witPath`.
- No imports and only `run: func() -> s32`, with no parameters. The loader checks the actual emitted WIT again after packaging.
- The clock-corrected v2 packager, DEBUG/OOM/GC-stress engine flags, engine-byte hash, debugger/WPT disabled, and all five optional packaging features disabled.

That export uses C++ `call()`'s singular I32 result store and the Rust splicer's direct I32 load. Its generated guest wrapper does not access `$memory.buffer`. All Buffer operations, four real allocation failures, pending-OOM/ownership assertions, retained views/brands, Error behavior, 32 recovery pairs and moving collections still execute inside the guest. Only the test's WIT report is numeric. [The allocator gate](../oom/results.json) passes three calls on one Jco instance and a fresh stock Wasmtime instance, with zero imports; its result records the exact admitted diagnostic audit.

This exception provides no general DEBUG string/list/record or Node compatibility claim. The unsafe indirect transport remains unavailable.

## Future base-aware binding generation: source inventory only

A principled DEBUG transport fix must preserve canonical pointer **values** and subtract the memory base only when accessing memory. `GetMemBuffer` must expose `[64, sbrk)` with length `sbrk - 64`; an explicitly implemented private binding contract would convey that base. No constructor shadow or memory Proxy is needed.

For ComponentizeJS 0.23's synchronous P2, UTF-8 path, the finite initial emission surface is:

| Source | Required adjustment |
| --- | --- |
| `js-component-bindgen 2.11.0/src/function_bindgen.rs`, `load` / `store` | Rebase DataView access addresses, preserving stored scalar/pointer values. |
| Same file, `ListCanonLower` | Rebase regular-array write addresses and the destination view; leave application-buffer offsets unchanged. |
| Same file, `ListCanonLift` | Rebase the start/end of the guest-memory slice; preserve canonical alignment and deallocation arguments. |
| Same file, `StringLift` | Rebase the guest-memory view only. |
| `src/intrinsics/string.rs`, `Utf8Encode` | Rebase the encoder destination, returning the original canonical pointer. |
| ComponentizeJS `bindgen.rs` and `embedding.cpp` | Select the private base-aware mode and correct borrowed buffer length/lifetime/OOM handling. |

This is seven principal emission groups across two crate files plus binding options and the embedding contract. Empty string/list representations may have pointers 0 or 1 and must avoid constructing negative-offset zero-length views. UTF-16, dynamic lift/lower intrinsics, P3 async, transcoders and managed buffers have further access sites and require separate coverage. ComponentizeJS currently selects `FunctionBindgen.is_async(false)` and rejects non-UTF-8 encoding in its binding builder. A generic Jco fix would therefore be substantially wider than this P2-specific proposal. No such patch has been implemented or claimed tested.

## Supported release OOM instrumentation alternative

The pinned [js/moz.configure](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/moz.configure#L492) supports `--enable-oom-breakpoint` independently of DEBUG. It defines `JS_OOM_BREAKPOINT`. [Utility.cpp](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/util/Utility.cpp#L25) compiles the same `FailureSimulator`, thread tagging and reset implementation when either configuration is enabled. The existing [OOM scopes](../../../builtins/node-compat/oom-testing.h) already accept either macro and retain their `MOZ_RELEASE_ASSERT` checks.

The inspected release archive has no defined simulator symbols; DEBUG does. The pinned [release assets](https://github.com/bytecodealliance/StarlingMonkey/releases/tag/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING) provide debug, release and release-weval distributions. None is a verified release OOM-breakpoint build. Defining the macro only in embedding code would not instrument the four internal allocation APIs and is insufficient.

A future release-style allocator artifact could reuse [cmake/spidermonkey.cmake](../../../cmake/spidermonkey.cmake)'s existing source-build mozconfig, keep `--disable-debug`, and add `--enable-oom-breakpoint` before rebuilding the entire pinned guest SpiderMonkey library. It would require a separate configuration/header/library/source manifest and actual four-site validation; it has not been built here. This is a guest build option, with no Wasmtime/wasmCloud change. The bounded scalar gate already supplies the required genuine failure coverage, so this larger build and general DEBUG rebasing remain optional engineering work.
