# Production HTTP: independent post-host verification

Both recorded host gates pass this independent read-only review: three HTTP200
requests on stock Wasmtime42.0.1 and three on official wash2.11.0, with both
processes stopped at exit0. Both use the exact same ccc87ae3 component bytes
(63,639,194 bytes), bound to the reviewed RuntimeOnly479821f8 engine.

The reader rehashes335 engine copies, the unchanged778-source closure/live8,
the59-file final capability index, reviewed phase pin and Root's phase review.
It repeats the prior binary/WIT/type-graph structural checks without running a
tool: exactly six standard0.2.10 imports, only incoming-handler export, clock
instance type5 containing duration:u64 only, and no callable/core clock or
Preview1 imports. All11 noncustom raw/embedded native-core section payloads
remain equal; the preserved prehost custom-metadata explanation is unchanged.

The exact pinned host binaries, deployed component copy, original/effective
wash configuration, empty user configuration and logs are hashed. Outgoing
host, IP lookup, loopback and volume grants are empty; custom plugins, sidecars,
Docker and NATS are absent. Wasmtime's command selects only a loopback incoming
server, with no directory/environment/outgoing grants. Effective wasmCloud
settings match the isolated source config. No host or guest is relaunched.

All six complete response bodies agree after removing only requestTag and three
explicitly random fields (secure bytes, UUID, multipart boundary). Each response
retains the exact16+4+9 protected cases,14 first-deployed aliases, Buffer/core
checks and snapshot-denied/deployed-success entropy behavior. Six distinct byte
samples/UUIDs are observations, not an entropy-quality proof. Counters[1,1,1]
claim neither general instance reuse nor request isolation.

An initial verifier assertion required the allowlist's order to match canonical
emitted-import order. The exact six names were identical and unique; only list
order differed. [History](history/attempt1/failure.json) preserves that schema
assumption failure/source. The corrected check compares the unique sorted
allowlist and keeps exact emitted imports. No host failure or artifact mutation
was inferred. A boolean computedBareImports flag is checked separately from its
14 alias records.

[results.json](results.json) records1191 hash/read paths and limits. Known getter
counts Node1/1/0 versus guest0/0/0, Symbol.dispose and GC co-ownership limitations
remain. Reset/ALS/request cleanup, complete Node HTTP/process/stream support and
performance/memory advantages remain unproved. Milestone acceptance and archive
closure are Root-owned. The verifier executes no host, guest, compiler, native
build, packager, Ninja, Node oracle or validation tool, and edits no existing
source, configuration, artifact or report.
