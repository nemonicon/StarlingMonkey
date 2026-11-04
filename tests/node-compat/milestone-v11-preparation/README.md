# Foundations v11 acceptance verifier — prepared, UNEXECUTED

No v11 archive or staging directory has been created by this producer. The
source-only skeleton and its pins are preserved under history/source-only-skeleton.
The completed verifier has had AST syntax checking only. Root reviews the code
and default read-only verification before authorizing archive creation.

Three current engines are admitted: OFF, RuntimeOnly and ordinary Release GC.
Core m0.11 changes exactly four of the 304 native inputs; the other 300,
protected Events m0.10 sources, native kernel, CMake, recipe and embedding are
unchanged. The accepted v10 archive is rehashed as an immutable parent reference.
Its Events-OFF control is explicitly historical: no fourth current engine,
identical new manifest or old prototype/receiver execution is implied.

The verifier checks all eight successful release jobs, including five
byte-verified same-engine reused passes and three fresh strict suites after the
storage failure. It verifies the separate allocator GC report and the fresh
focused OFF/RuntimeOnly/GC/getter reports. The focused set contains 19 application
components (8+8+2+1), separately from packager tooling: eleven import nothing and
eight import only wasi:random/random@0.2.10.

HTTP uses one 63,635,975-byte component, SHA-256
634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a,
tested with three requests each on stock Wasmtime42 and official wash2.11.
Exact six standard0.2.10 imports include selected random and a duration-only
monotonic-clock type dependency, with no callable clock imports. Schema5 and
all29 protected groups remain checked. Request counters1/1/1 do not establish
host instance reuse. No outgoing HTTP, DNS, socket, TLS, filesystem or CLI
capability follows.

The Node callback-return getter counterexample remains false parity:
ordinary/protected/already-aborted getter reads are Node1/1/0 and native0/0/0.
The getters return undefined; no callable-then or rejection result is claimed.
Target Symbol.dispose registry identity also differs. GC combines signal,
callback, disposer, view and closure-held Symbol owners and does not isolate
prototype-only Symbol liveness. Fatal instances are discarded. No full Node,
Buffer, EventTarget, stream, process, ALS, request-teardown, OOM/fault or current
production performance/memory/size advantage is claimed.

The copy closure contains the304 exact native inputs, attribution, three
original sidecars/configurations, external embedding source, frozen per-label
OpenSSL and Cargo evidence, actual tested source/oracle/fixture records,
generated text, host configuration and logs, failed-attempt/retry histories,
storage/COW records and the verifier's own history. Recorded relative manifests
are resolved against actual module bases and SHA-checked, including computed
negative fixtures. The actual external BufferList caller source and its package,
license and lock provenance are copied individually; no broad node_modules tree
is imported. Literal dependency discovery supplements these explicit witnesses.

All354 HTTP-index entries and current storage indexes are rehashed. Eligible
indexed text uses explicit repository/current-external/storage prefixes; other
references have an explicit omission reason. The actual wash project config,
empty user config, log and full run report are retained separately. The deployed
component and official host binary remain validated external references.

Private/candidate/timing trees are not recursively imported. Only four explicitly
pinned m11 patch/source/review provenance files are copied from its proposal.
Actual per-file consumed stream fixtures and the protected policy JSON remain
included without copying their candidate directories. Engines, components, Jco
cores, libraries and caches stay external. Only the same five exact versioned
host-API binary source assets may accompany the native304 source set.

The earlier missing-import and ENOSPC attempts are failures, not additional
passing gates. Most storage recovery occurred before COW bootstrap; its recorded
35,856,384-byte operation delta is nonexclusive and is not a physical-extent or
guest performance claim. Frozen engines/sources and the parent archive remain
unchanged.

Default mode verifies and prints a plan; it creates no stage. --show-plan also
prints every copy record and omission. --apply requires the exact reviewed
planSha256, rechecks every source before copying and every copied file afterward,
then atomically renames a fresh stage. Existing archives/stages are never
overwritten or removed. Failed stages remain for inspection.

Prepared commands (not executed by this preparation agent):

    python3 tests/node-compat/milestone-v11-preparation/accept-v11.py --show-plan
    python3 tests/node-compat/milestone-v11-preparation/accept-v11.py --apply --expected-plan REVIEWED_SHA256

The producer starts no host, compiler, componentizer, guest or diagnostic.
