# v10 acceptance preparation — v2 COPY-PLAN DRAFT, ARCHIVE UNWRITTEN

This directory prepares a new immutable `milestones/foundations-v10` checkpoint.
**Root ran the first default verification; its copy plan rejected three private
unapplied m11 control references. No final milestone or staging directory was
created.** The original433dbc71 script, README and failure log are preserved in
[history/plan-v1](history/plan-v1/receipt.json). V2 changes only the copy plan and
its reported omissions; its acceptance code has not been rerun. Root must review
the code and evidence before execution. The script was adapted from `foundations/accept-v9.py`;
earlier accepted archives are read-only inputs and remain unchanged.

The proposed checkpoint is bounded partial compatibility with two explicit
upfront Node differences:

- **Callback-return parity is false.** The safe fresh `.then` getter counter
  is Node `{ordinary:1,protectedSignal:1,alreadyAborted:0}` and native
  `{ordinary:0,protectedSignal:0,alreadyAborted:0}` on both Jco and Wasmtime.
  `observationCompleted:true` is a completed counterexample, not a compatibility
  pass. Returning thenables/Promises, throwing/rejecting getter effects, ALS and
  process error-handler parity are not established.
- **Symbol.dispose registry parity is false.** Node uses the registered
  `Symbol.for('nodejs.dispose')`; the target uses its actual well-known
  nonregistry `Symbol.dispose`, with different description/identity. This is
  measured and preserved, not normalized into a parity claim.

## Concrete selected evidence

The external root is `/tmp/starling-node-compat/foundations-v10`.

| Evidence | Acceptance checks prepared |
| --- | --- |
| Four original engine sidecars | OFF `1098e753...`, RuntimeOnly `dc5f834d...`, Release-GC `5dc29ba0...`, Events-OFF `b2944204...`; actual engine bytes/digests remain external. All304 native input manifests identical; recipe `354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754`. |
| Source/configuration | All304 source hashes match frozen and live files; actual3 external embedding inputs identical. Four original CMake caches/compile databases/sidecars/freeze receipts are copied byte-for-byte. Exactly60 affected layout commands and the embedding command have the protected macro ON, or absent in the Events-OFF control. GC uses the existing Release hook and is not DEBUG/OOM. |
| Root release batch | `release-gates-v1/results.json`:8 terminal jobs, all code0, report/log/runner hashes; core, installed allocator, stream/web, six prior optional modules and four strict suites. Strict suites record24 final component audits; prior optional modules record10, all no-import. |
| Focused native m0.10 | `foundation-add-abort/production-native-m0.10/evidence-receipt.json` and its exact16-file `source-freeze`. Each entropy mode has29 groups, three retained calls for main/aliases/benign, three fresh successful Wasmtime controls,8 rejected initializers and5 fatal/discard cases per host. OFF emits no imports; RuntimeOnly emits only explicit random0.2.10. |
| Combined Release GC | Three retained calls and fresh Wasmtime,8 valid public hex roundtrips per clean invocation, callback/owner/currentTarget behavior, latched initializer object and deployed fatal/discard evidence. This does not isolate prototype-only Symbol liveness. |
| Events-OFF | Two bundler denials, two raw-native import denials and benign success per host. No prototype/receiver negative ran on the control. |
| Safe callback-return observation | Full Node/Jco/Wasmtime report and exact source files retained; required `nodeCompatibilityPassed:false`, with1/1/0 versus0/0/0. Not counted among passing parity groups. |
| Joint HTTP | One component `0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610`,63,626,509 logical bytes, exact6 standard0.2.10 imports and incoming-handler export. Three requests each on stock Wasmtime42.0.1 and official wash2.11.0; both stopped/exit0 and counters `[1,1,1]`. No same-instance reuse claim. |
| Corrected configure evidence | Fresh19-case report under `production-adoption-m0.10/cmake-harness-correction-v1`, matching recipe354 and actual CMake source0155eae9.... The failed first old-namespace/occupied-sentinel attempt and before/after test-only source/receipt/logs remain historical. |

The successful Wasmtime report is specifically
`http-joint/wasmtime-v2/wasmtime-results.json`. The initial incorrect
`NODE_COMPAT_HTTP_REQUIRE_INTRINSICS=1` invocation remains preserved with host
logs. The rerun used the same component bytes and ordinary expectations, with
no repackaging/source edit. Neither that failure nor the earlier CMake failure
is accepted as a successful gate.

HTTP retains exactly `wasi:http/types`, `wasi:io/error`, `wasi:io/poll`,
`wasi:io/streams`, `wasi:random/random` and the **type-only**
`wasi:clocks/monotonic-clock`, all at0.2.10. No clock callable, outgoing HTTP,
filesystem, CLI, DNS, socket or TLS behavior follows from this evidence.

## Copy plan and binary/source distinction

`accept-v10.py` defaults to verification/planning only. `--apply` is the sole
write path. Every validation runs before staging exists. Copying uses a fresh
staging directory, checks source/destination hashes, rechecks live native inputs
and only then atomically renames it into a new milestone. An existing archive
or failed stage is never overwritten/deleted.

The plan includes full primary reports,304 exact native inputs plus attribution,
four original sidecars/caches/compile databases/freeze receipts, external
embedding sources, complete OpenSSL before-source inventories/dependency
receipts, actual tested harness/source snapshots, docs, generated text/WIT,
raw logs and explicit failed-attempt histories. Prior text/source history retains
its labels; copying is not an assertion that every archived file executed.
Private m0.11 source/artifacts/results are excluded.

The HTTP evidence index includes exactly three hash-pinned metadata controls
from the old **unapplied** m11 packet: `host-results.json`, `index.json`, and
`source-receipt.json`. V2 still revalidates every one of all348 HTTP-index
entries in the unchanged `validate()` function, including these three. It
omits only their artifact copies with reason
`reference-only-historical-unapplied-control`. Their original paths, hashes and
sizes remain in the copied HTTP index and acceptance omission records. The
three exact path/hash pairs are hard-pinned; any changed digest or unknown
other m11 copy path still fails. This does not turn private proposed metadata
into a current checkpoint artifact or relax a native/HTTP evidence gate.

The first plan's original script SHA is
`433dbc71a1ff8f9317f005ae619da69409e3c649f3cdd4dea1f6256297c2e48d`;
its preserved stderr SHA is
`119c2e0b43567003229d1658e66c589373946571f3137c696cb5f3310cde2ba8`.
That failed plan and source-only review are history, not successful acceptance.

Generated engines, application components, Jco core Wasm, compiled caches,
native libraries and other output binaries stay external; their original
paths/digests remain in reports. There is one tightly bounded distinction:
the304 required source inputs contain **five already-versioned host-API binary
assets**, which must be copied for source completeness:

- `host-apis/wasi-0.2.{0,3,10}/bindings/bindings_component_type.o` (three distinct
  exact hashes hard-pinned in the script).
- The debug/release repository Preview1 adapters, both SHA-256
  `988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0`.

Only these exact paths/digests may bypass binary exclusion, and only at their
`source/` destinations. This does not copy any generated native engine or
application component. Do not weaken the policy to allow arbitrary `.wasm` or
`.o` files under a directory named source.

Walkers use `os.walk(...,followlinks=False)`, skip symlink directories and
nonregular/symlink files, and validate native input path components. Sources
are never modified. Safe byte-preserving filesystem compression does not change
the logical hash checks. All future generated files are outside the completed
selected roots; the archive does not scan private build/cache trees.

## Root review and execution checklist

- [ ] Review this draft and script; independently inspect all known false-parity
  fields rather than treating every terminal process as a Node pass.
- [ ] Confirm focused receipt,16 saved source files and four original engine
  sidecars/configs match the actual immutable freeze, all304 live sources and
  recipe354; no m0.11/native edit occurred while validating.
- [ ] Review exactly five source-binary exceptions and no-follow copy policy.
- [ ] Check full8-job/old6/strict24 reports, both29-group focused modes, GC,
  optional-OFF denials, namespace/default/CJS/snapshot, fatal/discard and safe
  callback-return counterexample coverage.
- [ ] Check corrected CMake19 evidence and successful Wasmtime-v2 HTTP path;
  retain failed attempts as historical observations.
- [ ] Run verification-only after authorization: it must print a plan and create
  neither milestone nor staging.
- [ ] Root executes `--apply` only after review/authorization; independently
  rehash `copiedEvidence` afterward, check all304 source entries, sidecars and
  the five precise source-asset exceptions, and confirm no generated binary.
- [ ] Confirm all348 HTTP-index inputs were revalidated, exactly three known
  unapplied controls appear only in reference/omission metadata, and no other
  m11 path is copied. Retain the original failed433dbc71 plan/log unchanged.
- [ ] Update current documentation only after the archive is accepted. Earlier
  archives remain unchanged; no full Node/EventTarget/stream/process/ALS,
  complete teardown, prototype-only Symbol liveness or performance claim.

Prepared v2 commands, **not executed by the preparation agent**:

```sh
python3 tests/node-compat/milestone-v10-preparation/accept-v10.py
python3 tests/node-compat/milestone-v10-preparation/accept-v10.py --apply
```

The script never starts hosts/builds/guests or repeats hazardous diagnostics.
Root's later acceptance is a provenance checkpoint for the declared bounded
scope, with the callback-return limitation and Symbol difference retained.
