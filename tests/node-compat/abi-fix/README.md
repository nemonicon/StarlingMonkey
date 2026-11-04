# ComponentizeJS guest ABI corrections

The pinned ComponentizeJS 0.23.0 embedding misreads scalar WIT `u32` results at or above `2^31`. [componentize-u32-result.patch](componentize-u32-result.patch) corrects that exported-result conversion in guest code. The final candidate engine passes **339/339 actual-component checks** and **20 Wasmtime 42.0.1 invocations**: 16 scalar calls and four indirect list/record/result controls. The exact released engine remains a broken control, reproducing 138 scalar failures in the same 339-check corpus. See [results.json](results.json).

The scalar result patch is one narrow correction. A separately built guest-packaging splicer now corrects imported I32 arguments; its actual-component evidence is below. Neither change modifies a host.

## Source diagnosis and change

The generated bindings lift input values with `arg0 >>> 0` and lower scalar output with `toUint32(ret)`, whose implementation returns `val >>> 0`. This correctly produces ordinary nonnegative JavaScript Numbers. The embedding's `call()` then handles `CoreVal::I32` by reading `ret.toInt32()`, which requires an Int32-tagged JS value. SpiderMonkey stores large `u32` Numbers as Doubles, so the old code reads their raw payload instead of converting the numeric value. The observed bad outputs equal the low 32 bits of the IEEE-754 Double representation:

| WIT/JS value | Released output | Fixed output |
| --- | --- | --- |
| `2147483648` (`0x80000000`) | `0` | `2147483648` |
| `2342402100` | `109051904` | `2342402100` |
| `4294967295` (`0xffffffff`) | `4292870144` | `4294967295` |

The patch changes only the singular I32 return case to:

```cpp
static_cast<uint32_t>(JS::ToInt32(ret.toNumber()))
```

The already-lowered result is numeric. SpiderMonkey's existing non-GC `ToInt32(double)` performs numeric modulo conversion, then the unsigned store preserves the I32 bit pattern used by both signed and unsigned canonical ABI types. This adds no coercion callback, allocation or host capability. Signed and floating-point result paths retain their existing semantics.

The `CoreAbiSampleI32` function is an import-template sample, not the exported-result implementation. It, the other sample functions, and the Rust splicer's import-reader templates are unchanged. The actual emitted bindings and signature records are captured by `run.mjs`, hashed, and referenced in the results. [Pinned embedding source](https://github.com/bytecodealliance/ComponentizeJS/blob/4d812f5a7b524cea5bcfd565cac55f3fab876a57/embedding/embedding.cpp), [pinned splicer source](https://github.com/bytecodealliance/ComponentizeJS/blob/4d812f5a7b524cea5bcfd565cac55f3fab876a57/crates/spidermonkey-embedding-splicer/src/splice.rs)

## Executed coverage

[component.mjs](component.mjs) and [profile.wit](profile.wit) use WIT `u32` for the unsigned results throughout. No signed carrier, host-side bit reinterpretation or serialized-number workaround is used.

The 339 checks include:

- Direct, constant and computed `u32` outputs: 274 checks over eight boundary values and 128 deterministic generated inputs, including `0x80000000` and `0xffffffff`.
- Negative and boundary `s32` controls: 15 checks.
- `f32`/`f64` controls, including integer-tagged values, fractions, signed zero, infinities and NaN: 20 checks.
- `u32` lists and records, plus both success and error payloads in `result<u32,u32>`: 22 checks.
- In-guest JSON controls showing the values are correct before ABI transport: eight checks.

These execute through Jco's generated JavaScript loading real Wasm component core modules. The same compiled components are also invoked by the stock Wasmtime 42.0.1 CLI. Wasmtime checks the high scalar boundaries, constants, computed outputs, signed/float controls, a high-u32 list, a record containing high values, and both result variants. The CLI prints a shortest-roundtrip decimal for `f32`; the runner rounds only that displayed decimal with `Math.fround` for comparison. Unsigned integer checks compare the returned Numbers directly.

Both test components emit **zero external imports**. The native Buffer profile is present in the selected engine but unused by this fixture, isolating the result transport defect from Buffer and its codecs.

## Preserved artifacts and provenance

Base ComponentizeJS source: `4d812f5a7b524cea5bcfd565cac55f3fab876a57` (`0.23.0`). Patch SHA-256: `c70c1b76ae9ddeba7cbaad2861f1ecc03710da7241ca6365d00c9ece8243324b`.

| Engine | SHA-256 |
| --- | --- |
| Released broken control | `6094cd93d966f9bec9b01332db6e0eedbaf22f60b745c9f823f21e33cbd4d365` |
| ABI-only control, original native facade | `6daf1f03438aad3a14124b2dc09f95f09b91eac285233c2345cbd1a24b302748` |
| Combined final candidate release | `3f5bf602ad2d1507db5c1bcd5b938984aba9ca65af4c5a840b5bf8fcd09d370f` |
| Combined candidate with GC stress | `10d1c0e696deb43989d3b8005bda230c4fd6d603856a886883e0d94ee37fb779` |

The immutable ABI-only and candidate copies reside under `/tmp/starling-node-compat/improved-build/artifacts/`, named `starlingmonkey_embedding.abi-control.wasm`, `starlingmonkey_embedding.candidate.release.wasm` and `starlingmonkey_embedding.candidate.gc-stress.wasm`. Each has a `.wasm.build.json` sidecar. The ABI-only control and candidate have identical external embedding source hashes and patch digests, allowing native facade comparisons with the same ABI correction. [results.abi-control.json](results.abi-control.json) preserves the earlier isolated ABI-only regression; the main results reference the final release candidate.

[build-engine.sh](../build-engine.sh) now defaults to a separate `improved-build` work root and applies the patch after checking the pinned upstream source and patch hashes. Reapplication is idempotent and ambiguous source content is rejected. Metadata records `abiFixEnabled`, the base revision, patch hash and actual compiled embedding source hashes. Original baseline source directories and artifacts remain preserved. `NODE_COMPAT_ABI_FIX=0` selects a separately named, hash-checked pristine source/build for diagnostics; it does not silently remove the patch from an existing build.

## Reproduce

Install the pinned npm toolchain using [its package and lockfile](../toolchain/package.json). Use Node v22.14.0:

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
  tests/node-compat/build-engine.sh

NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-fixed.wasm \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 tests/node-compat/abi-fix/run.mjs
```

The normal runner requires a patched engine and verifies its patch/source provenance. `NODE_COMPAT_ABI_CONTROL_ONLY=1` runs only the released defect diagnostic and labels the output incomplete. Generated binaries, bindings and component files stay outside the checkout. Snapshot hashes identify individual runs; deterministic snapshot output is not claimed.

## Historical imported-callback defect

[callback-diagnostic.mjs](callback-diagnostic.mjs) composes the app with [callback-helper.wat](callback-helper.wat), a pure guest identity/constant component. `wasm-tools compose --no-imports` and final WIT inspection require zero external host imports. No custom host service or runtime modification is involved.

With the ABI-only fixed engine, a guest-to-guest `u32` call still passes an incorrect high argument: `2147483648` reaches the helper as `0`, and the other two high values reproduce the payload words in the table above. Low arguments work. A helper returning the constant `0xffffffff`, followed by the patched scalar export, returns the correct `4294967295`. Both Jco and Wasmtime reproduce these controls. See [callback-results.json](callback-results.json).

The separate `CoreTy::I32` imported-argument reader loads the JS value bits and uses `i32_wrap_i64` without converting Double-tagged numeric arguments. It is unchanged by this patch. [Pinned reader implementation](https://github.com/bytecodealliance/ComponentizeJS/blob/4d812f5a7b524cea5bcfd565cac55f3fab876a57/crates/spidermonkey-embedding-splicer/src/splice.rs#L598)

Run that explicitly scoped diagnostic with the same fixed engine, additionally setting `NODE_COMPAT_WASM_TOOLS` to pinned `wasm-tools 1.235.0`:

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_ENGINE=/path/to/abi-fixed-engine.wasm \
NODE_COMPAT_WASM_TOOLS=/path/to/wasm-tools-1.235.0 \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 tests/node-compat/abi-fix/callback-diagnostic.mjs
```

The scalar export correction does not establish complete Component Model ABI compatibility, imported-callback correctness, or complete Node.js/Buffer support.


## Imported I32 argument correction, version 1

[componentize-import-i32-v1.patch](componentize-import-i32-v1.patch) changes only `CoreTy::I32` argument extraction in the existing Rust-generated JSNative reader. The old reader loads the raw `JS::Value` then takes its low word. The replacement reuses the adjacent float readers' exact Int32 tag test (`0xFFFFFF81`). Int32-tagged arguments retain their existing path. Double-tagged canonical integers use `f64.reinterpret_i64`, `i64.trunc_f64_s`, then `i32.wrap_i64`. Every valid s32/u32 value fits in i64, including negative Doubles and high unsigned Numbers. The sample-function template contract and float/BigInt readers remain unchanged.

The patch SHA is `d300e345cb56a5bb1560f1f993c2cc763bca273e6bcf51e38aadc8e27d84782c`. It is a **packaging splicer correction**, separate from the native engine's scalar-result patch. The immutable `3f5bf6...` engine is identical in both regression arms. [import-v1-results.json](import-v1-results.json) records **333/333** patched Jco checks and **7/7** stock Wasmtime 42 invocations; the exact npm splicer control passes 183/333 and 5/7. Both application components are composed with a real guest helper and emit zero external imports. Tests cover generated/boundary u32 arguments, constant and computed calls, s32, f32/f64, u64, nonnegative s64, lists, flattened records and both result variants. Negative-s64 failures are recorded separately as a distinct pre-existing native BigInt defect, rather than counted as successes.

[raw-i32-reader.mjs](raw-i32-reader.mjs) exports the **actual generated reader function** from the real spliced core and invokes it from a pure guest probe. It does not reproduce the reader algorithm. The disposable probe writes raw Double Values into its scratch `vp[2]`, forcing negative Double carriers independently of SpiderMonkey boxing choices. The patched reader passes **9/9** versus **1/9** for npm, including `-2^31`, `-1`, `2^31` and `2^32-1`. The final diagnostic component has no host imports. [raw-i32-reader-results.json](raw-i32-reader-results.json) records the emitted function index and artifact hashes. This probe deliberately does not initialize SpiderMonkey or expose a deployment API.

### Local splicer build and selection

[build-splicer.sh](build-splicer.sh) applies the patch to exact ComponentizeJS commit `4d812f5a7b524cea5bcfd565cac55f3fab876a57`, builds with Rust/Cargo **1.96.1**, `wasm32-wasip1`, release and `--locked`, then uses pinned Jco **1.40.0** to generate an isolated package. Shared npm files, native engines and host executables stay unchanged. The package includes `splicer-build.json` with source, patch, lock, raw/component core and generated-file hashes. This is a local toolchain fork, not the released npm 0.23 artifact.

The upstream archive's Cargo.toml requires `js-component-bindgen 2.11.0` while its lock lists a local 2.10.1 entry without a registry checksum. [splicer-Cargo.v1.lock](splicer-Cargo.v1.lock) makes only the necessary entry replacement: published 2.11.0 with verified registry crate checksum `d73b9c04f15dd549239f5302dd6a80be973d055b93c6ad60b7d8d0c9ab07f9b9`. All other package versions remain fixed. The resulting lock SHA is `6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd`; the original lock SHA is preserved in the manifest. Cargo verifies registry checksums during `--locked` builds. No floating git dependency is introduced.

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_SPLICER_PROFILE=import-i32-v1 \
  tests/node-compat/abi-fix/build-splicer.sh

NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-build/package/src/componentize.js \
NODE_COMPAT_ENGINE=/path/to/scalar-ABI-fixed-engine.wasm \
  /path/to/node-v22.14.0 tests/node-compat/abi-fix/import-v1.mjs
```

Current profile callers use [componentizer.mjs](../componentizer.mjs). It requires an explicit patched module, known patch/lock/base pins, checks every generated manifest entry and separately checks hardcoded audited JS/core hashes. An explicit native engine is mandatory. Stock npm packaging is available only through an explicit legacy diagnostic opt-in. Historical benchmark scripts remain unchanged and retain their recorded stock packaging provenance. [loader-test-results.json](loader-test-results.json) records nine positive/negative gates, including stock refusal, missing engine and isolated manifest/JS/core tampering; even forging a manifest digest does not bypass known core pins.

The generated artifact pins currently describe the verified macOS arm64 build and exact recipe. A different platform or rebuild producing different binary bytes requires review and a new explicit artifact pin; the loader does not accept an arbitrary manifest's claims.


## Signed and unsigned I64 BigInt bridge correction, version 1

[componentize-i64-bigint-v1.patch](componentize-i64-bigint-v1.patch) fixes a separate native embedding defect discovered by the broader callback tests. Both `from_bigint64()` and singular `CoreVal::I64` export results previously accepted only `JS::detail::BigIntIsUint64`; a valid negative WIT s64 BigInt caused an abort. The new shared, nonallocating helper first accepts the existing entire u64 domain, then accepts `BigIntIsInt64` and converts its signed value to uint64 bits. The common core-i64 carrier consequently preserves `[-2^63,2^64-1]`. JavaScript/WIT bindings still distinguish s64 and u64. No sample function signature, host service, BigInt allocation, coercion callback or signed-carrier workaround is introduced.

The patch SHA is `c75bd3062ac03fce743901db2cab502b6ac60979679f23ef9f6a869488574cf4`, applied after the scalar-I32 patch. The combined embedding source SHA is `5893c8989d317d3aee95faea3048ad8665b7273c74f33e85e244d13c34c6b00b`. The existing `coreabi_to_bigint64` continues to create unsigned bits; generated lifting applies signed interpretation for WIT s64.

[i64-v1-results.json](i64-v1-results.json) records **377/377 Jco checks and 13/13 Wasmtime calls** against native engine `41207c7421113a6f2ea3e371edd9cfc67d6cfdd44e9d9a88152772b9207324c3`, using the same v1 packaging splicer for both arms. The preserved pre-I64 engine `680fb48a93921e5bfd077d12338d114913eecc5c6e6b12eb8f66e3e9cd8a554b` passes only six of the 13 host controls; seven negative-result/callback operations trap. Tests cover signed minimum, -1, zero, signed maximum, unsigned high/max, 64 generated bit patterns per domain, direct/local/callback/constant/computed paths, typed lists, records, and both result payload variants. Every composed component has zero external imports.

The verified release artifact is `/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.wasm` (9,455,855 bytes), with its build sidecar. [build-engine.sh](../build-engine.sh) applies this second native patch by default when the scalar fix is enabled; `NODE_COMPAT_BIGINT_FIX=0` retains a separate pre-I64 source/build/artifact for diagnostics. Builds now record the actual cache flags and compare complete source inventories before and after compilation. A changed input aborts metadata publication. Packaging splicer selection is recorded independently and is never described as compiled into native engine bytes.

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
  tests/node-compat/build-engine.sh

NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/path/to/audited-package/src/componentize.js \
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.wasm \
  /path/to/node-v22.14.0 tests/node-compat/abi-fix/i64-v1.mjs
```


## Disabled-clock errno correction, packaging version 2

The expanded DEBUG gate exposed a further independent pinned-splicer defect: Preview1 `clock_time_get` writes a timestamp but leaves the destination pointer as its return errno. [The tiny actual-stub diagnostic](../oom/clock-stub-results.json) reproduces return values 8, 64 and 1024 at those addresses, with no SpiderMonkey or Buffer involved and no external imports.

[componentize-clock-errno-v2.patch](../oom/componentize-clock-errno-v2.patch), SHA `57ace551f7d723cbf9faa41c42eda08feace9370f571175284e36c67d4c24da3`, removes the duplicate pointer load and emits success `i32.const 0` after the timestamp store. It leaves timestamp selection and feature policy unchanged. This is a syscall-result correction; it does not establish correct epoch rebasing or freeze policy for all scheduling APIs.

The isolated v2 package keeps the I32 patch, adds this separately identified clock patch and preserves the v1 package. Its packaging version is `componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1`. The actual generated primary core SHA is `edad4a6f77dfc307a42096bb90d2b7c8c37c893e7fb2325d785cf0d50fa52214`; generated JavaScript and the second core match v1. The raw Rust core SHA is `38a0c2cce5bc0b67272bad2885137517adbaa1f6b4b0e8ca036c44d429d79b12`. [clock-stub-fixed-results.json](../oom/clock-stub-fixed-results.json) verifies success errno at all four addresses while retaining a nonzero timestamp and zero imports. The loader's nine gates also pass against v2.

`build-splicer.sh` now defaults to v2 in `/tmp/starling-node-compat/import-abi-clock-v2-build`; `NODE_COMPAT_SPLICER_PROFILE=import-i32-v1` explicitly reproduces the older scoped correction. [componentizer.mjs](../componentizer.mjs) validates both known selections independently and exposes `getComponentizerPins(provenance)` for callers that must recheck exact packaging artifacts, including the HTTP adapter. It returns a fixed known map after checking the patch selection; it does not trust arbitrary hashes from a provided manifest.

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
  tests/node-compat/abi-fix/build-splicer.sh

# Select the current versioned guest packager explicitly:
export NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js
```

All versions remain bounded local guest-toolchain corrections. They do not establish complete Node.js, Buffer, Component Model ABI or lifecycle compatibility.


## Current native recipe and lock enforcement

The allocation error-path follow-up release is `/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.allocation-r2.wasm`, SHA `99fdaa97c2fbdea67cb7e5463d3dd2ca10c6981615acb4483d442079f6aab65c` (9,455,863 bytes). It preserves the prior `41207c...` release at its original path. The source change reports a pending OOM after a genuine failed `JS_malloc`; fault injection and recovery validation are documented separately in [the OOM gate](../oom/README.md).

[cmake/build-crates.cmake](../../../cmake/build-crates.cmake) already copied the repository's versioned aggregate `runtime/crates/staticlib-template/Cargo.lock`; its SHA `46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a` matches the observed prior release/debug projects. The new default-off `NODE_COMPAT_LOCKED_RUST` option invokes Corrosion's existing `LOCKED` argument. The audited recipe explicitly enables it. The observed Cargo command contains `--locked`, and metadata records that actual command plus the generated manifest/lock hashes. The recipe checks the lock after configure and build, the manifest before/after build, and all 191 repository input hashes before/after compilation. No source mutation is accepted between those checkpoints.

`NODE_COMPAT_ARTIFACT_TAG=allocation-r2` selects a distinct output suffix. Raw DEBUG artifacts remain separate: the OOM normalization helper removes only DWARF custom sections, verifies direct byte equality of every standard/retained custom section, and records raw/derived/tool hashes. It preserves DEBUG allocator simulator code. The recipe performs this derivation automatically for OOM builds.

[run-current.mjs](run-current.mjs) uses the explicitly selected versioned packager and preserves the earlier export-only runner/results as historical evidence. Its first v2 run against `41207c...` passes 339/339 actual Jco checks and 20/20 Wasmtime scalar/indirect checks; released native bytes still reproduce 138 failures with that same v2 packager. [results.current.json](results.current.json) records this independent packaging selection.


[Current validation summary](current-validation.json) ties each corpus to its exact engine and package receipt. The allocation-r2 release now also passes the export corpus's **339/339 + 20/20 Wasmtime** checks with v2. The current v2 I64 rerun passes **377/377 + 13/13** on that same release; its raw generated-reader probe passes **9/9**. The canonical imported-I32 corpus deliberately keeps the older native engine identical in both arms and passes **333/333 + 7/7** with v2. That isolates the guest-packaging correction from later native changes.

[Complete splicer source audit](splicer-source-audit-results.json) additionally verifies all **270 files per actual source tree** against the exact archive, allowing only the named Rust patch(es) and lock repair. An isolated unrelated Rust-file mutation is rejected. These receipts were observed after the original builds and leave their immutable package manifests unchanged. The future recipe now performs the same verification before Cargo and after packaging and compares both tree digests. That augmented path has not yet been rerun through Cargo; the verifier itself has passed against both actual trees. The v1 loader also rejects unknown `additionalPatches` metadata rather than permitting ambiguous provenance.


## DEBUG memory limitation and allocator validation

[DEBUG diagnosis and engineering options](debug-memory-findings.md) documents the verified upstream +64 memory-view defect, the source-based base-aware codegen inventory and supported release OOM-breakpoint alternative. General unrebased DEBUG packaging now fails before Wizer. The only admitted exception is the exact hash-pinned zero-import `run()->s32` allocator diagnostic, with postpack export/import checks; there is no arbitrary legacy DEBUG override. [The OOM results](../oom/results.json) validate all four real failures, recovery and moving-GC checks through that safe scalar carrier. The loader has **18** positive/negative gates, including rejection of indirect/expanded/importing diagnostic worlds.


Normal packaging now requires a byte-matching build sidecar with an unambiguous observed `Release` or `Debug` configuration. A missing sidecar is permitted only under explicit `legacyDiagnostic:true` for released engine SHA `6094cd93d966f9bec9b01332db6e0eedbaf22f60b745c9f823f21e33cbd4d365`. The known `3f5bf6...` release may use that explicit diagnostic mode with its historical sidecar, whose configuration predates actual cache capture. No other unknown configuration is accepted. Renaming a DEBUG binary and omitting its metadata is rejected. Current export/import diagnostic callers select the narrow exception explicitly; ordinary release, HTTP and scalar-OOM callers retain their checked current metadata. [Legacy engine guard controls](legacy-engine-guard-results.json) exercise the released broken control, held-constant historical release and normal allocation-r2 release without host imports.
