# Toolchain and initialization hardening

These changes close discovered dependencies before Phase 3 API expansion.
They are versioned guest-side changes against pinned ComponentizeJS
`4d812f5a7b524cea5bcfd565cac55f3fab876a57` (0.23.0) and StarlingMonkey
`54b3329b3ce818fd1f244e871e9c259b63667cda`, plus the recorded working-tree
profile sources. They do not modify Wasmtime/wasmCloud or add a host service.
The [execution ledger](execution-status.md) remains the roadmap status source.

## Imported I32 arguments

The splicer's `CoreTy::I32` reader previously wrapped the raw JS Value bits.
High-u32 Numbers are Double-tagged, so the reader passed payload bits instead
of the numeric value. The [versioned Rust patch](../../tests/node-compat/abi-fix/componentize-import-i32-v1.patch)
retains the Int32-tagged path and converts Double values through
`i64.trunc_f64_s` then `i32.wrap_i64`. The full normalized signed/unsigned
32-bit integer domain fits that intermediate conversion. It does not change
the import-template sample functions or require a custom host capability.

The [paired component regression](../../tests/node-compat/abi-fix/import-v1-results.json)
uses the same native engine in both arms and composes a pure guest helper,
leaving zero final imports. The fixed splicer passes 333 checks and seven
Wasmtime invocations; the released splicer fails 150 of the 333 checks. A
separate actual-reader test also forces negative Double carriers, avoiding an
assumption that all signed integers are always Int32-tagged.

The isolated build uses an exact checked-in Cargo lock repair: only
`js-component-bindgen` changes from the upstream lock's local 2.10.1 entry to
the published 2.11.0 required by the pinned Cargo.toml. Registry checksum and
every other dependency remain pinned. This is a local fork, not the released
npm binary. The original lock and released package remain preserved.

## Signed I64 BigInts

The existing native `from_bigint64` and scalar `CoreVal::I64` return path accepted
only `BigIntIsUint64`, rejecting negative values legitimately lowered for WIT
`s64`. The [separate native patch](../../tests/node-compat/abi-fix/componentize-i64-bigint-v1.patch)
first accepts the full unsigned domain, then accepts `BigIntIsInt64` and stores
the corresponding 64-bit pattern. This is a nonallocating conversion using
existing SpiderMonkey APIs. It preserves high-u64 values and negative-s64 bits.

The [i64 regression](../../tests/node-compat/abi-fix/i64-v1-results.json) passes
377 actual component checks and 13 Wasmtime calls with the patched native
engine. Coverage includes minimum/-1/zero/maximum signed values, high/full
unsigned values, generated values, local and guest-callback calls, constants,
computed results, lists, records and result payloads. The broken engine passes
only six of the 13 isolated host controls. Final components have zero imports.
The new release artifact is `starlingmonkey_embedding.abi-i32-i64-v1.wasm`,
SHA-256 `41207c7421113a6f2ea3e371edd9cfc67d6cfdd44e9d9a88152772b9207324c3`.
This does not assert complete Component Model ABI compatibility.

## Snapshot rejection and debugger-disabled initialization

With the profile selected, `Engine::eval_toplevel` now checks its tracked
unhandled-rejection set after the final pre-snapshot job/GC cleanup checkpoint.
It rejects remaining failures with `ERR_SM_NODE_INITIALIZATION_REJECTION` in
the diagnostic, while preserving original rejection reports. Checking only the
initial tracker notification would reject promises that a later initialization
job legitimately handles. Profile-disabled builds keep the previous policy.

`create_initializer_global` also installs `print` only when the existing
debugger implementation is enabled. Its disabled stub previously returned false
without a pending exception, causing an actual upstream initializer to fail.

The [selected upstream record](../../tests/node-compat/upstream/phase1-results.json)
verifies nine initialization vectors, 19 adapted Starling E2E sources, 15
ComponentizeJS builtin fixtures and both export-buffer ownership callbacks.
The baseline records preserve four initialization holes before the fix.
The [harness notes](../../tests/node-compat/upstream/README.md) name every
adaptation and unreached assertion; this is not an untouched full CTest/Vitest
or WPT run. Nine of ten integration routes pass (81 subtests); the remaining
OpenSSL entropy failure is still open.

## Disabled-clock stub errno

The clock-disabled splicer writes a timestamp for Preview1 `clock_time_get`
but leaves its destination pointer as the errno return value. A tiny actual-core
[diagnostic](../../tests/node-compat/oom/clock-stub-results.json), without Buffer
or SpiderMonkey, observes errno 8/64/1024 for pointers 8/64/1024; the required
success result is zero. Its final core has zero imports.

The [clock patch](../../tests/node-compat/oom/componentize-clock-errno-v2.patch)
retains the timestamp write and returns zero. The
[fixed diagnostic](../../tests/node-compat/oom/clock-stub-fixed-results.json)
passes all four pointer cases. The v2 isolated packager includes both this and
the imported-I32 patch. It is selected separately from the native engine using
`NODE_COMPAT_COMPONENTIZE_MODULE` and verified exact JS/core/source/lock pins.

DEBUG forced-GC testing exposed a null-TimeStamp assertion. The malformed errno
is proved independently; which timestamp operand was null was not captured.
The controlled retry changes only this packager while keeping the same debug
engine, GC flag and zero-import world. That retry's result must establish any
causal claim. A backwards nonzero clock value alone does not explain the
specific assertion: the pinned subtraction permits signed differences.

The controlled retry passes that earlier GC trap and catches both decoder OOMs,
then exposes a separate native staging-allocation failure. Disassembly proves
the simulator tripped and `JS_malloc` returned null, but no OOM exception was
pending. The existing API uses `maybe_pod_malloc`; the encoder previously
returned false without reporting that failure. Its private allocation helper
now calls `JS_ReportOutOfMemory` on the genuine null return. The
[failed control](../../tests/node-compat/oom/unreported-malloc-control.json)
preserves the exact trap/offset and source provenance. The corrected staging
helper now passes the bounded [accepted allocator gate](../../tests/node-compat/milestones/allocation-r2/README.md): all four real native failure scopes,
32 recovery pairs, three retained Jco calls and a fresh Wasmtime call pass.

The intervening string/list diagnostic failures were independent: pinned
DEBUG `GetMemBuffer` exposes a view beginning at byte64 while canonical bindings
use absolute addresses. [The source and control evidence](../../tests/node-compat/abi-fix/debug-memory-findings.md) records this displacement.
General DEBUG packaging fails fast. The accepted no-import/no-argument scalar
world retains every internal Buffer/error/ownership predicate and never uses
indirect canonical output. It proves those bounded failure/recovery scopes;
it does not fix the general DEBUG ABI or establish exhaustive engine OOM.

The allocation-r2 release, SHA-256
`99fdaa97c2fbdea67cb7e5463d3dd2ca10c6981615acb4483d442079f6aab65c`,
also enforces the existing aggregate Rust template lock through Corrosion's
real `LOCKED` option. Its receipt records the generated manifest/lock,
before/after hashes and the actual Cargo `--locked` command. Generic
profile-disabled CMake behavior is preserved.

The historical performance records predate this correction. They remain
observations of their exact artifacts, but the current toolchain needs refreshed
GC/memory/performance measurements before the roadmap's empirical gate closes.

## Explicit package and build selection

`componentizer.mjs` requires an explicit audited native engine and an explicitly
selected isolated packaging module. Stock packaging is admitted only for named
legacy diagnostics. Package, platform, componentizer and generated core/JS files
are hash-checked; current HTTP packaging independently rechecks the same known
pins before composing the existing `stubWasi` API. An arbitrary manifest digest
cannot authorize arbitrary replacement bytes.

Build metadata now records actual CMake options, cache/compile-command hashes,
native patches and a separate packaging reference. A before/after source
inventory detects input drift. A formatting-only edit during one debug build
was caught by the source gate; a clean recompile against the agreed source was
required. Matching pre/post hashes are not a general proof against transient
edits; build inputs must remain frozen during compilation.

The fault engine's DWARF-only normalization preserves every standard section
and retained custom section byte-for-byte. It avoids the splicer's 256-MiB
list-return limit while preserving DEBUG code and allocator simulation. It is
a test artifact, not a deployment/performance engine.
