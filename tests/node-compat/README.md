# Native Node compatibility integration tests

The latest [real-component lifecycle results](../../docs/node-compat/nextjs-lifecycle-results.md)
retain two passing95-check context comparisons and a failing cloned-response
cancellation regression. Run the repository-only evidence check with
`python3 -I -B tests/node-compat/async-context/next-lifecycle-root-results-v1/check-saved.py`.
That command verifies the saved failure; it does not execute or accept a new engine.

These tests require a ComponentizeJS embedding engine rebuilt from this checkout
with `ENABLE_BUILTIN_NODE_COMPAT=ON`. The runner refuses the released engine,
checks its build metadata/hash, and leaves the native `node:buffer` and
`node:child_process` imports in the application bundle. It never includes the
semantic facade or a reference hex kernel in the application.

Use the exact Node.js **v22.14.0** oracle, ComponentizeJS **0.23.0**, Jco **1.40.0**,
Rolldown **1.2.16**, and unmodified Wasmtime **42.0.1**. Generated engines, bundles,
components, transpiled files and results stay outside this checkout.

```sh
mkdir -p /private/tmp/starling-node-compat/native-toolchain
cp tests/node-compat/toolchain/package*.json /private/tmp/starling-node-compat/native-toolchain/
npm ci --prefix /private/tmp/starling-node-compat/native-toolchain --no-audit --no-fund

NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/native-toolchain \
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
NODE_COMPAT_SPLICER_PROFILE=import-i32-clock-v2 \
  bash tests/node-compat/abi-fix/build-splicer.sh

NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js \
NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/native-toolchain \
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
NODE_COMPAT_ENTROPY_MODE=OFF \
NODE_COMPAT_PATH=1 \
NODE_COMPAT_EVENTS=1 \
NODE_COMPAT_STRING_DECODER=1 \
NODE_COMPAT_ASSERT=1 \
NODE_COMPAT_QUERYSTRING=1 \
NODE_COMPAT_UTIL=1 \
NODE_COMPAT_ARTIFACT_TAG=foundations-v7 \
  bash tests/node-compat/build-engine.sh

NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/native-toolchain \
  /path/to/node-v22.14.0 tests/node-compat/bundle-test.mjs

NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/native-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js \
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.entropy-entry-v1.OFF.path-1.events-1.string-decoder-1.assert-1.querystring-1.util-1.foundations-v7.wasm \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 tests/node-compat/run.mjs
```

The commands build the current source with all optional foundations selected.
The [v7 bounded util evidence](milestones/foundations-v7/README.md) includes
293 captured inputs and native/host results. Its broader profile promotion is
withheld: ordinary synchronous event-listener exceptions can still be swallowed
during initialization. The next guest checkpoint fix is being validated separately;
this recipe currently reproduces that known failing policy. Earlier
[foundations-v6 evidence](milestones/foundations-v6/README.md) remains unchanged.
Use a fresh artifact tag/build root when reproducing a changed source tree.
The recipe rejects an existing engine or adjacent receipt before downloads or
configuration. Accepted historical checkpoints
are [allocation-r2](milestones/allocation-r2/README.md),
[entropy-v1](milestones/entropy-v1/README.md) and
[foundations-v3](milestones/foundations-v3/README.md).

`build-engine.sh` requires both reviewed scalar-export/BigInt fixes and applies
the actual private deployed-entry patch. Its adjacent `.wasm.build.json` records
actual CMake options, selected module manifests, all source hashes, locked Cargo
commands and complete OpenSSL source/archive/configure/library receipts. Sources
are guarded before and after compilation. Actual registration compile commands
must match all six optional flags. Separate policy/mode/feature source and
build directories preserve the original experiments; artifact tags preserve
accepted bytes. Historical unpatched ABI diagnostics use their archived recipes.

`NODE_COMPAT_EVENTS=0` omits the optional Events registration and manifest.
`NODE_COMPAT_PATH=0` omits the optional Path registration and manifest.
`NODE_COMPAT_STRING_DECODER=0`, `NODE_COMPAT_ASSERT=0` and
`NODE_COMPAT_QUERYSTRING=0` independently omit their registration and manifests.
`NODE_COMPAT_UTIL=0` omits util/types/sys; it adds no host capability.
All six optional flags default to0 and require the core profile. Their finite
generated headers are separate; normal CMake builds execute no Node/npm code.
`NODE_COMPAT_ENTROPY_MODE=RUNTIME_ONLY` selects the separate secure-entropy engine;
its components must retain random and explicitly select
`wasi:random/random@0.2.10`. The main zero-import Buffer runner uses OFF. Every
policy component requires exact `selectedInterfaces`, and the wrapper audits the
final bytes after any selected core wrapping. Defaults that emit another WASI
version are rejected, not relabeled.

Current component tests select the audited guest-packaging splicer through
`componentizer.mjs`. The versioned imported-I32 patch is separate from the native
engine's scalar-export/BigInt patches. The v2 package also corrects disabled-clock
errno reporting; v1 records remain useful controls. Its isolated package and locked Rust graph do not
modify the installed npm toolchain or a host runtime. Selection is explicit via
`NODE_COMPAT_COMPONENTIZE_MODULE`; stock packaging is admitted only by the
explicit legacy diagnostic option. Historical measurements retain their original
source and toolchain records.
`NODE_COMPAT_OUTPUT` selects an external output directory (default
`/tmp/starling-node-compat/native-output`). Its `results.json` identifies the
engine/component hashes, native module imports in the bundle, final component
WIT/imports, oracle case counts, repeated calls, Wasmtime execution, and expected
initialization failures. No result is claimed until that runner completes.

The main fixture covers exact exports, named/default/global identities, every
stub export on invocation/construction, safe namespace inspection, snapshot
brands/codecs/views, shared versus copied storage, offsets, typed-array
inheritance/species, limits/errors and unavailable APIs. A seeded oracle corpus
checks 381 UTF-8/hex strings and 250 byte arrays against Node. Hex cases include
NUL, lone surrogates, non-ASCII characters, odd lengths and invalid-pair positions.
Shared/resizable/detached rejection is exercised when the engine exposes ways to
create those inputs. A separate unbundled fixture exercises both native bare and
prefixed registry keys and per-specifier namespace caching. Top-level call,
construction, rejected top-level await and unknown named imports must fail
componentization. The final test world has zero host imports and one `run` export.

`profile-bundler.mjs` is deliberately narrow: admitted builtin imports become
canonical externals before adapter resolution. Literal builtin `require` calls
in local `.cjs` files imported by explicit path receive the builtin's ESM default
object through a small lexical CommonJS wrapper. Only default interop is provided. Dynamic require, require
aliasing/shadowing, filename bindings and unadmitted builtin modules are rejected.
This resolver is not a general npm CommonJS package loader.
The custom engine installs the canonical global Buffer; the bundler does not
inject a second implementation. `bundle-test.mjs` checks that mapping independently
and verifies that no JavaScript Buffer adapter entered the graph.

Import and wrapper helper names are chosen outside every identifier in the
original CommonJS source, including nested parameters. Regression checks keep
colliding local variables intact and verify a nested require still returns the
native default object.

For a development stress engine, rebuild with `NODE_COMPAT_GC_STRESS=1` and run
against `starlingmonkey_embedding.abi-i32-i64-v1.gc-stress.entropy-entry-v1.OFF.path-1.events-1.string-decoder-1.assert-1.querystring-1.util-1.foundations-v7.wasm` with a separate output directory.
The engine forces collection only at rooted native-kernel boundaries. This adds
no production GC global or host capability and must be disabled for performance
measurements. It does not replace OOM injection, sanitizers, or SpiderMonkey's
complete GC zeal suite. The subsequent [wasmCloud HTTP execution](wasmcloud/README-host.md)
and [corrected-clock A/B protocol](bench-clock-v2/README.md) have separate artifacts and
capability contracts from this pure integration fixture.

## Original executed result, 2026-11-03

These hashes identify the original, pre-optimization engine. The later
[allocation and ABI follow-up](../../docs/node-compat/buffer-optimization-and-abi-fix.md)
uses separate release/stress artifacts and preserves this record.

The compact [execution and provenance record](results.json) preserves the measured
imports, reports, source hashes, skipped cases and component sizes without binaries.

The normal and GC-stress engines both passed the full corpus, two calls of the
same Jco-instantiated component, direct Wasmtime 42.0.1 execution, four expected
componentization failures, and an unbundled alias/caching fixture including
cached dynamic ESM imports. First-time deployed builtin loading has a separate current regression gate; these historical results do not cover it. Both final worlds contain zero imports and only `run`.
The runner checked all 188 recorded repository source hashes against this
working tree before execution. SharedArrayBuffer is absent in this engine;
shared-input construction cases were skipped explicitly. Resizable and detached
input rejection passed.

| Build | Engine SHA-256 | Main test component bytes | Main test component SHA-256 |
| --- | --- | ---: | --- |
| Normal | `da69618da72315c3b3f20d105708fd625a3b7c0691f49329201036c3c2fd5796` | 17,848,631 | `97e04d144b48199aee4757c2f0f046d534faad889f0bdde86cfc340c17101ee6` |
| GC stress | `0362f52d6f918ff1ab9e63f62f6ea66432dacf8392d6d8eef2531f131f8371ac` | 17,850,183 | `7148c1014bc3b6102895a9cd025459e27ed4532f28dabd5ee98fba022d8eb027` |

Full reports from this run are external:
`/tmp/starling-node-compat/native-output/results.json` and
`/tmp/starling-node-compat/native-stress-output/results.json`. Component hashes
identify this run; deterministic snapshot builds are not asserted. The main
component contains the large oracle corpus and test assertions, so its byte size
is not a product-size comparison or evidence of native performance improvement.

The later HTTP fixture passed on both Wasmtime 42.0.1 and the official wasmCloud
2.11.0 local host, using the same component bytes. Its additional standard HTTP
transport interfaces are enumerated in [the host record](wasmcloud/README-host.md);
the pure fixture above and both A/B benchmark arms still have zero host imports.
