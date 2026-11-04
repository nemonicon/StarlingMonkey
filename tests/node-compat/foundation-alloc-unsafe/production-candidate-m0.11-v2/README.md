# Second unapplied m0.11 integration revision

This packet additively rebases the reviewed core allocation proposal on the
verified HTTP-v10 fixture. It changes no live production file and contains no
new engine, component execution or timing. The first 680-file m0.11 packet,
including its patch, receipt and host report, remains unchanged in the sibling
`production-candidate-m0.11` directory.

The [11-file patch](./core-m0.11-http-v10-rebased.patch) retains the exact four
reviewed core hashes and the five unchanged candidate harness files from the
first revision. The HTTP builder now recognizes v11 as a protected fixture;
the new `http-v11.mjs` copies the complete verified v10 body, changing only its
first comment. Foundation schema 5, all 16 public + four nested-once + nine
receiver cases, namespace/default/alias/CommonJS identities, seven own-field
errors, disposal-symbol observations, snapshots, first-deployed computed bare
imports, and every previous foundation check remain present. Fatal initialized
and deployed cases stay in the separate focused runner.

The existing protected preflight and shared host checker are byte-identical.
Source/layout/actual macro ON admission still precedes packaging a component
with receiver negatives. All 304 current native ancestry inputs are accounted
for: four core files change and the other 300 remain identical. Protected ten
sources, Events m0.10, stream/web m0.9, the native Buffer kernel, registration,
CMake, generator, build recipe and current source-admission selector are
unchanged. No new runtime flag, host import, fallback or synthetic engine
metadata is introduced. The receipt captures 397 copied live inputs, including
the 18 audited HTTP-v10 inputs and the consumed guest sources and oracles.

The core still returns `tagTrusted(new U8(unsafeTrunc(length)))` after the same
primary validation. Existing captured Uint8Array and private brand/prototype
paths provide zeroed, independent, no-pool storage. Public methods/exports,
16 MiB cap, truncation, errors, arity, call/construction and view behavior remain
bounded as reviewed. `allocUnsafeSlow` and all 91 deferred own prototype methods
remain unavailable. The secondary mutable Number hook difference remains an
explicit behavior outside the declared domain. There is no new C++ allocation
kernel, raw borrow or allocator transfer, and no genuine-OOM/fault/DEBUG claim.

The [source receipt](./source-receipt.json) records exact before/after hashes and
successful current-generator reproduction and patch apply-check. The
[host report](./host-results.json) records four ESM/strict-factory forms, each
with ten Node groups, five allocation-policy groups and 240 pure-JS refusal
checks; both direct forms also pass six numeric-hook cases. It includes ten
malformed policy/proof rejections, three literal module/version regex checks,
and unchanged m0.1/m0.8 selection for five actual historical engine receipts
(v7, v8, v9, v10 OFF and v10 RuntimeOnly). These historical checks read real
bytes and source receipts; they do not execute a prospective m0.11 engine.

The main source bundle retains only native Buffer/child-process imports. Both
HTTP source bundles retain the same 49-module graph and 15 residual imports as
the verified v10 artifact. All protected corpus sources, finite aliases,
shared checker and oracles are retained; no builtin facade, adapter or fatal
runner is bundled. Six existing m0.10 host responses are rechecked as controls.
These checks establish source preservation, not m0.11 guest behavior. Nine
changed JavaScript files pass syntax.

The inherited Events gap remains explicit. The pinned Node observation counts
one returned-object `then` getter read for an ordinary listener and one for a
fresh protected listener; both native hosts count zero. All three count zero
for an already-aborted signal. The getters return `undefined`: these are getter
read counts, with no callable-then or rejection test. The exact separate
counterexample report is copied and hashed; it is not normalized into parity
or fixed by this allocation proposal. Disposal-symbol registry identity and
the other existing profile limits also remain unchanged.

Draft history is preserved. Attempt 1 lacked a JSON dependency needed only by
the isolated host checker; the source bundles had passed. The complete draft
and failure log remain under `history/attempt1-missing-host-oracle`. A later
successful draft used ambiguous getter/call wording; it is retained under
`history/attempt2-before-getter-label-correction`. The final source/host pass
uses exact getter-read labels and the unchanged counterexample evidence. No
production patch byte changed during either correction.

The earlier private same-path experiment motivates a simpler expression and
possible CPU improvement. It does not establish performance of this rebased
source. Retain its counterexamples: higher peak RSS in 29/30 comparisons,
higher observed capacity in 4/30, and an 8,513-byte larger minimal snapshot.
Seven slower controls, five control reversals, n=2 independent processes and
seven correlated samples limit interpretation. No memory, size, Jco-adapter,
whole-application, Wasmtime-throughput, C++-kernel or isolated-fill win is
claimed, and no old measurement is transferred here.

After root finishes the m0.10 archive: review and coherently apply this packet;
build fresh actual configured receipts; run the combined core/allocator/refusal,
alias/CommonJS/snapshot/view, strict and moving-GC gates; inspect final imports;
then run the rebased joint fixture on unmodified Wasmtime 42 and official wash
2.11 using the same bytes. Until those pass, m0.11 stays proposed and unverified.
The [ledger text](./ledger-proposal.md) is a proposal only, with no active status
change. Classic Streams, Blob and scheduler work remain separate.
