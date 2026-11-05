# Bounded native codec cost decision

Continue the native synchronous codec candidate through its remaining
compatibility and release gates. Keep the optional profile disabled by default
until acceptance. These measurements justify that engineering work for these
workloads; they do not grant production adoption or complete `node:zlib` support.

The [independent actual timing review](../../tests/node-compat/foundation-zlib/independent-cost-timing-v5-results-review-v1/README.md)
verifies 360 fresh workers, 7,200 complete returned strings, matched batches,
separate controls, statistics and process/window records. The
[Root decision](../../tests/node-compat/foundation-zlib/cost-timing-v5-root-decision.json)
authenticates its entire 52-member family, exact contract, original calibration,
fresh-plan roles and three component artifacts. The old pilot proof helper is
unchanged; this direct decision admits no reusable proof-consumer API.

Native has lower median batch time in 27 of 30 provider cases on the same
engine. For 512 KiB repetitive input, fflate/native elapsed-time ratios are
100.94 for deflate, 121.77 for gzip and 94.87 for raw deflate. Native outputs
are one byte larger in those cases. Fflate has lower medians for empty raw
inflate, large pseudorandom gunzip and large pseudorandom raw inflate. Those
counterexamples remain explicit; no automatic provider dispatch is added.

| Exact measured artifact | Component bytes |
|---|---:|
| Native codec | 21,404,160 |
| Identical fflate bundle, native profile ON | 21,450,767 |
| Identical fflate bundle, native profile OFF | 21,419,907 |

The native artifact is 46,607 bytes smaller than fflate ON and 15,747 bytes
smaller than fflate OFF. Holding the fflate bundle fixed, enabling unused native
code adds 30,860 bytes. Provider and unused-profile comparisons answer different
questions. The latter's elapsed-time ratios span 0.9719–1.0466; 24 of 30 paired
ranges cross or touch 1. No general speed effect from unused native code follows.

Each arm has three fresh process setups and seven correlated samples per
process. Analysis retains process medians and paired ranges without pooling,
control subtraction, outlier deletion or significance claims. Measured work
includes output FNV consumption and guest wire conversion. Separate untimed
proofs establish full payload-byte correctness. Unrelated workstation activity
was uncontrolled.

Whole-process RSS is mixed and includes Node, authentication, parsers, loading,
runtime and allocator history. It establishes neither reduced guest memory nor
codec allocation. The combined load interval establishes no isolated startup
or physically cold startup improvement. Those benefits need dedicated measures.

Before adoption, resolve or explicitly bound all 22 Node error deviations and
source-coupled VERNUM; preserve the six synchronous operations' manifest, limits
and unsupported-operation behavior; and complete the selected combined engine's
target-host, release, preservation and archive/acceptance gates. Reassess cost
when engine, codec/options, transport or workload changes. Accepted production
remains foundations-v13.
