# Production regression replay after the private-tick source layer

This is a read-only source map and a plan. No runner, live source, old packet or
accepted archive was changed; no build, component, host or test ran. The new
production source set is 306 inputs. Diagnostic engines and metadata projections
are excluded. There is no future engine SHA in this packet.

The shared selector now admits the finite recipe 869d188… / policy 98e80d36… /
helper 78521fee… branch through the reviewed admission amendment. This does not
make the older, more specific runner preflights accept it. Those rejections are
correct and must be resolved with new versioned receipts and wrappers.

| Gate | Existing source | Compatibility with the new production layer | Necessary finite adaptation |
| --- | --- | --- | --- |
| Core Buffer/stubs | `run.mjs`, `core-expectations.mjs` | Semantic code is source-driven; no fixed 304 count, old recipe or strict version. Core m0.11 source hashes are unchanged. | Retain checks and fixtures. Run only after new exact production preflight; use fresh outputs and include the new admission helper/data in consumed-source evidence. |
| Allocator normal | `foundation-alloc-unsafe/installed/run-component-v11.mjs` | Its first `verifyProductionV11()` rejects the new engine. Core m0.11/direct-U8, numeric-hook and refusal checks otherwise remain valid. | New wrapper/preflight import and report paths; preserve all 10 groups, 5 profile groups, 240 refusal checks, initialization failures and actual old-core controls. |
| Allocator GC | `foundation-alloc-unsafe/installed/run-gc-v11.mjs` | Rejects the old strict version, the old m0.10 protected preflight, and fixed m0.11 GC engine/receipt/recipe/config pins. | New fixed real GC pins and common GC preflight. Preserve Release-only Buffer operations, 8 rooted hex roundtrips, backing/brand/snapshot checks, retained calls and fresh Wasmtime. |
| Optional Path | `foundation-path/run.mjs` | Source-driven selection and pure semantic checks; no old layer equality. | Keep semantic code and vectors. New orchestration/output evidence only. |
| Optional Events | `foundation-events/run-native-component.mjs:20` | Explicit old strict-policy equality rejects the new version even though Events m0.10 source is unchanged. | New versioned wrapper must require the exact new layered strict policy through common preflight; keep facade/oracle hashes and all checks. |
| Optional StringDecoder | `foundation-string-decoder/run-native-component.mjs` | Pins the unchanged actual decoder/factory source, then uses shared selection. No 304/recipe/strict-version pin. | Keep semantic code and decoder pins; new orchestration/output evidence only. |
| Optional Assert/Querystring/Util | Their `run-native-component.mjs` plus `foundations/native-scalar-harness.mjs` | Generic normal-Release/OFF-entropy selection is compatible; helpers reject GC and RuntimeOnly intentionally. | Keep checks and historical actual optional-OFF controls. Do not run these unchanged as GC/Runtime gates or relabel old controls as new-source proof. |
| Installed stream/web | `foundation-stream-web/production-candidate/run-native-component-v11.mjs` | First `verifyProductionV11()` rejects. `native-preflight.mjs` itself pins unchanged controller, decoder, kernel, factory and manifest bytes and uses shared selection. | New wrapper/preflight/report paths. Preserve all constructor/codec/cancellation/guard/view/controller/iteration/data cases, aliases/CJS, snapshot and 7 top-level failures. |
| Four strict suites | `foundation-add-abort/run-production-v11-{sync,runtime,late,callbacks}.mjs` | All import the old fixed preflight; sync/runtime/callbacks additionally compare the old strict version. | New sibling wrappers and common preflight. Keep all fatal, handled-later, reuse, late getter, callback/finalizer and corrected once-listener cases unchanged. |
| Focused protected listeners | `foundation-add-abort/production-native-m0.11/preflight.mjs` and runners | Rejects fixed three-engine paths/SHAs, recipe354, source304, old strict/protected versions/current source maps and embedding9a7c. | New fixed OFF/Runtime/GC pins plus exact new layered policy validation. Keep public16+nested4+receiver9, aliases, errors, fatal/discard and the separate safe getter counterexample. |
| Joint HTTP | `foundations/prepare-http-v11.mjs`, `audit-http-v11.mjs`, `wasmcloud/build-http.mjs` | Preparation/audit pin m0.11 Runtime engine/receipt. All call the old m0.10 protected preflight. Builder recognizes only named historical HTTP entries. | New HTTP entry/prepare/audit/source seal/component pins/report namespace and finite builder recognition; new protected preflight before receiver fixtures. Preserve the complete schema5/body29 and both-host gates. |

`production-v11-preflight.mjs` is a central blocker, not a reusable generic
preflight. It requires fixed m0.11 engine/sidecar/configuration identities, old
recipe/source maps, old strict/protected versions, embedding9a7c and exactly
three strict native commands. The new source layer has changed runtime and CMake
hashes, embedding9dcb and a selected fourth strict TU for the tick queue.

The old strict native patch, `basePolicy`, and
`embeddingBoundaryPatchSha256=84a91c…` remain valid ancestry. Do not replace them
with the fifth scheduler boundary patch or remove them. Validate the distinct
`parentSourcePolicy`, current resolved native maps, new strict/protected versions,
fifth patch a6c3a34… and current embedding9dcb together. The exact source layer is
already encoded in the authenticated integration policy and admission helper.

Before any future packaging, create one new finite production preflight backed
by **actual** frozen normal OFF, normal RuntimeOnly and Release-GC engine receipts.
It must verify engine/sidecar bytes, source306 and current/parent policy maps,
recipe869, all reviewed patches, locked Rust/OpenSSL receipts and immutable CMake
cache/compile-command digests. Reconstruct actual commands from that frozen
compile database and compare them to policy receipts. Require explicit matching
requested/observed tick, optional-module, entropy and GC choices. Do not create
missing flags, strip diagnostic fields, project diagnostic308 into production306,
or substitute an older engine. Select the actual desired tick setting in each
fixed pin, rather than silently assuming ON or OFF.

All seven public foundations are needed for the full prior replay. A slim
production variant is a separate admission/control gate; missing-module negative
tests stay separate from protected receiver tests. All Events receiver/prototype
negatives require the new exact Events-ON source and actual protected-layout
macro first. Events-OFF tests are module-admission/benign-export only. Existing
historical optional-OFF controls can remain exact independently verified controls;
they are not new scheduler-source evidence.

The common compile coverage must account for both optional C++ files. Tick and
protected lists cover 61/60 native TUs when StreamWeb is ON, and 60/59 when OFF
(ticks ON/OFF). The strict subset is 4/3; embedding is one. StreamWeb's private
macro belongs only to the five `builtin_node_compat` TUs when selected; the kernel
must not compile when OFF. Keep the admission v2 checks instead of treating every
source-inventory C++ file as compiled.

Use a new eight-job release orchestrator. The v11-v3 orchestrator authenticates
and reuses five earlier successful **same-v11-engine** reports and is unsuitable
for a new engine. Reuse fixture/oracle source bytes, never prior component or
runtime passes. Use fresh per-engine output/report paths; preserve all failed
attempts, accepted indices and old engine/configuration freezes.

Normal OFF scalar components retain imports `[]`; RuntimeOnly scalar components
retain only `wasi:random/random@0.2.10`; existing GC scalar gates retain `[]`.
Runtime HTTP keeps exactly the six existing standard 0.2.10 interfaces, with
monotonic-clock containing only the nominal `duration` type and no callable/core
clock import. Preserve the HTTP same-byte component on stock Wasmtime42.0.1 and
official wash2.11.0, 3 requests each, shutdown/exit checks, source seals,
allowlists and observed counters. Do not infer instance reuse from counters of 1.

The fresh then-getter gap (Node1/1/0 versus native0/0/0), disposal-symbol registry
gap, registration-getter timing deviation, GC co-ownership caveat and Reset OPEN
must remain limitations. Replaying prior public APIs does not exercise a private
tick enqueue API or establish scheduler ordering, cancellation, ALS or public
process compatibility; those require their separately admitted actual diagnostic
gates. No performance, size or memory claim transfers.

Two supplementary stale guards also require finite future updates if replayed:
`foundations/cmake-policy-test.py:68` has the old no-clobber artifact suffix, and
`abi-fix/run-current.mjs:84` pins a pre-entropy/pre-strict embedding source hash.
Do not run their old assumptions against the new recipe. The ordinary entropy
policy runner is source-driven; the production codec runner pins old engine/count
identities and needs a new ordinary source/config receipt for a future replay.
No stopped DEBUG/OOM/raw-memory branch is part of this plan.
