# Private direct UTF-8 codec experiment

This archived experiment changes a **private copy of existing `TextEncoder::encode`**, so the captured web encoder used by `Buffer.from(string, 'utf8')` remains the shared implementation. Its original controls and measurements preserved production sources, Buffer exports/facade/kernel and host runtimes. The later production v5 implementation has a [separate functional validation](README-production.md); the private performance numbers below do not automatically describe those new bytes. The private OOM gate remains unverified.

The motivation is a measured tradeoff: the corrected-clock 64-byte native UTF-8 case was much faster than Jco but requested about 26 MiB more linear memory and had higher peak RSS; the large-input case behaved differently. Source analysis identifies an allocation route worth testing, not the cause of that entire gap.

## Exact source and lifetime proof

The accepted baseline is the frozen v3 OFF engine, SHA `3d106756f65c6dd18b590ba3f41b4cc760635c27fb738b678ead8bccd8a21897`, with 268 native inputs. [pins.json](pins.json) records its recipe/input/patch hashes and actual SDK30/SM147 syntax checks. The private patch is [text-encoder-direct-v1.patch](text-encoder-direct-v1.patch); it changes existing `builtins/web/text-codec/text-encoder.cpp`, not a Buffer-specific duplicate encoder.

The old route is `buffer-facade.mjs::Buffer.from` → captured `TextEncoder::encode` → `core::encode` → `JS_EncodeStringToUTF8`. It creates owned null-terminated storage, adopts it into an explicit ArrayBuffer and creates a Uint8Array view. Successful adoption avoids a byte copy, but even a tiny result uses that external allocation and explicit buffer. The facade's WeakSet is weak; its presence alone is not evidence of permanent output retention.

The replacement uses actual public APIs from Firefox commit `9dab3d6f643e926a340c391ea30968e940390dec`:

1. Preserve the original omitted/undefined → fresh empty Uint8Array branch and receiver checks.
2. Root `JS::ToString(cx, args[0])`; propagate its exception rather than continuing with an empty failed `HostString`.
3. Ensure a non-linear string is linear, then call `JS::GetDeflatedUTF8StringLength`. The raw linear pointer's lexical scope ends before later GC/allocation.
4. Allocate a rooted `JS_NewUint8Array` with the exact byte length. No output pointer has been borrowed yet.
5. Enter `JS::AutoCheckCannotGC`, acquire `JS_GetUint8ArrayData`, and rederive the linear pointer from the **updated rooted string** with `JS_ASSERT_STRING_IS_LINEAR`. Call `JS::DeflateStringToUTF8Buffer` directly into that storage.
6. End the borrow/no-GC scope before any further operation that may collect or report an error. Return the rooted output.

`js/public/String.h` explicitly states the linear type is a syntactic distinction over the same GC thing; rooting the original string and rederiving after allocation is appropriate. The pinned `CharacterEncoding.cpp` implementations of the length/deflate functions use internal no-GC scopes and pure Latin-1/UTF-16 converters. The encoder replaces lone surrogates with U+FFFD and preserves embedded NUL/BOM bytes. [Public API](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/public/CharacterEncoding.h), [implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/CharacterEncoding.cpp).

For sufficiently small results, `JS_NewUint8Array` can keep its bytes inline and create its ArrayBuffer lazily; large results still use managed backing allocation. The exact configured limit is exposed by actual `JS_MaxMovableTypedArraySize`. This removes the **explicit external UTF-8 stage/adoption**; it is not a claim that SpiderMonkey performs no internal malloc or that every size is faster. A managed destination can require zero initialization, while the old route avoided that extra write and performed a redundant length scan in `core::encode`. Measure both small and large inputs.

`JS_EncodeStringToUTF8BufferPartial` was assessed but is unnecessary for this exact-size route. Its public contract permits OOM without reporting an exception and partial output; its pinned wrapper itself uses no-GC. Existing `encodeInto` uses it and is unchanged here, including its separate unreported-OOM concern. The regular `encodeInto` regression cases are not an OOM-fix claim for that method.

## Verified private artifacts

| Artifact | SHA-256 / result |
| --- | --- |
| Direct Release | `3dd0fcae2887a01454720225446a545f4df99ad6a79e9f68efbb5180175a7358` |
| Same-project original encoder control | `0bb5743ba97dbbc8d2c7636fe1ae35ad37e135ea523f9c8939004198fc4c21f8` |
| Direct rooted-GC Release | `0665355d7d32adf0b658527577cd896e6fe9ca038d51b3633669a19be9f932ce` |
| Direct codec component | `43f1e493561e1ba56401f50bffe7f85e13833fba34e00048a089c81245f8f75b` |
| Rooted-GC codec component | `319475ddfb59f7ea09fce800c95df881aed9db3973b4a419b2a85f4b89a65ed9` |

Both direct engines pass the [shared exact-Node Web codec cases](node-oracle-results.json): **8 groups, 77,769 assertions, 78 observations**, on three calls to one Jco instance and a fresh unmodified Wasmtime 42 instance, with zero imports. Tests cover 14 Unicode vectors, primitive conversion, six exception-identity stages, coercion order, exact fresh Uint8Array/backing/offset relationships, independent outputs, rope construction, 117 `encodeInto` capacity/offset combinations and captured methods under prototype/global-Uint8Array poisoning. Buffer checks compare supported bytes and valid view relationships, allowing Node's different pool offsets.

Both direct Release and rooted-GC Release also pass the existing **381-string / 250-byte Buffer corpus**, aliases/global/default relationships, supported errors, stub calls/constructors and expected initialization failures in actual components. The private GC flag forces shrinking collections only at rooted boundaries before/after allocation and after the byte borrow ends. It is verified in the actual web-codec compile command.

The paired original-encoder control fails the Node suite on both hosts: its first expected thrown case, `encode(Symbol(...))`, returns instead of throwing TypeError. This supports the source finding that old `encode` does not check failed `core::encode` before continuing. The direct candidate passes that case and all sentinel exception checks. The full suite stops at that first control mismatch; later control cases are not claimed to pass.

Receipts currently live under `/tmp/starling-node-compat/utf8-direct/{codec-release,codec-gc,codec-paired-control,buffer-release,buffer-gc}`. The paired engine/source freezes are under `paired/{candidate,control}-freeze`. Original candidate receipt bytes are preserved; an explicit relocated sidecar maps its 269 frozen source inputs after the live private project was restored to the original encoder. Earlier executed runner copies are preserved with hash verification when the paired-control allowlist was extended. No old report or patch was overwritten.

## Controlled pair and build mechanism

[build-engine.mjs](build-engine.mjs) copies the **frozen v3** recipe and 268 input files into a new private git/source/build namespace, applies only the codec patch and adds the private test header. It does not take later Events changes from the production checkout. Ordinary ABI/entry patches, locked Rust, OpenSSL audit and standard interface selection remain.

An initial GC setup attempt was rejected: the outer CMake cache saw `CXXFLAGS`, but the Starling child replaced the actual flags. That failed artifact is preserved; no Web-GC result is attributed to it. The corrected private recipe uses existing `CMAKE_PROJECT_ComponentizeJS_INCLUDE` and `target_compile_definitions(builtin_web_text_codec ...)`. [audit-build.mjs](audit-build.mjs) checks the actual compile command rather than a requested option alone. No production CMake change is required.

The first candidate's separately rebuilt OpenSSL archive differed from original v3 because paths/timestamps affected linked data and relocations, despite matching source/flags. It is contextual evidence, not the final causal control. The final control was built by restoring only the original encoder CPP **in the same private project**, retaining the harmless header, install paths, flags, library/cache and recipe. The pair has identical 269 source path sets with exactly one changed file, identical native embedding patches and **identical libcrypto archive SHA** `5b43fdc4983c51776a0336dcc8754b9c0bece5bbc29e408db2c1d0e41552823e`. Exact build caches, compile commands, library bytes and Makefiles are preserved.

The [benchmark builder](build-bench.mjs) rejects a different source/flags/library pair. The [driver](compare.mjs) separates packaging, Wasmtime compilation and measurement, retains raw samples and counterbalances arm order. Primary comparison is same-project original/native versus direct/native. Optional actual-Jco arms are a diagnostic control. Historical v3/Jco timing remains context, not the paired causal control.

The primary loop reads result bytes/length without `.buffer`; lazy backing materialization can change the tradeoff for applications that read `.buffer`. A separate backing-access scenario is appropriate. Retained-memory/GC behavior, allocator retention and thresholds must not be inferred from a single RSS or linear-memory high-water value.

## Completed ordinary Release measurement

The [artifact receipt](release-benchmark-artifacts.json), [separate compilation receipt](release-benchmark-compilation.json) and [raw measurements](release-benchmark-results.json) use **only the frozen ordinary Release pair**. GC stress and OOM instrumentation are disabled in both actual compile configurations. Both components have zero imports and the exact same application bundle SHA `9d71d79960413e024f71bbfedecf6dcfa9c4939c7cf1866179752dd9ea4d628e`. The inputs are valid ASCII strings for `Buffer.from(..., 'utf8')`; both setup/full checksums and timed-loop fingerprints match Node 22.14.0.

The unchanged, hash-pinned Wasmtime 42 benchmark host measured two counterbalanced arm-order rounds, three fresh instances per process and seven timed batches per instance: **24 instances and 168 timed batches overall**. Each arm/size has six fresh instances and 42 retained batches. Packaging and Wasmtime compilation finished before throughput timing. No DEBUG execution, fault simulation, GC-metadata extension, guest-memory inspection or access-tier change was part of this measurement.

| ASCII payload | Candidate/control throughput | Peak process RSS, MiB: control → direct | Largest linear-memory request, MiB: control → direct |
| --- | ---: | ---: | ---: |
| 64 bytes | **1.088×**; opposite-order rounds 1.089× / 1.066× | **51.64 → 24.58** | **35.06 → 9.06** |
| 512 KiB | **1.660×**; opposite-order rounds 1.682× / 1.646× | 36.125 → 36.109 | 20.5625 → 20.5625 |

Median instantiation was 32.94 → 32.08 microseconds in the 64-byte scenario and 27.58 → 27.54 microseconds in the large scenario. This excludes engine creation and precompiled-component deserialization, which the raw host reports separately. Setup was 0.727 → 0.680 milliseconds for 64 bytes and 318.870 → 315.054 milliseconds for 512 KiB; setup includes input construction and the full checksum. First-batch times are also retained separately from warmed batches.

One componentization per arm produced 11,842,584 → 11,847,913 raw bytes, and 3,991,507 → 3,997,669 gzip bytes. These are observed artifact sizes, not a replicated minimum-size claim. Single-run packaging times are recorded but are not a controlled packaging-speed comparison.

This local result supports the direct allocation route for the measured workload: the small case's memory high-water falls substantially, while the large case improves throughput with essentially unchanged memory high-water. It does not establish a uniform result across Unicode inputs, applications that materialize `.buffer`, full applications or other hosts. RSS includes host/runtime/code/allocator retention; largest desired linear memory is a ResourceLimiter observation, not live JS heap or a leak measurement. Within-instance batches are correlated. No statistical-significance or complete compatibility claim follows.

Read-only independent review recomputed the digest chain, raw/aggregate percentiles, throughput, round ratios, maxima and startup units without finding a substantive issue. [release-benchmark-receipt.json](release-benchmark-receipt.json) identifies the exact copied raw reports. Historical v3/Jco measurements are contextual and were not substituted for this same-project native pair.

## OOM gate unverified; telemetry remains a proposal

[text-encoder-direct-testing.h](text-encoder-direct-testing.h) uses the real DEBUG SpiderMonkey FailureSimulator, with no JS control. It asserts actual simulator trip, null API result and pending OOM, resetting before JS catches. Linearization is selected only for `!JS_StringIsLinear`, so a passing fault confirms an actual non-linear input and allocation checkpoint. Existing-entry/code paths do not manufacture errors.

The dedicated [scalar fixture](oom-component.mjs) was designed to preserve all four unchanged Buffer fault/recovery checks and add linearization/Uint8Array allocation checks, 32 recovery pairs, backing/source retention and coercion exception identity. It uses the exact permitted `run() -> s32` diagnostic world, not general DEBUG string/list bindings. Its EngineState guard is **fixture-bounded**: `finish_pre_initialization` precedes `bindExports`. The fixture has plain function exports and no late encode getters; it is not a universal deployed-entry barrier.

The DEBUG build and scalar component packaging completed, but the first Jco call trapped in `direct_testing::FaultScope::finish` for the linearization scope. No successful scalar result or passing OOM report was emitted. The exact failed native assertion has not been diagnosed, and no six-scope OOM pass is claimed. Existing Release/GC correctness results and the prior four-site Buffer evidence remain separate. Failed log: `/tmp/starling-node-compat/utf8-direct/oom-run.log`; packaged artifacts: `oom-result/`; raw/derived engine receipts: `oom-v1/build/artifacts/`. These artifacts are preserved without a retry.

Automatic review separately flagged the source-only OOM diagnostic follow-up as possible cybersecurity risk. That work was stopped. There has been no rephrasing retry, access-tier change, raw guest-memory observation, malformed ABI carrier or pointer probing. This review block is distinct from the actual guest assertion failure. Subsequent ordinary Release performance and production functional validation remain separate from this blocked, unverified gate.

For natural allocation diagnostics, actual `JS_GetGCParameter` can sample GC bytes, total/minor counts, major **slice** count and nursery size outside measured loops; additive nursery/slice callbacks can count reasons without allocation. Preserve runtime's existing `JS_SetGCCallback` logger. Such GC bytes are not exact live heap. `CollectRuntimeStats` additionally needs a verified allocator-specific `MallocSizeOf` callback; do not substitute an invented allocator measurement. No telemetry extension or live-heap accounting has been executed yet.
