# Correctness checkpoint; performance pending

The final source preflight passes on frozen v8 OFF engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9`, with293
source inputs verified before/after. [The full report](./correctness-results.json)
contains both minimal artifacts,45 common cases per fresh Jco instance, two fresh
Jco instances per arm, three full-zeroing/no-pool checks per instance, post-corpus
repeat checks, and15 fresh stock Wasmtime42 invocations per arm. Final imports
are empty; each component exports only the batch function.

| Arm | Exact component bytes | SHA256 |
| --- | ---: | --- |
| Installed profile | 12,044,770 | `6f6079350f03bbf92df78cc2e68c9a41acad0de4dbb0d16d1564448a3485f0dc` |
| Actual Jco adapter | 12,248,336 | `499313d43bf7b28d13b6c3ba2ed9cf350db0fb4f297b31648ab3490474764e19` |

The artifact-specific adapter byte delta is203,566. Both contain the same full
profile-enabled engine; this records extra bundled-adapter overhead, not a
minimal engine-profile deployment saving. The one-export fixtures are much
smaller in application scope than the full allocator/refusal corpus, while their
base engine remains deliberately held constant.

The earlier [preflight-v1](./preflight-v1/index.json) is preserved. The final
preflight moves future host checksum assertions outside timing, requires public
Memory exports for the later observer, adds generator source hashes, and verifies
engine bytes after packaging. Guest bundle hashes are identical between the two
preflights. Nevertheless the rebuilt native and JS snapshots differ by78B and40B
respectively; their exact component hashes/sizes are separate observations.
Componentization byte determinism has not been established. The38B delta change
is documented rather than attributed to an unverified cause.

No timing, RSS, linear-memory byte-length/growth, or startup observation has run.
The future host instrumentation is prepared and syntax-checked; its public Jco
explicit-instantiation loader is exercised by correctness tests, while its
measurement paths remain unexecuted. The public observer can record exported
Memory buffer lengths at boundaries; it cannot count hidden in-Wasm grow
attempts/failures or recover live guest heap size. The coordinator must open the
measurement window before `measure.mjs` runs.

All accepted historical allocation/core/helper reports remain untouched. Blob v2
remains an independent staged syntax-only candidate. No production source or
version changes are part of this experiment.
