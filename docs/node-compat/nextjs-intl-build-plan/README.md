# Proposed single Rust aggregate for Intl147

These are **unexecuted templates**, not a linked artifact, resolved Cargo graph
or action grant. Production/default non-Intl sources remain unchanged. Root owns
the SpiderMonkey workflow and `cmake/spidermonkey.cmake`; this companion changes
neither. The proposed `cmake/build-crates.cmake` afterimage consumes Root's real
`SPIDERMONKEY_INTL` selector, whose default is OFF, instead of adding a second
Intl switch. Four reversible edits preserve the existing Corrosion staticlib,
Rust profiles, hooks and allocator mechanism.

The actual existing `add_rust_lib` function always enables dependency defaults.
That is unsuitable for `icu_capi`: the exact fork's `jsrust_shared` explicitly
sets `default-features=false` and requests only `any_provider`, `compiled_data`,
`segmenter`, `calendar`. The template therefore appends that dependency and
the existing `pub use` pattern explicitly. `unicode-bidi-ffi` uses the genuine
existing `add_rust_lib` API. It adds no new `jsrust`, `mozglue-static`, allocator,
panic-handler library or invented symbol-retention function. ICU CAPI's wasm32
source imports `std` under a renamed binding; it participates in this same
Cargo compilation. Actual FFI symbol retention/linking still needs proof.

## Required source and overrides

Preserve these whole paths from commit
`9dab3d6f643e926a340c391ea30968e940390dec`, including checksum/source metadata:

- `intl/icu_capi/` — package 2.0.0, Rust minimum 1.82, normalized self-contained manifest.
- `intl/icu_segmenter_data/` — package 2.0.0, custom baked data used by the fork.
- `intl/bidi/rust/unicode-bidi-ffi/` — package 0.1.0; depends on ICU properties 2.0
  with `unicode_bidi`, and Unicode Bidi with `smallvec`.
- `third_party/rust/unicode-bidi/` — the fork's vendored git revision
  `ca612daf1c08c53abe07327cb3e6ef6e0a760f0c`, package 0.3.15. A same-version
  crates.io release is not an interchangeable source.

None of the three path manifests uses `workspace=true` inheritance or relative
sibling crate dependencies. They can be retained in an authenticated reduced
layout. Do not install Firefox's root Cargo manifest as the root of a partial
tree with missing workspace members. Keep its Cargo manifest/lock/config as
separately labeled provenance. Root's aggregate has its own `[workspace]`.

Dependency workspaces do not supply their root's patch table to this aggregate.
The alternate Cargo template explicitly carries the exact three relevant
overrides: CAPI path, segmenter-data path and patched Bidi git revision.
The private Cargo-config template replaces both registry and that git source
with one **new merged vendor directory**. It is not a fallback to host/system
ICU or an instruction to fetch dependencies during native compilation.

## Inputs still unissued

The existing actual aggregate lock has 49 packages. Conservative reachability
from CAPI/Bidi in the fork's whole-workspace lock also finds 49 packages;
these are different graphs. Thirty-five existing registry package versions
are absent from the fork lock. This does not prove those versions are absent
from every vendor directory, and the 49-row reachability is not an actual
feature-resolved minimum. Do not copy either old lock and label it combined.

Before configuration, Root must supply:

1. Coherent new Intl SpiderMonkey distribution/header/archive identities and
   the reviewed exact source bundle described above.
2. A private merged vendor set covering the old aggregate and new Intl graph,
   with Cargo checksum/source identities. Generate and review a genuine new
   aggregate lock, recording all changed old package versions and feature
   unification. Run actual offline Cargo metadata/locked validation before
   compiling; no such command ran here.
3. Absolute `NODE_COMPAT_INTL_FIREFOX_SOURCE` and new
   `NODE_COMPAT_INTL_LOCKFILE` paths, plus rendered private
   `CARGO_HOME/config.toml` and `CARGO_NET_OFFLINE=true` before Corrosion can
   invoke Cargo. The existing lock mode must remain ON. The templates refuse
   absent inputs and an old non-Intl generated header.

`actualCombinedLock` and `actualMergedVendor` remain NULL in the retained
constraints. No native-source/support count or metadata field is projected
from the old artifact; the eventual composed source inventory must account
for the changed CMake file and added alternate Cargo template explicitly.

## C++ archive packaging is separate

At the exact fork, `libjs_static.a` uses ICU. Mozilla's
[`_expand_libs`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/python/mozbuild/mozbuild/backend/common.py#L245-L302)
recursively flattens child static-library objects unless the child sets
`no_expand_lib`. ICU common/i18n/data and Intl components have no such barrier.
The expected generated archive therefore contains their objects; preserve the
actual response/member list to verify this. Keep the existing explicit extra
SpiderMonkey-object merge. Do not blindly append ICU archives again or nest
archives with `ar -q`. Rust ICU4X/Bidi remains the single-aggregate join above;
the C++ archive does not prove that separate FFI linkage.

## Source checks only

`python3.11 -B -I check-templates.py` performs offline hash/manifest/TOML checks,
four whole forward/inverse CMake edits and six meaningful DATA negatives.
It uses no Cargo, CMake, compiler, native engine or guest. Missing default-feature
suppression, extra logging, lost Bidi/data overrides, a second Rust library and
an additional shared-library output are rejected. These checks establish
template consistency, not Cargo workspace acceptance, feature resolution,
successful compilation, symbol retention, ABI or runtime correctness.

No heavy fetch/build is allowed at current local capacity. The main
[build plan](../nextjs-intl-build-plan.md) retains the capacity constraint and
subsequent full native rebuild, component/import and unchanged Next gates.
