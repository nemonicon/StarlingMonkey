# Independent source review of diagnostic producer Link1

The sealed `diagnostic-producer-v3-link1/index.json` is
`9db6d51f65fb0bec95b122e1a6904ee20a7f6ce1e4f65502a9f1c55bebbe61a7`.
All 30 indexed files were independently rehashed without mismatch. The 306 live
native/build inputs and two diagnostic inputs retain the parent source bytes;
live diagnostic and production recipes remain `1e2f15d1…` and `869d188d…`.

No concrete blocker was found in the sealed source proposal. Its CMake setting
uses the existing `CMAKE_EXE_LINKER_FLAGS` mechanism. The validator checks the
generated final-target Ninja command before and after a future build, exact
Clang `-Wl` arguments, Release/ThinLTO and post-link wasm-opt flags, and pinned
SDK files plus executable-alias resolution. It checks requested and cached
configuration separately and records four raw/validation witnesses. Command
text is parsed as data and never executed by the validator.

Two issues identified during draft review are resolved in the seal: Clang++ and
wasm-ld resolve to the hashed SDK executables, and generated Clang flags are
distinguished from inferred LLD forwarding. Spawned LLD arguments, actual thread
counts and resource benefits remain unobserved. The prior print-only audit is
supporting evidence, not an executed link trial.

The `diag-link1` namespace fits the four empty-tag configurations: OFF normal/GC
236/246 bytes, RuntimeOnly normal/GC 245/255 bytes for the longest required
basename. RuntimeOnly GC therefore permits no extra tag. Existing artifacts and
the diagnostic semantic version retain their meaning.

This is source-review readiness, not build admission or runtime acceptance. A
new finite freezer/preflight amendment must bind the recipe/helper/policy pins,
the four final-link witness files and requested/observed fields. Existing
consumers must continue rejecting unknown recipes. The 2 GiB launch minimum and
800 MiB stop threshold remain unchanged. Any later new engine requires its full
ordinary/GC component and production gates. Reset/reuse remains unsupported.

[review.json](review.json) records the review scope and exact source pins.
No owner packet was edited, and no candidate helper/test, CMake configuration,
compiler, linker, build, guest, storage helper or resource measurement was run by
this review.
