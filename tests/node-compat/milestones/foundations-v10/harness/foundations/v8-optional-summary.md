# Existing optional-module regressions on v8

All six installed bounded gates pass on the immutable v8 OFF Release engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9`.
The core profile is m0.8; the optional manifests retain their existing versions.
This is regression evidence, not expanded API compatibility.

[Machine-readable index](v8-optional-results.json) records the six report paths
and hashes, preserved prior reports, exact Node executable, engine receipt and
orchestrator. All 293 native inputs, engine bytes and sidecar were checked
before and after. Ten final-component audits select/import no host interfaces.
Each existing runner exercises Jco-hosted Wasm and stock Wasmtime42.0.1.

| Module | Existing bounded coverage replayed | Result |
| --- | --- | --- |
| Path m0.2 | 15,696 lexical / 4,046 glob vectors; 13 budget refusals; four accepted adversarial patterns; twelve invalid cases; six raw aliases | Pass |
| Events m0.3 | 27 selected synchronous/native cases; seven initialization refusals; aliases/CommonJS/snapshot state | Pass |
| StringDecoder m0.4 | 40 generic cases; 2,982 sequences / 8,886 writes; three initialization refusals | Pass |
| Assert m0.5 | 55 differential groups, 784 primitive comparisons; nine initialization refusals; actual historical optional-OFF admission | Pass |
| Querystring m0.6 | 32 groups, 210 separator vectors / 1,536 byte fallback vectors; eight initialization refusals; actual historical optional-OFF admission | Pass |
| Util m0.7 | 2,436 shared checks; 108 deferred call/new checks; eight initialization refusals; actual historical optional-OFF admission | Pass |

Raw outputs are under
`/tmp/starling-node-compat/foundations-v8/prior-foundations-v1/`. Assert's final
output is `assert-retry-1`: its initial attempt reached the historical OFF
control and failed on an incorrect control filename. The failed log and first
orchestrator source/index remain preserved. The corrected attempt uses the
original v5 engine by its real filename and does not relax or modify a test.
The first three passing modules were verified and retained rather than repeated.

Before overwriting latest module reports, the complete previous six module
source/report directories were copied to `prior-latest`, with an index of old
report/runner hashes. The immutable milestone-v7 checkpoint is also unchanged.

The new m0.9 stream/web installed runners remain **prepared and unexecuted**.
No new native engine, source change, stream/web installation, benchmark or
wasmCloud claim is part of these six scalar regression results. Existing module
limits and deviations in their manifests and reports continue to apply.
