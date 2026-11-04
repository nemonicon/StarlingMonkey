Independent actual process RSS supplement v2: **PASS within this bounded observation scope**. Root17254/parent11856 observed raw0 in98.196s. The599-file closure,18 distinct fresh PIDs,18 zero terminals with owned-group cleanup, all126 typed returns and the final10348-row source audit record match. Nothing was rerun by this reader. Source22/input10348 provenance is bound to prior source proof73fa; a second full input audit was not executed. Initial parent audit completion follows authenticated source control flow and completed execution; the final audit is a retained explicit pass record.

Both setup calls returned exact signed32 numbers151852933 and-1502831163 in all18 workers. The other90 values are whole JSON strings matching the phase and independent Python reconstruction of the pinned Node compact oracle. All7 call arguments/order,7 raw files,17 progress records, stdout/result/parent-observed replicas, identity/probe controls and snapshot/stage sequences were checked. Capacity, grow-count and guest-heap fields remain null.

Instantaneous process RSS is bytes; public maxRSS is KiB on Darwin. Node documents the [RSS byte unit](https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processmemoryusage) and [maximum-RSS API](https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processresourceusage). Its pinned [libuv Darwin branch](https://raw.githubusercontent.com/nodejs/node/v22.14.0/deps/uv/src/unix/core.c) divides OS bytes by1024. Tables convert to MiB for display; raw units remain in CSV/JSON.

Cells are median (min–max), **three independent processes per arm/comparison**. Stages within one worker are correlated, not extra independent samples.

| Comparison | Arm | Instantiate MiB | After small MiB | After large MiB | Max before final hash MiB | Terminal max MiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| same-engine-binding | native-on | 96.00 (92.98–96.11) | 145.34 (143.80–146.59) | 142.11 (140.61–143.36) | 145.53 (144.02–146.80) | 153.92 (149.27–154.27) |
| same-engine-binding | canonical-on | 99.20 (99.06–99.22) | 146.30 (145.45–146.42) | 145.53 (143.08–146.41) | 146.41 (145.53–146.53) | 154.55 (153.88–159.30) |
| whole-profile | canonical-on | 99.31 (99.27–99.45) | 146.14 (145.97–147.23) | 146.25 (146.12–147.33) | 146.25 (146.12–147.33) | 158.94 (158.56–160.00) |
| whole-profile | canonical-off | 97.20 (97.11–97.36) | 144.95 (143.83–144.98) | 145.55 (144.44–145.55) | 145.55 (144.44–145.55) | 155.83 (155.02–157.23) |
| different-stock-provider | canonical-on | 99.30 (99.23–99.30) | 145.59 (145.47–145.78) | 145.69 (145.59–145.88) | 145.69 (145.59–145.88) | 158.27 (156.66–158.61) |
| different-stock-provider | stock-on | 106.70 (106.69–106.78) | 150.11 (150.06–150.30) | 150.23 (150.17–150.41) | 150.28 (150.19–150.42) | 163.88 (163.88–164.00) |

Paired ratios are A/B within one repetition, retaining AB, BA, AB. Below1 means smaller A for that metric, without significance or causal inference.

| Comparison (A/B) | Pre-final max A/B, median (min–max) | Terminal max A/B, median (min–max) |
| --- | ---: | ---: |
| same-engine-binding (native-on/canonical-on) | 1.0000 (0.9837–1.0018) | 0.9982 (0.9370–1.0003) |
| whole-profile (canonical-on/canonical-off) | 1.0048 (1.0040–1.0200) | 1.0229 (1.0108–1.0268) |
| different-stock-provider (canonical-on/stock-on) | 0.9700 (0.9679–0.9707) | 0.9658 (0.9559–0.9671) |

Operational stage time stays separate. Compile-and-binding-load includes both activities, not physical cold startup or throughput.

| Comparison | Arm | Compile+binding ms | Instantiate ms | First identity ms | Whole worker ms |
| --- | --- | ---: | ---: | ---: | ---: |
| same-engine-binding | native-on | 15.57 (15.54–19.16) | 1.86 (1.82–2.13) | 25.09 (23.67–28.72) | 3895.00 (3855.00–4205.00) |
| same-engine-binding | canonical-on | 15.94 (15.82–16.34) | 1.96 (1.90–2.11) | 24.43 (23.70–25.82) | 3853.00 (3848.00–3869.00) |
| whole-profile | canonical-on | 15.85 (15.85–17.75) | 2.03 (1.92–2.22) | 23.65 (23.55–24.04) | 3857.00 (3844.00–3882.00) |
| whole-profile | canonical-off | 16.02 (15.73–17.30) | 2.02 (1.89–2.04) | 25.89 (24.26–28.37) | 3854.00 (3849.00–3898.00) |
| different-stock-provider | canonical-on | 15.88 (15.80–18.58) | 1.94 (1.90–2.29) | 24.19 (24.11–24.95) | 3861.00 (3855.00–3871.00) |
| different-stock-provider | stock-on | 16.42 (16.42–16.43) | 3.63 (3.60–3.80) | 12.71 (12.69–12.81) | 3880.00 (3879.00–3922.00) |

All13 snapshot RSS/cumulative times,9 stage times,7 call-time RSS values,2 maxima and whole-worker time are reconstructed in all-raw-metrics.csv and summary.csv (312 raw/control summaries). All396 defined raw paired ratios remain; the identically-zero bootstrap cumulative time has no ratio. Interval deltas remain in controls-not-subtracted.csv. They are differences between observations, not isolated guest allocation or causal hash cost.

Initial hash-interval RSS changes were about16.5–19.8MiB; final hash-interval changes about8.7–13.7MiB. Native same-engine large-after-small RSS fell about3.2MiB; no cause is identified. Sampled byte RSS is consistent with lifetime KiB maxima. Validation, streaming and allocator effects matter; no controls were subtracted or net guest-memory number inferred.

Same-engine pre-final maximum ratios cross1 across three pairs, so this does not establish a universal native memory reduction. Whole-profile ON maxima are slightly above OFF in this sample. Stock has a different provider/Buffer/scheduler, so that comparison cannot isolate one native mechanism. These are bounded process-cost observations of diagnostic engines and existing components, not production-engine performance, guest heap/capacity/growth, unique pages, worst-case memory, reset/reuse or universal superiority.

The large4MiB case follows small8KiB on one instance. Node/V8, glue, compilation cache, hashes, prior allocations and parent/shared-machine pressure affect observations. AB/BA/AB has2:1 first-arm imbalance and n=3 is small. No forced GC, allocator trimming or private memory inspection occurred.

Failed v1 e511 remains raw1 with zero measured workers; its source-review miss is retained. This18-worker supplement is separate from the old168-worker throughput batch and does not replace or reanalyse it. Old-Root context dependencies, archive/promotion holds, known Node/GC/HTTP limits and latest accepted checkpointv12 remain unchanged.
