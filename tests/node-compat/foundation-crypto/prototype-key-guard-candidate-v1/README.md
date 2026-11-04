This is an **unapplied source-only CryptoKey prototype-as-key guard candidate**.
It adds two short-circuit conditions in `SubtleCrypto::sign` and `verify` only.
The live repository, configured355 checkout, owner proposal216d and existing four
native engines remain unchanged. No old unsafe prototype path, key operation,
cryptographic operation, GC, native full build, link, guest, OOM or reset ran.

The actual public checks accepted any object recognized by the CryptoKey class
predicate. The intrinsic class prototype has that class, but its key/algorithm
slots are uninitialized. Sign/verify then pass the key to internal helpers that
assume initialized slots. The existing four public property getters already
reject `self == proto_obj`; those getter bodies and errors are preserved.

The proposed checks additionally reject
`&key_arg.toObject() == CryptoKey::proto_obj.get()` through the existing invalid-key
TypeError and rejected-promise branch. C++ short-circuiting ensures `toObject()` is
not evaluated for a primitive or another noninstance. The identity comparison
reads the intrinsic persistent root, does not inspect a user-visible property or
prototype chain, allocates nothing and invokes no JavaScript. It runs before
BufferSource validation, algorithm normalization, internal-slot helpers and all
sign/verify operations, at the same invalid-key admission point.

Factory-created instances are distinct objects from the intrinsic prototype and
follow the same existing path. The entire translation unit reverses to its exact
preimage after removing these two conditions. No other public argument ordering,
error branch, normalization, key rooting, signature implementation, factory,
getter, constructor or global property changes. This is a source/control-flow
conclusion; cryptographic semantics and actual rejection remain runtime-unproved.

`composition.json` explicitly combines this one-file/two-edit guard with the
four byte-exact owner afterimages from
`key-owner-candidate-v1` index216d0272…. The paths are disjoint: five composed
files, twenty total edits. The owner packet and its independent source review
a213a1e2… remain immutable. The guard works at the same public admission points
with the current class policy or the proposed foreground owner policy; it does
not alter the predicate used by the existing getter macros.

Pure checks exercise ten synthetic boolean/identity rows for sign/verify,
including the short-circuit condition. They execute no JSClass or private-slot
access and do not reproduce an old native fault. Source checks authenticate the
exact before/after bytes, both reversals, unchanged parent afterimages, error
bodies, relative control-flow order, getter/global surface and stored SDK data.

One actual isolated147/WASI Release frontend check passed on the composed
`subtle-crypto.cpp` context with the five-file VFS overlay. The prototype is the
actual frozen normal355 Release compile command, with only object generation
removed and VFS/syntax/dependency flags added. It preserves target wasm32-WASI,
O3/NDEBUG/no-exceptions and other flags. The overlay contains five afterimages;
this translation unit actually consumes the new CPP and the two owner headers.
The1,089 logical compiler-dependency files were hashed after the frontend. Parent
known source inputs were checked before and after, but this is not a claim that
every possible header was prehashed or that concurrent mutation was excluded.
The owner’s two earlier CPP frontend checks remain separate stored evidence.
There is no object, link, library-symbol, engine or runtime result here.

Source integration still requires a fresh reviewed full355 source lineage,
recipe/admission successor, native build/freeze and independent review. Neither
this guard nor the owner bytes may pass under an old source helper by projection.
All future authority and runtime result fields remain NULL. A future allowed
prototype-key test must use the newly built reviewed guarded artifact; no unsafe
old engine is a negative-test target.

The owner’s required BIGNUM partial-extraction, private-copy erasure and
allocation/length follow-ons remain open. No complete crypto ownership, isolated
rooting, exact finalization, all-copy erasure, full Node crypto, bounded memory,
performance, request reuse or acceptance claim is made. There is no new host
service, host import, private-memory API, diagnostic export or reset mechanism.
