# Independent bounded stock Wasmtime string transport review

The six actual stock Wasmtime 42.0.1 `validate(string)` calls pass this
independent READ/HASH/DECODE DATA review. Root executed one small and one
current-maximum request on each fresh native-on, fflate-on and fflate-off
component process. Reviewers invoked no owner proof helper, Node, parser
helper, CLI, codec, Jco, guest or host action.

Every input WAVE string was independently decoded to its exact complete JSON
request. Every complete retained WAVE return was independently decoded without
clipping, normalized-away text or ignored fields. All six inner JSON values and
strings match the pinned guest protocol. All twelve full output payloads match
independently reconstructed fixture bytes and the authenticated oracle: two
64-byte small-repeat outputs per small call and two 524,288-byte large-prng
outputs per maximum call. Compressed input hashes/FNV/base64, setup/stage
metadata, sentinel windows, counters and prior/mutation/restoration report
fields match exactly. There are 4,231,314 raw stdout bytes and 4,227,912 decoded
UTF8 bytes across the six returns.

Each call executes the within-export sequence
validate→setup→stage→observe→observe. It reports five named entries, two codec
calls and zero control operations; totals are 30 named entries and twelve
guest codec calls. Final state remains prepared/staged with retained output.
There was no checkpoint, reset or idle-state proof. Complete returned bytes and
instrumented ownership/stability fields are verified under the pinned source;
guest heap aliasing is not independently inspected after process exit.

The actual PIDs are 85084, 85087, 85104, 85107, 85126 and 85187. All six raw
terminals have exit zero, no spawn error, no timeout, empty stderr and gone
owned groups. Standalone and aggregate terminal, launch, component, plan,
authority and stream descriptors agree. All 53 retained external files are
accounted for. Unparsed raw terminals remain unchanged. Root's pure decoder
source orders stream fsync before decode; this is an authenticated source-order
witness, not an independent durability measurement.

The reader independently rebuilt all sixty complete current requests and WAVE
expressions, then all 180 per-arm argv models. The unique maximum is
`node-22.14.0.large-prng.gzip`, case 27, with 524,468 encoded bytes. Its final
expression is 699,737 UTF8 bytes; the actual argument including NUL is 699,738
bytes. Aggregate models are 700,013 / 700,013 / 700,014 bytes for the three
component paths. Small aggregates are 759 / 759 / 760 bytes. Every launch uses
the exact sole environment entry `RAYON_NUM_THREADS=1`. These exact large
arguments actually spawned and parsed successfully on the recorded pinned
host. This is not a portable per-argument limit, a kernel-accounting proof or a
promise for future records or all allowed one-MiB compressed inputs. Only the
selected two records were executed here; all sixty models were checked.

The accepted full bounded correctness review `e03bb0db…` and exact contract
`25411f2e…` were authenticated separately, including all 11,440 actual indexed
files and the complete source/native/tool/artifact input ledger. The source
`345ce70f…`, peer `ca663930…`, actual encoder catalog, all seventeen artifact
descriptors per arm, pinned stock host and separate six-call authority match.
Imports=[] comes from the existing artifact reviews bound to the same
component hashes. No new binary-WIT decode occurred.

The old all-provider model `7ce260e8…` still records
`correctnessIndependentAcceptance=PENDING` as historical DATA. The prepared
plan also keeps its unexecuted/null-authority labels. Neither is rewritten or
used as present execution authority: accepted correctness and Root's exact
`91d57160…` six-call authority are separate authenticated records. The prior
correctness proof's then-pending transport fields remain immutable too; this
new result establishes the bounded small/current-maximum transport outcomes.

Real batch controls remain pending. This packet has
`executedControlWorkloads=false`, `controlOperations=0`,
`actualBatchControlProofPending=true` and
`pilotTimingPrerequisitesSatisfied=false`. It grants no new action authority.
There is no separate-host-call interleaving, component reuse, general WAVE
grammar, resource/capacity, performance, runtime acceptance, source promotion
or operational admission claim. Ordinary350 admission stays CLOSED.

`results.json` uses the stable state
`INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_STRING_TRANSPORT_RESULTS_VERIFIED_V1`.
`result-contract.json` fixes exact fields, proof descriptors, observed job
identities and transport bounds for later consumers. `bindings-reader.py`
checks source/plan/process bindings and all sixty models;
`peer-raw-reader.py` independently checks every argument, return, output and
state/counter field. Their witnesses and input ledgers are sealed together.
Raw streams, launches and all twelve binary outputs are copied unchanged under
`evidence/`. Final verification rehashes the complete input union.
