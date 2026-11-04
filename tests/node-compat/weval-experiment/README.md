# Weval gate 2.4 experiment

This page and its original parent-directory scripts/pins preserve the historical v3 source-audited proposal and **unexecuted build/packaging template**. The separate [frozen v5 experiment](v5/README.md) now executes the guarded build against validated production sources, preserving these earlier bytes. Results from the new version are recorded separately; this historical proposal is not an execution receipt.

## Verified baseline and integration

| Input | Pin | Verification |
| --- | --- | --- |
| SpiderMonkey | `FIREFOX_147_0_4_RELEASE_STARLING`, Firefox commit `9dab3d6f643e926a340c391ea30968e940390dec` | Actual `release_weval` archive downloaded: 185,640,018 bytes; SHA `f108286a1b9c35aeee89a803b073175a077633ffea5bbe4c3b85fcc85230dba0`. Not extracted here yet. |
| Weval | `v0.5.1`, commit `47164ae9e5bacfdcc23ddaeb2fa491c8f61c644d` | macOS arm64 archive: SHA `10068ba146171f8729cdeeabe3449791ad8d50d33406b5ec544837704cc4b17b`. |
| Binaryen | version 123 | macOS arm64 archive: SHA `74428be348c1a09863e7b642a1fa948cabf8ec9561052233d8288e941951725b`. |
| ComponentizeJS / Jco | 0.23.0 commit `4d812f5a7b524cea5bcfd565cac55f3fab876a57` / 1.40.0 | Same reviewed native ABI/entry patches and audited v2 guest splicer as the accepted ordinary Release engine. |
| JavaScript adapter | Actual Jco 1.40 Buffer adapter, unenv 2.0.0-rc.24 | Existing A/B module-identity/bundle gates reused; no replacement reference kernel. |

[pins.json](pins.json) records archive sizes, URLs, source hashes, cached tool hashes and other platforms' published asset digests. Only the macOS arm64 assets have local download verification. The cached executable hashes have not yet been compared against newly extracted archive payloads; [prepare-assets.mjs](prepare-assets.mjs) makes that a required gate before use. [Weval release](https://github.com/bytecodealliance/weval/releases/tag/v0.5.1), [SpiderMonkey assets](https://github.com/bytecodealliance/StarlingMonkey/releases/tag/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING).

The actual repository mechanisms are:

- `cmake/spidermonkey.cmake` selects `release_weval` with `WEVAL=ON`; `SPIDERMONKEY_BINARIES` overrides that selection, so reusing the ordinary Release directory would be wrong. Its source-build route adds forced portable-baseline/AOT-IC/pbl-weval options.
- `cmake/weval.cmake` selects Weval 0.5.1. The npm wrapper also selects 0.5.1 but trusts an existing binary without a content check; the experiment uses an explicit verified path.
- `CMakeLists.txt` generates `starling-ics.wevalcache` by running the raw engine on `null.js` with writable `--cache`, then discards the transformed Wasm. This is a **generic IC cache**, not application-workload training. Rebuilding that ALL target deletes/recreates the cache; copy the accepted cache before another build.
- ComponentizeJS's Weval CMake target depends on that cache but copies the raw embedding. Its Makefile separately copies the cache into `lib/starlingmonkey_ics.wevalcache`.
- Application packaging separately uses `enableAot`, `--cache-ro`, the actual application initializer and `--init-func componentize.wizer`, producing specialized Wasm. Explicit `engine` wins over automatic engine selection, but default `aotCache` still points at the stock package cache. Both must be supplied and hash-bound together. [Pinned packaging implementation](https://github.com/bytecodealliance/ComponentizeJS/blob/4d812f5a7b524cea5bcfd565cac55f3fab876a57/src/componentize.js).

`USE_WASM_OPT=OFF` still executes `wasm-opt --strip-debug -O0`; ordinary Release uses `-O3`. The C++ compiler remains in Release mode. Comparing ordinary and Weval engines therefore compares the supported backend/optimizer pipelines, not an isolated Weval switch. Within each native/JavaScript pair, keep the same engine, cache, tools, patches, world and features. Existing ComponentizeJS tests select their AOT path with `WEVAL_TEST=1`; this is a functional pathway, not speed evidence.

## Isolated recipe

[build-engine.mjs](build-engine.mjs) defaults to a no-build plan. Its build mode requires an explicit accepted OFF Release engine and its complete source freeze. It clones a new private source tree, overlays only that engine's verified native inputs, copies the **frozen** normal build recipe, and applies the exact transformations in [recipe-transform.mjs](recipe-transform.mjs). Production `build-engine.sh` and CMake are unchanged; later Events changes cannot enter the v3 frozen source/recipe accidentally.

The changed settings are Release, `WEVAL=ON`, `USE_WASM_OPT=OFF`, the verified `release_weval` distribution, explicit verified Weval/Binaryen tools, the `_weval` embedding filename and separate artifact names. Existing ABI/entry patches, strict initializer, OpenSSL audit and locked Rust build remain. The receipt requires identical native and embedding source manifests to the accepted base; the matching cache must be generated from the exact copied raw engine. It records actual cache/optimizer commands, cache/tool hashes and requested/observed flags.

Initial tool settings are explicit `RUST_MIN_STACK=67108864` and `RAYON_NUM_THREADS=4`, rather than ComponentizeJS's free-RAM-dependent default. Their adequacy is untested. If adjustment is needed, preserve the failed run and change both arms together in a new recorded experiment. Packaging uses only that small explicit tool environment; it does not inherit arbitrary application environment values.

```sh
# Default: prints the plan, no clone/configure/build.
/path/to/node-v22.14.0 tests/node-compat/weval-experiment/build-engine.mjs --plan

# Later, after the coordinated build window:
NODE_COMPAT_WEVAL_BASE_ENGINE=/tmp/starling-node-compat/foundations-v3/native-freeze/off-path.engine.wasm \
NODE_COMPAT_WEVAL_SOURCE_FREEZE=/tmp/starling-node-compat/foundations-v3/native-freeze/source \
NODE_COMPAT_WEVAL_BASE_RECIPE=/tmp/starling-node-compat/foundations-v3/native-freeze/build-engine.sh \
NODE_COMPAT_WEVAL_BUILD_ROOT=/tmp/starling-node-compat/weval-experiment/custom-release-v1 \
  /path/to/node-v22.14.0 tests/node-compat/weval-experiment/build-engine.mjs --build
```

Only a new namespace is accepted. The scripts require the preserved accepted freeze plus the pinned SDK/cbindgen/CPM cache; this is not a clean-checkout-only reproduction claim. Syntax checks, no-build plan execution, exact pure recipe transformation and `bash -n` pass; native configuration/link/cache generation are untested.

## Gates before measurement

1. Extract and compare official tool payloads; record the actual Weval distribution's `js-confdefs.h`, selected SDK, compiler, tool versions and library hashes. Require Release. General DEBUG indirect bindings remain unsafe under the current JS adapter and are excluded.
2. Build the private engine/cache; validate complete source/configuration receipts and emitted imports. Reject stock engine/cache fallback and cache mutation after either arm. A Weval intrinsic or nonselected host import must not survive deployment.
3. Exercise real-component full-range u32/s32/floats, imported guest-to-guest callbacks, signed/unsigned i64 and indirect string/list/record/result cases using the existing corrected ABI gates. Their harnesses still need an explicit audited AOT-option route; ordinary passing results do not establish Weval passing results.
4. Run strict initialization, top-level unsupported calls/constructors, named/default exports, aliases and first deployed uncached builtin imports. Weval uses `--dir` while Wizer uses `--mapdir`; initialization paths, environment/clocks/entropy policy and snapshot/resumption need independent checks.
5. Run the full supported Buffer corpus and relevant Web codec tests, rooting/moving-GC checks in a separate test build, reuse/cancellation checks and standard-host instantiation. Verify target Wasmtime 42 and unmodified wash/wasmCloud 2.11 with the selected standard HTTP world before broader portability claims. No new host service or host patch is part of this plan.

## Native/JavaScript measurement

[package-arms.mjs](package-arms.mjs) is an unexecuted correctness/size builder based on the hash-pinned corrected-clock experiment. Both arms use the **same custom Weval engine and generic read-only cache**. The native arm imports the real registered module; the JavaScript arm bundles the actual Jco adapter and checks implementation identity, global Buffer, encoding support and module inventory. Both use the same workload, world, preview adapter, explicit AOT options and zero selected interfaces. Every setup/run checksum must match pinned Node before timing.

Use host timing with the unchanged stock Wasmtime benchmark protocol; report compilation/componentization separately from startup, setup, first batch and warmed throughput. Use multiple fresh instances, counterbalanced arm order, retained raw samples and all component hashes. Repeat componentization to measure final raw/gzip size variation and packaging cost/peak memory. Record linear-memory requests and process RSS with their limits: neither is exact live JavaScript heap. Keep tiny and large inputs separate, because the existing native measurements already show different memory tradeoffs.

This pair measures duplicate JavaScript-adapter overhead with the native profile installed in both arms. It does not establish the minimum profile-disabled component size. A later ordinary/Weval pipeline matrix must use the same accepted source freeze and disclose the different static-library/optimizer pipeline. No native-win prediction, uniform memory claim, whole-application speedup or statistical significance is assumed.
