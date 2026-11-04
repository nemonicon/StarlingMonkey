# Finite private-tick admission — source-only candidate

This packet changes no live selector and provides no engine or guest proof.
The proposed selector keeps the existing historical branch and adds a finite
host-side source-policy branch for production recipe869d188…, policy98e80d36…,
helper78521fee… and the exact306-input scheduler source inventory. The native
source/recipe layer is independently applied by Root; admission remains unapplied.

The [two-file patch](selector.UNAPPLIED.patch) adds a build-time helper and a
small selector dispatch. Existing protected-listener validation is byte-unchanged
when no private-tick source/policy/option hint exists. Seven actual frozen v10/v11
receipts select the same manifests and maps as the live selector, without adding
new fields to those historical records. Real missing-field legacy exceptions
remain governed by the unchanged pinned table.

Known new runtime/CMake source bytes, queue paths, option/feature fields, the new
recipe or a private-tick version hint route to exact new validation. Missing or
unknown values cannot silently fall back to the old policy. The source layer has
its distinct strict/protected versions even when ticks are OFF. Every306 source
byte is checked; the seven before/after pairs reconstruct the exact304-input
parent digest. Current and historical parent maps remain separate.

The new branch requires an explicit boolean internalTicksEnabled and matching
requested/observed ON/OFF values, all reviewed policy/helper/recipe/patch/embedding
digests, exact limits, no added-capability/process claim, and Reset OPEN. It
requires Release, Weval OFF, wasm-opt ON, locked Cargo, the selected WASI host API,
the ABI fixes and strict initialization, and consistent explicit optional-feature,
entropy and GC selections. The unchanged historical branch has no new defaults.
It
parses captured compiler text without running a shell: each relevant native TU
and the embedding must have actual -c syntax, no -fsyntax-only, and consistent
strict, protected-layout and tick macros. The queue TU is present exactly once
when ON and absent when OFF. A macro defined as zero is rejected: #ifdef would
still enable it. Split/duplicate/undefined macro forms are also refused.

Diagnostic engines are rejected before production branch selection. A separate
diagnostic preflight must authenticate its own recipe, production306 plus the
explicit two-input diagnostic partition (total308), actual test target/compiler
and generated install namespace, fixed engine/sidecar/configuration bytes, and
finite raw guest IDs. No production manifest, process module/global or private
ID is added. Raw private componentization must not bypass that preflight.

The [82 tests](test-results.json) run only host-side metadata/source validation.
New positive and negative records are explicitly synthetic, with no engine file,
and cannot authorize receiver-negative or any guest execution. Tests cover
ON/OFF, Events selection, Release-GC selection, malformed policies/sources/maps,
patches, options, compiler observations, macro-zero mistakes, diagnostic rejection,
actual source-byte tampering and seven unchanged real old receipt selections.
The temporary source view is built from immutable frozen v11 ancestry plus the
authenticated native patch; it is removed after testing. No compiler, Wizer,
componentizer, Wasmtime or host is started. Three JS syntax checks and patch
applicability checks pass. No native/runtime ordering, reset/cancellation, ALS,
memory, component-size or throughput result follows.

The staged target files are under source/tests/node-compat. Supporting staged
manifest/schema/legacy/policy data exists only so the proposed module is imported
unchanged during its unit tests; it is not another native build inventory.
The helper lazily authenticates pins.json and the frozen integration policy/helper
only for the new branch. Those data files are required when this candidate is
coherently adopted; old branch calls do not acquire that dependency.

Reset/cancellation and public process remain OPEN/absent. The known callback-return
then-getter and disposal-symbol differences are unchanged. Future actual Release
and Release-GC engines, fixed byte/configuration preflight, component ordering and
regression/import/host gates remain required before execution or promotion.

The history directory preserves the initial successful 68-test iteration and the
expanded iteration whose eight synthetic positives rejected because the new
check expected uppercase entropy metadata. The final check uses the recipe's
actual `off` / `runtime-only` strings and their uppercase CMake counterparts.
That failed iteration ran only this host-side source validator.
