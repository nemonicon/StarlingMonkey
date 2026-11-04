This directory contains the entropy policy integration for the opt-in Node
compatibility profile. **The bounded OFF and RUNTIME_ONLY gates now pass in real components and
on Wasmtime42/official wasmCloud2.11 HTTP hosts.** The older
`.in` templates, standalone fill model and `staged-results.json` describe the
previous staged milestone. They do not prove the production bridge works. No
`node:crypto` module or Node crypto export compatibility is added.

The triggering upstream failure is preserved in
[../upstream/crypto-diagnostic.log](../upstream/crypto-diagnostic.log): valid RSA
JWK import reaches Preview1 `random_get`, which the pinned ComponentizeJS splicer
replaces with `unreachable`. The existing P2 `host_api::Random::get_bytes`
implementation makes an additional host entropy service unnecessary.

Implemented sources covered by the exact engine/component receipts below:

| Integration | Source and behavior |
| --- | --- |
| Early configuration | [`cmake/node-compat-policy.cmake`](../../../cmake/node-compat-policy.cmake) selects `NODE_COMPAT_ENTROPY_MODE=OFF` by default; `RUNTIME_ONLY` requires the opt-in Node profile. |
| Private policy | [`include/node-compat-entropy.h`](../../../include/node-compat-entropy.h), [`entropy-policy.cpp`](../../../builtins/node-compat/entropy-policy.cpp) contain a per-instance deployed-entry barrier and coded errors. No JS setter, environment override or new host import/export exists. |
| Actual deployed entries | [`runtime/engine.cpp`](../../../runtime/engine.cpp), non-preinitialized `Engine` construction; [`host_api.cpp`](../../../host-apis/wasi-0.2.0/host_api.cpp), native incoming HTTP callback; [`componentize-entry-policy-v1.patch`](componentize-entry-policy-v1.patch), actual pinned ComponentizeJS `call()`. The external embedding patch must be applied by the engine recipe. |
| OpenSSL bytes | [`entropy-bridge.cpp`](../../../builtins/node-compat/entropy-bridge.cpp) obtains fresh owned P2 bytes in chunks of at most 65536, copies and clears temporaries, and has no seed, pool or persistent RNG resource. [`rand.patch`](../../../deps/patches/rand.patch) uses it only under `STARLING_NODE_ENTROPY_PROFILE`; non-profile `arc4random_buf` behavior remains. |
| Build provenance | [`cmake/openssl.cmake`](../../../cmake/openssl.cmake) keys source, install and build/stamp directories by pinned archive, both patch contents, policy, seed and flags. It hashes actual applied `rand_lib.c`, and writes `openssl-profile-receipt.txt`. [`add_builtin.cmake`](../../../cmake/add_builtin.cmake) consumes the dependency target's actual include path. |
| Multipart teardown | `MultipartFormData::create` initializes its finalizer-owned private slot to null before policy denial or any later failure; failed native implementation allocation reports OOM. |
| Secure Web API consumers | `Crypto::get_random_values`, UUID helper (`crypto.randomUUID` and `URL.createObjectURL`), and multipart boundary creation check policy before requesting entropy. |
| Owned WebCrypto inputs | [`buffer-source.h`](../../../builtins/web/crypto/buffer-source.h), [`subtle-crypto.cpp`](../../../builtins/web/crypto/subtle-crypto.cpp), [`crypto-algorithm.cpp`](../../../builtins/web/crypto/crypto-algorithm.cpp) validate BufferSource inputs, normalize algorithms, then take owned copies before promise allocation, OpenSSL or host calls. Raw-key temporaries are wiped. HMAC/EC/RSA parsed JWK owners now remain scoped through import, as Ed25519 already did. |

Policy contract:

| Variant | Secure calls | Packaging |
| --- | --- | --- |
| `OFF` | Valid secure requests throw `ERR_SM_ENTROPY_DISABLED`; caller bytes remain unchanged. This includes object URL tokens and multipart boundaries. The private OpenSSL bridge returns failure without a host call. | Disable upstream `random`; final components must have no random or Preview1 imports. Pure Buffer/SHA256 remain zero-import targets. |
| `RUNTIME_ONLY` | Until actual deployed entry, requests throw `ERR_SM_ENTROPY_INITIALIZATION`. Each allowed deployed request obtains fresh bytes through existing P2 random. | Explicitly select `wasi:random/random@0.2.10`; upstream random must remain enabled. Reject mismatches before Wizer and audit final imports. |

`Engine::finish_pre_initialization` runs before ComponentizeJS `bindExports`.
Its `Initialized` state therefore cannot substitute for the private barrier. A
late export getter must still fail. A handled snapshot denial must permit later
deployed calls; repeated calls keep readiness but retain no random bytes.
Instances have independent linear memories. Non-preinitialized runtime engine
construction permits its deployed initializer, while Wizer remains denied.

`Math.random` remains explicitly non-cryptographic. OFF retains the documented
upstream deterministic stub. Runtime-only checks the snapshot barrier before
its existing `Random::get_u32` call. No Node/V8 sequence/distribution claim is
made. Profile OpenSSL uses `--with-rand-seed=none`, so unhandled provider DRBG
paths fail closed instead of finding a second libc entropy source. The existing
non-profile seed configuration remains `getrandom`.

The standard secure random WIT has no recoverable error variant. The bridge
checks local failed/short results, clears partial output on recoverable failure,
and returns 1 only after a complete fill. Its OpenSSL callers put
`RAND_R_ERROR_RETRIEVING_ENTROPY` on the existing error queue and return 0 on
failure. A canonical allocator OOM or trapping host call can still trap; the
bridge cannot promise destructor execution or translate that trap into a JS
error. No Preview1, insecure-random, fallback, custom host service or host patch
is introduced. Actual provider and error-queue recovery require component tests.

Owned-input order and current limits:

- Pinned Node22.14.0 validates digest BufferSource types before algorithm
  getters, but observes mutation/detachment/shrink from those getters before
  copying input bytes. The old native implementation had the same visible
  mutation order while retaining an unsafe borrowed span. The fix preserves
  that order and revalidates/copies after normalization, in both build modes.
- The current [WebCrypto draft digest algorithm](https://www.w3.org/TR/webcrypto/#SubtleCrypto-method-digest)
  describes a copy before normalization (similarly sign/verify). This is an
  explicitly preserved existing divergence; this change makes no WebCrypto
  standards-conformance claim. Node errors and StarlingMonkey errors also
  differ in codes/messages for invalid BufferSources.
- Shared-backed BufferSources are rejected before getters, matching the safe
  1KiB Node22 oracle in [`shared-input-node-results.json`](shared-input-node-results.json).
  The accepted R2 realm reports `typeof SharedArrayBuffer === "undefined"`; the
  default realm has no local shared-memory enabling override. Rejecting shared
  views is an explicit validation tightening for any future embedding enabling
  them. No C++ racy-copy compatibility path is provided.
- `getRandomValues` roots its input, obtains and validates owned host bytes,
  then acquires the JS no-GC payload pointer only for the copy. No JS payload
  pointer crosses a host call. Other crypto BufferSources are copied into
  `JS_malloc` storage, have a `JS::FreePolicy` owner, and report allocation OOM.
  Raw-key temporaries are cleared before release; keys keep their existing
  native CryptoKey ownership/tracing/finalization.
- The raw-span audit covers all `value_to_buffer` sites in the crypto tree:
  digest, sign, verify (signature and data), and HMAC/EC/Ed25519/RSA raw/DER
  imports. Exposed methods are digest/importKey/sign/verify; unsupported
  encrypt/decrypt parameters such as `iv`/`additionalData` have no accepted
  implementation here. No new algorithms are claimed.
- Existing `CryptoKeyUsages::from` accepts arrays rather than arbitrary
  iterables. Array getters remain untrusted callbacks and are tested. General
  iterable support is still a compatibility limitation.

Verified evidence:

- [`cmake-policy-results.json`](cmake-policy-results.json): five actual policy-module
  acceptance/rejection cases pass, including runtime entropy without the Node
  profile and an unknown mode. This does not configure/build dependencies.
- [`openssl-patch-results.json`](openssl-patch-results.json): both pinned patches
  pass `git apply --check` and apply to a freshly extracted, hash-verified
  OpenSSL3.0.17 archive. Applied rand/uid source hashes are recorded; no source
  cache is reused. This is patch verification, not a compiled OpenSSL library.
- [`native-syntax-results.json`](native-syntax-results.json): 28 applicable
  translation units/configuration pairs pass `-fsyntax-only`, actual pinned
  SpiderMonkey Release headers, wasm32-wasi target and `-Werror`. This is not a
  linked Wasm engine or a native runtime test.
- [`mutation-baseline-results.json`](mutation-baseline-results.json): safe
  mutation-only vector ran in a real accepted R2 component (engine SHA
  `99fdaa97c2fbdea67cb7e5463d3dd2ca10c6981615acb4483d442079f6aab65c`, all
  191 frozen sources verified), zero imports, matching pinned Node22. It does
  not reproduce or certify absence of the borrowed-lifetime hazard.
- [`owned-input-node-results.json`](owned-input-node-results.json): eight
  cases in [`ownership-checks.mjs`](ownership-checks.mjs) first passed the Node
  oracle: mutation, initial detachment, getter detachment, RAB shrink with JS
  allocation pressure, validation-before-getter, HMAC key/message/signature
  ownership, and keyUsages getter order. Both production variant reports below
  now reproduce these results in real components.
  No detached/GC adversarial probe ran on the unsafe old native implementation.
- Historical `run-stage.mjs` evidence covers 14 standalone chunk/failure model
  cases and 17 policy selection cases; those are separate from production.

Production acceptance evidence:

| Variant | Engine SHA256 | Executed bounds |
| --- | --- | --- |
| OFF | `17181cc87579cb3784d444e9f0cc481e108522811609bd3382bcd16eea4efc07` | Two real scalar/export components, seven initialization rejections, eight Node ownership vectors, three retained calls plus fresh instance, zero final imports, Wasmtime42 run export. |
| RUNTIME_ONLY | `71c16b52d62beb1c9cae27420fd2b5135c400caf4745b8e872ea5cd9d5921bfa` | Same bounds, exact `wasi:random/random@0.2.10` sole scalar import, fresh samples across calls/instances, Wasmtime42 run export. |

[`production-off-results.json`](production-off-results.json) and
[`production-runtime-results.json`](production-runtime-results.json) contain each
267-input engine receipt, exact fixture source snapshots, scalar observations,
and the HTTP builder/Wasmtime/wash reports. The corresponding HTTP components
passed three requests on each host: OFF selects the five HTTP/IO interfaces,
RUNTIME_ONLY adds only secure random0.2.10. Monotonic-clock remains type-only.
Runtime HTTP also caught a snapshot RSA import failure and successfully retried
RSA import after deployment. The complete OpenSSL source audits in these records
verify all4,650 files against the pinned archive plus two patches, with identical
manifest SHA `02e422a422431574bf02fe1c1f2db6e3737b0f0d00e5ab86f399d1abfc59a4d3`.

[`../capability-policy-results.json`](../capability-policy-results.json) records
76 passing receipt/selection/import cases, including a real accepted-R2
packaging finalizer replacement rejected after wrapping. Malformed booleans,
profiles, modern receipts without policy, duplicate patches, non-string or
duplicate feature lists, custom/wildcard/versioned/insecure imports and malformed
policies are rejected. Empty-instance component fixtures validate names/versions,
not WASI function signatures or host behavior. The existing selected HTTP type
graph audit remains separate.

These are exact v1 artifacts, not automatic validation of later Path or other
source changes. Remaining limits include general indirect DEBUG ABI, exhaustive
crypto allocation/provider-path faults, deterministic finalization scheduling,
and entropy-quality certification. Different samples detect obvious replay only.
A finalizer initialization vector is diagnostic because scheduling is not
guaranteed without an explicit GC hook. No Node crypto compatibility is claimed.

[`run-production.mjs`](run-production.mjs) is the real-component runner. Supply
`NODE_COMPAT_ENGINE`, the audited `NODE_COMPAT_TOOLCHAIN`/
`NODE_COMPAT_COMPONENTIZE_MODULE`, and `NODE_COMPAT_WASMTIME`; select the matching
engine receipt. It ran in both modes with the explicitly pinned repository guest adapter
SHA `988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0`.
The first runtime attempt with default wrapping was correctly rejected for an
unselected random0.2.12 import; see
[`runtime-default-adapter-rejection.json`](runtime-default-adapter-rejection.json).
No version remapping or policy weakening was used. It audits exact root
component imports; proof of executable internal core imports remains the
packaging receipt's responsibility. The upstream crypto HTTP host gate is
separate from this scalar export runner.

The selected HTTP builder now preserves secure random through both relevant
`stubWasi` passes only for runtime-only engines, selects the explicit
[`profile-runtime-entropy.wit`](../wasmcloud/profile-runtime-entropy.wit), and
admits exactly `wasi:random/random@0.2.10` in addition to the existing five HTTP
interfaces. OFF keeps the previous HTTP pass/import set. Set
`NODE_COMPAT_HTTP_ENTRY` to the absolute path of [`http.mjs`](http.mjs) to run the
entropy fixture with the existing Wasmtime/wash host runners. It retains all
Buffer/stub assertions and appends snapshot denial, snapshot SHA256, ownership,
fresh-byte, object-URL/multipart and RSA-import recovery checks. The host reports above verify this fixture;
[`http-bundle-results.json`](http-bundle-results.json) remains the earlier isolated
Rolldown evidence. The unchanged original upstream native incoming HTTP server
also passed all ten routes, including152 crypto subtests, on both Wasmtime42 and
official wash2.11; see
[`../upstream/wasmcloud-integration-results.json`](../upstream/wasmcloud-integration-results.json).
The same component SHA `28f54fbc2401d642943d25119d0eac5d2e04846da6da27e557e7eb95b037a88e`
selects18 explicit standard0.2.10 interfaces. Two outgoing HTTP domain grants
serve the original fetch tests; no raw DNS/socket or TLS-over-sockets support
is inferred. This broad upstream world is separate from the minimal HTTP fixture.

The later [`production-runtime-v2-results.json`](production-runtime-v2-results.json)
repeats the scalar gate for engine
`8d260bf44128c57e4bfe4053d3c6532d9625458eeb6d78dbe2bc6a8fbbfcb068`
with all 268 v2 inputs verified: two components, seven initialization denials,
eight ownership cases, repeated/fresh-instance samples, Wasmtime42 and sole
secure random0.2.10 import. It does not transfer the v1 HTTP/upstream host
proofs to the changed v2 artifact.
