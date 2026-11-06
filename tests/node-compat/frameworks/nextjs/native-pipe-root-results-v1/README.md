# Native signal-pipe regression progress

The real component now matches pinned Node22.14 on all36 records: twelve cases
across three actual Wasmtime calls. The constructor's three commands and outer
parent exit0/clean; WIT validates exactly13 standard WASI0.2.10 imports and the
incoming-handler export. Runtime observations are valid, strict selected Node
parity is true, the outer parent exits0 and all owned groups are gone.

Component `1c711297…` is37,162,665 bytes over native engine `4623640b…`.
This validates the audited guest-JS facade over actual native readers/writers
and the protected abort listener. It does not replace SpiderMonkey's C++ signal
pipeTo path, cover all31 host cases, prove native resource counts/teardown or
promote the production profile. The earlier pinned Node reference completed
36 captured records with unmodified Node pipeTo; its capture is retained below.

`oracle-capture` contains byte-exact complete original monitor/process/stdout/
stderr/observation records. `node-oracle-authority.json` binds the selected
source family, executable and original monitor. The executed launcher is retained
as `launch-oracle.executed-v1.py`. Its observation field `oracleComparisons:36`
was a reporting-label mistake: it counts captured reference records, not
Node/guest comparisons. The original is unchanged, the capture index clarifies
the scope, and `launch-oracle.py` corrects the field for future source reuse.
No extra oracle run was needed to correct that label.

Run `python3 -I -B check-node-oracle.py` for the portable DATA check. It validates
the complete capture hashes/membership, actual source/executable descriptors,
owned terminal and all three twelve-record returns without starting Node or a
guest. Root's current readback passes. This verifies the reference capture,
not the separate guest execution.

The held [probe Source](../native-pipe-regression-v1/README.md) covers final
chunks, preventClose, source/write failures, pre-abort, falsy cancellation/abort
errors, protected listeners, in-flight writes, backpressure and lock refusals.
Those scenarios now compare as complete typed records using actual native
readers/writers and the protected abort listener. No mismatch, hang or failed
record is normalized into a passing result.

Earlier volume checks ranged from about811MiB to996MiB free and held construction.
Space subsequently rose above the unchanged1,024MiB start guard, allowing the
operation. The Root wrapper authenticates the entire referenced8025 WIT family,
all eight explicit WIT inputs, exact directories and aliases before/finally.
No build guard was lowered and no proof, engine or shared tool was deleted.

`pipe-v1-construction-authority.json` and `pipe-v1-runtime-authority.json` pin the
actual actions. Complete construction/world guards and runtime raw records are
being collected in a separate portable actual review. The held collector may
lose partial response bytes/headers if a fetch body aborts; no partial-wire
completeness is claimed. These successful requests retain all three full bodies.
