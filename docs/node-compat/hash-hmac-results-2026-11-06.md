# Experimental native SHA-256 Hash/Hmac results

The experimental guest implementation passes fourteen complete returns across
retained/fresh Jco and stock Wasmtime42.0.1. These cover280 accepted Node-record
comparisons and112 separate native-policy checks. Accepted production remains
**foundations-v13**; `node:crypto` is still deferred in that production profile.

The compatibility reference is Node22.14.0. The engine starts from StarlingMonkey
`54b3329b3ce818fd1f244e871e9c259b63667cda` plus the exact recorded357-source
overlay, three embedding inputs and twelve selected manifests. Engine
`9aec9297…` is10,024,185 bytes; its unchanged83-field sidecar is `2b725c11…`.
This is Release/COPY, audited borrowing OFF, entropy OFF. The pinned guest
OpenSSL dependency is3.0.17; a runtime provider-version string was not measured.

| Actual input/execution | Result |
| --- | --- |
| Pinned Node oracle, three calls | 60 accepted records;24 policy observations kept separately |
| Bundled fixture: three retained Jco, one fresh Jco, three fresh Wasmtime | 140 accepted comparisons;56 native-policy checks pass |
| Direct native imports: same seven-call schedule | 140 accepted comparisons;56 native-policy checks pass |
| Whole fresh-ordinal returns | Four full same-ordinal comparisons pass per component |
| Named/default/alias relationships | All13 declared function/default identities pass per call |
| Namespace object identity | Bundled imports share a namespace; direct bare/prefixed imports have distinct namespaces |

The finite surface is `createHash('sha256')`, `createHmac('sha256', key)`,
`update` with supported UTF8 strings or fixed unshared Uint8Array windows, and
`digest` returning the bounded Buffer or hex. Tests cover known SHA/RFC4231
vectors, Unicode/surrogates,55/56/63/64/65-byte boundaries, partitioned updates,
nonzero input windows, input mutation, copied keys, output ownership, empty Hmac
and finalized-state behavior. The twenty accepted records match Node completely
within the comparator's documented error-diagnostic scope. This does not prove
untested overloads or allocation boundaries.

The eight separate policy cases check refused constructors, SHA1, options,
unsupported input/output encodings, invalid algorithm types and invalid receivers.
Stock Node accepts several operations this profile deliberately refuses; those
are deviations, not parity failures disguised as support. Streams, `copy`, other
algorithms, general encodings and KeyObject APIs remain unavailable. Nine typed
guest-header constants are checked independently of Node's full host constants.

| Component | Bytes | Emitted imports | Public ABI |
| --- | ---: | --- | --- |
| Bundled `2e538349…` | 13,240,343 | None | `run() -> string` |
| Direct-import `793c9cb1…` | 13,250,961 | None | `run() -> string` |

Both component/core graphs and generated ESM pass independent artifact review.
The generated host code uses only its ordinary Node FS loader to read core
bytes; there is no host crypto shim. No custom host service or host modification
is used. These are scalar diagnostic worlds, not a deployed Next HTTP server.
wasmCloud was not exercised for these new components. Sizes are whole artifacts,
not incremental library costs or throughput/startup/memory measurements.

Direct imports expose a real deviation: `crypto` and `node:crypto` preserve the
same default object and named functions, but their ESM namespace objects differ.
The pinned Node oracle shares its namespace object. In
[`get_builtin_module`](../../runtime/script_loader.cpp), `moduleRegistry` is keyed
by the requested identifier; [`module_load_hook`](../../runtime/script_loader.cpp)
passes bare/prefixed identifiers separately. The native registrations share an
exports object. Bundler canonicalization hides the namespace-record difference,
which is why the direct-import arm is retained. Namespace descriptors and
provider identity are separate observations, with no broad Node parity claim.

An [unapplied native correction](../../tests/node-compat/foundation-crypto/node-builtin-namespace-identity-candidate-v1/README.md)
now selects one cache key only when both explicitly registered builtin names
hold the same JSObject. Its single real SDK frontend passes. The executed
driver's later membership-order assertion failure and separate read-only
verification are both retained. Synthetic models and fixture grammar checks
pass; linking and both raw import-order differentials remain pending. This
source proposal does not change the observed namespace deviation above.

The [bundled sequence review](../../tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-bundled-jco-wasmtime-sequence-review-v1.json)
and [direct-import sequence review](../../tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-raw-jco-wasmtime-sequence-review-v1.json)
validate all fourteen strings and clean process completion. The
[portable retained dataset](../../tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-runtime-validation-v1/index.json)
contains142 exact payloads, including complete returned strings, raw process
streams, typed observations and copied comparator inputs. Large binaries stay
at the recorded external paths with exact descriptors.

Repeat the retained checks without executing any workload:

```sh
node tests/node-compat/foundation-crypto/node-crypto-hash-hmac-retained-results-check-v1/check-results.mjs \
  tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-runtime-validation-v1
```

Use pinned Node22.14.0. The [checker](../../tests/node-compat/foundation-crypto/node-crypto-hash-hmac-retained-results-check-v1/README.md)
verifies every indexed hash and exact membership, then compares all fourteen
whole records. It works with a relocated same-byte dataset. Its28 DATA tests
cover missing/tampered evidence, bad ordinals/types and dependency changes.
Root's [actual recheck](../../tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-retained-check-root-results-v1.json)
exits0. This validates retained data, with component/provenance/process evidence
kept in the separate reviews.

Earlier failures remain evidence: the original build recipe exits0 while both
wrappers exit1 on a Git-index protection change; the first read-only path guard
rejects two retained `/tmp` aliases; a review publication omits its required
coverage field; the first Jco harness overwrites successful-call counters before
an awaited merge. Genuine successors fix those harness/data defects without
changing the engine. The original four digest returns passed80 comparisons but
their phase acceptance remains false. Corrected runs preserve truthful3/1
attempt/return/comparison counts; they are the accepted diagnostic evidence.

The [actual freeze](../../tests/node-compat/foundation-crypto/node-crypto-hash-hmac-freeze-v1-root-results.json)
now finishes with clean exit0. Receipt `187fabbe…` retains1,893 payload files,
641,351,629 bytes and the unchanged9aec/2b725 engine/metadata. Its genuine
frozen-only verifier returns a NOT_ADOPTED record using copied roles and pure
83-field models. [Independent actual-freeze review](../../tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-frozen-artifact-review-v1/results.json)
passes80,672 checks, including every copied role and whole result/contract
coverage. A reader-only stdout typo is preserved; its corrected read-only
completion finishes0 without rerunning the verifier or admission. The
freeze rechecks current references but does not physically copy the whole SDK
and reference distributions; its offline verifier does not rehash those live
originals. Earlier failed build outcomes remain unchanged.

The snapshot audit also identifies late initialization after
`Engine::finish_pre_initialization()` sets the Initialized state. Export binding
and final jobs/ticks still run before the snapshot finishes. A proposed native
barrier must combine engine state with the existing deployed-execution state;
REQUEST_HANDLER_ONLY alone is insufficient. The current9aec artifact has no
general live-EVP initialization barrier.
The [standalone barrier Source](../../tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-candidate-v1/README.md)
and [separate Source review](../../tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-source-review-v1/results.json)
now specify that restriction for all four native primitives, with identifiable
TypeError/code/operation fields and unconditional cleanup. Two actual SDK
frontends and [independent result review](../../tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-sdk-v2-results-review-v1/results.json)
now pass. The original driver failed before compilation on an absent include
directory; its genuine successor preserves that `-I` and checks explicit
absence. The guard remains unapplied and unlinked; actual early/late INIT
refusals and ordinary-call regressions require a genuine new native generation.

Remaining gates are fresh reproduction, initialization/live-EVP snapshot policy,
secret-copy/erasure and GC/lifetime
coverage, allocation limits, malformed inputs, performance/component-size
comparison, broader release gates and optional host capabilities. The fixture
creates contexts only during ordinary calls. Full Node, Buffer, crypto and
Next.js compatibility are not established. [progress.md](../../progress.md)
tracks the complete roadmap and retained failures.
