# Normal OFF strict and stream/web follow-ons: implemented preparation

This **unapplied source-only packet** adapts the four existing v11 strict suites
and installed stream/web runner to the reviewed
[production common preflight v3](../production-regression-candidate-v3/README.md).
The common actual production normal/GC pins are still `null`. Every entry stops
at that gate before toolchain, packager, fixtures or output creation. No future
engine hash is invented and no diagnostic metadata is projected. Latest accepted
remains foundations-v11; these preparations are not new runtime passes.

[test-results.json](test-results.json) records **27 host checks passed** and
[source-checks.json](source-checks.json) records **15 syntax checks**. Five negative
child Node entries fail at unconfigured pins even with impossible engine/source/
host paths. Other checks verify exact reverse transformations, unchanged whole
case/control sections, source seals and four owned-scratch tamper cases. No
native compiler, componentizer, Wasmtime invocation, component or guest ran.
The fixed-artifact success paths remain unexecuted.

## Entry contract and retained scope

[entry-contract.json](entry-contract.json) gives stable entry/report names for
future serial orchestration. Each strict entry uses its own fresh
`NODE_COMPAT_STRICT_EVENT_OUTPUT`; stream/web uses a fresh
`NODE_COMPAT_STREAM_WEB_OUTPUT`. The name `run-runtime.mjs` means deployed async
strict-boundary cases, **not** the RuntimeOnly entropy configuration. Every
entry here selects normal Release, entropy OFF, GC stress OFF, ticks ON and all
seven optional foundations ON through the common fixed preflight.

| Entry | Original fixture/control scope preserved | Primary report inside its fresh output |
| --- | --- | --- |
| `run-sync.mjs` |16 initialization cases (13 failures/3 successful controls), one deployed successful retained-reuse control and3 fresh deployed fatal/discard cases. |`private-ticks-sync-results.json` |
| `run-runtime.mjs` |2 exact original observation source strings plus3 further fresh fatal/discard cases;4 caught/handled-later/clean controls, each three retained calls and fresh Wasmtime. |`private-ticks-runtime-results.json` |
| `run-late.mjs` |6 valid post-binding interface-getter cases,3 rejection/3 success; preserves late microtask handler effectiveness and getter binding checks. |`private-ticks-late-results.json` |
| `run-callbacks.mjs` |8 finalizer/getter initialization failures and5 retained controls, including corrected once re-add/nested/stop cases and explicit registration-getter timing deviation. |`private-ticks-callback-results.json` |
| `run-stream-web.mjs` |41 constructor/250 codec/4 cancellation/24 guard/12 view/6 controller/67 iteration/26 DataView checks; own-error/intrinsic checks; aliases/CJS/cache/snapshot identities and7 initialization failures. Main3 retained calls/fresh Wasmtime plus alias2 retained/fresh Wasmtime remain. |`results.json` |

The original finite cases, expected values, guest source strings, fatal child
markers, discard policies and retained controls remain byte-identical. Both
original runtime observation sources are still read from the same pinned JSON
and checked against their recorded source digests. Stream/web still imports the
installed native module, forbids application facade/registry injection, retains
compression call/new deferrals and unknown-export failures, and checks zero
host imports. It does not expose deferred compression or missing signal/min
semantics as parity. No old invalid controller/DataView path or stopped private
fault branch is introduced.

## Actual inner guard changes

[prepare.py](prepare.py) generates only five sibling bodies under `runners/`.
It replaces each actual `verifyProductionV11` import/call with the v3
`verifyProductionTicks({gcStress:false})` call. The three old explicit strict
version equalities become the exact
`sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1` version. There is no
outer wrapper retaining an inner304/old-recipe rejection.

The **old** strict native patch and84a91c embedding-boundary patch checks remain
ancestry checks. The **current** embedding9dcb, fifth scheduler patch, source306,
recipe869, resolved/parent policies, exact61 native/four strict/one separate
embedding command and frozen configuration/artifact checks are supplied together
by the unchanged v3 fixed admission and authoritative selector. None is replaced
by an old patch identity alone. Native stream safety preflight remains an
additional actual source/flag gate inside its existing harness.

Generated bodies locate fixtures/oracles in their unchanged original directories.
Declared edits rebase host imports and fixture locations, update admission/
policy/report metadata, and move every mirrored latest-result write into the
new output. They never write old v11 source reports. Historical v11 names in
preserved comments/source-ancestry fields describe the original files; report
states and admission records identify the new selected source layer. No report
or old component pass is reused as new-engine evidence.

[runner-transformations.json](runner-transformations.json) records every edit.
Reversing them restores both bytes and SHA of all five original source files.
Each full case/control section has a separate unchanged digest; this is stronger
than merely retaining a case count. The remaining host harness/toolchain bodies
are the actual existing helpers, not an imitation of embedding APIs.

## Stable source seals

The outer entries first invoke [preflight.mjs](preflight.mjs), which calls the
fixed common preflight before any dynamic runner import. It then authenticates
the exact reviewed common index3064605f and captures the local manifest's digest
as an immutable primitive. Actual generated bodies repeat fixed production
admission at their replaced inner guard before invoking their harness.

On successful return the outer entry calls the common `production.recheck()`
first. That verifies immutable initial pin/manifest digests before following
changed data, plus the actual frozen artifact/source copies. The local manifest
is then read once and compared against its captured initial digest **before**
JSON parsing/row access, using the same reviewed v3 checker. Finally it writes
`followon-admission-complete.json` exclusively. Future acceptance requires process
exit0, the complete semantic report, and this completion seal; partial files are
not accepted passes.

[input-freeze.json](input-freeze.json) seals729 finite local inputs, including
the unchanged common665-input closure and its22-file preparation checkpoint,
all new executable bodies/entries, the original sources and their explicit
fixture/oracle data. The common real historical controls remain host-read data
and are not executed by these follow-on suites. Historical guards/original
runners are included only as source/ancestry data; the new entries do not import
their rejecting preflights. The future production306 and external embedding3
partitions remain separately authenticated by common admission. No engine or
other binary is copied into this packet. Existing package provenance guards
remain required; this is not a snapshot of all npm package files.

To rerun host-only checks, choose a nonexistent external JSON file:

```sh
NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT=/tmp/followon-off-host-check-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/production-followon-off-v1/test-host.mjs
```

`check-source.py` likewise requires a fresh
`NODE_COMPAT_FOLLOWON_SOURCE_CHECK_OUTPUT`; it performs Node `--check`, Python
AST parsing and read-only hashes. [index.json](index.json) and
[source-receipt.json](source-receipt.json) freeze the preparation. Populating
actual production pins requires a new reviewed common revision and a reviewed
follow-on closure update; there is no path or metadata override to activate it.

## Remaining gates and limits

The concrete blocker is still the absent reviewed actual production306 normal
and Release-GC freezes. This packet does not implement RuntimeOnly/focused
protected Events/GC/getter/HTTP adaptations, six other foundation orchestration,
actual builds or host replays; those remain in the
[regression plan](../regression-plan-v1/README.md). It supplies the four strict
and installed stream/web prerequisites only.

Fatal tests retain the existing paired positive controls and fresh discard
policy; import-free host traps do not establish inaccessible original JS error
causes. The Node1/1/0 versus native0/0/0 callback-return getter counterexample,
Symbol.dispose registry gap, registration-getter timing deviation, GC
co-ownership qualification and Reset OPEN remain. Successful retained calls do
not establish safe reuse after fatal failure or Engine reset. No public process,
ALS, request reuse, full classic streams, performance or broad Node parity is
claimed.
