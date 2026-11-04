# Native Buffer versus the existing Jco JavaScript adapter

This benchmark uses the same rebuilt release SpiderMonkey engine for both arms. `native` imports the registered `node:buffer`. `jco-js` bundles the **actual** Jco 1.40.0 `dist/node-builtins/buffer.js` adapter and its pinned unenv 2.0.0-rc.24/Feross implementation through `createBufferBuiltin`; it does not approximate that implementation with the test reference kernel. An independent external native-registry import proves that the selected JavaScript Buffer is a different object. Snapshot initialization also asserts that the selected implementation owns global Buffer. Both components have the same capability-free WIT world and zero host imports.

`workload.mjs` is shared with the exact Node v22.14.0 oracle. It prepares only each operation's input, outside throughput timing, and tests hex encode/decode, byte copying, and ASCII UTF-8 encode/decode at 64, 4,096, 65,536 and 524,288 input bytes. Each 64-byte batch uses 10,000 operations; larger inputs process 1 MiB per batch with identical iteration counts in both arms. An initial 4 MiB calibration showed about 1.46 seconds for one JavaScript hex-encode batch at 4,096 bytes, so the primary batch volume was reduced before collecting the full run. Hex source text is twice the input byte count and remains inside the profile's source-string cap. Setup executes one operation and computes its full FNV-1a checksum; every operation batch consumes length/first/middle/last in an O(1) fingerprint. Results are discarded between iterations. Full setup and batch checksums must match Node before measurement. Both arms use Rolldown's normal tree shaking (`treeshake:true`) and Jco's Node-plugin default target (`es2016`).

The result transport is signed `s32`, preserving every checksum bit through host reinterpretation as `u32`. The separate [ABI diagnostic](abi-diagnostic.mjs) found incorrect high-`u32` result lowering with the released and current embeddings; string-return diagnostics verified that Buffer contents and in-guest FNV computations were correct. This experiment does not change the embedding or native kernels to work around that unrelated binding defect.

Build artifacts stay outside the checkout:

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
NODE_COMPAT_ENGINE=/path/to/rebuilt/starlingmonkey_embedding.wasm \
  /path/to/node-v22.14.0 tests/node-compat/bench/build.mjs

# Build the stock Wasmtime measurement host; see host/Cargo.toml/Cargo.lock.
CARGO_TARGET_DIR=/tmp/starling-node-compat/bench-host-target \
  cargo +1.96.1 build --manifest-path tests/node-compat/bench/host/Cargo.toml --release --locked

NODE_COMPAT_BENCH_HOST=/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host \
  /path/to/node-v22.14.0 tests/node-compat/bench/run.mjs
```

`build-results.json` records adapter/source/engine/component hashes, emitted WIT, sizes and the oracle workload. `wasmtime-results.json` records every raw batch duration and process/memory observation plus median/IQR summaries. Optional `NODE_COMPAT_BENCH_OPERATIONS` and `NODE_COMPAT_BENCH_SIZES` select a disclosed subset. Defaults are three fresh instances, three warmup batches and seven timed batches per instance. Arm order alternates by scenario. Run when builds and other CPU-heavy work are idle.

The measurement host uses Rust/Cargo **1.96.1**, separate from the guest engine's pinned Rust **1.88.0**. Wasmtime 42 requires Rust 1.91 or later, so invoking unqualified Cargo from the repository would select an unsuitable guest toolchain. The measured guest engine is a Release build with `WEVAL=OFF` and `USE_WASM_OPT=ON`; no Weval/AOT experiment was requested. These results are specific to that mode and do not compare a Weval-enabled JavaScript implementation.

The stock Wasmtime 42.0.1 host uses an empty linker. It compiles and serializes each component in a separate process; measurement processes load only those locally produced artifacts. Throughput uses persistent instances and host `Instant`, separating compilation, deserialization, instantiation, setup, first batch and warmed batches. No process is launched per Buffer operation. RSS is sampled outside timed intervals and includes the runtime/code/allocator. ResourceLimiter's largest requested linear memory is recorded separately; it is neither total guest heap nor process RSS.

Both arms include the installed native profile because the engine is held constant. Consequently, the size difference measures incremental JavaScript adapter overhead in that engine, not savings relative to a separate minimal profile-off deployment. Input is ASCII and valid hex, so results describe these bounded operations. They do not establish a general Node compatibility or application speedup. GC-stress engines, compiler time and setup/FNV work are excluded from warmed operation measurements.

The JavaScript adapter supplies a broader Buffer API than this bounded profile. Component-size and retained-memory differences can therefore include API-surface cost as well as implementation choices; they cannot be attributed solely to moving hex loops into C++.

Human-readable throughput is **payload MiB/s**. For hex decode, the API receives twice that many ASCII bytes and produces `size` decoded bytes; its logical payload is `size`. The raw JSON's legacy `inputMiBPerSecond` fields use this payload-normalized definition. Other selected operations receive `size` input bytes. Ratios compare identical operations and inputs in both arms.

The per-result fingerprint uses a constant number of sampled accesses, rather than a full output scan. Character access can still materialize a JavaScript rope string. String-conversion timings therefore include this observable result access, rather than measuring creation of an unread lazy representation alone. Seven batches within an instance are correlated; three fresh instances are the independent setup units, rather than 21 independent trials.

## Recorded primary run

Recorded 2026-11-03T00:02:20.299Z on Apple M2 (8 logical CPUs), darwin arm64. All 40 arm/scenarios completed: 120 fresh instances and 840 timed batches, with matching Node setup/run checksums and no linear-memory growth failures. Both emitted components have zero host imports. Raw observations are in [results.json](results.json); exact component/adapter/engine pins and workloads are in [artifact-manifest.json](artifact-manifest.json).

The following ratio is JavaScript median batch time divided by native-profile median batch time. Values above one favor the native profile; values below one mean the native profile was slower. These are this Release, non-Weval configuration on one machine.

| Operation | 64 B | 4 KiB | 64 KiB | 512 KiB |
|---|---:|---:|---:|---:|
| hex-encode | 3.31x | 108.19x | 375.59x | 401.09x |
| hex-decode | 20.33x | 460.72x | 689.90x | 763.70x |
| byte-copy | 0.86x | 0.86x | 0.96x | 0.92x |
| utf8-encode | 21.03x | 819.74x | 2198.46x | 2521.60x |
| utf8-decode | 10.70x | 484.29x | 2221.30x | 2862.36x |

At 4 KiB, throughput and process peak RSS were:

| Operation | Native payload MiB/s | Jco JS payload MiB/s | Native peak RSS MiB | Jco JS peak RSS MiB |
|---|---:|---:|---:|---:|
| hex-encode | 293.30 | 2.71 | 26.34 | 34.86 |
| hex-decode | 159.38 | 0.35 | 35.22 | 30.17 |
| byte-copy | 302.19 | 350.41 | 35.17 | 35.81 |
| utf8-encode | 299.21 | 0.37 | 35.22 | 49.39 |
| utf8-decode | 311.89 | 0.64 | 25.78 | 33.56 |

The observed copy medians were about 4–17% slower with the bounded facade. Memory was mixed: native hex decode at 4 KiB had a higher process peak RSS, despite faster execution. RSS cannot be treated as isolated guest-heap use, and this run does not establish a uniform memory reduction. Largest requested linear memory, all raw timings, per-instance medians, and batch IQRs are retained in the JSON.

| Artifact/startup observation | Native | Jco JS |
|---|---:|---:|
| Raw component bytes | 10,991,198 | 11,273,296 |
| Gzip bytes | 3,694,472 | 3,804,714 |
| One Cranelift compile, ms | 5090.94 | 5100.92 |
| One serialization, ms | 4.52 | 4.44 |
| Fresh instantiation median, microseconds | 27.35 | 33.92 |

The JavaScript component added 282,098 raw bytes in this fixed profile-enabled engine. This is incremental adapter cost, not a minimal deployment comparison. Compilation and serialization observations are single runs, separate from warmed throughput. Fresh instantiation uses locally precompiled images and excludes engine creation/deserialization/compilation; the detailed report records those phases independently. It is not a cold-machine startup claim.
