# Recorded classic-stream component measurement

The recorded run completed168 workers (126 timed,42 pilots), with a terminal source audit. This numerical analysis recomputes all21 summaries from saved worker stdout/observed records. It does not rerun the benchmark, establish full compatibility, or record checkpoint acceptance. Integrity/provenance review is separate.

**Outcome:** the registered binding saves component bytes but shows no consistent warm-speed gain over the identical bundled factory. The canonical factory is faster than the different stock provider in the four measured pipelines, yet its median peak process RSS is higher in all four of those pairings. Large-input results are close to the copy/validation/FNV control, so they do not isolate stream overhead.

## Method and units

Each timed process contributes the median of its seven correlated batch samples; the reported central time is the median of three process medians. Times below divide by the actual shared pilot-selectedN, not the scenario’s requested maximum16. N=1 for18 pairs,2 for one and6 for two. Order is AB/BA/AB (a2:1 first-arm imbalance); no samples are pooled as independent and no significance claim is made. All process ranges and seven original values are retained in the JSON/CSV.

Ratio = B time per iteration / A time per iteration; >1 means higher observed A throughput. One64-byte pipeline iteration consumes8192 bytes; one512KiB-chunk pipeline consumes4194304 bytes. Processed MiB/s uses1048576 bytes/MiB and includes validation/FNV work. The zero-byte stream-construction control uses iterations/s, not byte throughput. Controls are never subtracted.

## Three separate comparisons

| Comparison | A | B | Scope |
| --- | --- | --- | --- |
| Same engine | native-on | canonical-on | Registered JS binding versus identical bundled JS factory; same native Buffer/Events/StringDecoder/private FIFO. No C++ stream state machine. |
| Whole profile | canonical-on | canonical-off | Identical application bundle with optional classic installation ON/OFF. |
| Different provider | canonical-on | stock-on | Untouched Jco/readable-stream provider with its own dependencies/microtask scheduler; different provider domain. |

| Comparison / pipeline chunk and operation | A ms/iteration | B ms/iteration | A throughput/B | A−B median peak process RSS (MiB) |
| --- | ---: | ---: | ---: | ---: |
| same-engine-binding / view-64B | 11.271 | 11.195 | 0.9933× | -80.56 |
| same-engine-binding / copy-64B | 11.156 | 11.002 | 0.9862× | +8.22 |
| same-engine-binding / view-512KiB | 3421.757 | 3392.710 | 0.9915× | -6.67 |
| same-engine-binding / copy-512KiB | 3407.002 | 3411.883 | 1.0014× | -0.67 |
| whole-profile / view-64B | 11.294 | 11.308 | 1.0012× | +74.23 |
| whole-profile / copy-64B | 11.043 | 11.149 | 1.0096× | -1.56 |
| whole-profile / view-512KiB | 3397.650 | 3411.101 | 1.0040× | +24.78 |
| whole-profile / copy-512KiB | 3394.389 | 3405.537 | 1.0033× | -20.64 |
| different-stock-provider / view-64B | 11.263 | 12.039 | 1.0689× | +16.78 |
| different-stock-provider / copy-64B | 11.058 | 11.907 | 1.0768× | +36.69 |
| different-stock-provider / view-512KiB | 3397.001 | 3445.692 | 1.0143× | +8.03 |
| different-stock-provider / copy-512KiB | 3392.461 | 3428.482 | 1.0106× | +0.33 |

Same-engine pipeline A ratios span0.9862–1.0014: three observed slowdowns and one small gain. Whole-profile pipeline ratios are1.0012–1.0096, alongside a larger component; these small differences do not establish a CPU advantage. Different-provider canonical pipeline ratios are1.0106–1.0768. These comparisons cannot be chained into a new paired native-versus-stock result.

## Measured controls — not subtracted

| Comparison / control | N | A ms/iteration | B ms/iteration | A throughput/B |
| --- | ---: | ---: | ---: | ---: |
| same-engine-binding / checksum-input-only | 1 | 6.788 | 6.690 | 0.9856× |
| same-engine-binding / byte-input-and-copy-construction-only | 1 | 3416.581 | 3405.637 | 0.9968× |
| same-engine-binding / stream-construction-and-clean-close-only | 1 | 0.991 | 0.957 | 0.9657× |
| whole-profile / checksum-input-only | 1 | 6.975 | 6.720 | 0.9635× |
| whole-profile / byte-input-and-copy-construction-only | 1 | 3402.254 | 3402.958 | 1.0002× |
| whole-profile / stream-construction-and-clean-close-only | 6 | 0.680 | 0.681 | 1.0018× |
| different-stock-provider / checksum-input-only | 2 | 6.627 | 6.612 | 0.9978× |
| different-stock-provider / byte-input-and-copy-construction-only | 1 | 3398.940 | 3401.777 | 1.0008× |
| different-stock-provider / stream-construction-and-clean-close-only | 6 | 0.686 | 0.792 | 1.1545× |

The4MiB copy/construction/consume control takes about3.40s per iteration, the same scale as the large pipelines (about3.39–3.45s). Per-byte equality checks and FNV remain timed and may dominate. Subtracting this control would not yield a valid isolated stream cost. Counterexamples include registered-binding checksum/construction-control slowdowns and canonical-versus-stock checksum-control slowdown.

## Actual component bytes and process memory

| Arm | Final component bytes | MiB |
| --- | ---: | ---: |
| native-on | 13,056,344 | 12.451 |
| canonical-on | 14,168,969 | 13.513 |
| canonical-off | 13,449,990 | 12.827 |
| stock-on | 16,487,001 | 15.723 |

Registered binding versus bundled canonical saves1,112,625 bytes (7.85%). Enabling the unused classic installation for the same bundled canonical application adds718,979 bytes (5.35%). Canonical versus stock is2,318,032 bytes smaller (14.06%). These are exact final-artifact observations, not archive-size or compressed-distribution estimates.

Public process peak RSS is mixed and includes source/hash validation, V8 and allocator retention. For the stock comparison, canonical’s four pipeline median peaks are higher by0.33–36.69MiB despite the smaller component. Same-engine examples include lower RSS for the64B view case, but higher RSS for64B copy and construction-only controls. Component size does not prove a heap/physical-memory advantage. Capacity and memory-grow counts are unavailable/null.

## Separate observed stages — not isolated startup

Representative64B view pipeline medians across three fresh processes, in milliseconds. Full stage medians and process ranges for every arm/family are in arm-costs.csv and processes.csv. Whole-worker duration includes setup, warmups, samples and audits; it is not startup time.

| Comparison / arm | Compile + binding load | Instantiate | First identity export | Setup | First batch | Whole worker |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| same-engine-binding / native-on | 14.973 | 1.813 | 24.953 | 1.331 | 30.448 | 2611.000 |
| same-engine-binding / canonical-on | 15.026 | 1.974 | 23.784 | 1.395 | 26.889 | 2612.000 |
| whole-profile / canonical-on | 15.101 | 1.914 | 27.822 | 1.659 | 26.269 | 2619.000 |
| whole-profile / canonical-off | 14.872 | 1.839 | 24.157 | 1.279 | 23.947 | 2576.000 |
| different-stock-provider / canonical-on | 14.898 | 1.867 | 23.985 | 1.505 | 27.040 | 2562.000 |
| different-stock-provider / stock-on | 15.469 | 4.285 | 12.796 | 1.055 | 22.154 | 2664.000 |

Stage counterexamples matter: in this64B-view pair the registered binding’s first batch is slower than bundled canonical; canonical’s first batch is slower than stock even though its warmed pipeline is faster. Other stages move in different directions. File/code caches were not reset to establish physical cold startup, and no isolated Wizer/snapshot latency or guest GC pause was measured.

## Interpretation and limits

- Prefer the registered binding for its measured footprint when this bounded profile is selected; do not advertise a CPU or general memory win. Keep an unused optional installation OFF when using the bundled fallback. These are scoped engineering recommendations, not source changes.
- The stock comparison supports only the common byte domain and current validation-heavy workload. It does not establish general Streams parity, object/UTF8/cancellation throughput, a native C++ state machine, whole-application speedup or a memory/size advantage across every deployment.
- Saved timing rows do not contain each compact batch return/checksum. Authenticated source exact() checks after first/warmup/sample calls and raw terminal completion support validation; independent per-batch raw decoding is unavailable. The separate308-observation correctness gate retains full raw evidence.
- Apple M2/macOS arm64 shared desktop; only three independent timed process medians per arm/group. Seven within-process samples are correlated. Process ranges, run order and pilots are retained; no p-values, confidence intervals, universal wins or invented metrics.
- Original28 trace counterexamples, parent raw exit1 and all per-arm guest/collector source origins remain unchanged. Runtime/default-OFF/ALS/reset/reuse and archive acceptance claims are separate.

## Data and reproduction

[analysis.json](analysis.json) retains all21 reconstructed summaries, per-process ranges, stage arrays, units, component/source references and limitations. [comparisons.csv](comparisons.csv) has21 pairs; [arm-costs.csv](arm-costs.csv)42 arm summaries; [processes.csv](processes.csv)126 timed processes with all seven sample columns; [pilots.csv](pilots.csv)42 pilots/budgets; [components.csv](components.csv) four actual artifacts. [input-references.json](input-references.json) binds the exact report, Root receipt, output-closure inventory and numerical worker inputs.

Source report `eded2bdba1703712682fab9a0c8e93dd6a80a5551b3b6c727028729df62f1f65`; Root receipt `fc51ab670f64745453f5a23fb399b9e8ea36a7327ed05460e618505922bd5e55`; Root1037-file closure `adaff03059c935da603a1314c67c9aeaed3b1941964765430caa236f8fc31b3a`. Guest source1b801, separate timing-admission source78b3 and supplemental stock collector257e remain distinct. No input, sealed packet or mutable status document was edited.

Recompute data only into a fresh directory (never a sealed report):

```sh
python3 analyze.py --output-directory /tmp/starling-node-compat/CLASSIC_NUMERICAL_REVIEW_FRESH
```

The reader hashes/reads JSON and performs standard-library arithmetic/CSV serialization. It imports no owner runtime helper and runs no Node, guest, host, compiler or timing action. No chart is needed to interpret the separate comparisons and exact tabular values.
