# Unapplied m0.9 shared integration — v2

**No live integration is applied and no engine is built.**
[results.json](results.json) pins the review result;
[stream-web-m0.9.UNAPPLIED.patch](stream-web-m0.9.UNAPPLIED.patch) is the complete
22-file v2 patch. `git apply --check --whitespace=error` passes against the current
workspace. All 306 copied live baseline files were verified unchanged before
and after staging. `base/` preserves immutable v8 native inputs plus the needed
live harness files; `source/` contains the proposed result.

The staged runtime source is the accepted composed candidate, with the same
evaluated factory literal SHA
`7e3dbfe2189827e116c4157c9dd485e77c427184b1cf1317204137caa946b271`.
Canonical filenames are relocated under builtins/node-compat; the manifest is
rewritten as the proposed production policy rather than a fixture description.
The existing seven generated headers retain their bytes. No benchmark, complete
Node compatibility, complete Web Streams support or new runtime proof follows
from this source preparation.

V1 is preserved in [history/v1](history/v1/README.md), including its source,
checks and patch `32e8bab1…c7fcf`. V2 adds shared malformed/duplicate compiled-input
validation with twenty declared ON/OFF rejection cases, and replaces the kernel
opening template disclaimer with neutral purpose text. The production kernel
SHA is now `b0cb1dab9dcaa38719e6ebdd5fd35080109e13b9a1769798cc909512d568caa8`;
the original `c2301cd4…73e7c8` template remains unchanged in the earlier history.

## Concrete changes

- `NODE_COMPAT_STREAM_WEB` defaults OFF. Only its ON branch adds the private
  stream-web-kernel.cpp source, macro, source-root include directory, dependency
  and link edges to existing web streams/text codec targets. Missing core,
  streams or codec prerequisites fail configuration. OFF does not require web
  streams, add the kernel or change its dependency/link graph.
- Existing strict factory evaluation and define_builtin_module register
  node:stream/web and stream/web. The caller enters the content realm and roots
  the returned native record before evaluation. The exact sixteen-key kernel
  uses public JS_GetClassObject, existing retained prototype roots and public
  JS::IsReadableStreamBYOBReader, excluding scripted Proxy receivers. It creates
  no temporary streams, initialization promises or host handles.
- Real finite ESM declarations, an ordinary mutable seventeen-member default
  record and the m0.9 manifest match the exact Node v22.14.0 seventeen-plus-default
  namespace. No new host interface is required. Compression/decompression are
  still explicit deferred functions; signal, minimum-fill greater than one,
  proxy/backing/realm and native error-code gaps remain documented.
- The native Transform controller checker adds class-plus-object-valued Stream
  slot validation before the four public methods/getter access slots. JS
  Node-facing guards remain intact. Their ERR_INVALID_THIS applies to the
  known uninitialized prototype; other native receiver paths can retain uncoded
  TypeError. The prepared corrected-OFF runner tests the native guard directly
  without those wrappers.
- The independent dependency-free generator is called from the common
  generator. It requires exact Node22.14, compares the manifest with the actual
  Node namespace, validates finite ESM declarations and reflects the emitted
  strict factory's graph/default/native identities. Reflection constructs no
  streams/codecs and never invokes its build-only brand callback; eight changed
  host descriptors are restored. This is not native callback proof.
- The build recipe accepts only 0/1 for the feature, adds a `.stream-web-0/1`
  suffix even when OFF, records streamWebEnabled and the selected manifest,
  verifies actual registration flags and conditionally present kernel compile
  commands, and records actual prerequisite cache values. New engine receipts
  always contain explicit boolean selection and observed ON/OFF.
- Admission accepts an absent field only for a pinned ordinary legacy engine
  SHA **and recomputed canonical sourceManifest SHA and recipe SHA**. Unknown,
  future and synthetic receipts must explicitly declare false with observed
  OFF, or true with observed ON and the selected compiled manifest. Source-list
  and recipe spoofing reject. Every declared or legacy receipt also requires
  unique, well-formed relative source paths and lowercase SHA256 entries; Map
  construction never silently replaces a duplicate. External receipt paths in the policy are audit
  provenance, never runtime file dependencies.

The twenty ordinary Release/oomTesting=false legacy tuples include actually
used v5 Assert/Querystring and v6 Util OFF controls, both v8 entropy modes and
the accepted v8 GC engine
`69bf0d270ad408353f962d5e2ab7ac3bc0f3804e432540b10ea8098a22133879`.
DEBUG/OOM and unbacked historical records are excluded in
[legacy-exclusions.json](legacy-exclusions.json). A historical benchmark lacking
the required frozen recipe evidence uses its archived selector; the new policy
does not provide a broad legacy override.

The staged future-runner contract updates the manifest hash while retaining the
factory-literal/native-kernel/controller source pins. Its prepared index is
updated consistently. Those installed runners remain **unexecuted**.

## Verified preparation checks

| Evidence | Result and scope |
| --- | --- |
| [selection](checks/selection-results.json) | 320/320 synthetic admission/bundler checks, including seven independent optional features, ESM/CJS aliases/defaults, OFF refusal, hash/flag/collision/private-shadow and legacy-spoof cases; no engine execution |
| [generator](checks/generator-results.json) | All eight headers match; six malformed-source/manifest/graph cases reject without overwriting the header; wrong Node version rejects; host reflection only |
| [CMake](checks/cmake-results.json) | Seven actual add_builtin configure cases plus script mode, with dummy prerequisite targets; default OFF, missing prerequisites, ON-only source/flags/link/dependency and declaration install order; no engine compilation |
| [syntax](checks/syntax-results.json) | Actual LLVM21.1.4/wasi-sdk30/SM147 syntax checks for kernel, registration ON/OFF and corrected controller; unlinked, no native entry |
| [legacy](checks/legacy-results.json) | Five actual immutable v5/v6/v8 metadata selections, including current GC; hashes read and checked, no engines executed |
| [recipe](checks/recipe-results.json) | Shell and four embedded Python blocks parse; receipt argument arity 27; recipe not run |

```sh
/path/to/node-v22.14.0 source/builtins/node-compat/generate-factories.mjs --check
NODE_COMPAT_TOOLCHAIN=/path/to/locked-toolchain \
/path/to/node-v22.14.0 source/tests/node-compat/module-selection-test.mjs
python3 checks/check-generator.py
python3 checks/check-cmake.py
python3 checks/check-syntax.py
/path/to/node-v22.14.0 checks/check-legacy.mjs
# Read-only application check from the repository root:
git apply --check --whitespace=error /absolute/path/to/stream-web-m0.9.UNAPPLIED.patch
```

The helper scripts currently pin the actual local v8 receipt/SDK paths used for
these checks. Moving them requires equivalent explicit pins, not bypassing a
source gate.

Before installed support: root reviews/applies the patch, builds new ON and
corrected OFF engines with immutable receipts, executes the prepared direct
native guard control and full installed module corpus, checks aliases/CJS/
componentization/snapshot reuse and both target HTTP hosts, and audits final
WASI imports. Real JS_GetClassObject identities, native callback behavior and
linkage remain pending. add_dependencies is not initializer topology: earlier
add_builtin declarations install web streams/text codec first, verified here;
native null-root guards still fail closed.
