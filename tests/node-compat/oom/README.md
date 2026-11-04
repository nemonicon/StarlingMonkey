# Native Buffer allocator-failure gate

This is a separate debug-engine test of four native allocation API scopes. It
does not change the bounded Buffer API or add JavaScript testing exports, host
services or deployed capabilities. Normal builds leave
`NODE_COMPAT_OOM_TESTING=OFF`; the instrumentation compiles out. A release
SpiderMonkey artifact cannot enable this test by merely defining the flag.

The guarded scalar gate passed on the recorded DEBUG + compacting-GC-stress
engine: one Jco instance returned `67583`, `133119`, and `198655`; a fresh
Wasmtime 42.0.1 instance returned `67583`. The final component has zero imports,
SHA-256 `a689b71a1010580bcd7e46f330e23b6e7b2d4d691cc81261bcecbc4eec3b52ed`.
[`results.json`](results.json) records the exact engine, four selected fault
points, raw statuses, source manifests, normalized-debug derivation and scalar
loader audit. This is the bounded gate's execution evidence, separate from the
earlier failure controls described below.

## Mechanism and coverage

[`oom-testing.h`](../../../builtins/node-compat/oom-testing.h) uses the pinned
SpiderMonkey `js::oom::FailureSimulator`, available in its actual debug artifact.
The verified upstream implementation interprets the count relative to its
current counter. Each scope selects the next main-thread allocation checkpoint,
fails subsequent allocations until the API returns, and resets the simulator
before any native owner unwinds or JavaScript catches the pending exception.
The previous thread classification is restored. See the pinned
[utility implementation](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/util/Utility.cpp#L45)
and [simulator declarations](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/public/Utility.h#L138).

In this fixture, top-level snapshot initialization uses both kernels
successfully and the first exported `run()` triggers each selected API scope
once. This observes the fixture's phase behavior; the `EngineState` check is
not a general boundary for every snapshot-time binding step, since
`finish_pre_initialization` can precede ComponentizeJS `bindExports` completion.
Native assertions require that the actual simulator
tripped, the selected API returned failure, and `JS_IsThrowingOutOfMemory` is
true. An unused checkpoint, a successful API recovery or an unrelated failure
aborts the test instead of passing it.

| Point | Actual native API | Owner already live when failure occurs |
| --- | --- | --- |
| decode UTF-8 staging | `JS_EncodeStringToUTF8` | Rooted input string |
| decode output view | `JS_NewUint8Array` | Rooted input string and owned UTF-8 temporary |
| encode staging | `JS_malloc`, with genuine-null `JS_ReportOutOfMemory` | Rooted input view and its backing buffer |
| encode output string | `JS_NewStringCopyN` | Rooted input view/backing and owned output staging |

The selected failure is the first allocation checkpoint **inside each API**.
This does not enumerate every internal allocation of those APIs. A tracked
deleter delegates to the same `JS::FreePolicy` used by `JS::UniqueChars`; every
kernel exit asserts zero live owned temporaries and equal acquisition/release
counts. The later decode/string failures exercise real cleanup after an earlier
native allocation succeeded. These counters cover native-owned temporary
buffers, not all SpiderMonkey heap objects or general heap leak detection.

The public fixture retains snapshot-created Buffers, backing ArrayBuffers,
offset views, an independent copy and encoded/decoded results. It checks their
contents, identities and private brands after each failure, then performs 32
successful encode/decode pairs per invocation. One Jco instance is called three
times; Wasmtime invokes a fresh instance once. Genuine OOM is the pinned
SpiderMonkey primitive string `"out of memory"`, whose actual native OOM status
is separately asserted. The fixture distinguishes it from the profile's
unsupported-operation Error and bounded-allocation RangeError. See
[the pinned OOM exception implementation](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/vm/JSContext.cpp#L253).

## Scalar diagnostic boundary

The test world is `starling:node-compat-oom-test@0.2.0`, with exactly
`run: func() -> s32` and no imports. The same in-guest checks use real strings,
Buffers and Error objects; only their test-report carrier is numeric. A pass
returns `(invocationCount << 16) | 0x7ff`. A negative number identifies the
failed stage: 1 initial integrity, 2 UTF-8 staging OOM, 3 decode view OOM,
4 decode recovery, 5 encode malloc OOM, 6 encode JS string OOM, 7 recovery pairs,
8 unsupported Error, 9 bounded RangeError, or 10 final integrity. The pass mask
records snapshot/initial integrity (bits 0–1), the four genuine failures
(bits 2–5), decode recovery (bit 6), 32 recovery pairs (bit 7), the two error
distinctions (bits 8–9), and final integrity (bit 10). Later invocations retain
the completed first-invocation fault bits and must complete new recovery/error
checks without firing a fault again.

This separate DEBUG engine cannot safely use ComponentizeJS indirect canonical
memory bindings: its debug `GetMemBuffer()` view begins at address 64 while the
bindings use absolute pointers. Independent controls demonstrate broken
string/list carriers without any Buffer or fault operation. The audited
packager loader rejects general DEBUG componentization and permits only this
exact hash-pinned, import-free scalar diagnostic world. No broad override or
indirect-result observer is part of the acceptance path. Release interoperability
is tested separately; this gate does not establish DEBUG string/list ABI
support. Keeping the carrier scalar does not relax any native OOM, ownership,
Buffer-content, real-string or Error-object predicate.

## Reproduction

Install the exact toolchain from `../toolchain/package-lock.json` and use Node
v22.14.0. The engine build driver owns download hashes and records the actual
debug archive, CMake options and source manifest in its `.build.json` sidecar:

The debug artifact is `spidermonkey-static-debug.tar.gz` at
`FIREFOX_147_0_4_RELEASE_STARLING`, SHA-256
`49a5b610dace59331bc699ac53a99d9f4c3b4579441efa66147aa8e96b4ffcee`.

```sh
export NODE_COMPAT_NODE=/absolute/path/to/node-v22.14.0/bin/node
export NODE_COMPAT_BUILD_ROOT=/tmp/starling-node-compat/oom-build
export NODE_COMPAT_OOM_TESTING=1
export NODE_COMPAT_GC_STRESS=1
tests/node-compat/build-engine.sh

export NODE_COMPAT_ENGINE=/absolute/path/to/printed-normalized-debug-engine.wasm
export NODE_COMPAT_WASMTIME=/absolute/path/to/wasmtime-42.0.1
export NODE_COMPAT_TOOLCHAIN=/absolute/path/to/pinned-toolchain
export NODE_COMPAT_COMPONENTIZE_MODULE=/absolute/path/to/import-abi-clock-v2-build/package/src/componentize.js
"$NODE_COMPAT_NODE" tests/node-compat/oom/run.mjs
```

Use the artifact path printed by the build driver. The runner requires matching
debug/OOM build metadata, checks every source-manifest hash, preserves external
native imports during bundling and rejects any final host imports. It records
the audited patched packager provenance, component/engine/source hashes and
raw results in `results.json`; full
generated files remain under `NODE_COMPAT_OOM_OUTPUT` (default
`/tmp/starling-node-compat/oom-gate`). Prior baseline engines and benchmark
artifacts are not overwritten.

If later source work has begun, set `NODE_COMPAT_ENGINE_SOURCE_ROOT` to the
preserved source tree for this immutable engine. Every archived source must
still match its build manifest; this does not bypass source checks. The report
records the selected source root separately from the current test sources.

The raw debug binary contains roughly 237 MB of DWARF custom sections. Its first
packaging attempt failed in the generated splicer byte-list return guard after
snapshotting. The derived artifact removes only `.debug_*` custom sections;
all standard section payloads and retained custom payloads, including `name`
and `component-type:bindings`, must compare byte-for-byte. The helper preserves
the raw artifact and records both hashes, exact command, section inventory and
tool/helper hashes in the derived sidecar. Its current tool-binary pin is the
verified macOS arm64 wasm-tools 1.235.0 artifact; other host platforms need an
additional reviewed tool pin. DEBUG allocator checks and simulator code remain
intact.

The current build driver invokes the normalizer automatically and preserves a
separate `.raw.wasm` artifact/sidecar. To normalize an archived raw engine
independently, use `node strip-debug.mjs RAW_ENGINE DERIVED_ENGINE WASM_TOOLS`;
the input must still contain DWARF. Do not feed the already normalized output
back into this helper.

## Limits

This gate covers four kernel API allocation scopes, recovery and temporary
ownership. It does not establish exhaustive engine OOM safety. Facade and web
codec allocations, module installation, ArrayBuffer materialization before the
selected scope, snapshot/bootstrap OOM and every internal allocation index
remain outside this test. It assumes the current single-threaded guest. The
debug fault engine is an acceptance artifact, not a deployment or performance
artifact. The initial DEBUG + forced compacting-GC attempt using the v1
packager trapped in SpiderMonkey scheduling before the fault scope. The v2
clock-stub correction lets the identical engine reach the actual allocator
faults without adding a clock import. The exact enabled GC setting and final
combined gate outcome must be read from `results.json`; source
inspection and successful syntax checks alone do not satisfy this gate.

## Independent clock-stub finding

[`clock-stub-diagnostic.mjs`](clock-stub-diagnostic.mjs) executes a tiny core
module through the actual packager, independently of Buffer or SpiderMonkey.
The v1 results in [`clock-stub-results.json`](clock-stub-results.json) show that
the disabled preview1 clock stub writes a nonzero build timestamp but returns
the output pointer as errno: destinations 8, 64 and 1024 produce errors 8, 64
and 1024, respectively, instead of success 0. The final diagnostic module has
zero imports. [`componentize-clock-errno-v2.patch`](componentize-clock-errno-v2.patch)
removes the extra stack value and returns errno 0 after the timestamp store.
The patch's exact base/patched-source hashes are checked by the separate
packager build recipe.

The observed debug trap is in GC scheduling's timestamp subtraction. The
pinned [`TimeStamp` subtraction](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/mozglue/misc/TimeStamp.h#L417)
asserts that both timestamps are non-null; negative differences are allowed.
[`ClockTimeNs`](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/mozglue/misc/TimeStamp_posix.cpp#L68)
ignores the `clock_gettime` result after one-time startup validation. The bad
errno can therefore leave its timespec uninitialized, but the diagnostic does
not capture either timestamp operand at the GC trap. A specific null operand
or clock-origin regression is not claimed as verified causality.

The same DEBUG + forced-GC engine and v2 packager subsequently passed that
earlier scheduling trap and reached the third native allocation scope. The
[`unreported-malloc-control.json`](unreported-malloc-control.json) control
records the exact trap offset/disassembly: the simulator tripped and
`JS_malloc` returned null, but no OOM exception was pending. The production
kernel now explicitly calls `JS_ReportOutOfMemory` only after that genuine
null allocation result. The [pinned API](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/jsapi.cpp#L1134)
uses [`maybe_pod_malloc`](https://github.com/bytecodealliance/firefox/blob/FIREFOX_147_0_4_RELEASE_STARLING/js/src/vm/MallocProvider.h#L50),
which does not report the exception itself. This control exposed a real error
propagation bug; it is not counted as a passing allocator-failure gate.

Run the same actual-core regression against the corrected explicit packager:

```sh
NODE_COMPAT_CLOCK_STUB_EXPECT=fixed \
NODE_COMPAT_COMPONENTIZE_MODULE=/absolute/path/to/v2/package/src/componentize.js \
"$NODE_COMPAT_NODE" tests/node-compat/oom/clock-stub-diagnostic.mjs
```

The fixed variant requires errno 0 for every destination, a nonzero timestamp
and zero imports, and writes `clock-stub-fixed-results.json` separately. That
[`fixed report`](clock-stub-fixed-results.json) records the actual v2 packager
passing all four destinations with errno 0, nonzero timestamps and zero imports.
The v1 failing control remains separate; the Rust patch alone is not counted as
execution evidence.
