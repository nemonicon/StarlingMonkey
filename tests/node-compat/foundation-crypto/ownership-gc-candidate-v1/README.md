SOURCE proposal: isolated Release-GC build and strongly held HMAC-key fixture.

No build, configure, freezer/bootstrap helper, guest, key, prototype, GC, Node,
Wasmtime or compiler action is performed by this packet. All new native pins,
independent source reviews, Root authorities, component results and GC results are
NULL. This is a bounded proposal with explicit unimplemented action gates.

The real recipe already supports `NODE_COMPAT_BUILD_ROOT`. Its source and CMake
project suffix omits the stress selector; only the artifact basename includes
`.gc-stress`. The current `build-one.py gc-off` hardcodes the existing normal work
root. Running it would reconfigure the normal CMake project and invalidate the
authenticated CMakeCache and compile_commands originals. It is unsuitable here.
Use the unchanged configured recipe only under a separately reviewed external
owned controller, with the proposed fresh work root in `build-plan.template.json`.
No invented recipe option or metadata projection is needed. A fresh artifact tag
alone does not isolate the CMake project.

The GC freeze must also use a distinct fresh root. Appending to the normal freeze
would change its exact 1,391-file membership. The corrected freezer's guard and
artifact common module currently hardbind the old freeze root; the bootstrap also
binds the old configured/build/frozen contexts. Those require a thin, independently
reviewed source successor and new actual data before any invocation. This packet
does not implement or authorize that successor. Normal guarded355 policy, five
native replacements, recipe, source files and every existing proof remain intact.
`normal-protection.json` retains all 1,387 original-reference entries (1,378 distinct
original paths), all 1,390 frozen-copy entries and the complete original normal
freeze receipt descriptor. Both vulnerable project originals are explicitly pinned.

The actual CMake option applies `NODE_COMPAT_GC_STRESS=1` privately to the
`builtin_node_compat` target. It does not instrument WebCrypto translation units.
In Buffer's native hex kernel, `stress_gc` calls `JS::PrepareForFullGC` and
`JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API)` at rooted
boundaries outside borrowed byte pointers. Public `Buffer.from(hex,'hex')` reaches
hexDecode; `buffer.toString('hex')` reaches hexEncode. Each has three source hook
sites. `Buffer.alloc` itself is a Uint8Array allocation/fill in the facade; it is
allocation pressure and is not the explicit forced-GC hook.

`guest.GC.UNEXECUTED.mjs` is a finite afterimage of the original sealed HMAC guest.
It retains the original four ordinary ABI functions and no top-level key, crypto,
Buffer-allocation, hex-conversion, async or pressure calls. It imports the existing
public `node:buffer` module and invokes pressure only inside `exercise`, after a
genuine key is already held in the original module holder and function argument.
Four pressure points surround each pair of sign/verify operations. Each allocates
64 filled bytes, verifies full hex encoding, decodes it, and checks every byte.
The original raw/JWK imports, whole tag/boolean/sentinel/prior-output checks and
refusal cases remain. Four exercises yield 16 pressure records per outer validate.
That is a source schedule, not an observed GC count or proof of compaction.

The combined module holders, argument, other locals and application objects remain
strong owners. This deliberately tests surviving those public collection sites
with strong application ownership; it does not isolate a native temporary root,
pending operation, finalizer, free, wipe, all private copies, or native global
counter. No claim is made about GC occurring inside a WebCrypto native call.

The original component guard refuses every essential new condition: gc-off,
another engine, gcStress true and the Buffer import. It must not be reused by
forging normal-off state or metadata. Root owns the separately reviewed component
composition/loader plan and full typed-result collector. The new import requires
genuine selected Buffer module composition and all transitive source checks.
The future collector must retain whole raw strings before checks, compare every
unchanged HMAC field and each new pressure record, bind actual native/component
proofs, and preserve clean owned lifecycle evidence. None is supplied as an action
by this packet. No old normal wrapper is relabeled as a GC result.

`plan.py` only constructs and validates DATA. `prepare.py` reads/hashes existing
sources, builds exact afterimages/contracts and performs pure planning regressions.
It never imports a producer helper. JavaScript syntax parsing of the new guest is
an explicitly pending check; no Node/parser or guest has been invoked here.
